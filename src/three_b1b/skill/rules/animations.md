---
name: Animation Types Reference
description: First-principles guide to Manim animations, from core concepts to composition
tags: [manim, animation, transform, rate-function, composition]
---

# Manim Animations: First-Principles Guide

## What is an animation in Manim?

An animation is a Python object that computes intermediate visual states of a
mobject over time. Animations are NOT functions -- they are objects you create
and pass to `self.play()`.

When you write `self.play(FadeIn(circle), run_time=2)`, Manim:
1. Captures the **start state** of `circle` (position, color, opacity, shape)
2. Determines the **end state** (fully visible)
3. Loops from **t=0 to t=1**, one step per video frame
4. Applies a **rate function** to t, producing a progress value
5. **Interpolates** the mobject between start/end at that progress
6. Renders each interpolated state as a frame

`run_time` controls real-world seconds (default: 1). The t=0-to-1 loop is
always the same -- longer `run_time` just means more frames.

Why objects? Because they carry configuration and Manim can compose them
(parallel, sequential) without special syntax.

## Your first animation

```python
from manim import *
class FirstAnimation(Scene):
    def construct(self):
        circle = Circle(radius=1, color=BLUE)      # mobject, NOT displayed yet
        self.play(Create(circle))                   # traces outline, then fills

        equation = MathTex(r"e^{i\pi} + 1 = 0").next_to(circle, DOWN)
        self.play(Write(equation))                  # simulates handwriting

        label = Text("Euler").next_to(equation, DOWN)
        self.play(FadeIn(label, shift=UP))          # fades in while sliding up
```

## Showing and hiding things

**Creation** -- each makes a mobject appear with a different visual effect:

| Animation | Visual effect |
|---|---|
| `Create(mob)` | Traces outline stroke, then fills the interior |
| `Write(mob)` | Simulates handwriting along the stroke path |
| `DrawBorderThenFill(mob)` | Draws full border first, then floods the fill |
| `ShowIncreasingSubsets(group)` | Reveals submobjects one at a time, keeping previous |
| `AddTextLetterByLetter(text)` | Types characters one by one like a terminal |
| `SpiralIn(group)` | Submobjects spiral inward from random outer positions |
| `GrowFromCenter(mob)` | Scales up from zero at the mob's center |
| `GrowFromEdge(mob, edge)` | Scales up from a specific edge (LEFT, RIGHT, UP, DOWN) |
| `SpinInFromNothing(mob)` | Scales up from zero while rotating in |

**Removal** -- each makes a mobject disappear:

| Animation | Visual effect |
|---|---|
| `Uncreate(mob)` | Reverse of Create: un-draws the stroke |
| `Unwrite(mob)` | Reverse of Write: erases the handwriting path |
| `FadeOut(mob)` | Fades opacity to 0. Accepts `shift=` and `scale=` |

```python
self.play(FadeIn(mob, shift=LEFT * 2))         # slides in from the right
self.play(FadeOut(mob, scale=0.5))             # shrinks while fading out
self.play(FadeIn(mob, target_position=other))  # fades in toward other mob
```

## Transforming one thing into another

A transform takes a source mobject and morphs it to look like a target by
interpolating every control point from source to target.

**Critical distinction -- Transform vs ReplacementTransform:**

- `Transform(A, B)`: After animation, **A is still the scene object** but
  looks like B. B was never added. Animating B later does nothing.
  *Analogy: putting a mask on A.*

- `ReplacementTransform(A, B)`: After animation, **A is removed, B is added**.
  B is the live object you can animate next.
  *Analogy: swapping A out for B on stage.*

```python
# Transform: square still in scene (looking like circle). circle NOT in scene.
self.play(Transform(square, circle))

# ReplacementTransform: square removed, circle added. Animate circle next.
self.play(ReplacementTransform(square, circle))
```

Use `ReplacementTransform` when you need to animate the target afterward.
Use `Transform` when you only need a visual morph.

**Other variants:**

```python
# TransformFromCopy(A, B): A stays. A COPY morphs into B. Both remain.
self.play(TransformFromCopy(eq1, eq2))

# FadeTransform(A, B): cross-fade. Better when shapes differ drastically.
self.play(FadeTransform(old_diagram, new_diagram))

# MoveToTarget: define end state procedurally, then animate to it.
mob.generate_target()           # mob.target = copy of mob
mob.target.shift(RIGHT * 2).set_color(RED)
self.play(MoveToTarget(mob))
```

## The .animate syntax

**Problem:** Turning "shift this circle right" into an animation requires
manually building a target and creating a Transform. Verbose for simple changes.

**Solution:** `.animate` captures method calls and converts them into an
animation. Under the hood it copies the mob, applies the methods to the copy,
then creates a Transform from original to copy.

```python
self.play(circle.animate.shift(RIGHT * 2))                          # single
self.play(circle.animate.shift(UP).scale(0.5).set_color(BLUE))     # chained
self.play(circle.animate.move_to(ORIGIN), run_time=3)              # with timing
self.play(circle.animate.shift(RIGHT * 3), rate_func=there_and_back)
```

## Highlighting and indicating

These draw attention **without permanently changing** the mobject:

```python
self.play(Indicate(mob))                    # scales up, flashes color, reverts
self.play(Flash(mob.get_center(), color=YELLOW, line_length=0.5))  # radial burst
self.play(Circumscribe(mob, color=RED, shape=Rectangle))  # draws shape around mob
self.play(Wiggle(mob))                      # oscillates side to side
self.play(ApplyWave(mob, direction=UP, amplitude=0.3))    # ripple deformation
self.play(FocusOn(mob))                     # dims surroundings, spotlights target
```

## Rate functions: controlling the feel of motion

A rate function maps normalized time (0 to 1) to progress (0 to 1). It
controls acceleration -- the "gas pedal" curve.

Default is `smooth`: starts slow, accelerates, decelerates. Like a real object
with inertia. Without it (`linear`), everything moves at constant speed.

```python
self.play(mob.animate.shift(RIGHT * 3), rate_func=rush_into, run_time=2)
```

| Function | Feel | Use for |
|---|---|---|
| `linear` | Constant speed | Continuous processes, tickers |
| `smooth` | Natural accel/decel (default) | Most animations |
| `rush_into` | Slow start, fast end | Object "commits" to motion |
| `rush_from` | Fast start, slow end | Object "lands" into position |
| `there_and_back` | Goes to target, returns | Temporary emphasis |
| `ease_in_out_sine` | Gentle S-curve | CSS-style easing |
| `ease_in_back` | Pulls back before moving | Windup before action |
| `ease_out_bounce` | Bounces on arrival | Playful landings |
| `running_start` | Pullback then overshoot | Springy start |
| `lingering` | Hovers at end | Contemplative feel |

**squish_rate_func(func, a, b):** Compresses animation into time sub-interval.
Before `a`: nothing happens. After `b`: animation is done.

```python
# Animation only runs during the 30%-70% window of run_time.
self.play(
    mob.animate.shift(RIGHT),
    rate_func=squish_rate_func(smooth, 0.3, 0.7), run_time=3,
)
```

## Composing multiple animations

**Parallel (simplest):** Multiple args to `self.play()`. Same run_time.
```python
self.play(FadeIn(title), Create(circle), Write(equation))
```

**AnimationGroup:** `lag_ratio=0` (default) = all at once. `lag_ratio=0.2` =
each starts when previous is 20% done.
```python
self.play(AnimationGroup(FadeIn(a), FadeIn(b), FadeIn(c), lag_ratio=0.3))
```

**LaggedStart:** Designed for staggered starts. Creates "wave" / "cascade".
```python
mobs = VGroup(*[Circle() for _ in range(5)]).arrange(RIGHT)
self.play(LaggedStart(
    *[FadeIn(m, shift=UP) for m in mobs], lag_ratio=0.2, run_time=2,
))
```

**LaggedStartMap:** Same animation class applied to every item with stagger.
```python
self.play(LaggedStartMap(FadeIn, mobs, shift=UP, lag_ratio=0.15))
```

**Succession:** Sequential animations in one `play()` call.
```python
self.play(Succession(FadeIn(mob), mob.animate.shift(RIGHT), FadeOut(mob)))
```

| Need | Use |
|---|---|
| Simple parallel | Multiple args to `self.play()` |
| Parallel with stagger | `AnimationGroup(lag_ratio=...)` |
| Cascading reveals | `LaggedStart` or `LaggedStartMap` |
| Sequential in one call | `Succession` |

## Movement animations

```python
# MoveAlongPath: mob follows a VMobject path (Arc, Line, CubicBezier)
self.play(MoveAlongPath(dot, Arc(angle=PI, radius=2), run_time=2))

# Rotate: by angle (radians), optionally around a point
self.play(Rotate(mob, angle=PI / 2))                    # 90 deg in place
self.play(Rotate(mob, angle=TAU, about_point=ORIGIN))   # full orbit

# Homotopy: most general -- f(x, y, z, t) -> (x', y', z')
self.play(Homotopy(
    lambda x, y, z, t: (x + t, y + np.sin(t * PI) * 0.5, z), mob,
))
```

## Common patterns

### Pattern 1: Equation derivation chain
ReplacementTransform so each new equation is the live object for the next step.
```python
eq1 = MathTex(r"f(x) = x^2")
eq2 = MathTex(r"f'(x) = 2x")
eq3 = MathTex(r"f''(x) = 2")
self.play(Write(eq1))
self.play(ReplacementTransform(eq1, eq2))
self.play(ReplacementTransform(eq2, eq3))
```

### Pattern 2: Highlight then transform
Indicate returns to original state, so the transform starts clean.
```python
self.play(Indicate(source, color=YELLOW))
self.wait(0.3)
self.play(ReplacementTransform(source, target))
```

### Pattern 3: Staggered grid reveal
```python
grid = VGroup(*[Square(side_length=0.5) for _ in range(12)]).arrange_in_grid(3, 4)
self.play(LaggedStartMap(FadeIn, grid, shift=UP * 0.3, lag_ratio=0.1, run_time=2))
self.play(grid.animate.set_color(BLUE), run_time=1)
```

### Pattern 4: Offset timing with squish_rate_func
Three animations in one play(), each in a different time window.
```python
self.play(
    mob_a.animate.shift(RIGHT * 2),                                   # full duration
    AnimationGroup(mob_b.animate.shift(LEFT),
                   rate_func=squish_rate_func(smooth, 0.0, 0.5)),     # first half
    AnimationGroup(FadeIn(mob_c),
                   rate_func=squish_rate_func(smooth, 0.5, 1.0)),     # second half
    run_time=3,
)
```

### Pattern 5: FadeTransform for dissimilar shapes
`Transform` interpolates control points, which looks broken when source and target
have very different geometry (e.g., a circle morphing into a bar chart). Use
`FadeTransform` instead: it cross-fades, producing a clean visual transition.

```python
# BAD: control point interpolation creates ugly intermediate shapes
self.play(Transform(pie_chart, bar_chart))

# GOOD: cross-fade for dissimilar shapes
self.play(FadeTransform(pie_chart, bar_chart))
```

Use `Transform` / `ReplacementTransform` when source and target share similar
structure (equation to equation, circle to ellipse). Use `FadeTransform` when
they differ structurally (diagram to chart, text to equation, pipeline to table).

### Pattern 6: TracedPath for following moving objects
`TracedPath` draws a trail behind a moving mobject. Useful for showing trajectories,
gradient descent paths, or orbit traces.

```python
dot = Dot(axes.c2p(0, 0), color=YELLOW)
trace = TracedPath(dot.get_center, stroke_color=YELLOW, stroke_opacity=0.6)
self.add(trace)

# The trace builds as the dot moves
self.play(MoveAlongPath(dot, axes.plot(lambda x: np.sin(x)), run_time=4))
```

Note: Add the `TracedPath` to the scene BEFORE animating the dot. The path
accumulates points from the moment it is added.

### Pattern 7: ShowPassingFlash for highlight sweeps
`ShowPassingFlash` runs a bright flash along a VMobject's path. Good for
emphasizing curves, edges, or connections without permanently changing them.

```python
curve = axes.plot(lambda x: x**2, color=BLUE)
self.add(curve)

# Flash sweeps along the curve
self.play(ShowPassingFlash(
    curve.copy().set_color(YELLOW).set_stroke(width=8),
    time_width=0.3,  # fraction of path lit at once (0 to 1)
    run_time=2,
))
```

Combine with `LaggedStart` for cascading flashes across multiple edges in
a graph or network diagram.
