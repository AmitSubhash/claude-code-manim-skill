import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


class HookScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR

        # -- Build processor chip --
        chip_body = RoundedRectangle(
            width=2.5, height=2.5, corner_radius=0.2,
            color=CHIP_BLUE, fill_opacity=0.15, stroke_width=2.5,
        )

        # Pins: 4 per side as small rectangles
        pin_w, pin_h = 0.18, 0.08
        pin_color = CHIP_BLUE

        def make_pins_h(y_offset: float, count: int = 4) -> VGroup:
            """Horizontal row of pins (top/bottom)."""
            pins = VGroup()
            xs = [-0.75, -0.25, 0.25, 0.75]
            for x in xs:
                p = Rectangle(
                    width=pin_w, height=pin_h,
                    color=pin_color, fill_opacity=0.6, stroke_width=1.5,
                )
                p.move_to([x, y_offset, 0])
                pins.add(p)
            return pins

        def make_pins_v(x_offset: float, count: int = 4) -> VGroup:
            """Vertical column of pins (left/right)."""
            pins = VGroup()
            ys = [-0.75, -0.25, 0.25, 0.75]
            for y in ys:
                p = Rectangle(
                    width=pin_h, height=pin_w,
                    color=pin_color, fill_opacity=0.6, stroke_width=1.5,
                )
                p.move_to([x_offset, y, 0])
                pins.add(p)
            return pins

        top_pins = make_pins_h(1.29)
        bottom_pins = make_pins_h(-1.29)
        left_pins = make_pins_v(-1.29)
        right_pins = make_pins_v(1.29)

        # Inner grid lines suggesting circuitry
        grid_lines = VGroup()
        for x in [-0.6, 0.0, 0.6]:
            grid_lines.add(
                Line([x, -0.9, 0], [x, 0.9, 0],
                     color=CHIP_BLUE, stroke_width=0.8, stroke_opacity=0.35)
            )
        for y in [-0.6, 0.0, 0.6]:
            grid_lines.add(
                Line([-0.9, y, 0], [0.9, y, 0],
                     color=CHIP_BLUE, stroke_width=0.8, stroke_opacity=0.35)
            )

        chip = VGroup(
            chip_body, top_pins, bottom_pins, left_pins, right_pins, grid_lines
        ).move_to(ORIGIN + UP * 0.5)

        # -- Crack lines (hidden at first, revealed after shake) --
        crack_data = [
            ([0, 0, 0], [0.9,  1.1, 0]),
            ([0, 0, 0], [-1.0, -0.8, 0]),
            ([0, 0, 0], [1.1, -0.7, 0]),
            ([0, 0, 0], [-0.7,  1.0, 0]),
        ]
        cracks = VGroup(*[
            Line(chip.get_center() + np.array(s),
                 chip.get_center() + np.array(e),
                 color=BUG_RED, stroke_width=2.5)
            for s, e in crack_data
        ])

        # -- Phase 1: Chip fade-in --
        self.play(FadeIn(chip, scale=0.85), run_time=1.0)
        self.wait(0.4)

        # -- Phase 2: Shake/glitch (translate back-and-forth) --
        shake_anims = []
        offsets = [0.08, -0.12, 0.10, -0.08, 0.06, -0.04, 0.0]
        for dx in offsets:
            shake_anims.append(
                chip.animate.shift(RIGHT * dx)
            )
        self.play(
            AnimationGroup(*shake_anims, lag_ratio=0.0),
            run_time=0.6,
            rate_func=linear,
        )

        # -- Phase 3: Cracks appear --
        self.play(
            LaggedStart(*[Create(c) for c in cracks], lag_ratio=0.25),
            chip_body.animate.set_fill(color=BUG_RED, opacity=0.08),
            run_time=0.9,
        )
        self.wait(0.3)

        # -- Phase 4: Stat counters --
        stat_texts = [
            ("11 bugs found",         BUG_RED),
            ("5 CVEs filed",          EXPLOIT_ORANGE),
            ("2 exploits demonstrated", MUTATION_YELLOW),
        ]

        stats = VGroup()
        for label, color in stat_texts:
            t = safe_text(label, font_size=BODY_SIZE, color=color, max_width=9.0)
            stats.add(t)

        stats.arrange(DOWN, buff=0.35)
        stats.next_to(chip, DOWN, buff=0.55)
        # Guard: keep stats inside safe region
        if stats.get_bottom()[1] < -3.0:
            stats.shift(UP * (stats.get_bottom()[1] + 3.0) * -1)

        self.play(
            LaggedStart(*[Write(s) for s in stats], lag_ratio=0.5),
            run_time=1.5,
        )
        self.wait(HOLD_MEDIUM)

        # -- Phase 5: FadeOut chip, cracks, stats --
        self.play(
            FadeOut(chip),
            FadeOut(cracks),
            *[FadeOut(s) for s in stats],
            run_time=0.8,
        )

        # -- Phase 6: Question text --
        q_line1 = safe_text(
            "How do you find bugs in silicon",
            font_size=HEADING_SIZE,
            color=WHITE,
            max_width=11.0,
        )
        q_line2 = safe_text(
            "that can't be patched?",
            font_size=HEADING_SIZE,
            color=WHITE,
            max_width=11.0,
        )
        question = VGroup(q_line1, q_line2).arrange(DOWN, buff=0.25, center=True)
        question.move_to(ORIGIN)

        self.play(FadeIn(question, scale=0.92), run_time=0.9)
        self.wait(HOLD_MEDIUM)

        # -- Cleanup --
        self.play(FadeOut(question), run_time=0.7)
        self.wait(0.1)
