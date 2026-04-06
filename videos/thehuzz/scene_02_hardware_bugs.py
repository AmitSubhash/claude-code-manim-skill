import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


class WhyHardwareBugsScene(Scene):
    """Scene 2: Software Bugs vs Hardware Bugs (~60s).

    DUAL_PANEL layout. Left shows software bug lifecycle (patchable).
    Right shows hardware bug reality (permanent, billions affected).
    Bottom note cites real-world examples.
    """

    def construct(self) -> None:
        self.camera.background_color = BG_COLOR

        # ------------------------------------------------------------------ #
        # 1. Title
        # ------------------------------------------------------------------ #
        title = safe_text(
            "Software Bugs vs Hardware Bugs",
            font_size=TITLE_SIZE,
            color=WHITE,
        ).move_to(UP * TITLE_Y)
        self.play(Write(title))
        self.wait(HOLD_SHORT)

        # ------------------------------------------------------------------ #
        # 2. Divider line
        # ------------------------------------------------------------------ #
        divider = DashedLine(
            start=UP * 2.8,
            end=DOWN * 2.8,
            color=LABEL_GRAY,
            stroke_width=1.5,
            dash_length=0.15,
        ).move_to(ORIGIN)
        self.play(Create(divider))

        # ------------------------------------------------------------------ #
        # 3. Panel headers
        # ------------------------------------------------------------------ #
        left_header = safe_text(
            "Software Bug",
            font_size=HEADING_SIZE,
            color=SAFE_GREEN,
        ).move_to(UP * 2.0 + LEFT * 3.2)

        right_header = safe_text(
            "Hardware Bug",
            font_size=HEADING_SIZE,
            color=BUG_RED,
        ).move_to(UP * 2.0 + RIGHT * 3.2)

        self.play(
            Write(left_header),
            Write(right_header),
        )
        self.wait(HOLD_SHORT * 0.5)

        # ------------------------------------------------------------------ #
        # 4. LEFT PANEL: Code file icon
        # ------------------------------------------------------------------ #
        file_rect = Rectangle(
            width=1.5, height=2.0,
            color=SAFE_GREEN,
            fill_opacity=0.15,
            stroke_width=2,
        ).move_to(UP * 0.6 + LEFT * 3.8)

        # Dog-ear fold on top-right corner of file icon
        corner_size = 0.3
        fold_pts = [
            file_rect.get_corner(UR) + LEFT * corner_size,
            file_rect.get_corner(UR),
            file_rect.get_corner(UR) + DOWN * corner_size,
        ]
        fold = Polygon(*fold_pts, color=SAFE_GREEN, stroke_width=1.5,
                       fill_opacity=0.35, fill_color=SAFE_GREEN)

        # Code lines inside the file
        code_lines = VGroup(*[
            Line(
                start=file_rect.get_left() + RIGHT * 0.2 + DOWN * (0.3 - 0.18 * i),
                end=file_rect.get_left() + RIGHT * (1.1 - 0.25 * (i % 2)) + DOWN * (0.3 - 0.18 * i),
                color=LABEL_GRAY,
                stroke_width=1.5,
            )
            for i in range(5)
        ])
        file_icon = VGroup(file_rect, fold, code_lines)

        self.play(Create(file_icon))
        self.wait(HOLD_SHORT * 0.5)

        # Bug circle on the file
        bug_circle_l = Circle(
            radius=0.28,
            color=BUG_RED,
            fill_opacity=0.85,
        ).move_to(file_rect.get_center() + RIGHT * 0.1 + UP * 0.1)
        bug_label_l = safe_text("BUG", font_size=SMALL_SIZE, color=WHITE)
        bug_label_l.move_to(bug_circle_l)
        bug_group_l = VGroup(bug_circle_l, bug_label_l)

        self.play(FadeIn(bug_group_l, scale=0.4))
        self.wait(HOLD_SHORT * 0.5)

        # PATCH rectangle slides over the bug from the left
        patch_rect = Rectangle(
            width=0.9, height=0.56,
            color=SAFE_GREEN,
            fill_opacity=0.85,
            stroke_width=2,
        ).move_to(bug_circle_l.get_center() + LEFT * 2.5)
        patch_label = safe_text("PATCH", font_size=SMALL_SIZE, color=WHITE)
        patch_label.move_to(patch_rect)
        patch_group = VGroup(patch_rect, patch_label)

        self.play(
            patch_group.animate.move_to(bug_circle_l.get_center()),
            run_time=0.9,
        )
        self.wait(HOLD_SHORT * 0.3)

        # Arrow pointing down + "Fixed in hours" label
        fix_arrow = Arrow(
            start=file_rect.get_bottom() + DOWN * 0.05,
            end=file_rect.get_bottom() + DOWN * 0.6,
            color=SAFE_GREEN,
            stroke_width=3,
            buff=0.0,
        )
        fix_label = safe_text("Fixed in hours", font_size=LABEL_SIZE, color=SAFE_GREEN)
        fix_label.next_to(fix_arrow, DOWN, buff=0.12)

        self.play(GrowArrow(fix_arrow), Write(fix_label))

        # Checkmark over the file
        check = safe_text("", font_size=HEADING_SIZE, color=SAFE_GREEN)
        check.move_to(file_rect.get_center())
        self.play(
            FadeOut(bug_group_l),
            FadeOut(patch_group),
            FadeIn(check),
        )
        self.wait(HOLD_MEDIUM * 0.5)

        # ------------------------------------------------------------------ #
        # 5. RIGHT PANEL: Chip icon
        # ------------------------------------------------------------------ #
        chip_body = RoundedRectangle(
            width=1.6, height=1.2,
            corner_radius=0.1,
            color=CHIP_BLUE,
            fill_opacity=0.2,
            stroke_width=2,
        ).move_to(UP * 0.7 + RIGHT * 3.2)

        # Chip pins (short lines on each side)
        pin_color = LABEL_GRAY
        pin_w = 2
        pins_top = VGroup(*[
            Line(
                chip_body.get_top() + LEFT * (0.5 - 0.25 * i) + UP * 0.0,
                chip_body.get_top() + LEFT * (0.5 - 0.25 * i) + UP * 0.2,
                color=pin_color, stroke_width=pin_w,
            )
            for i in range(5)
        ])
        pins_bottom = VGroup(*[
            Line(
                chip_body.get_bottom() + LEFT * (0.5 - 0.25 * i) + DOWN * 0.0,
                chip_body.get_bottom() + LEFT * (0.5 - 0.25 * i) + DOWN * 0.2,
                color=pin_color, stroke_width=pin_w,
            )
            for i in range(5)
        ])
        pins_left = VGroup(*[
            Line(
                chip_body.get_left() + DOWN * (0.2 - 0.2 * i) + LEFT * 0.0,
                chip_body.get_left() + DOWN * (0.2 - 0.2 * i) + LEFT * 0.2,
                color=pin_color, stroke_width=pin_w,
            )
            for i in range(3)
        ])
        pins_right = VGroup(*[
            Line(
                chip_body.get_right() + DOWN * (0.2 - 0.2 * i) + RIGHT * 0.0,
                chip_body.get_right() + DOWN * (0.2 - 0.2 * i) + RIGHT * 0.2,
                color=pin_color, stroke_width=pin_w,
            )
            for i in range(3)
        ])
        chip_label_inner = safe_text("CPU", font_size=SMALL_SIZE, color=CHIP_BLUE)
        chip_label_inner.move_to(chip_body)
        chip_icon = VGroup(chip_body, pins_top, pins_bottom, pins_left, pins_right, chip_label_inner)

        self.play(Create(chip_icon))
        self.wait(HOLD_SHORT * 0.5)

        # Bug circle on chip
        bug_circle_r = Circle(
            radius=0.28,
            color=BUG_RED,
            fill_opacity=0.85,
        ).move_to(chip_body.get_center() + RIGHT * 0.15 + UP * 0.05)
        bug_label_r = safe_text("BUG", font_size=SMALL_SIZE, color=WHITE)
        bug_label_r.move_to(bug_circle_r)
        bug_group_r = VGroup(bug_circle_r, bug_label_r)

        self.play(FadeIn(bug_group_r, scale=0.4))
        self.wait(HOLD_SHORT * 0.5)

        # Red X cross (no patch)
        x_line1 = Line(
            chip_body.get_center() + UL * 0.55,
            chip_body.get_center() + DR * 0.55,
            color=BUG_RED, stroke_width=5,
        )
        x_line2 = Line(
            chip_body.get_center() + UR * 0.55,
            chip_body.get_center() + DL * 0.55,
            color=BUG_RED, stroke_width=5,
        )
        cross = VGroup(x_line1, x_line2)

        self.play(Create(cross))
        self.wait(HOLD_SHORT * 0.3)

        # "PERMANENT" stamp
        permanent_text = safe_text(
            "PERMANENT",
            font_size=BODY_SIZE,
            color=BUG_RED,
        )
        permanent_text.move_to(chip_body.get_center() + DOWN * 1.1)

        # Red border rectangle around the word for stamp feel
        perm_border = Rectangle(
            width=permanent_text.width + 0.2,
            height=permanent_text.height + 0.15,
            color=BUG_RED,
            stroke_width=2.5,
            fill_opacity=0.0,
        ).move_to(permanent_text)
        perm_stamp = VGroup(perm_border, permanent_text)

        self.play(FadeIn(perm_stamp, scale=1.4))
        self.wait(HOLD_SHORT * 0.5)

        # 3 small chip copies spreading outward (billions affected)
        chip_copy_positions = [
            chip_body.get_center() + DOWN * 1.85 + LEFT * 0.9,
            chip_body.get_center() + DOWN * 1.85,
            chip_body.get_center() + DOWN * 1.85 + RIGHT * 0.9,
        ]
        small_chips = VGroup()
        for pos in chip_copy_positions:
            mini = RoundedRectangle(
                width=0.55, height=0.42,
                corner_radius=0.06,
                color=CHIP_BLUE,
                fill_opacity=0.6,
                stroke_width=1.5,
            ).move_to(pos)
            small_chips.add(mini)

        affected_label = safe_text(
            "Billions of chips affected",
            font_size=SMALL_SIZE,
            color=BUG_RED,
        ).next_to(small_chips, DOWN, buff=0.18)

        self.play(
            LaggedStart(*[FadeIn(c, scale=0.3) for c in small_chips], lag_ratio=0.25),
        )
        self.play(Write(affected_label))
        self.wait(HOLD_MEDIUM * 0.5)

        # ------------------------------------------------------------------ #
        # 6. Bottom note
        # ------------------------------------------------------------------ #
        note = bottom_note(
            "Intel Pentium FDIV: $475M recall.  Spectre/Meltdown: unfixable in deployed chips.",
            color=MUTATION_YELLOW,
        )
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(HOLD_LONG)

        # ------------------------------------------------------------------ #
        # 7. Final cleanup
        # ------------------------------------------------------------------ #
        all_objects = VGroup(
            title, divider,
            left_header, right_header,
            file_icon, check, fix_arrow, fix_label,
            chip_icon, bug_group_r, cross, perm_stamp,
            small_chips, affected_label,
            note,
        )
        self.play(FadeOut(all_objects))
        self.wait(0.3)
