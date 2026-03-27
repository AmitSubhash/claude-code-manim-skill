"""edit command: surgically modify a single scene in a multi-scene project."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click

from .generate import (
    PROVIDERS,
    _build_system_prompt,
    _extract_code,
    _render_scene,
    _resolve_api_key,
    call_llm,
)


def _find_project_dir(start: Path) -> Path:
    """Walk up from *start* looking for a directory with scene_*.py files."""
    d = start.resolve()
    for _ in range(5):
        if list(d.glob("scene_*.py")):
            return d
        if d.parent == d:
            break
        d = d.parent
    return start.resolve()


def _discover_scenes(project_dir: Path) -> list[dict]:
    """Return sorted list of scene dicts: {index, file, classes}."""
    scenes: list[dict] = []
    for f in sorted(project_dir.glob("scene_*.py")):
        source = f.read_text()
        classes = re.findall(
            r"^class\s+(\w+)\s*\(.*Scene.*\)", source, re.MULTILINE,
        )
        # Extract scene number from filename: scene_05_gpu.py -> 5
        m = re.match(r"scene_(\d+)", f.stem)
        idx = int(m.group(1)) if m else 0
        scenes.append({"index": idx, "file": f, "classes": classes})
    return scenes


def _read_style(project_dir: Path) -> str:
    """Read the project's style.py if it exists."""
    candidates = [
        project_dir / "utils" / "style.py",
        project_dir / "style.py",
    ]
    for p in candidates:
        if p.exists():
            return p.read_text()
    return ""


def _find_concat_script(project_dir: Path) -> Optional[Path]:
    """Find render_all.sh or similar concat script."""
    for name in ("render_all.sh", "concat.sh", "build.sh"):
        p = project_dir / name
        if p.exists():
            return p
    return None


def _reconcat(project_dir: Path, quality: str) -> None:
    """Re-run the concat step of render_all.sh without re-rendering all scenes."""
    script = _find_concat_script(project_dir)
    if script is None:
        click.echo("No render_all.sh found -- skipping concatenation.")
        click.echo("Run your concat script manually to update the full video.")
        return

    # Map quality to resolution dir
    res_map = {"l": "480p15", "m": "720p30", "h": "1080p60", "k": "2160p60"}
    res_dir = res_map.get(quality, "1080p60")

    # Build concat list from scene files
    scenes = _discover_scenes(project_dir)
    concat_file = project_dir / "concat_list.txt"
    entries: list[str] = []
    missing = 0
    for s in scenes:
        for cls in s["classes"]:
            video = (
                project_dir / "media" / "videos"
                / s["file"].stem / res_dir / f"{cls}.mp4"
            )
            if video.exists():
                entries.append(f"file '{video}'")
            else:
                click.echo(f"  Missing: {video.name}")
                missing += 1

    if not entries:
        click.echo("No rendered scene videos found -- skipping concat.")
        return

    concat_file.write_text("\n".join(entries) + "\n")

    # Find output name pattern
    output = project_dir / f"{project_dir.name}_full_{quality}.mp4"
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_file), "-c", "copy", str(output),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        click.echo(f"\nFull video updated: {output}")
    else:
        click.echo(f"ffmpeg concat failed: {result.stderr[:200]}")
        if missing:
            click.echo(f"({missing} scene videos were missing)")


EDIT_PROMPT = """\
You are editing a SINGLE Manim scene file. The user wants specific changes.

## Current scene code:
```python
{scene_code}
```

## Project style.py:
```python
{style_code}
```

## User's edit request:
{instruction}

## Rules:
1. Return the COMPLETE modified scene file (not a diff)
2. Keep the same class name and import structure
3. Follow all Manim rules: safe_text(), bottom_note() with FadeIn, no \\n in Text()
4. Layout bounds: x in [-5.5, 5.5], y in [-3.2, 3.2]
5. End with fade_all() cleanup
6. Only change what the user asked for -- preserve everything else
7. If adding new content, maintain the existing visual style and color palette

Return ONLY the complete Python file.\
"""


# ── list command ──────────────────────────────────────────────────────────


@click.command(name="list")
@click.option("--dir", "-d", "project_dir", default=".",
              type=click.Path(exists=True, file_okay=False, path_type=Path),
              help="Project directory (auto-detected if omitted).")
def list_scenes(project_dir: Path) -> None:
    """List all scenes in the current video project.

    \b
    Example:
      3brown1blue list
      3brown1blue list --dir videos/neuronmm
    """
    project_dir = _find_project_dir(project_dir)
    scenes = _discover_scenes(project_dir)

    if not scenes:
        click.echo(f"No scene_*.py files found in {project_dir}")
        return

    click.echo(f"\nProject: {project_dir.name}")
    click.echo(f"Scenes:  {len(scenes)}\n")
    click.echo(f"{'#':<4} {'File':<35} {'Class':<30}")
    click.echo("-" * 69)
    for s in scenes:
        cls_str = ", ".join(s["classes"]) if s["classes"] else "(no Scene class)"
        click.echo(f"{s['index']:<4} {s['file'].name:<35} {cls_str:<30}")

    style = _read_style(project_dir)
    if style:
        click.echo(f"\nStyle:   utils/style.py ({len(style)} chars)")

    script = _find_concat_script(project_dir)
    if script:
        click.echo(f"Render:  {script.name}")
    click.echo()


# ── edit command ──────────────────────────────────────────────────────────


@click.command()
@click.argument("target")
@click.argument("instruction")
@click.option("--provider", "-p", type=click.Choice(list(PROVIDERS)), default=None,
              help="LLM provider.")
@click.option("--model", "-m", default=None, help="Model (provider default).")
@click.option("--api-key", "-k", default=None, help="API key.")
@click.option("--dir", "-d", "project_dir", default=".",
              type=click.Path(exists=True, file_okay=False, path_type=Path),
              help="Project directory.")
@click.option("--render", is_flag=True, help="Re-render the edited scene.")
@click.option("--quality", "-q", type=click.Choice(["l", "m", "h", "k"]),
              default="l", show_default=True,
              help="Render quality for the edited scene.")
@click.option("--concat", is_flag=True,
              help="Re-concatenate the full video after rendering.")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt.")
def edit(
    target: str,
    instruction: str,
    provider: Optional[str],
    model: Optional[str],
    api_key: Optional[str],
    project_dir: Path,
    render: bool,
    quality: str,
    concat: bool,
    yes: bool,
) -> None:
    """Edit a specific scene in your video project.

    TARGET can be a scene number (e.g., "5") or a filename
    (e.g., "scene_05_gpu.py"). INSTRUCTION describes what to change.

    \b
    Examples:
      3brown1blue edit 5 "slow down the GPU explanation" -p claude-code
      3brown1blue edit scene_05_gpu.py "add tensor cores" -p anthropic --render
      3brown1blue edit 3 "use bigger font for the matrix" --render --concat -q h
      3brown1blue edit 14 "add A100 comparison bars" -p claude-code --render -y
    """
    from ._shared import prompt_provider

    project_dir = _find_project_dir(project_dir)
    scenes = _discover_scenes(project_dir)

    if not scenes:
        click.echo(f"No scene_*.py files found in {project_dir}")
        sys.exit(1)

    # Resolve target to a scene
    scene = None
    if target.isdigit():
        idx = int(target)
        for s in scenes:
            if s["index"] == idx:
                scene = s
                break
        if scene is None:
            click.echo(f"Scene {idx} not found. Available: {[s['index'] for s in scenes]}")
            sys.exit(1)
    else:
        target_path = project_dir / target
        for s in scenes:
            if s["file"] == target_path or s["file"].name == target:
                scene = s
                break
        if scene is None:
            click.echo(f"File '{target}' not found. Run `3brown1blue list` to see scenes.")
            sys.exit(1)

    scene_file: Path = scene["file"]
    scene_code = scene_file.read_text()
    style_code = _read_style(project_dir)

    click.echo(f"\nEditing: {scene_file.name}")
    click.echo(f"Class:   {', '.join(scene['classes'])}")
    click.echo(f"Change:  {instruction}")
    click.echo(f"Lines:   {len(scene_code.splitlines())}")

    if provider is None:
        provider = prompt_provider()

    cfg = PROVIDERS[provider]
    model = model or cfg["default_model"]
    api_key = _resolve_api_key(provider, api_key)

    # Call LLM with edit prompt
    click.echo(f"\nApplying edit with {cfg['label']} ({model})...")
    user_msg = EDIT_PROMPT.format(
        scene_code=scene_code,
        style_code=style_code or "(no style.py found)",
        instruction=instruction,
    )
    raw = call_llm(provider, model, api_key, user_msg)
    new_code = _extract_code(raw)

    # Show diff summary
    old_lines = len(scene_code.splitlines())
    new_lines = len(new_code.splitlines())
    click.echo(f"\nResult: {old_lines} -> {new_lines} lines")

    # Preview changes
    if not yes:
        click.echo("\n" + "=" * 50 + " PREVIEW " + "=" * 50)
        # Show first 40 lines of new code
        preview_lines = new_code.splitlines()[:40]
        for i, line in enumerate(preview_lines, 1):
            click.echo(f"  {i:3d} | {line}")
        if len(new_code.splitlines()) > 40:
            click.echo(f"  ... ({len(new_code.splitlines()) - 40} more lines)")
        click.echo("=" * 109)

        choice = click.prompt(
            "\nApply? [y]es / [v]iew full / [q]uit", default="y",
        ).strip().lower()
        if choice in ("v", "view"):
            click.echo(new_code)
            choice = click.prompt(
                "\nApply? [y]es / [q]uit", default="y",
            ).strip().lower()
        if choice not in ("y", "yes"):
            click.echo("Aborted.")
            sys.exit(0)

    # Write the edited file
    scene_file.write_text(new_code)
    click.echo(f"Saved: {scene_file.name}")

    # Render if requested
    if render:
        click.echo(f"\nRendering at -q{quality}...")
        _render_scene(scene_file, quality)

        if concat:
            click.echo("\nRe-concatenating full video...")
            _reconcat(project_dir, quality)

    elif concat:
        click.echo("\n--concat requires --render. Skipping.")

    click.echo("\nDone!")
