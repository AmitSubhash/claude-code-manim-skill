"""Scene 4: Gromov-Wasserstein Distance -- structure-preserving matching.

Duration target: ~16s
Template: FULL_CENTER
"""

import sys
sys.path.insert(0, "/Users/amit/Projects/3brown1blue/videos/fused_gromov_wasserstein")

from utils.style import *


class GromovWassersteinScene(Scene):
    def construct(self) -> None:
        # ── Title ─────────────────────────────────────────────────────
        title = section_title("Gromov-Wasserstein Distance")

        # NARRATION: But what if you cannot compare items directly
        # across domains?
        self.play(Write(title), run_time=1.0)
        self.wait(HOLD_SHORT)

        # ── Social network analogy: two friend groups ─────────────────
        # Left group (blue): Alice, Bob, Carol
        alice = kg_node("Alice", color=KG1_COLOR)
        bob = kg_node("Bob", color=KG1_COLOR)
        carol = kg_node("Carol", color=KG1_COLOR)

        alice.move_to(LEFT * 4.0 + UP * 1.0)
        bob.move_to(LEFT * 5.5 + DOWN * 0.8)
        carol.move_to(LEFT * 2.5 + DOWN * 0.8)

        e_ab = kg_edge(alice, bob, "friends", color=KG1_EDGE)
        e_ac = kg_edge(alice, carol, "friends", color=KG1_EDGE)

        left_group = VGroup(alice, bob, carol, e_ab, e_ac)

        # Right group (red): X, Y, Z
        x_node = kg_node("X", color=KG2_COLOR)
        y_node = kg_node("Y", color=KG2_COLOR)
        z_node = kg_node("Z", color=KG2_COLOR)

        x_node.move_to(RIGHT * 4.0 + UP * 1.0)
        y_node.move_to(RIGHT * 2.5 + DOWN * 0.8)
        z_node.move_to(RIGHT * 5.5 + DOWN * 0.8)

        e_xy = kg_edge(x_node, y_node, "friends", color=KG2_EDGE)
        e_xz = kg_edge(x_node, z_node, "friends", color=KG2_EDGE)

        right_group = VGroup(x_node, y_node, z_node, e_xy, e_xz)

        # Group labels
        lbl_left = safe_text("Group 1", font_size=LABEL_SIZE, color=KG1_COLOR)
        lbl_left.next_to(left_group, UP, buff=0.5)
        lbl_right = safe_text("Group 2", font_size=LABEL_SIZE, color=KG2_COLOR)
        lbl_right.next_to(right_group, UP, buff=0.5)

        # NARRATION: Gromov-Wasserstein compares internal structures
        # instead.
        self.play(
            FadeIn(left_group, shift=LEFT * 0.3),
            FadeIn(lbl_left),
            FadeIn(right_group, shift=RIGHT * 0.3),
            FadeIn(lbl_right),
            run_time=1.2,
        )
        self.wait(HOLD_SHORT)

        # ── Good mapping: friends -> friends (green check) ────────────
        # NARRATION: If Alice and Bob are friends, then whoever they
        # map to should also be friends.
        good_a_x = alignment_arrow(alice, x_node, color=MATCH_GOOD)
        good_b_y = alignment_arrow(bob, y_node, color=MATCH_GOOD)
        good_c_z = alignment_arrow(carol, z_node, color=MATCH_GOOD)

        self.play(Create(good_a_x), Create(good_b_y), Create(good_c_z),
                  run_time=1.0)

        check = safe_text("Friends map to friends", font_size=LABEL_SIZE,
                          color=MATCH_GOOD)
        check_icon = Text("\u2713", font_size=TITLE_SIZE, color=MATCH_GOOD)
        check_row = VGroup(check_icon, check).arrange(RIGHT, buff=0.3)
        check_row.move_to(DOWN * 2.3)

        self.play(Write(check_row), run_time=0.8)
        self.wait(HOLD_SHORT)

        # ── Bad mapping: friends -> non-friends (red X) ───────────────
        self.play(
            FadeOut(good_a_x), FadeOut(good_b_y), FadeOut(good_c_z),
            FadeOut(check_row),
            run_time=0.6,
        )

        bad_a_x = alignment_arrow(alice, x_node, color=MATCH_BAD)
        bad_b_z = alignment_arrow(bob, z_node, color=MATCH_BAD)
        bad_c_y = alignment_arrow(carol, y_node, color=MATCH_BAD)

        self.play(Create(bad_a_x), Create(bad_b_z), Create(bad_c_y),
                  run_time=1.0)

        x_mark = Text("\u2717", font_size=TITLE_SIZE, color=MATCH_BAD)
        bad_label = safe_text("Bob-Carol not friends, but Y-Z are",
                              font_size=LABEL_SIZE, color=MATCH_BAD)
        bad_row = VGroup(x_mark, bad_label).arrange(RIGHT, buff=0.3)
        bad_row.move_to(DOWN * 2.3)

        self.play(Write(bad_row), run_time=0.8)
        self.wait(HOLD_SHORT)

        # ── Clear networks, show GWD equation ─────────────────────────
        fade_all(
            self,
            left_group, right_group, lbl_left, lbl_right,
            bad_a_x, bad_b_z, bad_c_y, bad_row,
        )

        # GWD equation with substrings for dim-highlight
        gwd_eq = MathTex(
            r"\text{GWD}",
            r"=",
            r"\min_{\pi}",
            r"\sum_{i,j,k,l}",
            r"|A_{ij} - A'_{kl}|^2",
            r"\cdot",
            r"\pi_{ik}",
            r"\pi_{jl}",
            font_size=EQ_SIZE,
        )
        gwd_eq.move_to(UP * 0.8)

        self.play(Write(gwd_eq), run_time=1.5)
        self.wait(HOLD_MEDIUM)

        # Dim everything for decomposition
        self.play(gwd_eq.animate.set_opacity(0.3), run_time=0.5)

        # Highlight structure term: |A_ij - A'_kl|^2
        struct_part = gwd_eq[4]
        struct_part.set_opacity(1)
        struct_rect = SurroundingRectangle(struct_part, color=STRUCTURE_COLOR,
                                           buff=0.1)
        struct_brace = Brace(struct_part, DOWN, color=STRUCTURE_COLOR)
        struct_label = Text(
            "Do matched pairs have\nthe same relationship?",
            font_size=LABEL_SIZE, color=STRUCTURE_COLOR,
        )
        struct_label.next_to(struct_brace, DOWN, buff=0.1)

        self.play(
            Create(struct_rect), Create(struct_brace),
            Write(struct_label), run_time=0.8,
        )
        self.wait(HOLD_MEDIUM)
        self.play(
            FadeOut(struct_rect), FadeOut(struct_brace),
            FadeOut(struct_label), run_time=0.5,
        )
        struct_part.set_color(STRUCTURE_COLOR)

        # Highlight coupling term: pi_ik * pi_jl
        coupling_parts = VGroup(gwd_eq[6], gwd_eq[7])
        for part in coupling_parts:
            part.set_opacity(1)
        coupling_rect = SurroundingRectangle(coupling_parts,
                                              color=TRANSPORT_COLOR, buff=0.1)
        coupling_brace = Brace(coupling_parts, DOWN, color=TRANSPORT_COLOR)
        coupling_label = Text(
            "The coupling between\ntwo matchings",
            font_size=LABEL_SIZE, color=TRANSPORT_COLOR,
        )
        coupling_label.next_to(coupling_brace, DOWN, buff=0.1)

        self.play(
            Create(coupling_rect), Create(coupling_brace),
            Write(coupling_label), run_time=0.8,
        )
        self.wait(HOLD_MEDIUM)
        self.play(
            FadeOut(coupling_rect), FadeOut(coupling_brace),
            FadeOut(coupling_label), run_time=0.5,
        )
        for part in coupling_parts:
            part.set_color(TRANSPORT_COLOR)

        # Un-dim remaining parts
        remaining = [gwd_eq[i] for i in [0, 1, 2, 3, 5]]
        self.play(*[m.animate.set_opacity(1) for m in remaining], run_time=0.5)
        self.wait(HOLD_SHORT)

        # ── FGW equation ──────────────────────────────────────────────
        # NARRATION: Fused GW combines both... match entities that are
        # similar AND whose neighborhoods match up.
        self.play(gwd_eq.animate.shift(UP * 1.0).scale(0.8), run_time=0.7)

        fgw_eq = MathTex(
            r"\text{FGW}",
            r"=",
            r"\alpha",
            r"\cdot",
            r"\text{WD}",
            r"+",
            r"(1-\alpha)",
            r"\cdot",
            r"\text{GWD}",
            font_size=EQ_SIZE,
        )
        fgw_eq.move_to(DOWN * 0.5)

        self.play(Write(fgw_eq), run_time=1.0)
        self.wait(HOLD_SHORT)

        # Color WD (features) and GWD (structure)
        wd_part = fgw_eq[4]
        gwd_part = fgw_eq[8]
        alpha_wd = VGroup(fgw_eq[2], fgw_eq[3], fgw_eq[4])
        alpha_gwd = VGroup(fgw_eq[6], fgw_eq[7], fgw_eq[8])

        wd_rect = SurroundingRectangle(alpha_wd, color=FEATURE_COLOR, buff=0.1)
        gwd_rect = SurroundingRectangle(alpha_gwd, color=STRUCTURE_COLOR,
                                         buff=0.1)
        wd_label = safe_text("Features", font_size=LABEL_SIZE,
                             color=FEATURE_COLOR)
        wd_label.next_to(wd_rect, DOWN, buff=0.5)
        gwd_label = safe_text("Structure", font_size=LABEL_SIZE,
                              color=STRUCTURE_COLOR)
        gwd_label.next_to(gwd_rect, DOWN, buff=0.5)

        self.play(
            Create(wd_rect), Write(wd_label),
            Create(gwd_rect), Write(gwd_label),
            wd_part.animate.set_color(FEATURE_COLOR),
            gwd_part.animate.set_color(STRUCTURE_COLOR),
            run_time=1.0,
        )
        self.wait(HOLD_SHORT)

        # ── Bottom note ───────────────────────────────────────────────
        note = bottom_note("FGW: features + structure, jointly optimized.")
        self.play(Write(note), run_time=0.8)
        self.wait(HOLD_MEDIUM)

        # ── Cleanup ───────────────────────────────────────────────────
        fade_all(
            self,
            title, gwd_eq, fgw_eq,
            wd_rect, gwd_rect, wd_label, gwd_label, note,
        )
