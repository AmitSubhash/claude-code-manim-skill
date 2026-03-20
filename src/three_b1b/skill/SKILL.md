---
name: manim
description: Use when the user wants to create mathematical animations, research paper explainer videos, equation derivations, 3D visualizations, or any programmatic animation with Manim. Also trigger when the user mentions "3Blue1Brown style", "animate this equation", "explain this paper visually", or wants to render LaTeX equations as video.
metadata:
  tags: manim, animation, math, visualization, latex, 3blue1brown, video, research
---

## When to use

Trigger this skill when:
- User wants to create a mathematical animation or render an equation as video
- User asks to explain a research paper visually or create an explainer video
- User mentions Manim, 3Blue1Brown, or mathematical visualization
- User wants to animate a derivation, diagram, pipeline, or architecture
- User needs Remotion + Manim integration for a production video

**Default to Manim Community Edition** (`pip install manim`) unless the user specifically needs ManimGL's interactive features.

## Gotchas (read these first)

These are the most common failures. Load [rules/troubleshooting.md](rules/troubleshooting.md) for the full list.

1. **`Create(Text(...))` looks wrong** -- use `Write()` for text. `Create()` traces outlines.
2. **Arrow with `interpolate_color()` crashes** -- use a plain color constant, adjust opacity separately.
3. **`Brace.get_text("label", font_size=24)` crashes** -- create `Tex` separately, use `brace.put_at_tip()`.
4. **`MathTex(r"$E=mc^2$")` crashes** -- MathTex is already math mode. Drop the `$`. Use `Tex` for mixed text+math.
5. **`Transform(A, B)` then animating B does nothing** -- B was never added. Use `ReplacementTransform`.
6. **Chained `Transform(a,b)` then `Transform(a,c)`** -- a is still the scene object. b and c are ghosts. Use `ReplacementTransform` each step.
7. **`LaggedStartMap(Write, group)` crashes** -- use `LaggedStart(*[Write(m) for m in group])`.
8. **Updaters freeze during `self.wait()`** -- add `frozen_frame=False`.
9. **`.animate.shift(R).scale(2)` != `.animate.scale(2).shift(R)`** -- chain order matters after scaling.
10. **`get_part_by_tex("missing")` returns None silently** -- check before calling `.set_color()` on the result.
11. **`reference = mob` is NOT a copy** -- use `mob.copy()` for independent objects.
12. **Transparent background** -- mp4 has no alpha. Use `--format webm -t`.

## Scripts and Templates

Claude can copy and adapt these starter files instead of writing from scratch:

- [scripts/safe_manim.py](scripts/safe_manim.py) -- drop-in wrappers that prevent the 6 crash gotchas (import instead of raw Manim calls)
- [scripts/render_scene.sh](scripts/render_scene.sh) -- render a single scene with quality selection
- [templates/style.py](templates/style.py) -- shared color palette and helper functions for any project
- [templates/equation_explainer.py](templates/equation_explainer.py) -- dim-and-reveal equation scene template
- [templates/paper_explainer.py](templates/paper_explainer.py) -- 5-section paper explainer scaffold

## Quick Start

```python
from manim import *

class MyScene(Scene):
    def construct(self):
        eq = MathTex(r"e^{i\pi} + 1 = 0")
        self.play(Write(eq))
        self.wait()
```

```bash
manim -pql scene.py MyScene    # preview, low quality (fast)
manim -pqh scene.py MyScene    # preview, high quality (1080p)
```

## Rule Files

Load the relevant rule file for the task at hand. Claude should read only what it needs, not all files at once.

### Core (read first if unfamiliar with Manim)
- [rules/first-scene-tutorial.md](rules/first-scene-tutorial.md) -- install, hello world, render commands
- [rules/mobjects.md](rules/mobjects.md) -- Mobject hierarchy, positioning, styling, VGroup
- [rules/animations.md](rules/animations.md) -- animation lifecycle, Transform, rate functions, composition
- [rules/scene-lifecycle.md](rules/scene-lifecycle.md) -- Scene types, construct(), play/wait/add/remove

### Equations and Math
- [rules/equations.md](rules/equations.md) -- MathTex, submobjects, {{ }} notation, TransformMatchingTex
- [rules/equation-derivations.md](rules/equation-derivations.md) -- dim-and-reveal, step-by-step, worked examples
- [rules/graphs-plots.md](rules/graphs-plots.md) -- Axes, plots, parametric curves, BarChart
- [rules/matrices-linalg.md](rules/matrices-linalg.md) -- Matrix, linear transformations
- [rules/decorations.md](rules/decorations.md) -- SurroundingRectangle, Brace, Arrow annotations

### Dynamic and 3D
- [rules/updaters-trackers.md](rules/updaters-trackers.md) -- ValueTracker, add_updater, always_redraw
- [rules/three-d.md](rules/three-d.md) -- ThreeDScene, camera angles, surfaces, 3D shapes
- [rules/moving-camera.md](rules/moving-camera.md) -- MovingCameraScene, zoom, pan, follow

### Visual Design (read for any explainer video)
- [rules/visual-design-principles.md](rules/visual-design-principles.md) -- **12 core principles** from Tufte, Bret Victor, 3Blue1Brown: opacity layering, persistent context, geometry before algebra, question frames, concrete values
- [rules/visual-design-catalog.md](rules/visual-design-catalog.md) -- **22 implementable patterns** from 3b1b frame analysis (422 frames): probability sidebars, skip arcs, grid fills, interactive sliders, heatmaps, and more

### Video Production
- [rules/scene-planning.md](rules/scene-planning.md) -- **START HERE for multi-scene videos.** Layout templates, scene plans, agent prompt structure, style.py contract
- [rules/paper-explainer.md](rules/paper-explainer.md) -- explainer video structure, domain patterns
- [rules/production-quality.md](rules/production-quality.md) -- spatial layout, alignment, container bounds, data viz minimums, pre/post-render quality checks
- [rules/animation-design-thinking.md](rules/animation-design-thinking.md) -- pacing, narration sync, animate vs static
- [rules/project-organization.md](rules/project-organization.md) -- multi-scene projects, style.py, render scripts
- [rules/remotion-integration.md](rules/remotion-integration.md) -- Manim + Remotion pipeline

### Reference
- [rules/config-rendering.md](rules/config-rendering.md) -- quality presets, CLI flags, output formats
- [rules/color-palettes.md](rules/color-palettes.md) -- accessible palettes, color operations
- [rules/troubleshooting.md](rules/troubleshooting.md) -- common errors and fixes
- [rules/manimgl-differences.md](rules/manimgl-differences.md) -- CE vs ManimGL comparison
