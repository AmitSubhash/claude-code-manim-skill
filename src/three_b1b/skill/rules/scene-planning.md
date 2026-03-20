---
name: Scene Planning and Agent Dispatch
description: How to plan scene layouts, write agent prompts, and dispatch parallel scene agents for paper explainer videos
tags: [manim, planning, layout, agents, workflow, architecture]
---

# Scene Planning and Agent Dispatch

This file defines the planning phase that happens BETWEEN curriculum design
and code generation. It produces the spatial blueprints and agent prompts
that prevent layout errors, empty frames, and cross-scene inconsistency.

## The Planning Pipeline

```
research.md -> curriculum (scene list) -> SCENE PLANS -> style.py -> agents
                                            ^^^^^^^^^
                                         THIS IS NEW
```

A scene plan specifies WHAT goes WHERE for each scene. Without it, agents
invent their own layouts and 30-40% of scenes have spatial bugs.

## Layout Templates

Every scene should use one of these 6 templates. Pick the template during
planning, include it in the agent prompt.

### Template 1: FULL_CENTER
One main element centered with title above and note below.
Best for: equations, single diagrams, analogies.

```
+--------------------------------------------------+
|  Title (y=3.0)                                    |
|                                                    |
|              [Main content centered]               |
|              x=[-4, 4], y=[-1.5, 2.0]             |
|                                                    |
|  Bottom note (y=-3.2)                             |
+--------------------------------------------------+
```

### Template 2: DUAL_PANEL
Left and right panels for comparison scenes.
Best for: inverse vs forward, L2 vs cosine, before vs after.

```
+--------------------------------------------------+
|  Title (y=3.0)                                    |
|                                                    |
|  LEFT_PANEL        |  RIGHT_PANEL                  |
|  x=[-6, -0.8]     |  x=[0.8, 6]                   |
|  y=[-2, 2.2]      |  y=[-2, 2.2]                  |
|                    |                                |
|  Bottom note (y=-3.2)                             |
+--------------------------------------------------+
```

### Template 3: TOP_PERSISTENT_BOTTOM_CONTENT
A small persistent element at top (pipeline, header) with main
content below. The persistent element stays while content changes.
Best for: pipeline + details, method overview + zoom-ins.

```
+--------------------------------------------------+
|  [Persistent element, scaled 0.5-0.6x]           |
|  y=[2.0, 3.2]                                    |
|--------------------------------------------------|
|  Subtitle (y=1.5)                                |
|                                                    |
|  [Main content]                                   |
|  x=[-5, 5], y=[-2, 1.2]                          |
|                                                    |
|  Bottom note (y=-3.2)                             |
+--------------------------------------------------+
```

CRITICAL: Fade out the title BEFORE moving the persistent element up.

### Template 4: BUILD_UP
Progressive construction where elements accumulate.
Best for: signal model assembly, equation building, pipeline reveal.

```
+--------------------------------------------------+
|  Title (y=3.0)                                    |
|                                                    |
|  [Elements appear one by one]                     |
|  Each new element positioned relative to previous |
|  Use VGroup + arrange() or next_to()              |
|                                                    |
|  [Equation/summary builds at bottom]              |
|  y=[-2.5, -1.0]                                  |
|                                                    |
|  Bottom note (y=-3.2)                             |
+--------------------------------------------------+
```

### Template 5: CHART_FOCUS
Data visualization with axes as the main element.
Best for: performance comparisons, parameter sweeps, histograms.

```
+--------------------------------------------------+
|  Title (y=3.0)                                    |
|                                                    |
|  [Axes spanning most of the frame]                |
|  axes = Axes(x_range, y_range,                    |
|      x_length=9, y_length=4.5,                   |
|  ).shift(DOWN * 0.3)                              |
|  Legend in corner (UR or UL)                       |
|                                                    |
|  Bottom note (y=-3.2)                             |
+--------------------------------------------------+
```

### Template 6: GRID_CARDS
Multiple cards/boxes arranged in a grid.
Best for: metric displays, output maps, feature lists.

```
+--------------------------------------------------+
|  Title (y=3.0)                                    |
|                                                    |
|  [Source element at top center, y=1.5-2.2]        |
|                                                    |
|  [Cards in arrange_in_grid or arrange(RIGHT)]     |
|  VGroup(*cards).arrange_in_grid(rows, cols)       |
|  .move_to(DOWN * 0.5)                             |
|                                                    |
|  Bottom note (y=-3.2)                             |
+--------------------------------------------------+
```

## Scene Plan Format

During planning, write a scene plan for each scene:

```
## Scene N: ClassName (~duration)
Template: DUAL_PANEL
Content:
- LEFT: [what goes in left panel]
- RIGHT: [what goes in right panel]
- BOTTOM: [bottom note text]
Visual anchors: [key shapes/elements that persist]
Cleanup: [what to FadeOut before next section]
Equations: [list any MathTex strings, pre-validated]
Data: [any numbers, percentages, or chart data from paper]
```

This goes into the agent prompt verbatim.

## Agent Prompt Structure

Each scene agent prompt has 4 sections:

### Section 1: Context (copy-paste)
```
You are writing ONE Manim Scene class for a research paper explainer.
Paper: [exact title]
Authors: [exact author list from paper]
Year: [year]

Read style.py at [path]. Import: from style import *
```

### Section 2: Rules (copy-paste, same for ALL agents)
```
RULES (mandatory, non-negotiable):
1. Layout: Use the specified template. Never use absolute x > 5.5 or y > 3.2
2. Text: Use safe_text() for body/notes. Max width 12 Manim units
3. Containers: Child elements positioned relative to parent (next_to, move_to)
4. Lifecycle: FadeOut titles/headers before new content reuses their region
5. Density: Fill 50%+ of frame. Bars: fill_opacity >= 0.6, width >= 0.3
6. Cleanup: FadeOut all elements before the next logical section
7. MathTex: No dollar signs. Use Tex for mixed text+math
8. Animations: Write() for text, Create() for shapes, ReplacementTransform for eq chains
9. Bottom text: buff >= 0.5, FadeOut previous before adding new
10. Updaters: self.wait(frozen_frame=False) when updaters are active
```

### Section 3: Scene Plan (unique per agent)
The scene plan from the planning phase, including template, content
layout, equations, data, and cleanup instructions.

### Section 4: Scene Description (unique per agent)
The detailed creative description of what to show and how.

## style.py Template (Enhanced)

The planning phase should produce this enhanced style.py:

```python
from manim import *

# -- Colors (semantic names) --
PRIMARY = "#4A90D9"
SECONDARY = "#2ECC71"
ACCENT = "#F1C40F"
DANGER = "#E74C3C"
SUCCESS = "#27AE60"
# ... domain-specific colors ...

# -- Font Sizes --
TITLE_SIZE = 42
HEADING_SIZE = 34
BODY_SIZE = 28
LABEL_SIZE = 22
EQ_SIZE = 32
SMALL_EQ = 26

# -- Layout System --
TITLE_Y = 3.0
BOTTOM_Y = -3.2
LEFT_X = -3.5
RIGHT_X = 3.5
SAFE_WIDTH = 12.0
SAFE_HEIGHT = 6.0

# -- Safe Helpers --
def section_title(text, color=WHITE):
    return Text(text, font_size=TITLE_SIZE, color=color).to_edge(UP, buff=0.5)

def safe_text(text, font_size=BODY_SIZE, color=WHITE, max_width=12.0):
    t = Text(text, font_size=font_size, color=color)
    if t.width > max_width:
        t.scale_to_fit_width(max_width)
    return t

def bottom_note(text, color=YELLOW):
    t = Text(text, font_size=LABEL_SIZE, color=color)
    if t.width > SAFE_WIDTH:
        t.scale_to_fit_width(SAFE_WIDTH)
    return t.to_edge(DOWN, buff=0.5)

def fade_all(scene, *mobjects):
    if mobjects:
        scene.play(*[FadeOut(m) for m in mobjects])
```

## Verification Phase

After all scenes render, extract 3 frames per scene (start, mid, end)
and visually check:

1. No elements clipped at screen edges
2. No large empty regions (> 40% of frame)
3. No overlapping text/elements
4. Consistent title position across scenes
5. Bottom notes fully visible
6. Data viz elements clearly visible (not too small/dark)
7. Paper metadata (title, authors) correct in final scene
