"""Scene 03 Extended: 3D Surface Showcase.

Three surfaces, explained. Shows off what Manim 3D can do:
1. Attention landscape with gradient coloring and rotation
2. Morph into a saddle point (loss landscape)
3. Morph into a Gaussian mixture (probability density)
Each transition is narrated with a one-line explanation.
~25s total.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


def _color_gradient(z: float, z_min: float, z_max: float, low, mid, high):
    """Three-stop color gradient from z value."""
    if abs(z_max - z_min) < 1e-8:
        return mid
    t = max(0.0, min(1.0, (z - z_min) / (z_max - z_min)))
    c_low = np.array(color_to_rgb(low))
    c_mid = np.array(color_to_rgb(mid))
    c_high = np.array(color_to_rgb(high))
    if t < 0.5:
        s = t / 0.5
        rgb = (1 - s) * c_low + s * c_mid
    else:
        s = (t - 0.5) / 0.5
        rgb = (1 - s) * c_mid + s * c_high
    return rgb_to_color(rgb)


def _color_surface(surface, z_min, z_max, low, mid, high):
    """Apply height-based gradient to all faces."""
    for face in surface:
        z = face.get_center()[2]
        face.set_color(_color_gradient(z, z_min, z_max, low, mid, high))


class ExtendedSurfaceScene(ThreeDScene):
    """25-second 3D showcase with three morphing surfaces."""

    def construct(self) -> None:
        self.camera.background_color = BG
        self.set_camera_orientation(phi=65 * DEGREES, theta=-40 * DEGREES)

        axes = ThreeDAxes(
            x_range=[-3, 3, 1], y_range=[-3, 3, 1], z_range=[-1.5, 1.5, 0.5],
            x_length=6, y_length=6, z_length=3.5,
            axis_config={"color": SLATE, "stroke_width": 1.2},
        )

        # ── Surface 1: Attention landscape ──────────────────────────
        def attention_func(u, v):
            z = float(np.exp(-(u**2 + v**2) / 2.5) * np.cos(2 * u) * np.cos(2 * v))
            return axes.c2p(u, v, z)

        s1 = Surface(
            attention_func, u_range=[-3, 3], v_range=[-3, 3],
            resolution=(48, 48), fill_opacity=0.85,
            stroke_width=0.2, stroke_color=SLATE,
        )
        _color_surface(s1, -0.4, 1.0, ELECTRIC, GOLD, CORAL)

        # Caption system (fixed in frame)
        caption = safe_text("", font_size=BODY_SIZE, color=MINT)
        caption.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(caption)

        title = safe_text("", font_size=TITLE_SIZE, color=GOLD)
        title.to_edge(UP, buff=0.5)
        self.add_fixed_in_frame_mobjects(title)

        # -- Reveal axes + surface 1 --
        # NARRATION: Manim renders publication-quality 3D surfaces.
        new_title = safe_text("3D Surfaces in Manim", font_size=TITLE_SIZE, color=GOLD)
        new_title.to_edge(UP, buff=0.5)
        self.add_fixed_in_frame_mobjects(new_title)

        self.play(Create(axes), run_time=0.6)
        self.play(Create(s1), FadeIn(new_title), run_time=1.5)

        cap1 = safe_text("Attention weights as a landscape", font_size=BODY_SIZE, color=MINT)
        cap1.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(cap1)
        self.play(FadeIn(cap1, shift=UP * 0.15), run_time=0.5)

        self.begin_ambient_camera_rotation(rate=0.12)
        self.wait(3.0)
        self.stop_ambient_camera_rotation()

        # ── Surface 2: Loss landscape (saddle point) ────────────────
        # NARRATION: Morph it into a loss landscape with saddle points.
        def saddle_func(u, v):
            z = float(0.15 * (u**2 - v**2) + 0.3 * np.exp(-(u**2 + v**2) / 3))
            return axes.c2p(u, v, z)

        s2 = Surface(
            saddle_func, u_range=[-3, 3], v_range=[-3, 3],
            resolution=(48, 48), fill_opacity=0.85,
            stroke_width=0.2, stroke_color=SLATE,
        )
        _color_surface(s2, -1.2, 1.2, TEAL, WARM_WHITE, CORAL)

        cap2 = safe_text("Loss landscape with a saddle point", font_size=BODY_SIZE, color=MINT)
        cap2.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(cap2)

        self.play(
            ReplacementTransform(s1, s2),
            FadeOut(cap1), FadeIn(cap2, shift=UP * 0.15),
            run_time=2.0,
        )

        # Orbit around the saddle
        self.begin_ambient_camera_rotation(rate=-0.15)
        self.wait(3.0)
        self.stop_ambient_camera_rotation()

        # ── Surface 3: Gaussian mixture (probability) ───────────────
        # NARRATION: Or a probability density with multiple peaks.
        def gaussian_mix(u, v):
            g1 = np.exp(-((u - 1.2)**2 + (v - 1)**2) / 0.8)
            g2 = 0.7 * np.exp(-((u + 1.5)**2 + (v + 0.8)**2) / 1.2)
            g3 = 0.5 * np.exp(-((u + 0.3)**2 + (v - 1.8)**2) / 0.6)
            z = float(g1 + g2 + g3)
            return axes.c2p(u, v, z)

        s3 = Surface(
            gaussian_mix, u_range=[-3, 3], v_range=[-3, 3],
            resolution=(48, 48), fill_opacity=0.85,
            stroke_width=0.2, stroke_color=SLATE,
        )
        _color_surface(s3, 0.0, 1.0, ELECTRIC, VIOLET, CORAL)

        cap3 = safe_text(
            "Gaussian mixture density, three peaks",
            font_size=BODY_SIZE, color=MINT,
        )
        cap3.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(cap3)

        self.play(
            ReplacementTransform(s2, s3),
            FadeOut(cap2), FadeIn(cap3, shift=UP * 0.15),
            run_time=2.0,
        )

        # Dramatic camera move: tilt up to bird's eye
        self.move_camera(phi=30 * DEGREES, theta=-60 * DEGREES, run_time=3.0)
        self.wait(1.0)

        # ── Surface 4: Wave interference ────────────────────────────
        # NARRATION: Or wave interference patterns in physics.
        def wave_func(u, v):
            r1 = np.sqrt((u - 1.5)**2 + v**2)
            r2 = np.sqrt((u + 1.5)**2 + v**2)
            z = float(0.5 * (np.sin(3 * r1) / (r1 + 0.5) + np.sin(3 * r2) / (r2 + 0.5)))
            return axes.c2p(u, v, z)

        s4 = Surface(
            wave_func, u_range=[-3, 3], v_range=[-3, 3],
            resolution=(48, 48), fill_opacity=0.85,
            stroke_width=0.2, stroke_color=SLATE,
        )
        _color_surface(s4, -0.6, 0.8, ELECTRIC, MINT, GOLD)

        cap4 = safe_text(
            "Two-source wave interference",
            font_size=BODY_SIZE, color=MINT,
        )
        cap4.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(cap4)

        self.play(
            ReplacementTransform(s3, s4),
            FadeOut(cap3), FadeIn(cap4, shift=UP * 0.15),
            run_time=2.0,
        )

        # Return to standard angle
        self.move_camera(phi=60 * DEGREES, theta=-45 * DEGREES, run_time=2.0)
        self.wait(1.0)

        # ── Closing tagline ─────────────────────────────────────────
        cap_final = safe_text(
            "Any surface. Any domain. One tool.",
            font_size=BODY_SIZE + 4, color=GOLD,
        )
        cap_final.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(cap_final)

        self.play(
            FadeOut(cap4), FadeIn(cap_final, shift=UP * 0.15),
            s4.animate.set_opacity(0.4),
            run_time=0.8,
        )
        self.wait(2.0)
