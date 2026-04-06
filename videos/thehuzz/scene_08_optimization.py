import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


class OptimizationScene(Scene):
    """Scene 8: Optimization -- Finding the Best Tests (~60s).

    Shows how TheHuzz uses a set-cover optimization (IBM CPLEX) to select
    the minimum set of instruction-mutation pairs that cover all coverage
    points, and how the result drives future test-generation weights.
    """

    def construct(self) -> None:
        self.camera.background_color = BG_COLOR

        # ------------------------------------------------------------------ #
        # Phase 0 -- Title
        # ------------------------------------------------------------------ #
        title = safe_text(
            "Optimization: Finding the Best Tests",
            font_size=TITLE_SIZE,
            color=WHITE,
        ).to_edge(UP, buff=0.4)
        self.play(Write(title))
        self.wait(HOLD_SHORT)

        # ------------------------------------------------------------------ #
        # Phase 1 -- Coverage-point grid (6 x 5 = 30 dots)
        # ------------------------------------------------------------------ #
        grid_label = safe_text(
            "Coverage Points",
            font_size=LABEL_SIZE,
            color=LABEL_GRAY,
        )

        # Build 6 cols x 5 rows; centre the grid at y=0, x=0
        COLS, ROWS = 6, 5
        COL_SPACING = 1.1
        ROW_SPACING = 0.85
        DOT_RADIUS = 0.17

        grid_origin_x = -(COLS - 1) * COL_SPACING / 2  # -2.75
        grid_origin_y = (ROWS - 1) * ROW_SPACING / 2   # +1.70

        dots: list[Dot] = []
        dot_positions: list[tuple[float, float]] = []

        for row in range(ROWS):
            for col in range(COLS):
                x = grid_origin_x + col * COL_SPACING
                y = grid_origin_y - row * ROW_SPACING
                d = Dot(point=[x, y, 0], radius=DOT_RADIUS, color=DIM_GRAY)
                d.set_fill(DIM_GRAY, opacity=0.7)
                dots.append(d)
                dot_positions.append((x, y))

        grid_group = VGroup(*dots)
        grid_label.next_to(grid_group, UP, buff=0.35)

        self.play(
            FadeIn(grid_label),
            LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.04),
        )
        self.wait(HOLD_SHORT)

        # ------------------------------------------------------------------ #
        # Phase 2 -- Instruction-mutation ellipses covering subsets
        # ------------------------------------------------------------------ #
        # We define which dot indices each ellipse "covers" so the set-cover
        # animation in Phase 3 can reference them.  Indices follow row-major
        # order: dot[r*6 + c].

        # Ellipse 1 (CHIP_BLUE) -- top-left cluster, ~8 dots
        # dots: (0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1)
        e1_indices = [0, 1, 2, 6, 7, 8, 12, 13]
        e1_center = _cluster_center(dot_positions, e1_indices)
        ellipse1 = Ellipse(width=4.0, height=2.5, color=CHIP_BLUE)
        ellipse1.set_fill(CHIP_BLUE, opacity=0.15)
        ellipse1.set_stroke(CHIP_BLUE, width=2, opacity=0.9)
        _apply_dashes(ellipse1)
        ellipse1.move_to([e1_center[0] + 0.1, e1_center[1] + 0.05, 0])

        lbl1 = safe_text("ADD + M0", font_size=SMALL_SIZE, color=CHIP_BLUE)
        lbl1.next_to(ellipse1, UL, buff=-0.6)

        # Ellipse 2 (GOLDEN_GREEN) -- right column + overlap, ~6 dots
        # dots: (0,4),(0,5),(1,4),(1,5),(2,4),(2,5)
        e2_indices = [4, 5, 10, 11, 16, 17]
        e2_center = _cluster_center(dot_positions, e2_indices)
        ellipse2 = Ellipse(width=2.8, height=3.0, color=GOLDEN_GREEN)
        ellipse2.set_fill(GOLDEN_GREEN, opacity=0.15)
        ellipse2.set_stroke(GOLDEN_GREEN, width=2, opacity=0.9)
        _apply_dashes(ellipse2)
        ellipse2.move_to([e2_center[0], e2_center[1], 0])

        lbl2 = safe_text("FENCE + M2", font_size=SMALL_SIZE, color=GOLDEN_GREEN)
        lbl2.next_to(ellipse2, UR, buff=0.1)

        # Ellipse 3 (EXPLOIT_ORANGE) -- middle rows, ~7 dots
        # dots: (2,2),(2,3),(3,1),(3,2),(3,3),(4,1),(4,2)
        e3_indices = [14, 15, 19, 20, 21, 25, 26]
        e3_center = _cluster_center(dot_positions, e3_indices)
        ellipse3 = Ellipse(width=3.5, height=2.8, color=EXPLOIT_ORANGE)
        ellipse3.set_fill(EXPLOIT_ORANGE, opacity=0.15)
        ellipse3.set_stroke(EXPLOIT_ORANGE, width=2, opacity=0.9)
        _apply_dashes(ellipse3)
        ellipse3.move_to([e3_center[0], e3_center[1] - 0.1, 0])

        lbl3 = safe_text("SUB + M5", font_size=SMALL_SIZE, color=EXPLOIT_ORANGE)
        lbl3.next_to(ellipse3, DOWN, buff=0.1)

        # Ellipse 4 (OPTIMIZER_PURPLE) -- bottom-right, ~5 dots
        # dots: (3,4),(3,5),(4,3),(4,4),(4,5)
        e4_indices = [22, 23, 27, 28, 29]
        e4_center = _cluster_center(dot_positions, e4_indices)
        ellipse4 = Ellipse(width=2.8, height=2.2, color=OPTIMIZER_PURPLE)
        ellipse4.set_fill(OPTIMIZER_PURPLE, opacity=0.15)
        ellipse4.set_stroke(OPTIMIZER_PURPLE, width=2, opacity=0.9)
        _apply_dashes(ellipse4)
        ellipse4.move_to([e4_center[0] + 0.05, e4_center[1], 0])

        lbl4 = safe_text("MUL + M8", font_size=SMALL_SIZE, color=OPTIMIZER_PURPLE)
        lbl4.next_to(ellipse4, DR, buff=0.05)

        ellipses = [ellipse1, ellipse2, ellipse3, ellipse4]
        ellipse_labels = [lbl1, lbl2, lbl3, lbl4]

        self.play(
            LaggedStart(
                *[
                    AnimationGroup(Create(e), FadeIn(l))
                    for e, l in zip(ellipses, ellipse_labels)
                ],
                lag_ratio=0.4,
            )
        )
        self.wait(HOLD_MEDIUM)

        # ------------------------------------------------------------------ #
        # Phase 3 -- Set-cover selection animation
        # ------------------------------------------------------------------ #
        # Fade out the title before showing the goal text to avoid overlap
        self.play(FadeOut(title))

        goal_text = safe_text(
            "Goal: Cover all points with minimum pairs",
            font_size=BODY_SIZE,
            color=MUTATION_YELLOW,
        ).to_edge(UP, buff=0.3)
        self.play(Write(goal_text))
        self.wait(HOLD_SHORT)

        # Counter display (top-right corner)
        counter_label = safe_text("Selected:", font_size=LABEL_SIZE, color=LABEL_GRAY)
        counter_val = safe_text("0 / 30", font_size=HEADING_SIZE, color=WHITE)
        counter_group = VGroup(counter_label, counter_val).arrange(RIGHT, buff=0.2)
        counter_group.to_corner(UR, buff=0.5)
        counter_group.shift(LEFT * 0.2)
        self.play(FadeIn(counter_group))

        # Mapping: ellipse index -> (dot indices, color, count label)
        selection_steps = [
            (0, ellipse1, e1_indices, CHIP_BLUE, "8 / 30"),
            (2, ellipse3, e3_indices, EXPLOIT_ORANGE, "15 / 30"),
            (1, ellipse2, e2_indices, GOLDEN_GREEN, "21 / 30"),
            (3, ellipse4, e4_indices, OPTIMIZER_PURPLE, "26 / 30"),
        ]

        # Track which dots have already been colored
        colored_dot_indices: set[int] = set()

        for _order, ellipse, idx_list, color, count_str in selection_steps:
            # Highlight the selected ellipse border
            self.play(
                ellipse.animate.set_stroke(color, width=4, opacity=1.0)
                .set_fill(color, opacity=0.30),
                run_time=0.5,
            )

            # Color only the newly covered dots
            new_idx = [i for i in idx_list if i not in colored_dot_indices]
            colored_dot_indices.update(idx_list)

            dot_anims = [
                dots[i].animate.set_color(color).set_fill(color, opacity=1.0)
                for i in new_idx
            ]
            if dot_anims:
                self.play(LaggedStart(*dot_anims, lag_ratio=0.08), run_time=0.8)

            # Update counter
            new_counter = safe_text(count_str, font_size=HEADING_SIZE, color=WHITE)
            new_counter.move_to(counter_val)
            self.play(ReplacementTransform(counter_val, new_counter), run_time=0.4)
            counter_val = new_counter

            self.wait(0.5)

        # Color remaining uncovered dots (if any) in COVERAGE_TEAL
        remaining = [i for i in range(30) if i not in colored_dot_indices]
        if remaining:
            self.play(
                LaggedStart(
                    *[
                        dots[i].animate.set_color(COVERAGE_TEAL).set_fill(
                            COVERAGE_TEAL, opacity=1.0
                        )
                        for i in remaining
                    ],
                    lag_ratio=0.06,
                ),
                run_time=0.6,
            )
            final_counter = safe_text("30 / 30", font_size=HEADING_SIZE, color=SAFE_GREEN)
            final_counter.move_to(counter_val)
            self.play(ReplacementTransform(counter_val, final_counter), run_time=0.4)
            counter_val = final_counter

        self.wait(HOLD_SHORT)

        # ------------------------------------------------------------------ #
        # Phase 4 -- Weights output
        # ------------------------------------------------------------------ #
        # Fade out grid, ellipses, labels to make room
        fade_targets = (
            [grid_label, goal_text, counter_group]
            + ellipses
            + ellipse_labels
            + dots
        )
        self.play(*[FadeOut(m) for m in fade_targets], run_time=0.7)

        weights_header = safe_text(
            "Weights Guide Future Test Generation",
            font_size=HEADING_SIZE,
            color=MUTATION_YELLOW,
        ).move_to(UP * 2.3)
        self.play(Write(weights_header))
        self.wait(HOLD_SHORT)

        # Horizontal bar chart for 4 instruction types
        bar_data = [
            ("ADD",   0.72, CHIP_BLUE),
            ("FENCE", 0.55, GOLDEN_GREEN),
            ("SUB",   0.63, EXPLOIT_ORANGE),
            ("MUL",   0.41, OPTIMIZER_PURPLE),
        ]

        MAX_BAR_W = 4.5
        BAR_H = 0.52
        BAR_SPACING = 0.82
        bar_start_y = 0.9

        bar_group_mobs: list[VGroup] = []

        for i, (instr, weight, color) in enumerate(bar_data):
            y = bar_start_y - i * BAR_SPACING

            # Label on the left
            lbl = safe_text(instr, font_size=LABEL_SIZE, color=color)
            lbl.move_to([-4.8, y, 0])

            # Background track
            track = Rectangle(
                width=MAX_BAR_W, height=BAR_H,
                color=DIM_GRAY, fill_opacity=0.25, stroke_width=1,
            )
            track.move_to([MAX_BAR_W / 2 - 2.3, y, 0])

            # Filled bar
            bar_w = MAX_BAR_W * weight
            bar = Rectangle(
                width=bar_w, height=BAR_H,
                color=color, fill_opacity=0.85, stroke_width=0,
            )
            bar.move_to([0, y, 0])
            bar.align_to(track, LEFT)

            # Weight value label on the right of bar
            val_lbl = safe_text(
                f"w = {weight:.2f}",
                font_size=SMALL_SIZE,
                color=LABEL_GRAY,
            )
            val_lbl.next_to(track, RIGHT, buff=0.2)

            row = VGroup(lbl, track, bar, val_lbl)
            bar_group_mobs.append(row)

        self.play(
            LaggedStart(
                *[
                    AnimationGroup(
                        FadeIn(row[0]),           # label
                        FadeIn(row[1]),           # track
                        GrowFromEdge(row[2], LEFT),  # bar
                        FadeIn(row[3]),           # value
                    )
                    for row in bar_group_mobs
                ],
                lag_ratio=0.35,
            ),
            run_time=2.0,
        )
        self.wait(HOLD_MEDIUM)

        # ------------------------------------------------------------------ #
        # Bottom note
        # ------------------------------------------------------------------ #
        note = bottom_note("IBM CPLEX solves the set-cover optimization")
        self.play(FadeIn(note))
        self.wait(HOLD_MEDIUM)

        # ------------------------------------------------------------------ #
        # Cleanup -- FadeOut everything
        # ------------------------------------------------------------------ #
        all_mobs = (
            [weights_header, note]
            + [m for row in bar_group_mobs for m in row]
        )
        self.play(*[FadeOut(m) for m in all_mobs], run_time=0.8)
        self.wait(0.3)


# --------------------------------------------------------------------------- #
# Module-level helpers (not Manim mobjects, so outside the class)
# --------------------------------------------------------------------------- #

def _cluster_center(
    positions: list[tuple[float, float]],
    indices: list[int],
) -> tuple[float, float]:
    """Return the centroid of a subset of dot positions.

    Parameters
    ----------
    positions : list of (x, y) tuples for all 30 dots
    indices   : dot indices whose centroid is desired

    Returns
    -------
    (cx, cy) centroid coordinates
    """
    xs = [positions[i][0] for i in indices]
    ys = [positions[i][1] for i in indices]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def _apply_dashes(shape: VMobject, num_dashes: int = 20) -> None:
    """Convert a shape's stroke to a dashed appearance.

    Manim's DashedVMobject is a wrapper; here we simply reduce opacity in
    alternating stroke segments by shortening dash_offset.  For a simpler
    portable approach we just set a moderate stroke dash_offset style note.
    Since Manim's core VMobject does not natively support dashes on arbitrary
    shapes, we leave the stroke solid with slightly reduced opacity to imply
    a dashed boundary without requiring DashedVMobject restructuring.

    Parameters
    ----------
    shape     : the VMobject whose stroke to adjust
    num_dashes: unused placeholder for interface compatibility
    """
    # Solid strokes with 80% opacity give a clear, clean boundary.
    # True CSS-style dashes require DashedVMobject, which would break
    # the fill and label positioning logic above.
    shape.set_stroke(opacity=0.85)
