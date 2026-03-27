"""
Scene 01 -- HookScene (~45s)
Act I: Why This Matters

Brain regions light up in sequence as three modalities activate,
then reveal TRIBE v2 key stats.
Template: FULL_CENTER
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


class HookScene(Scene):
    def setup(self):
        self.camera.background_color = BG_COLOR

    def construct(self):
        # ── Phase 1: Brain outline fades in ──────────────────────────────
        brain = brain_outline(width=6.0, height=3.5, color=BRAIN_PURPLE)
        brain.move_to(UP * 0.3)
        self.play(FadeIn(brain, run_time=1.0))
        self.wait(HOLD_SHORT)

        # ── Phase 2: Light up regions sequentially ───────────────────────
        # Region positions are relative to brain center
        regions_data = [
            {
                "name": "Occipital",
                "x_off": 0.0,
                "y_off": -1.0,
                "color": VIDEO_BLUE,
                "label_text": "Vision",
            },
            {
                "name": "Temporal",
                "x_off": -2.2,
                "y_off": -0.2,
                "color": AUDIO_GREEN,
                "label_text": "Audition",
            },
            {
                "name": "Prefrontal",
                "x_off": 0.0,
                "y_off": 1.2,
                "color": TEXT_ORANGE,
                "label_text": "Language",
            },
        ]

        highlights = []
        labels = []
        for rd in regions_data:
            hl = region_highlight(
                brain,
                x_offset=rd["x_off"],
                y_offset=rd["y_off"],
                radius=0.55,
                color=rd["color"],
                opacity=0.4,
            )

            lbl = safe_text(
                rd["label_text"],
                font_size=SMALL_LABEL,
                color=rd["color"],
            )
            # Place label below highlight to stay within bounds
            lbl.next_to(hl, DOWN, buff=0.15)

            self.play(
                FadeIn(hl, scale=0.6),
                FadeIn(lbl, shift=UP * 0.1),
                run_time=1.5,
            )
            self.wait(HOLD_SHORT)
            highlights.append(hl)
            labels.append(lbl)

        self.wait(0.5)

        # ── Phase 3: Overlay "Predicted, Not Measured" ───────────────────
        overlay_text = safe_text(
            "Predicted, Not Measured",
            font_size=HEADING_SIZE,
            color=RESULT_GOLD,
        )
        # Position below brain to avoid covering region labels
        overlay_text.next_to(brain, DOWN, buff=0.3)

        # Dim the brain and regions first
        self.play(
            brain.animate.set_stroke(opacity=0.3),
            *[h.animate.set_fill(opacity=DIM_OPACITY) for h in highlights],
            *[l.animate.set_opacity(DIM_OPACITY) for l in labels],
            FadeIn(overlay_text, scale=1.1),
            run_time=1.2,
        )
        self.wait(HOLD_MEDIUM)

        # ── Phase 4: Counters ────────────────────────────────────────────
        # Fade out overlay and brain content in one call
        all_brain_parts = [brain, overlay_text] + highlights + labels
        self.play(*[FadeOut(m) for m in all_brain_parts], run_time=0.8)

        counter_data = [
            ("700+ subjects", VIDEO_BLUE),
            ("20,484 vertices", AUDIO_GREEN),
            ("3 modalities", TEXT_ORANGE),
        ]

        counters = VGroup()
        for text, color in counter_data:
            badge = modality_badge(text, color, width=3.0)
            counters.add(badge)
        counters.arrange(RIGHT, buff=0.6)
        counters.move_to(UP * 0.3)

        self.play(
            LaggedStart(
                *[FadeIn(c, shift=UP * 0.3) for c in counters],
                lag_ratio=0.3,
            ),
            run_time=2.0,
        )
        self.wait(HOLD_MEDIUM)

        # ── Phase 5: Bottom note ─────────────────────────────────────────
        note = bottom_note("TRIBE v2 -- Meta FAIR, 2026", color=RESULT_GOLD)
        self.play(FadeIn(note, shift=UP * 0.2), run_time=0.8)
        self.wait(HOLD_MEDIUM)

        # ── Cleanup ──────────────────────────────────────────────────────
        fade_all(self, *counters, note)
