"""
Scene 02 -- FragmentationScene (~60s)
Act I: Why This Matters

Three siloed research labs shown as cards, then unified by
a multimodal movie stimulus converging on prefrontal cortex.
Template: GRID_CARDS
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


# ── Icon Builders ────────────────────────────────────────────────────────

def eye_icon(color: str = VIDEO_BLUE, scale: float = 0.4) -> VGroup:
    """Simplified eye: outer ellipse + inner dot."""
    outer = Ellipse(
        width=1.0, height=0.5,
        color=color, stroke_width=2, fill_opacity=0.15,
    )
    pupil = Dot(point=ORIGIN, radius=0.1, color=color)
    return VGroup(outer, pupil).scale(scale)


def ear_icon(color: str = AUDIO_GREEN, scale: float = 0.4) -> VGroup:
    """Simplified ear: two concentric arcs."""
    arc_outer = Arc(
        radius=0.4, start_angle=PI * 0.25, angle=PI * 0.5,
        color=color, stroke_width=2.5,
    )
    arc_inner = Arc(
        radius=0.25, start_angle=PI * 0.25, angle=PI * 0.5,
        color=color, stroke_width=2,
    )
    return VGroup(arc_outer, arc_inner).scale(scale)


def text_lines_icon(color: str = TEXT_ORANGE, scale: float = 0.4) -> VGroup:
    """Simplified text icon: three horizontal lines."""
    lines = VGroup()
    widths = [0.7, 0.5, 0.6]
    for i, w in enumerate(widths):
        line = Line(
            LEFT * w / 2, RIGHT * w / 2,
            color=color, stroke_width=2,
        )
        line.shift(DOWN * i * 0.2)
        lines.add(line)
    lines.center()
    return lines.scale(scale)


# ── Card Builder ─────────────────────────────────────────────────────────

def silo_card(
    title: str,
    color: str,
    icon: VGroup,
    region_labels: list[str],
    width: float = 3.5,
    height: float = 3.0,
) -> VGroup:
    """A research-lab card with icon, title, and region labels."""
    rect = RoundedRectangle(
        width=width, height=height, corner_radius=0.15,
        color=color, fill_opacity=0.08, stroke_width=2,
    )

    header = safe_text(title, font_size=LABEL_SIZE, color=color)
    header.move_to(rect.get_top() + DOWN * 0.4)

    icon.move_to(rect.get_center() + DOWN * 0.1)

    region_group = VGroup()
    for rl in region_labels:
        badge = modality_badge(rl, color, width=1.2)
        region_group.add(badge)
    region_group.arrange(RIGHT, buff=0.2)
    region_group.move_to(rect.get_bottom() + UP * 0.5)

    return VGroup(rect, header, icon, region_group)


class FragmentationScene(Scene):
    def setup(self):
        self.camera.background_color = BG_COLOR

    def construct(self):
        # ── Phase 1: Title ───────────────────────────────────────────────
        title = section_title("The Silo Problem in Neuroscience")
        self.play(Write(title), run_time=1.0)
        self.wait(0.5)

        # ── Phase 2: Three silo cards ────────────────────────────────────
        card_vision = silo_card(
            "Vision Lab", VIDEO_BLUE,
            eye_icon(), ["V1", "V2"],
        )
        card_audio = silo_card(
            "Auditory Lab", AUDIO_GREEN,
            ear_icon(), ["A1", "STG"],
        )
        card_language = silo_card(
            "Language Lab", TEXT_ORANGE,
            text_lines_icon(), ["Broca", "Wernicke"],
        )

        cards = VGroup(card_vision, card_audio, card_language)
        cards.arrange(RIGHT, buff=0.4)
        cards.move_to(DOWN * 0.2)

        self.play(
            LaggedStart(
                *[FadeIn(c, shift=UP * 0.3) for c in cards],
                lag_ratio=0.35,
            ),
            run_time=2.5,
        )
        self.wait(HOLD_MEDIUM)

        # ── Phase 3: Red "isolated" X marks ──────────────────────────────
        x_marks = VGroup()
        for card in cards:
            cross = VGroup(
                Line(UL * 0.3, DR * 0.3, color=DANGER_RED, stroke_width=4),
                Line(UR * 0.3, DL * 0.3, color=DANGER_RED, stroke_width=4),
            )
            cross.move_to(card[0].get_corner(UR) + DL * 0.4)
            x_marks.add(cross)

        isolated_label = safe_text(
            "Isolated", font_size=SMALL_LABEL, color=DANGER_RED,
        )
        isolated_label.next_to(cards, UP, buff=0.15)
        # Make sure it does not overlap with the title
        if isolated_label.get_top()[1] > title.get_bottom()[1] - 0.15:
            isolated_label.next_to(cards, DOWN, buff=0.15)

        self.play(
            LaggedStart(
                *[Create(x) for x in x_marks],
                lag_ratio=0.2,
            ),
            FadeIn(isolated_label, shift=DOWN * 0.1),
            run_time=1.5,
        )
        self.wait(HOLD_MEDIUM)

        # ── Phase 4: Transition to convergence ───────────────────────────
        # Fade out title, X marks, and isolated label; keep cards dimmed
        self.play(
            FadeOut(title),
            FadeOut(x_marks),
            FadeOut(isolated_label),
            *[card.animate.set_opacity(0.5).scale(0.65) for card in cards],
            run_time=1.0,
        )

        # Reposition shrunken cards to upper area
        cards.generate_target()
        cards.target.arrange(RIGHT, buff=0.3).move_to(UP * 2.0)
        self.play(MoveToTarget(cards), run_time=0.8)

        # Movie scene box at center
        movie_box = labeled_box(
            "Movie Scene", width=3.0, height=1.0,
            color=RESULT_GOLD, fill_opacity=0.15,
        )
        movie_box.move_to(DOWN * 0.2)

        # Brain region "Prefrontal" at bottom
        pfc_box = labeled_box(
            "Prefrontal", width=2.8, height=0.9,
            color=BRAIN_PURPLE, fill_opacity=0.2,
        )
        pfc_box.move_to(DOWN * 2.2)

        self.play(
            FadeIn(movie_box, shift=UP * 0.3),
            run_time=1.0,
        )

        # Arrows from each card to movie box, then movie box to PFC
        card_arrows = VGroup()
        for card in cards:
            arrow = Arrow(
                card.get_bottom(), movie_box.get_top(), buff=0.2,
                color=LABEL_GRAY, stroke_width=2,
                max_tip_length_to_length_ratio=0.15,
            )
            card_arrows.add(arrow)

        self.play(
            LaggedStart(
                *[Create(a) for a in card_arrows],
                lag_ratio=0.15,
            ),
            run_time=1.2,
        )

        converge_arrow = down_arrow(movie_box, pfc_box, color=RESULT_GOLD)
        self.play(
            FadeIn(pfc_box, shift=UP * 0.2),
            Create(converge_arrow),
            run_time=1.0,
        )
        self.wait(HOLD_SHORT)

        # Cross-modal label
        cross_label = safe_text(
            "Cross-modal integration",
            font_size=LABEL_SIZE, color=BRAIN_PURPLE,
        )
        cross_label.next_to(pfc_box, DOWN, buff=0.2)

        self.play(FadeIn(cross_label, shift=UP * 0.1), run_time=0.8)
        self.wait(HOLD_SHORT)

        # ── Phase 5: Bottom note ─────────────────────────────────────────
        note = bottom_note("Real perception is multimodal", color=RESULT_GOLD)
        self.play(FadeIn(note, shift=UP * 0.2), run_time=0.8)
        self.wait(HOLD_MEDIUM)

        # ── Cleanup ──────────────────────────────────────────────────────
        fade_all(
            self,
            *cards, movie_box, pfc_box,
            *card_arrows, converge_arrow,
            cross_label, note,
        )
