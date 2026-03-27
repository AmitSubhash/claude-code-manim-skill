"""
Scene 04 -- FrozenBackbonesScene (~75s)
Act II: The Architecture

Three frozen feature extractors shown as parallel columns,
unified by a shared 2 Hz timeline bar.
Template: BUILD_UP
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


class FrozenBackbonesScene(Scene):
    def setup(self):
        self.camera.background_color = BG_COLOR

    def construct(self):
        # ── Phase 1: Title ─────────────────────────────────────────────
        title = safe_text(
            "Stage 1: Three Frozen Feature Extractors",
            font_size=TITLE_SIZE,
            color=WHITE,
        )
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=1.0)
        self.wait(HOLD_SHORT)

        # ── Phase 2: Build three parallel columns ──────────────────────
        col_x = [-3.5, 0.0, 3.5]
        col_configs = [
            {
                "name": "V-JEPA 2",
                "color": VIDEO_BLUE,
                "params": "ViT-Giant, ~1B",
                "mapping": "Video -> 1280-dim",
            },
            {
                "name": "Wav2Vec-BERT",
                "color": AUDIO_GREEN,
                "params": "580M params",
                "mapping": "Audio -> 1024-dim",
            },
            {
                "name": "LLaMA 3.2-3B",
                "color": TEXT_ORANGE,
                "params": "3B params",
                "mapping": "Text -> 2048-dim",
            },
        ]

        columns = []
        for i, cfg in enumerate(col_configs):
            # Main labeled box (narrower to fit within bounds)
            box = labeled_box(
                cfg["name"],
                width=2.5,
                height=1.0,
                color=cfg["color"],
                fill_opacity=0.25,
            )
            box.move_to([col_x[i], 1.2, 0])

            # Snowflake icon -- always placed below-right to avoid edge clipping
            flake = snowflake_icon(color=cfg["color"], scale=0.35)
            flake.next_to(box, DOWN, buff=0.1)
            flake.shift(RIGHT * 1.0)

            # Parameter label below box
            params_lbl = safe_text(
                cfg["params"],
                font_size=SMALL_LABEL,
                color=cfg["color"],
            )
            params_lbl.next_to(box, DOWN, buff=0.45)

            # Mapping label below params
            mapping_lbl = safe_text(
                cfg["mapping"],
                font_size=SMALL_LABEL,
                color=LABEL_GRAY,
            )
            mapping_lbl.next_to(params_lbl, DOWN, buff=0.2)

            col_group = VGroup(box, flake, params_lbl, mapping_lbl)
            columns.append(col_group)

        # Animate columns with LaggedStart, ~3s per column stagger
        self.play(
            LaggedStart(
                *[FadeIn(col, shift=UP * 0.4) for col in columns],
                lag_ratio=0.4,
            ),
            run_time=4.0,
        )
        self.wait(HOLD_MEDIUM)

        # ── Phase 3: Shared timeline bar ───────────────────────────────
        timeline_bar = RoundedRectangle(
            width=10.0,
            height=0.6,
            corner_radius=0.15,
            color=RESULT_GOLD,
            fill_opacity=0.2,
            stroke_width=2,
        )
        timeline_bar.move_to(DOWN * 2.3)

        timeline_label = safe_text(
            "Shared 2 Hz Timeline",
            font_size=LABEL_SIZE,
            color=RESULT_GOLD,
        )
        timeline_label.move_to(timeline_bar)

        timeline_group = VGroup(timeline_bar, timeline_label)

        # Arrows from each column down to the timeline bar
        col_arrows = []
        for col in columns:
            # Arrow from bottom of mapping label to top of timeline bar
            mapping_lbl = col[-1]  # last element is mapping label
            arrow = Arrow(
                mapping_lbl.get_bottom(),
                timeline_bar.get_top(),
                buff=0.2,
                color=WHITE,
                stroke_width=2,
                max_tip_length_to_length_ratio=0.2,
            )
            col_arrows.append(arrow)

        self.play(
            Create(timeline_group),
            *[Create(a) for a in col_arrows],
            run_time=1.5,
        )
        self.wait(HOLD_MEDIUM)

        # ── Phase 4: Bottom note ───────────────────────────────────────
        note = bottom_note(
            "Frozen = no gradients through these models",
            color=RESULT_GOLD,
        )
        self.play(FadeIn(note, shift=UP * 0.2), run_time=0.8)
        self.wait(HOLD_LONG)

        # ── Cleanup ────────────────────────────────────────────────────
        all_elements = [title, *columns, timeline_group, *col_arrows, note]
        fade_all(self, *all_elements)
