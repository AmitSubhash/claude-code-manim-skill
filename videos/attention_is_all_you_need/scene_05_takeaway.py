import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.style import *  # noqa: F403


def method_card(title_text: str, lines: list[str], color: str) -> VGroup:
    title = safe_text(title_text, font_size=LABEL_SIZE, color=color, max_width=2.4)
    body = safe_lines(*lines, font_size=SMALL_SIZE, color=WHITE, max_width=2.5, buff=0.16)
    body.next_to(title, DOWN, buff=0.22)
    group = VGroup(title, body)
    frame = RoundedRectangle(
        width=2.9,
        height=max(2.2, group.height + 0.45),
        corner_radius=0.14,
        color=color,
        fill_color=CARD_FILL,
        fill_opacity=0.85,
        stroke_width=2,
    )
    group.move_to(frame)
    return VGroup(frame, group)


class TakeawayScene(Scene):
    def construct(self) -> None:
        title = section_title("Why the Paper Changed Everything")

        rnn = method_card("RNN", ["long path", "sequential compute", "global context is indirect"], PATH_RED)
        cnn = method_card("CNN", ["short local windows", "parallel within a layer", "needs many layers for long range"], SOFT_PURPLE)
        tx = method_card("Transformer", ["one-hop global access", "highly parallel", "stackable attention blocks"], ATTN_GOLD)
        cards = VGroup(rnn, cnn, tx).arrange(RIGHT, buff=0.35, aligned_edge=UP)
        cards.next_to(title, DOWN, buff=0.78)

        focus = SurroundingRectangle(tx, color=ATTN_GOLD, buff=0.12, stroke_width=4)

        arrow = Arrow(cards.get_bottom() + DOWN * 0.2, cards.get_bottom() + DOWN * 1.1, buff=0.0, color=PAPER_BLUE, stroke_width=4)
        modern = VGroup(
            token_box("BERT", color=PAPER_BLUE, width=1.6),
            token_box("GPT", color=TOKEN_GREEN, width=1.5),
            token_box("T5", color=SOFT_PURPLE, width=1.4),
        ).arrange(RIGHT, buff=0.28)
        modern.next_to(arrow, DOWN, buff=0.22)
        modern_label = safe_text("Modern language models build on this blueprint", font_size=LABEL_SIZE, color=PAPER_BLUE)
        modern_label.next_to(modern, DOWN, buff=0.25)

        note = bottom_note("The paper mattered because it made long-range reasoning and large-scale training easier at the same time.")

        # NARRATION: Transformers won with shorter paths and parallel training.
        self.play(Write(title), LaggedStart(*[FadeIn(card, shift=UP * 0.12) for card in cards], lag_ratio=0.15), run_time=3.0)

        # NARRATION: That is why BERT, GPT, and T5 all build on this blueprint.
        self.play(Create(focus), run_time=0.9)
        self.play(Create(arrow), LaggedStart(*[FadeIn(model, shift=UP * 0.1) for model in modern], lag_ratio=0.12), run_time=1.4)
        self.play(FadeIn(modern_label), FadeIn(note, shift=UP * 0.16), run_time=1.0)
        self.wait(2.2)
