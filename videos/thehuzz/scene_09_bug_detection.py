import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


class BugDetectionScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR

        # ------------------------------------------------------------------ #
        # 1. Title
        # ------------------------------------------------------------------ #
        title = section_title("Bug Detection: Trace Comparison")
        self.play(Write(title))
        self.wait(HOLD_SHORT)

        # ------------------------------------------------------------------ #
        # 2. Vertical divider
        # ------------------------------------------------------------------ #
        divider = DashedLine(
            start=[0, 2.4, 0],
            end=[0, -2.8, 0],
            color=LABEL_GRAY,
            dash_length=0.15,
            dashed_ratio=0.5,
            stroke_width=1.5,
        )
        self.play(Create(divider))

        # ------------------------------------------------------------------ #
        # 3. Column headers
        # ------------------------------------------------------------------ #
        left_header = safe_text("RTL Trace (DUT)", font_size=LABEL_SIZE, color=CHIP_BLUE)
        left_header.move_to([-3.2, 2.0, 0])

        right_header = safe_text("Golden Model Trace", font_size=LABEL_SIZE, color=GOLDEN_GREEN)
        right_header.move_to([3.2, 2.0, 0])

        self.play(Write(left_header), Write(right_header))
        self.wait(0.3)

        # ------------------------------------------------------------------ #
        # 4. Row data definitions
        # ------------------------------------------------------------------ #
        rows_data = [
            {
                "left":  "ADD r1,r2,r3 -> r3=7",
                "right": "ADD r1,r2,r3 -> r3=7",
                "match": True,
            },
            {
                "left":  "SUB r4,r5,r6 -> r6=3",
                "right": "SUB r4,r5,r6 -> r6=3",
                "match": True,
            },
            {
                "left":  "OR r1,r2,r3 -> r3=5",
                "right": "OR r1,r2,r3 -> r3=5",
                "match": True,
            },
            {
                "left":  "SUB r7,r8,r9 -> carry=0",
                "right": "SUB r7,r8,r9 -> carry=1",
                "match": False,
            },
        ]

        row_start_y = 1.1
        row_gap = 0.72

        left_texts = []
        right_texts = []
        indicators = []
        row_groups = []

        for i, row in enumerate(rows_data):
            y = row_start_y - i * row_gap

            lt = safe_text(row["left"], font_size=SMALL_SIZE, color=WHITE, max_width=4.8)
            lt.move_to([-3.2, y, 0])

            rt = safe_text(row["right"], font_size=SMALL_SIZE, color=WHITE, max_width=4.8)
            rt.move_to([3.2, y, 0])

            if row["match"]:
                dot = Circle(radius=0.18, color=SAFE_GREEN, fill_opacity=0.85, stroke_width=2)
                dot.move_to([0, y, 0])
                check = safe_text("v", font_size=SMALL_SIZE, color=WHITE, max_width=0.3)
                check.move_to(dot)
                ind = VGroup(dot, check)
            else:
                dot = Circle(radius=0.18, color=BUG_RED, fill_opacity=0.85, stroke_width=2)
                dot.move_to([0, y, 0])
                cross = safe_text("X", font_size=SMALL_SIZE, color=WHITE, max_width=0.3)
                cross.move_to(dot)
                ind = VGroup(dot, cross)

            left_texts.append(lt)
            right_texts.append(rt)
            indicators.append(ind)
            row_groups.append(VGroup(lt, rt, ind))

        # ------------------------------------------------------------------ #
        # 5. Animate rows 1-3 (matching)
        # ------------------------------------------------------------------ #
        for i in range(3):
            self.play(
                Write(left_texts[i]),
                Write(right_texts[i]),
                run_time=0.6,
            )
            self.play(Create(indicators[i]), run_time=0.4)
            self.wait(0.25)

        # ------------------------------------------------------------------ #
        # 6. Row 4: mismatch with red highlight rectangle
        # ------------------------------------------------------------------ #
        y_mismatch = row_start_y - 3 * row_gap

        mismatch_rect = Rectangle(
            width=12.5,
            height=0.62,
            color=BUG_RED,
            fill_opacity=0.18,
            stroke_width=2,
        )
        mismatch_rect.move_to([0, y_mismatch, 0])

        left_texts[3].set_color(CHIP_BLUE)
        right_texts[3].set_color(GOLDEN_GREEN)

        self.play(
            Write(left_texts[3]),
            Write(right_texts[3]),
            Create(mismatch_rect),
            run_time=0.7,
        )
        self.play(Create(indicators[3]), run_time=0.4)
        self.wait(0.3)

        # Flash the mismatch
        self.play(
            Indicate(left_texts[3], color=BUG_RED, scale_factor=1.12),
            Indicate(right_texts[3], color=BUG_RED, scale_factor=1.12),
            run_time=0.7,
        )
        self.wait(HOLD_SHORT)

        # ------------------------------------------------------------------ #
        # 7. Phase 2 transition: fade out rows 1-3, headers, divider
        # ------------------------------------------------------------------ #
        self.play(
            FadeOut(left_header),
            FadeOut(right_header),
            FadeOut(divider),
            *[FadeOut(left_texts[i]) for i in range(3)],
            *[FadeOut(right_texts[i]) for i in range(3)],
            *[FadeOut(indicators[i]) for i in range(3)],
            FadeOut(title),
            run_time=0.8,
        )

        # Move mismatch row to center and enlarge
        mismatch_group = VGroup(
            left_texts[3],
            right_texts[3],
            indicators[3],
            mismatch_rect,
        )

        self.play(
            mismatch_group.animate.move_to([0, 1.4, 0]).scale(1.35),
            run_time=0.8,
        )
        self.wait(0.3)

        # ------------------------------------------------------------------ #
        # 8. Enlarged detail: DUT carry label with strikethrough effect
        # ------------------------------------------------------------------ #
        dut_carry_label = safe_text(
            "DUT: carry = 0",
            font_size=LABEL_SIZE,
            color=CHIP_BLUE,
            max_width=5.5,
        )
        dut_carry_label.move_to([-2.8, 0.2, 0])

        # Strikethrough line over the DUT value
        strike = Line(
            dut_carry_label.get_left() + [-0.1, 0, 0],
            dut_carry_label.get_right() + [0.1, 0, 0],
            color=BUG_RED,
            stroke_width=3,
        )

        golden_carry_label = safe_text(
            "Golden Model: carry = 1",
            font_size=LABEL_SIZE,
            color=GOLDEN_GREEN,
            max_width=5.5,
        )
        golden_carry_label.move_to([2.8, 0.2, 0])

        checkmark = safe_text("v", font_size=HEADING_SIZE, color=GOLDEN_GREEN, max_width=0.6)
        checkmark.next_to(golden_carry_label, RIGHT, buff=0.2)

        self.play(
            Write(dut_carry_label),
            Write(golden_carry_label),
            run_time=0.7,
        )
        self.play(
            Create(strike),
            Write(checkmark),
            run_time=0.5,
        )
        self.wait(0.4)

        # ------------------------------------------------------------------ #
        # 9. Arrow pointing down to bug description
        # ------------------------------------------------------------------ #
        bug_arrow = Arrow(
            start=[0, -0.25, 0],
            end=[0, -0.85, 0],
            color=BUG_RED,
            stroke_width=3,
            max_tip_length_to_length_ratio=0.25,
        )
        self.play(Create(bug_arrow), run_time=0.4)

        bug_text = safe_text(
            "Bug B5: Carry flag not updated\ncorrectly for subtract",
            font_size=LABEL_SIZE,
            color=BUG_RED,
            max_width=7.0,
        )
        bug_text.move_to([0, -1.45, 0])

        self.play(Write(bug_text), run_time=0.7)
        self.wait(0.4)

        # ------------------------------------------------------------------ #
        # 10. CVE badge
        # ------------------------------------------------------------------ #
        cve_rect = RoundedRectangle(
            width=2.8,
            height=0.52,
            corner_radius=0.12,
            color=BUG_RED,
            fill_opacity=0.25,
            stroke_width=2,
        )
        cve_rect.move_to([0, -2.35, 0])

        cve_label = safe_text("CVE-2021-41612", font_size=SMALL_SIZE, color=BUG_RED, max_width=2.6)
        cve_label.move_to(cve_rect)

        cve_badge = VGroup(cve_rect, cve_label)

        self.play(Create(cve_rect), Write(cve_label), run_time=0.6)
        self.wait(0.4)

        self.play(
            Indicate(cve_badge, color=BUG_RED, scale_factor=1.1),
            run_time=0.6,
        )
        self.wait(0.4)

        # ------------------------------------------------------------------ #
        # 11. Bottom note
        # ------------------------------------------------------------------ #
        note = bottom_note("Found in only 20 instructions")
        self.play(Write(note))
        self.wait(HOLD_LONG)

        # ------------------------------------------------------------------ #
        # 12. Final cleanup
        # ------------------------------------------------------------------ #
        self.play(
            FadeOut(mismatch_group),
            FadeOut(dut_carry_label),
            FadeOut(strike),
            FadeOut(golden_carry_label),
            FadeOut(checkmark),
            FadeOut(bug_arrow),
            FadeOut(bug_text),
            FadeOut(cve_badge),
            FadeOut(note),
            run_time=0.8,
        )
        self.wait(0.2)
