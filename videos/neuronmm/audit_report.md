# Audit Report: neuronmm
Generated: 2026-03-28 14:49:52
Scenes: 15

## Summary
- Code checks: 146/151 passed
- Frames extracted: 30

## Code Analysis

### Scene 1: scene_01_hook.py (HookScene)

- [PASS] No \n in Text(): Clean
- [PASS] Bottom notes use FadeIn: Clean
- [PASS] No $ in MathTex(): Clean
- [PASS] Layout bounds: Within safe area
- [PASS] Title lifecycle: No section_title() calls
- [PASS] End cleanup: Scene ends with cleanup
- [PASS] DIM_OPACITY value: Clean
- [PASS] interpolate_color wrapping: Clean
- [PASS] Style import: Imports style
- [PASS] Empty waits: Clean

### Scene 2: scene_02_llm.py (WhatIsLLMScene)

- [PASS] No \n in Text(): Clean
- [PASS] Bottom notes use FadeIn: Clean
- [PASS] No $ in MathTex(): Clean
- [PASS] Layout bounds: Within safe area
- [PASS] Title lifecycle: No section_title() calls
- [PASS] End cleanup: Scene ends with cleanup
- [WARN] DIM_OPACITY value: set_opacity(0.3) should be 0.1 at line 144
- [WARN] DIM_OPACITY value: set_opacity(0.3) should be 0.1 at line 187
- [PASS] interpolate_color wrapping: Clean
- [PASS] Style import: Imports style
- [PASS] Empty waits: Clean

### Scene 3: scene_03_matmul.py (MatrixMultiplyScene)

- [PASS] No \n in Text(): Clean
- [PASS] Bottom notes use FadeIn: Clean
- [PASS] No $ in MathTex(): Clean
- [PASS] Layout bounds: Within safe area
- [PASS] Title lifecycle: No section_title() calls
- [PASS] End cleanup: Scene ends with cleanup
- [PASS] DIM_OPACITY value: Clean
- [PASS] interpolate_color wrapping: Clean
- [PASS] Style import: Imports style
- [PASS] Empty waits: Clean

### Scene 4: scene_04_cpu.py (HowCPUWorksScene)

- [PASS] No \n in Text(): Clean
- [WARN] Bottom notes use FadeIn: Write() on bottom_note at line 263
- [PASS] No $ in MathTex(): Clean
- [PASS] Layout bounds: Within safe area
- [PASS] Title lifecycle: No section_title() calls
- [PASS] End cleanup: Scene ends with cleanup
- [PASS] DIM_OPACITY value: Clean
- [PASS] interpolate_color wrapping: Clean
- [PASS] Style import: Imports style
- [PASS] Empty waits: Clean

### Scene 5: scene_05_gpu.py (EnterTheGPUScene)

- [PASS] No \n in Text(): Clean
- [WARN] Bottom notes use FadeIn: Write() on bottom_note at line 162
- [PASS] No $ in MathTex(): Clean
- [PASS] Layout bounds: Within safe area
- [PASS] Title lifecycle: Titles cleaned up
- [PASS] End cleanup: Scene ends with cleanup
- [PASS] DIM_OPACITY value: Clean
- [PASS] interpolate_color wrapping: Clean
- [PASS] Style import: Imports style
- [PASS] Empty waits: Clean

### Scene 6: scene_06_memwall.py (MemoryHierarchyScene)

- [PASS] No \n in Text(): Clean
- [PASS] Bottom notes use FadeIn: Clean
- [PASS] No $ in MathTex(): Clean
- [PASS] Layout bounds: Within safe area
- [PASS] Title lifecycle: Titles cleaned up
- [PASS] End cleanup: Scene ends with cleanup
- [PASS] DIM_OPACITY value: Clean
- [PASS] interpolate_color wrapping: Clean
- [PASS] Style import: Imports style
- [PASS] Empty waits: Clean

### Scene 7: scene_07_gpumem.py (GPUMemoryDeepDiveScene)

- [PASS] No \n in Text(): Clean
- [PASS] Bottom notes use FadeIn: Clean
- [PASS] No $ in MathTex(): Clean
- [PASS] Layout bounds: Within safe area
- [PASS] Title lifecycle: Titles cleaned up
- [PASS] End cleanup: Scene ends with cleanup
- [PASS] DIM_OPACITY value: Clean
- [PASS] interpolate_color wrapping: Clean
- [PASS] Style import: Imports style
- [PASS] Empty waits: Clean

### Scene 8: scene_08_bandwidth.py (BandwidthBottleneckScene)

- [PASS] No \n in Text(): Clean
- [PASS] Bottom notes use FadeIn: Clean
- [PASS] No $ in MathTex(): Clean
- [PASS] Layout bounds: Within safe area
- [PASS] Title lifecycle: Titles cleaned up
- [PASS] End cleanup: Scene ends with cleanup
- [PASS] DIM_OPACITY value: Clean
- [PASS] interpolate_color wrapping: Clean
- [PASS] Style import: Imports style
- [PASS] Empty waits: Clean

### Scene 9: scene_09_accelerators.py (AIAcceleratorsScene)

- [PASS] No \n in Text(): Clean
- [PASS] Bottom notes use FadeIn: Clean
- [PASS] No $ in MathTex(): Clean
- [PASS] Layout bounds: Within safe area
- [PASS] Title lifecycle: Titles cleaned up
- [PASS] End cleanup: Scene ends with cleanup
- [PASS] DIM_OPACITY value: Clean
- [PASS] interpolate_color wrapping: Clean
- [PASS] Style import: Imports style
- [PASS] Empty waits: Clean

### Scene 10: scene_10_trainium.py (InsideTrainiumScene)

- [PASS] No \n in Text(): Clean
- [PASS] Bottom notes use FadeIn: Clean
- [PASS] No $ in MathTex(): Clean
- [PASS] Layout bounds: Within safe area
- [PASS] Title lifecycle: Titles cleaned up
- [PASS] End cleanup: Scene ends with cleanup
- [WARN] DIM_OPACITY value: set_opacity(0.3) should be 0.1 at line 136
- [PASS] interpolate_color wrapping: Clean
- [PASS] Style import: Imports style
- [PASS] Empty waits: Clean

### Scene 11: scene_11_constraints.py (TrainiumConstraintsScene)

- [PASS] No \n in Text(): Clean
- [PASS] Bottom notes use FadeIn: Clean
- [PASS] No $ in MathTex(): Clean
- [PASS] Layout bounds: Within safe area
- [PASS] Title lifecycle: Titles cleaned up
- [PASS] End cleanup: Scene ends with cleanup
- [PASS] DIM_OPACITY value: Clean
- [PASS] interpolate_color wrapping: Clean
- [PASS] Style import: Imports style
- [PASS] Empty waits: Clean

### Scene 12: scene_12_svd.py (SVDExplainedScene)

- [PASS] No \n in Text(): Clean
- [PASS] Bottom notes use FadeIn: Clean
- [PASS] No $ in MathTex(): Clean
- [PASS] Layout bounds: Within safe area
- [PASS] Title lifecycle: Titles cleaned up
- [PASS] End cleanup: Scene ends with cleanup
- [PASS] DIM_OPACITY value: Clean
- [PASS] interpolate_color wrapping: Clean
- [PASS] Style import: Imports style
- [PASS] Empty waits: Clean

### Scene 13: scene_13_neuronmm.py (NeuronMMSolutionScene)

- [PASS] No \n in Text(): Clean
- [PASS] Bottom notes use FadeIn: Clean
- [PASS] No $ in MathTex(): Clean
- [PASS] Layout bounds: Within safe area
- [PASS] Title lifecycle: Titles cleaned up
- [PASS] End cleanup: Scene ends with cleanup
- [PASS] DIM_OPACITY value: Clean
- [PASS] interpolate_color wrapping: Clean
- [PASS] Style import: Imports style
- [PASS] Empty waits: Clean

### Scene 14: scene_14_results.py (ResultsScene)

- [PASS] No \n in Text(): Clean
- [PASS] Bottom notes use FadeIn: Clean
- [PASS] No $ in MathTex(): Clean
- [PASS] Layout bounds: Within safe area
- [PASS] Title lifecycle: Titles cleaned up
- [PASS] End cleanup: Scene ends with cleanup
- [PASS] DIM_OPACITY value: Clean
- [PASS] interpolate_color wrapping: Clean
- [PASS] Style import: Imports style
- [PASS] Empty waits: Clean

### Scene 15: scene_15_wrapup.py (WrapUpScene)

- [PASS] No \n in Text(): Clean
- [PASS] Bottom notes use FadeIn: Clean
- [PASS] No $ in MathTex(): Clean
- [PASS] Layout bounds: Within safe area
- [PASS] Title lifecycle: Titles cleaned up
- [PASS] End cleanup: Scene ends with cleanup
- [PASS] DIM_OPACITY value: Clean
- [PASS] interpolate_color wrapping: Clean
- [PASS] Style import: Imports style
- [PASS] Empty waits: Clean

## Frame Extraction
Frames saved to: /Users/amit/Projects/3brown1blue/videos/neuronmm/audit_frames/

- scene_01_hook_HookScene/frame_10.png, frame_25.png
- scene_02_llm_WhatIsLLMScene/frame_10.png, frame_25.png
- scene_03_matmul_MatrixMultiplyScene/frame_10.png, frame_25.png
- scene_04_cpu_HowCPUWorksScene/frame_10.png, frame_25.png
- scene_05_gpu_EnterTheGPUScene/frame_10.png, frame_25.png
- scene_06_memwall_MemoryHierarchyScene/frame_10.png, frame_25.png
- scene_07_gpumem_GPUMemoryDeepDiveScene/frame_10.png, frame_25.png
- scene_08_bandwidth_BandwidthBottleneckScene/frame_10.png, frame_25.png
- scene_09_accelerators_AIAcceleratorsScene/frame_10.png, frame_25.png
- scene_10_trainium_InsideTrainiumScene/frame_10.png, frame_25.png
- scene_11_constraints_TrainiumConstraintsScene/frame_10.png, frame_25.png
- scene_12_svd_SVDExplainedScene/frame_10.png, frame_25.png
- scene_13_neuronmm_NeuronMMSolutionScene/frame_10.png, frame_25.png
- scene_14_results_ResultsScene/frame_10.png, frame_25.png
- scene_15_wrapup_WrapUpScene/frame_10.png, frame_25.png

Review frames manually for:
- Text overlap
- Empty frames (>60% blank)
- Elements clipped at edges
- Inconsistent title positioning
