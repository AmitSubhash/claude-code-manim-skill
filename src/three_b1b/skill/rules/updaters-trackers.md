---
name: Updaters and Value Trackers
description: Dynamic animations with ValueTracker, add_updater, always_redraw, and time-dependent updates
tags: [manim, updater, valuetracker, dynamic, interactive]
---

# Updaters and Value Trackers

## The problem updaters solve

Normal Manim animations are discrete: `self.play()` transitions from state A
to state B. But what if you want CONTINUOUS relationships -- a label that
always hovers above a moving dot, or a line that always connects two points?

Without updaters, you must manually reposition every dependent object before
every `self.play()`. Five animations that move a dot means five manual
repositioning calls for the label. Miss one and it freezes in the wrong spot.

Updaters let you declare a relationship ONCE. An updater is a function that
Manim calls EVERY FRAME (30-60fps) to enforce that relationship, no matter
what else is happening in the scene.

## ValueTracker: an invisible steering wheel

A ValueTracker is an invisible Mobject that holds a single float. It never
appears on screen. It exists to give you something to ANIMATE that other
objects can REACT TO. Think of it as a slider: drag the slider from 0 to 5,
and every object wired to it responds in real time.

The pattern is always three steps:
1. Create a tracker (the invisible slider)
2. Create visible objects that READ the tracker's value via updaters
3. Animate the tracker -- all dependents update automatically

```python
tracker = ValueTracker(0)        # invisible, stores 0.0
# A Mobject that draws nothing. Its only job: be animated while others react.

tracker.get_value()              # read: 0.0
tracker.set_value(5)             # write: instantly jumps to 5.0
tracker.increment_value(2)       # write: adds 2.0

# The real power -- animate it smoothly:
self.play(tracker.animate.set_value(10), run_time=3)
# Over 3s the value glides 5.0 -> 10.0. Updaters see every intermediate value.
```

## Your first updater

`mob.add_updater(func)` tells Manim: "call `func(mob)` every single frame."
The function receives the mobject itself. It runs continuously -- during
`play()`, during `wait()`, any time the scene renders.

```python
number_line = NumberLine(x_range=[0, 10])
tracker = ValueTracker(0)
dot = Dot(color=RED)
dot.add_updater(lambda d: d.move_to(number_line.n2p(tracker.get_value())))
# d IS the dot. Every frame it moves to wherever tracker points.

self.add(number_line, dot)
self.play(tracker.animate.set_value(8), run_time=3)
# As tracker glides 0 -> 8, dot slides along the number line.
```

Stack multiple updaters on one object (they run in order added):

```python
label = Text("here")
label.add_updater(lambda l: l.next_to(dot, UP, buff=0.2))   # follow dot
label.add_updater(lambda l: l.set_opacity(tracker.get_value() / 10))  # fade
```

## Time-based updaters (with dt)

If your updater accepts TWO arguments `(mobject, dt)`, Manim passes the time
elapsed since the last frame (~0.033s at 30fps, ~0.016s at 60fps). Use for
physics-like continuous motion independent of any ValueTracker.

```python
square = Square(color=BLUE)
square.add_updater(lambda m, dt: m.rotate(dt * PI / 2))
# Rotates 90 deg/s indefinitely. Multiplying by dt keeps speed framerate-independent.

self.add(square)
self.wait(4)  # spins for 4 seconds
```

## DecimalNumber: showing live values

DecimalNumber displays a formatted number. Paired with an updater it becomes
a live readout. Use `Integer` for whole numbers.

```python
tracker = ValueTracker(0)
dot = Dot(color=RED)
dot.add_updater(lambda d: d.move_to(RIGHT * tracker.get_value()))

decimal = DecimalNumber(0, num_decimal_places=2, font_size=36)
decimal.add_updater(lambda d: d.set_value(tracker.get_value()))
decimal.add_updater(lambda d: d.next_to(dot, UP))
# Two updaters: (1) update displayed number, (2) reposition above dot.

self.add(dot, decimal)
self.play(tracker.animate.set_value(5), run_time=3)
```

## always_redraw: the nuclear option

Sometimes you need to completely RECREATE a mobject every frame. A Line's
geometry (start/end points) is baked in at construction -- you cannot just
"move" it. You need a new Line with new endpoints each frame.

`always_redraw(lambda: ...)` calls your lambda every frame, gets a fresh
mobject, and swaps in the replacement.

```python
line = always_redraw(
    lambda: Line(dot1.get_center(), dot2.get_center(), color=YELLOW)
)
self.add(line)
self.play(dot1.animate.shift(UP * 2), dot2.animate.shift(DOWN * 2))
```

**When to use always_redraw vs add_updater:**
- `add_updater`: object's SHAPE stays the same; you change position, color,
  scale, or opacity. Fast (modifies in place).
- `always_redraw`: object's GEOMETRY changes (different endpoints, curve shape,
  brace width). Slower (reconstructs every frame).

Rule of thumb: if `move_to`/`next_to`/`set_color` can express the update, use
`add_updater`. If you need different constructor arguments, use `always_redraw`.

## Removing updaters

```python
def follow_dot(label: Mobject) -> None:
    label.next_to(dot, UP)

label.add_updater(follow_dot)
label.remove_updater(follow_dot)  # remove specific updater (needs reference)
label.clear_updaters()            # remove ALL updaters
```

During `self.wait()`, updaters still run. For a truly frozen frame:

```python
self.wait(2, frozen_frame=True)   # no updaters fire
```

## UpdateFromFunc and UpdateFromAlphaFunc animations

Wrap updater-like behavior into a finite animation with a `run_time`. Use when
you want frame-by-frame control for only one `play()` call.

```python
# UpdateFromFunc: called every frame during the animation
self.play(
    tracker.animate.set_value(5),
    UpdateFromFunc(dot, lambda d: d.move_to(axes.c2p(tracker.get_value(), 0))),
    run_time=3,
)

# UpdateFromAlphaFunc: func receives (mob, alpha) where alpha goes 0 -> 1
self.play(
    UpdateFromAlphaFunc(circle, lambda m, a: m.set_opacity(a)),
    run_time=2,
)
```

## ComplexValueTracker

Like ValueTracker but stores a complex number. Useful for complex plane
animations (Mobius transforms, conformal maps, polar coordinates).

```python
z_tracker = ComplexValueTracker(1 + 2j)
z_tracker.get_value()   # (1+2j)
self.play(z_tracker.animate.set_value(3 - 1j), run_time=2)
```

## Practical patterns (complete examples)

### Pattern 1: Label following a point on a graph

```python
class TracingLabel(Scene):
    def construct(self) -> None:
        axes = Axes(x_range=[0, 4, 1], y_range=[0, 16, 4])
        graph = axes.plot(lambda x: x**2, color=BLUE)
        t = ValueTracker(0.5)

        dot = always_redraw(
            lambda: Dot(axes.c2p(t.get_value(), t.get_value() ** 2), color=RED)
        )
        label = always_redraw(
            lambda: MathTex(
                f"({t.get_value():.1f},\\;{t.get_value()**2:.1f})"
            ).scale(0.7).next_to(dot, UR, buff=0.15)
        )

        self.add(axes, graph, dot, label)
        self.play(t.animate.set_value(3.5), run_time=4, rate_func=linear)
```

### Pattern 2: Dynamic area under a curve

```python
class DynamicArea(Scene):
    def construct(self) -> None:
        axes = Axes(x_range=[0, 4, 1], y_range=[0, 8, 2])
        graph = axes.plot(lambda x: x**2, color=BLUE)
        t = ValueTracker(0.5)

        area = always_redraw(
            lambda: axes.get_area(
                graph, x_range=[0, t.get_value()], color=BLUE, opacity=0.4
            )
        )
        area_label = always_redraw(
            lambda: DecimalNumber(
                (t.get_value() ** 3) / 3, num_decimal_places=2
            ).next_to(axes, RIGHT).shift(UP)
        )

        self.add(axes, graph, area, area_label)
        self.play(t.animate.set_value(3), run_time=4, rate_func=linear)
```

### Pattern 3: Connected diagram

```python
class ConnectedDiagram(Scene):
    def construct(self) -> None:
        dot_a = Dot(LEFT * 3, color=RED)
        dot_b = Dot(RIGHT * 3, color=BLUE)

        connector = always_redraw(
            lambda: Line(dot_a.get_center(), dot_b.get_center(), color=WHITE)
        )
        mid_label = always_redraw(
            lambda: Text("midpoint", font_size=24).move_to(
                (dot_a.get_center() + dot_b.get_center()) / 2 + UP * 0.4
            )
        )

        self.add(dot_a, dot_b, connector, mid_label)
        self.play(dot_a.animate.shift(UP * 2 + RIGHT), run_time=2)
        self.play(dot_b.animate.shift(DOWN * 2 + LEFT), run_time=2)
        self.play(
            dot_a.animate.move_to(LEFT),
            dot_b.animate.move_to(RIGHT),
            run_time=2,
        )
```

### Pattern 4: Live computation display

```python
class LiveComputation(Scene):
    def construct(self) -> None:
        x_tracker = ValueTracker(0)

        labels = VGroup(
            MathTex("x = "), MathTex("x^2 = "), MathTex("\\sin(x) = ")
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5).shift(LEFT * 2)

        values = [DecimalNumber(0, num_decimal_places=3) for _ in range(3)]
        funcs = [
            lambda v: x_tracker.get_value(),
            lambda v: x_tracker.get_value() ** 2,
            lambda v: np.sin(x_tracker.get_value()),
        ]
        for val, lbl, fn in zip(values, labels, funcs):
            val.next_to(lbl, RIGHT)
            val.add_updater(lambda d, f=fn: d.set_value(f(d)))
            val.add_updater(lambda d, l=lbl: d.next_to(l, RIGHT))

        self.add(labels, *values)
        self.play(
            x_tracker.animate.set_value(2 * PI), run_time=6, rate_func=linear
        )
```
