# TRIBE v2: A Foundation Model of Vision, Audition, and Language for In-Silico Neuroscience

## Paper Metadata
- **Title:** A Foundation Model of Vision, Audition, and Language for In-Silico Neuroscience
- **Authors:** Stephane d'Ascoli, Jeremy Rapin, Yohann Benchetrit, Teon Brooks, Katelyn Begany, Josephine Raugel, Hubert Jacob Banville, Jean-Remi King
- **Affiliation:** Meta FAIR (Fundamental AI Research), Brain & AI team
- **Date:** March 26, 2026
- **License:** CC-BY-NC-4.0
- **Code:** https://github.com/facebookresearch/tribev2
- **Weights:** https://huggingface.co/facebook/tribev2
- **Demo:** https://aidemos.atmeta.com/tribev2/
- **TRIBE v1:** arXiv 2507.22229, ICLR 2026 (won 1st at Algonauts 2025, 263 teams)

## Acronym
TRIBE = TRImodal Brain Encoder

## Core Problem
Neuroscience is fragmented: each lab studies one modality (vision OR hearing OR language), one task, one brain region. Traditional encoding models use linear regression (ridge) from one modality to one region. This cannot capture:
- Nonlinear cross-modal interactions
- Shared representations across subjects
- Fine-grained spatial topography of multisensory integration

## Key Insight
Combine three SOTA frozen foundation models (one per modality) with a trainable multimodal transformer to predict vertex-level fMRI BOLD responses across the entire cortex. Scale from 4 subjects to 700+.

## Architecture (3 Stages)

### Stage 1: Multimodal Feature Encoding (Frozen)
| Modality | Model | Params | Dim | Details |
|----------|-------|--------|-----|---------|
| Text | LLaMA 3.2-3B | 3B | 2,048 | Context: last 1,024 words, causal. Layers at [0, 0.2, 0.4, 0.6, 0.8, 1.0] |
| Audio | Wav2Vec-BERT 2.0 | 580M | 1,024 | 60s chunks, 50Hz -> 2Hz. Bidirectional. Layers: [0.75, 1.0] |
| Video | V-JEPA 2 (ViT-Giant) | ~1B | 1,280 | 64-frame window (4s lookback), 2Hz. Causal. Layers: [0.75, 1.0] |

All resampled to shared 2 Hz timeline matching fMRI dynamics.

### Stage 2: Multimodal Integration (Trainable Transformer)
- Per-modality projector: LayerNorm -> Linear -> GELU MLP -> hidden dim
- Concatenation on feature dimension
- Transformer Encoder: 8 layers, hidden dim 1152, 8 heads
- Window: 100 TRs (~150 seconds)
- Learnable positional embeddings, max seq len 1024
- Modality dropout: 0.3 (entire modality zeroed, at least one remains)
- Subject dropout: 0.1
- Temporal dropout: zeros random positions
- Adaptive average pooling -> n_output timesteps
- Optional temporal smoothing via depthwise Conv1d (kernel=9)

### Stage 3: Brain Mapping (Subject-Conditional Head)
- Low-rank bottleneck: hidden (1152) -> low_rank_head (2048)
- Subject-specific linear layer -> brain output
- Target: fsaverage5 cortical mesh, ~20,484 vertices (10,242/hemisphere)
- Output shape: (batch, n_vertices, n_timesteps)

## Key Design Decisions
- No explicit HRF modeling (transformer learns it implicitly)
- Frozen feature extractors (no backprop through LLaMA/V-JEPA2/Wav2Vec)
- Modality dropout enables graceful degradation for missing modalities
- Subject-agnostic core; only final head is subject-specific

## Training Details
- **Datasets:** Algonauts/Courtois NeuroMod (4 subj, TV), Lahner 2024 BOLD Moments (10 subj, clips), Lebel 2023 (8 subj, audiobooks), Wen 2017 (video segments)
- **Total:** 700+ subjects, 1000+ hours fMRI
- **Optimizer:** Adam, lr=1e-4, OneCycleLR (cosine annealing, pct_start=0.1)
- **Batch size:** 8, max epochs 15
- **Loss:** MSE (reduction='none', then averaged)
- **Preprocessing:** fMRIPrep -> fsaverage5 cortical surface

## Key Results

### Algonauts 2025 (v1)
| Rank | Team | Mean Pearson |
|------|------|-------------|
| **1** | **TRIBE** | **0.2146** |
| 2 | NCG | 0.2096 |
| 3 | SDA | 0.2094 |

Normalized Pearson: 0.54 +/- 0.1 (54% of explainable variance)

### v2 Improvements
- 2-3x improvement over previous methods
- 70-fold increase in spatial resolution (~20k vertices vs ~1k parcels)
- Zero-shot generalization to unseen subjects, languages, tasks

### Unimodal vs Multimodal Ablation
| Config | Score |
|--------|-------|
| Text only | 0.22 |
| Audio only | 0.24 |
| Video only | 0.25 |
| Text + Video | 0.30 |
| All three | 0.31 |

### Without transformer: 0.23 (drop of 0.08)
### Separate-subject training: 0.29 (drop of 0.02)

### Modality Localization
- Audio dominant: temporal gyrus (auditory cortex)
- Video dominant: occipital cortex, parietal cortex
- Text dominant: parietal lobe, prefrontal cortex
- Text + Audio bimodal: superior temporal lobe
- Video + Audio bimodal: ventral/dorsal visual cortex
- Text + Video: prefrontal/parietal

### Scaling Laws
- Encoding score increases monotonically with more training sessions (no plateau)
- LLaMA context length (0 to 1024 words): continuous improvement

### Out-of-Distribution Generalization (v1)
- Friends S7 (in-distribution): 0.3195
- Pulp Fiction: 0.2604
- Princess Mononoke: 0.2449
- World of Tomorrow (cartoon): 0.1924
- Planet Earth (wildlife): 0.1886
- Charlie Chaplin (silent B&W): 0.1686

## In-Silico Neuroscience
The model acts as a "digital twin" of human neural processing:
1. Virtual experiments: test hypotheses computationally before running fMRI
2. Recovery of known findings: retinotopy, tonotopy, language lateralization
3. New discoveries: fine-grained topography of multisensory integration
4. Clinical potential: neurological disease diagnosis speed-up

## Key Equations
- Loss: L = (1/N) sum_i (y_pred_i - y_true_i)^2
- Normalized Pearson: rho_norm = rho / rho_max, where rho_max = sqrt(2 / (1 + 1/rho_self))
- Ensemble weighting (v1): w_{m,p} = softmax(score_{m,p} / tau), tau=0.3
- Feature projection: x_mod = LayerNorm(Linear(concat_layers(backbone_mod(input))))

## Limitations
1. fMRI-only (no electrophysiology, MEG, EEG)
2. Limited to perception/comprehension (not behavior, memory, decision-making)
3. Spatial resolution limited by fsaverage5 (~20k vertices)
4. Temporal resolution limited by fMRI TR (~1.5-2.0s)
5. Frozen feature extractors may miss brain-relevant features
6. CC-BY-NC license restricts commercial use
7. Scaling laws show sub-linear, plateauing trends
