import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.style import *  # noqa: F403


class ScaledDotProductScene(Scene):
    def construct(self) -> None:
        title = section_title("Scaled Dot-Product Attention")
        formula = MathTex(
            r"\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V",
            font_size=EQ_SIZE,
            color=WHITE,
        )
        formula.scale_to_fit_width(11.2)
        formula.next_to(title, DOWN, buff=0.55)

        score_box = token_box("scores", color=PATH_RED, width=1.7).scale(0.82)
        softmax_box = token_box("softmax", color=ATTN_GOLD, width=1.9).scale(0.82)
        sum_box = token_box("weighted sum", color=TOKEN_GREEN, width=2.3).scale(0.82)
        pipeline = VGroup(score_box, softmax_box, sum_box).arrange(RIGHT, buff=0.55)
        pipeline.next_to(formula, DOWN, buff=0.65)

        arrows = VGroup(
            Arrow(score_box.get_right(), softmax_box.get_left(), buff=0.12, color=MUTED_GRAY),
            Arrow(softmax_box.get_right(), sum_box.get_left(), buff=0.12, color=MUTED_GRAY),
        )

        matrix_values = [
            [0.72, 0.18, 0.10, 0.08],
            [0.16, 0.64, 0.22, 0.11],
            [0.09, 0.23, 0.68, 0.21],
            [0.36, 0.14, 0.18, 0.58],
        ]
        rows = VGroup()
        for row_values in matrix_values:
            row = VGroup(*[attention_cell(value) for value in row_values]).arrange(RIGHT, buff=0.08)
            rows.add(row)
        heatmap = rows.arrange(DOWN, buff=0.08)
        heatmap.next_to(pipeline, DOWN, buff=0.55)

        row_labels = VGroup(*[safe_text(f"q{i + 1}", font_size=SMALL_SIZE, color=MUTED_GRAY) for i in range(4)])
        for label, row in zip(row_labels, rows):
            label.next_to(row, LEFT, buff=0.18)
        col_labels = VGroup(*[safe_text(f"k{i + 1}", font_size=SMALL_SIZE, color=MUTED_GRAY) for i in range(4)])
        for label, cell in zip(col_labels, rows[0]):
            label.next_to(cell, UP, buff=0.16)

        focus_row = SurroundingRectangle(rows[1], color=ATTN_GOLD, buff=0.1)
        output_box = token_box("mixed output", color=TOKEN_GREEN, width=2.1).scale(0.82)
        output_box.next_to(heatmap, RIGHT, buff=1.0)
        output_arrow = Arrow(heatmap.get_right(), output_box.get_left(), buff=0.18, color=TOKEN_GREEN, stroke_width=4)

        note = bottom_note("The scale term stabilizes the scores before softmax turns them into probabilities.")

        # NARRATION: Here is the rule: score, softmax, then weighted sum.
        self.play(Write(title), Write(formula), run_time=2.0)
        self.play(LaggedStart(*[FadeIn(box, shift=UP * 0.12) for box in pipeline], lag_ratio=0.15), run_time=1.3)
        self.play(LaggedStart(*[Create(arrow) for arrow in arrows], lag_ratio=0.2), run_time=1.0)

        # NARRATION: Each row shows where one query is looking.
        self.play(
            LaggedStart(*[FadeIn(cell, scale=0.9) for row in rows for cell in row], lag_ratio=0.03),
            FadeIn(row_labels),
            FadeIn(col_labels),
            run_time=1.8,
        )
        self.play(Create(focus_row), Create(output_arrow), FadeIn(output_box), run_time=1.1)

        # NARRATION: That row blends values into the next representation.
        self.play(FadeIn(note, shift=UP * 0.16), run_time=1.0)
        self.wait(2.0)
