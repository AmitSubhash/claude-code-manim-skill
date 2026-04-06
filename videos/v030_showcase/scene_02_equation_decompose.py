"""Scene 02: Equation Decomposition -- the dim-and-highlight teaching pattern.

Shows the attention equation, then highlights each term one by one with
color-coded rectangles, braces, and explanatory labels. Ends with the
full color-coded equation and a golden tagline.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *

DIM_OPACITY = 0.1


def _highlight_term(
    scene: Scene,
    equation: MathTex,
    part_index: int,
    color: str,
    label_text: str,
) -> VGroup:
    """Highlight a sub-expression: rectangle + brace + label.

    Returns the annotation VGroup so it can be cleaned up later.
    """
    target = equation[part_index]

    rect = SurroundingRectangle(
        target, color=color, buff=0.12, corner_radius=0.08, stroke_width=2.0
    )
    brace = Brace(target, DOWN, color=color, buff=0.15)
    brace.stretch_to_fit_width(max(brace.width, target.width * 0.8))
    label = safe_text(label_text, font_size=LABEL_SIZE, color=color)
    label.next_to(brace, DOWN, buff=0.15)
    if label.width > 6.0:
        label.scale_to_fit_width(6.0)

    # Bring this term to full opacity
    scene.play(
        target.animate.set_opacity(1.0),
        Create(rect),
        GrowFromCenter(brace),
        FadeIn(label, shift=UP * 0.15),
        run_time=0.8,
    )
    scene.wait(0.8)

    # Color the term, remove annotation
    annotation = VGroup(rect, brace, label)
    scene.play(
        target.animate.set_color(color),
        FadeOut(annotation),
        run_time=0.6,
    )
    return annotation


class EquationDecomposeScene(Scene):
    """12-second centerpiece: dim-and-highlight decomposition."""

    def construct(self) -> None:
        self.camera.background_color = BG

        # -- Build equation with isolatable sub-expressions --
        # Index 0: "Attention(Q,K,V) ="
        # Index 1: "softmax"  (the function name)
        # Index 2: "(" (open paren with fraction)
        # Index 3: "QK^T"
        # Index 4: "\\sqrt{d_k}"
        # Index 5: ")" V
        #
        # Restructured for clean isolation:
        equation = MathTex(
            r"{{ \mathrm{Attention}(Q,K,V) = }}",  # 0
            r"{{ \mathrm{softmax} }}",              # 1
            r"{{ \left( \frac{ QK^T }{ \sqrt{d_k} } \right) }}",  # 2
            r"{{ V }}",                             # 3
            font_size=EQ_SIZE + 4,
        )
        equation.set_color(WARM_WHITE)
        equation.move_to(ORIGIN + UP * 0.8)

        # -- Write full equation --
        self.play(Write(equation), run_time=1.2)
        self.wait(0.3)

        # -- Dim everything to DIM_OPACITY --
        self.play(equation.animate.set_opacity(DIM_OPACITY), run_time=0.5)

        # -- Highlight softmax (index 1) --
        _highlight_term(
            self, equation, 1, TEAL, "normalizes scores to probabilities"
        )

        # -- Dim again, highlight scaled dot product (index 2) --
        self.play(
            equation[1].animate.set_opacity(DIM_OPACITY),
            run_time=0.3,
        )
        _highlight_term(
            self, equation, 2, CORAL, "scaled dot-product attention scores"
        )

        # -- Dim again, highlight V (index 3) --
        self.play(
            equation[2].animate.set_opacity(DIM_OPACITY),
            run_time=0.3,
        )
        _highlight_term(
            self, equation, 3, VIOLET, "value vectors, weighted by attention"
        )

        # -- Restore full equation with all colors --
        self.play(
            equation.animate.set_opacity(1.0),
            run_time=0.8,
        )
        self.wait(0.3)

        # -- Tagline at the bottom --
        tag1 = safe_text("Every term explained.", font_size=BODY_SIZE, color=GOLD)
        tag2 = safe_text("Every color earned.", font_size=BODY_SIZE, color=GOLD)
        tagline = VGroup(tag1, tag2).arrange(DOWN, buff=0.2, center=True)
        tagline.to_edge(DOWN, buff=0.6)

        self.play(FadeIn(tagline, shift=UP * 0.2), run_time=0.8)
        self.wait(1.0)
