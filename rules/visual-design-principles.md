---
name: Visual Design Principles
description: 12 core principles for creating effective math animations -- from Tufte, Bret Victor, 3Blue1Brown, and cognitive science
tags: [manim, design, principles, pedagogy, 3b1b, visual-explanation]
---

# 12 Visual Design Principles

## 1. Geometry Before Algebra

Show the shape first, the equation second. Visual memory encodes 6x faster than symbolic memory (picture superiority effect). When the viewer sees the geometric pattern before the formula, the equation feels earned -- it formalizes what they already understand.

```python
parabola = axes.plot(lambda x: x**2 - 4*x + 3, color=BLUE)
self.play(Create(parabola))
self.wait(2)  # viewer sees the shape, notices where it crosses zero

roots = VGroup(*[Dot(axes.c2p(r, 0), color=YELLOW) for r in [1, 3]])
self.play(FadeIn(roots))
self.wait(1)

# NOW the equation formalizes what they already see
eq = MathTex(r"(x-1)(x-3) = 0", font_size=36, color=YELLOW)
eq.next_to(parabola, UR, buff=0.3)
self.play(Write(eq))
```

## 2. Opacity Layering

Direct attention through brightness, not removal. The brain processes visual salience in layers: high-contrast elements are pre-attentive (~200ms), low-contrast elements remain accessible but do not compete. This lets you keep 3-4 layers visible without overload.

```python
PRIMARY = 1.0    # the thing being explained NOW
CONTEXT = 0.4    # previously introduced, still relevant
GRID = 0.15      # structural elements (axes, grids, guides)

# Introducing a new concept: dim the old, add the new at full opacity
self.play(prev_concept.animate.set_opacity(CONTEXT), FadeIn(new_concept))
```

## 3. Persistent Context

Never explain a detail in isolation. Keep the parent object visible (dimmed, scaled to 30-40% of frame width) while zooming into its parts. Without spatial context the viewer loses the "where does this fit?" anchor, and working memory fragments.

```python
self.play(
    full_network.animate.scale(0.4).to_corner(UL).set_opacity(0.5),
)
neuron_detail = create_neuron_detail().to_edge(RIGHT)
self.play(FadeIn(neuron_detail))
# Dashed line connecting detail back to its location in the full view
link = DashedLine(
    full_network[3].get_right(), neuron_detail.get_left(),
    color=YELLOW, stroke_opacity=0.5,
)
self.play(Create(link))
```

## 4. Linked Dual Representations

Show two views of the same data, synchronized via a shared ValueTracker. Dual coding theory: verbal + spatial encoding produces 2x retention vs. either alone. The viewer viscerally grasps "these are the same object" when moving one updates the other.

```python
t = ValueTracker(1.0)
curve_dot = always_redraw(
    lambda: Dot(left_axes.c2p(t.get_value(), f(t.get_value())), color=YELLOW)
)
deriv_bar = always_redraw(lambda: Rectangle(
    width=0.5, height=abs(fp(t.get_value())) * 2,
    fill_color=BLUE if fp(t.get_value()) > 0 else RED, fill_opacity=0.8,
).move_to(right_axes.c2p(0, fp(t.get_value()) / 2)))
self.play(t.animate.set_value(4), run_time=4)  # both panels update together
```

## 5. Parameter Manipulation

"If you can't play with it, you don't understand it" (Bret Victor). Continuous parameter sweeps via ValueTracker engage causal reasoning: the brain infers cause-and-effect through temporal contiguity. The viewer watches a change happen and constructs understanding.

```python
a = ValueTracker(1)
parabola = always_redraw(
    lambda: axes.plot(lambda x: a.get_value() * x**2, color=BLUE)
)
label = always_redraw(
    lambda: MathTex(f"a = {a.get_value():.1f}", font_size=28).to_corner(UR)
)
self.play(a.animate.set_value(3), run_time=3)
self.play(a.animate.set_value(-2), run_time=3)
```

## 6. Continuous Morphing

Transform between representations to show they are the same idea in different notation. Object permanence makes the viewer track identity through the morph, encoding "A IS B" rather than "A is related to B." This is the most underused Manim technique.

```python
circle_arrow = Arc(radius=1.5, angle=PI / 3, color=BLUE)
self.play(Create(circle_arrow))
self.wait(1)

matrix = Matrix([[r"\cos\theta", r"-\sin\theta"],
                 [r"\sin\theta", r"\cos\theta"]])
self.play(ReplacementTransform(circle_arrow, matrix))
self.wait(1)

exp_form = MathTex(r"e^{i\theta}")
self.play(ReplacementTransform(matrix, exp_form))
```

## 7. Question Frames

Pose a question on screen, wait 2-3 seconds, then answer visually. The generation effect: a brain that predicts an answer encodes the real answer more deeply, even if the prediction was wrong. The pause is thinking time, not dead air.

```python
question = Text(
    "Which direction decreases C(x,y)\nmost quickly?",
    font_size=28, color=YELLOW,
)
question.to_edge(UP, buff=0.5)
self.play(Write(question))
self.wait(2.5)  # viewer actively predicts

gradient_arrow = Arrow(point, point + grad_dir, color=YELLOW)
self.play(GrowArrow(gradient_arrow))
self.wait(1)
self.play(FadeOut(question))  # visual answer replaces verbal question
```

## 8. Annotations ON Objects

Labels must be physically attached to their target. When annotation and object are spatially separated, the viewer's eyes saccade between them, fragmenting working memory (split-attention effect, Sweller 1988). Use braces, arrows, or `next_to` with small `buff`.

```python
# BAD: label far from target
label = Text("Force").to_edge(DOWN)

# GOOD: label attached directly
eq = MathTex(r"{{ F }} = {{ m }}{{ a }}")
brace = Brace(eq.get_part_by_tex("F"), DOWN, buff=0.05)
f_label = brace.get_tex(r"\text{Force}")

# GOOD: arrow from label to object
label = Text("Cost function", font_size=24).next_to(cost_curve, UR, buff=0.1)
arrow = Arrow(label.get_bottom(), cost_curve.get_top(), buff=0.05)
```

## 9. Color as Semantic Data

Every color must carry meaning -- never decorative. Consistent semantic color mapping lets the viewer decode information pre-attentively (~200ms, before conscious reading). One color = one meaning, maintained across the entire video.

```python
# Define once, use everywhere
POSITIVE = BLUE      # positive values, weights, correct direction
NEGATIVE = RED       # negative values, errors, wrong direction
FOCUS = YELLOW       # current point of attention, highlights
CORRECT = GREEN      # desired outcomes, correct predictions
NEUTRAL = WHITE      # structural labels, axes text

# Apply semantically: color encodes sign of weight
weight_color = interpolate_color(NEGATIVE, POSITIVE, (w + 1) / 2)
```

## 10. Concrete Values

Use real numbers, not placeholders. When the viewer sees `[0.34, 0.16, 0.92]` instead of `[a1, a2, a3]`, they can verify the math, build intuition about scale, and anchor abstract concepts to tangible quantities. Concrete examples activate episodic memory that symbols do not.

```python
# BAD: abstract placeholders
bars = VGroup(*[Rectangle(width=0.4, height=1) for _ in range(5)])

# GOOD: concrete values the viewer can reason about
values = [0.34, 0.16, 0.27, 0.53, 0.92]
bars = VGroup(*[
    Rectangle(width=0.4, height=v * 3, fill_opacity=0.8,
              color=interpolate_color(RED, BLUE, v))
    for v in values
]).arrange(RIGHT, buff=0.05)
nums = VGroup(*[
    DecimalNumber(v, num_decimal_places=2, font_size=20).next_to(b, DOWN)
    for v, b in zip(values, bars)
])
```

## 11. Progressive Complexity

Build complexity layer by layer: dim the previous layer, add the new one. Never remove old layers entirely -- the viewer can always trace back through the conceptual stack. This is Vygotsky's scaffolding: each layer is comprehensible because the previous one supports it.

```python
self.play(Write(layer_1))
self.wait(1)

# Layer 2: dim layer 1, introduce layer 2
self.play(layer_1.animate.set_opacity(0.3))
self.play(Write(layer_2))
self.wait(1)

# Layer 3: cascade the dimming
self.play(
    layer_1.animate.set_opacity(0.15),
    layer_2.animate.set_opacity(0.3),
)
self.play(Write(layer_3))
```

## 12. Emotional Anchoring

Put charged language ON SCREEN, not just in narration. "Utter trash" next to a bad prediction creates emotional tagging (amygdala activation strengthens memory consolidation). The contrast between failure and success creates narrative tension that keeps the viewer engaged and makes the payoff memorable.

```python
verdict = Text("Utter trash", font_size=28, color=RED, slant=ITALIC)
verdict.next_to(output_display, DOWN, buff=0.3)
self.play(Write(verdict))
self.wait(1.5)

# After training succeeds -- relief through contrast
self.play(FadeOut(verdict))
success = Text("0.96 accuracy!", font_size=28, color=GREEN)
success.next_to(output_display, DOWN, buff=0.3)
self.play(Write(success))
```

## 13. Live Values in Diagrams

Show actual numbers flowing through a diagram, not equations beside it. When a parameter changes, ALL downstream values update simultaneously. This is the difference between "explaining a system" and "running a system in front of the viewer." The viewer watches cause and effect propagate in real time.

```python
# A network node that shows its current computed value
param = ValueTracker(0.0)

node_value = always_redraw(lambda: DecimalNumber(
    param.get_value(), num_decimal_places=2, font_size=20, color=WHITE,
).move_to(node_circle))

# Downstream node recomputes when param changes
downstream_value = always_redraw(lambda: DecimalNumber(
    sigmoid(param.get_value() * weight), num_decimal_places=3,
    font_size=20, color=WHITE,
).move_to(downstream_circle))

# Change the parameter -- everything updates together
self.play(param.animate.set_value(0.10), run_time=1.5)
# The viewer sees: input changes -> intermediate changes -> output changes -> loss changes
```

The key insight: don't explain what WOULD happen if a value changed. CHANGE the value and let the viewer watch the cascade. This engages causal reasoning far more than static equations.

## 14. Density Ramp

Start sparse, end dense. The visual complexity of each frame should mirror the conceptual complexity at that point in the explanation. Begin with 2-3 elements. End with 15+.

```
Frame 1:    [circle]                          # just the shape
Frame 10:   [circle] [equation]               # shape + one equation
Frame 30:   [circle] [eq] [graph]             # add a linked view
Frame 50:   [circle] [eq] [graph] [values]    # add concrete numbers
Frame 60:   [EVERYTHING radiating outward]    # the full picture
```

This creates a narrative feeling of "building understanding." The viewer watches complexity emerge from simplicity, which mirrors how learning actually works. Never start at maximum density -- it overwhelms. Never stay sparse -- it feels empty.

Bad: constant density throughout (every frame has 5 elements)
Bad: starting dense then simplifying (feels like information is being removed)
Good: 2 elements -> 5 -> 8 -> 12 -> full diagram (feels like building)

```python
# Phase 1: just the core diagram (sparse)
self.play(Create(network_skeleton))
self.wait(1)

# Phase 2: add values flowing through
self.play(*[Write(v) for v in node_values])

# Phase 3: add the linked loss curve
self.play(Create(loss_axes), Create(loss_curve))

# Phase 4: add gradient arrows radiating from every node
self.play(LaggedStart(*[GrowArrow(a) for a in gradient_arrows],
                       lag_ratio=0.1))
# Maximum density at the climax
```

## 15. Per-Scene Skeleton

Each scene should have ONE anchor diagram that stays visible throughout the scene. Elements are added TO it, highlighted WITHIN it, but the skeleton itself never disappears. This gives the viewer a stable spatial map. They always know "where they are" in the explanation.

The skeleton is NOT the same diagram across scenes (that would be monotonous). It's the principle that within any single scene, there is ONE persistent reference object.

```python
# Scene: explaining softmax
# Skeleton = the network diagram (stays for entire scene)
network = create_network_diagram()
self.play(Create(network))

# Everything else is added relative to the skeleton
highlight = SurroundingRectangle(network.output_layer, color=YELLOW)
self.play(Create(highlight))

softmax_eq = MathTex(r"\text{softmax}(z_i) = \frac{e^{z_i}}{\sum e^{z_j}}")
softmax_eq.next_to(network, RIGHT, buff=0.5)
self.play(Write(softmax_eq))

# Skeleton remains. Additions come and go around it.
self.play(FadeOut(highlight), FadeOut(softmax_eq))
# network is STILL there for the next beat
```

## 16. Caption Zone

Reserve the bottom 20% of the frame (y < -2.5) exclusively for narration text or subtitles. Never place visual elements there. This creates a clear spatial contract: the viewer looks at the middle for visuals and glances down for explanation. Mixing the two causes confusion.

```python
CAPTION_Y = -3.0

# Narration-synced caption
caption = Text("the gradient tells us which direction to move",
               font_size=22, color=WHITE)
caption.move_to(DOWN * CAPTION_Y)
self.play(Write(caption))

# When the next line of narration comes, replace it
next_caption = Text("and by how much", font_size=22, color=WHITE)
next_caption.move_to(DOWN * CAPTION_Y)
self.play(ReplacementTransform(caption, next_caption))
```

## Quick Reference

| # | Principle | Key Idea |
|---|-----------|----------|
| 1 | Geometry before algebra | Shape first, equation second |
| 2 | Opacity layering | Primary 100%, context 40%, grid 15% |
| 3 | Persistent context | Parent stays visible during detail work |
| 4 | Linked dual representations | Two views, one ValueTracker |
| 5 | Parameter manipulation | Sweep parameters, viewer sees effect |
| 6 | Continuous morphing | Transform A into B to show identity |
| 7 | Question frames | Ask, pause 2-3s, answer visually |
| 8 | Annotations ON objects | Labels attached, never floating |
| 9 | Color as semantic data | Every color carries consistent meaning |
| 10 | Concrete values | Real numbers, not placeholders |
| 11 | Progressive complexity | Dim previous, add new layer |
| 12 | Emotional anchoring | Charged language on screen |
| 13 | Live values in diagrams | Numbers flow through diagrams, update in real time |
| 14 | Density ramp | Start sparse (2-3 elements), end dense (15+) |
| 15 | Per-scene skeleton | ONE anchor diagram per scene, never removed |
| 16 | Caption zone | Bottom 20% reserved for narration text only |
