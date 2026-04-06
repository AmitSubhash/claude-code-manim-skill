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

> **Browsing:** During the research phase, use `browser-use` (Bash) for reading
> papers, checking figures, and gathering reference material. Core workflow:
> `browser-use open <url>` -> `browser-use state` -> interact. See
> [paper-explainer.md](paper-explainer.md) for examples.

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

## Narrative Arc Templates

Choose one arc per video. The arc determines scene ordering and emotional pacing.

### Discovery Arc
question -> explore -> insight -> formalize

Best for: pure math, visual proofs, "why does X work?"
- Scene 1-2: Pose the question, show failed intuition
- Scene 3-5: Explore visually, let patterns emerge
- Scene 6-7: The "aha" insight
- Scene 8+: Formalize with equations, show generality

### Problem-Solution Arc
problem -> failed attempt -> key insight -> solution

Best for: engineering papers, optimization methods, systems design
- Scene 1-2: Show the problem concretely (slow, broken, expensive)
- Scene 3-4: Obvious approach and why it fails
- Scene 5: The key insight that changes everything
- Scene 6-8: Solution, results, implications

### Comparison Arc
method A -> method B -> head-to-head -> winner

Best for: benchmark papers, A-vs-B evaluations, technique surveys
- Scene 1-2: Method A explained
- Scene 3-4: Method B explained
- Scene 5-6: Head-to-head comparison (same data, same chart)
- Scene 7: Winner declared with concrete numbers

### Build-Up Arc
simple case -> add complexity -> full picture

Best for: tutorials, concept introductions, "from scratch" explanations
- Scene 1-2: Simplest possible version (1D, 2 elements, toy data)
- Scene 3-5: Add one dimension of complexity per scene
- Scene 6-7: Full real-world version
- Scene 8: Zoom out to see the complete picture

## Per-Scene Variation Checklist

Each scene MUST differ from its neighbors in at least 2 of these 4 dimensions:

1. **Dominant color** -- the primary color that fills the most screen area
2. **Layout template** -- FULL_CENTER, DUAL_PANEL, BUILD_UP, CHART_FOCUS, etc.
3. **Animation entry direction** -- elements entering from LEFT, RIGHT, UP, or scaling in
4. **Visual weight distribution** -- top-heavy, bottom-heavy, left-heavy, centered

If two adjacent scenes share the same layout AND the same dominant color, one of them
needs a redesign. Monotony kills engagement faster than complexity.

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

-- Layout & bounds --
1. Layout: Use the specified template. Never use absolute x > 5.5 or y > 3.2
2. Density: Fill 50%+ of frame. Bars: fill_opacity >= 0.6, width >= 0.3
3. Edge overflow: If a box is at |x| > 2.5, place auxiliary labels BELOW (DOWN),
   never further toward the screen edge. Do NOT write x-clamp guards.

-- Text --
4. Text: Use safe_text() for single lines. Use safe_multiline() for centered
   multi-line text. NEVER use \n inside Text() for centered displays.
5. Bottom notes: Use bottom_note() helper. Animate with FadeIn(note, shift=UP*0.2),
   NOT Write(). Write() creates ugly partial-stroke frames on small text.
6. Scaled layouts: When boxes will be shown at reduced size (split-view, header),
   use abbreviated labels ("I-Cache" not "Instruction Cache"). Text does not reflow.

-- Containers --
7. Containers: Child elements positioned relative to parent (next_to, move_to).
   Children inside a labeled_box() must be offset DOWN * 0.3 from center to avoid
   covering the label.

-- Lifecycle & transitions --
8. Lifecycle: FadeOut titles/headers COMPLETELY before new content appears in the
   top 25% of the frame. Dimming to 0.1 is NOT removal. FadeOut means FadeOut.
9. Overlay text: When text needs a clean background, FadeOut previous elements
   completely. Only dim (0.1 opacity) when the dimmed element stays BESIDE new
   content, never UNDER it.
10. Transitions: Combine FadeOut of previous phase with Write/FadeIn of next
    phase title in a SINGLE self.play() call. Never leave a frame with only a
    title and > 60% empty space.
11. Cleanup: FadeOut all elements before the next logical section.

-- Animations --
12. Animations: Write() for text, Create() for shapes, ReplacementTransform for
    equation chains. Use LaggedStart(*[Write(m) for m in group]) not
    LaggedStartMap(Write, group).
13. MathTex: No dollar signs. Use Tex for mixed text+math.
14. Updaters: self.wait(frozen_frame=False) when updaters are active.
15. DIM_OPACITY = 0.1, never 0.3. On dark backgrounds, 0.3 still competes.

-- Diagrams --
16. Arrows: Use pipeline_arrow() with buff=0.25. For arrows between boxes less
    than 1.5 units apart, increase buff to 0.3 or reduce tip size.
17. Chart legends: Place in the corner with LEAST data density. For rising
    curves, use lower-right. Never place where curves converge.
18. Exact metadata: Copy the exact paper title, author list, and year into the
    scene. Never guess or abbreviate author names.
```

### Section 3: Scene Plan (unique per agent)
The scene plan from the planning phase, including template, content
layout, equations, data, and cleanup instructions.

### Section 4: Scene Description (unique per agent)
The detailed creative description of what to show and how.

## style.py Template (Enhanced)

The planning phase should produce this enhanced style.py. Copy the template from
`templates/style.py` and customize the color palette for your domain.

Key helpers every project must have:

```python
from manim import *

# -- Colors (semantic names) --
PRIMARY = "#4A90D9"
SECONDARY = "#2ECC71"
ACCENT = "#F1C40F"
DANGER = "#E74C3C"
SUCCESS = "#27AE60"
DIM_OPACITY = 0.1  # never 0.3 on dark backgrounds

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

# -- Text Helpers --
def safe_text(text, font_size=BODY_SIZE, color=WHITE, max_width=12.0):
    """Single-line text with width cap."""
    t = Text(text, font_size=font_size, color=color)
    if t.width > max_width:
        t.scale_to_fit_width(max_width)
    return t

def safe_multiline(*lines, font_size=BODY_SIZE, color=WHITE,
                   line_buff=0.3, max_width=12.0):
    """Centered multi-line text. Avoids left-align bug with \\n in Text().
    Each line is a separate Text in a VGroup with center=True."""
    texts = []
    for line in lines:
        t = Text(line, font_size=font_size, color=color)
        if t.width > max_width:
            t.scale_to_fit_width(max_width)
        texts.append(t)
    return VGroup(*texts).arrange(DOWN, buff=line_buff, center=True)

def section_title(text, color=WHITE):
    return Text(text, font_size=TITLE_SIZE, color=color).to_edge(UP, buff=0.5)

def bottom_note(text, color=YELLOW):
    """Animate with FadeIn(shift=UP*0.2), NOT Write()."""
    t = Text(text, font_size=LABEL_SIZE, color=color)
    if t.width > SAFE_WIDTH:
        t.scale_to_fit_width(SAFE_WIDTH)
    return t.to_edge(DOWN, buff=0.5)

# -- Diagram Helpers --
def labeled_box(label, width=2.5, height=1.0, color=BLUE_C,
                font_size=LABEL_SIZE, fill_opacity=0.2):
    """Label sits at center. Child elements: offset DOWN * 0.3."""
    rect = RoundedRectangle(width=width, height=height, corner_radius=0.1,
                            color=color, fill_opacity=fill_opacity, stroke_width=2)
    text = Text(label, font_size=font_size, color=color)
    text.move_to(rect)
    if text.width > width - 0.3:
        text.scale_to_fit_width(width - 0.3)
    return VGroup(rect, text)

def pipeline_arrow(start, end, color=WHITE, stroke_width=3):
    """Arrow with buff=0.25 to prevent tip crowding between adjacent boxes."""
    return Arrow(start.get_right(), end.get_left(), buff=0.25,
                 color=color, stroke_width=stroke_width,
                 max_tip_length_to_length_ratio=0.15)

# -- Scene Helpers --
def fade_all(scene, *mobjects):
    if mobjects:
        scene.play(*[FadeOut(m) for m in mobjects])

def story_bridge(scene, text):
    bridge = Text(text, font_size=HEADING_SIZE, color=ACCENT)
    scene.play(FadeIn(bridge, shift=UP * 0.3))
    scene.wait(2.0)
    scene.play(FadeOut(bridge, shift=UP * 0.3))
```

## Audience-Level Curriculum Redesign

When the audience level changes (graduate to general, specialist to broad),
do NOT simplify existing scenes. Rebuild the curriculum from scratch.

**Why text simplification fails:** A graduate-level 10-scene video about
matrix optimization has zero background scenes. A general-audience version
needs 5-8 new foundational scenes (what is a matrix? what is a GPU? what
is memory hierarchy?) before the optimization content even begins. Simply
rewording the existing scenes leaves the viewer without the mental models
needed to follow the argument.

**The pattern:**
1. Identify what the NEW audience does not know (list explicitly)
2. Design new foundational scenes that build those mental models
3. Keep only the 3-5 scenes from the original that still apply
4. Rewrite those retained scenes with slower pacing and analogies
5. Add a recap/wrap-up scene that ties the new scaffolding to the conclusion

**Example:** NeuronMM paper, graduate (10 scenes) to general audience (15):
- Scenes 1-4 (NEW): What LLMs do, matrix multiplication from scratch, how CPUs work
- Scenes 5-8 (NEW): GPUs, memory hierarchy, bandwidth bottleneck, AI accelerators
- Scenes 9-12 (REBUILT): Trainium architecture, constraints, SVD (with analogies)
- Scenes 13-15 (ADAPTED): NeuronMM solution, results, wrap-up

Rule: audience redesign = curriculum redesign, not text replacement.

## Post-Generation Fix Cycle (Parallel Agents)

When 3-4 agents generate scenes in parallel, expect 1-3 runtime errors
that `py_compile` does not catch. Common categories:

| Error | Cause | Fix |
|---|---|---|
| `'str' has no attribute 'interpolate'` | Hex string passed to `interpolate_color()` | Wrap in `ManimColor()` |
| `IndexError` in animation | Animating a removed or never-added mobject | Check lifecycle order |
| Layout overflow | `next_to()` pushing element off-screen near edges | Use `move_to()` with explicit coords |
| Text truncation | Long label inside scaled-down container | Use abbreviated labels |

**Fix workflow:**
1. Run Phase 1+2 from "Multi-Scene Render Testing Workflow" (production-quality.md)
2. Fix each failing scene, re-test at `-ql`
3. Typically takes 1-2 fix iterations (10-20 min for 15 scenes)
4. Only then proceed to full `-qh` render

**File cleanup after renumbering:** When scene count or naming changes
(e.g., 10 -> 15 scenes, `scene_02_bottleneck.py` -> `scene_02_llm.py`),
explicitly remove old files:
```bash
# Check for orphans
ls scene_*.py | sort
git status  # shows deleted + untracked
# Remove old files, stage new ones
git rm scene_02_bottleneck.py
git add scene_02_llm.py
```

## Verification Phase

After all scenes render, extract 5 frames per scene (at 10%, 25%, 50%, 75%, 90%)
and visually check each frame:

### Overlap checks
1. No text overlapping other text
2. No text overlapping graphical elements (boxes, arrows, charts)
3. No elements clipped at screen edges
4. Child elements inside labeled_box do not cover the label
5. Chart legends do not overlap curve data
6. GRM/example tags do not stack on top of source boxes

### Density checks
7. No frames with only a title and > 60% empty space (transition gap)
8. Content fills >= 50% of frame at scene midpoint
9. Bottom notes fully visible (not truncated at edges)

### Consistency checks
10. Title position consistent across scenes (TITLE_Y = 3.0)
11. Colors match style.py semantic meanings
12. Paper metadata (title, authors) correct in final scene

### Text rendering checks
13. Multi-line text is properly centered (not left-aligned)
14. Scaled-down box labels are readable (not truncated to fragments)
15. Bottom notes are NOT mid-Write() at their final frame -- use FadeIn

### Common bugs to look for (from past audits)
- `next_to(box, RIGHT)` pushing elements off-screen when box is near edge
- `Text("line1\nline2")` left-aligning instead of centering
- Title still visible (at reduced opacity) when new content overlaps it
- "legit code" style blocks placed at box center covering the box label
- Pipeline elements at DIM_OPACITY still visible under overlay text
