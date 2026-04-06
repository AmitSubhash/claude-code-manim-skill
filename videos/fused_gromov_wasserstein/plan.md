# Fused Gromov-Wasserstein for Knowledge Graph Entity Alignment

Paper: Tang et al., "A Fused Gromov-Wasserstein Framework for Unsupervised Knowledge Graph Entity Alignment" (ACL 2023 Findings)
Source: https://arxiv.org/abs/2305.06574

## Narration Script

### Scene 1: Hook (~12s)
"Two knowledge graphs, built independently, in different languages. Can we automatically discover which entities are the same? This paper does it with zero supervision and beats methods that use thousands of labeled pairs. The secret? Optimal transport."

### Scene 2: Problem (~12s)
"The standard approach embeds each entity, then matches nearest neighbors. But greedy matching ignores something crucial: graph structure. If two entities have similar names but completely different neighborhoods, should they really match?"

### Scene 3: Optimal Transport Background (~14s)
"Optimal transport finds the cheapest way to move mass from one distribution to another. Think of it as shipping goods from warehouses to stores. The transport plan tells you how much to ship along each route. This plan is a matrix, and finding the best one is a linear program."

### Scene 4: Gromov-Wasserstein Distance (~16s)
"But what if you cannot compare items directly across domains? Gromov-Wasserstein compares internal structures instead. If Alice and Bob are friends, then whoever they map to should also be friends. Fused GW combines both: match entities that are similar AND whose neighborhoods match up."

### Scene 5: The FGWEA Method (~14s)
"FGWEA works in three stages. First, match by name embeddings to find anchor pairs. Second, use anchors to linearize the expensive structural comparison. Third, refine globally with full Gromov-Wasserstein optimization. Each stage bootstraps the next."

### Scene 6: Takeaway (~10s)
"On cross-lingual benchmarks, FGWEA with zero labels hits 98.7% accuracy, beating supervised methods trained on 30% labeled data. The lesson: when matching structured objects, compare the structure, not just the features."

## Curriculum

Scene 1 (Hook, ~12s): Key result reveal
  Insight: "Unsupervised alignment of KGs works better than supervised when you use structure"
  Patterns: #22 Title Card, cross-lingual KG pair with alignment arrows
  Template: FULL_CENTER

Scene 2 (Problem, ~12s): Why greedy embedding matching fails
  Insight: "Embeddings lose structural information; greedy matching is locally optimal"
  Patterns: #10 Side-by-Side comparison, #19 Strikethrough on wrong matches
  Template: DUAL_PANEL

Scene 3 (OT Background, ~14s): Optimal transport as shipping problem
  Insight: "A transport plan is a soft matching matrix that respects marginal constraints"
  Patterns: Geometry before algebra -- show warehouses/stores first, then the matrix
  Template: BUILD_UP

Scene 4 (GW + FGW Theory, ~16s): Structure-preserving matching
  Insight: "GWD preserves internal relationships; FGW adds feature similarity"
  Patterns: Social network analogy, then equation decomposition with dim-highlight
  Template: FULL_CENTER

Scene 5 (FGWEA Method, ~14s): Three-stage progressive algorithm
  Insight: "Anchors linearize the quadratic problem; each stage bootstraps the next"
  Patterns: Pipeline diagram with 3 stages, anchor propagation visual
  Template: TOP_PERSISTENT_BOTTOM_CONTENT

Scene 6 (Takeaway, ~10s): Results and key message
  Insight: "Structure matters more than labels"
  Patterns: Bar chart comparison, one-line takeaway
  Template: GRID_CARDS

## Color Semantics

- KG1 entities/edges: BLUE_C family
- KG2 entities/edges: RED_C family
- Transport plan / alignment: YELLOW / GOLD
- Correct match: GREEN
- Wrong match: RED_D
- Structure: TEAL
- Features/semantic: ORANGE
- Anchors: PURE_YELLOW
