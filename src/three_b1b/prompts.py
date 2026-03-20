"""User-side prompts that reference the skill's own structures.

These prompts are the bridge between the user's intent and the full Manim
skill loaded in the system prompt. They explicitly ask the LLM to use the
layout templates, scene plan format, production rules, and style.py contract
defined in the skill rules.
"""

# ── Topic-based generation (generate command) ─────────────────────────────

RESEARCH_AND_PLAN = """\
TOPIC: {topic}

Follow the planning pipeline from your Scene Planning rules:
  research -> curriculum (scene list) -> scene plans -> style.py

STEP 1 - RESEARCH: Think deeply about this topic. What are the core concepts,
the key equations, the visual intuitions? What would a viewer need to understand?
What data or concrete values can you include?

STEP 2 - CURRICULUM: Design a 6-10 scene sequence following the 5-minute
template from your Paper Explainer rules:
  Hook (10s) -> Problem (30s) -> Background (60s) -> Method (120s) -> Results (60s) -> Takeaway (20s)
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

STEP 5 - VISUAL DESIGN: Apply these principles from your rules:
  - Geometry before algebra (show the shape, then the equation)
  - Opacity layering (primary 100%, context 40%, grid 15%)
  - Persistent context objects across scenes
  - Question frames before reveals
  - Annotations ON the object, not beside it
  - Color as semantic data (consistent meaning throughout)
  - Concrete values at every stage (never just "it increases")

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

Apply the 12 visual design principles and production quality rules from your system prompt.
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

Return ONLY the complete Python file.\
"""

# ── Image description (from-slides vision extraction) ─────────────────────

IMAGE_DESCRIBE = (
    "Describe what this image shows in the context of a presentation slide. "
    "Include data values, labels, structure, equations, and key information. "
    "Be specific."
)
