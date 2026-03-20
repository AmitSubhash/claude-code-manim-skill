---
name: Equation Derivation Patterns
description: Step-by-step derivation animations, annotation patterns, and complete worked examples for Manim equation scenes
tags: [manim, derivation, equations, annotation, first-principles, worked-examples]
---

# Equation Derivation Patterns

Prerequisite: read [equations.md](equations.md) first for MathTex fundamentals and TransformMatchingTex.

## Highlighting a term with annotation

A common pattern: draw a box around a term, add a brace underneath with a label.

```python
class AnnotateEquation(Scene):
    def construct(self) -> None:
        eq = MathTex(r"{{ F }} = {{ m }} {{ a }}")
        self.play(Write(eq))
        self.wait()

        # Highlight the force term with a colored rectangle
        f_part = eq.get_part_by_tex("F")
        box = SurroundingRectangle(f_part, color=YELLOW, buff=0.1)
        self.play(Create(box))

        # Add a brace below "ma" with a label
        ma_group = VGroup(eq.get_part_by_tex("m"), eq.get_part_by_tex("a"))
        brace = Brace(ma_group, DOWN)
        label = brace.get_tex(r"\text{cause of acceleration}")
        self.play(Create(brace), Write(label))
        self.wait(2)
```

## The "dim and reveal" technique

For complex equations, do not show everything at once. Instead:

1. Show the full equation so the viewer sees its shape (2s pause)
2. Dim everything to 30% opacity
3. Highlight term 1: full opacity + SurroundingRectangle + annotation
4. Color term 1 distinctively, remove rectangle, move to term 2
5. Repeat until all terms are color-coded
6. Un-dim: now the viewer can "read" the equation by color

```python
class DimAndReveal(Scene):
    def construct(self) -> None:
        eq = MathTex(
            r"{{ \Phi }} = {{ \int }} {{ G(r, r') }} {{ S(r') }} {{ dr' }}",
            font_size=44,
        )
        self.play(Write(eq))
        self.wait(2)  # let viewer see the shape

        # Dim everything
        self.play(eq.animate.set_opacity(0.3))

        # Reveal term by term
        terms = [
            ("\\Phi", YELLOW, r"Measured signal"),
            ("G(r, r')", BLUE, r"Green's function"),
            ("S(r')", RED, r"Source distribution"),
        ]
        for tex, color, description in terms:
            part = eq.get_part_by_tex(tex)
            box = SurroundingRectangle(part, color=color, buff=0.1)
            label = Tex(description, font_size=28, color=color)
            label.next_to(box, DOWN)

            self.play(part.animate.set_opacity(1.0), Create(box))
            self.play(Write(label))
            self.wait(1.5)

            self.play(part.animate.set_color(color), FadeOut(box), FadeOut(label))

        # Un-dim: full equation now color-coded
        self.play(eq.animate.set_opacity(1.0))
        self.wait(2)
```

## Step-by-step derivation pattern

Chain `TransformMatchingTex` calls to walk through a proof.

**Design process:**
1. Write out all steps of the derivation on paper
2. Identify which terms persist across steps (these get `{{ }}` groups with matching names)
3. Terms that appear/disappear between steps are left unmatched (Manim fades them)
4. Add `self.wait()` between steps so the viewer can read

```python
class PythagoreanDerivation(Scene):
    def construct(self) -> None:
        eq1 = MathTex(r"{{ a^2 }} + {{ b^2 }} = {{ c^2 }}")
        self.play(Write(eq1))
        self.wait(2)

        eq2 = MathTex(r"{{ a^2 }} = {{ c^2 }} - {{ b^2 }}")
        self.play(TransformMatchingTex(eq1, eq2))
        self.wait(2)

        eq3 = MathTex(r"{{ a }} = \sqrt{ {{ c^2 }} - {{ b^2 }} }")
        self.play(TransformMatchingTex(eq2, eq3))
        self.wait(2)
```

## Complete example: E=mc^2 from first principles

Every line is annotated. This demonstrates the full derivation workflow.

```python
from manim import *

class EnergyDerivation(Scene):
    """Derives E=mc^2 from the energy-momentum relation.

    Each step is a separate MathTex with {{ }} groups that
    persist across transformations. The viewer sees terms
    rearranging and simplifying smoothly.
    """
    def construct(self) -> None:
        # Step 1: Start with a known equation the viewer recognizes
        step1 = MathTex(
            r"{{ E }}^2 = ({{ p }} c)^2 + ({{ m }} c^2)^2",
            font_size=44,
        )
        step1_label = Tex(
            r"Energy-momentum relation", font_size=32, color=GRAY
        ).next_to(step1, UP, buff=0.5)

        self.play(Write(step1_label))
        self.play(Write(step1))
        self.wait(2)

        # Step 2: Apply the condition p=0 (particle at rest)
        step2 = MathTex(
            r"{{ E }}^2 = (0)^2 + ({{ m }} c^2)^2",
            font_size=44,
        )
        rest_note = Tex(
            r"At rest: $p = 0$", font_size=32, color=YELLOW
        ).next_to(step2, DOWN, buff=0.5)

        self.play(FadeOut(step1_label))
        self.play(TransformMatchingTex(step1, step2))
        self.play(Write(rest_note))
        self.wait(2)

        # Step 3: Simplify (0)^2 = 0, drop it
        step3 = MathTex(
            r"{{ E }}^2 = ({{ m }} c^2)^2",
            font_size=44,
        )
        self.play(FadeOut(rest_note))
        self.play(TransformMatchingTex(step2, step3))
        self.wait(1)

        # Step 4: Take square root of both sides
        step4 = MathTex(
            r"{{ E }} = {{ m }} c^2",
            font_size=44,
        )
        self.play(TransformMatchingTex(step3, step4))
        self.wait(1)

        # Step 5: Final form - scale up and highlight
        final = MathTex(r"E = mc^2", font_size=72, color=YELLOW)
        box = SurroundingRectangle(
            final, color=YELLOW, buff=0.3, corner_radius=0.1
        )

        self.play(ReplacementTransform(step4, final))
        self.play(Create(box))
        self.wait(3)
```
