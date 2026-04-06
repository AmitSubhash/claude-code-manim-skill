"""Bridge to mathcode: parse Lean formalizations into explanation scaffolds.

Reads mathcode output (Lean 4 files, thinking logs, eval JSON) and
extracts a structured breakdown that the planner uses to design
mathematically rigorous animated explanations.

Each proof step becomes a candidate animation beat. Lemma references
become "background knowledge" scenes. The theorem statement becomes
the hook equation.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class MathStep:
    """One step in the formal proof breakdown."""

    description: str
    lean_snippet: str = ""
    lemmas_used: list[str] = field(default_factory=list)


@dataclass
class FormalBreakdown:
    """Structured extraction from mathcode output."""

    theorem_name: str
    theorem_statement: str
    natural_language: str
    proof_strategy: str
    steps: list[MathStep]
    lemmas: list[str]
    pitfalls: list[str]
    lean_source: str
    eval_grade: str = ""


def parse_lean_file(lean_path: Path) -> dict[str, str]:
    """Extract theorem name and statement from a Lean 4 file.

    Parameters
    ----------
    lean_path : Path
        Path to a .lean file produced by mathcode.

    Returns
    -------
    dict
        Keys: theorem_name, theorem_statement, full_source.
    """
    source = lean_path.read_text()
    # Match: theorem <name> : <statement> := by
    match = re.search(
        r"theorem\s+(\w+)\s*(?:\{[^}]*\})?\s*:\s*(.*?)\s*:=\s*by",
        source,
        re.DOTALL,
    )
    if match:
        return {
            "theorem_name": match.group(1),
            "theorem_statement": match.group(2).strip(),
            "full_source": source,
        }
    # Fallback: just get any theorem/def
    match = re.search(r"theorem\s+(\w+)\s*.*?:=", source, re.DOTALL)
    if match:
        return {
            "theorem_name": match.group(1),
            "theorem_statement": source[match.start() : match.end()],
            "full_source": source,
        }
    return {
        "theorem_name": lean_path.stem,
        "theorem_statement": "",
        "full_source": source,
    }


def parse_thinking_log(log_path: Path) -> dict[str, str]:
    """Parse a mathcode Phase 5.2 thinking log.

    Parameters
    ----------
    log_path : Path
        Path to a .thinking_stdout.log file.

    Returns
    -------
    dict
        Keys: proof_strategy, lemmas, pitfalls, full_text.
    """
    if not log_path.exists():
        return {"proof_strategy": "", "lemmas": "", "pitfalls": "", "full_text": ""}
    text = log_path.read_text()

    def _extract_section(header: str) -> str:
        pattern = rf"(?:^|\n)\d*\)?\s*{header}[:\s]*\n(.*?)(?=\n\d+\)|$)"
        m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return m.group(1).strip() if m else ""

    return {
        "proof_strategy": _extract_section("Proof strategy")
        or _extract_section("Revised strategy"),
        "lemmas": _extract_section("Candidate lemmas"),
        "pitfalls": _extract_section("Coercion.*pitfall")
        or _extract_section("type pitfall"),
        "full_text": text,
    }


def parse_eval_json(eval_path: Path) -> str:
    """Extract grade from mathcode eval JSON.

    Parameters
    ----------
    eval_path : Path
        Path to .eval.json file.

    Returns
    -------
    str
        Grade string (A, B, C, D) or empty.
    """
    if not eval_path.exists():
        return ""
    try:
        data = json.loads(eval_path.read_text())
        return str(data.get("grade", data.get("evaluation", {}).get("grade", "")))
    except (json.JSONDecodeError, AttributeError):
        return ""


def load_mathcode_output(
    source: Path,
    problem_json: Optional[Path] = None,
) -> FormalBreakdown:
    """Load mathcode output from a Lean file or output directory.

    Parameters
    ----------
    source : Path
        Either a .lean file directly, or a mathcode output directory
        containing .lean files and logs.
    problem_json : Path, optional
        Original problem JSON for natural language extraction.

    Returns
    -------
    FormalBreakdown
        Structured breakdown for the planner.
    """
    # Find the Lean file
    if source.is_file() and source.suffix == ".lean":
        lean_path = source
        logs_dir = source.parent
    elif source.is_dir():
        lean_files = sorted(source.glob("*.lean"))
        if not lean_files:
            raise FileNotFoundError(f"No .lean files found in {source}")
        lean_path = lean_files[0]
        logs_dir = source.parent / "logs" if (source.parent / "logs").exists() else source
    else:
        raise FileNotFoundError(f"Not a .lean file or directory: {source}")

    # Parse Lean
    lean_info = parse_lean_file(lean_path)

    # Parse thinking log (find latest iteration)
    theorem_name = lean_info["theorem_name"]
    thinking_logs = sorted(logs_dir.glob(f"{theorem_name}*.thinking_stdout.log"))
    thinking = parse_thinking_log(thinking_logs[-1]) if thinking_logs else {
        "proof_strategy": "", "lemmas": "", "pitfalls": "", "full_text": "",
    }

    # Parse eval
    eval_files = sorted(logs_dir.glob(f"{theorem_name}*.eval.json"))
    grade = parse_eval_json(eval_files[-1]) if eval_files else ""

    # Parse natural language from problem JSON
    natural_language = ""
    if problem_json and problem_json.exists():
        try:
            data = json.loads(problem_json.read_text())
            problem_lines = data.get("problem", [])
            if isinstance(problem_lines, list):
                natural_language = " ".join(problem_lines)
        except json.JSONDecodeError:
            pass

    # Build steps from proof strategy
    steps: list[MathStep] = []
    if thinking["proof_strategy"]:
        for line in thinking["proof_strategy"].split("\n"):
            line = line.strip().lstrip("- ").lstrip("0123456789.)").strip()
            if line:
                steps.append(MathStep(description=line))

    # Extract lemma names
    lemmas: list[str] = []
    if thinking["lemmas"]:
        for line in thinking["lemmas"].split("\n"):
            line = line.strip().lstrip("- ")
            if line:
                lemmas.append(line)

    # Extract pitfalls
    pitfalls: list[str] = []
    if thinking["pitfalls"]:
        for line in thinking["pitfalls"].split("\n"):
            line = line.strip().lstrip("- ")
            if line:
                pitfalls.append(line)

    return FormalBreakdown(
        theorem_name=theorem_name,
        theorem_statement=lean_info["theorem_statement"],
        natural_language=natural_language,
        proof_strategy=thinking["proof_strategy"],
        steps=steps,
        lemmas=lemmas,
        pitfalls=pitfalls,
        lean_source=lean_info["full_source"],
        eval_grade=grade,
    )


def breakdown_to_prompt_context(breakdown: FormalBreakdown) -> str:
    """Convert a FormalBreakdown into prompt context for the planner.

    Parameters
    ----------
    breakdown : FormalBreakdown
        Parsed mathcode output.

    Returns
    -------
    str
        Markdown block to inject into the planning prompt.
    """
    sections = [
        "## Formal Mathematical Context (from mathcode)",
        "",
        f"**Theorem:** `{breakdown.theorem_name}`",
    ]

    if breakdown.natural_language:
        sections.append(f"\n**Natural language:** {breakdown.natural_language}")

    if breakdown.theorem_statement:
        sections.append(f"\n**Formal statement (Lean 4):**\n```lean\n{breakdown.theorem_statement}\n```")

    if breakdown.proof_strategy:
        sections.append(f"\n**Proof strategy:**\n{breakdown.proof_strategy}")

    if breakdown.steps:
        sections.append("\n**Proof steps (use these as animation beats):**")
        for i, step in enumerate(breakdown.steps, 1):
            sections.append(f"{i}. {step.description}")

    if breakdown.lemmas:
        sections.append("\n**Key lemmas/theorems referenced:**")
        for lemma in breakdown.lemmas:
            sections.append(f"- {lemma}")

    if breakdown.pitfalls:
        sections.append("\n**Common misconceptions / pitfalls:**")
        for pitfall in breakdown.pitfalls:
            sections.append(f"- {pitfall}")

    if breakdown.eval_grade:
        sections.append(f"\n**Formalization quality grade:** {breakdown.eval_grade}")

    sections.extend([
        "",
        "Use this formal breakdown to structure the visual explanation.",
        "Each proof step should map to one or more animation beats.",
        "The theorem statement should appear as the central equation.",
        "Lemmas should be introduced as background before the main proof.",
        "Pitfalls should be addressed in the misconception analysis.",
    ])

    return "\n".join(sections)
