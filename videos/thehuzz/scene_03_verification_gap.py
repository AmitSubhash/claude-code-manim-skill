import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *
from utils.icons import branch_tree_icon, magnifying_glass_icon, dual_rect_icon

import random


class VerificationGapScene(Scene):
    """Scene 3: The Verification Gap -- ~90 seconds.

    Phase 1: Three limitation cards (formal verification, manual review, prior
    fuzzers) with red X marks, then fade out.
    Phase 2: 10x8 coverage dot grid showing ~35% explored hardware behavior.
    Phase 3: Story bridge -- "What if we had an answer key?"
    """

    def construct(self) -> None:
        self.camera.background_color = BG_COLOR
        random.seed(42)

        self._phase_cards()
        self._phase_coverage_grid()
        story_bridge(self, "What if we had an answer key?")

    # ---------------------------------------------------------------------- #
    # Phase 1: Limitation cards                                               #
    # ---------------------------------------------------------------------- #

    def _phase_cards(self) -> None:
        title = safe_text(
            "The Verification Gap",
            font_size=TITLE_SIZE,
            color=WHITE,
        ).move_to([0, TITLE_Y, 0])

        self.play(Write(title))
        self.wait(HOLD_SHORT)

        card_formal = self._make_card_formal()
        card_manual = self._make_card_manual()
        card_fuzzer = self._make_card_fuzzer()

        cards = VGroup(card_formal, card_manual, card_fuzzer)
        cards.arrange(RIGHT, buff=0.45)
        cards.move_to([0, -0.3, 0])
        if cards.width > 13.0:
            cards.scale_to_fit_width(13.0)

        self.play(
            LaggedStart(
                *[FadeIn(c, shift=UP * 0.2) for c in cards],
                lag_ratio=0.35,
            )
        )
        self.wait(HOLD_MEDIUM)

        # Red X marks appear one by one at the bottom of each card
        x_marks = VGroup(*[
            self._make_red_x().move_to(c.get_bottom() + UP * 0.55)
            for c in cards
        ])
        for x_mark in x_marks:
            self.play(Create(x_mark), run_time=0.5)
            self.wait(0.3)

        self.wait(HOLD_MEDIUM)

        self.play(FadeOut(title), FadeOut(cards), FadeOut(x_marks))

    # ---------------------------------------------------------------------- #
    # Phase 2: Coverage dot grid                                              #
    # ---------------------------------------------------------------------- #

    def _phase_coverage_grid(self) -> None:
        grid_title = safe_text(
            "Hardware Behavior Coverage",
            font_size=HEADING_SIZE,
            color=WHITE,
        ).move_to([0, TITLE_Y, 0])

        self.play(Write(grid_title))

        dots = self._build_dot_grid()
        dots.move_to([0, 0.3, 0])

        self.play(
            LaggedStart(
                *[Create(d) for d in dots],
                lag_ratio=0.015,
                run_time=2.5,
            )
        )
        self.wait(HOLD_SHORT)

        legend = self._build_legend()
        legend.next_to(dots, DOWN, buff=0.5)
        self.play(FadeIn(legend))
        self.wait(HOLD_SHORT)

        note = bottom_note(
            "Large regions of hardware behavior remain unexplored"
        )
        self.play(FadeIn(note))
        self.wait(HOLD_LONG)

        self.play(FadeOut(grid_title), FadeOut(dots), FadeOut(legend), FadeOut(note))

    # ---------------------------------------------------------------------- #
    # Card builders                                                           #
    # ---------------------------------------------------------------------- #

    def _make_card(
        self,
        title_text: str,
        title_color: str,
        stat_text: str,
        flaw_text: str,
        icon_mobject: VMobject,
    ) -> VGroup:
        """Rounded-rectangle card with title, icon, stat, and flaw label."""
        rect = RoundedRectangle(
            width=3.2,
            height=3.0,
            corner_radius=0.2,
            color=title_color,
            fill_color=title_color,
            fill_opacity=DIM_OPACITY,
            stroke_width=2,
        )

        card_title = safe_text(
            title_text, font_size=LABEL_SIZE, color=title_color, max_width=2.8
        )
        card_title.move_to(rect.get_top() + DOWN * 0.35)

        icon_mobject.set_height(0.75)
        icon_mobject.move_to(rect.get_center() + UP * 0.45)

        stat = safe_text(stat_text, font_size=BODY_SIZE, color=WHITE, max_width=2.8)
        stat.move_to(rect.get_center() + DOWN * 0.3)

        flaw = safe_text(flaw_text, font_size=SMALL_SIZE, color=LABEL_GRAY, max_width=2.8)
        flaw.move_to(rect.get_bottom() + UP * 0.55)

        return VGroup(rect, card_title, icon_mobject, stat, flaw)

    def _make_card_formal(self) -> VGroup:
        return self._make_card(
            title_text="Formal Verification",
            title_color=CHIP_BLUE,
            stat_text="10^58 states",
            flaw_text="State explosion",
            icon_mobject=branch_tree_icon(color=BUG_RED),
        )

    def _make_card_manual(self) -> VGroup:
        return self._make_card(
            title_text="Manual Review",
            title_color=MUTATION_YELLOW,
            stat_text="48% detected",
            flaw_text="Misses half",
            icon_mobject=magnifying_glass_icon(color=MUTATION_YELLOW),
        )

    def _make_card_fuzzer(self) -> VGroup:
        return self._make_card(
            title_text="Prior Fuzzers",
            title_color=OPTIMIZER_PURPLE,
            stat_text="Limited metrics",
            flaw_text="Blind spots",
            icon_mobject=dual_rect_icon(color=OPTIMIZER_PURPLE),
        )

    # ---------------------------------------------------------------------- #
    # Red X mark                                                              #
    # ---------------------------------------------------------------------- #

    @staticmethod
    def _make_red_x() -> VGroup:
        """Two crossing lines forming a red X."""
        size = 0.22
        line1 = Line(
            LEFT * size + DOWN * size,
            RIGHT * size + UP * size,
            color=BUG_RED,
            stroke_width=4,
        )
        line2 = Line(
            LEFT * size + UP * size,
            RIGHT * size + DOWN * size,
            color=BUG_RED,
            stroke_width=4,
        )
        return VGroup(line1, line2)

    # ---------------------------------------------------------------------- #
    # Dot grid                                                                #
    # ---------------------------------------------------------------------- #

    def _build_dot_grid(self) -> VGroup:
        """Build 10x8 dot grid: ~35% teal (explored), ~65% dim.

        Returns
        -------
        VGroup
            80 Dot mobjects in row-major order.
        """
        cols, rows = 10, 8
        total = cols * rows       # 80
        n_explored = 28           # ~35 %
        explored = set(random.sample(range(total), n_explored))

        spacing_x, spacing_y = 0.9, 0.65
        all_dots = []
        for row in range(rows):
            for col in range(cols):
                idx = row * cols + col
                if idx in explored:
                    color, opacity = COVERAGE_TEAL, 1.0
                else:
                    color, opacity = DIM_GRAY, 0.35
                dot = Dot(
                    point=[
                        (col - (cols - 1) / 2) * spacing_x,
                        ((rows - 1) / 2 - row) * spacing_y,
                        0,
                    ],
                    radius=0.16,
                    color=color,
                    fill_opacity=opacity,
                )
                all_dots.append(dot)
        return VGroup(*all_dots)

    # ---------------------------------------------------------------------- #
    # Legend                                                                  #
    # ---------------------------------------------------------------------- #

    @staticmethod
    def _build_legend() -> VGroup:
        """Two-entry legend: teal Explored, gray Unexplored."""
        dot_exp = Dot(radius=0.12, color=COVERAGE_TEAL, fill_opacity=1.0)
        lbl_exp = safe_text("Explored", font_size=SMALL_SIZE, color=COVERAGE_TEAL)
        lbl_exp.next_to(dot_exp, RIGHT, buff=0.15)
        entry_exp = VGroup(dot_exp, lbl_exp)

        dot_unexp = Dot(radius=0.12, color=DIM_GRAY, fill_opacity=0.35)
        lbl_unexp = safe_text("Unexplored", font_size=SMALL_SIZE, color=LABEL_GRAY)
        lbl_unexp.next_to(dot_unexp, RIGHT, buff=0.15)
        entry_unexp = VGroup(dot_unexp, lbl_unexp)

        legend = VGroup(entry_exp, entry_unexp)
        legend.arrange(RIGHT, buff=0.7)
        return legend
