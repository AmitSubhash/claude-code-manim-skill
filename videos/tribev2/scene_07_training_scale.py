"""
Scene 07 -- TrainingScaleScene (~60s)
End of Act II: How TRIBE v2 Works

Side-by-side comparison of TRIBE v1 (small) vs TRIBE v2 (massive scale).
Dashed vertical divider, left panel dimmed, right panel highlighted.
Template: DUAL_PANEL
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


def info_row(
    label: str,
    color: str,
    font_size: int = SMALL_LABEL,
    max_width: float = 3.5,
) -> Text:
    """Single info row with width cap."""
    t = Text(label, font_size=font_size, color=color)
    if t.width > max_width:
        t.scale_to_fit_width(max_width)
    return t


def subject_row(count: int, label: str, color: str) -> VGroup:
    """Row with subject icons followed by a label."""
    icons = VGroup(*[subject_icon(color=color, scale=0.35) for _ in range(count)])
    icons.arrange(RIGHT, buff=0.12)
    text = safe_text(label, font_size=SMALL_LABEL, color=color, max_width=2.0)
    row = VGroup(icons, text).arrange(RIGHT, buff=0.25)
    return row


def resolution_badge(label: str, color: str) -> VGroup:
    """Accent badge for resolution callout."""
    rect = RoundedRectangle(
        width=2.2, height=0.5, corner_radius=0.15,
        color=color, fill_opacity=0.35, stroke_width=2,
    )
    text = Text(label, font_size=SMALL_LABEL, color=color, weight=BOLD)
    text.move_to(rect)
    if text.width > rect.width - 0.2:
        text.scale_to_fit_width(rect.width - 0.2)
    return VGroup(rect, text)


class TrainingScaleScene(Scene):
    def setup(self):
        self.camera.background_color = BG_COLOR

    def construct(self):
        # ── Phase 1: Title ─────────────────────────────────────────────
        title = section_title("Training at Scale")
        self.play(Write(title), run_time=1.0)
        self.wait(0.5)

        # ── Phase 2: Dashed vertical divider ───────────────────────────
        divider = DashedLine(
            UP * 2.2, DOWN * 2.8,
            color=LABEL_GRAY, stroke_width=1.5,
            dash_length=0.15,
        )
        divider.move_to(ORIGIN + DOWN * 0.3)
        self.play(Create(divider), run_time=0.6)

        # ── Phase 3: Left panel -- TRIBE v1 (dimmed) ──────────────────
        left_center = LEFT * 3.0 + DOWN * 0.3

        v1_header = safe_text(
            "TRIBE v1", font_size=HEADING_SIZE, color=BASELINE_GRAY,
        )
        v1_header.move_to(left_center + UP * 1.8)

        v1_subjects = subject_row(4, "4 subjects", BASELINE_GRAY)
        v1_dataset = info_row("1 dataset (NeuroMod)", BASELINE_GRAY)
        v1_hours = info_row("~80 hrs / subject", BASELINE_GRAY)
        v1_parcels = info_row("1,000 parcels", BASELINE_GRAY)

        v1_stack = VGroup(v1_subjects, v1_dataset, v1_hours, v1_parcels)
        v1_stack.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        v1_stack.move_to(left_center + DOWN * 0.2)

        v1_panel = VGroup(v1_header, v1_stack)

        self.play(
            FadeIn(v1_header, shift=DOWN * 0.2),
            LaggedStart(
                *[FadeIn(item, shift=RIGHT * 0.2) for item in v1_stack],
                lag_ratio=0.2,
            ),
            run_time=2.0,
        )
        self.wait(HOLD_SHORT)

        # Dim the v1 panel
        self.play(v1_panel.animate.set_opacity(0.4), run_time=0.5)

        # ── Phase 4: Right panel -- TRIBE v2 (highlighted) ────────────
        right_center = RIGHT * 3.0 + DOWN * 0.3

        v2_header = safe_text(
            "TRIBE v2", font_size=HEADING_SIZE, color=RESULT_GOLD,
        )
        v2_header.move_to(right_center + UP * 1.8)

        v2_subjects = subject_row(7, "700+ subjects", RESULT_GOLD)

        # Datasets as two lines to fit width
        v2_datasets_label = info_row("4 datasets", RESULT_GOLD)
        v2_datasets_names = info_row(
            "NeuroMod, BOLD, Lebel, Wen",
            LABEL_GRAY, font_size=SMALL_LABEL - 2, max_width=3.8,
        )
        v2_datasets = VGroup(v2_datasets_label, v2_datasets_names)
        v2_datasets.arrange(DOWN, buff=0.08, aligned_edge=LEFT)

        v2_hours = info_row("1,000+ total hours", RESULT_GOLD)
        v2_vertices = info_row("20,484 vertices", RESULT_GOLD)

        v2_stack = VGroup(v2_subjects, v2_datasets, v2_hours, v2_vertices)
        v2_stack.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        v2_stack.move_to(right_center + DOWN * 0.2)

        self.play(
            FadeIn(v2_header, shift=DOWN * 0.2),
            LaggedStart(
                *[FadeIn(item, shift=LEFT * 0.2) for item in v2_stack],
                lag_ratio=0.2,
            ),
            run_time=2.5,
        )
        self.wait(HOLD_MEDIUM)

        # ── Phase 5: Resolution badge with connecting arrow ────────────
        # Arrow between v1 parcels and v2 vertices
        res_arrow = Arrow(
            v1_parcels.get_right() + RIGHT * 0.2,
            v2_vertices.get_left() + LEFT * 0.2,
            buff=0.15,
            color=ACCENT,
            stroke_width=3,
            max_tip_length_to_length_ratio=0.12,
        )

        badge = resolution_badge("70x resolution", ACCENT)
        badge.move_to(res_arrow.get_center() + UP * 0.4)

        self.play(
            Create(res_arrow),
            FadeIn(badge, shift=UP * 0.15),
            run_time=1.2,
        )
        self.wait(HOLD_SHORT)

        # ── Phase 6: Center "Scale" arrow ──────────────────────────────
        scale_arrow = Arrow(
            LEFT * 1.2 + UP * 1.8,
            RIGHT * 1.2 + UP * 1.8,
            buff=0.1,
            color=WHITE,
            stroke_width=3,
            max_tip_length_to_length_ratio=0.1,
        )
        scale_label = safe_text(
            "Scale", font_size=LABEL_SIZE, color=WHITE,
        )
        scale_label.next_to(scale_arrow, UP, buff=0.1)

        self.play(
            Create(scale_arrow),
            FadeIn(scale_label, shift=DOWN * 0.1),
            run_time=0.8,
        )
        self.wait(HOLD_SHORT)

        # ── Phase 7: Bottom note ───────────────────────────────────────
        note = bottom_note(
            "MSE loss, Adam optimizer, 15 epochs, single GPU",
            color=RESULT_GOLD,
        )
        self.play(FadeIn(note, shift=UP * 0.2), run_time=0.8)
        self.wait(HOLD_LONG)

        # ── Cleanup ────────────────────────────────────────────────────
        fade_all(
            self,
            title, divider, v1_panel, v2_header, v2_stack,
            res_arrow, badge, scale_arrow, scale_label, note,
        )
