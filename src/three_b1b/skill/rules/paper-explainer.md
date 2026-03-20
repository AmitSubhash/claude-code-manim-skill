---
name: Research Paper Explainer Videos
description: First-principles guide to creating research paper explainer videos with Manim - pedagogy, structure, decision frameworks, and domain-specific patterns
tags: [manim, research, paper, explainer, video, scientific, pedagogy]
---

# Research Paper Explainer Videos

Prerequisites: you have read `equations.md` (MathTex, TransformMatchingTex, submobjects) and `animations.md` (animation types, rate functions, composition). This file teaches you how to THINK about building a video, not just how to write the code.

## Why animate a research paper?

Static figures are snapshots. Animation shows process, causality, and temporal evolution. A viewer watching an animation builds a mental simulation they can replay. A reader looking at a figure builds a static image. The mental simulation is stickier and more transferable.

**Animate when:**
1. There is a sequence of steps (algorithm, pipeline, derivation)
2. Spatial relationships change over time (data flows, transformations)
3. Equation terms "do" something (a coefficient grows, a sum accumulates, a gradient descends)
4. You are comparing before/after states or method A vs method B

**Do NOT animate when:** the concept is already clear from a single well-labeled diagram. A circuit schematic, a table of hyperparameters, or a static anatomy reference gains nothing from motion. Show it as a static figure with `FadeIn` and move on.

## Who is watching?

Your target viewer is a researcher in an adjacent field, or a grad student learning the topic. They know the general domain (e.g., "machine learning" or "biomedical optics") but not your specific method. They are smart but unfamiliar.

**Cognitive load rule:** a viewer can track roughly 3 new concepts before needing a consolidation pause. After introducing 3 new ideas, stop and let the viewer see all three together before adding more. In Manim terms: after every 3-4 animations, add `self.wait(1)`.

## Video structure: the 5-minute template

| Section | Duration | Purpose |
|---|---|---|
| Hook | 10s | Show the punchline first |
| Problem | 30s | What gap exists? Why care? |
| Background | 60s | What the viewer needs to follow your method |
| Method | 120s | The core contribution, built piece by piece |
| Results | 60s | Animated evidence that it works |
| Takeaway | 20s | One sentence the viewer should remember |

**Why hook first?** Cognitive anchoring. When the viewer sees the end result up front, they watch the rest with a specific question: "how did they do that?" This transforms passive viewing into active prediction. Show the final reconstruction, the accuracy number, or the key diagram. Then rewind.

**Why this order?** Each section sets up the next. The problem creates a gap the viewer wants filled. Background gives them the vocabulary. Method fills the gap. Results validate it. Takeaway crystallizes the memory. Rearranging this order breaks the causal chain.

## First-principles equation explanation

This is THE key pattern for research videos. The goal: take an equation the viewer has never seen and make every term intuitively understood.

**The decomposition process (why each step exists):**

1. **Write the full equation on screen.** Do not animate individual terms yet. WHY: the viewer needs to see the shape of what they are about to learn. It sets expectations.
2. **Pause 2 seconds.** WHY: let the viewer scan the equation and form initial impressions.
3. **Dim the entire equation to 30% opacity.** WHY: this signals "we are about to zoom in" and reduces visual competition.
4. **Highlight the FIRST term:** bring it to full opacity, add a `SurroundingRectangle`. Explain with a label, brace, or small animation.
5. **When done with that term, color it** (e.g., blue) and move to the NEXT term. WHY: the color acts as a "done" marker. The viewer knows blue terms are understood.
6. **Repeat until every term is explained and distinctly colored.**
7. **Un-dim everything.** Now the full equation is color-coded and the viewer can "read" it like a sentence.

**How to decide term order:**
- Start with what the viewer already knows (outputs, simple constants, standard notation)
- Move to domain-specific but well-known terms (one-sentence description each)
- Save YOUR contribution for last (derive it, show where it comes from)
- This order builds confidence: the viewer feels "I understand most of this" before hitting the hard part

**How to decide annotation depth:**
- Standard notation (integral, summation, common subscripts): name it briefly with a brace
- Domain-specific but established (Green's function, Jacobian): one sentence + a small visual
- Your novel contribution: derive from scratch, show the physical intuition, animate the mechanism

```python
class EquationDecomposition(Scene):
    """Demonstrates the dim-highlight-color pattern for the diffusion equation."""

    def construct(self) -> None:
        # Step 1: Show the full equation so the viewer sees the whole shape
        eq = MathTex(
            r"{{ \nabla \cdot }} {{ D(\mathbf{r}) }} {{ \nabla }} "
            r"{{ \Phi(\mathbf{r}) }} - {{ \mu_a(\mathbf{r}) }} "
            r"{{ \Phi(\mathbf{r}) }} = {{ -S(\mathbf{r}) }}",
            font_size=40,
        )
        title = Tex("Photon Diffusion Equation", font_size=36, color=GRAY)
        title.to_edge(UP)

        self.play(Write(title))
        self.play(Write(eq))
        self.wait(2)  # Step 2: let viewer scan

        # Step 3: Dim everything - signals "we are zooming in"
        self.play(eq.animate.set_opacity(0.3), FadeOut(title))

        # Step 4-6: Highlight each term, explain, color, move on
        terms = [
            (r"\Phi(\mathbf{r})", "Photon fluence\n(what we measure)", YELLOW),
            (r"D(\mathbf{r})", "Diffusion coefficient\n(how light spreads)", BLUE),
            (r"\mu_a(\mathbf{r})", "Absorption\n(how much light is lost)", RED),
            (r"-S(\mathbf{r})", "Light source\n(where photons enter)", GREEN),
        ]

        for tex_str, description, color in terms:
            parts = eq.get_parts_by_tex(tex_str)
            for part in parts:
                part.set_opacity(1)
            first_part = parts[0]
            rect = SurroundingRectangle(first_part, color=color, buff=0.1)
            brace = Brace(first_part, DOWN, color=color)
            label = brace.get_text(description, font_size=22).set_color(color)

            self.play(Create(rect), Create(brace), Write(label), run_time=0.8)
            self.wait(1.5)
            self.play(FadeOut(rect, brace, label), run_time=0.5)
            for part in parts:
                part.set_color(color)

        # Step 7: Un-dim - now the full equation is color-coded
        remaining = [sm for sm in eq.submobjects if sm.get_fill_opacity() < 0.5]
        anims = [sm.animate.set_opacity(1) for sm in remaining]
        if anims:
            self.play(*anims)
        self.wait(2)
```

## Building pipeline/architecture diagrams

**The thinking process:**
1. Read the paper's method section. Identify the main processing stages (usually 3-7).
2. For each stage, ask: does the viewer need to see INSIDE this box? If yes, plan a zoom-in later.
3. Choose layout: horizontal for temporal flow (input -> process -> output), vertical for hierarchy (encoder above decoder).

**Granularity decisions:**
- One box per conceptually distinct operation
- If two steps always happen together and the boundary is unimportant, merge them into one box
- If a step has interesting internal structure, show it as one box first, then zoom in later

**Animation strategy and WHY:**
- Reveal boxes one at a time with `FadeIn(shift=UP*0.5)`. WHY: sequential reveal matches the data flow, building the pipeline in the viewer's mind left to right.
- After each box appears, add the connecting arrow. WHY: the arrow says "output of A becomes input of B," and it should appear only after both endpoints exist.
- Use consistent colors: input=GREEN, processing=BLUE, output=YELLOW. WHY: the viewer learns the color scheme once and can instantly classify new boxes.

```python
class PipelineDiagram(Scene):
    """4-stage pipeline with animated reveal and data flow."""

    def construct(self) -> None:
        stage_data = [
            ("Raw Signal", GREEN),
            ("Preprocessing", BLUE),
            ("Neural Network", BLUE),
            ("Reconstruction", YELLOW),
        ]

        boxes = VGroup()
        for name, color in stage_data:
            rect = Rectangle(width=2.4, height=0.9, color=color, fill_opacity=0.2)
            label = Text(name, font_size=20)
            label.move_to(rect)
            box = VGroup(rect, label)
            boxes.add(box)
        boxes.arrange(RIGHT, buff=1.0)

        # Reveal one at a time: each box then its connecting arrow
        self.play(FadeIn(boxes[0], shift=UP * 0.5))
        arrows = VGroup()
        for i in range(1, len(boxes)):
            arrow = Arrow(
                boxes[i - 1][0].get_right(),
                boxes[i][0].get_left(),
                buff=0.1, color=WHITE,
            )
            arrows.add(arrow)
            self.play(GrowArrow(arrow), FadeIn(boxes[i], shift=UP * 0.5), run_time=0.8)
            self.wait(0.3)  # brief pause per stage for rhythm

        self.wait(1)

        # Optional: animate a dot flowing through the pipeline
        dot = Dot(color=YELLOW).move_to(boxes[0])
        self.play(FadeIn(dot, scale=0.5))
        for arrow in arrows:
            self.play(MoveAlongPath(dot, arrow, run_time=0.5))
        self.play(FadeOut(dot, scale=2))
```

## Animating results and evidence

Each result type has a natural animation pattern:

- **Training curves:** `Axes` + `plot` with `Create(graph, rate_func=linear)`. Add a `ValueTracker` and a tracing `Dot` if you want the viewer to follow the curve as it draws. The linear rate_func is critical here because the x-axis represents real time/epochs.
- **Bar charts:** `BarChart` with `change_bar_values()` to animate transitions between conditions.
- **Confusion matrices:** `Table` or manual grid with `interpolate_color(BLUE, RED, value)` for cells. `LaggedStartMap(FadeIn, cells)` for dramatic reveal.
- **Before/after comparison:** split screen with `VGroup(left, right).arrange(RIGHT, buff=1.5)`. Add a vertical `Line` divider. Reveal baseline first, then yours, so the viewer sees the improvement.
- **Side-by-side:** put both on screen, use `Indicate()` to draw attention to the differences.

## Pacing and timing rules

These are calibrated for narrated videos. Adjust if the video is silent.

| Action | Recommended run_time | Why |
|---|---|---|
| Show equation for first time | Write default (1s) + 2s wait | Viewer needs to read and parse the symbols |
| Highlight one term | 0.5s | Quick, viewer's eye is already on it |
| TransformMatchingTex between steps | 1.5-2s | Viewer needs to track which parts move where |
| FadeIn a new diagram element | 0.8s | Faster than equation work since shapes are simpler |
| Pipeline stage reveal | 0.5-0.8s per stage | Rhythm matters more than individual speed |
| Camera zoom to detail | 1.5s | Viewer needs to reorient spatial context |
| Hold after major reveal | 2-3s | Let the insight sink in |

**Breathing room:** After every 3-4 animations, add `self.wait(1)`. The viewer needs time to consolidate. Without pauses, animations blur together and nothing sticks.

**Narration sync strategy:**
- Animations should START slightly BEFORE the narrator describes them (about 0.5s lead). The viewer sees the visual, then hears the explanation. This is more effective than hearing first because the visual creates a question the narration answers.
- Time `self.wait()` calls to match narration pauses.
- Rule: if the narrator takes 5 seconds to explain something, the corresponding animations should total about 4 seconds with a 1 second hold at the end.

## Deciding what to animate vs show static

**Animate when:**
- Temporal sequence (step 1, then step 2, then step 3)
- Spatial transformation (data changes shape, equation rearranges)
- Comparison (before/after, method A vs method B)
- Building complexity (simple case, add a term, add another)

**Show static when:**
- Complex spatial layout where motion would confuse (circuit diagram, dense network graph)
- Reference information the viewer should memorize (table of parameters, list of abbreviations)
- The concept is already clear from a well-labeled figure

**The test:** ask yourself "does the ORDER in which parts appear matter?" If yes, animate. If the viewer needs to see everything simultaneously to understand the relationships, show it static.

## Domain-specific patterns

### Machine Learning papers
- **Architecture diagrams:** build encoder-decoder piece by piece. Color by layer type: Conv=BLUE, Attention=ORANGE, Linear=GREEN, Norm=GRAY.
- **Attention mechanism:** show query/key/value as colored vectors (`Arrow` or `Rectangle`), dot product as connection lines with opacity proportional to attention weight, softmax as a color normalization step.
- **Loss landscape:** `ThreeDScene` with `Surface`. Color by height (loss value). Animate a `Dot3D` rolling down the surface with a `ValueTracker` controlling position along a gradient descent path.
- **Training dynamics:** animated training curve with an epoch counter (`Integer` + `ValueTracker`). Show train and val loss diverging to illustrate overfitting.

### Physics/Engineering papers
- **Field visualization:** `ArrowVectorField` for discrete arrows, `StreamLines` for continuous flow. Use `start_animation(warm_up=True)` for StreamLines.
- **Wave propagation:** `ValueTracker` for time, `always_redraw` for a `ParametricFunction` that shifts with time. The viewer sees the wave move.
- **Particle systems:** many `Dot` objects with `add_updater` applying forces each frame. Use `dt` parameter in updater for physics-correct integration.
- **Energy diagrams:** horizontal `Line` objects at different heights with `Arrow` showing transitions. Color arrows by energy (blue=low, red=high).

### Biomedical/Imaging papers
- **Sensor layouts:** `Dot` objects arranged on geometry (`Circle` for brain surface, `Rectangle` for tissue slab). Color-code sources (RED) vs detectors (BLUE).
- **Signal propagation:** animated arrows or color gradients (`interpolate_color`) showing signal path through tissue. Use `Create` on curved arrows with `run_time=0.5` for each path.
- **Reconstruction pipeline:** show measured data (heatmap or signal plot) on the left, animate the algorithm step (matrix multiply, iterative update), show reconstructed image appearing on the right.
- **Sensitivity maps:** grid of `Square` objects with `fill_opacity` proportional to sensitivity value. Use `LaggedStartMap(FadeIn, cells, lag_ratio=0.01)` for a sweep-reveal effect.

## Common mistakes in explainer videos

1. **Too many simultaneous animations.** The viewer can track at most 2 things moving at once. If you have 5 boxes appearing together, use `LaggedStart` so they appear sequentially.
2. **No pause after complex reveals.** After showing a full equation or completing a pipeline, add `self.wait(2)`. Without this, the next animation starts before the viewer has processed the current one.
3. **Showing the full equation at full opacity before explaining parts.** Dim it first (step 3 in the decomposition process), then reveal piece by piece. Otherwise the viewer tries to read the whole thing and gets overwhelmed.
4. **Inconsistent colors across scenes.** Define a `COLOR_MAP` dict in a shared `style.py` and import it everywhere. If absorption is RED in scene 1, it must be RED in scene 5.
5. **Moving too fast between pipeline stages.** Each stage needs its own moment. Add `self.wait(0.3)` between stage reveals for rhythm.
6. **Forgetting the "so what."** Every section should end with WHY this matters. After showing the method, add a text annotation or narration cue that says what the viewer just learned and why it is important.
7. **Animating everything.** Some things are better shown static. A table of hyperparameters does not need to fly in from the left. Use simple `FadeIn` and move on.
