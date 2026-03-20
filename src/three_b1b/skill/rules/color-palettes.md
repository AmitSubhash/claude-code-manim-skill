---
name: Color Palettes
description: Curated color palettes for Manim animations - academic, dark mode, accessible, and domain-specific schemes
tags: [manim, colors, palette, accessibility, styling, design]
---

# Color Palettes for Manim

## Why color choices matter

Color serves three purposes in mathematical animation:
1. **Semantic encoding**: "blue always means input, red always means loss" - viewers learn the vocabulary
2. **Attention direction**: bright/warm colors draw the eye; dim/cool colors recede
3. **Accessibility**: ~8% of men have color vision deficiency - your palette must work for them too

## Manim's built-in color system

Manim provides ~170 predefined color constants. Each base color has variants A (lightest) through E (darkest):

```python
BLUE_A  # lightest blue
BLUE_B
BLUE_C  # = BLUE (the default)
BLUE_D
BLUE_E  # darkest blue
```

Available bases: BLUE, RED, GREEN, YELLOW, GOLD, PURPLE, MAROON, TEAL, PINK, ORANGE, GRAY

Special: WHITE, BLACK, PURE_RED, PURE_GREEN, PURE_BLUE

Custom hex: `ManimColor("#1F77B4")`

## Recommended palettes

### Academic (light, publication-style on dark background)

Best for: conference talks, paper figures, formal presentations

```python
# style.py
PALETTE_ACADEMIC = {
    "primary": BLUE_C,        # main objects, axes
    "secondary": RED_C,       # comparison, alternative
    "accent": YELLOW_C,       # highlights, annotations
    "positive": GREEN_C,      # correct, increase, gain
    "negative": RED_D,        # error, decrease, loss
    "neutral": GRAY_B,        # labels, secondary text
    "background": BLACK,      # Manim default
}
```

### Vibrant (high contrast, 3Blue1Brown style)

Best for: YouTube, teaching videos, maximum visual impact

```python
PALETTE_VIBRANT = {
    "primary": BLUE,
    "secondary": YELLOW,
    "tertiary": GREEN,
    "highlight": PURE_YELLOW,
    "emphasis": RED,
    "subtle": GRAY,
    "background": "#1C1C1C",   # slightly lighter than pure black
}
```

### Colorblind-safe (deuteranopia-friendly)

Best for: any public-facing content. Uses blue-orange instead of red-green.

```python
PALETTE_ACCESSIBLE = {
    "primary": "#0077BB",      # blue
    "secondary": "#EE7733",    # orange
    "tertiary": "#009988",     # teal
    "highlight": "#DDAA33",    # gold
    "negative": "#CC3311",     # vermillion (distinct from orange)
    "neutral": "#BBBBBB",      # gray
    "background": "#000000",
}
```

**Test your palette:** View your render in grayscale (desaturate in any image viewer). If you can still distinguish all elements, your palette works for most color vision deficiencies.

### ML paper palette

Best for: architecture diagrams, training curves, attention visualizations

```python
PALETTE_ML = {
    "input": GREEN_C,          # input data, embeddings
    "encoder": BLUE_C,         # encoding layers
    "decoder": PURPLE_C,       # decoding layers
    "attention": YELLOW_C,     # attention weights
    "loss": RED_C,             # loss values, errors
    "output": TEAL_C,          # predictions, output
    "label": GRAY_B,           # text labels
}
```

### Physics/Engineering palette

```python
PALETTE_PHYSICS = {
    "field": BLUE_C,           # fields, potentials
    "source": RED_C,           # sources, charges
    "detector": GREEN_C,       # detectors, measurements
    "wave": YELLOW_C,          # waves, oscillations
    "boundary": WHITE,         # boundaries, interfaces
    "annotation": GRAY_B,     # labels, dimensions
}
```

### Biomedical palette

```python
PALETTE_BIO = {
    "tissue": PINK,            # biological tissue
    "signal": GREEN_C,         # detected signals
    "source_light": RED_C,     # light sources, lasers
    "detector": BLUE_C,        # detectors, sensors
    "reconstruction": YELLOW_C, # reconstructed images
    "reference": GRAY_B,       # reference, baseline
}
```

## How to use a palette consistently

Create a `style.py` file and import it in every scene:

```python
# style.py
from manim import *

# Choose your palette
C = {
    "primary": BLUE_C,
    "secondary": RED_C,
    "accent": YELLOW_C,
    "positive": GREEN_C,
    "negative": RED_D,
    "dim": GRAY,
}

TITLE_SIZE = 64
BODY_SIZE = 40
LABEL_SIZE = 28
```

```python
# scenes/s01_intro.py
from manim import *
from style import C, TITLE_SIZE

class Intro(Scene):
    def construct(self):
        title = Text("My Paper", font_size=TITLE_SIZE, color=C["primary"])
        # ...
```

## Color operations

```python
from manim.utils.color import interpolate_color, color_gradient

# Blend two colors
mid = interpolate_color(RED, BLUE, 0.5)  # alpha=0.5 = halfway

# Create a gradient (list of N colors from start to end)
gradient = color_gradient([BLUE, GREEN, YELLOW], 10)  # 10 colors

# Set a gradient on a mobject
mob.set_color_by_gradient(BLUE, RED)  # left-to-right gradient

# Height-based coloring for 3D surfaces
surface.set_fill_by_value(
    axes,
    colorscale=[(RED, -1), (YELLOW, 0), (GREEN, 1)],
    axis=2,  # z-axis
)
```

## Anti-patterns

1. **Using red and green together** for important distinctions - 8% of viewers cannot tell them apart
2. **Too many colors** in one scene - limit to 4-5 distinct colors max
3. **Changing a color's meaning** between scenes - if blue means "input" in scene 1, keep it
4. **Pure white on pure black** for large areas - it creates harsh contrast. Use GRAY_B for labels
5. **Neon/saturated colors for large fills** - use lower opacity (0.3-0.5) for fills, full saturation for strokes only
