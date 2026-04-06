import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


class CoverageMetricsScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR

        # Metric definitions: (name, description)
        METRICS = [
            ("Statement",   "Every line of RTL code executed"),
            ("Branch",      "Both true/false paths tested"),
            ("Condition",   "Each sub-condition tested independently"),
            ("Expression",  "All combinational logic inputs tested"),
            ("Toggle",      "Every flip-flop toggles 0/1/z"),
            ("FSM",         "All state transitions covered"),
        ]

        # ------------------------------------------------------------------ #
        # 1. Title
        # ------------------------------------------------------------------ #
        title = section_title("Six Coverage Metrics", color=COVERAGE_TEAL)
        self.play(Write(title))
        self.wait(HOLD_SHORT)

        # ------------------------------------------------------------------ #
        # 2. Build 6 pill-shaped cards in a 2x3 grid
        #    Row 1 (y=0.8): Statement, Branch, Condition
        #    Row 2 (y=-0.5): Expression, Toggle, FSM
        # ------------------------------------------------------------------ #
        CARD_W = 2.8
        CARD_H = 0.85
        COL_XS = [-3.8, 0.0, 3.8]
        ROW_YS = [0.8, -0.5]

        cards = []   # list of VGroup (rect, label)
        positions = []

        for idx, (name, _) in enumerate(METRICS):
            row = idx // 3
            col = idx % 3
            cx = COL_XS[col]
            cy = ROW_YS[row]

            rect = RoundedRectangle(
                width=CARD_W, height=CARD_H, corner_radius=0.25,
                color=COVERAGE_TEAL, fill_color=COVERAGE_TEAL,
                fill_opacity=0.15, stroke_width=2.5,
            )
            label = safe_text(name, font_size=LABEL_SIZE, color=COVERAGE_TEAL,
                              max_width=CARD_W - 0.4)
            label.move_to(rect)
            card = VGroup(rect, label)
            card.move_to([cx, cy, 0])
            cards.append(card)
            positions.append((cx, cy))

        # Animate grid appearance
        self.play(LaggedStart(*[FadeIn(c, scale=0.85) for c in cards],
                              lag_ratio=0.15))
        self.wait(HOLD_MEDIUM)

        # ------------------------------------------------------------------ #
        # 3. Phase 2 -- Highlight each metric one at a time
        # ------------------------------------------------------------------ #
        for i, (name, desc) in enumerate(METRICS):
            # Dim all other cards
            dim_anims = []
            for j, card in enumerate(cards):
                if j != i:
                    dim_anims.append(card.animate.set_opacity(DIM_OPACITY))
                else:
                    # Highlight current: brighter fill + white border
                    dim_anims.append(
                        cards[i][0].animate.set_stroke(color=WHITE, width=3.5)
                        .set_fill(color=COVERAGE_TEAL, opacity=0.45)
                    )
                    dim_anims.append(
                        cards[i][1].animate.set_color(WHITE)
                    )
            self.play(*dim_anims, run_time=0.5)

            # Description text -- placed below the grid, centered
            desc_text = safe_text(desc, font_size=BODY_SIZE, color=WHITE,
                                  max_width=9.0)
            desc_text.move_to([0, -1.6, 0])
            self.play(FadeIn(desc_text, shift=UP * 0.2))
            self.wait(HOLD_MEDIUM)
            self.play(FadeOut(desc_text, shift=DOWN * 0.15))

            # Restore card to normal state
            restore_anims = [
                cards[i][0].animate.set_stroke(color=COVERAGE_TEAL, width=2.5)
                .set_fill(color=COVERAGE_TEAL, opacity=0.15),
                cards[i][1].animate.set_color(COVERAGE_TEAL),
            ]
            # Restore opacity of all dimmed cards
            for j, card in enumerate(cards):
                if j != i:
                    restore_anims.append(card.animate.set_opacity(1.0))
            self.play(*restore_anims, run_time=0.4)

        self.wait(HOLD_SHORT)

        # ------------------------------------------------------------------ #
        # 4. FadeOut title and metric grid before Phase 3
        # ------------------------------------------------------------------ #
        self.play(FadeOut(title), *[FadeOut(c) for c in cards])
        self.wait(0.3)

        # ------------------------------------------------------------------ #
        # 5. Phase 3 -- Dual bar-chart comparison
        #    LEFT: DifuzzRTL (2 short bars)
        #    RIGHT: TheHuzz  (6 tall bars)
        # ------------------------------------------------------------------ #

        # -- Column headers --
        difuzz_header = safe_text("DifuzzRTL", font_size=HEADING_SIZE,
                                  color=BUG_RED, max_width=4.0)
        difuzz_header.move_to([LEFT_X, 2.5, 0])

        huzz_header = safe_text("TheHuzz", font_size=HEADING_SIZE,
                                color=GOLDEN_GREEN, max_width=4.0)
        huzz_header.move_to([RIGHT_X, 2.5, 0])

        self.play(Write(difuzz_header), Write(huzz_header))
        self.wait(0.4)

        # -- Helper: build a bar --
        def make_bar(
            bar_width: float,
            bar_height: float,
            fill_color: str,
            label_str: str,
            base_y: float,
            center_x: float,
        ) -> VGroup:
            rect = Rectangle(
                width=bar_width, height=bar_height,
                color=fill_color, fill_color=fill_color,
                fill_opacity=0.75, stroke_width=1.5,
            )
            # Anchor bottom of bar at base_y
            rect.move_to([center_x, base_y + bar_height / 2, 0])
            lbl = safe_text(label_str, font_size=SMALL_SIZE,
                            color=LABEL_GRAY, max_width=bar_width + 0.3)
            lbl.next_to(rect, DOWN, buff=0.18)
            return VGroup(rect, lbl)

        BASE_Y = -2.6
        BAR_W  = 0.55

        # DifuzzRTL: 2 metrics (MUX control + CRs), short bars
        difuzz_bar_data = [
            ("1 MUX",  0.5),
            ("2 CRs",  0.65),
        ]
        difuzz_xs = [-4.3, -3.5]
        difuzz_bars = [
            make_bar(BAR_W, h, BUG_RED, name, BASE_Y, x)
            for (name, h), x in zip(difuzz_bar_data, difuzz_xs)
        ]

        # TheHuzz: 6 metrics, tall bars
        huzz_bar_data = [
            ("Stmt",   2.0),
            ("Brnch",  2.15),
            ("Cond",   2.25),
            ("Expr",   2.1),
            ("Tgl",    1.95),
            ("FSM",    2.3),
        ]
        huzz_xs = [2.0, 2.65, 3.3, 3.95, 4.6, 5.25]
        huzz_bars = [
            make_bar(BAR_W, h, COVERAGE_TEAL, name, BASE_Y, x)
            for (name, h), x in zip(huzz_bar_data, huzz_xs)
        ]

        # Baseline
        difuzz_baseline = Line(
            start=[-5.0, BASE_Y, 0],
            end=[-2.8, BASE_Y, 0],
            color=LABEL_GRAY, stroke_width=2,
        )
        huzz_baseline = Line(
            start=[1.4, BASE_Y, 0],
            end=[5.8, BASE_Y, 0],
            color=LABEL_GRAY, stroke_width=2,
        )

        self.play(Create(difuzz_baseline), Create(huzz_baseline))

        # Animate DifuzzRTL bars growing from baseline
        self.play(LaggedStart(
            *[GrowFromEdge(b[0], DOWN) for b in difuzz_bars],
            lag_ratio=0.25,
        ))
        self.play(LaggedStart(
            *[Write(b[1]) for b in difuzz_bars],
            lag_ratio=0.2,
        ))
        self.wait(0.4)

        # Animate TheHuzz bars growing -- more dramatic
        self.play(LaggedStart(
            *[GrowFromEdge(b[0], DOWN) for b in huzz_bars],
            lag_ratio=0.12,
        ))
        self.play(LaggedStart(
            *[Write(b[1]) for b in huzz_bars],
            lag_ratio=0.1,
        ))
        self.wait(HOLD_SHORT)

        # Coverage count annotations
        difuzz_count = safe_text("2 types", font_size=LABEL_SIZE,
                                 color=BUG_RED, max_width=2.5)
        difuzz_count.move_to([LEFT_X, 1.5, 0])

        huzz_count = safe_text("6 types", font_size=LABEL_SIZE,
                               color=GOLDEN_GREEN, max_width=2.5)
        huzz_count.move_to([RIGHT_X, 1.5, 0])

        self.play(FadeIn(difuzz_count, scale=0.8), FadeIn(huzz_count, scale=0.8))
        self.wait(HOLD_MEDIUM)

        # ------------------------------------------------------------------ #
        # 6. Bottom note
        # ------------------------------------------------------------------ #
        note = bottom_note("More coverage types = more bugs found")
        self.play(Write(note))
        self.wait(HOLD_LONG)

        # ------------------------------------------------------------------ #
        # 7. Cleanup -- FadeOut all
        # ------------------------------------------------------------------ #
        all_objects = (
            [difuzz_header, huzz_header,
             difuzz_baseline, huzz_baseline,
             difuzz_count, huzz_count, note]
            + difuzz_bars
            + huzz_bars
        )
        self.play(*[FadeOut(obj) for obj in all_objects])
        self.wait(0.3)
