"""CLI for 3brown1blue -- install the Manim skill and generate animated explainers."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import click

from .audit_video import audit
from .edit_scene import edit, list_scenes, preview
from .from_slides import from_slides
from .generate import generate
from .remix_audience import remix
from .split_project import split
from .voiceover import voiceover

SKILL_SOURCE = Path(__file__).parent / "skill"

PLATFORMS = [
    ("claude-code", "Claude Code (CLI)"),
    ("cursor",      "Cursor"),
    ("windsurf",    "Windsurf"),
    ("copilot",     "GitHub Copilot"),
]

START_MARKER = "<!-- 3b1b:start -->"
END_MARKER   = "<!-- 3b1b:end -->"


def _prompt_platform() -> str:
    click.echo("\nWhich AI coding tool are you using?\n")
    for i, (key, label) in enumerate(PLATFORMS, 1):
        click.echo(f"  {i}. {label}")
    click.echo()
    choice = click.prompt("Platform", type=click.IntRange(1, len(PLATFORMS)))
    return PLATFORMS[choice - 1][0]


def _prompt_scope() -> str:
    click.echo("\nInstall scope:\n")
    click.echo("  1. Global  (all your projects)")
    click.echo("  2. Project (current directory only)\n")
    choice = click.prompt("Scope", type=click.IntRange(1, 2))
    return "global" if choice == 1 else "project"


def _merge_skill_markdown() -> str:
    """Merge SKILL.md + all rule files into one markdown string."""
    parts: list[str] = []

    skill_md = SKILL_SOURCE / "SKILL.md"
    if skill_md.exists():
        parts.append(skill_md.read_text())

    rules_dir = SKILL_SOURCE / "rules"
    if rules_dir.exists():
        for f in sorted(rules_dir.glob("*.md")):
            heading = f.stem.replace("-", " ").title()
            parts.append(f"\n\n---\n\n## {heading}\n\n{f.read_text()}")

    return "\n".join(parts)


def _replace_marked_block(existing: str, block: str) -> str:
    """Replace a marked block in existing content, or append it."""
    if START_MARKER in existing:
        if END_MARKER not in existing:
            click.echo(
                "Found start marker but no end marker -- file may be corrupt. "
                "Remove the block manually and re-run."
            )
            sys.exit(1)
        s = existing.index(START_MARKER)
        e = existing.index(END_MARKER) + len(END_MARKER)
        return existing[:s] + block + existing[e:]
    return (existing.rstrip() + "\n\n" + block) if existing.strip() else block


# ── Platform installers ────────────────────────────────────────────────────

def _install_claude_code(force: bool) -> None:
    dest = Path.home() / ".claude" / "skills" / "manim"
    if dest.exists() and not force:
        click.echo(f"Already installed at {dest}\nRun with --force to overwrite.")
        sys.exit(1)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(SKILL_SOURCE, dest)
    click.echo(f"\nInstalled to {dest}")
    click.echo("Restart Claude Code to activate.")


def _uninstall_claude_code() -> None:
    dest = Path.home() / ".claude" / "skills" / "manim"
    if not dest.exists():
        click.echo("Claude Code: not installed.")
        return
    shutil.rmtree(dest)
    click.echo(f"Removed {dest}")


def _install_cursor(scope: str, force: bool) -> None:
    base = Path.home() if scope == "global" else Path.cwd()
    rules_dir = base / ".cursor" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)

    rule_files = sorted((SKILL_SOURCE / "rules").glob("*.md"))
    targets = [rules_dir / "manim-explainer.mdc"] + [
        rules_dir / f"manim-{f.stem}.mdc" for f in rule_files
    ]
    if any(t.exists() for t in targets) and not force:
        click.echo(f"Already installed in {rules_dir}\nRun with --force to overwrite.")
        sys.exit(1)

    skill_md = SKILL_SOURCE / "SKILL.md"
    if not skill_md.exists():
        click.echo("Skill data missing -- reinstall the package.")
        sys.exit(1)

    _write_mdc(
        rules_dir / "manim-explainer.mdc",
        "Manim video explainer skill -- use for animation, paper explainers, equation videos",
        skill_md.read_text(),
    )
    for rule_file in rule_files:
        _write_mdc(
            rules_dir / f"manim-{rule_file.stem}.mdc",
            f"Manim: {rule_file.stem.replace('-', ' ')}",
            rule_file.read_text(),
        )

    click.echo(f"\nInstalled {len(targets)} rule files to {rules_dir}")
    click.echo("Rules are off by default. Enable them in Cursor > Rules as needed.")


def _uninstall_cursor(scope: str) -> None:
    base = Path.home() if scope == "global" else Path.cwd()
    rules_dir = base / ".cursor" / "rules"
    removed = 0
    for f in list(rules_dir.glob("manim-*.mdc")) if rules_dir.exists() else []:
        f.unlink()
        removed += 1
    if removed:
        click.echo(f"Removed {removed} rule files from {rules_dir}")
    else:
        click.echo("Cursor: nothing to remove.")


def _write_mdc(path: Path, description: str, content: str) -> None:
    safe_desc = description.replace('"', '\\"')
    path.write_text(
        f'---\ndescription: "{safe_desc}"\nalwaysApply: false\n---\n\n{content}'
    )


def _install_windsurf(force: bool) -> None:
    rules_file = Path.cwd() / ".windsurfrules"
    existing = rules_file.read_text() if rules_file.exists() else ""

    if START_MARKER in existing and not force:
        click.echo("Already installed in .windsurfrules\nRun with --force to overwrite.")
        sys.exit(1)

    block = f"{START_MARKER}\n{_merge_skill_markdown()}\n{END_MARKER}"
    rules_file.write_text(_replace_marked_block(existing, block))
    click.echo(f"\nInstalled to {rules_file}")


def _uninstall_windsurf() -> None:
    rules_file = Path.cwd() / ".windsurfrules"
    if not rules_file.exists():
        click.echo("Windsurf: nothing to remove.")
        return
    existing = rules_file.read_text()
    if START_MARKER not in existing:
        click.echo("Windsurf: nothing to remove.")
        return
    if END_MARKER not in existing:
        click.echo("Found start marker but no end marker -- remove manually.")
        sys.exit(1)
    s = existing.index(START_MARKER)
    e = existing.index(END_MARKER) + len(END_MARKER)
    rules_file.write_text((existing[:s] + existing[e:]).strip())
    click.echo(f"Removed block from {rules_file}")


def _install_copilot(force: bool) -> None:
    github_dir = Path.cwd() / ".github"
    github_dir.mkdir(exist_ok=True)
    instructions = github_dir / "copilot-instructions.md"
    existing = instructions.read_text() if instructions.exists() else ""

    if START_MARKER in existing and not force:
        click.echo(
            "Already installed in .github/copilot-instructions.md\n"
            "Run with --force to overwrite."
        )
        sys.exit(1)

    block = f"{START_MARKER}\n{_merge_skill_markdown()}\n{END_MARKER}"
    instructions.write_text(_replace_marked_block(existing, block))
    click.echo(f"\nInstalled to {instructions}")


def _uninstall_copilot() -> None:
    instructions = Path.cwd() / ".github" / "copilot-instructions.md"
    if not instructions.exists():
        click.echo("Copilot: nothing to remove.")
        return
    existing = instructions.read_text()
    if START_MARKER not in existing:
        click.echo("Copilot: nothing to remove.")
        return
    if END_MARKER not in existing:
        click.echo("Found start marker but no end marker -- remove manually.")
        sys.exit(1)
    s = existing.index(START_MARKER)
    e = existing.index(END_MARKER) + len(END_MARKER)
    instructions.write_text((existing[:s] + existing[e:]).strip())
    click.echo(f"Removed block from {instructions}")


# ── CLI ────────────────────────────────────────────────────────────────────

@click.group()
@click.version_option()
def main() -> None:
    """Generate and install Manim animated explainer videos.

    Generate a scene from a topic using any LLM provider, or install
    the skill into Claude Code, Cursor, Windsurf, or GitHub Copilot.
    """


main.add_command(audit)
main.add_command(generate)
main.add_command(from_slides)
main.add_command(edit)
main.add_command(list_scenes)
main.add_command(preview)
main.add_command(remix)
main.add_command(split)
main.add_command(voiceover)


@main.command()
@click.option("--platform", "-p",
              type=click.Choice([k for k, _ in PLATFORMS]),
              help="Skip the platform prompt.")
@click.option("--scope", "-s",
              type=click.Choice(["global", "project"]),
              default=None,
              help="Global or project install (Cursor only).")
@click.option("--force", is_flag=True, help="Overwrite existing installation.")
def install(platform: str | None, scope: str | None, force: bool) -> None:
    """Install the Manim explainer skill."""
    if platform is None:
        platform = _prompt_platform()

    if platform == "claude-code":
        _install_claude_code(force)
    elif platform == "cursor":
        if scope is None:
            scope = _prompt_scope()
        _install_cursor(scope, force)
    elif platform == "windsurf":
        _install_windsurf(force)
    elif platform == "copilot":
        _install_copilot(force)


@main.command()
@click.option("--platform", "-p",
              type=click.Choice([k for k, _ in PLATFORMS]),
              help="Skip the platform prompt.")
@click.option("--scope", "-s",
              type=click.Choice(["global", "project"]),
              default=None)
def update(platform: str | None, scope: str | None) -> None:
    """Update an existing installation to the current version."""
    if platform is None:
        platform = _prompt_platform()
    if platform == "cursor" and scope is None:
        scope = _prompt_scope()
    ctx = click.get_current_context()
    ctx.invoke(install, platform=platform, scope=scope, force=True)


@main.command()
@click.option("--platform", "-p",
              type=click.Choice([k for k, _ in PLATFORMS]),
              help="Skip the platform prompt.")
@click.option("--scope", "-s",
              type=click.Choice(["global", "project"]),
              default=None,
              help="Cursor scope.")
def uninstall(platform: str | None, scope: str | None) -> None:
    """Remove the Manim explainer skill."""
    if platform is None:
        platform = _prompt_platform()

    if platform == "claude-code":
        _uninstall_claude_code()
    elif platform == "cursor":
        if scope is None:
            scope = _prompt_scope()
        _uninstall_cursor(scope)
    elif platform == "windsurf":
        _uninstall_windsurf()
    elif platform == "copilot":
        _uninstall_copilot()


@main.command()
def status() -> None:
    """Show what is currently installed."""
    found = False

    cc = Path.home() / ".claude" / "skills" / "manim"
    if cc.exists():
        files = list(cc.rglob("*"))
        click.echo(f"Claude Code:    {cc}  ({sum(1 for f in files if f.is_file())} files)")
        found = True

    cg = Path.home() / ".cursor" / "rules"
    mdc_global = list(cg.glob("manim-*.mdc")) if cg.exists() else []
    if mdc_global:
        click.echo(f"Cursor global:  {cg}  ({len(mdc_global)} rules)")
        found = True

    cp = Path.cwd() / ".cursor" / "rules"
    mdc_proj = list(cp.glob("manim-*.mdc")) if cp.exists() else []
    if mdc_proj:
        click.echo(f"Cursor project: {cp}  ({len(mdc_proj)} rules)")
        found = True

    ws = Path.cwd() / ".windsurfrules"
    if ws.exists() and START_MARKER in ws.read_text():
        click.echo(f"Windsurf:       {ws}")
        found = True

    gh = Path.cwd() / ".github" / "copilot-instructions.md"
    if gh.exists() and START_MARKER in gh.read_text():
        click.echo(f"Copilot:        {gh}")
        found = True

    if not found:
        click.echo("Not installed anywhere. Run `3brown1blue install` to set up.")
