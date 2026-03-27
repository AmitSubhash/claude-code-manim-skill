"""
Scene 05 -- IntegrationTransformerScene (~75s)
Act II: The Architecture

Multimodal fusion transformer: per-modality projectors,
concatenation into a shared transformer encoder, and
modality dropout for robustness.
Template: TOP_PERSISTENT_BOTTOM_CONTENT
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


class IntegrationTransformerScene(Scene):
    def setup(self):
        self.camera.background_color = BG_COLOR

    # ── Persistent header helpers ──────────────────────────────────────
    def _build_persistent_header(self) -> VGroup:
        """Miniaturized 3-backbone summary in the HEADER_Y region."""
        mini_vjepa = labeled_box(
            "V-JEPA", width=1.4, height=0.5,
            color=VIDEO_BLUE, font_size=SMALL_LABEL, fill_opacity=0.25,
        )
        mini_w2vb = labeled_box(
            "W2V-B", width=1.4, height=0.5,
            color=AUDIO_GREEN, font_size=SMALL_LABEL, fill_opacity=0.25,
        )
        mini_llama = labeled_box(
            "LLaMA", width=1.4, height=0.5,
            color=TEXT_ORANGE, font_size=SMALL_LABEL, fill_opacity=0.25,
        )
        header = VGroup(mini_vjepa, mini_w2vb, mini_llama)
        header.arrange(RIGHT, buff=0.5)
        header.scale(HEADER_SCALE)
        header.move_to(UP * 2.8)
        return header

    def construct(self):
        # ── Persistent header ──────────────────────────────────────────
        header = self._build_persistent_header()
        self.play(FadeIn(header, shift=DOWN * 0.2), run_time=0.8)

        subtitle = safe_text(
            "Stage 2: Multimodal Fusion Transformer",
            font_size=HEADING_SIZE,
            color=WHITE,
        )
        subtitle.move_to(UP * 2.0)
        self.play(Write(subtitle), run_time=1.0)
        self.wait(HOLD_SHORT)

        # ── Phase 1: Per-modality projectors ───────────────────────────
        proj_colors = [VIDEO_BLUE, AUDIO_GREEN, TEXT_ORANGE]
        proj_labels = ["Proj", "Proj", "Proj"]
        proj_descs = ["LN -> Linear -> GELU"] * 3

        projectors = VGroup()
        proj_desc_labels = VGroup()
        for i, (color, plabel, desc) in enumerate(
            zip(proj_colors, proj_labels, proj_descs)
        ):
            box = labeled_box(
                plabel, width=1.6, height=0.7,
                color=color, font_size=LABEL_SIZE, fill_opacity=0.3,
            )
            dlbl = safe_text(desc, font_size=SMALL_LABEL, color=LABEL_GRAY)
            dlbl.next_to(box, DOWN, buff=0.15)
            projectors.add(box)
            proj_desc_labels.add(dlbl)

        projectors.arrange(RIGHT, buff=1.2)
        projectors.move_to(UP * 0.8)

        # Re-position desc labels after arrangement
        for box, dlbl in zip(projectors, proj_desc_labels):
            dlbl.next_to(box, DOWN, buff=0.15)

        # Arrows from header mini-boxes down to projectors
        header_arrows = VGroup()
        for hbox, pbox in zip(header, projectors):
            arrow = Arrow(
                hbox.get_bottom(), pbox.get_top(), buff=0.2,
                color=WHITE, stroke_width=2,
                max_tip_length_to_length_ratio=0.2,
            )
            header_arrows.add(arrow)

        self.play(
            LaggedStart(
                *[FadeIn(p, shift=UP * 0.3) for p in projectors],
                lag_ratio=0.25,
            ),
            LaggedStart(
                *[FadeIn(d, shift=UP * 0.1) for d in proj_desc_labels],
                lag_ratio=0.25,
            ),
            LaggedStart(
                *[Create(a) for a in header_arrows],
                lag_ratio=0.25,
            ),
            run_time=2.5,
        )
        self.wait(HOLD_MEDIUM)

        # ── Phase 2: Concatenation + Transformer ──────────────────────
        # Fade projector descriptions to make room
        self.play(
            *[FadeOut(d) for d in proj_desc_labels],
            run_time=0.5,
        )

        # Concatenation symbol
        concat_sym = safe_text(
            "||", font_size=TITLE_SIZE, color=RESULT_GOLD,
        )
        concat_sym.move_to(DOWN * 0.1)

        # Converging arrows from projectors to concat
        converge_arrows = VGroup()
        for pbox in projectors:
            arrow = Arrow(
                pbox.get_bottom(), concat_sym.get_top(), buff=0.15,
                color=LABEL_GRAY, stroke_width=2,
                max_tip_length_to_length_ratio=0.15,
            )
            converge_arrows.add(arrow)

        self.play(
            *[Create(a) for a in converge_arrows],
            FadeIn(concat_sym, scale=1.2),
            run_time=1.2,
        )
        self.wait(HOLD_SHORT)

        # Transformer encoder box
        transformer_box = labeled_box(
            "Transformer Encoder",
            width=5.0, height=1.2,
            color=TRANSFORM_TEAL, font_size=LABEL_SIZE, fill_opacity=0.2,
        )
        transformer_box.move_to(DOWN * 1.2)

        # Spec label inside box, offset down by 0.3 per container rule
        spec_label = safe_text(
            "8 layers, 1152-dim, 8 heads",
            font_size=SMALL_LABEL,
            color=TRANSFORM_TEAL,
        )
        spec_label.move_to(transformer_box[0].get_center() + DOWN * 0.3)

        # Window label below transformer
        window_label = safe_text(
            "Window: 100 TRs (~150s)",
            font_size=SMALL_LABEL,
            color=LABEL_GRAY,
        )
        window_label.next_to(transformer_box, DOWN, buff=0.2)

        # Arrow from concat to transformer
        concat_to_tf = Arrow(
            concat_sym.get_bottom(), transformer_box.get_top(), buff=0.15,
            color=RESULT_GOLD, stroke_width=3,
            max_tip_length_to_length_ratio=0.15,
        )

        self.play(
            Create(concat_to_tf),
            FadeIn(transformer_box, shift=UP * 0.3),
            FadeIn(spec_label, shift=UP * 0.1),
            run_time=1.5,
        )
        self.play(FadeIn(window_label, shift=UP * 0.1), run_time=0.6)
        self.wait(HOLD_MEDIUM)

        # ── Phase 3: Modality Dropout visualization ────────────────────
        # Clean up phase 2 diagram elements
        phase2_elements = [
            projectors, header_arrows, converge_arrows,
            concat_sym, concat_to_tf, transformer_box,
            spec_label, window_label,
        ]
        self.play(
            *[FadeOut(m) for m in phase2_elements],
            run_time=0.8,
        )

        dropout_title = safe_text(
            "Modality Dropout",
            font_size=HEADING_SIZE,
            color=TRANSFORM_TEAL,
        )
        dropout_title.move_to(UP * 0.8)

        # Three colored bars representing modality streams
        bar_width = 2.5
        bar_height = 0.5
        bars = VGroup()
        bar_labels_list = ["Video", "Audio", "Text"]
        bar_colors = [VIDEO_BLUE, AUDIO_GREEN, TEXT_ORANGE]

        for j, (blabel, bcolor) in enumerate(
            zip(bar_labels_list, bar_colors)
        ):
            bar = RoundedRectangle(
                width=bar_width, height=bar_height, corner_radius=0.1,
                color=bcolor, fill_opacity=0.6, stroke_width=2,
            )
            blbl = safe_text(blabel, font_size=SMALL_LABEL, color=bcolor)
            blbl.move_to(bar)
            bars.add(VGroup(bar, blbl))

        bars.arrange(DOWN, buff=0.25)
        bars.move_to(DOWN * 0.4)

        self.play(
            FadeIn(dropout_title, shift=UP * 0.2),
            LaggedStart(
                *[FadeIn(b, shift=LEFT * 0.3) for b in bars],
                lag_ratio=0.2,
            ),
            run_time=1.5,
        )
        self.wait(HOLD_SHORT)

        # Red X over the audio bar (index 1) to show dropout
        x_mark = VGroup(
            Line(UL * 0.3, DR * 0.3, color=DANGER_RED, stroke_width=5),
            Line(DL * 0.3, UR * 0.3, color=DANGER_RED, stroke_width=5),
        )
        x_mark.move_to(bars[1])

        p_label = safe_text("p = 0.3", font_size=LABEL_SIZE, color=DANGER_RED)
        p_label.next_to(bars[1], RIGHT, buff=0.4)

        self.play(
            Create(x_mark),
            bars[1][0].animate.set_fill(opacity=DIM_OPACITY),
            bars[1][1].animate.set_opacity(DIM_OPACITY),
            run_time=0.8,
        )
        self.play(FadeIn(p_label, shift=LEFT * 0.2), run_time=0.5)
        self.wait(HOLD_SHORT)

        # "At least one modality always remains" label
        remains_label = safe_text(
            "At least one modality always remains",
            font_size=LABEL_SIZE,
            color=RESULT_GOLD,
        )
        remains_label.next_to(bars, DOWN, buff=0.4)
        self.play(FadeIn(remains_label, shift=UP * 0.1), run_time=0.8)
        self.wait(HOLD_MEDIUM)

        # ── Bottom note ────────────────────────────────────────────────
        note = bottom_note(
            "The transformer learns cross-modal attention AND the HRF",
            color=RESULT_GOLD,
        )
        self.play(FadeIn(note, shift=UP * 0.2), run_time=0.8)
        self.wait(HOLD_LONG)

        # ── Cleanup ────────────────────────────────────────────────────
        all_elements = [
            header, subtitle, dropout_title,
            bars, x_mark, p_label, remains_label, note,
        ]
        fade_all(self, *all_elements)
