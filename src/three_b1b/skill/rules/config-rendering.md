---
name: Configuration and Rendering
description: Quality presets, CLI flags, output formats, config files, and rendering options for Manim
tags: [manim, config, rendering, quality, output, cli]
---

# Configuration and Rendering

## Conceptual Overview

What does rendering configuration control? When Manim builds your video, it needs to know: how many pixels wide/tall (resolution), how many frames per second (frame rate), what format to save (mp4, webm, gif), and what background color to use. These settings control the tradeoff between render speed and output quality. During development, use low quality (`-ql`, 480p at 15fps) for fast iteration. For final output, use high (`-qh`, 1080p at 60fps) or 4K (`-qk`).

Configuration can be set in three places, from lowest to highest priority: (1) `manim.cfg` file in your project root (project-level defaults), (2) Python `config` object in your script (programmatic control), (3) CLI flags when you run `manim` (per-render overrides). CLI flags always win.

## Quality Presets

| Preset | Resolution | FPS | CLI Flag |
|---|---|---|---|
| Low | 854x480 | 15 | `-ql` |
| Medium | 1280x720 | 30 | `-qm` |
| High | 1920x1080 | 60 | `-qh` |
| Production | 2560x1440 | 60 | `-qp` |
| Four K | 3840x2160 | 60 | `-qk` |

## CLI Usage

### Basic rendering

```bash
# Render a specific scene at low quality
manim -ql scene.py MyScene

# Render at high quality
manim -qh scene.py MyScene

# Render and preview immediately
manim -qm -p scene.py MyScene

# Save last frame as PNG (no video)
manim -qs scene.py MyScene

# Render all scenes in the file
manim -ql -a scene.py
```

### Output format

```bash
# MP4 (default)
manim -qh --format mp4 scene.py MyScene

# GIF
manim -qm --format gif scene.py MyScene

# WebM (supports transparency)
manim -qh --format webm scene.py MyScene

# PNG sequence
manim -qh --format png scene.py MyScene
```

### Transparency

```bash
# Transparent background (use webm, not mp4 -- mp4 does not support alpha)
manim -qh --format webm -t scene.py MyScene

# -t is shorthand for --transparent
```

### FPS override

```bash
manim -qh --fps 30 scene.py MyScene
```

### Renderer selection

```bash
# Cairo renderer (default, recommended for final renders)
manim --renderer cairo scene.py MyScene

# OpenGL renderer (faster preview, interactive)
manim --renderer opengl scene.py MyScene
```

## Python Config API

Set configuration programmatically before scene construction:

```python
from manim import config

# Resolution
config.pixel_width = 1920
config.pixel_height = 1080
config.frame_rate = 30

# Background
config.background_color = "#1a1a2e"
config.background_opacity = 1.0  # 0 for transparent

# Output
config.media_dir = "./media"
config.video_dir = "./media/videos"
config.images_dir = "./media/images"

# Quality shorthand
config.quality = "high_quality"  # or "low_quality", "medium_quality", "fourk_quality"
```

## Output Directory Structure

Manim organizes output as:

```
media/
  videos/
    scene_file_name/
      480p15/          # low quality
        MyScene.mp4
      720p30/          # medium quality
        MyScene.mp4
      1080p60/         # high quality
        MyScene.mp4
  images/
    scene_file_name/
      MyScene_ManimCE_v0.18.0.png
  texts/               # cached LaTeX
  Tex/                 # compiled LaTeX
```

## manim.cfg (Project-Level Config)

Place a `manim.cfg` file in your project root:

```ini
[CLI]
# Quality
quality = high_quality
fps = 30

# Output
media_dir = ./media
video_dir = ./media/videos

# Background
background_color = #1a1a2e
background_opacity = 1

# Renderer
renderer = cairo

# LaTeX
tex_template_file = ./custom_template.tex

# Preview
preview = True
```

### Section structure

```ini
[CLI]
# Main CLI flags

[logger]
# Logging configuration
log_dir = ./logs

[jupyter]
# Jupyter notebook settings
media_width = 60%
```

## Transparent Background

For overlay clips (e.g., for Remotion compositing):

```python
# In Python
config.background_opacity = 0

# Must use webm format (mp4 does not support alpha channel)
# CLI: manim -qh --format webm -t scene.py MyScene
```

For opaque clips with custom background color:

```python
config.background_color = "#0d1117"  # dark blue-black
```

## Remotion Integration Notes

When rendering clips for Remotion composition:

```bash
# Opaque clips (most common)
manim -qh --fps 30 --format mp4 scene.py SceneName

# Transparent overlay clips
manim -qh --fps 30 --format webm -t scene.py SceneName
```

Match Manim settings to your Remotion project:
- Resolution: both at 1920x1080
- Frame rate: both at 30fps (or both at 60fps)
- Use mp4 for opaque backgrounds, webm for transparent overlays

## Custom TexTemplate

For LaTeX packages not included by default:

```python
from manim import TexTemplate

template = TexTemplate()
template.add_to_preamble(r"\usepackage{physics}")
template.add_to_preamble(r"\usepackage{siunitx}")
template.add_to_preamble(r"\usepackage{chemfig}")

# Use globally
config.tex_template = template

# Or per-mobject
eq = MathTex(r"\qty{9.8}{\meter\per\second\squared}", tex_template=template)
```

## manim.cfg Project Configuration

Place `manim.cfg` in your project root to set defaults for all renders in that directory. This avoids repeating CLI flags and ensures consistency across team members.

### Recommended starter config

```ini
[CLI]
# Visual defaults
background_color = #1a1a2e
background_opacity = 1
fps = 30

# Output
media_dir = ./media
video_dir = ./media/videos
images_dir = ./media/images

# Quality (override per-render with -ql, -qh, etc.)
quality = medium_quality

# Resolution (only needed if you want non-standard sizes)
pixel_height = 1080
pixel_width = 1920

# Renderer
renderer = cairo

# Preview
preview = False

# LaTeX
# tex_template_file = ./custom_template.tex
```

### Common project-level overrides

| Setting | Value | Use case |
|---------|-------|----------|
| `background_color` | `#1a1a2e` | Dark blue-black (3b1b style) |
| `background_color` | `#0d1117` | GitHub dark theme |
| `background_color` | `#ffffff` | White background for print/slides |
| `frame_rate` / `fps` | 30 | Standard video (default for `-qm`) |
| `frame_rate` / `fps` | 60 | Smooth animation (default for `-qh`) |
| `pixel_height` | 1080 | Standard HD |
| `pixel_height` | 2160 | 4K output |
| `output_file` | `my_video` | Custom output filename |

### Programmatic equivalent

```python
from manim import config

config.background_color = "#1a1a2e"
config.frame_rate = 30
config.pixel_height = 1080
config.pixel_width = 1920
config.media_dir = "./media"
```

CLI flags always override `manim.cfg`, which overrides Python `config` defaults.

## Chapter Markers with next_section()

Use `self.next_section()` to mark logical chapter breaks in your scene. Each section becomes a separate video file when rendered with `--save_sections`, useful for compositing, chaptered uploads, or isolating specific parts for re-rendering.

### Basic usage

```python
class FullVideo(Scene):
    def construct(self) -> None:
        self.next_section("Hook")
        title = Text("Attention Is All You Need", font_size=36)
        self.play(Write(title))
        self.wait(2)

        self.next_section("Problem")
        self.play(FadeOut(title))
        problem = Text("RNNs are slow. Can we do better?", font_size=28)
        self.play(Write(problem))
        self.wait(2)

        self.next_section("Method")
        self.play(FadeOut(problem))
        # ... method explanation ...

        self.next_section("Results")
        # ... results ...

        self.next_section("Takeaway")
        # ... closing ...
```

### Rendering sections

```bash
# Render full video as one file (sections are metadata only)
manim -qh scene.py FullVideo

# Render each section as a separate file
manim -qh --save_sections scene.py FullVideo
# Produces: Hook.mp4, Problem.mp4, Method.mp4, Results.mp4, Takeaway.mp4
```

### Skip sections during development

```python
# Skip rendering a section (useful for iterating on later sections)
self.next_section("Hook", skip_animations=True)
# ... hook animations are skipped ...

self.next_section("Method", skip_animations=False)
# ... only this section renders ...
```

### When to use sections vs separate scene files

| Approach | When to use |
|----------|-------------|
| `next_section()` in one scene | Chapters share state (mobjects carry over between sections) |
| Separate scene files | Chapters are independent. Enables parallel agent generation. Preferred for multi-scene projects. |

For multi-scene projects, prefer separate files (see `project-organization.md`). Use `next_section()` within a single scene when transitions depend on objects from the previous section (e.g., a pipeline that builds up across chapters).

## Useful CLI Flags Summary

| Flag | Description |
|---|---|
| `-ql` | Low quality (854x480@15fps) |
| `-qm` | Medium quality (1280x720@30fps) |
| `-qh` | High quality (1920x1080@60fps) |
| `-qp` | Production quality (2560x1440@60fps) |
| `-qk` | 4K quality (3840x2160@60fps) |
| `-p` | Preview after render |
| `-s` | Save last frame only (PNG) |
| `-a` | Render all scenes in file |
| `-t` | Transparent background |
| `--format` | Output format: mp4, gif, webm, png |
| `--fps` | Override frame rate |
| `--renderer` | cairo (default) or opengl |
| `-n START,END` | Render only animations START through END |
| `--disable_caching` | Force re-render everything |
| `--write_all` | Write all animations, not just last |

## Caching

Manim caches rendered animations. Force re-render with:

```bash
manim --disable_caching scene.py MyScene
```

Or flush the cache:

```bash
manim --flush_cache scene.py MyScene
```

## Batch Rendering Script

```bash
#!/bin/bash
# render_all.sh
set -euo pipefail

QUALITY="${1:--qh}"

for scene_file in scenes/s*.py; do
    echo "Rendering $scene_file..."
    manim "$QUALITY" --format mp4 --fps 30 "$scene_file"
done

echo "All scenes rendered."
```
