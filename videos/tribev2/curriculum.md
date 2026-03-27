# TRIBE v2 Video Curriculum

## Audience: Graduate / Researcher
Viewers know: fMRI BOLD signal, linear encoding models, transformers, foundation models, attention.
Viewers do NOT know: TRIBE-specific architecture, how modality dropout works, the fsaverage5 mesh, this specific competition.

## Video Target
- Duration: ~15 minutes (12 scenes)
- Pacing: 165-185 wpm narration, run_time 0.5-1.0 for most animations
- Tone: peer-to-peer lab meeting presentation, willing to critique

## Act Structure

### Act I: Why This Matters (Scenes 1-3, ~3 min)
**Goal:** Establish the problem gap and why a unified multimodal brain model is needed.

Scene 1 - Hook (45s): "Digital Twin of the Brain"
- Key insight: You can now predict what every patch of cortex is doing while someone watches a movie -- without scanning them.
- Aha: Show a brain surface lighting up in response to a movie clip, then reveal it's predicted, not measured.

Scene 2 - The Fragmentation Problem (60s): "The Silo Problem"
- Key insight: Neuroscience labs study vision OR hearing OR language, one region at a time, with linear models. This misses cross-modal interactions.
- Aha: Show how a scene in a movie (car crash) activates visual, auditory, AND language regions simultaneously. Linear models per modality miss the cross-talk.

Scene 3 - Brain Encoding 101 (60s): "Stimulus -> Brain Response"
- Key insight: An encoding model maps stimulus features to predicted BOLD signal. Traditional = ridge regression. The gap: nonlinear, multimodal, cross-subject.
- Aha: Show linear encoding as a single matrix multiply, then ask "what if we need something more powerful?"

### Act II: The Architecture (Scenes 4-7, ~5 min)
**Goal:** Build the full TRIBE pipeline piece by piece.

Scene 4 - Three Frozen Giants (75s): "Borrowing World Knowledge"
- Key insight: Instead of training feature extractors on fMRI data, use frozen foundation models that already encode rich representations of each modality.
- Aha: LLaMA, V-JEPA 2, and Wav2Vec-BERT each see the same movie, outputting features at 2 Hz.
- Misconception: "Wouldn't a single multimodal model (like GPT-4V) work better?" No -- separate specialists outperform.

Scene 5 - The Integration Transformer (75s): "Learning Cross-Modal Fusion"
- Key insight: A trainable 8-layer transformer learns to fuse features from all three modalities. Modality dropout (p=0.3) forces robustness.
- Aha: Zero out one modality at random during training -- the model learns to work with any combination.

Scene 6 - Brain Mapping Head (60s): "From Latent Space to Cortex"
- Key insight: A low-rank bottleneck + subject-specific linear head maps transformer output to ~20,484 cortical vertices.
- Aha: The same transformer core serves 700+ subjects. Only the final layer changes.

Scene 7 - Training at Scale (60s): "700 Brains, 1000 Hours"
- Key insight: v2 trains on 4 diverse fMRI datasets (movies, clips, audiobooks). The implicit HRF learning -- no explicit convolution needed.
- Aha: Show the data scale-up from v1 (4 subjects, 1 dataset) to v2 (700+, 4 datasets).

### Act III: What It Reveals (Scenes 8-10, ~4.5 min)
**Goal:** Show the results and what the model teaches us about the brain.

Scene 8 - Competition Results & Noise Ceiling (90s): "How Good Is It?"
- Key insight: Won Algonauts 2025 (1st of 263), captures 54% of explainable variance. Near ceiling in auditory/language cortex.
- Aha: Show the normalized Pearson as a fraction of noise ceiling. Near ceiling = we're capturing nearly all the signal the data can support.

Scene 9 - Modality Maps (90s): "Which Modality Predicts Which Region?"
- Key insight: Audio dominates temporal gyrus, video dominates occipital, text dominates prefrontal/parietal. Multimodal advantage strongest in prefrontal (~30% improvement).
- Aha: Brain surface coloring by dominant modality -- reveals the topography of multisensory integration.

Scene 10 - In-Silico Neuroscience (90s): "Virtual Experiments"
- Key insight: The model recovers known findings (tonotopy, retinotopy, language lateralization) and enables testing new hypotheses computationally.
- Aha: You can simulate an experiment that would take months of fMRI scanning in seconds.

### Act IV: Critical Analysis (Scenes 11-12, ~2.5 min)
**Goal:** Ablations, limitations, and what remains open.

Scene 11 - Ablations & Scaling Laws (75s): "What Actually Matters?"
- Key insight: Multimodal > unimodal (0.31 vs 0.25), transformer essential (0.31 vs 0.23), more data helps without plateau.
- Aha: The ablation bar chart with annotations showing the biggest drops.

Scene 12 - Limitations & Open Questions (75s): "What This Cannot Do"
- Key insight: fMRI-only (no temporal precision), perception-only (no behavior/memory), frozen backbones may miss brain-relevant features, sub-linear scaling.
- Aha: End with open questions: Can we close the noise ceiling gap? What about EEG/MEG temporal resolution? Can we decode (brain -> stimulus) with the same architecture?

## Misconception Targets (Graduate-Level)
1. "A single multimodal model would be better than three specialists" (Scene 4)
   - Why it's wrong: Separate pretrained specialists outperform intrinsically multimodal models for brain encoding
   - The assumption: joint training captures cross-modal structure. Reality: frozen specialists already encode richer per-modality features.

2. "Linear encoding is just a weaker version of what transformers do" (Scene 5)
   - Why it's wrong: The transformer enables cross-modal attention that linear models cannot represent at all -- it's qualitatively different, not just more parameters.

3. "More spatial resolution always helps" (Scene 12)
   - Why it's wrong: fsaverage5 (~20k vertices) may be past the SNR benefit for fMRI. Finer meshes add computation without proportional signal.

## Narration Tone
- Collegial, precise, willing to critique
- "The authors claim..." vs "The paper shows..."
- Identify limitations honestly
- Use hedged technical language
