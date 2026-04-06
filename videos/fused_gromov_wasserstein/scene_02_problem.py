"""Scene 2: The Matching Problem -- why greedy embedding matching fails.

Duration target: ~12s
Template: DUAL_PANEL
"""

import sys
sys.path.insert(0, "/Users/amit/Projects/3brown1blue/videos/fused_gromov_wasserstein")

from utils.style import *


class ProblemScene(Scene):
    def construct(self):
        # ── Title ─────────────────────────────────────────────────────
        title = section_title("The Matching Problem")

        # NARRATION: The standard approach embeds each entity,
        # then matches nearest neighbors.
        self.play(Write(title), run_time=1.0)
        self.wait(HOLD_SHORT)

        # ── Panel divider ────────────────────────────────────────────
        divider = Line(UP * 2.3, DOWN * 2.3, color=DIM_GRAY, stroke_width=1)
        self.play(Create(divider), run_time=0.5)

        # ── Panel labels ─────────────────────────────────────────────
        lbl_left = safe_text(
            "Embedding Space", font_size=LABEL_SIZE, color=MUTED_GRAY,
        )
        lbl_left.move_to(LEFT * 3.5 + UP * 2.0)

        lbl_right = safe_text(
            "Graph Structure", font_size=LABEL_SIZE, color=MUTED_GRAY,
        )
        lbl_right.move_to(RIGHT * 3.5 + UP * 2.0)

        self.play(FadeIn(lbl_left), FadeIn(lbl_right), run_time=0.5)

        # ── Left panel: embedding dots ───────────────────────────────
        # KG1 entities (blue dots)
        blue_positions = [
            LEFT * 5.0 + UP * 0.8,
            LEFT * 4.2 + DOWN * 0.3,
            LEFT * 5.3 + DOWN * 1.2,
        ]
        blue_dots = VGroup(*[
            Dot(pos, color=KG1_COLOR, radius=0.12) for pos in blue_positions
        ])
        blue_labels_text = ["A", "B", "C"]
        blue_labels = VGroup(*[
            Text(lbl, font_size=14, color=KG1_COLOR).next_to(dot, LEFT, buff=0.15)
            for lbl, dot in zip(blue_labels_text, blue_dots)
        ])

        # KG2 entities (red dots)
        red_positions = [
            LEFT * 2.0 + UP * 0.7,
            LEFT * 2.8 + DOWN * 0.4,
            LEFT * 1.8 + DOWN * 1.3,
        ]
        red_dots = VGroup(*[
            Dot(pos, color=KG2_COLOR, radius=0.12) for pos in red_positions
        ])
        red_labels_text = ["A'", "B'", "C'"]
        red_labels = VGroup(*[
            Text(lbl, font_size=14, color=KG2_COLOR).next_to(dot, RIGHT, buff=0.15)
            for lbl, dot in zip(red_labels_text, red_dots)
        ])

        self.play(
            FadeIn(blue_dots), FadeIn(blue_labels),
            FadeIn(red_dots), FadeIn(red_labels),
            run_time=1.0,
        )

        # ── Greedy match lines ───────────────────────────────────────
        # Two correct matches (green)
        match_a = Line(
            blue_dots[0].get_center(), red_dots[0].get_center(),
            color=MATCH_GOOD, stroke_width=2,
        )
        match_c = Line(
            blue_dots[2].get_center(), red_dots[2].get_center(),
            color=MATCH_GOOD, stroke_width=2,
        )
        # One wrong match (red) -- B matched to wrong target
        match_b_wrong = Line(
            blue_dots[1].get_center(), red_dots[2].get_center(),
            color=MATCH_BAD, stroke_width=3,
        )

        self.play(
            Create(match_a), Create(match_c), run_time=0.8,
        )
        self.play(Create(match_b_wrong), run_time=0.8)
        self.wait(0.5)

        # NARRATION: But greedy matching ignores something crucial...
        # graph structure.

        # ── Right panel: two small KGs with neighborhoods ────────────
        # KG1 subgraph (blue)
        n_a = kg_node("A", color=KG1_COLOR, radius=0.25, font_size=16)
        n_b = kg_node("B", color=KG1_COLOR, radius=0.25, font_size=16)
        n_c = kg_node("C", color=KG1_COLOR, radius=0.25, font_size=16)

        n_a.move_to(RIGHT * 2.2 + UP * 0.5)
        n_b.move_to(RIGHT * 3.2 + DOWN * 0.5)
        n_c.move_to(RIGHT * 2.2 + DOWN * 1.3)

        e_ab = kg_edge(n_a, n_b, color=KG1_EDGE)
        e_ac = kg_edge(n_a, n_c, color=KG1_EDGE)

        kg1_sub = VGroup(n_a, n_b, n_c, e_ab, e_ac)

        # KG2 subgraph (red) -- B' has different neighborhood
        n_a2 = kg_node("A'", color=KG2_COLOR, radius=0.25, font_size=16)
        n_b2 = kg_node("B'", color=KG2_COLOR, radius=0.25, font_size=16)
        n_c2 = kg_node("C'", color=KG2_COLOR, radius=0.25, font_size=16)

        n_a2.move_to(RIGHT * 4.8 + UP * 0.5)
        n_b2.move_to(RIGHT * 4.8 + DOWN * 0.5)
        n_c2.move_to(RIGHT * 4.8 + DOWN * 1.3)

        e_a2b2 = kg_edge(n_a2, n_b2, color=KG2_EDGE)
        # Note: B' connects to A' only, not C' -- different neighborhood

        kg2_sub = VGroup(n_a2, n_b2, n_c2, e_a2b2)

        self.play(FadeIn(kg1_sub), FadeIn(kg2_sub), run_time=1.0)
        self.wait(0.5)

        # NARRATION: If two entities have similar names but different
        # neighborhoods, should they really match?

        # ── Red X on the wrong match ─────────────────────────────────
        cross_center = match_b_wrong.get_center()
        cross = VGroup(
            Line(cross_center + UL * 0.2, cross_center + DR * 0.2,
                 color=MATCH_BAD, stroke_width=5),
            Line(cross_center + UR * 0.2, cross_center + DL * 0.2,
                 color=MATCH_BAD, stroke_width=5),
        )
        self.play(Create(cross), run_time=0.5)
        self.wait(0.5)

        # ── Bottom note ──────────────────────────────────────────────
        note = bottom_note("Embeddings lose structure.")
        self.play(Write(note), run_time=0.8)
        self.wait(HOLD_MEDIUM)

        # ── Cleanup ──────────────────────────────────────────────────
        fade_all(
            self,
            title, divider, lbl_left, lbl_right,
            blue_dots, blue_labels, red_dots, red_labels,
            match_a, match_b_wrong, match_c, cross,
            kg1_sub, kg2_sub, note,
        )
