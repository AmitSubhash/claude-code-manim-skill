import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


class ArchitectureOverviewScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR

        # ------------------------------------------------------------------ #
        # 1. Title
        # ------------------------------------------------------------------ #
        title = section_title("TheHuzz Architecture")
        self.play(Write(title))
        self.wait(HOLD_MEDIUM)
        self.play(FadeOut(title))

        # ------------------------------------------------------------------ #
        # 2. Build pipeline boxes
        #    Main row y=0.5:  Seed Gen  Stimulus Gen  Comparator  Bug Report
        #    Upper row y=1.8: RTL Simulation (DUT)
        #    Lower row y=-0.8: Golden Model
        #    Optimizer y=-2.0
        # ------------------------------------------------------------------ #

        # -- Seed Generator --
        seed_box = labeled_box(
            "Seed\nGenerator", width=2.0, height=0.8,
            color=CHIP_BLUE, font_size=SMALL_SIZE,
        )
        seed_box.move_to([-5.0, 0.5, 0])

        # -- Stimulus Generator --
        stim_box = labeled_box(
            "Stimulus\nGenerator", width=2.2, height=0.8,
            color=COVERAGE_TEAL, font_size=SMALL_SIZE,
        )
        stim_box.move_to([-2.2, 0.5, 0])

        # -- RTL Simulation (DUT) --
        dut_box = labeled_box(
            "RTL Simulation\n(DUT)", width=2.4, height=0.8,
            color=BUG_RED, font_size=SMALL_SIZE,
        )
        dut_box.move_to([1.0, 1.8, 0])

        # -- Golden Model --
        golden_box = labeled_box(
            "Golden Model", width=2.4, height=0.8,
            color=GOLDEN_GREEN, font_size=SMALL_SIZE,
        )
        golden_box.move_to([1.0, -0.8, 0])

        # -- Comparator --
        comp_box = labeled_box(
            "Comparator", width=2.2, height=0.8,
            color=MUTATION_YELLOW, font_size=SMALL_SIZE,
        )
        comp_box.move_to([3.5, 0.5, 0])

        # -- Bug Report --
        bug_box = labeled_box(
            "Bug\nReport", width=1.5, height=0.8,
            color=EXPLOIT_ORANGE, font_size=SMALL_SIZE,
        )
        bug_box.move_to([4.9, 0.5, 0])

        # -- Optimizer --
        opt_box = labeled_box(
            "Optimizer", width=2.0, height=0.7,
            color=OPTIMIZER_PURPLE, font_size=SMALL_SIZE,
        )
        opt_box.move_to([-2.2, -2.0, 0])

        # ------------------------------------------------------------------ #
        # 3. Arrows between boxes
        # ------------------------------------------------------------------ #

        # Seed -> Stimulus
        arr_seed_stim = Arrow(
            seed_box.get_right(), stim_box.get_left(),
            buff=0.15, color=WHITE, stroke_width=2.5,
            max_tip_length_to_length_ratio=0.2,
        )

        # Stimulus -> DUT (up-right)
        arr_stim_dut = Arrow(
            stim_box.get_top() + [0.3, 0, 0],
            dut_box.get_left(),
            buff=0.15, color=BUG_RED, stroke_width=2.5,
            max_tip_length_to_length_ratio=0.2,
        )

        # Stimulus -> Golden (down-right)
        arr_stim_golden = Arrow(
            stim_box.get_bottom() + [0.3, 0, 0],
            golden_box.get_left(),
            buff=0.15, color=GOLDEN_GREEN, stroke_width=2.5,
            max_tip_length_to_length_ratio=0.2,
        )

        # DUT -> Comparator (down-right)
        arr_dut_comp = Arrow(
            dut_box.get_right(),
            comp_box.get_top() + [-0.1, 0, 0],
            buff=0.15, color=BUG_RED, stroke_width=2.5,
            max_tip_length_to_length_ratio=0.2,
        )

        # Golden -> Comparator (up-right)
        arr_golden_comp = Arrow(
            golden_box.get_right(),
            comp_box.get_bottom() + [-0.1, 0, 0],
            buff=0.15, color=GOLDEN_GREEN, stroke_width=2.5,
            max_tip_length_to_length_ratio=0.2,
        )

        # Comparator -> Bug Report
        arr_comp_bug = Arrow(
            comp_box.get_right(), bug_box.get_left(),
            buff=0.15, color=EXPLOIT_ORANGE, stroke_width=2.5,
            max_tip_length_to_length_ratio=0.2,
        )

        # ------------------------------------------------------------------ #
        # 4. Animate pipeline step by step
        # ------------------------------------------------------------------ #

        # Step 1: Seed Generator
        self.play(Create(seed_box[0]), Write(seed_box[1]))
        self.wait(0.3)

        # Step 2: Arrow + Stimulus Generator
        self.play(Create(arr_seed_stim))
        self.play(Create(stim_box[0]), Write(stim_box[1]))
        self.wait(0.3)

        # Step 3: Fork up to DUT
        self.play(Create(arr_stim_dut))
        self.play(Create(dut_box[0]), Write(dut_box[1]))
        self.wait(0.3)

        # Step 4: Fork down to Golden Model
        self.play(Create(arr_stim_golden))
        self.play(Create(golden_box[0]), Write(golden_box[1]))
        self.wait(0.3)

        # Step 5: Both converge at Comparator
        self.play(Create(arr_dut_comp), Create(arr_golden_comp))
        self.play(Create(comp_box[0]), Write(comp_box[1]))
        self.wait(0.3)

        # Step 6: Comparator -> Bug Report
        self.play(Create(arr_comp_bug))
        self.play(Create(bug_box[0]), Write(bug_box[1]))
        self.wait(0.4)

        # ------------------------------------------------------------------ #
        # 5. Coverage feedback arc: DUT -> Stimulus Generator (curved)
        # ------------------------------------------------------------------ #

        feedback_arc = CurvedArrow(
            start_point=dut_box.get_top() + [0, 0.1, 0],
            end_point=stim_box.get_top() + [0, 0.1, 0],
            angle=-TAU / 5,
            color=COVERAGE_TEAL,
            stroke_width=2.5,
        )

        fb_label = safe_text(
            "Coverage\nFeedback",
            font_size=SMALL_SIZE,
            color=COVERAGE_TEAL,
            max_width=2.2,
        )
        fb_label.next_to(feedback_arc, UP, buff=0.15)

        self.play(Create(feedback_arc), Write(fb_label))
        self.wait(0.3)

        # ------------------------------------------------------------------ #
        # 6. Optimizer box connected below feedback arc
        # ------------------------------------------------------------------ #

        arr_opt_stim = Arrow(
            opt_box.get_top(),
            stim_box.get_bottom(),
            buff=0.15, color=OPTIMIZER_PURPLE, stroke_width=2.5,
            max_tip_length_to_length_ratio=0.2,
        )

        self.play(Create(arr_opt_stim))
        self.play(Create(opt_box[0]), Write(opt_box[1]))
        self.wait(0.4)

        # ------------------------------------------------------------------ #
        # 7. Pulse / highlight the feedback loop
        # ------------------------------------------------------------------ #

        self.play(
            Indicate(feedback_arc, color=COVERAGE_TEAL, scale_factor=1.15),
            Indicate(fb_label, color=COVERAGE_TEAL, scale_factor=1.15),
            Indicate(opt_box, color=OPTIMIZER_PURPLE, scale_factor=1.1),
        )
        self.wait(0.4)

        # ------------------------------------------------------------------ #
        # 8. Bottom note
        # ------------------------------------------------------------------ #

        note = bottom_note("Coverage-guided fuzzing with differential testing")
        self.play(Write(note))
        self.wait(HOLD_LONG)

        # ------------------------------------------------------------------ #
        # 9. Collect full pipeline VGroup and scale to persistent header
        # ------------------------------------------------------------------ #

        pipeline = VGroup(
            seed_box, arr_seed_stim,
            stim_box,
            arr_stim_dut, dut_box,
            arr_stim_golden, golden_box,
            arr_dut_comp, arr_golden_comp,
            comp_box,
            arr_comp_bug, bug_box,
            feedback_arc, fb_label,
            arr_opt_stim, opt_box,
        )

        self.play(FadeOut(note))

        # Scale to HEADER_SCALE and move to top of screen
        self.play(
            pipeline.animate
            .scale(HEADER_SCALE)
            .move_to([0, 2.6, 0]),
            run_time=1.2,
        )
        self.wait(HOLD_SHORT)

        # ------------------------------------------------------------------ #
        # 10. Final cleanup: FadeOut everything
        # ------------------------------------------------------------------ #

        self.play(FadeOut(pipeline))
        self.wait(0.3)
