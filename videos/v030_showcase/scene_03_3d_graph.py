"""Scene 03: 3D Attention Surface -- rotating heatmap landscape.

A ThreeDScene showing a peaked, rippled surface colored from
ELECTRIC (valleys) through GOLD (mid) to CORAL (peaks), with
labeled axes and slow camera rotation.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


def _attention_landscape(u: float, v: float) -> np.ndarray:
    """Surface function: peaked landscape with interference ripples.

    Parameters
    ----------
    u : float
        x-coordinate in [-3, 3].
    v : float
        y-coordinate in [-3, 3].

    Returns
    -------
    np.ndarray
        [x, y, z] point on the surface.
    """
    z = float(
        np.exp(-(u**2 + v**2) / 2.5)
        * np.cos(2.0 * u)
        * np.cos(2.0 * v)
    )
    return np.array([u, v, z])


def _color_from_height(z: float, z_min: float, z_max: float) -> str:
    """Map height to a three-stop gradient: ELECTRIC -> GOLD -> CORAL.

    Parameters
    ----------
    z : float
        Current z value.
    z_min : float
        Minimum z on the surface.
    z_max : float
        Maximum z on the surface.

    Returns
    -------
    str
        Hex color interpolated across the gradient.
    """
    if abs(z_max - z_min) < 1e-8:
        return GOLD
    t = (z - z_min) / (z_max - z_min)
    t = max(0.0, min(1.0, t))

    c_low = color_to_rgb(ELECTRIC)
    c_mid = color_to_rgb(GOLD)
    c_high = color_to_rgb(CORAL)

    if t < 0.5:
        s = t / 0.5
        rgb = (1 - s) * np.array(c_low) + s * np.array(c_mid)
    else:
        s = (t - 0.5) / 0.5
        rgb = (1 - s) * np.array(c_mid) + s * np.array(c_high)

    return rgb_to_color(rgb)


class GraphScene3D(ThreeDScene):
    """8-second 3D surface with camera rotation."""

    def construct(self) -> None:
        self.camera.background_color = BG

        # -- Camera initial angle --
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)

        # -- 3D Axes --
        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            z_range=[-1, 1.2, 0.5],
            x_length=6,
            y_length=6,
            z_length=3,
            axis_config={"color": SLATE, "stroke_width": 1.5},
        )

        # Axis labels
        x_label = Text("Query", font=MONO, font_size=LABEL_SIZE, color=WARM_WHITE)
        x_label.rotate(PI / 2, axis=RIGHT)
        x_label.next_to(axes.x_axis.get_end(), RIGHT + DOWN, buff=0.3)

        y_label = Text("Key", font=MONO, font_size=LABEL_SIZE, color=WARM_WHITE)
        y_label.rotate(PI / 2, axis=RIGHT)
        y_label.next_to(axes.y_axis.get_end(), LEFT + DOWN, buff=0.3)

        z_label = Text("Attention Weight", font=MONO, font_size=LABEL_SIZE - 2, color=WARM_WHITE)
        z_label.rotate(PI / 2, axis=RIGHT)
        z_label.next_to(axes.z_axis.get_end(), UP + LEFT, buff=0.3)

        labels = VGroup(x_label, y_label, z_label)

        # -- Surface --
        surface = Surface(
            lambda u, v: axes.c2p(*_attention_landscape(u, v)),
            u_range=[-3, 3],
            v_range=[-3, 3],
            resolution=(64, 64),
            fill_opacity=0.85,
            stroke_width=0.3,
            stroke_color=SLATE,
        )

        # Color each face by height
        z_min, z_max = -0.4, 1.0
        for face in surface:
            z_val = face.get_center()[2]
            face.set_color(_color_from_height(z_val, z_min, z_max))

        # -- Bottom caption --
        caption = safe_text(
            "3D visualizations, built-in", font_size=BODY_SIZE, color=MINT
        )
        caption.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(caption)
        caption.set_opacity(0)

        # -- Animation sequence (~8s) --

        # Axes fade in (0.8s)
        self.play(Create(axes), FadeIn(labels), run_time=0.8)

        # Surface appears (1.5s)
        self.play(Create(surface), run_time=1.5)

        # Rotate camera while holding (3.0s)
        self.play(
            caption.animate.set_opacity(1.0),
            run_time=0.6,
        )
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(3.0)
        self.stop_ambient_camera_rotation()

        # Final hold (1.0s)
        self.wait(1.0)
