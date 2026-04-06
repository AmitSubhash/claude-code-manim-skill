import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


class TakeawayScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR

        # ------------------------------------------------------------------ #
        # Phase 1: Build compact pipeline (pre-assembled, FadeIn at once)
        #   Layout (scaled down from Scene 5 to fit center):
        #   Main row y=0.3:  Seed Gen  Stim Gen  Comparator  Bug Report
        #   Upper y=1.3:     RTL Simulation (DUT)
        #   Lower y=-0.7:    Golden Model
        # ------------------------------------------------------------------ #

        # -- Boxes --
        seed_box = labeled_box(
            "Seed\nGenerator", width=1.7, height=0.7,
            color=CHIP_BLUE, font_size=SMALL_SIZE,
        )
        seed_box.move_to([-5.0, 0.3, 0])

        stim_box = labeled_box(
            "Stimulus\nGenerator", width=1.9, height=0.7,
            color=COVERAGE_TEAL, font_size=SMALL_SIZE,
        )
        stim_box.move_to([-2.5, 0.3, 0])

        dut_box = labeled_box(
            "RTL Simulation\n(DUT)", width=2.1, height=0.7,
            color=BUG_RED, font_size=SMALL_SIZE,
        )
        dut_box.move_to([0.5, 1.3, 0])

        golden_box = labeled_box(
            "Golden Model", width=2.1, height=0.7,
            color=GOLDEN_GREEN, font_size=SMALL_SIZE,
        )
        golden_box.move_to([0.5, -0.7, 0])

        comp_box = labeled_box(
            "Comparator", width=1.9, height=0.7,
            color=MUTATION_YELLOW, font_size=SMALL_SIZE,
        )
        comp_box.move_to([3.0, 0.3, 0])

        bug_box = labeled_box(
            "Bug\nReport", width=1.4, height=0.7,
            color=EXPLOIT_ORANGE, font_size=SMALL_SIZE,
        )
        bug_box.move_to([4.9, 0.3, 0])

        # -- Arrows --
        arr_seed_stim = Arrow(
            seed_box.get_right(), stim_box.get_left(),
            buff=0.12, color=WHITE, stroke_width=2.5,
            max_tip_length_to_length_ratio=0.2,
        )

        arr_stim_dut = Arrow(
            stim_box.get_top() + [0.25, 0, 0],
            dut_box.get_left(),
            buff=0.12, color=BUG_RED, stroke_width=2.5,
            max_tip_length_to_length_ratio=0.2,
        )

        arr_stim_golden = Arrow(
            stim_box.get_bottom() + [0.25, 0, 0],
            golden_box.get_left(),
            buff=0.12, color=GOLDEN_GREEN, stroke_width=2.5,
            max_tip_length_to_length_ratio=0.2,
        )

        arr_dut_comp = Arrow(
            dut_box.get_right(),
            comp_box.get_top() + [-0.1, 0, 0],
            buff=0.12, color=BUG_RED, stroke_width=2.5,
            max_tip_length_to_length_ratio=0.2,
        )

        arr_golden_comp = Arrow(
            golden_box.get_right(),
            comp_box.get_bottom() + [-0.1, 0, 0],
            buff=0.12, color=GOLDEN_GREEN, stroke_width=2.5,
            max_tip_length_to_length_ratio=0.2,
        )

        arr_comp_bug = Arrow(
            comp_box.get_right(), bug_box.get_left(),
            buff=0.12, color=EXPLOIT_ORANGE, stroke_width=2.5,
            max_tip_length_to_length_ratio=0.2,
        )

        # -- Coverage feedback arc above pipeline --
        feedback_arc = CurvedArrow(
            start_point=dut_box.get_top() + [0, 0.1, 0],
            end_point=stim_box.get_top() + [0, 0.1, 0],
            angle=-TAU / 5,
            color=COVERAGE_TEAL,
            stroke_width=2.5,
        )

        # -- Collect into VGroup for unified FadeIn --
        pipeline = VGroup(
            seed_box,
            arr_seed_stim, stim_box,
            arr_stim_dut, dut_box,
            arr_stim_golden, golden_box,
            arr_dut_comp, arr_golden_comp,
            comp_box,
            arr_comp_bug, bug_box,
            feedback_arc,
        )

        # FadeIn entire pipeline at once
        self.play(FadeIn(pipeline))
        self.wait(HOLD_SHORT)

        # ------------------------------------------------------------------ #
        # Phase 2: Stat labels overlaid near relevant boxes
        # ------------------------------------------------------------------ #

        # "11 bugs" near Comparator
        stat_bugs = safe_text("11 bugs", font_size=LABEL_SIZE, color=BUG_RED)
        stat_bugs.next_to(comp_box, DOWN, buff=0.3)

        # "5 CVEs" near Bug Report
        stat_cves = safe_text("5 CVEs", font_size=LABEL_SIZE, color=EXPLOIT_ORANGE)
        stat_cves.next_to(bug_box, DOWN, buff=0.3)

        # "3.33x faster" near feedback arc (above arc)
        stat_faster = safe_text("3.33x faster", font_size=LABEL_SIZE, color=COVERAGE_TEAL)
        stat_faster.move_to([-1.0, 2.5, 0])

        # "2 exploits" at top center
        stat_exploits = safe_text("2 exploits", font_size=LABEL_SIZE, color=MUTATION_YELLOW)
        stat_exploits.move_to([0.0, -2.5, 0])

        self.play(
            LaggedStart(
                *[FadeIn(m, shift=UP * 0.2) for m in [
                    stat_bugs, stat_cves, stat_faster, stat_exploits
                ]],
                lag_ratio=0.3,
            )
        )
        self.wait(HOLD_MEDIUM)

        # ------------------------------------------------------------------ #
        # Phase 3: Dim pipeline + stats; show central takeaway text
        # ------------------------------------------------------------------ #

        self.play(
            FadeOut(pipeline),
            FadeOut(stat_bugs),
            FadeOut(stat_cves),
            FadeOut(stat_faster),
            FadeOut(stat_exploits),
        )

        takeaway = safe_text(
            "Golden reference models turn\nhardware verification into\na searchable problem.",
            font_size=HEADING_SIZE,
            color=WHITE,
            max_width=10.0,
        )
        takeaway.move_to(ORIGIN)

        self.play(Write(takeaway))
        self.wait(HOLD_MEDIUM)

        # ------------------------------------------------------------------ #
        # Phase 4: Takeaway fades out; citation appears
        # ------------------------------------------------------------------ #

        self.play(FadeOut(takeaway))

        citation_line1 = safe_text(
            "Kande et al., USENIX Security 2022",
            font_size=BODY_SIZE,
            color=WHITE,
            max_width=10.0,
        )
        citation_line2 = safe_text(
            "TheHuzz: Instruction Fuzzing of Processors",
            font_size=LABEL_SIZE,
            color=LABEL_GRAY,
            max_width=10.0,
        )
        citation_line3 = safe_text(
            "Using Golden-Reference Models",
            font_size=LABEL_SIZE,
            color=LABEL_GRAY,
            max_width=10.0,
        )

        citation_line1.move_to([0, 0.6, 0])
        citation_line2.next_to(citation_line1, DOWN, buff=0.35)
        citation_line3.next_to(citation_line2, DOWN, buff=0.2)

        citation = VGroup(citation_line1, citation_line2, citation_line3)

        self.play(FadeIn(citation, shift=UP * 0.2))
        self.wait(HOLD_LONG)

        # ------------------------------------------------------------------ #
        # Cleanup: FadeOut everything
        # ------------------------------------------------------------------ #

        self.play(FadeOut(citation))
        self.wait(0.3)
