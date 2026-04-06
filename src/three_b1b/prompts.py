"""User-side prompts that reference the skill's own structures.

These prompts are the bridge between the user's intent and the full Manim
skill loaded in the system prompt. They explicitly ask the LLM to use the
layout templates, scene plan format, production rules, and style.py contract
defined in the skill rules.
"""

# ── Single-scene quick generation (--single-scene flag) ──────────────────

SINGLE_SCENE = """\
TOPIC: {topic}
AUDIENCE: {audience}
DOMAIN: {domain}

Generate ONE self-contained Manim scene that explains this topic in {duration} seconds.

RULES:
1. One Scene subclass, one construct() method, one file
2. Layout template: {template}
3. Start with a title, end with a bottom note takeaway
4. Geometry before algebra: show the visual first, then the equation
5. Use Write() for text, Create() for shapes
6. MathTex without dollar signs
7. safe_text() pattern: cap width at 12 Manim units
8. self.wait() after every major reveal
9. Fill 50%+ of frame, no large empty regions
10. x in [-5.5, 5.5], y in [-3.2, 3.2]
11. Add # NARRATION: comments for voiceover beats
12. Font: use font="Menlo" for all Text() objects
13. Use named color constants, never raw hex inline
14. Include concrete values and examples, not abstract descriptions

Output a complete, runnable Python file. No explanation outside the code.\
"""

# ── Topic-based generation (generate command) ─────────────────────────────

RESEARCH_AND_PLAN = """\
TOPIC: {topic}
AUDIENCE: {audience}
DOMAIN: {domain}

Follow the planning pipeline from your Scene Planning rules:
  research -> curriculum (scene list) -> scene plans -> style.py

STEP 1 - RESEARCH: Think deeply about this topic. What are the core concepts,
the key equations, the visual intuitions? What would a viewer need to understand?
What data or concrete values can you include?

STEP 1.5 - MISCONCEPTION ANALYSIS (required):
Before designing the curriculum, identify:
1. What does the target audience WRONGLY believe about this topic?
2. What is the most common incorrect mental model?
3. Where does intuition break down?
Structure the video to: show the misconception first (let viewer think "yes, that makes sense"),
introduce the evidence that breaks it, show the correct model, explain WHY the misconception exists.

STEP 2 - CURRICULUM: Design a scene sequence following the audience-specific
curriculum structure from your Audience rules. Match the scene count, pacing,
and annotation depth to the specified audience level.
Identify the ONE surprising connection or core question the video answers.

STEP 3 - SCENE PLANS: For each scene, write a plan in this exact format:
  ## Scene N: ClassName (~duration)
  Template: [one of FULL_CENTER, DUAL_PANEL, TOP_PERSISTENT_BOTTOM_CONTENT, BUILD_UP, CHART_FOCUS, GRID_CARDS]
  Content:
  - [what goes where, using the template's coordinate regions]
  Visual anchors: [persistent elements across scenes]
  Cleanup: [what to FadeOut before next section]
  Equations: [any MathTex strings, NO dollar signs]
  Data: [concrete numbers, percentages, values]

STEP 4 - STYLE CONTRACT: Define a style.py section with:
  - Semantic color names and hex values
  - Font sizes (TITLE_SIZE, BODY_SIZE, LABEL_SIZE, EQ_SIZE)
  - Layout constants (TITLE_Y, BOTTOM_Y, SAFE_WIDTH)
  - Helper functions: section_title(), safe_text(), bottom_note(), fade_all()

STEP 5 - VISUAL DESIGN: Apply these principles from your rules and domain-specific
conventions (if a domain is specified):
  - Geometry before algebra (show the shape, then the equation)
  - Opacity layering (primary 100%, context 40%, grid 15%)
  - Persistent context objects across scenes
  - Question frames before reveals
  - Annotations ON the object, not beside it
  - Color as semantic data (consistent meaning throughout)
  - Concrete values at every stage (never just "it increases")

STEP 6 - NARRATION SCRIPT:
For each scene, write a narration script (what a narrator would say).
One paragraph per scene, timed to match the animation duration.
Match vocabulary and tone to the specified audience level.
Output as a separate "## Narration Script" section at the end.

Output the complete plan as structured markdown.\
"""

GENERATE_FROM_PLAN = """\
VIDEO PLAN:

{plan}

Generate a complete, runnable Manim Python file implementing ALL scenes.

MANDATORY RULES (from your skill rules, non-negotiable):
1. Layout: Use the template specified in each scene plan. x in [-5.5, 5.5], y in [-3.2, 3.2]
2. Text: safe_text() pattern for body. Max width 12 Manim units. Scale if wider.
3. Containers: Position children relative to parent (next_to, move_to), not absolute
4. Lifecycle: FadeOut titles/headers before new content reuses their region
5. Density: Fill 50%+ of frame. Bars fill_opacity >= 0.6, width >= 0.3
6. Cleanup: FadeOut all elements before the next logical section
7. MathTex: NO dollar signs. Use Tex for mixed text+math
8. Animations: Write() for text, Create() for shapes, ReplacementTransform for eq chains
9. Bottom text: buff >= 0.5, FadeOut previous before adding new
10. Updaters: self.wait(frozen_frame=False) when updaters are active
11. Misconception arc: If the plan includes a misconception scene, animate the wrong model
    first with a distinct "wrong" color, then transition to the correct model
12. Audience pacing: Match wait() durations and annotation density to the audience level
    in the plan (high-school: longer waits, fewer annotations; graduate: faster, denser)
13. Domain conventions: Apply domain-specific notation and visual idioms from the plan
    (e.g., ML: loss curves, weight matrices; physics: vector fields, free-body diagrams)
14. Narration hooks: Add a comment above each self.play() block indicating the narration
    line it corresponds to (# NARRATION: "...")
15. Color semantics: Define all colors as named constants at the top; never use raw hex
    strings inline. Every color must appear in the style contract.
16. Persistent elements: Objects declared as "Visual anchors" in the plan must be created
    once and transformed/updated across scenes, never recreated from scratch
17. Equation chains: Use ReplacementTransform between successive equation states; align
    on the equals sign using aligned environment when showing derivation steps
18. Final scene: Always end with a summary or takeaway scene that revisits the core
    question posed in the hook, completing the narrative arc

STRUCTURE:
- Define style constants at the top (colors, sizes, helpers) matching the plan's style contract
- One Scene subclass per scene in the plan, in order
- Each scene is self-contained and independently renderable
- Use safe_manim patterns: safe_arrow(), safe_brace_label() where applicable
- from manim import * at the top

Return ONLY the complete Python file.\
"""

# ── Slides-based generation (from-slides command) ─────────────────────────

SLIDES_PLAN = """\
SLIDE CONTENT:

{slides_content}

AUDIENCE: {audience}
DOMAIN: {domain}

Plan a 3Blue1Brown-style animated explainer from these slides.

Use the Scene Plan format from your rules:
  ## Scene N: ClassName (~duration)
  Template: [FULL_CENTER | DUAL_PANEL | TOP_PERSISTENT_BOTTOM_CONTENT | BUILD_UP | CHART_FOCUS | GRID_CARDS]
  Content: [what goes where]
  Visual anchors: [persistent elements]
  Equations: [MathTex strings, no dollar signs]
  Data: [concrete values from the slides]

Include:
  - Title and core question the video answers
  - 4-10 scenes with template, layout, animation ideas, narration focus
  - Style contract: semantic colors, font sizes, layout constants, helpers
  - Color semantics and persistent visual motifs
  - Mathematical or conceptual throughline
  - Audience-appropriate pacing and annotation density (see your Audience rules)
  - Domain-specific notation and visual conventions (see your Domain rules if applicable)
  - Narration script: one paragraph per scene at the end under "## Narration Script"

Apply the visual design principles and production quality rules from your system prompt.
Be specific enough that a Manim developer can implement each scene directly.\
"""

SLIDES_GENERATE = """\
VIDEO PLAN:

{plan}

Generate a complete, runnable Manim Python file implementing all scenes.

MANDATORY RULES:
1. Use the layout template specified in each scene plan
2. x in [-5.5, 5.5], y in [-3.2, 3.2] for all elements
3. Write() for text, Create() for shapes, ReplacementTransform for equation chains
4. MathTex without dollar signs. Tex for mixed text+math
5. FadeOut elements before reusing their screen region
6. self.wait(frozen_frame=False) when updaters are active
7. Fill 50%+ of frame, no large empty regions
8. Style constants at top (colors, sizes, helpers) matching the plan
9. Each Scene subclass self-contained and independently renderable
10. from manim import * at the top
11. Audience pacing: Match wait() durations and annotation density to the audience level
    in the plan (high-school: longer waits, fewer annotations; graduate: faster, denser)
12. Domain conventions: Apply domain-specific notation and visual idioms from the plan

Return ONLY the complete Python file.\
"""

# ── Image description (from-slides vision extraction) ─────────────────────

IMAGE_DESCRIBE = (
    "Describe what this image shows in the context of a presentation slide. "
    "Include data values, labels, structure, equations, and key information. "
    "Be specific."
)
