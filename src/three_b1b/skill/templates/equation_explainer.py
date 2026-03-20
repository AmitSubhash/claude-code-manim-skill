"""Template: Dim-and-reveal equation explainer scene.

Copy this file, replace YOUR_EQUATION and the reveals list with your
equation and terms. Claude should adapt, not follow rigidly.
"""

from manim import *

# If using a multi-file project, import your shared style:
# import sys; from pathlib import Path
# sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# from utils.style import *

# Otherwise, define inline:
EQ_SIZE = 44
LABEL_SIZE = 24
HOLD_SHORT = 1.0
HOLD_MEDIUM = 2.0
HOLD_LONG = 3.0


class EquationExplainer(Scene):
    def construct(self) -> None:
        title = Text("Your Equation Title", font_size=36).to_edge(UP)
        self.play(Write(title))

        # ── Write the full equation ──────────────────────────────
        # Split into parts with separate strings so each is targetable.
        eq = MathTex(
            r"\text{LHS}",     # index 0
            r"=",              # index 1
            r"\text{term}_1",  # index 2
            r"+",              # index 3
            r"\text{term}_2",  # index 4
            font_size=EQ_SIZE,
        )
        self.play(Write(eq))
        self.wait(HOLD_MEDIUM)  # let viewer see the shape

        # ── Dim everything ───────────────────────────────────────
        self.play(eq.animate.set_opacity(0.3))
        self.wait(HOLD_SHORT)

        # ── Reveal term by term ──────────────────────────────────
        # Each tuple: (indices into eq, color, label text)
        # Adapt this list to your equation.
        reveals = [
            ([0], BLUE, "Left-hand side: what we compute"),
            ([2], RED, "First term: description"),
            ([4], GREEN, "Second term: description"),
        ]

        for indices, color, label_text in reveals:
            parts = VGroup(*[eq[i] for i in indices])
            for p in parts:
                p.set_opacity(1.0)
            box = SurroundingRectangle(parts, color=color, buff=0.1)
            label = Text(label_text, font_size=LABEL_SIZE, color=color)
            label.next_to(box, DOWN, buff=0.3)

            self.play(Create(box), Write(label))
            self.wait(HOLD_MEDIUM)
            self.play(FadeOut(box), FadeOut(label))

            for p in parts:
                p.set_color(color)

        # ── Un-dim: show color-coded equation ────────────────────
        self.play(eq.animate.set_opacity(1.0))
        self.wait(HOLD_LONG)
