---
name: Visual Design Pattern Catalog
description: 22 concrete visualization patterns from 3Blue1Brown frame analysis -- implementable recipes for Manim scenes
tags: [manim, patterns, 3b1b, catalog, visualization, recipes]
---

# Visual Design Pattern Catalog

422 frames analyzed across 3 videos (NN Ch2, Transformer Ch6, MLP Ch8).
Each pattern: name, description, one code snippet.

---

## Data Display Patterns

### 1. Probability Distribution Sidebar

Right-aligned vertical word list with proportional inline bars and percentages. The sampled token gets a yellow border highlight. Reads like a ranked leaderboard.

```python
for word, prob in [("for", 0.69), ("as", 0.22), ("or", 0.02)]:
    label = Text(word, font_size=24).align_to(anchor, RIGHT)
    bar = Rectangle(width=prob * 5, height=0.25,
                    fill_color=interpolate_color(TEAL, GREEN, prob), fill_opacity=0.8)
```

### 2. Per-Number Sign Coloring

Color every individual number inside a matrix by its sign: positive in teal, negative in red. Creates a heatmap effect that communicates polarity distribution at a glance without reading values.

```python
for entry in matrix_entries:
    val = float(entry.get_tex_string())
    entry.set_color(TEAL if val > 0 else RED)
```

### 3. Running Counters

Real-time updating accuracy or loss numbers that change as examples flow through the system. Gives viewers a sense of progress rather than a static final result.

```python
correct, total = ValueTracker(0), ValueTracker(0)
counter = always_redraw(lambda: MathTex(
    rf"{int(correct.get_value())}/{int(total.get_value())} = "
    rf"{correct.get_value()/max(total.get_value(),1):.3f}"
).to_corner(UR))
```

### 4. Attention Heatmap Table

Matrix where rows are key tokens, columns are query tokens, and cell shading intensity encodes attention weight. Triangular masking (future tokens = dark) is immediately visible as a pattern.

```python
for i, row in enumerate(tokens):
    for j, col in enumerate(tokens):
        weight = attention_weights[i][j]
        cell = Circle(radius=0.15, fill_opacity=weight, fill_color=WHITE)
        cell.move_to(table_pos(i, j))
```

### 5. Vertical Number Line Display

Place dot-product results at their numeric position on a vertical axis. Words cluster spatially by semantic similarity. Position alone communicates value -- no bars needed.

```python
number_line = NumberLine(x_range=[-4, 4], length=6, rotation=PI/2)
for word, val in [("cats", 1.8), ("student", -1.1)]:
    dot = Dot(number_line.n2p(val), color=YELLOW)
    label = Text(word, font_size=20).next_to(dot, RIGHT)
```

---

## Architecture Visualization

### 6. 3D Transparent Box as Process Container

Render a multi-step process (e.g., Linear -> ReLU -> Linear) inside a semi-transparent 3D box. Front face is fully transparent so internals are visible. Label sits above, not inside.

```python
box = Prism(dimensions=[8, 3, 2], fill_opacity=0.1, stroke_color=WHITE)
label = Text("MLP").next_to(box, UP)
# Place pipeline elements as children inside box
```

### 7. Skip Connection as Yellow Bypass Arc

Show residual connections as a bright yellow arc that goes OVER the process box, terminating at a circled-plus operator. Spatial separation (over vs through) makes the two data paths unmistakable.

```python
skip_arc = ArcBetweenPoints(
    input_vec.get_top(), plus_sign.get_top(),
    angle=-0.5, color=YELLOW, stroke_width=3)
plus_sign = MathTex(r"\oplus", color=YELLOW)
```

### 8. Exploded Parallel Instance View

Show that an operation applies to every token by "exploding" a single instance into N copies stacked in 3D depth. Yellow lines across instances indicate shared weights.

```python
instances = VGroup(*[
    mlp_box.copy().shift(i * 0.4 * OUT + i * 0.3 * DOWN)
    for i in range(n_tokens)
])
```

### 9. Concrete Pipeline (Input -> Process -> Output)

Left: concrete input with real numbers. Center: labeled process box. Right: concrete output with real numbers and proportional bars. The viewer can verify the math.

```python
input_vec = Matrix([[0.34], [0.92], [0.16]])
box = Rectangle(width=2, height=1.5).add(Text("softmax"))
output_bars = VGroup(*[Rectangle(width=p*3, height=0.25,
    fill_color=BLUE, fill_opacity=0.8) for p in [0.01, 0.61, 0.25]])
```

---

## Layout and Composition

### 10. Side-by-Side Comparison

Two COMPLETE examples (same structure, different values) visible simultaneously. Same layout on both sides so the viewer's eye naturally diffs left vs right.

```python
left_panel = build_distribution(temp=0).to_edge(LEFT)
right_panel = build_distribution(temp=5).to_edge(RIGHT)
divider = Line(UP * 3, DOWN * 3, color=GREY, stroke_opacity=0.3)
```

### 11. Progressive Grid Fill

Build a gallery of peer visualizations one cell at a time (e.g., what each neuron learns). Don't show all at once -- fill a grid element by element so the pattern emerges across instances.

```python
for i, (r, c) in enumerate([(r, c) for r in range(4) for c in range(4)]):
    cell = create_weight_heatmap(neuron_index=i)
    cell.move_to([c * 1.5 - 2.25, -r * 1.5 + 2.25, 0])
    self.play(FadeIn(cell), run_time=0.5)
```

### 12. Multi-Scale Zoom

Drill down through layers of a system: architecture -> block -> vector -> scalar. Each zoom level maintains visual echoes of the level above so context is never lost.

```python
# Zoom sequence: full pipeline visible, highlight one block
self.play(FocusOn(block_2), block_2.animate.scale(2).move_to(ORIGIN),
          *[b.animate.set_opacity(0.2) for b in other_blocks])
# Then zoom further into a single vector within that block
```

### 13. Four-Quadrant Summary Frame

2x2 grid where each quadrant contains a miniaturized key concept from the video. Each cell is a complete mini-scene with its own labels, axes, and data. Used as a visual recap near the end.

```python
quadrants = VGroup(*[build_mini_scene(topic).scale(0.42)
                     for topic in ["Embedding", "Attention", "Dot Product", "MatMul"]])
quadrants.arrange_in_grid(rows=2, cols=2, buff=0.4)
```

### 14. Title/Concept Decomposition

Split a multi-word concept across the screen. Highlight one word at a time (yellow) while others go gray. Below each highlighted word, show a concrete visual example.

```python
words = VGroup(*[Text(w, font_size=64) for w in
                 ["Generative", "Pre-trained", "Transformer"]])
words.arrange(RIGHT, buff=1.5).to_edge(UP)
# Animate: set focused word YELLOW, others GREY_D
```

---

## Pedagogical Devices

### 15. Question Frame

Pose a question on screen for 2-3 seconds before showing the answer. Creates micro-suspense where the viewer actively predicts. Place the question in yellow near the relevant visual.

```python
question = Text("Which direction decreases C(x,y)\nmost quickly?",
                font_size=28, color=YELLOW)
self.play(Write(question)); self.wait(2)
self.play(FadeOut(question), GrowArrow(gradient_arrow))
```

### 16. Truth vs Convenient Lie

Split frame horizontally. Top: "The Truth" with the accurate version. Bottom: "A Convenient Lie" with the simplified version. Both show the same content so the simplification is explicit.

```python
divider = Line(LEFT * 6, RIGHT * 6, color=WHITE)
truth_label = Text("The Truth", font_size=32).next_to(divider, UP, buff=1.5)
lie_label = Text("A Convenient Lie", font_size=28).next_to(divider, DOWN, buff=1.5)
```

### 17. Cloud of Unknown

Use an amorphous gray blob as a visual placeholder for concepts that resist visualization (e.g., 12,288-dimensional space). Gradually replace the cloud with partial views as understanding builds.

```python
cloud = SVGMobject("cloud.svg", fill_color=GREY, fill_opacity=0.4).scale(3)
label = Text("12,288-dim\nSpace", color=YELLOW, font_size=28)
label.next_to(cloud, LEFT)
```

### 18. Absurdist Counterexample

After showing a system working correctly, immediately feed it an adversarial input (random noise, out-of-distribution image). The contrast between "96% accuracy" and "thinks noise is a 5" is more instructive than either alone.

```python
noise_image = ImageMobject(np.random.rand(28, 28))
noise_image.add(SurroundingRectangle(noise_image, color=YELLOW, buff=0.05))
result_label = Text("Looks like a 5 to me!", color=YELLOW, font_size=24)
```

### 19. Strikethrough for Conceptual Revision

Show the original text with a red line through it, then place the revised text nearby. The struck-through text remains visible so the viewer sees what changed and why.

```python
old_text = MathTex(r"90^\circ", color=RED)
strike = Line(old_text.get_left(), old_text.get_right(), color=RED, stroke_width=3)
new_text = MathTex(r"89^\circ \text{ to } 91^\circ", color=TEAL).next_to(old_text, UP)
```

### 20. Interactive Slider with Live Output

A parameter slider with a visible handle. As the value changes, ALL output values and bars update simultaneously. Input stays fixed while only the parameter changes.

```python
temp = ValueTracker(1.0)
slider = NumberLine(x_range=[0, 10], length=4)
handle = Triangle(fill_color=RED).scale(0.15)
handle.add_updater(lambda m: m.move_to(slider.n2p(temp.get_value()) + UP * 0.1))
```

### 21. Interpretive Piecewise Labels

Place a conditional/piecewise annotation next to a formula, translating math into English meaning. Bridges abstract notation to concrete semantics using quoted natural language.

```python
interp = MathTex(
    r"\begin{cases}\approx 1 & \text{If encodes ``Michael''} \\"
    r"\leq 0 & \text{If not}\end{cases}", font_size=24)
interp.next_to(dot_product_eq, RIGHT, buff=0.3)
```

### 22. Section Title Card

Clean transition: single centered title on pure black background, white serif text. Zero visual complexity signals "new topic." Hold for 2 seconds, then fade out.

```python
title = Text("Superposition", font="serif", font_size=56)
title.move_to(ORIGIN)
self.play(Write(title)); self.wait(2); self.play(FadeOut(title))
```

---

## Quick Reference

| #  | Pattern                        | Category      |
|----|--------------------------------|---------------|
| 1  | Probability Distribution       | Data Display  |
| 2  | Per-Number Sign Coloring       | Data Display  |
| 3  | Running Counters               | Data Display  |
| 4  | Attention Heatmap Table        | Data Display  |
| 5  | Vertical Number Line           | Data Display  |
| 6  | 3D Transparent Box             | Architecture  |
| 7  | Skip Connection Arc            | Architecture  |
| 8  | Exploded Parallel View         | Architecture  |
| 9  | Concrete Pipeline              | Architecture  |
| 10 | Side-by-Side Comparison        | Layout        |
| 11 | Progressive Grid Fill          | Layout        |
| 12 | Multi-Scale Zoom               | Layout        |
| 13 | Four-Quadrant Summary          | Layout        |
| 14 | Title/Concept Decomposition    | Layout        |
| 15 | Question Frame                 | Pedagogical   |
| 16 | Truth vs Convenient Lie        | Pedagogical   |
| 17 | Cloud of Unknown               | Pedagogical   |
| 18 | Absurdist Counterexample       | Pedagogical   |
| 19 | Strikethrough Revision         | Pedagogical   |
| 20 | Interactive Slider             | Pedagogical   |
| 21 | Interpretive Piecewise Labels  | Pedagogical   |
| 22 | Section Title Card             | Pedagogical   |
