"""Shared style constants for a Manim video project.

Copy this file to your project's utils/style.py and customize the palette.
Import in every scene file: from utils.style import *
"""

from manim import *

# ── Color Palette ────────────────────────────────────────────────
# Assign semantic meaning to colors. Keep consistent across all scenes.
# Viewers learn the vocabulary: "blue = input" carries between scenes.
C = {
    "primary": BLUE_C,
    "secondary": RED_C,
    "accent": YELLOW_C,
    "positive": GREEN_C,
    "negative": RED_D,
    "highlight": PURE_YELLOW,
    "dim": GRAY,
    "label": GRAY_B,
}

# ── Font Sizes ───────────────────────────────────────────────────
TITLE_SIZE = 56
SUBTITLE_SIZE = 36
BODY_SIZE = 32
LABEL_SIZE = 24
EQ_SIZE = 44
EQ_SMALL = 32

# ── Timing (seconds) ────────────────────────────────────────────
HOLD_SHORT = 1.0
HOLD_MEDIUM = 2.0
HOLD_LONG = 3.0


# ── Reusable Components ─────────────────────────────────────────

def labeled_box(
    label: str,
    width: float = 2.5,
    height: float = 1.0,
    color: str = BLUE_C,
    font_size: int = LABEL_SIZE,
) -> VGroup:
    """Labeled rectangle for pipeline/architecture diagrams."""
    rect = RoundedRectangle(
        width=width, height=height, corner_radius=0.1,
        color=color, fill_opacity=0.2, stroke_width=2,
    )
    text = Text(label, font_size=font_size, color=color)
    text.move_to(rect)
    return VGroup(rect, text)


def story_bridge(scene: Scene, text: str) -> None:
    """Brief transition text connecting two narrative phases."""
    bridge = Text(text, font_size=BODY_SIZE, color=C["highlight"])
    scene.play(FadeIn(bridge, shift=UP * 0.3))
    scene.wait(HOLD_MEDIUM)
    scene.play(FadeOut(bridge, shift=UP * 0.3))
