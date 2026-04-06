---
name: Voiceover and Narration
description: TTS backend selection, teaching-style text rewrites, beat-aware narration sync, manim-voiceover plugin, and CLI workflow for narrated videos
tags: [manim, voiceover, narration, tts, kokoro, audio, sync]
---

# Voiceover and Narration

Prerequisites: you have read `paper-explainer.md` (narration script gate, pacing) and `animation-design-thinking.md` (narration sync strategy). This file teaches you how to generate and integrate speech audio with your Manim scenes.

## 1. Backend Options

### Kokoro-82M (Recommended)

82M parameters. Apache 2.0 license. Sub-second generation on Apple Silicon. 54 voices plus voice mixing.

| Property | Value |
|----------|-------|
| Best voice | `af_heart` (Grade A, warm teaching tone) |
| Runner-up | `af_heart` + `af_bella` mix (warmth + personality) |
| Speed | 1.0 for natural pacing, 1.1 for tighter sync |
| Generation time | 0.5-0.8s per paragraph (CPU) |
| Apple Silicon | Native MPS, MLX, and ONNX runtimes |
| Reproducibility | Deterministic output |

**Install in a dedicated venv (requires Python 3.11):**
```bash
python3.11 -m venv .tts311
.tts311/bin/pip install 'kokoro>=0.9.4' 'misaki[en]' soundfile
```

**Minimal generation example:**
```python
from kokoro import KPipeline
import soundfile as sf

pipeline = KPipeline(lang_code="a")  # "a" = American English
audio, sr = pipeline(
    "Here is the rule... score, softmax, weighted sum.",
    voice="af_heart",
    speed=1.0,
)
sf.write("narration.wav", audio, sr)
```

**Voice mixing (blend two voices):**
```python
import torch

v1 = pipeline.load_voice("af_heart")
v2 = pipeline.load_voice("af_bella")
blended = torch.lerp(v1, v2, 0.4)  # 60% heart, 40% bella
audio, sr = pipeline("Your text here.", voice=blended, speed=1.0)
```

### VibeVoice-Realtime-0.5B

500M parameters. MIT license. More expressive prosody but 15x slower than Kokoro.

| Property | Value |
|----------|-------|
| Best male voice | Carter (warm, natural) |
| Best female voice | Emma (warm, clear) |
| cfg_scale | 1.5 (default). Never below 1.0 (degrades quality) |
| Generation time | 7-10s per paragraph |
| Apple Silicon | MPS (float32 only, no float16) |
| No speed control | Duration is content-dependent |

Use VibeVoice when you need more emotional expressiveness or multilingual narration than Kokoro provides.

### Chatterbox

500M parameters. MIT license. Voice cloning from a 10-second audio sample. CPU-only on Mac (MPS broken due to Float64 errors).

| Property | Value |
|----------|-------|
| Best config | Default voice, exaggeration=0.5 |
| Generation time | 17-35s per paragraph (CPU) |
| Voice cloning | Provide any 10s WAV as reference |
| Apple Silicon | CPU only (MPS broken as of 2026-03) |

Use Chatterbox when you want to clone a specific human voice. Requires a new bridge script (not yet integrated into the 3brown1blue CLI).

## 2. Teaching-Style Text Rewrites

**Key finding from A/B testing:** text rewriting matters MORE than backend choice. The same voice sounds noticeably better with teaching-style text across all backends tested.

### Rewrite rules

**Use ellipses for thinking pauses.** The TTS model inserts natural breathing pauses at ellipses, creating the cadence of someone thinking through a concept.
```
# Before (flat delivery)
"The attention mechanism computes a score, applies softmax, and produces a weighted sum."

# After (teaching delivery)
"Here is the rule... score, softmax, weighted sum."
```

**Use rhetorical questions.** Questions add conversational inflection that makes narration sound less robotic.
```
"That shortcut? That is the core idea."
"Why does this work? Because the query and key live in the same space."
```

**Quote key terms for emphasis.** Wrapping a term in quotes signals the TTS model to give it slight emphasis.
```
"The word 'it' can point straight back to 'animal.'"
"This 'residual connection' is what makes deep networks trainable."
```

**Break into 1-2 sentence beats.** Each beat should align to one animation group. Long paragraphs produce monotone delivery.
```
# Before (one long block)
"The encoder processes the input sequence through six identical layers, each containing
a multi-head self-attention mechanism followed by a position-wise feedforward network,
with residual connections and layer normalization applied after each sub-layer."

# After (beat-aligned)
"Six layers. Each one identical."
"First... multi-head self-attention. The sequence talks to itself."
"Then a feedforward network. Each position, independently."
"And around each step? A residual connection plus layer norm."
```

## 3. Beat-Aware Narration

### Scene comment format

Mark voiceover beats in your scene files using `# NARRATION:` comments. Each beat corresponds to a visual phase (one or more animation calls).

```python
class AttentionScene(Scene):
    def construct(self) -> None:
        # NARRATION: "Every word in the input gets three vectors... query, key, and value."
        q_arrow = Arrow(LEFT, RIGHT, color=RED)
        k_arrow = Arrow(LEFT, RIGHT, color=BLUE)
        v_arrow = Arrow(LEFT, RIGHT, color=GREEN)
        labels = VGroup(
            Text("Query", font_size=20, color=RED),
            Text("Key", font_size=20, color=BLUE),
            Text("Value", font_size=20, color=GREEN),
        )
        self.play(
            LaggedStart(
                GrowArrow(q_arrow), GrowArrow(k_arrow), GrowArrow(v_arrow),
                lag_ratio=0.3,
            ),
            run_time=2.0,
        )
        self.wait(1.0)

        # NARRATION: "The query asks... what should I pay attention to?"
        highlight = SurroundingRectangle(q_arrow, color=YELLOW)
        self.play(Create(highlight), run_time=0.8)
        self.wait(1.5)
```

### Duration calculation

Target duration for each beat is calculated from the animation calls:
- `self.play(..., run_time=X)` contributes X seconds
- `self.wait(Y)` contributes Y seconds
- Sum these for the beat's target duration

The CLI generates audio for each beat, then pads with silence to match the target duration. If the audio is longer than the target, the compose step can either truncate or stretch the video timing (controlled by `--audio-fit`).

### Beat alignment strategies

| Strategy | Flag | When to use |
|----------|------|-------------|
| `pad` | `--audio-fit pad` | Audio shorter than animation. Adds trailing silence. |
| `truncate` | `--audio-fit truncate` | Audio longer than animation. Clips audio end. |
| `hybrid` | `--audio-fit hybrid` | Pads short audio, adjusts wait() for long audio. Recommended. |

## 4. manim-voiceover Plugin (Alternative)

The `manim-voiceover` package provides a different integration path with word-level sync via bookmarks.

**Install:**
```bash
pip install manim-voiceover
# Plus a TTS backend:
pip install "manim-voiceover[elevenlabs]"
pip install "manim-voiceover[azure]"
pip install "manim-voiceover[gtts]"   # free, lower quality
```

**Usage pattern:**
```python
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.elevenlabs import ElevenLabsService

class NarratedScene(VoiceoverScene):
    def construct(self) -> None:
        self.set_speech_service(ElevenLabsService(voice_name="Adam"))

        with self.voiceover(
            text='Every word gets <bookmark mark="A"/>three vectors.'
        ) as tracker:
            self.wait_until_bookmark("A")
            arrows = VGroup(
                Arrow(LEFT, RIGHT, color=RED),
                Arrow(LEFT, RIGHT, color=BLUE),
                Arrow(LEFT, RIGHT, color=GREEN),
            ).arrange(DOWN)
            self.play(
                LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.3),
                run_time=tracker.duration,
            )
```

Key features:
- `tracker.duration` gives the total audio length for timing animations
- `<bookmark mark="X"/>` in text creates sync points
- `self.wait_until_bookmark("X")` pauses until that word is spoken
- Audio is cached after first generation (re-renders are fast)

Use the manim-voiceover plugin when you need word-level sync precision or when using cloud TTS backends (ElevenLabs, Azure). Use the 3brown1blue CLI workflow (Section 5) when using local backends (Kokoro, VibeVoice) with beat-level sync.

## 5. CLI Workflow

### Generate voiceover audio

```bash
# Generate with Kokoro (recommended)
3brown1blue voiceover <project_dir> \
  --backend kokoro \
  --speaker-name af_heart \
  --speech-speed 1.0 \
  --source-mode scene-comments \
  --output-dir voiceover_audio

# Generate with VibeVoice
3brown1blue voiceover <project_dir> \
  --backend vibevoice \
  --speaker-name Carter \
  --source-mode scene-comments \
  --output-dir voiceover_audio

# Use a custom Kokoro venv (if .tts311 is not on PATH)
3brown1blue voiceover <project_dir> \
  --backend kokoro \
  --kokoro-python .tts311/bin/python \
  --speaker-name af_heart \
  --speech-speed 1.0 \
  --source-mode scene-comments
```

### Compose narrated video

```bash
# Compose with beat-aware audio sync
3brown1blue compose-voiceover <project_dir> \
  --audio-dir voiceover_audio \
  --quality l \
  --audio-fit hybrid

# Higher quality render
3brown1blue compose-voiceover <project_dir> \
  --audio-dir voiceover_audio \
  --quality h \
  --audio-fit hybrid
```

### End-to-end recommended workflow

```bash
# 1. Write scenes with # NARRATION: comments (teaching style text)

# 2. Generate audio
3brown1blue voiceover videos/my_project \
  --backend kokoro --speaker-name af_heart \
  --speech-speed 1.0 --source-mode scene-comments

# 3. Preview at low quality
3brown1blue compose-voiceover videos/my_project \
  --audio-dir voiceover_audio --quality l --audio-fit hybrid

# 4. Watch the preview, adjust narration text or animation timing

# 5. Final render at high quality
3brown1blue compose-voiceover videos/my_project \
  --audio-dir voiceover_audio --quality h --audio-fit hybrid
```

### Source modes

| Mode | Flag | Reads narration from |
|------|------|---------------------|
| Scene comments | `--source-mode scene-comments` | `# NARRATION:` comments in .py files |
| Script file | `--source-mode script` | `narration_script.md` in project dir |
| Beat file | `--source-mode beats` | `beats.json` with per-beat text and timing |
