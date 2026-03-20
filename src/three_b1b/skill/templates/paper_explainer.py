"""Template: Paper explainer video scaffold.

Copy this file and fill in each section. Each phase uses next_section()
for logical breaks but stays in ONE Scene class for visual continuity.
Adapt freely -- this is a starting point, not a rigid script.
"""

import sys
from pathlib import Path

# For multi-file projects:
# sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# from utils.style import *

from manim import *


class PaperExplainer(Scene):
    """Scaffold for a ~5 minute paper explainer video.

    Phases: Hook -> Problem -> Method -> Results -> Takeaway
    Adapt durations and content to your paper.
    """

    def construct(self) -> None:
        # ── HOOK (10s): show the punchline first ────────────────
        self.next_section("Hook")

        # TODO: Replace with your paper's key result
        result = Text("Your key result here", font_size=48, color=YELLOW)
        self.play(Write(result))
        self.wait(2)
        question = Text("How?", font_size=72, color=WHITE)
        self.play(ReplacementTransform(result, question))
        self.wait(1)
        self.play(FadeOut(question))

        # ── PROBLEM (30s): what gap exists? ─────────────────────
        self.next_section("Problem")

        # TODO: Explain the problem your paper solves
        # Use labeled_box() for diagrams, Text for descriptions
        problem = Text("The problem:\nYour description here", font_size=36)
        self.play(Write(problem))
        self.wait(3)
        self.play(FadeOut(problem))

        # ── METHOD (120s): your core contribution ───────────────
        self.next_section("Method")

        # TODO: This is the main section. Options:
        # - Equation dim-and-reveal (copy from equation_explainer.py)
        # - Pipeline diagram (labeled_box + Arrows)
        # - Architecture buildup (bottom-to-top with next_section)
        method_title = Text("Our Approach", font_size=48)
        self.play(Write(method_title))
        self.wait(2)

        # Example: show your key equation
        eq = MathTex(r"y = f(x)", font_size=44)
        eq.next_to(method_title, DOWN, buff=1)
        self.play(Write(eq))
        self.wait(3)
        self.play(FadeOut(method_title, eq))

        # ── RESULTS (60s): evidence it works ────────────────────
        self.next_section("Results")

        # TODO: Bar charts, training curves, comparison tables
        results_title = Text("Results", font_size=48)
        self.play(Write(results_title))
        self.wait(2)
        self.play(FadeOut(results_title))

        # ── TAKEAWAY (20s): one sentence to remember ────────────
        self.next_section("Takeaway")

        # TODO: Replace with your paper's core message
        takeaway = Text(
            "One sentence the viewer should remember.",
            font_size=36, color=YELLOW,
        )
        self.play(Write(takeaway))
        self.wait(3)
        self.play(FadeOut(takeaway))
