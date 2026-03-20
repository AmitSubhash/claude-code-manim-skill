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
