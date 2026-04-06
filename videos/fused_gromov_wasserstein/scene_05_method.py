"""Scene 5: FGWEA Method -- three-stage pipeline.

Duration target: ~14s
Template: TOP_PERSISTENT_BOTTOM_CONTENT
"""

import sys
sys.path.insert(0, "/Users/amit/Projects/3brown1blue/videos/fused_gromov_wasserstein")

from utils.style import *


class MethodScene(Scene):
    def construct(self) -> None:
        # ── Title ─────────────────────────────────────────────────────
        title = section_title("FGWEA: Three Stages")

        # NARRATION: FGWEA works in three stages.
        self.play(Write(title), run_time=1.0)
        self.wait(HOLD_SHORT)

        # ── Pipeline boxes ────────────────────────────────────────────
        box_width = 2.8
        box_height = 0.9

        def stage_box(
            label: str,
            sublabel: str,
            color: str,
        ) -> VGroup:
            rect = RoundedRectangle(
                width=box_width, height=box_height,
                corner_radius=0.15, color=color,
                fill_opacity=0.2, stroke_width=2,
            )
            main = Text(label, font_size=LABEL_SIZE, color=color)
            sub = Text(sublabel, font_size=16, color=GRAY_B)
            text_group = VGroup(main, sub).arrange(DOWN, buff=0.1)
            text_group.move_to(rect)
            return VGroup(rect, text_group)

        s1 = stage_box("Stage 1", "Semantic Init", FEATURE_COLOR)
        s2 = stage_box("Stage 2", "Anchor OT", STRUCTURE_COLOR)
        s3 = stage_box("Stage 3", "GW Refine", ANCHOR_COLOR)

        pipeline = VGroup(s1, s2, s3).arrange(RIGHT, buff=1.0)
        pipeline.move_to(UP * 1.3)

        # Arrows between stages
        arrow_1_2 = Arrow(
            s1.get_right(), s2.get_left(),
            color=GRAY_B, buff=0.1, stroke_width=2,
            max_tip_length_to_length_ratio=0.15,
        )
        arrow_2_3 = Arrow(
            s2.get_right(), s3.get_left(),
            color=GRAY_B, buff=0.1, stroke_width=2,
            max_tip_length_to_length_ratio=0.15,
        )

        self.play(
            FadeIn(s1, shift=UP * 0.2),
            FadeIn(s2, shift=UP * 0.2),
            FadeIn(s3, shift=UP * 0.2),
            Create(arrow_1_2),
            Create(arrow_2_3),
            run_time=1.2,
        )
        self.wait(HOLD_SHORT)

        # ── Stage 1 highlight: semantic matching ──────────────────────
        # NARRATION: First, match by name embeddings to find anchor pairs.
        s1_highlight = SurroundingRectangle(s1, color=FEATURE_COLOR, buff=0.15)
        self.play(Create(s1_highlight), run_time=0.5)

        # Show name embedding comparison below
        emb_left = safe_text('"Pokemon"', font_size=LABEL_SIZE,
                             color=KG1_COLOR)
        emb_arrow = MathTex(r"\xrightarrow{\text{embed}}", font_size=28,
                            color=GRAY_B)
        emb_vec = MathTex(r"[0.8, 0.3, \ldots]", font_size=LABEL_SIZE,
                          color=FEATURE_COLOR)
        emb_row = VGroup(emb_left, emb_arrow, emb_vec).arrange(RIGHT, buff=0.3)

        emb_left2 = safe_text('"Pokemon"', font_size=LABEL_SIZE,
                              color=KG2_COLOR)
        emb_arrow2 = MathTex(r"\xrightarrow{\text{embed}}", font_size=28,
                             color=GRAY_B)
        emb_vec2 = MathTex(r"[0.7, 0.4, \ldots]", font_size=LABEL_SIZE,
                           color=FEATURE_COLOR)
        emb_row2 = VGroup(emb_left2, emb_arrow2, emb_vec2).arrange(
            RIGHT, buff=0.3,
        )

        match_icon = Text("\u2713 anchor pair", font_size=LABEL_SIZE,
                          color=ANCHOR_COLOR)

        stage1_content = VGroup(emb_row, emb_row2, match_icon).arrange(
            DOWN, buff=0.35,
        )
        stage1_content.move_to(DOWN * 1.2)

        self.play(Write(stage1_content), run_time=1.2)
        self.wait(HOLD_SHORT)

        # ── Stage 2 highlight: anchor propagation ─────────────────────
        # NARRATION: Second, use anchors to linearize the expensive
        # structural comparison.
        self.play(
            FadeOut(s1_highlight), FadeOut(stage1_content),
            run_time=0.5,
        )

        s2_highlight = SurroundingRectangle(s2, color=STRUCTURE_COLOR,
                                             buff=0.15)
        self.play(Create(s2_highlight), run_time=0.5)

        # Anchor propagation visual
        anchor_node = kg_node("A", color=ANCHOR_COLOR, radius=0.3)
        anchor_node.move_to(DOWN * 1.0)

        neighbor_positions = [
            DOWN * 1.0 + LEFT * 1.5 + DOWN * 0.9,
            DOWN * 1.0 + RIGHT * 1.5 + DOWN * 0.9,
            DOWN * 1.0 + LEFT * 0.0 + DOWN * 1.4,
        ]
        neighbors = VGroup(*[
            kg_node(f"n{i+1}", color=MUTED_GRAY, radius=0.25)
            for i in range(3)
        ])
        for node, pos in zip(neighbors, neighbor_positions):
            node.move_to(pos)

        prop_arrows = VGroup(*[
            Arrow(
                anchor_node.get_center(), n.get_center(),
                color=STRUCTURE_COLOR, buff=0.3, stroke_width=2,
                max_tip_length_to_length_ratio=0.2,
            )
            for n in neighbors
        ])

        self.play(FadeIn(anchor_node), run_time=0.4)
        self.play(
            FadeIn(neighbors),
            *[Create(a) for a in prop_arrows],
            run_time=0.8,
        )

        # Transformation label
        transform_label = safe_text(
            "quadratic -> linear",
            font_size=LABEL_SIZE, color=STRUCTURE_COLOR,
        )
        transform_label.move_to(DOWN * 3.0)

        self.play(Write(transform_label), run_time=0.6)
        self.wait(HOLD_SHORT)

        # ── Stage 3 highlight: GW refinement ──────────────────────────
        # NARRATION: Third, refine globally with full Gromov-Wasserstein
        # optimization.
        self.play(
            FadeOut(s2_highlight),
            FadeOut(anchor_node), FadeOut(neighbors),
            FadeOut(prop_arrows), FadeOut(transform_label),
            run_time=0.5,
        )

        s3_highlight = SurroundingRectangle(s3, color=ANCHOR_COLOR, buff=0.15)
        self.play(Create(s3_highlight), run_time=0.5)

        # Simple optimization visual: transport matrix refining
        refine_label = safe_text(
            "Full FGW optimization over all entity pairs",
            font_size=LABEL_SIZE, color=ANCHOR_COLOR,
        )
        refine_label.move_to(DOWN * 1.2)

        # Small transport matrix
        grid_vals = [
            [0.9, 0.05, 0.05],
            [0.1, 0.8, 0.1],
            [0.05, 0.1, 0.85],
        ]
        cells = VGroup()
        for r, row in enumerate(grid_vals):
            for c, val in enumerate(row):
                cell = transport_cell(val, size=0.6)
                cell.move_to(RIGHT * (c - 1) * 0.62 + DOWN * (r - 1) * 0.62)
                cells.add(cell)
        cells.move_to(DOWN * 2.4)

        pi_label = MathTex(r"\pi^*", font_size=BODY_SIZE, color=TRANSPORT_COLOR)
        pi_label.next_to(cells, LEFT, buff=0.5)

        self.play(
            Write(refine_label),
            FadeIn(cells), Write(pi_label),
            run_time=1.0,
        )
        self.wait(HOLD_SHORT)

        self.play(FadeOut(s3_highlight), run_time=0.3)

        # ── Bottom note ───────────────────────────────────────────────
        note = bottom_note("Each stage bootstraps the next.")
        self.play(
            FadeOut(refine_label), FadeOut(cells), FadeOut(pi_label),
            run_time=0.4,
        )
        self.play(Write(note), run_time=0.8)
        self.wait(HOLD_MEDIUM)

        # ── Cleanup ───────────────────────────────────────────────────
        fade_all(
            self,
            title, s1, s2, s3, arrow_1_2, arrow_2_3, note,
        )
