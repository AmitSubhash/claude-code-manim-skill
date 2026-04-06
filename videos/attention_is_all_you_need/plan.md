# Attention Is All You Need

## Scene 1: HookScene (~10s)
Template: BUILD_UP
Content:
- Show a sentence with two distant words that should communicate.
- Contrast a long recurrent path with a direct attention link.
Visual anchors: token cards, gold attention highlight
Cleanup: fade arrow clutter before next scene
Equations: none
Data: paper published in 2017

## Scene 2: QueryKeyValueScene (~10s)
Template: DUAL_PANEL
Content:
- Turn one token into a query.
- Compare that query against keys from all tokens.
- Show attention weights and remind the viewer that values are mixed using those weights.
Visual anchors: token cards, gold attention highlight
Cleanup: remove bars and arrows before transition
Equations: none
Data: example weights 0.12, 0.18, 0.24, 0.74

## Scene 3: ScaledDotProductScene (~11s)
Template: FULL_CENTER
Content:
- Present the scaled dot-product attention formula.
- Break it into scores, softmax, and weighted sum.
- Use a small heatmap to show one query row selecting values.
Visual anchors: gold heatmap cells
Cleanup: fade heatmap and formula before next scene
Equations: Attention(Q,K,V)=softmax(QK^T / sqrt(d_k))V
Data: 4x4 example attention matrix

## Scene 4: MultiHeadPositionalScene (~10s)
Template: GRID_CARDS
Content:
- Show three different attention heads with distinct patterns.
- Add simple positional signals underneath token slots.
Visual anchors: repeated heatmap motif
Cleanup: fade panels before final takeaway
Equations: none
Data: three 3x3 attention maps

## Scene 5: TakeawayScene (~10s)
Template: GRID_CARDS
Content:
- Compare RNNs, CNNs, and transformers on path length and parallelism.
- Connect the transformer column to later models like BERT, GPT, and T5.
Visual anchors: gold highlight on transformer card
Cleanup: none
Equations: none
Data: paper published in 2017

## Narration Script

### Scene 1
Older models pass information one step at a time. Watch this. The word "it" can point straight back to "animal." That shortcut is the core idea.

### Scene 2
Each token makes a query, key, and value. The query checks every key and scores what matters. Then those scores mix the values into one new token.

### Scene 3
Here is the rule: score, softmax, then weighted sum. Each row shows where one query is looking. That row blends values into the next representation.

### Scene 4
One map helps, but several heads help more. Different heads catch different patterns. And because attention has no built-in order, we add position signals.

### Scene 5
Transformers won with shorter paths and parallel training. That is why BERT, GPT, and T5 all build on this blueprint.
