"""
Scene 11 -- AblationsScene (~75s)
Act III: Results

Ablation study with modality bar chart, architecture horizontal bars,
and scaling law inset curve.
Template: CHART_FOCUS
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *
import numpy as np


class AblationsScene(Scene):
    def setup(self):
        self.camera.background_color = BG_COLOR

    def construct(self):
        # ── Phase 1: Modality Ablation Bar Chart (~30s) ────────────────
        title = safe_text(
            "Ablation Study: What Actually Matters?",
            font_size=TITLE_SIZE,
            color=WHITE,
        )
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=1.0)
        self.wait(0.5)

        # Bar chart data
        bar_data = [
            ("Text", 0.22, TEXT_ORANGE),
            ("Audio", 0.24, AUDIO_GREEN),
            ("Video", 0.25, VIDEO_BLUE),
            ("T+V", 0.30, BRAIN_PURPLE),
            ("All", 0.31, RESULT_GOLD),
        ]

        # Axes: manual construction for clarity
        y_min, y_max = 0.18, 0.34
        chart_left = -4.5
        chart_right = 4.5
        chart_bottom = -2.5
        chart_top = 1.8
        chart_width = chart_right - chart_left
        chart_height = chart_top - chart_bottom

        # Y-axis line
        y_axis = Line(
            [chart_left, chart_bottom, 0],
            [chart_left, chart_top, 0],
            color=WHITE, stroke_width=2,
        )
        # X-axis line
        x_axis = Line(
            [chart_left, chart_bottom, 0],
            [chart_right, chart_bottom, 0],
            color=WHITE, stroke_width=2,
        )

        # Y-axis tick labels
        y_ticks = VGroup()
        for val in [0.18, 0.22, 0.26, 0.30, 0.34]:
            y_frac = (val - y_min) / (y_max - y_min)
            y_pos = chart_bottom + y_frac * chart_height
            tick_lbl = safe_text(
                f"{val:.2f}",
                font_size=SMALL_LABEL,
                color=LABEL_GRAY,
            )
            tick_lbl.move_to([chart_left - 0.6, y_pos, 0])
            tick_line = Line(
                [chart_left - 0.1, y_pos, 0],
                [chart_left, y_pos, 0],
                color=LABEL_GRAY, stroke_width=1,
            )
            y_ticks.add(tick_lbl, tick_line)

        # Y-axis label
        y_label = safe_text(
            "Encoding Score",
            font_size=SMALL_LABEL,
            color=LABEL_GRAY,
        )
        y_label.rotate(PI / 2)
        y_label.move_to([chart_left - 1.4, (chart_bottom + chart_top) / 2, 0])

        axes_group = VGroup(y_axis, x_axis, y_ticks, y_label)
        self.play(FadeIn(axes_group), run_time=0.8)

        # Build and animate bars one by one
        n_bars = len(bar_data)
        bar_spacing = chart_width / (n_bars + 1)
        bar_width = 0.7

        bars = VGroup()
        bar_labels = VGroup()
        bar_values = VGroup()

        for i, (name, val, color) in enumerate(bar_data):
            x_center = chart_left + (i + 1) * bar_spacing
            y_frac = (val - y_min) / (y_max - y_min)
            bar_height = y_frac * chart_height

            bar_rect = Rectangle(
                width=bar_width,
                height=bar_height,
                color=color,
                fill_opacity=0.7,
                stroke_width=1.5,
            )
            bar_rect.move_to([x_center, chart_bottom + bar_height / 2, 0])

            # Highlight the "All" bar with a glow border
            if name == "All":
                glow = Rectangle(
                    width=bar_width + 0.15,
                    height=bar_height + 0.1,
                    color=RESULT_GOLD,
                    fill_opacity=0.0,
                    stroke_width=3,
                )
                glow.move_to(bar_rect)
                bar_rect = VGroup(bar_rect, glow)

            # Category label below bar
            cat_lbl = safe_text(name, font_size=SMALL_LABEL, color=color)
            cat_lbl.move_to([x_center, chart_bottom - 0.3, 0])

            # Value label on top
            val_lbl = safe_text(
                f"{val:.2f}",
                font_size=SMALL_LABEL,
                color=WHITE,
            )
            val_lbl.move_to(
                [x_center, chart_bottom + bar_height + 0.2, 0]
            )

            bars.add(bar_rect)
            bar_labels.add(cat_lbl)
            bar_values.add(val_lbl)

        # Reveal bars left to right with LaggedStart
        self.play(
            LaggedStart(
                *[
                    AnimationGroup(
                        FadeIn(bars[i], shift=UP * 0.3),
                        FadeIn(bar_labels[i], shift=UP * 0.1),
                        FadeIn(bar_values[i], shift=DOWN * 0.1),
                    )
                    for i in range(n_bars)
                ],
                lag_ratio=0.3,
            ),
            run_time=4.0,
        )
        self.wait(HOLD_SHORT)

        # Annotation arrow from "Video" bar to "All" bar: "+24%"
        video_idx = 2
        all_idx = 4
        video_bar_top = bar_values[video_idx].get_top()
        all_bar_top = bar_values[all_idx].get_top()

        annot_arrow = CurvedArrow(
            video_bar_top + UP * 0.25,
            all_bar_top + UP * 0.25,
            angle=-0.4,
            color=RESULT_GOLD,
            stroke_width=2.5,
        )
        annot_text = safe_text(
            "+24%", font_size=LABEL_SIZE, color=RESULT_GOLD,
        )
        annot_text.next_to(annot_arrow, UP, buff=0.1)

        self.play(
            Create(annot_arrow),
            FadeIn(annot_text, shift=DOWN * 0.1),
            run_time=1.2,
        )
        self.wait(HOLD_LONG)

        # ── Phase 2: Architecture Ablation (~25s) ──────────────────────
        phase1_elements = VGroup(
            axes_group, bars, bar_labels, bar_values,
            annot_arrow, annot_text,
        )

        subtitle = safe_text(
            "Architecture Matters",
            font_size=HEADING_SIZE,
            color=WHITE,
        )
        subtitle.to_edge(UP, buff=0.4)

        self.play(
            FadeOut(title),
            FadeOut(phase1_elements),
            Write(subtitle),
            run_time=1.0,
        )

        # Horizontal bar chart
        hbar_data = [
            ("No Transformer", 0.23, DANGER_RED, "drop of 0.08"),
            ("Separate Subjects", 0.29, TEXT_ORANGE, "drop of 0.02"),
            ("Full Model", 0.31, RESULT_GOLD, ""),
        ]

        hbar_y_min, hbar_y_max = 0.18, 0.34
        hbar_left = -4.0
        hbar_max_width = 7.5
        hbar_height = 0.7
        hbar_y_positions = [0.8, -0.2, -1.2]

        hbar_group = VGroup()
        for i, (name, val, color, annot) in enumerate(hbar_data):
            frac = (val - hbar_y_min) / (hbar_y_max - hbar_y_min)
            w = frac * hbar_max_width

            bar_rect = Rectangle(
                width=w,
                height=hbar_height,
                color=color,
                fill_opacity=0.65,
                stroke_width=1.5,
            )
            bar_rect.move_to(
                [hbar_left + w / 2, hbar_y_positions[i], 0]
            )

            # Label to the left of bar
            name_lbl = safe_text(
                name, font_size=SMALL_LABEL, color=WHITE,
            )
            name_lbl.next_to(bar_rect, LEFT, buff=0.15)
            # Ensure label does not overflow left edge
            if name_lbl.get_left()[0] < -5.4:
                name_lbl.scale_to_fit_width(
                    abs(bar_rect.get_left()[0] - (-5.4)) - 0.2
                )
                name_lbl.next_to(bar_rect, LEFT, buff=0.15)

            # Value at right end of bar
            val_lbl = safe_text(
                f"{val:.2f}", font_size=SMALL_LABEL, color=WHITE,
            )
            val_lbl.next_to(bar_rect, RIGHT, buff=0.15)

            # Annotation
            annot_lbl = None
            if annot:
                annot_lbl = safe_text(
                    annot, font_size=SMALL_LABEL, color=color,
                )
                annot_lbl.next_to(val_lbl, RIGHT, buff=0.3)
                # Clamp annotation within safe bounds
                if annot_lbl.get_right()[0] > 5.4:
                    annot_lbl.shift(
                        LEFT * (annot_lbl.get_right()[0] - 5.4)
                    )

            row = VGroup(bar_rect, name_lbl, val_lbl)
            if annot_lbl:
                row.add(annot_lbl)
            hbar_group.add(row)

        self.play(
            LaggedStart(
                *[FadeIn(row, shift=RIGHT * 0.5) for row in hbar_group],
                lag_ratio=0.4,
            ),
            run_time=3.5,
        )
        self.wait(HOLD_MEDIUM)

        # ── Phase 3: Scaling Law Inset (~15s) ──────────────────────────
        # Small axes in bottom-right corner
        inset_origin = np.array([3.0, -2.0, 0.0])
        inset_w = 2.5
        inset_h = 1.5

        inset_x_axis = Line(
            inset_origin,
            inset_origin + RIGHT * inset_w,
            color=LABEL_GRAY, stroke_width=1.5,
        )
        inset_y_axis = Line(
            inset_origin,
            inset_origin + UP * inset_h,
            color=LABEL_GRAY, stroke_width=1.5,
        )
        inset_x_lbl = safe_text(
            "Training data", font_size=SMALL_LABEL - 4, color=LABEL_GRAY,
        )
        inset_x_lbl.next_to(inset_x_axis, DOWN, buff=0.1)
        inset_y_lbl = safe_text(
            "Score", font_size=SMALL_LABEL - 4, color=LABEL_GRAY,
        )
        inset_y_lbl.next_to(inset_y_axis, LEFT, buff=0.1)

        # Log-like monotonically increasing curve
        n_pts = 30
        t_vals = np.linspace(0.05, 1.0, n_pts)
        curve_pts = [
            inset_origin
            + RIGHT * (t * inset_w)
            + UP * (np.log(1 + 4 * t) / np.log(5) * inset_h)
            for t in t_vals
        ]
        scaling_curve = VMobject(color=RESULT_GOLD, stroke_width=3)
        scaling_curve.set_points_smoothly(
            [np.array(p) for p in curve_pts]
        )

        no_plateau = safe_text(
            "No plateau reached",
            font_size=SMALL_LABEL - 2,
            color=RESULT_GOLD,
        )
        no_plateau.next_to(
            scaling_curve.get_end(), UP, buff=0.15,
        )
        # Keep annotation within bounds
        if no_plateau.get_right()[0] > 5.4:
            no_plateau.shift(LEFT * (no_plateau.get_right()[0] - 5.4))

        inset_group = VGroup(
            inset_x_axis, inset_y_axis, inset_x_lbl, inset_y_lbl,
            scaling_curve, no_plateau,
        )

        self.play(
            FadeIn(VGroup(inset_x_axis, inset_y_axis, inset_x_lbl, inset_y_lbl)),
            run_time=0.6,
        )
        self.play(Create(scaling_curve), run_time=2.0)
        self.play(FadeIn(no_plateau, shift=DOWN * 0.1), run_time=0.6)
        self.wait(HOLD_MEDIUM)

        # ── Bottom note ───────────────────────────────────────────────
        note = bottom_note(
            "Multimodality and the transformer are each essential",
            color=RESULT_GOLD,
        )
        self.play(FadeIn(note, shift=UP * 0.2), run_time=0.8)
        self.wait(HOLD_MEDIUM)

        # ── Cleanup ──────────────────────────────────────────────────
        fade_all(self, subtitle, hbar_group, inset_group, note)
