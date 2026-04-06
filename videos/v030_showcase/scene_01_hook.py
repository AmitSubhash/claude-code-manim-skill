"""Scene 01: Hook -- 'What if your AI could teach like this?'

Opens with an elegant question, then the softmax attention equation
writes itself in gold. Pure visual impact in ~5 seconds.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


class HookScene(Scene):
    """5-second hook: question -> golden attention equation."""

    def construct(self) -> None:
        self.camera.background_color = BG

        # -- Question text (two lines, centered via VGroup) --
        q1 = safe_text("What if your AI", font_size=TITLE_SIZE, color=WARM_WHITE)
        q2 = safe_text("could teach like this?", font_size=TITLE_SIZE, color=WARM_WHITE)
        question = VGroup(q1, q2).arrange(DOWN, buff=0.25, center=True)
        question.move_to(ORIGIN + UP * 0.5)

        # -- Attention equation (golden, large, centered) --
        equation = MathTex(
            r"\text{Attention}(Q,K,V)",
            r"=",
            r"\text{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}}\right)",
            r"V",
            font_size=EQ_SIZE + 8,
        )
        equation.set_color(GOLD)
        equation.move_to(ORIGIN)

        # -- Glow rectangle (subtle golden border) --
        glow = SurroundingRectangle(
            equation,
            color=GOLD,
            buff=0.35,
            corner_radius=0.15,
            stroke_width=1.5,
            stroke_opacity=0.6,
        )

        # -- Animation sequence (~5s total) --

        # Fade in question (0.8s)
        self.play(FadeIn(question, shift=UP * 0.3), run_time=0.8)
        self.wait(0.4)

        # Fade out question, write equation simultaneously (1.2s)
        self.play(
            FadeOut(question, shift=UP * 0.4),
            Write(equation),
            run_time=1.2,
        )

        # Glow border fades in (0.6s)
        self.play(Create(glow), run_time=0.6)

        # Hold on the beautiful equation (1.0s)
        self.wait(1.0)
