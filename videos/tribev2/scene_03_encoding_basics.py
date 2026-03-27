"""
Scene 03 -- EncodingBasicsScene (~60s)
Act I: Why This Matters

Dual-panel comparison of traditional single-modality encoding
vs. the multimodal approach TRIBE v2 introduces.
Template: DUAL_PANEL
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


# ── Small signal trace icon ──────────────────────────────────────────────

def bold_trace_icon(
    width: float = 1.6,
    height: float = 0.5,
    color: str = BOLD_RED,
) -> VGroup:
    """Tiny BOLD hemodynamic response curve."""
    # Simple HRF-like shape: rise, peak, undershoot
    points = [
        LEFT * width / 2,
        LEFT * width / 4 + UP * height * 0.3,
        ORIGIN + UP * height,
        RIGHT * width / 4 + UP * height * 0.2,
        RIGHT * width * 0.35 + DOWN * height * 0.15,
        RIGHT * width / 2,
    ]
    curve = VMobject(color=color, stroke_width=2.5)
    curve.set_points_smoothly(points)
    label = safe_text("BOLD", font_size=SMALL_LABEL, color=color)
    label.next_to(curve, DOWN, buff=0.1)
    return VGroup(curve, label)


class EncodingBasicsScene(Scene):
    def setup(self):
        self.camera.background_color = BG_COLOR

    def construct(self):
        # ── Title ────────────────────────────────────────────────────────
        title = section_title("Brain Encoding: Stimulus to Predicted BOLD")
        self.play(Write(title), run_time=1.0)
        self.wait(0.5)

        # ── Vertical divider ─────────────────────────────────────────────
        divider = DashedLine(
            UP * 2.5, DOWN * 3.0,
            color=LABEL_GRAY, stroke_width=1.5,
            dash_length=0.15,
        )
        divider.move_to(ORIGIN)
        self.play(Create(divider), run_time=0.5)

        # ==============================================================
        # LEFT PANEL: Traditional approach
        # ==============================================================
        left_cx = (LEFT_PANEL_X[0] + LEFT_PANEL_X[1]) / 2  # -3.4

        left_header = safe_text(
            "Traditional", font_size=HEADING_SIZE, color=BASELINE_GRAY,
        )
        left_header.move_to(RIGHT * left_cx + UP * 2.0)

        # Pipeline boxes: Stimulus -> Features -> Ridge -> BOLD
        stim_box = labeled_box(
            "Stimulus", width=1.8, height=0.7,
            color=BASELINE_GRAY, fill_opacity=0.15,
        )
        feat_box = labeled_box(
            "Features", width=1.8, height=0.7,
            color=BASELINE_GRAY, fill_opacity=0.15,
        )
        ridge_box = labeled_box(
            "Ridge (W)", width=1.8, height=0.7,
            color=BASELINE_GRAY, fill_opacity=0.15,
        )
        bold_icon = bold_trace_icon()

        left_pipeline = VGroup(stim_box, feat_box, ridge_box, bold_icon)
        left_pipeline.arrange(DOWN, buff=0.5)
        left_pipeline.move_to(RIGHT * left_cx + DOWN * 0.2)

        # Arrows between pipeline steps
        arr_1 = down_arrow(stim_box, feat_box, color=BASELINE_GRAY)
        arr_2 = down_arrow(feat_box, ridge_box, color=BASELINE_GRAY)
        arr_3 = down_arrow(ridge_box, bold_icon, color=BASELINE_GRAY)

        left_arrows = VGroup(arr_1, arr_2, arr_3)

        # Description label
        left_desc = safe_text(
            "Linear, single-modality, per-region",
            font_size=SMALL_LABEL, color=LABEL_GRAY, max_width=5.0,
        )
        left_desc.next_to(left_pipeline, DOWN, buff=0.25)

        # Equation
        eq = MathTex(r"y = Wx + b", font_size=SMALL_EQ, color=BASELINE_GRAY)
        eq.next_to(left_desc, DOWN, buff=0.2)

        # Animate left panel
        self.play(Write(left_header), run_time=0.6)
        self.play(
            LaggedStart(
                FadeIn(stim_box, shift=DOWN * 0.2),
                Create(arr_1),
                FadeIn(feat_box, shift=DOWN * 0.2),
                Create(arr_2),
                FadeIn(ridge_box, shift=DOWN * 0.2),
                Create(arr_3),
                FadeIn(bold_icon, shift=DOWN * 0.2),
                lag_ratio=0.25,
            ),
            run_time=2.5,
        )
        self.play(
            FadeIn(left_desc, shift=UP * 0.1),
            FadeIn(eq, shift=UP * 0.1),
            run_time=0.8,
        )
        self.wait(HOLD_MEDIUM)

        # ==============================================================
        # RIGHT PANEL: What We Need
        # ==============================================================
        right_cx = (RIGHT_PANEL_X[0] + RIGHT_PANEL_X[1]) / 2  # 3.4

        right_header = safe_text(
            "What We Need", font_size=HEADING_SIZE, color=RESULT_GOLD,
        )
        right_header.move_to(RIGHT * right_cx + UP * 2.0)

        # Three input modality badges
        vid_badge = modality_badge("Video", VIDEO_BLUE, width=1.4)
        aud_badge = modality_badge("Audio", AUDIO_GREEN, width=1.4)
        txt_badge = modality_badge("Text", TEXT_ORANGE, width=1.4)

        input_row = VGroup(vid_badge, aud_badge, txt_badge)
        input_row.arrange(RIGHT, buff=0.2)
        input_row.move_to(RIGHT * right_cx + UP * 0.8)

        # Mystery box (dashed border)
        mystery_solid = RoundedRectangle(
            width=2.5, height=0.8, corner_radius=0.1,
            color=RESULT_GOLD, fill_opacity=0.1, stroke_width=0,
        )
        mystery_dash = DashedVMobject(
            RoundedRectangle(
                width=2.5, height=0.8, corner_radius=0.1,
                color=RESULT_GOLD, stroke_width=2,
            ),
            num_dashes=20,
        )
        mystery_label = safe_text("???", font_size=HEADING_SIZE, color=RESULT_GOLD)
        mystery_label.move_to(mystery_solid)
        mystery_rect = VGroup(mystery_solid, mystery_dash)
        mystery_box = VGroup(mystery_rect, mystery_label)
        mystery_box.move_to(RIGHT * right_cx + DOWN * 0.3)

        # Brain outline for output
        brain_small = brain_outline(width=3.0, height=1.6, color=BRAIN_PURPLE)
        brain_small.move_to(RIGHT * right_cx + DOWN * 1.8)

        # Arrows
        arr_in = down_arrow(input_row, mystery_box, color=RESULT_GOLD)
        arr_out = down_arrow(mystery_box, brain_small, color=BRAIN_PURPLE)

        # Description label
        right_desc = safe_text(
            "Nonlinear, multimodal, cross-subject",
            font_size=SMALL_LABEL, color=LABEL_GRAY, max_width=5.0,
        )
        right_desc.next_to(brain_small, DOWN, buff=0.25)

        # Animate right panel
        self.play(Write(right_header), run_time=0.6)
        self.play(
            LaggedStart(
                *[FadeIn(b, shift=DOWN * 0.2) for b in input_row],
                lag_ratio=0.2,
            ),
            run_time=1.0,
        )
        self.play(
            Create(arr_in),
            FadeIn(mystery_box, scale=0.9),
            run_time=1.0,
        )
        self.play(
            Create(arr_out),
            FadeIn(brain_small, scale=0.95),
            run_time=1.0,
        )
        self.play(FadeIn(right_desc, shift=UP * 0.1), run_time=0.6)
        self.wait(HOLD_MEDIUM)

        # ── Bottom note ──────────────────────────────────────────────────
        note = bottom_note("What fills the ??? box?", color=RESULT_GOLD)
        self.play(FadeIn(note, shift=UP * 0.2), run_time=0.8)
        self.wait(HOLD_LONG)

        # ── Cleanup ──────────────────────────────────────────────────────
        fade_all(
            self,
            title, divider,
            left_header, left_pipeline, left_arrows, left_desc, eq,
            right_header, input_row, mystery_box, brain_small,
            arr_in, arr_out, right_desc, note,
        )
