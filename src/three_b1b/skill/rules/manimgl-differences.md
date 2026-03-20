---
name: ManimGL vs Community Edition
description: Key differences between ManimGL (3Blue1Brown) and Manim Community Edition, interactive mode, and when to use each
tags: [manim, manimgl, 3blue1brown, interactive, community]
---

# ManimGL vs Community Edition

**Why two versions of Manim?** Grant Sanderson (3Blue1Brown) created the original
Manim for his YouTube videos. The community forked it into "Manim Community Edition"
(CE) with better docs, pip install, and a broader contributor base. Grant continued
developing his version as "ManimGL" (GL = OpenGL), adding interactive features, live
coding, and GPU-accelerated rendering. Both produce beautiful math animations. The key
difference: CE is better for rendering final videos (stable, well-documented, Cairo
renderer). ManimGL is better for live demos and interactive exploration (OpenGL window,
IPython embedding, real-time manipulation). Do not install both in the same Python
environment -- they share the `manim` namespace and will conflict.

## Overview

| Feature | Community Edition (CE) | ManimGL |
|---|---|---|
| Install | `pip install manim` | `pip install manimgl` |
| Import | `from manim import *` | `from manimlib import *` |
| Renderer | Cairo (default) + OpenGL | OpenGL only |
| Backend | Cairo + FFmpeg | ModernGL + Pyglet |
| Preview | Opens file in media player | Native window (real-time) |
| Interactive | No | Yes (`self.embed()`) |
| Documentation | Excellent (docs.manim.community) | Sparse (source code is the docs) |
| Maintenance | Active community, regular releases | Grant Sanderson + small team |
| Best for | Final renders, CI/CD, reproducible | Live demos, prototyping, interactive |

## Installation

```bash
# Community Edition
pip install manim

# ManimGL
pip install manimgl
```

Do NOT install both in the same environment. They conflict.

## Key API Differences

### Imports

```python
# Community Edition
from manim import *

# ManimGL
from manimlib import *
```

### Scene classes

```python
# CE: only Scene
class MyScene(Scene):
    def construct(self):
        ...

# ManimGL: Scene and InteractiveScene
class MyScene(Scene):
    def construct(self):
        ...

class MyInteractive(InteractiveScene):
    def construct(self):
        ...
```

### Core animation API (mostly the same)

```python
# Both editions:
circle = Circle(radius=1, color=BLUE)
self.play(Create(circle))
self.play(circle.animate.shift(RIGHT * 2))
self.wait()
```

### Rendering differences

```python
# CE: renders to file, then plays
# CLI: manim -qh scene.py MyScene

# ManimGL: renders in real-time window
# CLI: manimgl scene.py MyScene
```

### Shader system

ManimGL uses a per-mobject shader system:

```python
# ManimGL: each mobject type has its own shader folder
# e.g., manimlib/shaders/quadratic_bezier_fill/
# CE uses Cairo drawing paths (no shaders for 2D)
```

### Configuration

```python
# CE: config object
from manim import config
config.pixel_width = 1920

# ManimGL: custom_config dict or CLI args
# manimgl scene.py MyScene -w 1920 -h 1080
```

## Interactive Mode (ManimGL Only)

The killer feature of ManimGL. Drop into an IPython shell mid-scene:

```python
class InteractiveDemo(InteractiveScene):
    def construct(self):
        circle = Circle(radius=1, color=BLUE)
        self.play(Create(circle))

        # Drop into interactive shell
        self.embed()
        # Now you can type in the terminal:
        # >>> self.play(circle.animate.shift(RIGHT))
        # >>> square = Square(); self.play(Create(square))
        # >>> exit()  # continues construct()

        self.play(FadeOut(circle))
```

### Live coding workflow

1. Run `manimgl scene.py InteractiveDemo`
2. Scene plays until `self.embed()`
3. IPython shell opens in the terminal
4. Type Manim commands, see results in real-time
5. `exit()` to continue the scene

### Selection tools

In interactive mode, you can click on mobjects in the window:

```python
# In the IPython shell:
# Click a mobject in the window, it becomes `self.selection`
mob = self.selection
mob.set_color(RED)
```

### Keyboard shortcuts (in interactive window)

| Key | Action |
|---|---|
| `g` | Grab (move) selected mobject |
| `t` | Resize (scale) selected mobject |
| `r` | Rotate selected mobject |
| `Cmd+z` / `Ctrl+z` | Undo |
| `Cmd+Shift+z` | Redo |
| `Scroll` | Zoom camera |
| `Click+Drag` | Pan camera |

### Event handlers (ManimGL)

Attach mouse/keyboard events to mobjects:

```python
class EventDemo(InteractiveScene):
    def construct(self):
        circle = Circle(radius=1, color=BLUE)

        def on_press(mob, event):
            mob.set_color(RED)

        def on_drag(mob, event):
            mob.move_to(event["point"])

        circle.on_mouse_press = on_press
        circle.on_mouse_drag = on_drag

        self.add(circle)
        self.embed()
```

## ManimGL Interactive Controls

ManimGL provides UI widgets for interactive scenes:

```python
from manimlib import *

class ControlDemo(InteractiveScene):
    def construct(self):
        # Slider
        slider = LinearNumberSlider(
            value=0.5,
            min_value=0,
            max_value=1,
        )

        # Checkbox
        checkbox = Checkbox(label="Show Grid")

        # Text input
        textbox = Textbox(placeholder="Enter value...")

        # Control panel groups them
        panel = ControlPanel(
            slider, checkbox, textbox,
        )
        self.add(panel)
        self.embed()
```

## When to Use Each Edition

### Use Community Edition (CE) when:

- Producing final rendered videos for YouTube/conferences
- Running in CI/CD pipelines (no display needed)
- Needing reproducible renders across machines
- Working with collaborators (better docs, more examples)
- Building a Manim + Remotion pipeline
- Need transparent background export (webm)
- Want the latest features and bug fixes

### Use ManimGL when:

- Giving live demos or lectures
- Prototyping animations interactively
- Teaching where you want real-time feedback
- Building interactive mathematical explorations
- Need to tweak animations without re-rendering
- Creating 3Blue1Brown-style content and want the exact same look

## Migration Notes: CE to ManimGL

Most code is compatible. Key differences to watch for:

```python
# CE: config.background_color = BLACK
# ManimGL: camera.background_color = BLACK (in scene)

# CE: self.camera.frame (in MovingCameraScene)
# ManimGL: self.camera.frame (in all scenes, camera is always movable)

# CE: ThreeDScene
# ManimGL: Scene (3D is always available, no special scene class)

# CE: add_fixed_in_frame_mobjects(mob)
# ManimGL: mob.fix_in_frame()

# CE: BarChart(values, bar_names, ...)
# ManimGL: no built-in BarChart (build manually)
```

## Migration Notes: ManimGL to CE

```python
# ManimGL: self.embed()
# CE: no equivalent (use -p flag for preview)

# ManimGL: InteractiveScene
# CE: no equivalent

# ManimGL: mob.fix_in_frame()
# CE: self.add_fixed_in_frame_mobjects(mob)

# ManimGL: self.camera.frame.animate.set_height(6)
# CE: self.camera.frame.animate.set(height=6)  (in MovingCameraScene)
```

## Recommendation

**Develop in Community Edition** for final output. Use ManimGL only when you specifically need interactive features for live demos or teaching. CE has better documentation, a larger community, more consistent behavior, and works in headless environments (servers, CI).

For the Manim + Remotion pipeline, always use Community Edition since it renders to files cleanly without requiring a display.
