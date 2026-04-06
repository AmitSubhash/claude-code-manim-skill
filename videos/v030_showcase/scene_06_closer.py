"""Scene 06: Bold closing with version, stats, and install CTA."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


class CloserScene(Scene):
    def construct(self):
        self.camera.background_color = BG

        # -- Subtle radial vignette glow behind version text -------------------
        glow = Circle(
            radius=2.5, color=GOLD, fill_opacity=0.03, stroke_width=0,
        ).move_to(ORIGIN)

        # -- Large version number with scale-up entrance -----------------------
        version = Text(
            "v0.3.0", font=MONO, font_size=72, color=GOLD,
            weight=BOLD,
        ).move_to(UP * 1.0)
        version.scale(0.8)

        self.play(
            FadeIn(glow, run_time=0.5),
            version.animate.scale(1.0 / 0.8),
            rate_func=smooth,
            run_time=1.2,
        )

        # -- Three stat lines, staggered fade-in ------------------------------
        stats = [
            ("17 design principles", TEAL),
            ("26 visual patterns", ELECTRIC),
            ("3 voiceover backends", CORAL),
        ]
        stat_texts = []
        for i, (text, color) in enumerate(stats):
            t = safe_text(text, font_size=BODY_SIZE, color=color)
            t.move_to(DOWN * (0.3 + i * 0.55))
            stat_texts.append(t)

        self.play(
            LaggedStart(
                *[FadeIn(t, shift=UP * 0.15) for t in stat_texts],
                lag_ratio=0.25,
            ),
            run_time=1.5,
        )
        self.wait(1.0)

        # -- pip install command in a rounded box ------------------------------
        pip_text = Text(
            "pip install 3brown1blue",
            font=MONO, font_size=BODY_SIZE, color=WARM_WHITE,
        )
        pip_box = RoundedRectangle(
            corner_radius=0.2,
            width=pip_text.width + 0.8,
            height=pip_text.height + 0.5,
            color=GOLD,
            stroke_width=2.0,
            fill_opacity=0.05,
        )
        pip_group = VGroup(pip_box, pip_text).move_to(DOWN * 2.2)

        # -- GitHub URL --------------------------------------------------------
        github_url = safe_text(
            "github.com/AmitSubhash/3brown1blue",
            font_size=LABEL_SIZE, color=SLATE,
        ).next_to(pip_group, DOWN, buff=0.35)

        self.play(
            pip_group.animate.shift(ORIGIN).set_opacity(1),
            FadeIn(pip_group, shift=UP * 0.4, rate_func=smooth),
            run_time=0.8,
        )
        self.play(
            FadeIn(github_url, shift=UP * 0.15),
            run_time=0.5,
        )

        # -- Subtle glow pulse on the version to draw eye back ----------------
        version_glow = version.copy().set_opacity(0.3).set_color(GOLD)
        self.play(
            FadeIn(version_glow, rate_func=there_and_back),
            run_time=1.0,
        )
        self.remove(version_glow)

        self.wait(2.0)
