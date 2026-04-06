import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.style import *  # noqa: F403


class HookScene(Scene):
    def construct(self) -> None:
        title = section_title("Attention Is All You Need")
        subtitle = safe_lines(
            "Why was the 2017 transformer paper such a big deal?",
            "It replaced long recurrent chains with direct token-to-token links.",
            font_size=BODY_SIZE,
            color=MUTED_GRAY,
        )
        subtitle.next_to(title, DOWN, buff=0.28)

        words = ["The", "animal", "did", "not", "cross", "because", "it", "was", "tired"]
        tokens = VGroup(*[token_box(word) for word in words]).arrange(RIGHT, buff=0.14)
        tokens.scale(0.78)
        tokens.next_to(subtitle, DOWN, buff=0.65)

        animal_frame = SurroundingRectangle(tokens[1], color=TOKEN_GREEN, buff=0.07)
        pronoun_frame = SurroundingRectangle(tokens[6], color=ATTN_GOLD, buff=0.07)

        chain_arrows = VGroup()
        for left, right in zip(tokens[:-1], tokens[1:]):
            arrow = Arrow(
                left.get_bottom() + DOWN * 0.08,
                right.get_bottom() + DOWN * 0.08,
                buff=0.07,
                color=PATH_RED,
                stroke_width=3,
                max_tip_length_to_length_ratio=0.12,
            )
            chain_arrows.add(arrow)
        chain_arrows.shift(DOWN * 0.22)
        chain_label = safe_text(
            "Old recurrent path: information hops through many steps",
            font_size=LABEL_SIZE,
            color=PATH_RED,
        )
        chain_label.next_to(chain_arrows, DOWN, buff=0.28)

        direct_arc = CurvedArrow(
            tokens[6].get_top() + UP * 0.06,
            tokens[1].get_top() + UP * 0.06,
            angle=PI / 2.8,
            color=ATTN_GOLD,
            stroke_width=5,
        )
        direct_label = safe_text("Attention can connect them in one hop", font_size=LABEL_SIZE, color=ATTN_GOLD)
        direct_label.next_to(direct_arc, UP, buff=0.18)

        note = bottom_note("The core move is simple: let each token look anywhere in the sequence.")

        # NARRATION: Older models pass information one step at a time.
        self.play(Write(title), FadeIn(subtitle, shift=UP * 0.2), run_time=1.7)
        self.play(LaggedStart(*[FadeIn(token, shift=UP * 0.12) for token in tokens], lag_ratio=0.08), run_time=1.6)

        # NARRATION: Watch this. The word it can point straight back to animal.
        self.play(Create(animal_frame), Create(pronoun_frame), run_time=1.0)
        self.play(LaggedStart(*[Create(arrow) for arrow in chain_arrows], lag_ratio=0.12), FadeIn(chain_label), run_time=1.8)
        self.play(Create(direct_arc), FadeIn(direct_label, shift=UP * 0.12), run_time=1.4)

        # NARRATION: That shortcut is the core idea.
        self.play(chain_arrows.animate.set_stroke(opacity=0.28), FadeIn(note, shift=UP * 0.16), run_time=1.0)
        self.wait(1.9)
