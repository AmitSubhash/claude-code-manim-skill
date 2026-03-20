---
name: LaTeX Equation Animation
description: First-principles guide to animating LaTeX equations in Manim - from rendering basics through step-by-step derivations
tags: [manim, latex, equations, animation, math, first-principles]
---

# LaTeX Equation Animation - From Scratch

## What happens when Manim renders an equation

When you write `MathTex(r"E = mc^2")`, Manim does the following behind the scenes:

1. **Compiles LaTeX**: Manim sends your string to a LaTeX compiler (pdflatex/xelatex), which typesets the math beautifully
2. **Converts to SVG**: The compiled output is converted to SVG vector paths
3. **Creates a Mobject**: Each SVG path becomes a Manim object (a "Mobject" - short for Mathematical Object) that you can position, color, scale, and animate

The result is NOT a static image. It is a collection of vector curves that Manim can manipulate individually. This is the key insight: every glyph, every symbol in your equation is a separate animatable piece.

## MathTex: Your primary equation tool

`MathTex` renders its input in LaTeX math mode (specifically `align*` environment). You do not need `$...$` delimiters:

```python
from manim import *

# This renders the equation as a collection of vector paths
eq = MathTex(r"E = mc^2")

# eq is now a Mobject. You can:
eq.set_color(BLUE)           # change its color
eq.scale(2)                  # double its size
eq.move_to(UP * 2)           # position it on screen
eq.rotate(PI / 4)            # rotate 45 degrees
```

For mixed text and math, use `Tex` instead (which uses LaTeX text mode, requiring `$...$` for math):

```python
label = Tex(r"Einstein's equation: $E = mc^2$")
```

**When to use which:**
- `MathTex` - pure math: integrals, fractions, Greek letters, equations
- `Tex` - text with occasional math, labels, descriptions

## The submobject concept (critical to understand)

When Manim renders `MathTex(r"a + b = c")`, it creates ONE object containing all the glyphs. The entire equation is a single unit. You cannot individually animate the "a" or the "b" - they are fused together.

This is a problem. To animate a derivation step by step, you NEED to target individual terms. That is what "submobjects" solve.

**A submobject is a child object inside a parent.** Think of it like a Python list: the parent equation contains child elements you can access by index.

There are three ways to split an equation into addressable submobjects:

### Method 1: Double-brace notation `{{ }}`

Wrap each piece you want to target in double braces:

```python
eq = MathTex(r"{{ a^2 }} + {{ b^2 }} = {{ c^2 }}")
```

Manim now creates 5 submobjects (the `+` and `=` between groups also become submobjects):

```python
eq[0]  # submobject containing "a^2"
eq[1]  # submobject containing "+"
eq[2]  # submobject containing "b^2"
eq[3]  # submobject containing "="
eq[4]  # submobject containing "c^2"
```

**Why double braces?** Single braces `{ }` already have meaning in LaTeX (grouping). Manim uses `{{ }}` as its own delimiter that does NOT interfere with LaTeX syntax. The rule: `{{ }}` must appear at the start of the string or after whitespace to be recognized.

### Method 2: Multiple string arguments

Pass each piece as a separate argument:

```python
eq = MathTex("a^2", "+", "b^2", "=", "c^2")
# Same result: eq[0] is "a^2", eq[1] is "+", etc.
```

This is equivalent to double-brace notation. Use whichever reads more clearly.

### Method 3: substrings_to_isolate

Tell Manim which substrings to split on automatically:

```python
eq = MathTex(
    r"a^2 + b^2 = c^2",
    substrings_to_isolate=["a^2", "b^2", "c^2"]
)
```

**When to use each:**
- `{{ }}` - when you want precise control over exactly what is grouped
- Multiple args - when each piece is short and clearly separate
- `substrings_to_isolate` - when your LaTeX is long and you only need to target specific parts

## Coloring specific terms

### At creation time: tex_to_color_map

```python
# RED, BLUE, GREEN are predefined Manim color constants
eq = MathTex(
    r"x^2 + y^2 = r^2",
    tex_to_color_map={"x": RED, "y": BLUE, "r": GREEN}
)
# Every occurrence of "x" is red, "y" is blue, "r" is green
```

This works by internally using `substrings_to_isolate` to find and color those substrings.

### After creation: set_color_by_tex

```python
eq = MathTex(r"{{ F }} = {{ m }} {{ a }}")
eq.set_color_by_tex("F", YELLOW)
eq.set_color_by_tex("m", RED)
eq.set_color_by_tex("a", BLUE)
```

### Accessing a specific part

`get_part_by_tex()` returns the submobject matching that LaTeX string. It returns a Mobject (or None if not found), so you can use any Mobject method on it:

```python
f_part = eq.get_part_by_tex("F")  # returns a VMobject reference
f_part.set_color(YELLOW)          # colors it in the equation
f_part.scale(1.5)                 # enlarges just that term
```

**Important:** `f_part` is NOT a copy. It is the actual submobject inside `eq`. Modifying it modifies the equation.

### Dimming everything except one term

```python
eq.set_opacity_by_tex("F", 1.0, remaining_opacity=0.3)
# "F" stays fully opaque; everything else dims to 30%
```

## Animating equation transformations

This is where Manim truly shines: morphing one equation into another while keeping matching parts visually connected.

### The problem TransformMatchingTex solves

Imagine you have two equations:
- `a^2 + b^2 = c^2`
- `a^2 = c^2 - b^2`

You want the "a^2" to stay in place, the "c^2" to slide to the right side, and the "b^2" to move and get a minus sign. `TransformMatchingTex` does exactly this: it looks at each submobject's LaTeX source string, finds matches between the two equations, and morphs matching parts into each other.

### How it works

1. You create both equations with `{{ }}` groups
2. Manim examines each submobject's `tex_string` property (the LaTeX source that created it)
3. Submobjects with identical `tex_string` values are matched and morphed
4. Unmatched submobjects fade out (source) or fade in (target)

```python
class DerivationStep(Scene):
    def construct(self) -> None:
        # Both equations use {{ }} to create matchable parts
        eq1 = MathTex(r"{{ a^2 }} + {{ b^2 }} = {{ c^2 }}")
        eq2 = MathTex(r"{{ a^2 }} = {{ c^2 }} - {{ b^2 }}")

        # Write writes the equation with a handwriting-like animation
        # self.play() runs animations and renders frames to the video
        self.play(Write(eq1))
        self.wait()  # pause 1 second so viewer can read

        # Morph eq1 into eq2: "a^2" matches "a^2", "b^2" matches "b^2", etc.
        # The "+" has no match in eq2 (fades out), "-" has no match in eq1 (fades in)
        self.play(TransformMatchingTex(eq1, eq2))
        self.wait()
```

### What happens to unmatched parts

By default, unmatched source parts fade out toward the target, and unmatched target parts fade in. You can change this:

```python
# Morph unmatched parts into each other (looks like they transform)
self.play(TransformMatchingTex(eq1, eq2, transform_mismatches=True))

# Cross-fade unmatched parts (smoother for big changes)
self.play(TransformMatchingTex(eq1, eq2, fade_transform_mismatches=True))
```

### key_map: when variable names change

If "a" in equation 1 should map to "x" in equation 2 (e.g., renaming variables):

```python
eq1 = MathTex(r"{{ a }} + {{ b }} = {{ c }}")
eq2 = MathTex(r"{{ x }} + {{ y }} = {{ z }}")

# Without key_map: nothing matches (all fade out/in). Ugly.
# With key_map: "a" morphs into "x", "b" into "y", "c" into "z". Beautiful.
self.play(TransformMatchingTex(eq1, eq2, key_map={"a": "x", "b": "y", "c": "z"}))
```

### TransformMatchingShapes: matching by appearance

`TransformMatchingTex` matches by LaTeX source string. `TransformMatchingShapes` matches by visual shape (normalized point coordinates). Useful for `Text` objects (which have no `tex_string`):

```python
text1 = Text("Hello World")
text2 = Text("World Hello")
# The letters rearrange to match their shapes
self.play(TransformMatchingShapes(text1, text2, path_arc=PI/2))
```

## Transform vs ReplacementTransform

Two similar but critically different animations:

**`Transform(A, B)`**: Morphs A to look like B. After the animation, A is still the object in the scene (it just looks like B). B was never added to the scene. Subtle but important: if you later try to animate B, nothing will happen because B is not on screen.

**`ReplacementTransform(A, B)`**: Morphs A into B, then removes A and adds B. After the animation, B is the object in the scene. A is gone. This is usually what you want.

```python
eq1 = MathTex(r"x = 1")
eq2 = MathTex(r"x = 2")
self.play(Write(eq1))
self.play(ReplacementTransform(eq1, eq2))
# eq2 is now on screen. eq1 is removed.
# self.play(eq2.animate.set_color(RED))  # works because eq2 is in the scene
```

**Rule of thumb:** Use `ReplacementTransform` for equation-to-equation transitions. Use `TransformMatchingTex` when you need part-by-part matching.

## Sizing equations

Default font_size is 48 (Manim's internal units, not LaTeX pt). Adjust for context:

```python
title_eq = MathTex(r"E = mc^2", font_size=72)     # large, for emphasis
body_eq = MathTex(r"\int_0^1 f(x)\,dx", font_size=44)  # normal
small_eq = MathTex(r"x \to 0", font_size=28)      # small annotation
```

## Custom LaTeX packages

If your equation uses special packages (physics, bm, etc.), create a TexTemplate:

```python
template = TexTemplate()
template.add_to_preamble(r"\usepackage{physics}")
template.add_to_preamble(r"\usepackage{bm}")

eq = MathTex(
    r"\bra{\psi} \hat{H} \ket{\psi}",
    tex_template=template
)
```

## Common LaTeX mistakes in Manim

1. **Forgetting raw strings**: Use `r"..."` so Python does not interpret `\f`, `\n`, etc. as escape sequences
2. **Brace balancing**: Every `{` needs `}`. Double braces `{{ }}` add TWO extra braces for Manim's parser
3. **Multi-character sub/superscripts**: `x_{12}` not `x_12` (which only subscripts the "1")
4. **Percent sign**: `r"\%"` not `%` (which starts a LaTeX comment and swallows the rest of the line)
5. **Line breaks**: `r"\\"` in a raw string produces the `\\` that LaTeX interprets as a line break

For derivation patterns, annotations, and complete worked examples, see [equation-derivations.md](equation-derivations.md).
