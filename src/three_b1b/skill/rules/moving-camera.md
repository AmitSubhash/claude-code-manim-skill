---
name: 2D Camera Control
description: MovingCameraScene for zoom, pan, and follow animations in 2D Manim scenes
tags: [manim, camera, zoom, pan, movingcamera, zoomedscene]
---

# 2D Camera Control

**What is MovingCameraScene?** In a regular Scene, the camera is fixed -- it always
shows the same rectangular region of the coordinate plane. MovingCameraScene gives you
a camera you can zoom, pan, and follow objects with. **Why this matters:** when you
build a complex diagram that doesn't fit on one screen, or when you want to zoom into
a detail then zoom back out, you need camera control. The camera's "frame" is itself a
Mobject (a Rectangle) that defines what's visible. Animating the frame's position =
panning. Animating the frame's width = zooming. Because the frame is a Mobject, you
use the same `.animate` syntax you already know. Manim also provides `ZoomedScene` for
picture-in-picture insets where you magnify one region while keeping the full view.

## MovingCameraScene

Extends `Scene` with a movable 2D camera. The camera frame is a `Rectangle` mobject you can animate like any other mobject.

```python
from manim import *

class CameraDemo(MovingCameraScene):
    def construct(self) -> None:
        # self.camera.frame is the camera rectangle
        # Default: full scene width/height

        circle = Circle(radius=1, color=BLUE).shift(LEFT * 3)
        square = Square(side_length=1, color=RED).shift(RIGHT * 3)
        self.add(circle, square)
        self.wait()
```

## Zoom

Scale the camera frame to zoom in or out:

```python
class ZoomDemo(MovingCameraScene):
    def construct(self) -> None:
        details = VGroup(*[
            Dot(point=np.random.uniform(-1, 1, 3)) for _ in range(50)
        ])
        self.add(details)

        # Zoom in (smaller width = closer view)
        self.play(self.camera.frame.animate.set(width=4))
        self.wait()

        # Zoom out
        self.play(self.camera.frame.animate.set(width=14))
        self.wait()

        # Zoom with scale factor
        self.play(self.camera.frame.animate.scale(0.3))  # zoom in to 30%
        self.wait()
        self.play(self.camera.frame.animate.scale(1 / 0.3))  # zoom back out
```

## Pan

Move the camera frame to a different location:

```python
class PanDemo(MovingCameraScene):
    def construct(self) -> None:
        left_group = VGroup(
            Text("Section A"), Circle(radius=0.5)
        ).arrange(DOWN).shift(LEFT * 4)

        right_group = VGroup(
            Text("Section B"), Square(side_length=1)
        ).arrange(DOWN).shift(RIGHT * 4)

        self.add(left_group, right_group)

        # Pan to left group
        self.play(self.camera.frame.animate.move_to(left_group))
        self.wait()

        # Pan to right group
        self.play(self.camera.frame.animate.move_to(right_group))
        self.wait()

        # Pan back to center
        self.play(self.camera.frame.animate.move_to(ORIGIN))
        self.wait()
```

## Combined Zoom + Pan

Chain `.animate` calls for simultaneous zoom and pan:

```python
# Zoom into a specific region
self.play(
    self.camera.frame.animate.scale(0.5).move_to(target_mob),
    run_time=2,
)
```

## Follow a Moving Object

Use `add_updater` to track a mobject:

```python
class FollowDemo(MovingCameraScene):
    def construct(self) -> None:
        dot = Dot(color=RED)
        path = ParametricFunction(
            lambda t: np.array([2 * np.cos(t), 2 * np.sin(t), 0]),
            t_range=[0, TAU],
        )

        # Camera follows the dot
        self.camera.frame.add_updater(lambda f: f.move_to(dot))

        # Zoom in to follow closely
        self.camera.frame.set(width=6)

        self.add(path, dot)
        self.play(MoveAlongPath(dot, path), run_time=4, rate_func=linear)

        # Stop following
        self.camera.frame.clear_updaters()
        self.play(self.camera.frame.animate.set(width=14).move_to(ORIGIN))
```

## auto_zoom

Automatically zoom to fit a mobject with margin:

```python
class AutoZoomDemo(MovingCameraScene):
    def construct(self) -> None:
        group = VGroup(*[Circle(radius=0.3) for _ in range(5)]).arrange(RIGHT, buff=2)
        self.add(group)

        # Zoom to fit the first element
        self.camera.auto_zoom(group[0], animate=True, margin=1)
        self.wait()

        # Zoom to fit entire group
        self.camera.auto_zoom(group, animate=True, margin=0.5)
        self.wait()
```

## ZoomedScene (Picture-in-Picture)

Shows a zoomed-in inset view of part of the scene:

```python
class PIPZoom(ZoomedScene):
    def __init__(self, **kwargs):
        super().__init__(
            zoom_factor=0.3,              # how much to zoom
            zoomed_display_height=3,      # inset window height
            zoomed_display_width=3,       # inset window width
            image_frame_stroke_width=2,
            zoomed_camera_config={
                "default_frame_stroke_width": 3,
            },
            zoomed_camera_frame_starting_position=ORIGIN,
            **kwargs,
        )

    def construct(self) -> None:
        # Small details that need magnification
        tiny_text = Text("Fine Print", font_size=10).shift(UP)
        self.add(tiny_text)

        # The zoomed camera frame (what gets magnified)
        zoomed_camera = self.zoomed_camera
        zoomed_display = self.zoomed_display

        # Position the zoomed display (inset window)
        zoomed_display.to_corner(DR)

        # Activate the zoom
        self.activate_zooming(animate=True)
        self.wait()

        # Move the zoom frame around
        self.play(
            self.zoomed_camera.frame.animate.move_to(tiny_text),
            run_time=2,
        )
        self.wait(2)

        # Deactivate
        self.play(
            self.get_zoomed_display_pop_out_animation(),
            unfold_camera=True,
        )
```

## Camera Animation Patterns

### Progressive reveal

```python
class ProgressiveReveal(MovingCameraScene):
    def construct(self) -> None:
        # Create a long horizontal scene
        sections = VGroup()
        for i in range(5):
            section = VGroup(
                Text(f"Step {i + 1}", font_size=36),
                Circle(radius=0.5),
            ).arrange(DOWN)
            sections.add(section)
        sections.arrange(RIGHT, buff=3)

        # Start zoomed into first section
        self.camera.frame.move_to(sections[0]).set(width=6)
        self.add(sections[0])

        for i in range(1, 5):
            self.play(FadeIn(sections[i]))
            self.play(
                self.camera.frame.animate.move_to(sections[i]),
                run_time=1.5,
            )
            self.wait(0.5)

        # Zoom out to see everything
        self.play(
            self.camera.frame.animate.move_to(sections.get_center()).set(width=sections.width + 2),
            run_time=2,
        )
```

### Zoom into equation detail

```python
class ZoomEquation(MovingCameraScene):
    def construct(self) -> None:
        eq = MathTex(
            r"\int_0^\infty e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}",
            font_size=48,
        )
        self.play(Write(eq))
        self.wait()

        # Zoom into the integrand
        integrand = eq[0][4:10]  # approximate submobject range
        self.play(
            self.camera.frame.animate.set(width=3).move_to(integrand),
            run_time=2,
        )
        self.wait(2)

        # Zoom back out
        self.play(
            self.camera.frame.animate.set(width=14).move_to(ORIGIN),
            run_time=2,
        )
```

### Smooth camera path

```python
class SmoothPath(MovingCameraScene):
    def construct(self) -> None:
        points = [LEFT * 3 + UP * 2, RIGHT * 3 + DOWN, RIGHT * 3 + UP * 3]
        mobs = [Circle(radius=0.5, color=c).move_to(p)
                for p, c in zip(points, [RED, GREEN, BLUE])]
        self.add(*mobs)

        for mob in mobs:
            self.play(
                self.camera.frame.animate.set(width=4).move_to(mob),
                run_time=1.5,
                rate_func=smooth,
            )
            self.wait(0.5)
```
