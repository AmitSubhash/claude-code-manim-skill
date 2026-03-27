# TRIBE v2: A Foundation Model for In-Silico Neuroscience

3Blue1Brown-style explainer video for Meta FAIR's TRIBE v2 paper.

## Paper

**A Foundation Model of Vision, Audition, and Language for In-Silico Neuroscience**
d'Ascoli, Rapin, Benchetrit, Brooks, Begany, Raugel, Banville, King -- Meta FAIR, 2026

- Paper: https://ai.meta.com/research/publications/a-foundation-model-of-vision-audition-and-language-for-in-silico-neuroscience/
- Code: https://github.com/facebookresearch/tribev2
- Weights: https://huggingface.co/facebook/tribev2
- Demo: https://aidemos.atmeta.com/tribev2/

## Video Structure

12 scenes, ~5 min animation time (designed for ~15 min with narration).
Graduate audience, neuroscience domain patterns.

| # | Scene | Duration | Template | Content |
|---|-------|----------|----------|---------|
| 1 | Hook | 22s | FULL_CENTER | Brain regions light up: "Predicted, Not Measured" |
| 2 | Fragmentation | 21s | GRID_CARDS | Vision/Auditory/Language lab silos |
| 3 | Encoding Basics | 19s | DUAL_PANEL | Traditional linear vs multimodal "???" |
| 4 | Frozen Backbones | 16s | BUILD_UP | V-JEPA 2, Wav2Vec-BERT, LLaMA 3.2 |
| 5 | Integration Transformer | 27s | TOP_PERSISTENT | 8-layer fusion + modality dropout |
| 6 | Brain Mapping | 28s | TOP_PERSISTENT | Low-rank bottleneck, 700+ subject heads |
| 7 | Training Scale | 19s | DUAL_PANEL | v1 (4 subj) vs v2 (700+ subj) |
| 8 | Results | 23s | CHART_FOCUS | Algonauts 1st place + noise ceiling |
| 9 | Modality Maps | 31s | FULL_CENTER | Brain surface by dominant modality |
| 10 | In-Silico | 30s | BUILD_UP | Virtual experiments, known findings |
| 11 | Ablations | 27s | CHART_FOCUS | Modality + architecture ablation charts |
| 12 | Limitations | 24s | BUILD_UP | Limitations, open questions, citation |

## Render

```bash
# Prerequisites
pip install manim

# Single scene (preview)
manim -pql scene_01_hook.py HookScene

# All scenes at 1080p
for f in scene_*.py; do manim -qh "$f"; done

# Concatenate final video
ffmpeg -f concat -safe 0 -i <(
  for f in scene_*.py; do
    name=$(basename "$f" .py)
    class=$(python -c "import ast; t=ast.parse(open('$f').read()); print([n.name for n in ast.walk(t) if isinstance(n, ast.ClassDef)][0])")
    echo "file 'media/videos/${name}/1080p60/${class}.mp4'"
  done
) -c copy tribev2_full.mp4
```

## Project Structure

```
videos/tribev2/
  research.md              # Paper analysis, architecture, results
  curriculum.md            # 4-act structure, audience profile, misconceptions
  storyboard.md            # 12 scene plans with templates and data
  utils/
    style.py               # Semantic colors, layout constants, helpers
  scene_01_hook.py         # through scene_12_limitations.py
  tribev2_full.mp4         # Final concatenated video (after render)
```

## Color System

| Color | Hex | Semantic |
|-------|-----|----------|
| VIDEO_BLUE | #4A90D9 | Video modality / V-JEPA 2 |
| AUDIO_GREEN | #2ECC71 | Audio modality / Wav2Vec-BERT |
| TEXT_ORANGE | #E67E22 | Text modality / LLaMA |
| BRAIN_PURPLE | #9B59B6 | Brain cortex / neural activity |
| TRANSFORM_TEAL | #1ABC9C | Transformer / integration |
| RESULT_GOLD | #F1C40F | Results / novel contribution |
| SUBJECT_PINK | #E91E63 | Subject-specific components |
| BASELINE_GRAY | #7F8C8D | Baselines / prior work |
| DANGER_RED | #C0392B | Limitations / failures |

## Key Concepts Covered

- **TRIBE** = TRImodal Brain Encoder
- Three frozen foundation models (V-JEPA 2, Wav2Vec-BERT 2.0, LLaMA 3.2-3B) extract features at 2 Hz
- 8-layer trainable transformer fuses modalities with modality dropout (p=0.3)
- Subject-conditional brain mapping to ~20,484 fsaverage5 cortical vertices
- Won Algonauts 2025 (1st of 263 teams), 54% noise ceiling
- Modality-specific brain topography: video=occipital, audio=temporal, text=prefrontal
- In-silico neuroscience: recover tonotopy, retinotopy, language lateralization
- Scale: 700+ subjects, 1000+ hours fMRI, 70x resolution increase over v1
