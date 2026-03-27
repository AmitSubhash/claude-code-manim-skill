"""
Scene 12 -- LimitationsScene (~75s)
Act IV: Closing

Honest limitations, open research questions, and final citation card.
Template: BUILD_UP
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


# ── Icon Builders ────────────────────────────────────────────────────────

def warning_icon(color: str = DANGER_RED, scale: float = 0.3) -> VGroup:
    """Small warning triangle."""
    tri = Triangle(color=color, fill_opacity=0.7, stroke_width=1.5)
    tri.scale(scale)
    bang = safe_text("!", font_size=14, color=WHITE)
    bang.move_to(tri.get_center() + DOWN * 0.02)
    return VGroup(tri, bang)


def question_icon(color: str = RESULT_GOLD, scale: float = 0.3) -> VGroup:
    """Small question mark circle."""
    circ = Circle(
        radius=0.2, color=color,
        fill_opacity=0.25, stroke_width=1.5,
    )
    circ.scale(scale)
    q = safe_text("?", font_size=16, color=color)
    q.move_to(circ)
    return VGroup(circ, q)


class LimitationsScene(Scene):
    def setup(self):
        self.camera.background_color = BG_COLOR

    def construct(self):
        # ── Phase 1: Honest Limitations (~30s) ─────────────────────────
        title = safe_text(
            "Limitations and Open Questions",
            font_size=TITLE_SIZE,
            color=WHITE,
        )
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=1.0)
        self.wait(0.5)

        limitations = [
            "fMRI only -- no temporal precision (1.5-2s TR)",
            "Perception only -- cannot model behavior or memory",
            "Frozen backbones may miss brain-relevant features",
            "Sub-linear scaling -- diminishing returns",
        ]

        y_positions = [1.5, 0.7, -0.1, -0.9]
        lim_items = VGroup()

        for i, (text, y_pos) in enumerate(zip(limitations, y_positions)):
            icon = warning_icon(color=DANGER_RED, scale=0.3)
            lbl = safe_text(
                text,
                font_size=LABEL_SIZE,
                color=WHITE,
                max_width=9.0,
            )
            icon.move_to([-4.5, y_pos, 0])
            lbl.next_to(icon, RIGHT, buff=0.25)

            # Ensure text does not overflow right edge
            if lbl.get_right()[0] > 5.4:
                lbl.scale_to_fit_width(5.4 - lbl.get_left()[0])
                lbl.next_to(icon, RIGHT, buff=0.25)

            item = VGroup(icon, lbl)
            lim_items.add(item)

        self.play(
            LaggedStart(
                *[
                    FadeIn(item, shift=RIGHT * 0.3)
                    for item in lim_items
                ],
                lag_ratio=0.35,
            ),
            run_time=4.0,
        )
        self.wait(HOLD_MEDIUM)

        # ── Phase 2: Open Questions (~20s) ─────────────────────────────
        # Dim limitations, do not remove them
        self.play(
            *[item.animate.set_opacity(DIM_OPACITY) for item in lim_items],
            run_time=0.8,
        )

        questions = [
            "Can we close the noise ceiling gap (54% -> ?)?",
            "EEG/MEG for millisecond temporal resolution?",
            "Decode brain -> stimulus with same architecture?",
            "Fine-tune backbones with brain data?",
        ]

        q_y_positions = [1.5, 0.7, -0.1, -0.9]
        q_items = VGroup()

        for i, (text, y_pos) in enumerate(zip(questions, q_y_positions)):
            icon = question_icon(color=RESULT_GOLD, scale=0.35)
            lbl = safe_text(
                text,
                font_size=LABEL_SIZE,
                color=RESULT_GOLD,
                max_width=9.0,
            )
            icon.move_to([-4.5, y_pos, 0])
            lbl.next_to(icon, RIGHT, buff=0.25)

            # Ensure text does not overflow right edge
            if lbl.get_right()[0] > 5.4:
                lbl.scale_to_fit_width(5.4 - lbl.get_left()[0])
                lbl.next_to(icon, RIGHT, buff=0.25)

            item = VGroup(icon, lbl)
            q_items.add(item)

        self.play(
            LaggedStart(
                *[
                    FadeIn(item, shift=RIGHT * 0.3)
                    for item in q_items
                ],
                lag_ratio=0.35,
            ),
            run_time=4.0,
        )
        self.wait(HOLD_MEDIUM)

        # ── Phase 3: Citation Card (~15s) ──────────────────────────────
        # Fade out everything cleanly
        self.play(
            FadeOut(title),
            FadeOut(lim_items),
            FadeOut(q_items),
            run_time=0.8,
        )

        # Paper title (2 lines via safe_multiline)
        paper_title = safe_multiline(
            "A Foundation Model of Vision, Audition,",
            "and Language for In-Silico Neuroscience",
            font_size=BODY_SIZE,
            color=WHITE,
            max_width=10.0,
        )
        paper_title.move_to(UP * 1.5)

        # Authors
        authors = safe_multiline(
            "d'Ascoli, Rapin, Benchetrit, Brooks, Begany,",
            "Raugel, Banville, King",
            font_size=SMALL_LABEL,
            color=LABEL_GRAY,
            max_width=10.0,
        )
        authors.next_to(paper_title, DOWN, buff=0.35)

        # Venue
        venue = safe_text(
            "Meta FAIR, 2026",
            font_size=LABEL_SIZE,
            color=WHITE,
        )
        venue.next_to(authors, DOWN, buff=0.3)

        # Links
        gh_link = safe_text(
            "github.com/facebookresearch/tribev2",
            font_size=SMALL_LABEL,
            color=TRANSFORM_TEAL,
        )
        gh_link.next_to(venue, DOWN, buff=0.35)

        hf_link = safe_text(
            "huggingface.co/facebook/tribev2",
            font_size=SMALL_LABEL,
            color=RESULT_GOLD,
        )
        hf_link.next_to(gh_link, DOWN, buff=0.2)

        # Decorative border around the citation card
        card_content = VGroup(
            paper_title, authors, venue, gh_link, hf_link,
        )
        card_border = RoundedRectangle(
            width=card_content.width + 1.2,
            height=card_content.height + 0.8,
            corner_radius=0.2,
            color=BRAIN_PURPLE,
            fill_opacity=0.05,
            stroke_width=1.5,
        )
        card_border.move_to(card_content)

        citation_card = VGroup(card_border, card_content)

        self.play(
            FadeIn(card_border, scale=0.95),
            run_time=0.6,
        )
        self.play(
            LaggedStart(
                Write(paper_title),
                FadeIn(authors, shift=UP * 0.15),
                FadeIn(venue, shift=UP * 0.1),
                FadeIn(gh_link, shift=UP * 0.1),
                FadeIn(hf_link, shift=UP * 0.1),
                lag_ratio=0.3,
            ),
            run_time=3.5,
        )

        # Bottom note -- final message
        note = bottom_note(
            "The gap between digital twin and biological reality "
            "remains -- but it is shrinking",
            color=RESULT_GOLD,
        )
        self.play(FadeIn(note, shift=UP * 0.2), run_time=0.8)
        self.wait(HOLD_LONG)

        # ── Cleanup (final scene, gentle fade) ────────────────────────
        fade_all(self, citation_card, note)
