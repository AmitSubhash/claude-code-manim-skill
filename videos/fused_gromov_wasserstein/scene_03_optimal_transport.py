"""Scene 3: Optimal Transport -- warehouses to stores, then matrix form.

Duration target: ~14s
Template: BUILD_UP
"""

import sys
sys.path.insert(0, "/Users/amit/Projects/3brown1blue/videos/fused_gromov_wasserstein")

from utils.style import *


class OptimalTransportScene(Scene):
    def construct(self):
        # ── Title ─────────────────────────────────────────────────────
        title = section_title("Optimal Transport")

        # NARRATION: Optimal transport finds the cheapest way to move
        # mass from one distribution to another.
        self.play(Write(title), run_time=1.0)
        self.wait(HOLD_SHORT)

        # ── Geometry: warehouses (blue) and stores (red) ─────────────
        # NARRATION: Think of it as shipping goods from warehouses
        # to stores.

        warehouse_labels = ["W1", "W2", "W3"]
        store_labels = ["S1", "S2", "S3"]

        warehouses = VGroup()
        for i, lbl in enumerate(warehouse_labels):
            sq = Square(side_length=0.5, color=KG1_COLOR, fill_opacity=0.3)
            txt = Text(lbl, font_size=16, color=KG1_COLOR)
            txt.move_to(sq)
            node = VGroup(sq, txt)
            warehouses.add(node)
        warehouses.arrange(DOWN, buff=0.6)
        warehouses.move_to(LEFT * 4.0 + DOWN * 0.3)

        stores = VGroup()
        for i, lbl in enumerate(store_labels):
            sq = Square(side_length=0.5, color=KG2_COLOR, fill_opacity=0.3)
            txt = Text(lbl, font_size=16, color=KG2_COLOR)
            txt.move_to(sq)
            node = VGroup(sq, txt)
            stores.add(node)
        stores.arrange(DOWN, buff=0.6)
        stores.move_to(RIGHT * 4.0 + DOWN * 0.3)

        # Labels above
        w_label = safe_text("Warehouses", font_size=LABEL_SIZE, color=KG1_COLOR)
        w_label.next_to(warehouses, UP, buff=0.3)
        s_label = safe_text("Stores", font_size=LABEL_SIZE, color=KG2_COLOR)
        s_label.next_to(stores, UP, buff=0.3)

        self.play(
            FadeIn(warehouses, shift=RIGHT * 0.2),
            FadeIn(w_label),
            FadeIn(stores, shift=LEFT * 0.2),
            FadeIn(s_label),
            run_time=1.0,
        )
        self.wait(0.5)

        # ── Shipping arrows with varying thickness ───────────────────
        # Transport amounts (rows = warehouses, cols = stores)
        transport_values = [
            [0.8, 0.1, 0.1],
            [0.1, 0.7, 0.2],
            [0.2, 0.1, 0.7],
        ]

        arrows = VGroup()
        for i in range(3):
            for j in range(3):
                val = transport_values[i][j]
                if val < 0.05:
                    continue
                arrow = Line(
                    warehouses[i].get_right() + RIGHT * 0.05,
                    stores[j].get_left() + LEFT * 0.05,
                    color=TRANSPORT_COLOR,
                    stroke_width=val * 6,
                    stroke_opacity=0.3 + val * 0.7,
                )
                arrows.add(arrow)

        self.play(
            *[Create(a) for a in arrows],
            run_time=1.5,
        )
        self.wait(HOLD_SHORT)

        # NARRATION: The transport plan is a matrix... and finding
        # the best one is a linear program.

        # ── Transform into matrix ────────────────────────────────────
        # Fade out the geometry
        fade_all(
            self,
            warehouses, stores, arrows, w_label, s_label,
        )

        # Build transport matrix from transport_cell()
        cells = VGroup()
        for i in range(3):
            for j in range(3):
                cell = transport_cell(transport_values[i][j], size=0.7)
                cells.add(cell)
        cells.arrange_in_grid(3, 3, buff=0.05)
        cells.move_to(ORIGIN + UP * 0.2)

        # Row labels (warehouses)
        row_labels = VGroup(*[
            Text(f"W{i+1}", font_size=16, color=KG1_COLOR)
            for i in range(3)
        ])
        for i, rl in enumerate(row_labels):
            rl.next_to(cells[i * 3], LEFT, buff=0.3)

        # Column labels (stores)
        col_labels = VGroup(*[
            Text(f"S{j+1}", font_size=16, color=KG2_COLOR)
            for j in range(3)
        ])
        for j, cl in enumerate(col_labels):
            cl.next_to(cells[j], UP, buff=0.3)

        # Matrix label
        pi_label = MathTex(r"\pi", font_size=EQ_SIZE, color=TRANSPORT_COLOR)
        pi_label.next_to(cells, LEFT, buff=1.0)
        eq_sign = MathTex("=", font_size=EQ_SIZE)
        eq_sign.next_to(pi_label, RIGHT, buff=0.3)

        matrix_group = VGroup(cells, row_labels, col_labels, pi_label, eq_sign)

        self.play(FadeIn(matrix_group, shift=UP * 0.3), run_time=1.5)
        self.wait(HOLD_SHORT)

        # ── Equation ─────────────────────────────────────────────────
        equation = MathTex(
            r"\min_{\pi} \sum_{i,j} C_{ij} \cdot \pi_{ij}",
            font_size=EQ_SMALL,
        )
        equation.next_to(cells, DOWN, buff=0.8)

        # Constraint annotations
        row_constraint = safe_text(
            "Row sums = supply", font_size=18, color=KG1_COLOR,
        )
        col_constraint = safe_text(
            "Col sums = demand", font_size=18, color=KG2_COLOR,
        )
        constraints = VGroup(row_constraint, col_constraint).arrange(
            RIGHT, buff=1.0,
        )
        constraints.next_to(equation, DOWN, buff=0.4)

        self.play(Write(equation), run_time=1.0)
        self.play(FadeIn(constraints, shift=UP * 0.15), run_time=0.8)
        self.wait(0.5)

        # ── Bottom note ──────────────────────────────────────────────
        note = bottom_note(
            "The transport plan pi is a soft matching matrix.",
        )
        self.play(Write(note), run_time=0.8)
        self.wait(HOLD_MEDIUM)

        # ── Cleanup ──────────────────────────────────────────────────
        fade_all(
            self,
            title, matrix_group, equation, constraints, note,
        )
