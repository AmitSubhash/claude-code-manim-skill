"""3brown1blue v0.3.0 release marketing video (~20s)."""

from manim import *


# -- Palette ----------------------------------------------------------------
BG = "#1a1a2e"
GOLD = "#FFD700"
TEAL = "#2EC4B6"
CORAL = "#FF6B6B"
BLUE = "#4EA8DE"
SLATE = "#8B8FA8"
WHITE_T = "#F0F0F0"
MONO = "Menlo"


class ReleaseScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG

        # ── Phase 1: Logo + version (0-3s) ─────────────────────────
        logo = Text("3brown1blue", font=MONO, font_size=56, color=GOLD)
        version = Text("v0.3.0", font=MONO, font_size=36, color=TEAL)
        version.next_to(logo, DOWN, buff=0.3)
        tagline = Text(
            "AI-powered Manim explainer videos",
            font=MONO, font_size=22, color=SLATE,
        )
        tagline.next_to(version, DOWN, buff=0.4)

        self.play(Write(logo), run_time=0.8)
        self.play(FadeIn(version, shift=UP * 0.2), run_time=0.5)
        self.play(FadeIn(tagline, shift=UP * 0.15), run_time=0.4)
        self.wait(0.8)

        # ── Phase 2: Feature cards fly in (3-12s) ──────────────────
        self.play(
            FadeOut(tagline),
            logo.animate.scale(0.5).to_corner(UL, buff=0.4),
            version.animate.scale(0.5).to_corner(UL, buff=0.4).shift(DOWN * 0.5),
            run_time=0.7,
        )

        features = [
            ("17 Design Principles", "cognitive science-backed", TEAL),
            ("26 Visual Patterns", "from 3b1b frame analysis", BLUE),
            ("Voiceover Pipeline", "Kokoro + VibeVoice + Chatterbox", CORAL),
            ("Single-Scene Mode", "generate -1 for quick demos", GOLD),
            ("13 Audit Patterns", "from real production bugs", TEAL),
            ("4 Narrative Arcs", "adopted from Hermes", BLUE),
        ]

        cards = VGroup()
        for title, subtitle, color in features:
            card_bg = RoundedRectangle(
                width=5.0, height=0.8, corner_radius=0.1,
                color=color, fill_opacity=0.15, stroke_width=1.5,
            )
            card_title = Text(title, font=MONO, font_size=20, color=color)
            card_sub = Text(subtitle, font=MONO, font_size=14, color=SLATE)
            card_title.move_to(card_bg).shift(UP * 0.12)
            card_sub.move_to(card_bg).shift(DOWN * 0.18)
            card = VGroup(card_bg, card_title, card_sub)
            cards.add(card)

        cards.arrange(DOWN, buff=0.15)
        cards.move_to(ORIGIN + DOWN * 0.2)

        for i, card in enumerate(cards):
            direction = LEFT if i % 2 == 0 else RIGHT
            card.shift(direction * 8)

        for i, card in enumerate(cards):
            direction = LEFT if i % 2 == 0 else RIGHT
            self.play(
                card.animate.shift(-direction * 8),
                run_time=0.35,
                rate_func=rush_from,
            )

        self.wait(1.5)

        # ── Phase 3: pip install callout (12-16s) ──────────────────
        self.play(*[card.animate.set_opacity(0.3) for card in cards], run_time=0.4)

        install_bg = RoundedRectangle(
            width=8.0, height=1.0, corner_radius=0.15,
            color=GOLD, fill_opacity=0.1, stroke_width=2,
        )
        install_cmd = Text(
            "pip install 3brown1blue==0.3.0",
            font=MONO, font_size=28, color=GOLD,
        )
        install_cmd.move_to(install_bg)
        install_group = VGroup(install_bg, install_cmd)
        install_group.move_to(ORIGIN)

        self.play(FadeIn(install_group, scale=0.9), run_time=0.5)
        self.wait(1.5)

        # ── Phase 4: Closing (16-20s) ─────────────────────────────
        self.play(FadeOut(install_group), run_time=0.3)
        self.play(*[card.animate.set_opacity(1) for card in cards], run_time=0.3)

        # Highlight pulse on all cards
        self.play(
            *[card[0].animate.set_stroke(width=3) for card in cards],
            run_time=0.3,
        )
        self.play(
            *[card[0].animate.set_stroke(width=1.5) for card in cards],
            run_time=0.3,
        )

        closer = Text(
            "github.com/AmitSubhash/3brown1blue",
            font=MONO, font_size=18, color=SLATE,
        )
        closer.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(closer, shift=UP * 0.15), run_time=0.4)
        self.wait(1.5)
