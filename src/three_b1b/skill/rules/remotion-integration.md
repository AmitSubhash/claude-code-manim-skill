---
name: Remotion Integration
description: Pipeline for combining Manim mathematical animations with Remotion video composition
tags: [manim, remotion, video, pipeline, react, composition]
---

# Manim + Remotion Integration Pipeline

## Overview

**Pipeline**: Manim renders math/diagram clips -> Remotion composes the final video with titles, transitions, captions, and branding.

## When to Use Manim vs Remotion

| Manim | Remotion |
|---|---|
| LaTeX equations and derivations | Title cards and lower thirds |
| Mathematical diagrams | Text overlays and captions |
| 3D surface plots | Transitions between clips |
| Graph plotting and data visualization | Branding, logos, watermarks |
| Geometric constructions | Web content (HTML/CSS-based visuals) |
| Linear algebra transformations | Progress bars and chapter markers |
| Physics simulations | Background music sync |
| Animated proofs | Thumbnail generation |

## Export Settings for Manim Clips

### Opaque clips (most common)

```bash
manim -qh --fps 30 --format mp4 scene.py SceneName
```

### Transparent overlay clips

```bash
# webm supports alpha channel; mp4 does NOT
manim -qh --fps 30 --format webm -t scene.py SceneName
```

### Ensure resolution and FPS match Remotion

Both Manim and Remotion must use identical settings:
- Resolution: 1920x1080
- Frame rate: 30fps (or both at 60fps)

```ini
# manim.cfg
[CLI]
quality = high_quality
fps = 30
```

## File Naming Convention

Name exported clips consistently for easy reference in Remotion:

```
clips/
  clip_hook_01.mp4
  clip_problem_02.mp4
  clip_equation_03.mp4
  clip_equation_04.webm     # transparent overlay
  clip_pipeline_05.mp4
  clip_results_06.mp4
  clip_conclusion_07.mp4
```

Pattern: `clip_{scene_name}_{index}.{mp4|webm}`

### Export script

```bash
#!/bin/bash
# export_clips.sh - render and copy to Remotion public directory
set -euo pipefail

REMOTION_PUBLIC="./remotion-project/public/clips"
mkdir -p "$REMOTION_PUBLIC"

# Render
manim -qh --fps 30 --format mp4 scenes/s01_intro.py S01Intro
manim -qh --fps 30 --format mp4 scenes/s02_method.py S02Method
manim -qh --fps 30 --format webm -t scenes/s03_overlay.py S03Overlay

# Copy to Remotion
cp media/videos/s01_intro/1080p60/S01Intro.mp4 "$REMOTION_PUBLIC/clip_intro_01.mp4"
cp media/videos/s02_method/1080p60/S02Method.mp4 "$REMOTION_PUBLIC/clip_method_02.mp4"
cp media/videos/s03_overlay/1080p60/S03Overlay.webm "$REMOTION_PUBLIC/clip_overlay_03.webm"

echo "Clips exported to $REMOTION_PUBLIC"
```

## Remotion Import Pattern

### Using a Manim clip in Remotion

```tsx
import { Video, staticFile } from "remotion";

export const MathClip: React.FC = () => (
  <Video src={staticFile("clips/clip_equation_03.mp4")} />
);
```

### Transparent overlay

```tsx
import { Video, staticFile, AbsoluteFill } from "remotion";

export const OverlayClip: React.FC = () => (
  <AbsoluteFill>
    {/* Background content (e.g., a gradient or image) */}
    <AbsoluteFill style={{ backgroundColor: "#1a1a2e" }} />

    {/* Transparent Manim clip on top */}
    <Video
      src={staticFile("clips/clip_overlay_03.webm")}
      style={{ width: "100%", height: "100%" }}
    />
  </AbsoluteFill>
);
```

## Duration Sync

Use `getVideoMetadata()` to match clip length dynamically:

```tsx
import { getVideoMetadata } from "@remotion/media-utils";
import { staticFile, useEffect, useState } from "remotion";

export const useManimClipDuration = (clipName: string) => {
  const [duration, setDuration] = useState<number | null>(null);

  useEffect(() => {
    getVideoMetadata(staticFile(`clips/${clipName}`)).then((metadata) => {
      setDuration(metadata.durationInSeconds);
    });
  }, [clipName]);

  return duration;
};
```

### In composition registration

```tsx
import { Composition } from "remotion";

const fps = 30;

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="PaperExplainer"
      component={PaperExplainer}
      durationInFrames={fps * 300}  // 5 minutes
      fps={fps}
      width={1920}
      height={1080}
    />
  </>
);
```

## Composition Structure

A typical paper explainer composition:

```tsx
import {
  Sequence,
  Video,
  staticFile,
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
} from "remotion";

const fps = 30;

export const PaperExplainer: React.FC = () => {
  return (
    <AbsoluteFill>
      {/* Title card (Remotion) */}
      <Sequence from={0} durationInFrames={fps * 5}>
        <TitleCard
          title="Paper Title"
          authors="Author et al., 2025"
        />
      </Sequence>

      {/* Hook clip (Manim) */}
      <Sequence from={fps * 5} durationInFrames={fps * 10}>
        <Video src={staticFile("clips/clip_hook_01.mp4")} />
      </Sequence>

      {/* Problem setup (Manim) */}
      <Sequence from={fps * 15} durationInFrames={fps * 30}>
        <Video src={staticFile("clips/clip_problem_02.mp4")} />
      </Sequence>

      {/* Equation walkthrough with caption overlay */}
      <Sequence from={fps * 45} durationInFrames={fps * 60}>
        <AbsoluteFill>
          <Video src={staticFile("clips/clip_equation_03.mp4")} />
          <CaptionOverlay text="The governing equation..." />
        </AbsoluteFill>
      </Sequence>

      {/* Results (Manim) */}
      <Sequence from={fps * 105} durationInFrames={fps * 60}>
        <Video src={staticFile("clips/clip_results_06.mp4")} />
      </Sequence>

      {/* End card (Remotion) */}
      <Sequence from={fps * 165} durationInFrames={fps * 10}>
        <EndCard />
      </Sequence>
    </AbsoluteFill>
  );
};
```

## Project Structure for Combined Manim + Remotion

```
paper-explainer/
  manim/                    # Manim project
    scenes/
      s01_hook.py
      s02_problem.py
      s03_equations.py
      s04_results.py
    utils/
      style.py
      components.py
    manim.cfg
    render_all.sh
    export_clips.sh         # copies to remotion/public/clips

  remotion/                 # Remotion project
    public/
      clips/                # Manim output goes here
        clip_hook_01.mp4
        clip_problem_02.mp4
        clip_equations_03.mp4
        clip_results_04.mp4
      images/               # Static images
    src/
      Root.tsx
      PaperExplainer.tsx
      components/
        TitleCard.tsx
        CaptionOverlay.tsx
        EndCard.tsx
        TransitionWipe.tsx
    package.json
    remotion.config.ts

  Makefile                  # Orchestrate both
```

## Makefile for Orchestration

```makefile
.PHONY: manim remotion preview render clean

manim:
	cd manim && bash render_all.sh -qh 30 mp4
	cd manim && bash export_clips.sh

remotion-preview:
	cd remotion && npx remotion preview

remotion-render:
	cd remotion && npx remotion render PaperExplainer out/final.mp4

preview: manim remotion-preview

render: manim remotion-render

clean:
	rm -rf manim/media remotion/public/clips/*.mp4 remotion/public/clips/*.webm remotion/out
```

## Tips

1. **Render Manim clips first**, then compose in Remotion. Never render both simultaneously.
2. **Keep Manim scenes focused**: one concept per clip. Let Remotion handle sequencing.
3. **Use transparent webm** only for overlays (equation annotations on top of other content). Default to opaque mp4.
4. **Match frame rates exactly**: a mismatch causes stuttering or frame skipping.
5. **Version your clips**: include a version suffix (`clip_equation_03_v2.mp4`) during iteration.
6. **Test with low quality** Manim renders (`-ql`) during composition, switch to high quality for final render.
