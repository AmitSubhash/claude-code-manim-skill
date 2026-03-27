"""
Scene 10 -- InSilicoScene (~90s)
Act III: Results

In-silico neuroscience: compare traditional vs TRIBE v2 approaches,
recover known findings (tonotopy, retinotopy, lateralization),
then reveal fine-grained multisensory topography.
Template: BUILD_UP
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


class InSilicoScene(Scene):
    def setup(self):
        self.camera.background_color = BG_COLOR

    def construct(self):
        # ── Phase 1: Title + Concept Comparison (~30s) ─────────────────
        title = safe_text(
            "In-Silico Neuroscience: Virtual Experiments",
            font_size=TITLE_SIZE,
            color=WHITE,
        )
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=1.0)
        self.wait(0.5)

        # -- LEFT side: Traditional approach (vertical stack) --
        trad_label = safe_text(
            "Traditional",
            font_size=LABEL_SIZE,
            color=BASELINE_GRAY,
        )
        trad_label.move_to([-3.5, 1.8, 0])

        person = subject_icon(color=BASELINE_GRAY, scale=0.5)
        person.move_to([-3.5, 1.2, 0])

        fmri_box = labeled_box(
            "fMRI Scanner",
            width=2.2,
            height=0.7,
            color=BASELINE_GRAY,
            fill_opacity=0.15,
        )
        fmri_box.move_to([-3.5, 0.3, 0])

        brain_maps_box = labeled_box(
            "Brain Maps",
            width=2.2,
            height=0.7,
            color=BASELINE_GRAY,
            fill_opacity=0.15,
        )
        brain_maps_box.move_to([-3.5, -0.7, 0])

        trad_arrow1 = down_arrow(person, fmri_box, color=BASELINE_GRAY)
        trad_arrow2 = down_arrow(fmri_box, brain_maps_box, color=BASELINE_GRAY)

        months_label = safe_text(
            "Months of scanning",
            font_size=SMALL_LABEL,
            color=BASELINE_GRAY,
        )
        months_label.next_to(brain_maps_box, DOWN, buff=0.25)

        trad_group = VGroup(
            trad_label, person, fmri_box, brain_maps_box,
            trad_arrow1, trad_arrow2, months_label,
        )

        # -- RIGHT side: TRIBE v2 approach (vertical stack) --
        tribe_label = safe_text(
            "TRIBE v2",
            font_size=LABEL_SIZE,
            color=RESULT_GOLD,
        )
        tribe_label.move_to([3.5, 1.8, 0])

        stim_box = labeled_box(
            "Stimulus",
            width=2.2,
            height=0.7,
            color=RESULT_GOLD,
            fill_opacity=0.2,
        )
        stim_box.move_to([3.5, 1.2, 0])

        tribe_box = labeled_box(
            "TRIBE v2",
            width=2.2,
            height=0.7,
            color=TRANSFORM_TEAL,
            fill_opacity=0.25,
        )
        tribe_box.move_to([3.5, 0.3, 0])

        pred_box = labeled_box(
            "Predicted Maps",
            width=2.2,
            height=0.7,
            color=RESULT_GOLD,
            fill_opacity=0.2,
        )
        pred_box.move_to([3.5, -0.7, 0])

        tribe_arrow1 = down_arrow(stim_box, tribe_box, color=WHITE)
        tribe_arrow2 = down_arrow(tribe_box, pred_box, color=WHITE)

        secs_label = safe_text(
            "Seconds of compute",
            font_size=SMALL_LABEL,
            color=RESULT_GOLD,
        )
        secs_label.next_to(pred_box, DOWN, buff=0.25)

        tribe_group = VGroup(
            tribe_label, stim_box, tribe_box, pred_box,
            tribe_arrow1, tribe_arrow2, secs_label,
        )

        # -- VS divider --
        vs_text = safe_text("vs", font_size=HEADING_SIZE, color=LABEL_GRAY)
        vs_text.move_to([0.0, 0.5, 0])

        # Animate left, then right
        self.play(
            LaggedStart(
                FadeIn(trad_label, shift=DOWN * 0.2),
                FadeIn(person, shift=RIGHT * 0.2),
                Create(trad_arrow1),
                FadeIn(fmri_box, shift=RIGHT * 0.2),
                Create(trad_arrow2),
                FadeIn(brain_maps_box, shift=RIGHT * 0.2),
                FadeIn(months_label, shift=UP * 0.1),
                lag_ratio=0.2,
            ),
            run_time=3.0,
        )
        self.wait(0.5)

        self.play(FadeIn(vs_text, scale=1.2), run_time=0.6)

        self.play(
            LaggedStart(
                FadeIn(tribe_label, shift=DOWN * 0.2),
                FadeIn(stim_box, shift=RIGHT * 0.2),
                Create(tribe_arrow1),
                FadeIn(tribe_box, shift=RIGHT * 0.2),
                Create(tribe_arrow2),
                FadeIn(pred_box, shift=RIGHT * 0.2),
                FadeIn(secs_label, shift=UP * 0.1),
                lag_ratio=0.2,
            ),
            run_time=3.0,
        )
        self.wait(HOLD_MEDIUM)

        # ── Phase 2: Recovery of Known Findings (~30s) ─────────────────
        # Fade out phase 1 and title together, bring in new subtitle
        subtitle = safe_text(
            "Recovers Established Neuroscience",
            font_size=HEADING_SIZE,
            color=RESULT_GOLD,
        )
        subtitle.to_edge(UP, buff=0.4)

        self.play(
            FadeOut(title),
            FadeOut(trad_group),
            FadeOut(tribe_group),
            FadeOut(vs_text),
            Write(subtitle),
            run_time=1.2,
        )

        # Three small brain outlines with colored highlighted regions
        findings_data = [
            {
                "name": "Tonotopy",
                "color": AUDIO_GREEN,
                "desc": "Frequency gradient",
                "region_x": 0.0,
                "region_y": 0.0,
            },
            {
                "name": "Retinotopy",
                "color": VIDEO_BLUE,
                "desc": "Spatial position map",
                "region_x": 0.1,
                "region_y": -0.15,
            },
            {
                "name": "Lateralization",
                "color": TEXT_ORANGE,
                "desc": "Left hemisphere",
                "region_x": -0.3,
                "region_y": 0.0,
            },
        ]

        brain_cards = VGroup()
        for fd in findings_data:
            # Small brain ellipse
            small_brain = brain_outline(
                width=2.4, height=1.5, color=BRAIN_PURPLE,
            )

            # Colored region highlight
            hl = Circle(
                radius=0.4, color=fd["color"],
                fill_opacity=0.45, stroke_width=1.5,
            )
            hl.move_to(
                small_brain.get_center()
                + RIGHT * fd["region_x"]
                + UP * fd["region_y"]
            )

            # Finding name below brain
            name_lbl = safe_text(
                fd["name"],
                font_size=LABEL_SIZE,
                color=fd["color"],
            )
            name_lbl.next_to(small_brain, DOWN, buff=0.15)

            # Description below name
            desc_lbl = safe_text(
                fd["desc"],
                font_size=SMALL_LABEL,
                color=LABEL_GRAY,
            )
            desc_lbl.next_to(name_lbl, DOWN, buff=0.1)

            card = VGroup(small_brain, hl, name_lbl, desc_lbl)
            brain_cards.add(card)

        brain_cards.arrange(RIGHT, buff=0.8)
        brain_cards.move_to(DOWN * 0.3)

        self.play(
            LaggedStart(
                *[FadeIn(bc, shift=UP * 0.3) for bc in brain_cards],
                lag_ratio=0.4,
            ),
            run_time=3.5,
        )
        self.wait(HOLD_LONG)

        # ── Phase 3: New Discoveries (~20s) ────────────────────────────
        # Fade out the three small brains, bring in large brain
        new_subtitle = safe_text(
            "New Discovery: Multisensory Topography",
            font_size=HEADING_SIZE,
            color=RESULT_GOLD,
        )
        new_subtitle.to_edge(UP, buff=0.4)

        self.play(
            FadeOut(subtitle),
            FadeOut(brain_cards),
            Write(new_subtitle),
            run_time=1.0,
        )

        large_brain = brain_outline(
            width=5.5, height=3.2, color=BRAIN_PURPLE,
        )
        large_brain.move_to(DOWN * 0.2)

        # Multiple colored sub-regions for fine-grained topography
        region_specs = [
            (-1.2, 0.6, 0.35, VIDEO_BLUE, 0.35),
            (0.8, 0.5, 0.3, AUDIO_GREEN, 0.35),
            (-0.3, -0.3, 0.4, TEXT_ORANGE, 0.3),
            (1.5, -0.4, 0.3, TRANSFORM_TEAL, 0.35),
            (-1.8, -0.5, 0.25, RESULT_GOLD, 0.4),
            (0.3, 0.9, 0.25, SUBJECT_PINK, 0.3),
            (-0.8, 0.1, 0.3, VIDEO_BLUE, 0.25),
            (1.0, 0.0, 0.28, AUDIO_GREEN, 0.3),
        ]

        region_circles = VGroup()
        for rx, ry, rad, col, opa in region_specs:
            c = Circle(
                radius=rad, color=col,
                fill_opacity=opa, stroke_width=1,
            )
            c.move_to(large_brain.get_center() + RIGHT * rx + UP * ry)
            region_circles.add(c)

        self.play(FadeIn(large_brain), run_time=0.8)
        self.play(
            LaggedStart(
                *[FadeIn(rc, scale=0.5) for rc in region_circles],
                lag_ratio=0.08,
            ),
            run_time=2.5,
        )

        # Caption label
        topo_label = safe_text(
            "Fine-grained topography of multisensory integration",
            font_size=LABEL_SIZE,
            color=WHITE,
        )
        topo_label.next_to(large_brain, DOWN, buff=0.25)

        annot_label = safe_text(
            "Resolution impossible with traditional methods",
            font_size=SMALL_LABEL,
            color=LABEL_GRAY,
        )
        annot_label.next_to(topo_label, DOWN, buff=0.15)

        self.play(
            FadeIn(topo_label, shift=UP * 0.15),
            FadeIn(annot_label, shift=UP * 0.1),
            run_time=1.0,
        )
        self.wait(HOLD_MEDIUM)

        # ── Bottom note ───────────────────────────────────────────────
        note = bottom_note(
            "Simulate experiments that would take months -- in seconds",
            color=RESULT_GOLD,
        )
        self.play(FadeIn(note, shift=UP * 0.2), run_time=0.8)
        self.wait(HOLD_LONG)

        # ── Cleanup ──────────────────────────────────────────────────
        fade_all(
            self,
            new_subtitle, large_brain, region_circles,
            topo_label, annot_label, note,
        )
