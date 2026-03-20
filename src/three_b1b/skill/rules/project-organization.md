---
name: Project Organization
description: Multi-scene project structure, shared styling, reusable components, and batch rendering for Manim projects
tags: [manim, project, organization, structure, style, components]
---

# Multi-Scene Project Organization

**Why does project organization matter for Manim?** A research explainer video might
have 10+ scenes across multiple files. Without organization, you'll have: duplicated
color definitions, inconsistent styling between scenes, no easy way to re-render just
one scene, and a messy `media/` folder. This file shows a project structure that solves
all of these: shared style constants, reusable components, per-scene files, and a batch
render script.

## Recommended Project Layout

```
my_video/
  scenes/
    s01_intro.py
    s02_background.py
    s03_method.py
    s04_results.py
    s05_conclusion.py
  utils/
    style.py          # shared colors, fonts, helpers
    components.py     # reusable diagram components
  assets/
    images/           # PNG, JPG for ImageMobject
    svgs/             # SVG files for SVGMobject
    data/             # CSV, JSON for data-driven animations
  media/              # output directory (gitignored)
  manim.cfg           # project-level config
  render_all.sh       # batch render script
  requirements.txt    # manim + any extra deps
```

## style.py: Shared Visual Constants

```python
"""Shared visual constants for the project."""

from manim import *

# ── Color Palette ──
PRIMARY = "#1F77B4"
SECONDARY = "#FF7F0E"
ACCENT = "#2CA02C"
HIGHLIGHT = "#FFD700"
DANGER = "#E74C3C"
BG_DARK = "#1a1a2e"
BG_LIGHT = "#f0f0f0"

# ── Font Sizes ──
TITLE_SIZE = 64
HEADING_SIZE = 48
BODY_SIZE = 36
CAPTION_SIZE = 24
LABEL_SIZE = 20

# ── Consistent tex_to_color_map ──
# Use across all equations in the video for visual consistency
PAPER_COLOR_MAP = {
    r"\mu_a": "#FF6B6B",
    r"\mu_s": "#4ECDC4",
    r"\Phi": "#FFE66D",
    r"\mathbf{J}": "#A8E6CF",
}

# ── Standard margins and spacing ──
STANDARD_BUFF = 0.3
SECTION_BUFF = 0.8


def section_title(text: str) -> VGroup:
    """Create a styled section title with underline."""
    title = Text(text, font_size=HEADING_SIZE, color=PRIMARY)
    underline = Line(
        title.get_left(), title.get_right(),
        color=PRIMARY, stroke_width=2,
    ).next_to(title, DOWN, buff=0.05)
    return VGroup(title, underline).to_edge(UP, buff=0.5)


def fade_scene_transition(scene: Scene, *mobs: Mobject) -> None:
    """Fade out all given mobjects for a clean transition."""
    scene.play(*[FadeOut(m) for m in mobs])
    scene.wait(0.3)
```

## components.py: Reusable Diagram Components

```python
"""Reusable diagram components."""

from manim import *
from .style import PRIMARY, BODY_SIZE, LABEL_SIZE


def labeled_box(
    label: str,
    width: float = 2.5,
    height: float = 0.9,
    color: str = PRIMARY,
    font_size: int = LABEL_SIZE,
) -> VGroup:
    """A rectangle with centered text label."""
    box = Rectangle(
        width=width,
        height=height,
        color=color,
        fill_opacity=0.2,
        stroke_width=2,
    )
    text = Text(label, font_size=font_size)
    text.move_to(box)
    return VGroup(box, text)


def pipeline(
    stage_names: list[str],
    colors: list[str] | None = None,
    direction: np.ndarray = RIGHT,
    buff: float = 0.6,
) -> tuple[VGroup, VGroup]:
    """Create a pipeline of labeled boxes with arrows.

    Returns
    -------
    boxes : VGroup
        The stage boxes.
    arrows : VGroup
        The connecting arrows.
    """
    if colors is None:
        colors = [PRIMARY] * len(stage_names)

    boxes = VGroup(*[
        labeled_box(name, color=c) for name, c in zip(stage_names, colors)
    ])
    boxes.arrange(direction, buff=buff)

    arrows = VGroup()
    for i in range(len(boxes) - 1):
        if np.array_equal(direction, RIGHT):
            arrow = Arrow(boxes[i][0].get_right(), boxes[i + 1][0].get_left(), buff=0.05)
        else:
            arrow = Arrow(boxes[i][0].get_bottom(), boxes[i + 1][0].get_top(), buff=0.05)
        arrows.add(arrow)

    return boxes, arrows


def data_table(
    headers: list[str],
    rows: list[list[str]],
    col_widths: list[float] | None = None,
) -> VGroup:
    """Create a simple data table."""
    if col_widths is None:
        col_widths = [2.0] * len(headers)

    table = VGroup()
    # Header row
    header_cells = VGroup()
    for j, (header, width) in enumerate(zip(headers, col_widths)):
        cell = VGroup(
            Rectangle(width=width, height=0.5, fill_color=GREY_D, fill_opacity=0.5, stroke_width=1),
            Text(header, font_size=18, weight=BOLD),
        )
        cell[1].move_to(cell[0])
        header_cells.add(cell)
    header_cells.arrange(RIGHT, buff=0)
    table.add(header_cells)

    # Data rows
    for row_data in rows:
        row_cells = VGroup()
        for j, (val, width) in enumerate(zip(row_data, col_widths)):
            cell = VGroup(
                Rectangle(width=width, height=0.4, stroke_width=0.5),
                Text(val, font_size=16),
            )
            cell[1].move_to(cell[0])
            row_cells.add(cell)
        row_cells.arrange(RIGHT, buff=0)
        table.add(row_cells)

    table.arrange(DOWN, buff=0)
    return table
```

## Scene File Pattern

Each scene file follows a consistent structure:

```python
# scenes/s01_intro.py
"""Scene 1: Introduction and hook."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *
from utils.style import TITLE_SIZE, BODY_SIZE
from utils.components import labeled_box


class S01Intro(Scene):
    def construct(self) -> None:
        # ── Title Card ──
        title = Text("Paper Title Here", font_size=TITLE_SIZE)
        subtitle = Text("Author et al., 2025", font_size=BODY_SIZE, color=GRAY)
        VGroup(title, subtitle).arrange(DOWN, buff=0.5)

        self.play(Write(title))
        self.play(FadeIn(subtitle, shift=UP * 0.3))
        self.wait(2)

        fade_scene_transition(self, title, subtitle)

        # ── Hook ──
        # ... rest of scene
```

## Scene Naming Conventions

- Files: `s01_intro.py`, `s02_background.py`, etc.
- Classes: `S01Intro`, `S02Background` (match file number)
- Output clips: `S01Intro.mp4`, etc.

For Remotion integration, rename outputs:

```bash
# Rename for Remotion
cp media/videos/s01_intro/1080p60/S01Intro.mp4 clips/clip_intro_01.mp4
```

## manim.cfg

```ini
[CLI]
quality = high_quality
fps = 30
media_dir = ./media
background_color = #1a1a2e
renderer = cairo
```

## render_all.sh

```bash
#!/bin/bash
# Render all scenes in order
set -euo pipefail

QUALITY="${1:--qh}"
FPS="${2:-30}"
FORMAT="${3:-mp4}"

echo "Rendering with quality=$QUALITY fps=$FPS format=$FORMAT"

for scene_file in scenes/s*.py; do
    scene_name=$(basename "$scene_file" .py)
    echo "=== Rendering $scene_name ==="
    manim "$QUALITY" --fps "$FPS" --format "$FORMAT" "$scene_file"
done

echo "=== All scenes rendered ==="
ls -la media/videos/*/
```

Make executable: `chmod +x render_all.sh`

## .gitignore

```gitignore
media/
__pycache__/
*.pyc
.DS_Store
*.log
```

## requirements.txt

```
manim>=0.18.0
numpy
```

## Tips

1. **Keep scenes under 300 lines.** Split complex scenes into helper functions in `utils/`.
2. **Import shared styles** in every scene file for visual consistency.
3. **Test at low quality first**: `manim -ql scenes/s01_intro.py` before rendering at high quality.
4. **Use `manim -s`** to render just the last frame when debugging layout.
5. **Number scene files** to maintain order: `s01_`, `s02_`, etc.
