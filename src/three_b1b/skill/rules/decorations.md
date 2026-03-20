---
name: Decorations and Annotations
description: Annotations, highlights, braces, arrows, and labeling patterns for Manim
tags: [manim, annotations, brace, arrow, highlight, decoration]
---

# Decorations and Annotations

## Conceptual Overview

What are decorations? Decorations are visual annotations you add ON TOP of existing Mobjects to draw the viewer's attention. They solve the problem of "I have an equation on screen, how do I point at a specific part?" SurroundingRectangle highlights a region, Brace labels a span, Arrow connects two things. Decorations are Mobjects themselves, so you can animate them independently (Create, FadeIn, FadeOut, Transform).

The typical workflow: (1) create the main content (equation, diagram), (2) isolate the part you want to annotate (using `get_part_by_tex` or indexing), (3) create a decoration anchored to that part, (4) animate the decoration in and out. Since decorations are just Mobjects, you can group them, transform them, and layer multiple annotations in sequence.

## SurroundingRectangle

Draw a rectangle around any mobject:

```python
from manim import *

eq = MathTex(r"E = mc^2")
rect = SurroundingRectangle(
    eq,
    color=YELLOW,
    buff=0.15,              # padding around mobject
    corner_radius=0.1,      # rounded corners
    stroke_width=2,
)
self.play(Write(eq), Create(rect))
```

### Around a sub-part of an equation

```python
eq = MathTex(r"{{ F }} = {{ m }} {{ a }}")
m_part = eq.get_part_by_tex("m")
rect = SurroundingRectangle(m_part, color=RED, buff=0.1)
self.play(Create(rect))
```

## BackgroundRectangle

Adds a filled rectangle behind a mobject (useful for readability over complex backgrounds):

```python
label = MathTex(r"\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}")
bg = BackgroundRectangle(
    label,
    fill_opacity=0.8,
    fill_color=BLACK,
    buff=0.15,
)
self.add(bg, label)  # bg must be added first (behind label)
```

## Cross

Draw an X through a mobject (for "cancel" or "wrong" indication):

```python
wrong_eq = MathTex(r"1 + 1 = 3")
cross = Cross(
    wrong_eq,
    stroke_color=RED,
    stroke_width=6,
)
self.play(Write(wrong_eq))
self.play(Create(cross))
```

## Underline

```python
title = Text("Important Result")
underline = Underline(title, color=YELLOW, buff=0.1)
self.play(Write(title), Create(underline))
```

## Brace

A curly brace along one side of a mobject:

```python
group = VGroup(Square(), Square(), Square()).arrange(RIGHT, buff=0.3)
brace = Brace(
    group,
    direction=DOWN,     # which side to place the brace
    buff=0.1,
    sharpness=1.0,      # higher = more pointy
)
label = brace.get_text("Three squares")  # plain text label
# or:
tex_label = brace.get_tex(r"n = 3")      # LaTeX label

self.play(Create(brace), Write(label))
```

## BraceBetweenPoints

Place a brace between two arbitrary points:

```python
brace = BraceBetweenPoints(
    LEFT * 2,
    RIGHT * 2,
    direction=DOWN,
)
label = brace.get_tex(r"L = 4")
```

## Arrows

### Straight arrows

```python
arrow = Arrow(
    start=LEFT * 2,
    end=RIGHT * 2,
    buff=0,            # 0 to touch endpoints, >0 for gap
    stroke_width=4,
    tip_length=0.25,
    color=WHITE,
)
self.play(GrowArrow(arrow))
```

### Curved arrows

```python
# Single-headed curved arrow
c_arrow = CurvedArrow(
    start_point=LEFT * 2 + UP,
    end_point=RIGHT * 2 + UP,
    color=YELLOW,
)

# Double-headed curved arrow
dc_arrow = CurvedDoubleArrow(
    start_point=LEFT * 2,
    end_point=RIGHT * 2,
)
```

### Arrow pointing to a mobject

```python
target = Circle(radius=0.5).shift(RIGHT * 2)
arrow = Arrow(LEFT * 2, target.get_left(), buff=0.1, color=YELLOW)
label = Text("Look here", font_size=24).next_to(arrow, UP)
```

## DashedLine and DashedVMobject

```python
# Dashed line
dashed = DashedLine(LEFT * 3, RIGHT * 3, dash_length=0.2, color=GRAY)

# Make any VMobject dashed
circle = Circle(radius=1.5)
dashed_circle = DashedVMobject(circle, num_dashes=20)
```

## Annotating Equations

The standard annotation workflow: isolate a term, surround it, add a brace or arrow with a label.

```python
class AnnotatedEquation(Scene):
    def construct(self) -> None:
        eq = MathTex(
            r"{{ F }} = {{ m }} {{ a }}",
            font_size=64,
        )
        eq.set_color_by_tex("F", YELLOW)
        eq.set_color_by_tex("m", RED)
        eq.set_color_by_tex("a", BLUE)
        self.play(Write(eq))

        # Highlight force
        f_part = eq.get_part_by_tex("F")
        f_rect = SurroundingRectangle(f_part, color=YELLOW, buff=0.1)
        f_label = Text("Force", font_size=24, color=YELLOW).next_to(f_rect, UP)
        self.play(Create(f_rect), Write(f_label))
        self.wait()

        # Brace under mass
        m_part = eq.get_part_by_tex("m")
        m_brace = Brace(m_part, DOWN, buff=0.1)
        m_label = m_brace.get_text("mass", font_size=24).set_color(RED)
        self.play(
            FadeOut(f_rect, f_label),
            Create(m_brace),
            Write(m_label),
        )
        self.wait()

        # Arrow pointing to acceleration
        a_part = eq.get_part_by_tex("a")
        a_arrow = Arrow(
            a_part.get_right() + RIGHT * 1.5,
            a_part.get_right(),
            buff=0.1,
            color=BLUE,
        )
        a_label = Text("acceleration", font_size=24, color=BLUE).next_to(a_arrow, RIGHT)
        self.play(
            FadeOut(m_brace, m_label),
            GrowArrow(a_arrow),
            Write(a_label),
        )
        self.wait()
```

## Labeling with next_to

Position labels relative to any mobject:

```python
# Directions: UP, DOWN, LEFT, RIGHT, UL, UR, DL, DR
label.next_to(mob, UP, buff=0.2)

# Align edge
label.next_to(mob, RIGHT, aligned_edge=UP)
```

## Color Highlighting Workflow

### Method 1: tex_to_color_map at creation

```python
eq = MathTex(
    r"\frac{\partial u}{\partial t} = \alpha \nabla^2 u",
    tex_to_color_map={
        r"\partial u": BLUE,
        r"\alpha": RED,
        r"\nabla^2": GREEN,
    },
)
```

### Method 2: set_color_by_tex after creation

```python
eq = MathTex(r"{{ \vec{F} }} = q({{ \vec{E} }} + {{ \vec{v} }} \times {{ \vec{B} }})")
eq.set_color_by_tex(r"\vec{F}", YELLOW)
eq.set_color_by_tex(r"\vec{E}", RED)
eq.set_color_by_tex(r"\vec{v}", GREEN)
eq.set_color_by_tex(r"\vec{B}", BLUE)
```

### Method 3: Index into submobjects

```python
eq = MathTex("a", "+", "b", "=", "c")
eq[0].set_color(RED)    # "a"
eq[2].set_color(BLUE)   # "b"
eq[4].set_color(GREEN)  # "c"
```

## Combining Multiple Annotations

```python
class MultiAnnotation(Scene):
    def construct(self) -> None:
        eq = MathTex(
            r"{{ \mathcal{L} }} = {{ \frac{1}{2} }} {{ m }} {{ v^2 }} - {{ V(x) }}",
            font_size=52,
        )
        self.play(Write(eq))

        # Annotate kinetic energy
        ke_parts = VGroup(eq.get_part_by_tex(r"\frac{1}{2}"), eq.get_part_by_tex("m"), eq.get_part_by_tex("v^2"))
        ke_brace = Brace(ke_parts, DOWN, color=BLUE)
        ke_label = ke_brace.get_tex(r"T = \text{kinetic energy}").set_color(BLUE).scale(0.7)

        self.play(Create(ke_brace), Write(ke_label))
        self.wait()

        # Annotate potential energy
        pe_part = eq.get_part_by_tex("V(x)")
        pe_brace = Brace(pe_part, DOWN, color=RED)
        pe_label = pe_brace.get_tex(r"V = \text{potential energy}").set_color(RED).scale(0.7)

        self.play(
            FadeOut(ke_brace, ke_label),
            Create(pe_brace),
            Write(pe_label),
        )
        self.wait()
```
