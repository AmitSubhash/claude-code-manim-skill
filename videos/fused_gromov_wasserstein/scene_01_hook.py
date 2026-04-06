"""Scene 1: Hook -- Two KGs, alignment arrows, key result reveal.

Duration target: ~12s
Template: FULL_CENTER
"""

import sys
sys.path.insert(0, "/Users/amit/Projects/3brown1blue/videos/fused_gromov_wasserstein")

from utils.style import *


class HookScene(Scene):
    def construct(self):
        # ── Title ─────────────────────────────────────────────────────
        title = section_title("Fused Gromov-Wasserstein")

        # NARRATION: Two knowledge graphs, built independently,
        # in different languages.
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.0)
        self.wait(HOLD_SHORT)

        # ── Left KG (English, blue) ──────────────────────────────────
        pokemon_en = kg_node("Pokemon", color=KG1_COLOR)
        nintendo_en = kg_node("Nintendo", color=KG1_COLOR)
        gameboy_en = kg_node("Game Boy", color=KG1_COLOR)

        pokemon_en.move_to(LEFT * 4.0 + UP * 0.6)
        nintendo_en.move_to(LEFT * 5.5 + DOWN * 1.2)
        gameboy_en.move_to(LEFT * 2.5 + DOWN * 1.2)

        edge_pub = kg_edge(pokemon_en, nintendo_en, "Publisher", color=KG1_EDGE)
        edge_plat = kg_edge(pokemon_en, gameboy_en, "Platform", color=KG1_EDGE)

        kg_left = VGroup(pokemon_en, nintendo_en, gameboy_en, edge_pub, edge_plat)

        # ── Right KG (Japanese, red) ─────────────────────────────────
        pokemon_jp = kg_node("Pokemon", color=KG2_COLOR, font_size=18)
        nintendo_jp = kg_node("Nintendo", color=KG2_COLOR, font_size=18)
        gameboy_jp = kg_node("GameBoy", color=KG2_COLOR, font_size=18)

        pokemon_jp.move_to(RIGHT * 4.0 + UP * 0.6)
        nintendo_jp.move_to(RIGHT * 2.5 + DOWN * 1.2)
        gameboy_jp.move_to(RIGHT * 5.5 + DOWN * 1.2)

        edge_pub_jp = kg_edge(pokemon_jp, nintendo_jp, color=KG2_EDGE)
        edge_plat_jp = kg_edge(pokemon_jp, gameboy_jp, color=KG2_EDGE)

        kg_right = VGroup(pokemon_jp, nintendo_jp, gameboy_jp, edge_pub_jp, edge_plat_jp)

        # ── Language labels ──────────────────────────────────────────
        lbl_en = safe_text("English KG", font_size=LABEL_SIZE, color=KG1_COLOR)
        lbl_en.next_to(kg_left, UP, buff=0.3)
        lbl_jp = safe_text("Japanese KG", font_size=LABEL_SIZE, color=KG2_COLOR)
        lbl_jp.next_to(kg_right, UP, buff=0.3)

        # Animate both KGs appearing
        self.play(
            FadeIn(kg_left, shift=LEFT * 0.3),
            FadeIn(lbl_en, shift=LEFT * 0.3),
            FadeIn(kg_right, shift=RIGHT * 0.3),
            FadeIn(lbl_jp, shift=RIGHT * 0.3),
            run_time=1.5,
        )
        self.wait(HOLD_SHORT)

        # NARRATION: Can we automatically discover which entities
        # are the same?

        # ── Alignment arrows (dashed yellow) ─────────────────────────
        arrow_pokemon = alignment_arrow(pokemon_en, pokemon_jp)
        arrow_nintendo = alignment_arrow(nintendo_en, nintendo_jp)
        arrow_gameboy = alignment_arrow(gameboy_en, gameboy_jp)

        self.play(
            Create(arrow_pokemon),
            Create(arrow_nintendo),
            Create(arrow_gameboy),
            run_time=1.5,
        )
        self.wait(HOLD_SHORT)

        # NARRATION: This paper does it with zero supervision...
        # and beats methods that use thousands of labeled pairs.

        # ── Bottom note ──────────────────────────────────────────────
        note = bottom_note("Zero supervision. 98.7% accuracy.")

        self.play(Write(note), run_time=1.0)
        self.wait(HOLD_MEDIUM)

        # ── Cleanup ──────────────────────────────────────────────────
        fade_all(
            self,
            title, kg_left, kg_right, lbl_en, lbl_jp,
            arrow_pokemon, arrow_nintendo, arrow_gameboy, note,
        )
