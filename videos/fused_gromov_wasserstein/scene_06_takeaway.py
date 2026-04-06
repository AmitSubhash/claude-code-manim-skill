"""Scene 6: Takeaway -- results comparison and key message.

Duration target: ~10s
Template: GRID_CARDS
"""

import sys
sys.path.insert(0, "/Users/amit/Projects/3brown1blue/videos/fused_gromov_wasserstein")

from utils.style import *


class TakeawayScene(Scene):
    def construct(self) -> None:
        # ── Title ─────────────────────────────────────────────────────
        title = section_title("Results")

        # NARRATION: On cross-lingual benchmarks, FGWEA with zero labels
        # hits 98.7 percent accuracy.
        self.play(Write(title), run_time=1.0)
        self.wait(HOLD_SHORT)

        # ── Three comparison cards ────────────────────────────────────
        card_width = 3.2
        card_height = 2.2

        def result_card(
            method: str,
            detail: str,
            score: str,
            color: str,
            highlight: bool = False,
        ) -> VGroup:
            rect = RoundedRectangle(
                width=card_width, height=card_height,
                corner_radius=0.2, color=color,
                fill_opacity=0.15, stroke_width=2.5 if highlight else 1.5,
            )
            method_txt = Text(method, font_size=LABEL_SIZE, color=color)
            detail_txt = Text(detail, font_size=16, color=MUTED_GRAY)
            score_txt = Text(score, font_size=TITLE_SIZE, color=color,
                             weight=BOLD)
            content = VGroup(method_txt, detail_txt, score_txt).arrange(
                DOWN, buff=0.3,
            )
            content.move_to(rect)
            return VGroup(rect, content)

        card_sup = result_card(
            "Supervised", "30% labels", "96.2%",
            color=MUTED_GRAY,
        )
        card_emb = result_card(
            "Unsupervised", "embedding only", "87.4%",
            color=MUTED_GRAY,
        )
        card_fgw = result_card(
            "FGWEA", "zero labels", "98.7%",
            color=ANCHOR_COLOR, highlight=True,
        )

        cards = VGroup(card_sup, card_emb, card_fgw).arrange(
            RIGHT, buff=0.6,
        )
        cards.move_to(DOWN * 0.3)

        self.play(
            FadeIn(card_sup, shift=UP * 0.3),
            FadeIn(card_emb, shift=UP * 0.3),
            run_time=1.0,
        )
        self.play(FadeIn(card_fgw, shift=UP * 0.3), run_time=0.8)
        self.wait(HOLD_SHORT)

        # ── FGWEA card grows with gold border ─────────────────────────
        gold_border = SurroundingRectangle(
            card_fgw, color=ANCHOR_COLOR, buff=0.1,
            stroke_width=3,
        )
        self.play(
            card_fgw.animate.scale(1.08),
            Create(gold_border),
            run_time=0.8,
        )
        self.wait(HOLD_SHORT)

        # ── Transition to takeaway ────────────────────────────────────
        # NARRATION: The lesson... when matching structured objects,
        # compare the structure, not just the features.
        self.play(
            FadeOut(card_sup), FadeOut(card_emb),
            FadeOut(card_fgw), FadeOut(gold_border),
            run_time=0.8,
        )

        takeaway = safe_text(
            "When matching structured objects,",
            font_size=BODY_SIZE, color=WHITE,
        )
        takeaway2 = safe_text(
            "compare the structure, not just the features.",
            font_size=BODY_SIZE, color=STRUCTURE_COLOR,
        )
        takeaway_group = VGroup(takeaway, takeaway2).arrange(DOWN, buff=0.4)
        takeaway_group.move_to(UP * 0.3)

        self.play(Write(takeaway), run_time=1.0)
        self.play(Write(takeaway2), run_time=1.0)
        self.wait(HOLD_SHORT)

        # ── Attribution ───────────────────────────────────────────────
        attrib = bottom_note("Tang et al., ACL 2023")
        self.play(Write(attrib), run_time=0.6)
        self.wait(HOLD_MEDIUM)

        # ── Cleanup ───────────────────────────────────────────────────
        fade_all(self, title, takeaway_group, attrib)
