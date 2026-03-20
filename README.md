# 3brown1blue

Generate 3Blue1Brown-style Manim explainer videos from topics or slide decks, or install the Manim skill into your AI coding tool.

## Install the skill (recommended)

The primary use: install 24 rule files, templates, and safe wrappers into your AI tool so it generates production-quality animations.

```bash
pip install 3brown1blue
3brown1blue install
```

Supports: **Claude Code**, **Cursor**, **Windsurf**, **GitHub Copilot**

Then just ask your AI: *"make a video explaining backpropagation"* -- the skill handles layout templates, production rules, visual design principles, and common gotchas automatically.

## Generate from a topic

Two-step pipeline: plans the video first (research, curriculum, scene plans, style contract), shows you the plan for review, then generates Manim code.

```bash
# one-shot with uvx (no permanent install)
uvx '3brown1blue[anthropic]' generate "Fourier transforms" --render

# or with Claude Code (no API key needed)
3brown1blue generate "attention mechanism" -p claude-code --render -q h
```

## Generate from slides

Extract content from a PowerPoint deck, plan a video, and generate Manim code. Auto-detects whether vision extraction is needed for diagram-heavy slides.

```bash
pip install '3brown1blue[slides]'
3brown1blue from-slides lecture.pptx -p claude-code --render
```

The pipeline: extract text + speaker notes + images -> plan with scene templates -> review/edit the plan -> generate Manim code -> render.

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
- **3 templates**: equation explainer, paper explainer, shared style.py
- **Safe wrappers**: drop-in replacements for crash-prone Manim APIs
- **12 gotchas**: documented crashes and silent bugs with fixes
- **22 visual patterns**: extracted from 422 frames of 3Blue1Brown videos

## CLI reference

```
3brown1blue generate TOPIC [OPTIONS]
3brown1blue from-slides DECK [OPTIONS]
3brown1blue install [--platform] [--force]
3brown1blue uninstall [--platform]
3brown1blue update [--platform]
3brown1blue status
```

Common options for generate/from-slides:
```
  --provider  -p   claude-code | anthropic | openai | google | groq | mistral
  --model     -m   generation model (provider default if omitted)
  --plan-model     planning model (same as --model if omitted)
  --api-key   -k   API key (or set the provider env var)
  --output    -o   output file  [default: scene.py]
  --render         run manim after generation
  --quality   -q   l=fast | m=medium | h=1080p | k=4K  [default: l]
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
