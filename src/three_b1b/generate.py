"""LLM-powered Manim scene generation from a topic description."""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click

SKILL_SOURCE = Path(__file__).parent / "skill"

PROVIDERS = {
    "anthropic": {
        "env_var": "ANTHROPIC_API_KEY",
        "default_model": "claude-sonnet-4-5",
        "label": "Anthropic (Claude)",
    },
    "openai": {
        "env_var": "OPENAI_API_KEY",
        "default_model": "gpt-4o",
        "label": "OpenAI",
        "base_url": None,
    },
    "google": {
        "env_var": "GOOGLE_API_KEY",
        "default_model": "gemini-2.0-flash",
        "label": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
    },
    "groq": {
        "env_var": "GROQ_API_KEY",
        "default_model": "llama-3.3-70b-versatile",
        "label": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
    },
    "mistral": {
        "env_var": "MISTRAL_API_KEY",
        "default_model": "mistral-large-latest",
        "label": "Mistral",
        "base_url": "https://api.mistral.ai/v1",
    },
    "claude-code": {
        "env_var": None,
        "default_model": "opus",
        "label": "Claude Code (claude -p)",
    },
}

MAX_TOKENS = 16384


def _build_system_prompt(audience: str = "undergrad", domain: str = "auto") -> str:
    parts: list[str] = []
    # Audience rules FIRST (highest priority)
    audience_path = SKILL_SOURCE / "audiences" / f"{audience}.md"
    if audience_path.exists():
        parts.append(f"\n\n## Audience: {audience.title()}\n\n{audience_path.read_text()}")
    # Domain rules SECOND
    if domain != "auto":
        domain_path = SKILL_SOURCE / "domains" / f"{domain}.md"
        if domain_path.exists():
            parts.append(f"\n\n## Domain: {domain.title()}\n\n{domain_path.read_text()}")
    # SKILL.md is the main entry point -- gotchas, templates, rule index
    skill_md = SKILL_SOURCE / "SKILL.md"
    if skill_md.exists():
        parts.append(skill_md.read_text())
    # Load ALL rule files -- the full depth of the skill
    rules_dir = SKILL_SOURCE / "rules"
    if rules_dir.exists():
        for f in sorted(rules_dir.glob("*.md")):
            heading = f.stem.replace("-", " ").title()
            parts.append(f"\n\n## {heading}\n\n{f.read_text()}")
    # Include templates as reference code the model can adapt
    templates_dir = SKILL_SOURCE / "templates"
    if templates_dir.exists():
        parts.append("\n\n## Reference Templates\n")
        for f in sorted(templates_dir.glob("*.py")):
            parts.append(f"\n### {f.stem}\n```python\n{f.read_text()}```")
    # Include safe_manim wrappers
    safe = SKILL_SOURCE / "scripts" / "safe_manim.py"
    if safe.exists():
        parts.append(f"\n\n## Safe Manim Wrappers\n```python\n{safe.read_text()}```")
    parts.append(
        "\n\n---\n\n"
        "Return ONLY a complete, runnable Python file. "
        "Do not include any explanation outside the code. "
        "The file must define at least one Scene subclass. "
        "Use descriptive comments inside the code."
    )
    return "\n".join(parts)


def _extract_code(response: str) -> str:
    match = re.search(r"```(?:python)?\n(.*?)```", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return response.strip()


def _resolve_api_key(provider: str, api_key: Optional[str]) -> str:
    env_var = PROVIDERS[provider].get("env_var")
    if env_var is None:
        return ""
    key = (api_key or "").strip() or os.environ.get(env_var, "").strip()
    if not key:
        click.echo(f"No API key found. Set {env_var} or pass --api-key.")
        sys.exit(1)
    return key


def _call_anthropic(user_msg: str, model: str, api_key: str, system: str) -> str:
    try:
        import anthropic
    except ImportError:
        click.echo("Run: pip install anthropic  (or: pip install '3brown1blue[anthropic]')")
        sys.exit(1)
    try:
        client = anthropic.Anthropic(api_key=api_key, timeout=60.0)
        msg = client.messages.create(
            model=model, max_tokens=MAX_TOKENS, system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
    except anthropic.APIConnectionError:
        click.echo("Could not connect to Anthropic API. Check your network.")
        sys.exit(1)
    except anthropic.APIStatusError as e:
        click.echo(f"Anthropic API error ({e.status_code}): {e.message}")
        sys.exit(1)
    except Exception:
        click.echo("An unexpected error occurred calling the Anthropic API.")
        sys.exit(1)
    if msg.stop_reason == "max_tokens":
        click.echo("Warning: response was cut off (max tokens reached).")
    return msg.content[0].text


def _call_openai_compatible(
    user_msg: str, model: str, api_key: str, base_url: Optional[str], system: str
) -> str:
    try:
        import openai
        from openai import OpenAI
    except ImportError:
        click.echo("Run: pip install openai  (or: pip install '3brown1blue[openai]')")
        sys.exit(1)
    kwargs: dict = {"api_key": api_key, "timeout": 60.0}
    if base_url:
        kwargs["base_url"] = base_url
    try:
        client = OpenAI(**kwargs)
        response = client.chat.completions.create(
            model=model, max_tokens=MAX_TOKENS,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg},
            ],
        )
    except openai.APIConnectionError:
        click.echo("Could not connect to API. Check your network.")
        sys.exit(1)
    except openai.APIStatusError as e:
        click.echo(f"API error ({e.status_code}): {e.message}")
        sys.exit(1)
    except Exception:
        click.echo("An unexpected error occurred calling the API.")
        sys.exit(1)
    choice = response.choices[0]
    if choice.finish_reason == "length":
        click.echo("Warning: response was cut off (max tokens reached).")
    content = choice.message.content
    if not content:
        click.echo("Provider returned empty content. Try again or check your API quota.")
        sys.exit(1)
    return content


def _call_claude_code(user_msg: str, model: str, system: str) -> str:
    if not shutil.which("claude"):
        click.echo("'claude' CLI not found. Install Claude Code first.")
        sys.exit(1)
    try:
        result = subprocess.run(
            ["claude", "-p", "--model", model, "--system-prompt", system, "--tools", ""],
            input=user_msg, capture_output=True, text=True, timeout=600,
        )
    except subprocess.TimeoutExpired:
        click.echo("claude -p timed out after 5 minutes.")
        sys.exit(1)
    except Exception:
        click.echo("Failed to run claude -p.")
        sys.exit(1)
    if result.returncode != 0:
        click.echo(f"claude -p failed (exit {result.returncode}).")
        sys.exit(1)
    return result.stdout.strip()


def call_llm(
    provider: str,
    model: str,
    api_key: str,
    user_msg: str,
    system: Optional[str] = None,
    audience: str = "undergrad",
    domain: str = "auto",
) -> str:
    """Call any configured LLM provider with explicit system and user messages."""
    if provider not in PROVIDERS:
        click.echo(f"Unknown provider '{provider}'. Valid: {', '.join(PROVIDERS)}")
        sys.exit(1)
    sys_prompt = system if system is not None else _build_system_prompt(audience=audience, domain=domain)
    if provider == "claude-code":
        return _call_claude_code(user_msg, model, sys_prompt)
    if provider == "anthropic":
        return _call_anthropic(user_msg, model, api_key, sys_prompt)
    cfg = PROVIDERS[provider]
    return _call_openai_compatible(user_msg, model, api_key, cfg.get("base_url"), sys_prompt)


def _render_scene(scene_file: Path, quality: str) -> None:
    source = scene_file.read_text()
    matches = re.findall(r"^class\s+(\w+)\s*\(.*Scene.*\)", source, re.MULTILINE)
    if not matches:
        click.echo("Could not detect a Scene class -- skipping render.")
        click.echo(f"Run manually: manim -pq{quality} {scene_file} <SceneName>")
        return
    scene_name = matches[-1]
    cmd = ["manim", f"-pq{quality}", str(scene_file), scene_name]
    click.echo(f"Rendering:  {' '.join(cmd)}\n")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        click.echo(f"\nRender failed (exit {result.returncode}).")
        sys.exit(result.returncode)


# ── Click command ──────────────────────────────────────────────────────────

@click.command()
@click.argument("topic")
@click.option("--provider", "-p", type=click.Choice(list(PROVIDERS)), default=None,
              help="LLM provider to use.")
@click.option("--model", "-m", default=None, help="Generation model (provider default).")
@click.option("--plan-model", default=None, help="Planning model (same as --model if omitted).")
@click.option("--api-key", "-k", default=None, help="API key (or set the provider env var).")
@click.option("--output", "-o", default="scene.py", show_default=True, help="Output file.")
@click.option("--plan-output", default=None, help="Optional markdown file to save the reviewed plan.")
@click.option("--render", is_flag=True, help="Run manim on the generated file.")
@click.option("--quality", "-q", type=click.Choice(["l", "m", "h", "k"]), default="l",
              show_default=True, help="Render quality: l=low/fast, m=medium, h=1080p, k=4K.")
@click.option("--audience", "-a",
              type=click.Choice(["high-school", "undergrad", "graduate", "industry"]),
              default="undergrad", show_default=True,
              help="Target audience level.")
@click.option("--domain", "-d",
              type=click.Choice(["auto", "machine-learning", "mathematics", "physics", "biology", "security", "neuroscience", "algorithms"]),
              default="auto", show_default=True,
              help="Academic domain (auto-detect if omitted).")
def generate(
    topic: str,
    provider: Optional[str],
    model: Optional[str],
    plan_model: Optional[str],
    api_key: Optional[str],
    output: str,
    plan_output: Optional[str],
    render: bool,
    quality: str,
    audience: str,
    domain: str,
) -> None:
    """Generate a Manim explainer video from TOPIC.

    Two-step pipeline: first plans the video (research, curriculum, scene
    plans, style contract), shows you the plan for review, then generates
    complete Manim code following the skill's layout templates and rules.

    \b
    Examples:
      3brown1blue generate "backpropagation" -p claude-code
      3brown1blue generate "Fourier transform" --provider openai --render
      3brown1blue generate "attention mechanism" -p anthropic --render -q h
      3brown1blue generate "neural ODEs" -a graduate -d machine-learning
    """
    from .prompts import RESEARCH_AND_PLAN, GENERATE_FROM_PLAN
    from ._shared import prompt_provider, confirm_plan

    if provider is None:
        provider = prompt_provider()

    cfg = PROVIDERS[provider]
    model = model or cfg["default_model"]
    plan_model = plan_model or model
    api_key = _resolve_api_key(provider, api_key)

    # Step 1: Research and plan
    click.echo(f"\nPlanning: \"{topic}\"")
    click.echo(f"Provider: {cfg['label']}  ({plan_model})")
    click.echo(f"Audience: {audience}  Domain: {domain}")
    plan = call_llm(provider, plan_model, api_key,
                    RESEARCH_AND_PLAN.format(topic=topic, audience=audience, domain=domain),
                    audience=audience, domain=domain)

    # Step 2: Review
    plan = confirm_plan(plan)
    if plan_output:
        plan_path = Path(plan_output)
        plan_path.write_text(plan)
        click.echo(f"Saved plan: {plan_path}")

    # Step 3: Generate code from plan
    click.echo(f"\nGenerating Manim code with {model}...")
    raw = call_llm(provider, model, api_key,
                   GENERATE_FROM_PLAN.format(plan=plan),
                   audience=audience, domain=domain)
    code = _extract_code(raw)

    out_path = Path(output)
    out_path.write_text(code)
    click.echo(f"Saved: {out_path}")

    if render:
        _render_scene(out_path, quality)
