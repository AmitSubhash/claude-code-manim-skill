---
name: scene-lifecycle
description: Scene types, lifecycle methods, play/wait/add/remove, camera setup
tags: scene, lifecycle, camera, construct
---

# Scene Architecture and Lifecycle

## Conceptual Overview

What is a Scene? A Scene is the container for your entire animation. Think of it as a stage in a theater: it has a camera pointing at it, objects (Mobjects) placed on it, and a timeline of events (animations). When you write a Scene class, Manim creates the stage, calls your `construct()` method to let you place objects and run animations, then renders every frame to a video file.

The `construct()` method is where ALL your animation code goes. Manim calls it exactly once. Inside it, you use `self.play()` to run animations (which renders frames to the video), `self.add()` to place objects instantly (no animation), `self.wait()` to hold the current frame, and `self.remove()` to take objects off the stage.

The rendering loop: when you call `self.play(animation)`, Manim runs a loop from t=0 to t=run_time. At each timestep, it computes the interpolated state of all animated objects, renders the frame, and writes it to the video file. This is why "playing" an animation literally means "rendering frames." If you never call `self.play()` or `self.wait()`, no frames are rendered and you get an empty video.

There is also `setup()` (called before `construct()`) for shared initialization across scene subclasses, and `tear_down()` (called after `construct()`) for cleanup. Most scenes only need `construct()`.

## Scene Types

| Scene Class | Import | Use Case |
|---|---|---|
| `Scene` | `from manim import *` | Standard 2D animations |
| `MovingCameraScene` | `from manim import *` | 2D with zoom/pan camera |
| `ThreeDScene` | `from manim import *` | 3D scenes with perspective camera |
| `SpecialThreeDScene` | `from manim import *` | 3D with auto-shading defaults |
| `VectorSpaceScene` | `from manim import *` | Linear algebra vector space |
| `ZoomedScene` | `from manim import *` | Picture-in-picture zoom |

## Scene Lifecycle

```python
class MyScene(Scene):
    def setup(self):
        """Called before construct(). Use for shared setup across scenes."""
        self.tracker = ValueTracker(0)

    def construct(self):
        """Main method. All animation logic goes here."""
        circle = Circle()
        self.play(Create(circle))
        self.wait()

    def tear_down(self):
        """Called after construct(). Cleanup if needed."""
        pass
```

## Core Scene Methods

### Adding/Removing Mobjects

```python
self.add(mob1, mob2)           # Add to scene instantly (no animation)
self.remove(mob1)              # Remove instantly
self.clear()                   # Remove everything
```

### Playing Animations

```python
# Single animation
self.play(Write(text))

# Multiple simultaneous animations
self.play(
    Write(text),
    Create(circle),
    FadeIn(square),
    run_time=2              # shared run_time
)

# Sequential (within one play call using Succession)
from manim import Succession
self.play(Succession(Write(text), FadeOut(text)))
```

### Waiting

```python
self.wait()                    # Default 1 second
self.wait(3)                   # 3 seconds
self.wait(frozen_frame=False)  # Keep updaters running during wait
```

### Key Parameters for play()

```python
self.play(
    animation,
    run_time=1,                # Duration in seconds (default 1)
    rate_func=smooth,          # Easing function
    lag_ratio=0,               # Stagger submobject animations (0-1)
)
```

## Frame Dimensions

The default Manim frame is 14.2 units wide and 8 units tall:

```python
from manim import config

config.frame_width   # 14.222... (default)
config.frame_height  # 8.0 (default)
```

Screen edges are approximately at:
- Left/Right: +/-7.1 units
- Top/Bottom: +/-4 units

## Coordinate System

Manim uses a standard math coordinate system:
- Origin (0, 0, 0) is at screen center
- X increases rightward
- Y increases upward
- Z increases toward viewer (OUT direction)

```python
ORIGIN = np.array([0, 0, 0])
UP     = np.array([0, 1, 0])
DOWN   = np.array([0, -1, 0])
LEFT   = np.array([-1, 0, 0])
RIGHT  = np.array([1, 0, 0])
OUT    = np.array([0, 0, 1])
IN     = np.array([0, 0, -1])

# Diagonals
UL = UP + LEFT
UR = UP + RIGHT
DL = DOWN + LEFT
DR = DOWN + RIGHT
```

## Sections (for video editors)

```python
class SectionedScene(Scene):
    def construct(self):
        self.next_section("Introduction")
        # ... animations ...

        self.next_section("Main Content", skip_animations=False)
        # ... animations ...

        self.next_section("Conclusion")
        # ... animations ...
```

Sections split the output into labeled video files for editing.
