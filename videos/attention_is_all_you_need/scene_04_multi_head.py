import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.style import *  # noqa: F403


def build_head_panel(title_text: str, values: list[list[float]], color: str) -> VGroup:
    title = safe_text(title_text, font_size=LABEL_SIZE, color=color, max_width=2.8)
    rows = VGroup()
    for row_values in values:
        row = VGroup(*[attention_cell(value, color=color, size=0.38) for value in row_values]).arrange(RIGHT, buff=0.05)
        rows.add(row)
    heatmap = rows.arrange(DOWN, buff=0.05)
    panel = VGroup(title, heatmap).arrange(DOWN, buff=0.2)
    frame = SurroundingRectangle(panel, color=color, buff=0.16, corner_radius=0.12)
    return VGroup(frame, panel)


class MultiHeadPositionalScene(Scene):
    def construct(self) -> None:
        title = section_title("Multi-Head Attention + Position")

        head_a = build_head_panel(
            "head 1: local",
            [[0.72, 0.22, 0.08], [0.18, 0.68, 0.20], [0.05, 0.21, 0.74]],
            PAPER_BLUE,
        )
        head_b = build_head_panel(
            "head 2: syntax",
            [[0.20, 0.76, 0.11], [0.61, 0.18, 0.25], [0.28, 0.19, 0.71]],
            TOKEN_GREEN,
        )
        head_c = build_head_panel(
            "head 3: long-range",
            [[0.13, 0.18, 0.78], [0.22, 0.24, 0.62], [0.74, 0.16, 0.12]],
            SOFT_PURPLE,
        )
        heads = VGroup(head_a, head_b, head_c).arrange(RIGHT, buff=0.35)
        heads.next_to(title, DOWN, buff=0.7)

        tokens = VGroup(*[token_box(word, width=1.1).scale(0.72) for word in ["pos 1", "pos 2", "pos 3", "pos 4"]])
        tokens.arrange(RIGHT, buff=0.18)
        tokens.next_to(heads, DOWN, buff=0.8)

        bars = VGroup()
        heights = [0.4, 0.9, 1.25, 0.65]
        colors = [PAPER_BLUE, TOKEN_GREEN, ATTN_GOLD, SOFT_PURPLE]
        for height, color in zip(heights, colors):
            bar = Rectangle(
                width=0.38,
                height=height,
                color=color,
                fill_color=color,
                fill_opacity=0.78,
                stroke_width=1.5,
            )
            bars.add(bar)
        bars.arrange(RIGHT, buff=0.45, aligned_edge=DOWN)
        bars.next_to(tokens, DOWN, buff=0.35)
        pos_label = safe_text("positional signal", font_size=LABEL_SIZE, color=ATTN_GOLD)
        pos_label.next_to(bars, DOWN, buff=0.2)

        note = bottom_note("Different heads specialize, and positional encoding restores word order.")

        # NARRATION: One map helps, but several heads help more.
        self.play(Write(title), LaggedStart(*[FadeIn(head, shift=UP * 0.12) for head in heads], lag_ratio=0.15), run_time=2.6)

        # NARRATION: Different heads catch different patterns.
        self.play(head_b.animate.shift(UP * 0.08), head_c.animate.shift(UP * 0.12), run_time=1.0)
        self.play(head_b.animate.shift(DOWN * 0.08), head_c.animate.shift(DOWN * 0.12), run_time=1.0)

        # NARRATION: And because attention has no built-in order, we add position signals.
        self.play(LaggedStart(*[FadeIn(token, shift=UP * 0.08) for token in tokens], lag_ratio=0.08), run_time=1.1)
        self.play(LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in bars], lag_ratio=0.1), FadeIn(pos_label), run_time=1.2)
        self.play(FadeIn(note, shift=UP * 0.16), run_time=0.8)
        self.wait(1.8)
