"""remix command: re-target an existing video project to a different audience level."""

from __future__ import annotations

import re
import stat
import sys
from pathlib import Path
from typing import Optional

import click

from .edit_scene import _discover_scenes, _find_project_dir, _read_style
from .generate import (
    PROVIDERS,
    _extract_code,
    _render_scene,
    _resolve_api_key,
    call_llm,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_CONSTRUCT_PREVIEW_LINES = 20

AUDIENCE_CHOICES = ["high-school", "undergrad", "graduate", "industry", "general"]

# "general" has no audience rule file -- map to "high-school" internally,
# but the prompt wording says "general audience with no assumed domain knowledge".
_AUDIENCE_RULE_MAP: dict[str, str] = {
    "general": "high-school",
}

REMIX_PLAN = """\
You are re-targeting an existing Manim video project to a different audience.

CURRENT PROJECT:
{scene_summary}

CURRENT STYLE:
{style_code}

EXISTING PLANNING DOCS:
{planning_docs}

NEW TARGET AUDIENCE: {audience_label}

CRITICAL RULE: Changing audience level requires FULL CURRICULUM REBUILD,
not just simplifying text. Read the audience rules for "{audience_rule}" carefully.

STEP 1: Analyze what the current audience knows vs what the new audience knows.
List concepts that need new foundational scenes.

STEP 2: Design a NEW curriculum (scene list) following the {audience_rule} audience rules.
- Add new background/foundational scenes where needed
- Adapt existing scenes that still apply (slower pacing, analogies, etc.)
- Remove scenes that are too advanced for the new audience
- The total scene count may increase or decrease

STEP 3: For each scene in the new curriculum, write a scene plan:
  ## Scene N: ClassName (~duration)
  Template: [FULL_CENTER | DUAL_PANEL | BUILD_UP | ...]
  Source: [NEW | ADAPTED from scene_XX | KEPT from scene_XX]
  Content: [what goes where]
  Changes from original: [if adapted, what changed]

STEP 4: Updated style.py contract (colors, sizes, helpers).

Output the complete remix plan as structured markdown.\
"""

REMIX_GENERATE = """\
REMIX PLAN:
{plan}

ORIGINAL STYLE.PY:
{style_code}

Generate ALL scene files for the remixed video. Output format:

### FILE: scene_01_name.py
```python
...code...
```

### FILE: scene_02_name.py
```python
...code...
```

### FILE: utils/style.py
```python
...code...
```

MANDATORY RULES (non-negotiable):
1. Layout: Use the template specified in each scene plan. x in [-5.5, 5.5], y in [-3.2, 3.2]
2. Text: safe_text() pattern for body. Max width 12 Manim units. Scale if wider.
3. Containers: Position children relative to parent (next_to, move_to), not absolute
4. Lifecycle: FadeOut titles/headers before new content reuses their region
5. Density: Fill 50%+ of frame. Bars fill_opacity >= 0.6, width >= 0.3
6. Cleanup: FadeOut all elements before the next logical section
7. MathTex: NO dollar signs. Use Tex for mixed text+math
8. Animations: Write() for text, Create() for shapes, ReplacementTransform for eq chains
9. Bottom text: buff >= 0.5, FadeOut previous before adding new
10. Updaters: self.wait(frozen_frame=False) when updaters are active
11. Audience pacing: Match wait() durations and annotation density to the audience level
12. Color semantics: Define all colors as named constants at the top; never use raw hex inline
13. Persistent elements: Objects declared as "Visual anchors" must be created once and \
transformed/updated across scenes, never recreated from scratch
14. Equation chains: Use ReplacementTransform between successive equation states
15. Final scene: Always end with a summary/takeaway scene
16. Each scene must be self-contained and independently renderable
17. Import from utils.style import * in each scene file
18. from manim import * at the top of each scene file

Return ONLY the file blocks described above. No explanation outside code.\
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_scene_summary(scenes: list[dict]) -> str:
    """Build a compact summary of each scene: filename, class, docstring, construct head.

    Parameters
    ----------
    scenes : list[dict]
        Scene dicts from ``_discover_scenes``.

    Returns
    -------
    str
        Markdown-formatted summary of all scenes.
    """
    parts: list[str] = []
    for s in scenes:
        source = s["file"].read_text()
        classes_str = ", ".join(s["classes"]) if s["classes"] else "(none)"

        # Extract docstring (first triple-quoted string after class definition)
        docstring = ""
        doc_match = re.search(
            r'class\s+\w+\s*\(.*?\):\s*\n\s+"""(.*?)"""',
            source,
            re.DOTALL,
        )
        if doc_match:
            docstring = doc_match.group(1).strip().split("\n")[0]

        # Extract the first N lines of construct()
        construct_head = ""
        construct_match = re.search(
            r"(def construct\(self\).*?)(?=\n    def |\Z)",
            source,
            re.DOTALL,
        )
        if construct_match:
            lines = construct_match.group(1).splitlines()
            preview = lines[: _CONSTRUCT_PREVIEW_LINES + 1]  # +1 for def line
            construct_head = "\n".join(preview)
            if len(lines) > _CONSTRUCT_PREVIEW_LINES + 1:
                construct_head += f"\n        # ... ({len(lines) - _CONSTRUCT_PREVIEW_LINES - 1} more lines)"

        part = f"### {s['file'].name}  (classes: {classes_str})"
        if docstring:
            part += f"\nDocstring: {docstring}"
        if construct_head:
            part += f"\n```python\n{construct_head}\n```"
        parts.append(part)

    return "\n\n".join(parts)


def _read_planning_docs(project_dir: Path) -> str:
    """Read curriculum.md and research.md if they exist.

    Parameters
    ----------
    project_dir : Path
        Root directory of the video project.

    Returns
    -------
    str
        Combined content of planning docs, or "(none found)".
    """
    docs: list[str] = []
    for name in ("curriculum.md", "research.md"):
        p = project_dir / name
        if p.exists():
            docs.append(f"## {name}\n\n{p.read_text()}")
    return "\n\n".join(docs) if docs else "(none found)"


def _parse_file_blocks(response: str) -> list[tuple[str, str]]:
    """Parse ``### FILE: filename.py`` blocks from LLM response.

    Parameters
    ----------
    response : str
        Raw LLM response containing file blocks.

    Returns
    -------
    list[tuple[str, str]]
        List of (filename, code) tuples.
    """
    files: list[tuple[str, str]] = []
    # Match "### FILE: path/to/file.py" followed by a code block
    pattern = re.compile(
        r"###\s+FILE:\s*(.+\.py)\s*\n```(?:python)?\n(.*?)```",
        re.DOTALL,
    )
    for match in pattern.finditer(response):
        filename = match.group(1).strip()
        code = match.group(2).strip()
        files.append((filename, code))
    return files


def _generate_render_script(
    project_dir: Path,
    file_blocks: list[tuple[str, str]],
) -> Path:
    """Generate a render_all.sh script for the new scene files.

    Parameters
    ----------
    project_dir : Path
        Root directory of the video project.
    file_blocks : list[tuple[str, str]]
        List of (filename, code) from the LLM.

    Returns
    -------
    Path
        Path to the generated render_all.sh.
    """
    scene_entries: list[tuple[str, str]] = []
    for filename, code in file_blocks:
        if not filename.startswith("scene_"):
            continue
        classes = re.findall(
            r"^class\s+(\w+)\s*\(.*Scene.*\)", code, re.MULTILINE,
        )
        if classes:
            scene_entries.append((filename, classes[0]))

    project_name = project_dir.name
    lines = [
        "#!/bin/bash",
        f"# Render all {project_name} scenes and concatenate into final video.",
        "# Usage: ./render_all.sh [quality]",
        "#   quality: l (480p), m (720p), h (1080p), k (4K)",
        "#   default: h (1080p)",
        "",
        "set -euo pipefail",
        "",
        'QUALITY="${1:-h}"',
        'SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"',
        'cd "$SCRIPT_DIR"',
        "",
        "SCENES=(",
    ]
    for filename, class_name in scene_entries:
        lines.append(f'    "{filename} {class_name}"')
    lines += [
        ")",
        "",
        "# Map quality to resolution folder name",
        'case "$QUALITY" in',
        '    l) RES_DIR="480p15" ;;',
        '    m) RES_DIR="720p30" ;;',
        '    h) RES_DIR="1080p60" ;;',
        '    k) RES_DIR="2160p60" ;;',
        '    *) echo "Unknown quality: $QUALITY (use l, m, h, or k)"; exit 1 ;;',
        "esac",
        "",
        'echo "=== Rendering ${#SCENES[@]} scenes at quality -q${QUALITY} ==="',
        "",
        "FAILED=0",
        'for entry in "${SCENES[@]}"; do',
        "    FILE=$(echo \"$entry\" | awk '{print $1}')",
        "    CLASS=$(echo \"$entry\" | awk '{print $2}')",
        '    echo ""',
        '    echo "--- Rendering $FILE :: $CLASS ---"',
        '    if ! manim -q"$QUALITY" "$FILE" "$CLASS"; then',
        '        echo "FAILED: $FILE :: $CLASS"',
        "        FAILED=$((FAILED + 1))",
        "    fi",
        "done",
        "",
        'if [ "$FAILED" -gt 0 ]; then',
        '    echo ""',
        '    echo "=== $FAILED scene(s) failed to render ==="',
        "    exit 1",
        "fi",
        "",
        'echo ""',
        'echo "=== All scenes rendered. Concatenating... ==="',
        "",
        "# Build ffmpeg concat list",
        'CONCAT_FILE="$SCRIPT_DIR/concat_list.txt"',
        '> "$CONCAT_FILE"',
        "",
        'for entry in "${SCENES[@]}"; do',
        "    FILE=$(echo \"$entry\" | awk '{print $1}')",
        "    CLASS=$(echo \"$entry\" | awk '{print $2}')",
        '    BASENAME="${FILE%.py}"',
        '    VIDEO_PATH="$SCRIPT_DIR/media/videos/${BASENAME}/${RES_DIR}/${CLASS}.mp4"',
        '    if [ -f "$VIDEO_PATH" ]; then',
        """        echo "file '$VIDEO_PATH'" >> "$CONCAT_FILE\"""",
        "    else",
        '        echo "WARNING: Missing $VIDEO_PATH"',
        "    fi",
        "done",
        "",
        f'OUTPUT="$SCRIPT_DIR/{project_name}_full_${{QUALITY}}.mp4"',
        'ffmpeg -y -f concat -safe 0 -i "$CONCAT_FILE" -c copy "$OUTPUT" 2>/dev/null',
        "",
        'echo ""',
        'echo "=== Done! Final video: $OUTPUT ==="',
        'echo "=== Scenes: ${#SCENES[@]}, Quality: ${QUALITY} ==="',
    ]

    script_path = project_dir / "render_all.sh"
    script_path.write_text("\n".join(lines) + "\n")
    script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
    return script_path


def _cleanup_old_scenes(
    project_dir: Path,
    new_filenames: set[str],
) -> list[Path]:
    """Remove old scene_*.py files not present in the new plan.

    Parameters
    ----------
    project_dir : Path
        Root directory of the video project.
    new_filenames : set[str]
        Set of new scene filenames (basename only).

    Returns
    -------
    list[Path]
        List of paths that were removed.
    """
    removed: list[Path] = []
    for old_file in sorted(project_dir.glob("scene_*.py")):
        if old_file.name not in new_filenames:
            old_file.unlink()
            removed.append(old_file)
    return removed


# ---------------------------------------------------------------------------
# CLI command
# ---------------------------------------------------------------------------


@click.command()
@click.option(
    "--audience", "-a", required=True,
    type=click.Choice(AUDIENCE_CHOICES),
    help="Target audience level for the remixed video.",
)
@click.option(
    "--provider", "-p",
    type=click.Choice(list(PROVIDERS)),
    default=None,
    help="LLM provider.",
)
@click.option("--model", "-m", default=None, help="Model (provider default).")
@click.option("--api-key", "-k", default=None, help="API key.")
@click.option(
    "--dir", "-d", "project_dir", default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Project directory (auto-detected if omitted).",
)
@click.option(
    "--plan-output",
    default=None,
    help="Optional markdown file to save the reviewed remix plan.",
)
@click.option("--render", is_flag=True, help="Render all new scenes after generation.")
@click.option(
    "--quality", "-q",
    type=click.Choice(["l", "m", "h", "k"]),
    default="l", show_default=True,
    help="Render quality: l=low/fast, m=medium, h=1080p, k=4K.",
)
def remix(
    audience: str,
    provider: Optional[str],
    model: Optional[str],
    api_key: Optional[str],
    project_dir: Path,
    plan_output: Optional[str],
    render: bool,
    quality: str,
) -> None:
    """Re-target an existing video project to a different audience level.

    Reads all existing scene files, style, and planning docs, then asks the
    LLM to rebuild the curriculum and generate new scene files for the target
    audience.

    \b
    Examples:
      3brown1blue remix --audience general -p claude-code
      3brown1blue remix --audience graduate -p anthropic --dir videos/neuronmm
      3brown1blue remix --audience high-school -p claude-code --render -q h
    """
    from ._shared import confirm_plan, prompt_provider

    # -- Resolve project directory and discover existing scenes ---------------
    project_dir = _find_project_dir(project_dir)
    scenes = _discover_scenes(project_dir)

    if not scenes:
        click.echo(f"No scene_*.py files found in {project_dir}")
        sys.exit(1)

    click.echo(f"\nProject:  {project_dir.name}")
    click.echo(f"Scenes:   {len(scenes)}")
    click.echo(f"Audience: {audience}")

    # -- Resolve provider and model ------------------------------------------
    if provider is None:
        provider = prompt_provider()

    cfg = PROVIDERS[provider]
    model = model or cfg["default_model"]
    api_key = _resolve_api_key(provider, api_key)

    click.echo(f"Provider: {cfg['label']}  ({model})")

    # -- Build context -------------------------------------------------------
    scene_summary = _build_scene_summary(scenes)
    style_code = _read_style(project_dir) or "(no style.py found)"
    planning_docs = _read_planning_docs(project_dir)

    # Map audience to rule file name and prompt label
    audience_rule = _AUDIENCE_RULE_MAP.get(audience, audience)
    if audience == "general":
        audience_label = "general audience with no assumed domain knowledge"
    else:
        audience_label = audience

    # -- Step 1: Ask LLM to re-plan ------------------------------------------
    click.echo("\nBuilding remix plan...")
    plan_prompt = REMIX_PLAN.format(
        scene_summary=scene_summary,
        style_code=style_code,
        planning_docs=planning_docs,
        audience_label=audience_label,
        audience_rule=audience_rule,
    )
    plan = call_llm(
        provider, model, api_key, plan_prompt,
        audience=audience_rule,
    )

    # -- Step 2: User confirms the plan --------------------------------------
    plan = confirm_plan(plan)
    if plan_output:
        plan_path = Path(plan_output)
        plan_path.write_text(plan)
        click.echo(f"Saved plan: {plan_path}")

    # -- Step 3: Generate new scene files ------------------------------------
    click.echo(f"\nGenerating remixed scenes with {model}...")
    generate_prompt = REMIX_GENERATE.format(
        plan=plan,
        style_code=style_code,
    )
    raw = call_llm(
        provider, model, api_key, generate_prompt,
        audience=audience_rule,
    )

    # -- Step 4: Parse file blocks from LLM response -------------------------
    file_blocks = _parse_file_blocks(raw)

    if not file_blocks:
        # Fallback: if the LLM returned a single code block without FILE markers,
        # extract it and save as a single file
        code = _extract_code(raw)
        if code:
            click.echo("Warning: LLM returned a single code block instead of file blocks.")
            click.echo("Saving as scene_01_remixed.py")
            file_blocks = [("scene_01_remixed.py", code)]
        else:
            click.echo("Error: Could not parse any scene files from LLM response.")
            click.echo("Raw response saved to remix_raw_output.txt for debugging.")
            (project_dir / "remix_raw_output.txt").write_text(raw)
            sys.exit(1)

    click.echo(f"\nParsed {len(file_blocks)} files from LLM response:")
    for filename, code in file_blocks:
        lines_count = len(code.splitlines())
        click.echo(f"  {filename} ({lines_count} lines)")

    # -- Step 5: Warn about overwrites and clean up old files ----------------
    new_filenames: set[str] = set()
    for filename, _ in file_blocks:
        basename = Path(filename).name
        new_filenames.add(basename)

    # Check for files that will be overwritten
    overwrite_targets: list[Path] = []
    for filename, _ in file_blocks:
        target = project_dir / filename
        if target.exists():
            overwrite_targets.append(target)

    if overwrite_targets:
        click.echo(f"\nFiles that will be overwritten ({len(overwrite_targets)}):")
        for t in overwrite_targets:
            click.echo(f"  {t.name}")

    # Identify old scene files to remove
    old_scene_names = {s["file"].name for s in scenes}
    to_remove = old_scene_names - new_filenames
    if to_remove:
        click.echo(f"\nOld scene files to remove ({len(to_remove)}):")
        for name in sorted(to_remove):
            click.echo(f"  {name}")

    if overwrite_targets or to_remove:
        if not click.confirm("\nProceed with file changes?", default=True):
            click.echo("Aborted.")
            sys.exit(0)

    # Remove old scene files
    removed = _cleanup_old_scenes(project_dir, new_filenames)
    if removed:
        click.echo(f"\nRemoved {len(removed)} old scene file(s).")

    # -- Step 6: Write new files ---------------------------------------------
    for filename, code in file_blocks:
        target = project_dir / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(code + "\n")
        click.echo(f"  Wrote: {filename}")

    # -- Step 7: Generate render_all.sh --------------------------------------
    script_path = _generate_render_script(project_dir, file_blocks)
    click.echo(f"  Wrote: {script_path.name}")

    # -- Step 8: Optionally render all scenes --------------------------------
    if render:
        click.echo(f"\nRendering all scenes at -q{quality}...")
        for filename, code in file_blocks:
            if not filename.startswith("scene_"):
                continue
            scene_file = project_dir / filename
            click.echo(f"\n--- {filename} ---")
            _render_scene(scene_file, quality)

    click.echo(f"\nRemix complete! {len(file_blocks)} files written to {project_dir}")
    click.echo(f"Target audience: {audience_label}")
