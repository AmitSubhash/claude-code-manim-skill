"""Scene 05: Elegant data pipeline visualization."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


class PipelineScene(Scene):
    def construct(self):
        self.camera.background_color = BG

        # -- Title -------------------------------------------------------------
        title = safe_text("From paper to video in minutes",
                          font_size=TITLE_SIZE, color=GOLD).to_edge(UP, buff=0.6)
        self.play(Write(title, rate_func=smooth), run_time=1.0)

        # -- Build stage cards with icons -------------------------------------
        stage_defs = [
            ("Read", ELECTRIC, self._doc_icon),
            ("Plan", TEAL, self._grid_icon),
            ("Animate", CORAL, self._play_icon),
            ("Narrate", VIOLET, self._wave_icon),
        ]
        xs = [-4.2, -1.4, 1.4, 4.2]
        cards, icons = [], []
        for i, (label, color, icon_fn) in enumerate(stage_defs):
            box = RoundedRectangle(corner_radius=0.2, width=2.0, height=1.6,
                                   color=color, fill_opacity=0.06,
                                   stroke_width=1.8).move_to([xs[i], 0, 0])
            txt = Text(label, font=MONO, font_size=LABEL_SIZE,
                       color=color).move_to(box.get_center() + DOWN * 0.4)
            card = VGroup(box, txt)
            icon = icon_fn(color).scale(0.55).move_to(box.get_center() + UP * 0.25)
            cards.append(card)
            icons.append(icon)

        # Connector lines
        connectors = [
            Line(cards[i].get_right() + RIGHT * 0.05,
                 cards[i + 1].get_left() + LEFT * 0.05,
                 color=SLATE, stroke_width=1.8, stroke_opacity=0.5)
            for i in range(3)
        ]

        # -- Animate cards left-to-right --------------------------------------
        self.play(LaggedStart(
            *[AnimationGroup(FadeIn(c, scale=0.7), FadeIn(ic, scale=0.5))
              for c, ic in zip(cards, icons)],
            lag_ratio=0.2), run_time=1.5)
        self.play(LaggedStart(
            *[Create(c, rate_func=rush_from) for c in connectors],
            lag_ratio=0.15), run_time=0.6)
        self.wait(0.2)

        # -- Flowing dot morphs color through stages --------------------------
        stage_colors = [ELECTRIC, TEAL, CORAL, VIOLET]
        dot = Dot(cards[0].get_center(), radius=0.12, color=ELECTRIC,
                  fill_opacity=0.9)
        glow = Dot(cards[0].get_center(), radius=0.25, color=ELECTRIC,
                   fill_opacity=0.25)
        self.play(FadeIn(dot), FadeIn(glow), run_time=0.3)
        for i in range(1, 4):
            tgt = cards[i].get_center()
            self.play(
                dot.animate.move_to(tgt).set_color(stage_colors[i]),
                glow.animate.move_to(tgt).set_color(stage_colors[i]),
                rate_func=smooth, run_time=0.6)
        self.play(FadeOut(dot), FadeOut(glow), run_time=0.3)

        # -- Waveform bars expand at Narrate stage ----------------------------
        bar_h = [0.5, 0.9, 0.35, 0.75, 0.6]
        bx = cards[3].get_center()[0] - 0.4
        by = cards[3].get_bottom()[1] - 0.6
        bars = VGroup(*[
            Rectangle(width=0.12, height=h * 0.6, color=VIOLET,
                      fill_opacity=0.7, stroke_width=0).move_to([bx + j * 0.2, by, 0])
            for j, h in enumerate(bar_h)
        ])
        self.play(LaggedStart(
            *[GrowFromCenter(b, rate_func=smooth) for b in bars],
            lag_ratio=0.08), run_time=0.7)
        # Pulse cycle
        targets = [0.8, 0.4, 1.0, 0.55, 0.7]
        self.play(*[b.animate.stretch_to_fit_height(t * 0.6)
                    for b, t in zip(bars, targets)],
                  rate_func=there_and_back, run_time=0.8)

        # -- Bottom caption ----------------------------------------------------
        caption = safe_text("Kokoro TTS. Teaching tone. Beat-synced.",
                            font_size=BODY_SIZE, color=MINT).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(caption, shift=UP * 0.2), run_time=0.6)
        self.wait(1.5)

    # -- Icon helpers (compact) ------------------------------------------------
    @staticmethod
    def _doc_icon(color):
        pg = Rectangle(width=0.5, height=0.65, color=color, stroke_width=1.5,
                       fill_opacity=0.1)
        lns = VGroup(*[Line(LEFT * 0.15, RIGHT * 0.15, color=color,
                            stroke_width=1.2, stroke_opacity=0.6
                            ).shift(UP * (0.12 - i * 0.12)) for i in range(3)])
        return VGroup(pg, lns.move_to(pg))

    @staticmethod
    def _grid_icon(color):
        g = VGroup(*[Square(side_length=0.22, color=color, stroke_width=1.5,
                            fill_opacity=0.1).shift(RIGHT * c * 0.28 + DOWN * r * 0.28)
                     for r in range(2) for c in range(2)])
        return g.center()

    @staticmethod
    def _play_icon(color):
        return Triangle(color=color, fill_opacity=0.2,
                        stroke_width=1.5).scale(0.25).rotate(-PI / 2)

    @staticmethod
    def _wave_icon(color):
        return FunctionGraph(lambda x: 0.15 * np.sin(4 * x),
                             x_range=[-0.5, 0.5, 0.01], color=color, stroke_width=2)
