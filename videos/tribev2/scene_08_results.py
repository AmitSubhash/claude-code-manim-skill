"""
Scene 08 -- ResultsScene (~90s)
Act III: What Did It Achieve?

Phase 1: Bar chart of Algonauts 2025 competition (TRIBE 1st of 263).
Phase 2: Noise ceiling gauge showing 54% of explainable variance.
Template: CHART_FOCUS
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


# ── Chart Helpers ────────────────────────────────────────────────────────

def make_bar(
    value: float,
    label: str,
    color: str,
    bar_width: float = 0.7,
    y_scale: float = 18.0,
    y_floor: float = 0.18,
    origin: np.ndarray = ORIGIN,
) -> VGroup:
    """Single bar with value label on top and team name below."""
    bar_height = (value - y_floor) * y_scale
    bar_height = max(bar_height, 0.1)

    rect = Rectangle(
        width=bar_width, height=bar_height,
        color=color, fill_opacity=0.7, stroke_width=1.5,
    )
    rect.move_to(origin + UP * bar_height / 2)

    val_text = Text(
        f"{value:.4f}", font_size=SMALL_LABEL - 2, color=color,
    )
    val_text.next_to(rect, UP, buff=0.08)

    name_text = Text(
        label, font_size=SMALL_LABEL - 2, color=LABEL_GRAY,
    )
    name_text.next_to(rect, DOWN, buff=0.1)

    return VGroup(rect, val_text, name_text)


class ResultsScene(Scene):
    def setup(self):
        self.camera.background_color = BG_COLOR

    def construct(self):
        # ==================================================================
        # Phase 1: Competition bar chart
        # ==================================================================
        title = section_title("Algonauts 2025: 1st of 263 Teams")
        self.play(Write(title), run_time=1.0)
        self.wait(0.3)

        # ── Axes ───────────────────────────────────────────────────────
        y_axis_label = safe_text(
            "Mean Pearson rho", font_size=SMALL_LABEL, color=LABEL_GRAY,
        )
        y_axis_label.rotate(PI / 2)
        y_axis_label.move_to(LEFT * 5.0 + DOWN * 0.5)

        # Bar data
        teams = [
            ("TRIBE", 0.2146, RESULT_GOLD),
            ("NCG", 0.2096, BASELINE_GRAY),
            ("SDA", 0.2094, BASELINE_GRAY),
            ("Team 4", 0.2050, BASELINE_GRAY),
            ("Team 5", 0.2000, BASELINE_GRAY),
        ]

        # y_floor = 0.18 so bars have visible differences
        y_floor = 0.18
        y_scale = 18.0
        bar_width = 0.7
        bar_spacing = 1.1
        chart_left = -2.5

        bars = VGroup()
        for i, (name, val, color) in enumerate(teams):
            x_pos = chart_left + i * bar_spacing
            bar = make_bar(
                value=val, label=name, color=color,
                bar_width=bar_width, y_scale=y_scale, y_floor=y_floor,
                origin=np.array([x_pos, -2.0, 0]),
            )
            bars.add(bar)

        # Baseline line at y_floor
        baseline = Line(
            np.array([chart_left - 0.6, -2.0, 0]),
            np.array([chart_left + 4 * bar_spacing + 0.6, -2.0, 0]),
            color=LABEL_GRAY, stroke_width=1,
        )

        # Tick marks along y axis
        ticks = VGroup()
        for rho_val in [0.19, 0.20, 0.21, 0.22]:
            y_pos = -2.0 + (rho_val - y_floor) * y_scale
            tick_line = Line(
                np.array([chart_left - 0.8, y_pos, 0]),
                np.array([chart_left - 0.5, y_pos, 0]),
                color=LABEL_GRAY, stroke_width=1,
            )
            tick_label = Text(
                f"{rho_val:.2f}", font_size=SMALL_LABEL - 4, color=LABEL_GRAY,
            )
            tick_label.next_to(tick_line, LEFT, buff=0.08)
            ticks.add(VGroup(tick_line, tick_label))

        self.play(
            FadeIn(y_axis_label),
            Create(baseline),
            LaggedStart(*[FadeIn(t) for t in ticks], lag_ratio=0.1),
            run_time=1.0,
        )

        # Bars appear left to right with LaggedStart
        self.play(
            LaggedStart(
                *[FadeIn(bar, shift=UP * 0.3) for bar in bars],
                lag_ratio=0.25,
            ),
            run_time=2.5,
        )
        self.wait(HOLD_LONG)

        # ── Collect all Phase 1 elements ───────────────────────────────
        phase1_elements = VGroup(
            title, y_axis_label, baseline, ticks, bars,
        )

        # ==================================================================
        # Phase 2: Noise ceiling context
        # ==================================================================
        # Transition: FadeOut Phase 1, bring in new title simultaneously
        title2 = section_title("How Close to the Ceiling?")
        self.play(
            FadeOut(phase1_elements),
            Write(title2),
            run_time=1.0,
        )
        self.wait(0.5)

        # ── Horizontal gauge ───────────────────────────────────────────
        gauge_width = 8.0
        gauge_height = 0.8
        gauge_center = DOWN * 0.3

        # Full gauge background (represents noise ceiling = 1.0 normalized)
        gauge_bg = RoundedRectangle(
            width=gauge_width, height=gauge_height, corner_radius=0.15,
            color=BASELINE_GRAY, fill_opacity=0.15, stroke_width=1.5,
        )
        gauge_bg.move_to(gauge_center)

        # Filled portion = 54%
        fill_width = gauge_width * 0.54
        gauge_fill = RoundedRectangle(
            width=fill_width, height=gauge_height - 0.06,
            corner_radius=0.12,
            color=RESULT_GOLD, fill_opacity=0.6, stroke_width=0,
        )
        gauge_fill.align_to(gauge_bg, LEFT)
        gauge_fill.shift(RIGHT * 0.03)

        # Labels on the gauge
        fill_label = safe_text(
            "54%", font_size=HEADING_SIZE, color=WHITE,
        )
        fill_label.move_to(gauge_fill)

        unfill_label = safe_text(
            "46%", font_size=LABEL_SIZE, color=BASELINE_GRAY,
        )
        unfill_center_x = gauge_bg.get_right()[0] - (gauge_width * 0.46) / 2
        unfill_label.move_to(
            np.array([unfill_center_x, gauge_center[1], 0])
        )

        # "of explainable variance" label below gauge
        variance_label = safe_text(
            "54% of explainable variance",
            font_size=LABEL_SIZE, color=RESULT_GOLD,
        )
        variance_label.next_to(gauge_bg, DOWN, buff=0.3)

        self.play(
            FadeIn(gauge_bg),
            run_time=0.5,
        )

        # Animate the fill growing from zero
        gauge_fill_anim = gauge_fill.copy()
        gauge_fill_anim.stretch_to_fit_width(0.01)
        gauge_fill_anim.align_to(gauge_bg, LEFT).shift(RIGHT * 0.03)
        self.add(gauge_fill_anim)

        self.play(
            gauge_fill_anim.animate.become(gauge_fill),
            run_time=1.5,
            rate_func=smooth,
        )
        self.remove(gauge_fill_anim)
        self.add(gauge_fill)

        self.play(
            FadeIn(fill_label),
            FadeIn(unfill_label),
            FadeIn(variance_label, shift=UP * 0.15),
            run_time=0.8,
        )
        self.wait(HOLD_MEDIUM)

        # ── Equation ───────────────────────────────────────────────────
        eq = MathTex(
            r"\rho_{\text{norm}} = \frac{\rho}{\rho_{\max}}",
            font_size=EQ_SIZE, color=WHITE,
        )
        eq.next_to(gauge_bg, UP, buff=0.6)

        self.play(Write(eq), run_time=1.2)
        self.wait(HOLD_SHORT)

        # ── Annotation ─────────────────────────────────────────────────
        annotation = safe_text(
            "Near ceiling in auditory / language cortex",
            font_size=LABEL_SIZE, color=AUDIO_GREEN,
        )
        annotation.next_to(variance_label, DOWN, buff=0.3)

        self.play(FadeIn(annotation, shift=UP * 0.1), run_time=0.8)
        self.wait(HOLD_SHORT)

        # ── Bottom note ────────────────────────────────────────────────
        note = bottom_note(
            "Normalized Pearson captures signal quality relative to data noise",
            color=RESULT_GOLD,
        )
        self.play(FadeIn(note, shift=UP * 0.2), run_time=0.8)
        self.wait(HOLD_LONG)

        # ── Cleanup ────────────────────────────────────────────────────
        fade_all(
            self,
            title2, gauge_bg, gauge_fill, fill_label, unfill_label,
            variance_label, eq, annotation, note,
        )
