# TRIBE v2 Storyboard

## Scene 1: HookScene (~45s)
Template: FULL_CENTER
Content:
- MAIN: Stylized brain surface (ellipse with cortical regions outlined)
- Brain regions light up in sequence (occipital -> temporal -> prefrontal) as if responding to a movie
- Text overlay: "Predicted, Not Measured" with question mark morphing to checkmark
- Counter animates: "700+ subjects, 20,484 vertices, 3 modalities"
- BOTTOM: "TRIBE v2 -- Meta FAIR, 2026"
Visual anchors: Brain outline persists through lighting animation
Cleanup: FadeOut all before Scene 2
Data: 700+ subjects, 20,484 vertices, 54% noise ceiling

## Scene 2: FragmentationScene (~60s)
Template: GRID_CARDS
Content:
- Title: "The Silo Problem in Neuroscience"
- 3 cards in a row representing fragmented approaches:
  - Card 1: "Vision Lab" -- eye icon, V1/V2 labels, single modality arrow
  - Card 2: "Auditory Lab" -- ear icon, A1/STG labels, single modality arrow
  - Card 3: "Language Lab" -- speech icon, Broca/Wernicke labels, single modality arrow
- Each card has a red X for "isolated"
- Then: show a movie scene (car crash) requiring all three simultaneously
- Arrows from all three converge to prefrontal cortex region
- BOTTOM: "Real perception is multimodal -- linear models per modality miss the cross-talk"
Visual anchors: 3 cards
Cleanup: FadeOut all
Data: None (conceptual)

## Scene 3: EncodingBasicsScene (~60s)
Template: DUAL_PANEL
Content:
- Title: "Brain Encoding: Stimulus -> Predicted BOLD"
- LEFT: Traditional encoding
  - Stimulus (movie frame icon) -> feature extractor (single box) -> ridge regression (W matrix) -> predicted BOLD (signal trace)
  - Label: "Linear, single-modality, per-region"
- RIGHT: What we want
  - Three stimulus streams (video + audio + text) -> ??? -> full cortex prediction
  - Question mark box in the middle
  - Label: "Nonlinear, multimodal, cross-subject"
- BOTTOM: "What goes in the ??? box?"
Visual anchors: The ??? box (will be filled in Scene 4-6)
Cleanup: FadeOut all
Equations: y = Wx + b (ridge regression)

## Scene 4: FrozenBackbonesScene (~75s)
Template: BUILD_UP
Content:
- Title: "Stage 1: Three Frozen Feature Extractors"
- Build three parallel columns, one per modality:
  - Column 1: V-JEPA 2 (ViT-Giant, ~1B params)
    - Video frames in -> spatial avg -> 1280-dim at 2Hz
    - Color: VIDEO_BLUE
  - Column 2: Wav2Vec-BERT 2.0 (580M params)
    - Audio waveform in -> 1024-dim at 2Hz
    - Color: AUDIO_GREEN
  - Column 3: LLaMA 3.2-3B (3B params)
    - Word tokens in -> 2048-dim at 2Hz
    - Color: TEXT_ORANGE
- All three outputs converge to a "2 Hz timeline" bar at bottom
- Snowflake icon on each = "frozen" (no gradients)
- BOTTOM: "Misconception: wouldn't a single multimodal model work better?"
Visual anchors: Three columns with frozen indicators
Cleanup: Scale down to header for Scene 5
Equations: None
Data: Params: 1B, 580M, 3B; Dims: 1280, 1024, 2048; Shared: 2Hz

## Scene 5: IntegrationTransformerScene (~75s)
Template: TOP_PERSISTENT_BOTTOM_CONTENT
Content:
- TOP PERSISTENT: Miniaturized Stage 1 from Scene 4
- Subtitle: "Stage 2: Multimodal Fusion Transformer"
- MAIN: Transformer architecture diagram
  - Per-modality projectors (LN -> Linear -> GELU) shown as 3 small boxes
  - Concatenation symbol (||) merging feature dims
  - 8-layer Transformer block (self-attention + FFN)
  - Dim annotations: 1152 hidden, 8 heads
  - Window: 100 TRs (~150s)
- Modality dropout visualization:
  - Show 3 modality streams; randomly zero one out (X over it)
  - "p=0.3, at least one remains"
- BOTTOM: "The transformer learns cross-modal attention AND the hemodynamic response"
Visual anchors: Persistent header, transformer block
Cleanup: Keep header, FadeOut main content
Equations: None explicit (architectural)
Data: 8 layers, 1152 hidden, 8 heads, p_dropout=0.3, window=100 TRs

## Scene 6: BrainMappingScene (~60s)
Template: TOP_PERSISTENT_BOTTOM_CONTENT
Content:
- TOP PERSISTENT: Miniaturized Stages 1+2
- Subtitle: "Stage 3: Subject-Conditional Brain Mapping"
- MAIN: Low-rank bottleneck diagram
  - Transformer output (1152) -> Linear (2048) -> Subject head -> 20,484 vertices
  - Show fsaverage5 mesh as a flattened cortical surface (ellipse with grid)
  - Subject embedding icons: show 3-4 subject icons, each with own final layer
  - Shared trunk highlighted in YELLOW (novel contribution)
- BOTTOM: "Same core model for 700+ subjects -- only the final layer changes"
Visual anchors: Full pipeline now visible in header
Cleanup: FadeOut, transition to results
Equations: h = Linear(transformer_out), y_s = W_s * h (per subject)
Data: 1152 -> 2048 -> 20,484 vertices, 700+ subjects

## Scene 7: TrainingScaleScene (~60s)
Template: DUAL_PANEL
Content:
- Title: "Training at Scale"
- LEFT: "TRIBE v1" (small scale)
  - 4 subjects icon
  - 1 dataset (Courtois NeuroMod)
  - ~80 hrs/subject
  - 1,000 Schaefer parcels
  - Dimmed, smaller
- RIGHT: "TRIBE v2" (massive scale) -- highlighted
  - 700+ subjects icon
  - 4 datasets (NeuroMod, BOLD Moments, Lebel, Wen)
  - 1,000+ total hours
  - 20,484 vertices
  - "70x resolution increase" annotation
- Center: arrow from left to right with "scale" label
- BOTTOM: "MSE loss, Adam optimizer, 15 epochs, 1 GPU"
Visual anchors: Scale comparison
Cleanup: FadeOut all
Data: v1: 4 subj, 1000 parcels; v2: 700+ subj, 20484 vertices, 70x

## Scene 8: ResultsScene (~90s)
Template: CHART_FOCUS
Content:
- Title: "Algonauts 2025: 1st of 263 Teams"
- Phase 1: Competition bar chart
  - Axes: Team (x) vs Mean Pearson rho (y)
  - Bars: TRIBE=0.2146 (gold), NCG=0.2096, SDA=0.2094, others lower
  - TRIBE bar highlighted in ACCENT color
- Phase 2: Noise ceiling visualization
  - Horizontal line at rho_max (noise ceiling)
  - TRIBE bar fills to 54% of ceiling
  - Near-ceiling annotation for auditory/language cortex
- BOTTOM: "Normalized Pearson: 0.54 -- 54% of explainable variance captured"
Visual anchors: Bar chart
Cleanup: FadeOut chart
Equations: rho_norm = rho / rho_max, rho_max = sqrt(2 / (1 + 1/rho_self))
Data: TRIBE=0.2146, NCG=0.2096, SDA=0.2094, normalized=0.54

## Scene 9: ModalityMapsScene (~90s)
Template: FULL_CENTER
Content:
- Title: "Which Modality Predicts Which Region?"
- MAIN: Flattened cortical surface (ellipse) with regions colored by dominant modality
  - Occipital (posterior): VIDEO_BLUE -- "V-JEPA 2 dominates"
  - Temporal (lateral): AUDIO_GREEN -- "Wav2Vec dominates"
  - Prefrontal (anterior): TEXT_ORANGE -- "LLaMA dominates"
  - Parietal (superior): mixed coloring -- "Multimodal integration zone"
- Animation: regions light up one by one as each modality is discussed
- Inset: small bar chart showing multimodal advantage by region
  - Prefrontal: +30% from multimodal
  - Parieto-occipito-temporal: +30%
- BOTTOM: "Multimodal advantage strongest where modalities converge"
Visual anchors: Brain surface
Cleanup: FadeOut all
Data: Audio=temporal, Video=occipital, Text=prefrontal, +30% multimodal advantage

## Scene 10: InSilicoScene (~90s)
Template: BUILD_UP
Content:
- Title: "In-Silico Neuroscience: Virtual Experiments"
- Phase 1: Show the concept
  - Traditional: Human + fMRI scanner + months -> brain maps
  - TRIBE v2: Stimulus + model + seconds -> predicted brain maps
  - Side by side with speed comparison
- Phase 2: Recovery of known findings
  - Show 3 established results the model recovers:
    1. Tonotopy in auditory cortex (frequency selectivity gradient)
    2. Retinotopy in visual cortex (spatial position selectivity)
    3. Language lateralization (left hemisphere dominance)
  - Each appears as a small brain map with the expected pattern
- Phase 3: New discoveries
  - "Fine-grained topography of multisensory integration"
  - Show high-res map that traditional methods couldn't produce
- BOTTOM: "Simulate experiments that would take months -- in seconds"
Visual anchors: Model box as "digital twin"
Cleanup: FadeOut all

## Scene 11: AblationsScene (~75s)
Template: CHART_FOCUS
Content:
- Title: "Ablation Study: What Actually Matters?"
- Phase 1: Modality ablation bar chart
  - Bars: Text=0.22, Audio=0.24, Video=0.25, T+V=0.30, All=0.31
  - Progressive reveal, each bar grows
  - Annotation: "Multimodal > best unimodal by 24%"
- Phase 2: Architecture ablation
  - Without transformer: 0.23 (red bar, annotated "drop of 0.08")
  - Separate subjects: 0.29 (orange bar, annotated "drop of 0.02")
  - Full model: 0.31 (green bar)
- Phase 3: Scaling law inset
  - Small axes: x=training sessions, y=encoding score
  - Monotonically increasing curve, "no plateau reached" annotation
- BOTTOM: "The transformer and multimodality are each essential -- not interchangeable"
Visual anchors: Bar chart
Cleanup: FadeOut all
Data: All scores from research.md ablation tables

## Scene 12: LimitationsScene (~75s)
Template: BUILD_UP
Content:
- Title: "Limitations and Open Questions"
- Phase 1: Honest limitations (build up list)
  1. "fMRI only" -- no temporal precision (1.5-2s TR)
  2. "Perception only" -- cannot model behavior, memory, decision-making
  3. "Frozen backbones" -- may miss brain-relevant features not learned by LLaMA/V-JEPA
  4. "Sub-linear scaling" -- more data helps, but with diminishing returns
  - Each with a warning icon in DANGER color
- Phase 2: Open questions (transition to ACCENT color)
  1. Can we close the noise ceiling gap (54% -> ???)?
  2. What about EEG/MEG for temporal resolution?
  3. Can we decode (brain -> stimulus) with the same architecture?
  4. What about fine-tuning the backbones with brain data?
  - Each with a question mark icon
- Phase 3: Citation card
  - Paper title, authors, year
  - GitHub + HuggingFace links
- BOTTOM: "The gap between digital twin and biological reality remains -- but it's shrinking"
Visual anchors: Limitation list
Cleanup: Final scene, hold
Data: Noise ceiling 54%, TR 1.5-2s
