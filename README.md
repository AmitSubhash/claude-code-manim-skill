<p align="center">
  <img src="assets/header.gif" alt="3brown1blue banner" width="800">
</p>

# 3brown1blue

Generate 3Blue1Brown-style Manim explainer videos from topics or slide decks, or install the Manim skill into your AI coding tool.

## What's new in v0.2.5

**Audience-aware generation** -- videos now adapt to who's watching:

```bash
3brown1blue generate "attention mechanism" -a graduate -d machine-learning -p claude-code
3brown1blue generate "CRISPR" -a high-school -d biology -p anthropic --render
3brown1blue from-slides lecture.pptx -a undergrad -d physics -p claude-code
```

- `--audience` / `-a`: **high-school**, **undergrad** (default), **graduate**, **industry** -- each level has its own curriculum structure, pacing, vocabulary, and annotation depth
- `--domain` / `-d`: **machine-learning**, **mathematics**, **physics**, **biology**, **security**, **neuroscience**, **algorithms** (or `auto`) -- domain-specific visual patterns, color semantics, and notation conventions
- **Misconception engine**: the planner now identifies what the audience wrongly believes and structures the video to show the wrong intuition first, then correct it (based on Muller's research, effect size 0.8)
- **Narration scripts**: every plan now includes a per-scene narration script matched to audience vocabulary
- **18 production rules** (was 10): new rules for text centering, container label safety, dim-vs-fadeout, transition density, arrow spacing, chart legend placement
- **35 domain-specific visual patterns** (5 per domain) extending the 22 general patterns
- **Automated audit tools**: `audit_video.sh` extracts frames and prints a visual checklist; `concat_scenes.sh` joins scenes with ffmpeg

## Install the skill (recommended)

The primary use: install rule files, templates, and safe wrappers into your AI tool so it generates production-quality animations.

```bash
pip install 3brown1blue
3brown1blue install
```

Supports: **Claude Code**, **Cursor**, **Windsurf**, **GitHub Copilot**

Then just ask your AI: *"make a video explaining backpropagation"* -- the skill handles layout templates, production rules, visual design principles, and common gotchas automatically.

## Generate from a topic

Two-step pipeline: plans the video first (research, misconception analysis, curriculum, scene plans, narration script, style contract), shows you the plan for review, then generates Manim code.

```bash
# one-shot with uvx (no permanent install)
uvx '3brown1blue[anthropic]' generate "Fourier transforms" --render

# with Claude Code (no API key needed)
3brown1blue generate "attention mechanism" -p claude-code --render -q h

# audience + domain aware
3brown1blue generate "neural ODEs" -a graduate -d machine-learning -p claude-code
3brown1blue generate "sorting algorithms" -a high-school -d algorithms -p anthropic --render

# save the reviewed plan so you can generate voiceover later
3brown1blue generate "attention mechanism" -p claude-code --plan-output attention_plan.md
```

## Generate from slides

Extract content from a PowerPoint deck, plan a video, and generate Manim code. Auto-detects whether vision extraction is needed for diagram-heavy slides.

```bash
pip install '3brown1blue[slides]'
3brown1blue from-slides lecture.pptx -p claude-code --render
3brown1blue from-slides research_talk.pptx -a graduate -d neuroscience -p anthropic
```

## Generate voiceover with VibeVoice-Realtime

Experimental single-speaker narration workflow using Microsoft's open-source
VibeVoice-Realtime model. This is the supported path for narration right now;
the older multi-speaker VibeVoice-TTS release was removed upstream.

Install VibeVoice separately in the same environment:

```bash
git clone https://github.com/microsoft/VibeVoice.git
cd VibeVoice
pip install -e .[streamingtts]
```

Then save a video plan and turn its `## Narration Script` into per-scene WAVs:

```bash
3brown1blue generate "backpropagation" -p claude-code --plan-output backprop_plan.md

3brown1blue voiceover backprop_plan.md \
  --voices-dir /path/to/VibeVoice/demo/voices/streaming_model \
  --speaker-name Carter \
  --output-dir backprop_voice
```

You can also point `voiceover` at a project directory. It will first look for
`# NARRATION:` comments in `scene_*.py`, then fall back to `narration.md`,
`plan.md`, `video_plan.md`, or `storyboard.md`.

## Audience levels

| Level | Assumes | Curriculum | Scenes | Style |
|-------|---------|-----------|--------|-------|
| **high-school** | Algebra, curiosity | Concrete example first, generalize, real world | 5-7 | Metaphor-heavy, generous pacing |
| **undergrad** | Calculus, linear algebra, intro field | Hook, background, method, results, takeaway | 8-10 | Balance of intuition and formalism |
| **graduate** | Deep field knowledge | Skip background, start with contribution | 10-12 | Dense, fast-paced, more equations |
| **industry** | Practical focus | Problem, solution, how to adopt | 6-8 | Applied, demo-oriented, benchmarks |

## Domain support

Each domain includes a visual vocabulary, preferred layout templates, 5 domain-specific patterns, color semantics, and notation conventions.

| Domain | Key patterns |
|--------|-------------|
| **machine-learning** | Layer-by-layer build, forward/backward overlay, loss landscape, attention heatmap, training dynamics |
| **mathematics** | Geometry-first reveal, dim-and-reveal decomposition, continuous morphing, proof step counter |
| **physics** | Phenomenon-first intro, free body diagram build, field line animation, conservation partition |
| **biology** | Scale transition zoom, pathway state animation, structure-function annotation |
| **security** | Threat model setup, exploit chain, expected-vs-actual, memory layout diagram |
| **neuroscience** | Anatomy-first grounding, multi-channel signal trace, imaging modality setup, connectivity matrix |
| **algorithms** | Concrete data execution, pseudocode cursor, complexity growth, recursion tree build |

## Supported providers

| Provider | Install extra | Env var | Notes |
|----------|--------------|---------|-------|
| Claude Code | none | none | Uses `claude -p`, no API key needed |
| Anthropic | `[anthropic]` | `ANTHROPIC_API_KEY` | |
| OpenAI | `[openai]` | `OPENAI_API_KEY` | |
| Google Gemini | `[openai]` | `GOOGLE_API_KEY` | OpenAI-compatible API |
| Groq | `[openai]` | `GROQ_API_KEY` | OpenAI-compatible API |
| Mistral | `[openai]` | `MISTRAL_API_KEY` | OpenAI-compatible API |

## What the skill includes

- **24 rule files**: animations, equations, visual design, production quality, 3D, graphs, updaters, troubleshooting, and more
- **4 audience profiles**: high-school, undergrad, graduate, industry -- each with curriculum, pacing, and vocabulary rules
- **7 domain rule sets**: ML, math, physics, bio, security, neuro, algorithms -- with 35 domain-specific visual patterns
- **3 templates**: equation explainer, paper explainer, shared style.py with `safe_multiline()`, `pipeline_arrow()`, `bottom_note()`
- **Safe wrappers**: drop-in replacements for crash-prone Manim APIs
- **18 production rules**: layout, text centering, container safety, lifecycle, transitions, arrow spacing, chart legends
- **Misconception engine**: plans videos to show wrong intuition before correcting it
- **Narration scripts**: per-scene scripts generated alongside the video plan
- **Audit tools**: `audit_video.sh` for frame extraction + checklist, `concat_scenes.sh` for joining scenes

## CLI reference

```
3brown1blue generate TOPIC [OPTIONS]
3brown1blue from-slides DECK [OPTIONS]
3brown1blue voiceover SOURCE [OPTIONS]
3brown1blue install [--platform] [--force]
3brown1blue uninstall [--platform]
3brown1blue update [--platform]
3brown1blue status
```

Common options for generate/from-slides:
```
  --provider  -p   claude-code | anthropic | openai | google | groq | mistral
  --audience  -a   high-school | undergrad | graduate | industry  [default: undergrad]
  --domain    -d   auto | machine-learning | mathematics | physics | biology |
                   security | neuroscience | algorithms  [default: auto]
  --model     -m   generation model (provider default if omitted)
  --plan-model     planning model (same as --model if omitted)
  --api-key   -k   API key (or set the provider env var)
  --output    -o   output file  [default: scene.py]
  --plan-output    optional markdown file to save the reviewed plan
  --render         run manim after generation
  --quality   -q   l=fast | m=medium | h=1080p | k=4K  [default: l]
```

Voiceover options:
```
  --project-dir -d   project directory for scene-name matching
  --model-path       VibeVoice-Realtime model id/path
  --speaker-name     voice preset name  [default: Carter]
  --voice-prompt     explicit .pt voice prompt file
  --voices-dir       directory containing VibeVoice voice prompts
  --output-dir -o    output directory for wav files
  --device           auto | cuda | mps | cpu  [default: auto]
  --cfg-scale        guidance scale  [default: 1.5]
  --ddpm-steps       diffusion steps  [default: 5]
  --list-voices      list available prompts and exit
```

## Showcase

See generated videos: [3brown1blue-showcase](https://github.com/AmitSubhash/3brown1blue-showcase)

## Prerequisites

```bash
pip install manim
# macOS: brew install mactex
# Linux: apt install texlive-full
# Windows: install MiKTeX
```

## License

MIT
