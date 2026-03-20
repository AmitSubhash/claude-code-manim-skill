---
name: First Scene Tutorial
description: Complete walkthrough for someone who has never used Manim - from install to first rendered video
tags: [manim, tutorial, beginner, getting-started, first-principles]
---

# Your First Manim Scene - From Zero

## What is Manim?

Manim is a Python library that creates mathematical animations as video files. You write Python code describing what should appear on screen and how it should move, and Manim renders it frame-by-frame into an MP4 or other video format.

Manim was originally created by Grant Sanderson (3Blue1Brown) to produce his YouTube videos. The version we use is **Manim Community Edition**, maintained by an open-source community.

## Install

```bash
pip install manim

# macOS also needs:
brew install py3cairo ffmpeg

# Linux:
# sudo apt install libcairo2-dev ffmpeg libpango1.0-dev
```

Verify the install:
```bash
manim --version
```

You also need a working LaTeX installation for equation rendering:
```bash
# macOS
brew install --cask mactex-no-gui

# Linux
# sudo apt install texlive-full
```

## Your first scene: a circle appears

Create a file called `scene.py`:

```python
from manim import *
# This imports everything: Scene, Circle, colors (RED, BLUE, ...),
# directions (UP, DOWN, LEFT, RIGHT), animations (Create, Write, FadeIn), etc.

class FirstScene(Scene):
    # Every Manim scene is a Python class that inherits from Scene.
    # Scene provides the canvas, camera, and animation engine.

    def construct(self):
        # construct() is the method Manim calls to build your video.
        # Everything you want to animate goes here.

        # Step 1: Create a circle object
        circle = Circle(radius=1, color=BLUE, fill_opacity=0.5)
        # This does NOT show the circle yet. It just creates it in memory.
        # radius=1 means 1 Manim unit (the screen is ~14 units wide, ~8 tall)
        # fill_opacity=0.5 means 50% transparent interior

        # Step 2: Animate the circle appearing on screen
        self.play(Create(circle))
        # self.play() runs an animation and renders frames to the video.
        # Create() traces the outline of the shape, then fills it.
        # This takes 1 second by default.

        # Step 3: Pause so the viewer can see it
        self.wait(2)
        # Holds the current frame for 2 seconds.
```

## Render it

```bash
# Quick low-quality preview (fast, opens player when done)
manim -pql scene.py FirstScene

# Flags explained:
#   -p     preview (open the video after rendering)
#   -q l   quality: l=low (480p), m=medium (720p), h=high (1080p), k=4K
```

You should see a blue circle traced and filled on a black background.

## Understanding the output

Manim creates a `media/` folder:
```
media/
  videos/
    scene/
      480p15/           # resolution and framerate
        FirstScene.mp4  # your video!
```

## Adding more objects and animations

```python
class SecondScene(Scene):
    def construct(self):
        # Create objects
        circle = Circle(radius=1, color=BLUE, fill_opacity=0.5)
        square = Square(side_length=2, color=RED)
        text = Text("Hello Manim!", font_size=48)

        # Position them: text at top, shapes below side by side
        text.to_edge(UP)           # snap to top of screen
        circle.shift(2 * LEFT)     # move 2 units left of center
        square.shift(2 * RIGHT)    # move 2 units right of center

        # Animate: text writes itself, then shapes appear
        self.play(Write(text))     # Write simulates handwriting
        self.wait(0.5)

        self.play(
            Create(circle),        # both animations run
            FadeIn(square),        # SIMULTANEOUSLY (same play call)
        )
        self.wait()

        # Transform the circle into the square
        self.play(Transform(circle, square.copy().shift(4 * LEFT)))
        self.wait()

        # Clean up: fade everything out
        self.play(FadeOut(text), FadeOut(circle), FadeOut(square))
```

## Your first equation

```python
class EquationScene(Scene):
    def construct(self):
        # MathTex renders LaTeX math. Use raw strings (r"...") for backslashes.
        equation = MathTex(r"e^{i\pi} + 1 = 0", font_size=72)

        # Write the equation with a handwriting animation
        self.play(Write(equation))
        self.wait(2)

        # Change its color smoothly
        self.play(equation.animate.set_color(YELLOW))
        # .animate turns any method call into an animation
        self.wait()
```

## Key concepts recap

| Concept | What it means |
|---|---|
| `Scene` | The canvas. Your class inherits from it. |
| `construct()` | The method where you build your animation. |
| `Mobject` | Any visual object (circle, text, equation, arrow, etc.) |
| `self.play()` | Run animation(s) and render frames to the video. |
| `self.wait()` | Pause for N seconds (default 1). |
| `self.add()` | Put a Mobject on screen instantly (no animation). |
| `Create()` | Animation: traces the outline of a shape. |
| `Write()` | Animation: handwriting effect for text/equations. |
| `FadeIn()` | Animation: fades from transparent to visible. |
| `Transform(A, B)` | Animation: morphs A to look like B. |
| `.animate` | Turns any Mobject method into an animation. |

## What to learn next

1. **mobjects.md** - All the objects you can create and how to position them
2. **equations.md** - LaTeX equations, coloring terms, step-by-step derivations
3. **animations.md** - Every animation type, rate functions, composition
4. **updaters-trackers.md** - Dynamic, continuous animations
5. **paper-explainer.md** - Structuring a research paper explainer video

## Quick reference: render commands

```bash
manim -pql file.py Scene     # low quality preview
manim -pqm file.py Scene     # medium quality preview
manim -pqh file.py Scene     # high quality preview (1080p)
manim -qk file.py Scene      # 4K render (no preview)
manim -pqh -s file.py Scene  # save last frame as PNG
manim -pqh -a file.py        # render ALL scenes in file
```
