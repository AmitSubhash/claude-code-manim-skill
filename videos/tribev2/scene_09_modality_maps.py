"""
Scene 09 -- ModalityMapsScene (~90s)
Act III: What Did It Achieve?

Regions on a brain outline light up one by one, colored by dominant modality.
After all regions shown, a summary legend appears.
Template: FULL_CENTER
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


# ── Region Label Builder ─────────────────────────────────────────────────

def region_label_group(
    name: str,
    detail: str,
    color: str,
    highlight: Mobject,
    direction: np.ndarray = DOWN,
) -> VGroup:
    """Two-line label placed relative to a highlight circle.

    Rule 3: if highlight is at |x| > 2.5, labels go DOWN to avoid edge overflow.
    """
    name_text = safe_text(name, font_size=LABEL_SIZE, color=color, max_width=3.0)
    detail_text = safe_text(
        detail, font_size=SMALL_LABEL, color=LABEL_GRAY, max_width=3.0,
    )
    group = VGroup(name_text, detail_text).arrange(DOWN, buff=0.08)

    # Enforce edge overflow rule: if far from center, always place below
    hx = highlight.get_center()[0]
    safe_dir = DOWN if abs(hx) > 2.5 else direction
    group.next_to(highlight, safe_dir, buff=0.2)

    # Clamp within safe bounds
    if group.get_right()[0] > 5.3:
        group.shift(LEFT * (group.get_right()[0] - 5.3))
    if group.get_left()[0] < -5.3:
        group.shift(RIGHT * (-5.3 - group.get_left()[0]))
    if group.get_bottom()[1] < -3.0:
        group.shift(UP * (-3.0 - group.get_bottom()[1]))

    return group


def legend_entry(label: str, color: str) -> VGroup:
    """Small color dot + label for the summary legend."""
    dot = Dot(radius=0.08, color=color, fill_opacity=0.9)
    text = safe_text(label, font_size=SMALL_LABEL, color=color, max_width=3.0)
    return VGroup(dot, text).arrange(RIGHT, buff=0.15)


class ModalityMapsScene(Scene):
    def setup(self):
        self.camera.background_color = BG_COLOR

    def construct(self):
        # ── Title ──────────────────────────────────────────────────────
        title = section_title("Which Modality Predicts Which Region?")
        self.play(Write(title), run_time=1.0)
        self.wait(0.3)

        # ── Brain outline ──────────────────────────────────────────────
        brain = brain_outline(width=7.0, height=4.0, color=BRAIN_PURPLE)
        brain.move_to(DOWN * 0.2)
        self.play(FadeIn(brain, run_time=1.0))
        self.wait(0.5)

        # ── Region data ───────────────────────────────────────────────
        regions = [
            {
                "name": "Visual Cortex",
                "detail": "V-JEPA 2 dominates",
                "x_off": 0.0,
                "y_off": -1.2,
                "radius": 0.7,
                "color": VIDEO_BLUE,
                "label_dir": DOWN,
            },
            {
                "name": "Auditory Cortex",
                "detail": "Wav2Vec dominates",
                "x_off": 2.0,
                "y_off": -0.1,
                "radius": 0.6,
                "color": AUDIO_GREEN,
                "label_dir": DOWN,
            },
            {
                "name": "Prefrontal Cortex",
                "detail": "LLaMA dominates",
                "x_off": 0.0,
                "y_off": 1.2,
                "radius": 0.65,
                "color": TEXT_ORANGE,
                "label_dir": RIGHT,
            },
            {
                "name": "Integration Zone",
                "detail": "+30% from multimodal",
                "x_off": 1.2,
                "y_off": 0.5,
                "radius": 0.5,
                "color": TRANSFORM_TEAL,
                "label_dir": RIGHT,
            },
        ]

        highlights = []
        labels = []

        for rd in regions:
            hl = region_highlight(
                brain,
                x_offset=rd["x_off"],
                y_offset=rd["y_off"],
                radius=rd["radius"],
                color=rd["color"],
                opacity=0.4,
            )
            lbl = region_label_group(
                rd["name"], rd["detail"], rd["color"],
                hl, direction=rd["label_dir"],
            )

            self.play(
                FadeIn(hl, scale=0.6),
                FadeIn(lbl, shift=UP * 0.1),
                run_time=1.5,
            )
            self.wait(HOLD_LONG)

            highlights.append(hl)
            labels.append(lbl)

        # ── Dim labels, show summary ───────────────────────────────────
        self.play(
            *[lbl.animate.set_opacity(DIM_OPACITY) for lbl in labels],
            run_time=0.8,
        )

        # Legend in bottom-right corner (least data density)
        legend_items = [
            legend_entry("Video (V-JEPA 2)", VIDEO_BLUE),
            legend_entry("Audio (Wav2Vec)", AUDIO_GREEN),
            legend_entry("Text (LLaMA)", TEXT_ORANGE),
            legend_entry("Multimodal", TRANSFORM_TEAL),
        ]
        legend = VGroup(*legend_items).arrange(DOWN, buff=0.12, aligned_edge=LEFT)

        legend_box = RoundedRectangle(
            width=legend.width + 0.4,
            height=legend.height + 0.3,
            corner_radius=0.1,
            color=LABEL_GRAY,
            fill_opacity=0.08,
            stroke_width=1,
        )
        legend_group = VGroup(legend_box, legend)
        legend.move_to(legend_box)
        legend_group.to_corner(DR, buff=0.4)

        # Clamp legend within safe bounds
        if legend_group.get_right()[0] > 5.5:
            legend_group.shift(LEFT * (legend_group.get_right()[0] - 5.5))
        if legend_group.get_bottom()[1] < -3.0:
            legend_group.shift(UP * (-3.0 - legend_group.get_bottom()[1]))

        self.play(FadeIn(legend_group, shift=LEFT * 0.2), run_time=1.0)
        self.wait(HOLD_SHORT)

        # Summary text
        summary = safe_text(
            "Multimodal advantage strongest where modalities converge",
            font_size=LABEL_SIZE,
            color=RESULT_GOLD,
            max_width=8.0,
        )
        summary.move_to(DOWN * 1.8)

        self.play(
            FadeIn(summary, shift=UP * 0.15),
            # Restore label opacity for final hold
            *[lbl.animate.set_opacity(0.6) for lbl in labels],
            run_time=1.0,
        )
        self.wait(HOLD_MEDIUM)

        # ── Bottom note ────────────────────────────────────────────────
        note = bottom_note(
            "Each modality predicts distinct brain territories",
            color=RESULT_GOLD,
        )
        self.play(FadeIn(note, shift=UP * 0.2), run_time=0.8)
        self.wait(HOLD_LONG)

        # ── Cleanup ────────────────────────────────────────────────────
        fade_all(
            self,
            title, brain, *highlights, *labels,
            legend_group, summary, note,
        )
