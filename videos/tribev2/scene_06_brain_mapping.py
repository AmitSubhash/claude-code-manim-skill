"""
Scene 06 -- BrainMappingScene (~60s)
Act II: The Architecture

Subject-conditional brain mapping: low-rank bottleneck,
subject-specific heads, and final output onto cortical surface.
Template: TOP_PERSISTENT_BOTTOM_CONTENT
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


class BrainMappingScene(Scene):
    def setup(self):
        self.camera.background_color = BG_COLOR

    # ── Persistent header helpers ──────────────────────────────────────
    def _build_persistent_header(self) -> VGroup:
        """Miniaturized pipeline: 3 backbone boxes -> transformer."""
        mini_vjepa = labeled_box(
            "V-JEPA", width=1.2, height=0.45,
            color=VIDEO_BLUE, font_size=SMALL_LABEL, fill_opacity=0.25,
        )
        mini_w2vb = labeled_box(
            "W2V-B", width=1.2, height=0.45,
            color=AUDIO_GREEN, font_size=SMALL_LABEL, fill_opacity=0.25,
        )
        mini_llama = labeled_box(
            "LLaMA", width=1.2, height=0.45,
            color=TEXT_ORANGE, font_size=SMALL_LABEL, fill_opacity=0.25,
        )
        backbones = VGroup(mini_vjepa, mini_w2vb, mini_llama)
        backbones.arrange(RIGHT, buff=0.3)

        # Small arrow
        mini_arrow = Arrow(
            ORIGIN, RIGHT * 0.6,
            color=WHITE, stroke_width=2,
            max_tip_length_to_length_ratio=0.25,
        )

        mini_tf = labeled_box(
            "Transformer", width=1.6, height=0.45,
            color=TRANSFORM_TEAL, font_size=SMALL_LABEL, fill_opacity=0.25,
        )

        header = VGroup(backbones, mini_arrow, mini_tf)
        header.arrange(RIGHT, buff=0.2)
        header.scale(HEADER_SCALE)
        header.move_to(UP * 2.8)
        return header

    def construct(self):
        # ── Persistent header ──────────────────────────────────────────
        header = self._build_persistent_header()
        self.play(FadeIn(header, shift=DOWN * 0.2), run_time=0.8)

        subtitle = safe_text(
            "Stage 3: Subject-Conditional Brain Mapping",
            font_size=HEADING_SIZE,
            color=WHITE,
        )
        subtitle.move_to(UP * 2.0)
        self.play(Write(subtitle), run_time=1.0)
        self.wait(HOLD_SHORT)

        # ── Phase 1: Low-rank bottleneck diagram ──────────────────────
        tf_out_box = labeled_box(
            "Transformer Out", width=2.2, height=0.9,
            color=TRANSFORM_TEAL, font_size=SMALL_LABEL, fill_opacity=0.25,
        )
        tf_out_dim = safe_text(
            "1152-dim", font_size=SMALL_LABEL, color=TRANSFORM_TEAL,
        )

        lowrank_box = labeled_box(
            "Low-Rank", width=2.2, height=0.9,
            color=BRAIN_PURPLE, font_size=SMALL_LABEL, fill_opacity=0.25,
        )
        lowrank_dim = safe_text(
            "2048-dim", font_size=SMALL_LABEL, color=BRAIN_PURPLE,
        )

        brain_head_box = labeled_box(
            "Brain Head", width=2.2, height=0.9,
            color=SUBJECT_PINK, font_size=SMALL_LABEL, fill_opacity=0.25,
        )

        # Arrange horizontally
        pipeline = VGroup(tf_out_box, lowrank_box, brain_head_box)
        pipeline.arrange(RIGHT, buff=1.6)
        pipeline.move_to(UP * 0.5)

        # Dimension labels below each box (DOWN from center per rule 7)
        tf_out_dim.next_to(tf_out_box, DOWN, buff=0.15)
        lowrank_dim.next_to(lowrank_box, DOWN, buff=0.15)

        # Pipeline arrows
        arrow1 = pipeline_arrow(tf_out_box, lowrank_box, color=WHITE)
        arrow2 = pipeline_arrow(lowrank_box, brain_head_box, color=WHITE)

        self.play(
            LaggedStart(
                FadeIn(tf_out_box, shift=RIGHT * 0.3),
                FadeIn(tf_out_dim, shift=UP * 0.1),
                Create(arrow1),
                FadeIn(lowrank_box, shift=RIGHT * 0.3),
                FadeIn(lowrank_dim, shift=UP * 0.1),
                Create(arrow2),
                FadeIn(brain_head_box, shift=RIGHT * 0.3),
                lag_ratio=0.2,
            ),
            run_time=3.0,
        )
        self.wait(HOLD_MEDIUM)

        # ── Phase 2: Subject branching ─────────────────────────────────
        # Fade out dimension labels to make space
        self.play(
            FadeOut(tf_out_dim), FadeOut(lowrank_dim),
            run_time=0.4,
        )

        # Subject-specific boxes branching from Brain Head
        subject_labels = ["S1", "S2", "S3", "S4"]
        subject_boxes = VGroup()
        for slabel in subject_labels:
            icon = subject_icon(color=SUBJECT_PINK, scale=0.35)
            sbox = labeled_box(
                slabel, width=0.9, height=0.55,
                color=SUBJECT_PINK, font_size=SMALL_LABEL, fill_opacity=0.2,
            )
            icon.next_to(sbox, LEFT, buff=0.08)
            subject_boxes.add(VGroup(icon, sbox))

        subject_boxes.arrange(RIGHT, buff=0.35)
        subject_boxes.next_to(brain_head_box, DOWN, buff=0.7)

        # Branching arrows from brain head to each subject box
        branch_arrows = VGroup()
        for sgroup in subject_boxes:
            sbox = sgroup[1]  # the labeled_box
            arr = Arrow(
                brain_head_box.get_bottom(), sbox.get_top(), buff=0.15,
                color=SUBJECT_PINK, stroke_width=2,
                max_tip_length_to_length_ratio=0.2,
            )
            branch_arrows.add(arr)

        subject_count_label = safe_text(
            "700+ subject-specific heads",
            font_size=LABEL_SIZE,
            color=SUBJECT_PINK,
        )
        subject_count_label.next_to(subject_boxes, DOWN, buff=0.25)

        self.play(
            LaggedStart(
                *[Create(a) for a in branch_arrows],
                lag_ratio=0.15,
            ),
            LaggedStart(
                *[FadeIn(s, shift=DOWN * 0.2) for s in subject_boxes],
                lag_ratio=0.15,
            ),
            run_time=2.0,
        )
        self.play(FadeIn(subject_count_label, shift=UP * 0.1), run_time=0.6)
        self.wait(HOLD_MEDIUM)

        # ── Phase 3: Output visualization ──────────────────────────────
        # Clear phase 1-2 elements
        phase12_elements = [
            tf_out_box, lowrank_box, brain_head_box,
            arrow1, arrow2,
            subject_boxes, branch_arrows, subject_count_label,
        ]
        self.play(
            *[FadeOut(m) for m in phase12_elements],
            run_time=0.8,
        )

        # Brain outline with vertex label
        brain = brain_outline(width=4.5, height=2.8, color=BRAIN_PURPLE)
        brain.move_to(DOWN * 0.2)

        vertices_label = safe_text(
            "20,484 vertices", font_size=LABEL_SIZE, color=BRAIN_PURPLE,
        )
        vertices_label.next_to(brain, DOWN, buff=0.2)

        # Shared trunk annotation with highlight
        shared_highlight = RoundedRectangle(
            width=2.5, height=1.2, corner_radius=0.2,
            color=RESULT_GOLD, fill_opacity=0.15, stroke_width=2,
        )
        shared_highlight.move_to(brain.get_center() + UP * 0.1)

        shared_label = safe_text(
            "Shared across all subjects",
            font_size=SMALL_LABEL,
            color=RESULT_GOLD,
        )
        shared_label.next_to(shared_highlight, DOWN, buff=0.1)

        # Mini subject heads pointing to brain
        mini_subjects = VGroup()
        for slabel, xoff in zip(["S1", "S2", "S3"], [-2.0, 0.0, 2.0]):
            ms = labeled_box(
                slabel, width=0.8, height=0.45,
                color=SUBJECT_PINK, font_size=SMALL_LABEL, fill_opacity=0.2,
            )
            ms.move_to([xoff, 1.2, 0])
            mini_subjects.add(ms)

        # Arrows from mini subjects to brain
        subj_to_brain_arrows = VGroup()
        for ms in mini_subjects:
            arr = Arrow(
                ms.get_bottom(), brain.get_top(), buff=0.15,
                color=SUBJECT_PINK, stroke_width=2,
                max_tip_length_to_length_ratio=0.15,
            )
            subj_to_brain_arrows.add(arr)

        self.play(
            FadeIn(brain, scale=0.9),
            FadeIn(vertices_label, shift=UP * 0.1),
            run_time=1.2,
        )
        self.play(
            LaggedStart(
                *[FadeIn(ms, shift=DOWN * 0.2) for ms in mini_subjects],
                lag_ratio=0.15,
            ),
            LaggedStart(
                *[Create(a) for a in subj_to_brain_arrows],
                lag_ratio=0.15,
            ),
            run_time=1.5,
        )
        self.play(
            FadeIn(shared_highlight, scale=0.9),
            FadeIn(shared_label, shift=UP * 0.1),
            run_time=1.0,
        )
        self.wait(HOLD_MEDIUM)

        # ── Equation ───────────────────────────────────────────────────
        # h = f(z),  y_s = W_s h   (no dollar signs per rule 13)
        eq = MathTex(
            r"\mathbf{h} = f(\mathbf{z})", r",\quad",
            r"\mathbf{y}_s = \mathbf{W}_s \, \mathbf{h}",
            font_size=EQ_SIZE,
            color=WHITE,
        )
        eq.next_to(brain, DOWN, buff=0.7)

        self.play(Write(eq), run_time=1.5)
        self.wait(HOLD_MEDIUM)

        # ── Bottom note ────────────────────────────────────────────────
        note = bottom_note(
            "Same core model for 700+ subjects",
            color=RESULT_GOLD,
        )
        self.play(FadeIn(note, shift=UP * 0.2), run_time=0.8)
        self.wait(HOLD_LONG)

        # ── Cleanup ────────────────────────────────────────────────────
        all_elements = [
            header, subtitle, brain, vertices_label,
            shared_highlight, shared_label,
            mini_subjects, subj_to_brain_arrows,
            eq, note,
        ]
        fade_all(self, *all_elements)
