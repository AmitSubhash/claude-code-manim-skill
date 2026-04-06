import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


class GoldenModelScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR

        # ------------------------------------------------------------------ #
        # Phase 1: Title + ISA aha-moment                                     #
        # ------------------------------------------------------------------ #

        title = section_title("The Golden Reference Model", color=GOLDEN_GREEN)
        self.play(Write(title), run_time=0.8)
        self.wait(0.3)

        aha_text = safe_text(
            "Every processor ISA has a software\nsimulator that defines correct behavior",
            font_size=BODY_SIZE,
            color=WHITE,
            max_width=11.0,
        ).move_to(ORIGIN + UP * 0.4)

        self.play(Write(aha_text), run_time=1.2)
        self.wait(HOLD_MEDIUM)

        # ------------------------------------------------------------------ #
        # Phase 2: ISA Spec document icon at center, fork to DUT and GRM     #
        # ------------------------------------------------------------------ #

        # ISA Spec box -- positioned above center
        isa_box = labeled_box(
            "ISA Spec",
            width=2.8,
            height=1.0,
            color=MUTATION_YELLOW,
            font_size=LABEL_SIZE,
            fill_opacity=0.2,
        ).move_to(ORIGIN + UP * 1.8)

        # Small "document" detail lines inside the box
        doc_lines = VGroup()
        doc_lines.add(
            Line(
                isa_box.get_center() + LEFT * 0.7 + DOWN * 0.15,
                isa_box.get_center() + LEFT * 0.1 + DOWN * 0.15,
                color=MUTATION_YELLOW, stroke_width=1.2, stroke_opacity=0.5,
            ),
            Line(
                isa_box.get_center() + LEFT * 0.7,
                isa_box.get_center() + RIGHT * 0.1,
                color=MUTATION_YELLOW, stroke_width=1.2, stroke_opacity=0.5,
            ),
            Line(
                isa_box.get_center() + LEFT * 0.7 + UP * 0.15,
                isa_box.get_center() + LEFT * 0.3 + UP * 0.15,
                color=MUTATION_YELLOW, stroke_width=1.2, stroke_opacity=0.5,
            ),
        )

        # Fork arrows: center-bottom of ISA Spec -> DUT (down-left) and GRM (down-right)
        fork_origin = isa_box.get_bottom() + DOWN * 0.15

        dut_target = np.array([LEFT_X, -0.3, 0])
        grm_target = np.array([RIGHT_X, -0.3, 0])

        arrow_left = Arrow(
            fork_origin,
            dut_target + UP * 0.5,
            buff=0.1,
            color=CHIP_BLUE,
            stroke_width=3,
            max_tip_length_to_length_ratio=0.15,
        )
        arrow_right = Arrow(
            fork_origin,
            grm_target + UP * 0.5,
            buff=0.1,
            color=GOLDEN_GREEN,
            stroke_width=3,
            max_tip_length_to_length_ratio=0.15,
        )

        # DUT and GRM boxes at the bottom of the fork arrows
        dut_box = labeled_box(
            "RTL Design\n(DUT)",
            width=2.8,
            height=1.2,
            color=CHIP_BLUE,
            font_size=LABEL_SIZE,
            fill_opacity=0.2,
        ).move_to(np.array([LEFT_X, -0.9, 0]))

        grm_box = labeled_box(
            "Software Simulator\n(GRM)",
            width=2.8,
            height=1.2,
            color=GOLDEN_GREEN,
            font_size=LABEL_SIZE,
            fill_opacity=0.2,
        ).move_to(np.array([RIGHT_X, -0.9, 0]))

        # Animate aha_text -> ISA Spec box
        self.play(FadeOut(aha_text), run_time=0.5)
        self.play(FadeIn(isa_box), FadeIn(doc_lines), run_time=0.7)
        self.wait(0.3)

        # Fork arrows and boxes appear together
        self.play(
            Create(arrow_left),
            Create(arrow_right),
            run_time=0.8,
        )
        self.play(
            FadeIn(dut_box, shift=DOWN * 0.2),
            FadeIn(grm_box, shift=DOWN * 0.2),
            run_time=0.7,
        )
        self.wait(HOLD_MEDIUM)

        # ------------------------------------------------------------------ #
        # Phase 3: Transition to comparison view                              #
        # -- FadeOut ISA Spec and fork arrows, keep DUT and GRM              #
        # ------------------------------------------------------------------ #

        self.play(
            FadeOut(isa_box),
            FadeOut(doc_lines),
            FadeOut(arrow_left),
            FadeOut(arrow_right),
            run_time=0.7,
        )

        # Shift DUT and GRM up a bit to make room for instruction arrows and comparator
        self.play(
            dut_box.animate.move_to(np.array([LEFT_X, 0.5, 0])),
            grm_box.animate.move_to(np.array([RIGHT_X, 0.5, 0])),
            run_time=0.6,
        )

        # Column labels
        dut_label = safe_text("Chip Under Test", font_size=SMALL_SIZE, color=CHIP_BLUE, max_width=3.5)
        dut_label.next_to(dut_box, UP, buff=0.15)
        grm_label = safe_text("Golden Model", font_size=SMALL_SIZE, color=GOLDEN_GREEN, max_width=3.5)
        grm_label.next_to(grm_box, UP, buff=0.15)

        self.play(
            LaggedStart(*[Write(m) for m in [dut_label, grm_label]], lag_ratio=0.3),
            run_time=0.8,
        )
        self.wait(0.3)

        # ------------------------------------------------------------------ #
        # Phase 4: Instruction arrows enter both boxes from above             #
        # ------------------------------------------------------------------ #

        # "Instructions" label above the split, centered
        instr_label = safe_text("Instructions", font_size=SMALL_SIZE, color=MUTATION_YELLOW, max_width=4.0)
        instr_label.move_to(UP * 2.8)

        # Arrows from instruction label region down into each box top
        instr_arrow_left = Arrow(
            np.array([LEFT_X, 2.4, 0]),
            dut_box.get_top() + DOWN * 0.05,
            buff=0.1,
            color=MUTATION_YELLOW,
            stroke_width=2.5,
            max_tip_length_to_length_ratio=0.18,
        )
        instr_arrow_right = Arrow(
            np.array([RIGHT_X, 2.4, 0]),
            grm_box.get_top() + DOWN * 0.05,
            buff=0.1,
            color=MUTATION_YELLOW,
            stroke_width=2.5,
            max_tip_length_to_length_ratio=0.18,
        )

        self.play(
            FadeIn(instr_label, shift=DOWN * 0.2),
            run_time=0.5,
        )
        self.play(
            Create(instr_arrow_left),
            Create(instr_arrow_right),
            run_time=0.7,
        )
        self.wait(0.3)

        # ------------------------------------------------------------------ #
        # Phase 5: Output arrows converge to comparator at bottom            #
        # ------------------------------------------------------------------ #

        # Output labels
        dut_out_label = safe_text("Register\nValues", font_size=SMALL_SIZE, color=LABEL_GRAY, max_width=2.5)
        dut_out_label.next_to(dut_box, DOWN, buff=0.55)

        grm_out_label = safe_text("Register\nValues", font_size=SMALL_SIZE, color=LABEL_GRAY, max_width=2.5)
        grm_out_label.next_to(grm_box, DOWN, buff=0.55)

        # Arrows from DUT/GRM boxes going down toward comparator
        out_arrow_left = Arrow(
            dut_box.get_bottom() + DOWN * 0.05,
            dut_out_label.get_top() + DOWN * 0.05,
            buff=0.1,
            color=CHIP_BLUE,
            stroke_width=2.5,
            max_tip_length_to_length_ratio=0.18,
        )
        out_arrow_right = Arrow(
            grm_box.get_bottom() + DOWN * 0.05,
            grm_out_label.get_top() + DOWN * 0.05,
            buff=0.1,
            color=GOLDEN_GREEN,
            stroke_width=2.5,
            max_tip_length_to_length_ratio=0.18,
        )

        self.play(
            Create(out_arrow_left),
            Create(out_arrow_right),
            run_time=0.6,
        )
        self.play(
            LaggedStart(*[Write(m) for m in [dut_out_label, grm_out_label]], lag_ratio=0.2),
            run_time=0.7,
        )
        self.wait(0.3)

        # Comparator box at bottom center
        comparator = labeled_box(
            "Comparator",
            width=2.6,
            height=0.9,
            color=MUTATION_YELLOW,
            font_size=LABEL_SIZE,
            fill_opacity=0.25,
        ).move_to(np.array([0.0, -2.2, 0]))

        # Arrows converging from output labels into comparator
        conv_arrow_left = Arrow(
            dut_out_label.get_bottom() + DOWN * 0.05,
            comparator.get_left() + LEFT * 0.05,
            buff=0.1,
            color=CHIP_BLUE,
            stroke_width=2.5,
            max_tip_length_to_length_ratio=0.15,
        )
        conv_arrow_right = Arrow(
            grm_out_label.get_bottom() + DOWN * 0.05,
            comparator.get_right() + RIGHT * 0.05,
            buff=0.1,
            color=GOLDEN_GREEN,
            stroke_width=2.5,
            max_tip_length_to_length_ratio=0.15,
        )

        self.play(FadeIn(comparator, scale=0.9), run_time=0.6)
        self.play(
            Create(conv_arrow_left),
            Create(conv_arrow_right),
            run_time=0.7,
        )
        self.wait(0.4)

        # ------------------------------------------------------------------ #
        # Phase 6: Match and mismatch outcomes                                #
        # ------------------------------------------------------------------ #

        # Match outcome (green check) -- show first
        match_check = safe_text("Match = OK", font_size=LABEL_SIZE, color=SAFE_GREEN, max_width=3.5)
        match_check.next_to(comparator, RIGHT, buff=0.55)

        check_mark = Text("", font_size=HEADING_SIZE, color=SAFE_GREEN)
        check_mark.next_to(match_check, LEFT, buff=0.15)

        match_group = VGroup(check_mark, match_check)
        match_group.next_to(comparator, RIGHT, buff=0.4)

        self.play(
            LaggedStart(*[Write(m) for m in match_group], lag_ratio=0.3),
            run_time=0.8,
        )
        self.wait(HOLD_SHORT)

        # Mismatch outcome (red X and BUG!) -- replace match briefly
        mismatch_label = safe_text("Mismatch = BUG!", font_size=LABEL_SIZE, color=BUG_RED, max_width=3.5)
        bug_flash = safe_text("BUG!", font_size=HEADING_SIZE, color=BUG_RED, max_width=2.0)

        mismatch_group = VGroup(mismatch_label)
        mismatch_group.next_to(comparator, RIGHT, buff=0.4)

        bug_flash.next_to(comparator, UP, buff=0.3)

        self.play(
            ReplacementTransform(match_group, mismatch_group),
            run_time=0.7,
        )
        self.play(
            FadeIn(bug_flash, scale=1.3),
            run_time=0.5,
        )
        self.wait(HOLD_SHORT)

        # Restore match outcome for final state
        self.play(
            FadeOut(bug_flash),
            ReplacementTransform(mismatch_group, match_group),
            run_time=0.7,
        )
        self.wait(0.4)

        # ------------------------------------------------------------------ #
        # Phase 7: Example GRM implementations as small tags                 #
        # ------------------------------------------------------------------ #

        example_data = [
            ("Spike", "RISC-V", GOLDEN_GREEN),
            ("or1ksim", "OpenRISC", COVERAGE_TEAL),
            ("Archsim", "x86 (Intel)", EXPLOIT_ORANGE),
        ]

        example_tags = VGroup()
        for name, arch, color in example_data:
            tag_rect = RoundedRectangle(
                width=2.2, height=0.55,
                corner_radius=0.1,
                color=color, fill_opacity=0.15, stroke_width=1.5,
            )
            tag_text = Text(
                f"{name}  ({arch})",
                font_size=SMALL_SIZE,
                color=color,
            )
            if tag_text.width > 2.2 - 0.2:
                tag_text.scale_to_fit_width(2.2 - 0.2)
            tag_text.move_to(tag_rect)
            example_tags.add(VGroup(tag_rect, tag_text))

        example_tags.arrange(DOWN, buff=0.2)
        # Position below the grm_box so tags don't overlap the box label
        example_tags.next_to(grm_box, DOWN, buff=0.25)

        examples_header = safe_text(
            "Real GRMs:",
            font_size=SMALL_SIZE,
            color=LABEL_GRAY,
            max_width=2.5,
        )
        examples_header.next_to(example_tags, UP, buff=0.15)

        self.play(FadeIn(examples_header), run_time=0.4)
        self.play(
            LaggedStart(*[FadeIn(tag, shift=LEFT * 0.2) for tag in example_tags], lag_ratio=0.3),
            run_time=1.0,
        )
        self.wait(HOLD_MEDIUM)

        # ------------------------------------------------------------------ #
        # Phase 8: Bottom note                                                #
        # ------------------------------------------------------------------ #

        note = bottom_note(
            "Like having the teacher's answer key for every possible test",
            color=MUTATION_YELLOW,
        )
        self.play(FadeIn(note, shift=UP * 0.2), run_time=0.6)
        self.wait(HOLD_LONG)

        # ------------------------------------------------------------------ #
        # Cleanup: FadeOut all elements                                       #
        # ------------------------------------------------------------------ #

        all_elements = [
            title,
            dut_box, grm_box,
            dut_label, grm_label,
            instr_label,
            instr_arrow_left, instr_arrow_right,
            out_arrow_left, out_arrow_right,
            dut_out_label, grm_out_label,
            comparator,
            conv_arrow_left, conv_arrow_right,
            match_group,
            example_tags, examples_header,
            note,
        ]

        self.play(
            *[FadeOut(el) for el in all_elements],
            run_time=1.0,
        )
        self.wait(0.1)
