import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.style import *  # noqa: F403


class QueryKeyValueScene(Scene):
    def construct(self) -> None:
        title = section_title("Queries, Keys, and Values")

        words = ["The", "query", "checks", "keys"]
        tokens = VGroup(*[token_box(word) for word in words]).arrange(RIGHT, buff=0.25)
        tokens.next_to(title, DOWN, buff=0.7)

        selected = SurroundingRectangle(tokens[1], color=ATTN_GOLD, buff=0.08)
        query_box = token_box("Query", color=ATTN_GOLD, width=1.6).scale(0.85)
        query_box.next_to(tokens[1], DOWN, buff=0.75)

        key_boxes = VGroup()
        value_boxes = VGroup()
        for token in tokens:
            key = token_box("Key", color=TOKEN_GREEN, width=1.1, height=0.54).scale(0.72)
            value = token_box("Value", color=PAPER_BLUE, width=1.25, height=0.54).scale(0.72)
            key.next_to(token, DOWN, buff=0.8)
            value.next_to(key, DOWN, buff=0.18)
            key_boxes.add(key)
            value_boxes.add(value)

        arrows = VGroup()
        weights = [0.12, 0.18, 0.24, 0.74]
        bars = VGroup()
        for idx, (key_box, value) in enumerate(zip(key_boxes, weights)):
            color = ATTN_GOLD if idx == 3 else MUTED_GRAY
            arrows.add(
                Arrow(
                    query_box.get_bottom(),
                    key_box.get_top(),
                    buff=0.12,
                    color=color,
                    stroke_width=3,
                    max_tip_length_to_length_ratio=0.12,
                )
            )
            bar = Rectangle(
                width=0.5,
                height=1.2 * value,
                color=color,
                fill_color=color,
                fill_opacity=0.75,
                stroke_width=1.5,
            )
            label = safe_text(f"{value:.2f}", font_size=SMALL_SIZE, color=color, max_width=0.7)
            label.next_to(bar, DOWN, buff=0.12)
            bars.add(VGroup(bar, label))
        bars.arrange(RIGHT, buff=0.3, aligned_edge=DOWN)
        bars.next_to(value_boxes, DOWN, buff=0.45)
        weight_label = safe_text("Attention weights", font_size=LABEL_SIZE, color=ATTN_GOLD)
        weight_label.next_to(bars, DOWN, buff=0.18)

        note = bottom_note("A query scores all keys, then blends the values using those scores.")

        # NARRATION: Each token makes a query, key, and value.
        self.play(Write(title), LaggedStart(*[FadeIn(token, shift=UP * 0.12) for token in tokens], lag_ratio=0.1), run_time=2.2)

        # NARRATION: The query checks every key and scores what matters.
        self.play(Create(selected), FadeIn(query_box, shift=DOWN * 0.12), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(key, shift=DOWN * 0.1) for key in key_boxes], lag_ratio=0.08), run_time=1.1)
        self.play(LaggedStart(*[FadeIn(value, shift=DOWN * 0.1) for value in value_boxes], lag_ratio=0.08), run_time=1.1)
        self.play(LaggedStart(*[Create(arrow) for arrow in arrows], lag_ratio=0.08), run_time=1.2)

        # NARRATION: Then those scores mix the values into one new token.
        self.play(LaggedStart(*[GrowFromEdge(bar[0], DOWN) for bar in bars], lag_ratio=0.08), FadeIn(VGroup(*[bar[1] for bar in bars])), run_time=1.2)
        self.play(FadeIn(weight_label), FadeIn(note, shift=UP * 0.16), run_time=0.8)
        self.wait(1.8)
