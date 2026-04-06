import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *

import numpy as np


class ResultsScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR

        # ------------------------------------------------------------------ #
        # 1. Title
        # ------------------------------------------------------------------ #
        title = section_title("Results", color=MUTATION_YELLOW)
        self.play(Write(title))
        self.wait(HOLD_SHORT)

        # ------------------------------------------------------------------ #
        # 2. Axes -- chart occupies center-lower portion of frame
        # ------------------------------------------------------------------ #
        axes = Axes(
            x_range=[0, 1000, 200],
            y_range=[0, 450, 100],
            x_length=8.5,
            y_length=3.5,
            axis_config={"color": LABEL_GRAY, "stroke_width": 2},
            x_axis_config={"include_tip": True, "tip_length": 0.2},
            y_axis_config={"include_tip": True, "tip_length": 0.2},
        )
        # Shift slightly down to leave room for title and legend
        axes.shift(DOWN * 0.45 + RIGHT * 0.2)

        x_label = safe_text(
            "Instructions (thousands)", font_size=SMALL_SIZE, color=LABEL_GRAY,
            max_width=4.5,
        )
        x_label.next_to(axes.x_axis, DOWN, buff=0.35)

        y_label = safe_text(
            "Coverage Points (K)", font_size=SMALL_SIZE, color=LABEL_GRAY,
            max_width=3.0,
        )
        y_label.rotate(PI / 2)
        y_label.next_to(axes.y_axis, LEFT, buff=0.35)

        self.play(Create(axes), Write(x_label), Write(y_label))
        self.wait(0.3)

        # ------------------------------------------------------------------ #
        # 3. Three coverage curves
        #
        # Data is scaled so axes x=0..1000, y=0..450.
        # Random:     fast rise, plateau ~350K; 350*(1-exp(-x/80))
        # DifuzzRTL:  plateau ~404K around x=600-1000; 404*(1-exp(-x/180))
        # TheHuzz:    crosses 404K at x~300, keeps rising to ~430K;
        #             420*(1-exp(-x/130)) + 0.018*x  capped at graph edge
        #
        # All functions evaluated over [0,1000].
        # ------------------------------------------------------------------ #

        def random_fn(x):
            return 350 * (1 - np.exp(-x / 80))

        def difuzz_fn(x):
            return 404 * (1 - np.exp(-x / 180))

        def huzz_fn(x):
            # Rises faster, crosses difuzz plateau early, keeps growing
            return min(420 * (1 - np.exp(-x / 130)) + 0.018 * x, 445)

        curve_random = axes.plot(
            random_fn,
            x_range=[0, 1000],
            color=DIM_GRAY,
            stroke_width=2.5,
        )
        # Dashed random
        curve_random_dashed = DashedVMobject(curve_random, num_dashes=40)

        curve_difuzz = axes.plot(
            difuzz_fn,
            x_range=[0, 1000],
            color=CHIP_BLUE,
            stroke_width=2.5,
        )
        curve_difuzz_dashed = DashedVMobject(curve_difuzz, num_dashes=40)

        curve_huzz = axes.plot(
            huzz_fn,
            x_range=[0, 1000],
            color=BUG_RED,
            stroke_width=4.5,
        )

        # ------------------------------------------------------------------ #
        # 4. Legend -- upper left, inside axes region
        # ------------------------------------------------------------------ #
        legend_x = axes.get_left()[0] + 0.3
        legend_y = axes.get_top()[1] - 0.25

        def legend_entry(label: str, color: str, dashed: bool = False) -> VGroup:
            if dashed:
                line = DashedLine(LEFT * 0.4, RIGHT * 0.4, color=color,
                                  stroke_width=2.5, dash_length=0.07)
            else:
                line = Line(LEFT * 0.4, RIGHT * 0.4, color=color, stroke_width=4.5)
            txt = safe_text(label, font_size=SMALL_SIZE, color=color, max_width=3.5)
            txt.next_to(line, RIGHT, buff=0.15)
            return VGroup(line, txt)

        leg_random = legend_entry("Random", DIM_GRAY, dashed=True)
        leg_difuzz = legend_entry("DifuzzRTL", CHIP_BLUE, dashed=True)
        leg_huzz   = legend_entry("TheHuzz", BUG_RED, dashed=False)

        # Stack entries vertically
        leg_difuzz.next_to(leg_random, DOWN, buff=0.18, aligned_edge=LEFT)
        leg_huzz.next_to(leg_difuzz, DOWN, buff=0.18, aligned_edge=LEFT)

        legend = VGroup(leg_random, leg_difuzz, leg_huzz)
        legend.move_to([legend_x + legend.width / 2, legend_y - legend.height / 2, 0])

        legend_bg = SurroundingRectangle(
            legend,
            color=LABEL_GRAY,
            fill_color=BG_COLOR,
            fill_opacity=0.75,
            stroke_width=1,
            buff=0.15,
            corner_radius=0.1,
        )

        # ------------------------------------------------------------------ #
        # 5. Animate curves left-to-right, one at a time
        # ------------------------------------------------------------------ #
        self.play(Create(curve_random_dashed), run_time=1.5)
        self.play(FadeIn(legend_bg), FadeIn(leg_random))
        self.wait(0.2)

        self.play(Create(curve_difuzz_dashed), run_time=1.5)
        self.play(FadeIn(leg_difuzz))
        self.wait(0.2)

        self.play(Create(curve_huzz), run_time=2.0)
        self.play(FadeIn(leg_huzz))
        self.wait(HOLD_SHORT)

        # ------------------------------------------------------------------ #
        # 6. Annotation: "3.33x faster" arrow
        #    Point where TheHuzz reaches ~404K -> x~300, y=404
        #    Point where DifuzzRTL reaches ~404K -> x~1000, y=404
        # ------------------------------------------------------------------ #
        # axes.c2p converts data coords to scene coords
        huzz_cross_point = axes.c2p(300, 404)
        difuzz_cross_point = axes.c2p(800, 404)

        annot_dot = Dot(huzz_cross_point, color=BUG_RED, radius=0.09)

        # Horizontal comparison line at y=404
        compare_line = DashedLine(
            axes.c2p(0, 404),
            axes.c2p(1000, 404),
            color=MUTATION_YELLOW,
            stroke_width=1.5,
            dash_length=0.08,
        )

        annot_label = safe_text("3.33x faster", font_size=LABEL_SIZE,
                                color=MUTATION_YELLOW, max_width=2.8)
        # Position label above and to the right of the crossing dot
        annot_label.move_to(huzz_cross_point + UP * 0.7 + RIGHT * 0.6)

        annot_arrow = Arrow(
            annot_label.get_bottom() + DOWN * 0.05,
            huzz_cross_point + UP * 0.12,
            buff=0.05,
            color=MUTATION_YELLOW,
            stroke_width=2,
            max_tip_length_to_length_ratio=0.2,
        )

        self.play(Create(compare_line), run_time=0.8)
        self.play(FadeIn(annot_dot, scale=1.4))
        self.play(Write(annot_label), Create(annot_arrow))
        self.wait(HOLD_MEDIUM)

        # ------------------------------------------------------------------ #
        # 7. Bottom note for Phase 1
        # ------------------------------------------------------------------ #
        note_chart = bottom_note(
            "3.33x faster than DifuzzRTL, 1.98x faster than random regression"
        )
        self.play(Write(note_chart))
        self.wait(HOLD_LONG)

        # ------------------------------------------------------------------ #
        # 8. FadeOut Phase 1 (chart + annotation + note)
        # ------------------------------------------------------------------ #
        phase1_objects = [
            title, axes, x_label, y_label,
            curve_random_dashed, curve_difuzz_dashed, curve_huzz,
            legend_bg, legend,
            compare_line, annot_dot, annot_label, annot_arrow,
            note_chart,
        ]
        self.play(*[FadeOut(obj) for obj in phase1_objects], run_time=0.9)
        self.wait(0.3)

        # ------------------------------------------------------------------ #
        # 9. Phase 2 -- Bug summary: 4 processor cards in a row
        # ------------------------------------------------------------------ #
        title2 = section_title("Bugs Found", color=BUG_RED)
        self.play(Write(title2))
        self.wait(0.3)

        PROCESSORS = [
            ("Ariane\n4 bugs",  CHIP_BLUE),
            ("mor1kx\n3 bugs",  COVERAGE_TEAL),
            ("or1200\n3 bugs",  GOLDEN_GREEN),
            ("Rocket\n1 bug",   OPTIMIZER_PURPLE),
        ]

        CARD_W = 2.2
        CARD_H = 1.5
        CARD_Y = 0.5
        # 4 cards, evenly spaced across the frame
        # Each card half-width = 1.1; rightmost edge = 4.1+1.1 = 5.2 < 5.5
        CARD_XS = [-4.1, -1.4, 1.4, 4.1]

        def processor_card(label: str, color: str, cx: float, cy: float) -> VGroup:
            rect = RoundedRectangle(
                width=CARD_W,
                height=CARD_H,
                corner_radius=0.2,
                color=color,
                fill_color=color,
                fill_opacity=0.18,
                stroke_width=2.5,
            )
            rect.move_to([cx, cy, 0])
            lbl = safe_text(label, font_size=LABEL_SIZE, color=color,
                            max_width=CARD_W - 0.35)
            lbl.move_to(rect)
            return VGroup(rect, lbl)

        cards = [
            processor_card(label, color, cx, CARD_Y)
            for (label, color), cx in zip(PROCESSORS, CARD_XS)
        ]

        self.play(LaggedStart(*[FadeIn(c, scale=0.85) for c in cards], lag_ratio=0.15))
        self.wait(HOLD_SHORT)

        # ------------------------------------------------------------------ #
        # 10. Summary text below cards
        # ------------------------------------------------------------------ #
        summary = safe_text(
            "8 new + 3 known = 11 total  |  5 CVEs  |  2 exploits",
            font_size=BODY_SIZE,
            color=WHITE,
            max_width=11.5,
        )
        summary.move_to([0, CARD_Y - CARD_H / 2 - 0.65, 0])

        self.play(FadeIn(summary, shift=UP * 0.2))
        self.wait(HOLD_MEDIUM)

        # ------------------------------------------------------------------ #
        # 11. Bottom note for Phase 2
        # ------------------------------------------------------------------ #
        note_bugs = bottom_note(
            "3.33x faster than DifuzzRTL, 1.98x faster than random regression"
        )
        self.play(Write(note_bugs))
        self.wait(HOLD_LONG)

        # ------------------------------------------------------------------ #
        # 12. FadeOut all
        # ------------------------------------------------------------------ #
        all_objects = [title2, summary, note_bugs] + cards
        self.play(*[FadeOut(obj) for obj in all_objects], run_time=0.9)
        self.wait(0.3)
