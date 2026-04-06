"""Scene 04: Neural network / knowledge graph visualization."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


class NetworkGraphScene(Scene):
    def construct(self):
        self.camera.background_color = BG

        # -- Node positions ----------------------------------------------------
        L = [np.array([-4, 2 - i * 1.3, 0]) for i in range(4)]
        C = [np.array([0, 1, 0]), np.array([0, -0.8, 0])]
        R = [np.array([4, 2 - i * 1.3, 0]) for i in range(4)]

        def make_node(pos, text, color, r=0.28):
            glow = Circle(radius=r + 0.08, color=color, fill_opacity=0.06,
                          stroke_width=0).move_to(pos)
            ring = Circle(radius=r, color=color, fill_opacity=0.15,
                          stroke_width=2.5).move_to(pos)
            lbl = Text(text, font=MONO, font_size=14, color=color).move_to(pos)
            return VGroup(glow, ring, lbl)

        left_nodes = [make_node(p, f"Q{i+1}", ELECTRIC) for i, p in enumerate(L)]
        center_nodes = [make_node(p, f"V{i+1}", GOLD) for i, p in enumerate(C)]
        right_nodes = [make_node(p, f"K{i+1}", CORAL) for i, p in enumerate(R)]
        all_nodes = left_nodes + center_nodes + right_nodes

        # -- Nodes appear with stagger ----------------------------------------
        self.play(
            LaggedStart(
                *[FadeIn(n, scale=0.5, rate_func=smooth) for n in all_nodes],
                lag_ratio=0.08,
            ),
            run_time=1.8,
        )
        self.wait(0.3)

        # -- Edges with attention-weight opacity -------------------------------
        conn = [
            (L[0], C[0], 0.6, ELECTRIC), (L[1], C[0], 0.3, ELECTRIC),
            (L[1], C[1], 0.8, ELECTRIC), (L[2], C[1], 0.5, ELECTRIC),
            (L[3], C[0], 0.4, ELECTRIC), (L[3], C[1], 0.7, ELECTRIC),
            (C[0], R[0], 0.7, GOLD), (C[0], R[1], 0.4, GOLD),
            (C[0], R[2], 0.5, GOLD), (C[1], R[1], 0.8, GOLD),
            (C[1], R[2], 0.3, GOLD), (C[1], R[3], 0.9, GOLD),
            (L[0], R[0], 0.15, SLATE), (L[2], R[3], 0.15, SLATE),
        ]

        def curved(s, e, opac, col, sw=1.5, tip=0.15):
            ang = 0.3 if s[1] > e[1] else -0.3
            return CurvedArrow(s, e, angle=ang, color=col, stroke_width=sw,
                               stroke_opacity=opac, tip_length=tip)

        edges = [curved(s, e, o, c) for s, e, o, c in conn]
        self.play(
            LaggedStart(*[Create(e, rate_func=rush_from) for e in edges],
                        lag_ratio=0.04),
            run_time=1.5,
        )
        self.wait(0.3)

        # -- Attention pulse: Q1 activates through V1 to keys -----------------
        query_glow = Circle(radius=0.55, color=ELECTRIC, fill_opacity=0.25,
                            stroke_width=0).move_to(L[0])
        highlights = [
            curved(L[0], C[0], 0.9, MINT, 3.5, 0.18),
            curved(C[0], R[0], 0.9, MINT, 3.5, 0.18),
            curved(C[0], R[1], 0.6, MINT, 2.5, 0.18),
            curved(C[0], R[2], 0.3, MINT, 1.5, 0.18),
        ]

        self.play(
            FadeIn(query_glow, rate_func=there_and_back, run_time=1.2),
            LaggedStart(*[Create(a, rate_func=smooth) for a in highlights],
                        lag_ratio=0.12),
            run_time=1.5,
        )
        self.play(
            query_glow.animate.scale(1.3).set_opacity(0),
            rate_func=smooth, run_time=0.8,
        )

        # -- Bottom caption ----------------------------------------------------
        caption = safe_text(
            "Graph theory, attention maps, knowledge graphs",
            font_size=BODY_SIZE, color=TEAL,
        ).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(caption, shift=UP * 0.2), run_time=0.6)
        self.wait(1.5)
