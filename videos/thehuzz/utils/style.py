"""Shared style constants for TheHuzz explainer video.

Import in every scene file: from utils.style import *
"""

from manim import *

# -- Background --
BG_COLOR = "#1e1e2e"

# -- Colors (semantic names for hardware security domain) --
CHIP_BLUE = "#4A90D9"       # Processor / DUT
GOLDEN_GREEN = "#2ECC71"    # Golden reference model
BUG_RED = "#E74C3C"         # Bugs, mismatches, vulnerabilities
EXPLOIT_ORANGE = "#E67E22"  # Exploits, attacks
COVERAGE_TEAL = "#1ABC9C"   # Coverage metrics, feedback
OPTIMIZER_PURPLE = "#9B59B6"  # Optimization, weights
MUTATION_YELLOW = "#F1C40F"  # Mutations, highlights
SAFE_GREEN = "#27AE60"      # Correct behavior, match
DIM_GRAY = "#555555"        # Dimmed elements
LABEL_GRAY = "#AAAAAA"      # Labels, annotations

# Shorthand dict
C = {
    "dut": CHIP_BLUE,
    "golden": GOLDEN_GREEN,
    "bug": BUG_RED,
    "exploit": EXPLOIT_ORANGE,
    "coverage": COVERAGE_TEAL,
    "optimizer": OPTIMIZER_PURPLE,
    "mutation": MUTATION_YELLOW,
    "safe": SAFE_GREEN,
    "dim": DIM_GRAY,
    "label": LABEL_GRAY,
}

# -- Font Sizes --
TITLE_SIZE = 42
HEADING_SIZE = 34
BODY_SIZE = 28
LABEL_SIZE = 22
SMALL_SIZE = 18
EQ_SIZE = 32
SMALL_EQ = 26

# -- Layout System --
TITLE_Y = 3.0
SUBTITLE_Y = 2.2
BOTTOM_Y = -3.2
LEFT_X = -3.5
RIGHT_X = 3.5
CENTER_X = 0.0
SAFE_WIDTH = 12.0
SAFE_HEIGHT = 6.0
DIM_OPACITY = 0.1

# Panel bounds
LEFT_PANEL_X = (-6.0, -0.8)
RIGHT_PANEL_X = (0.8, 6.0)
PANEL_Y = (-2.0, 2.2)

# Persistent header region
HEADER_Y = (2.0, 3.2)
HEADER_SCALE = 0.45

# -- Timing (seconds) --
HOLD_SHORT = 1.0
HOLD_MEDIUM = 2.0
HOLD_LONG = 3.0


# -- Safe Helpers --

def section_title(text: str, color=WHITE) -> Text:
    """Create a section title at standard position."""
    return Text(text, font_size=TITLE_SIZE, color=color).to_edge(UP, buff=0.5)


def safe_text(
    text: str,
    font_size: int = BODY_SIZE,
    color=WHITE,
    max_width: float = 12.0,
) -> Text:
    """Create text with automatic width capping."""
    t = Text(text, font_size=font_size, color=color)
    if t.width > max_width:
        t.scale_to_fit_width(max_width)
    return t


def bottom_note(text: str, color=MUTATION_YELLOW) -> Text:
    """Create a bottom note with width safety."""
    t = Text(text, font_size=LABEL_SIZE, color=color)
    if t.width > SAFE_WIDTH:
        t.scale_to_fit_width(SAFE_WIDTH)
    return t.to_edge(DOWN, buff=0.5)


def labeled_box(
    label: str,
    width: float = 2.5,
    height: float = 0.8,
    color: str = CHIP_BLUE,
    font_size: int = LABEL_SIZE,
    fill_opacity: float = 0.2,
) -> VGroup:
    """Labeled rectangle for pipeline/architecture diagrams."""
    rect = RoundedRectangle(
        width=width, height=height, corner_radius=0.15,
        color=color, fill_opacity=fill_opacity, stroke_width=2,
    )
    text = Text(label, font_size=font_size, color=color)
    text.move_to(rect)
    if text.width > width - 0.3:
        text.scale_to_fit_width(width - 0.3)
    return VGroup(rect, text)


def pipeline_arrow(start, end, color=WHITE, stroke_width=3) -> Arrow:
    """Create a pipeline arrow between two mobjects."""
    return Arrow(
        start.get_right(), end.get_left(),
        buff=0.15, color=color, stroke_width=stroke_width,
        max_tip_length_to_length_ratio=0.15,
    )


def fade_all(scene: Scene, *mobjects) -> None:
    """FadeOut multiple mobjects at once."""
    if mobjects:
        scene.play(*[FadeOut(m) for m in mobjects])


def story_bridge(scene: Scene, text: str) -> None:
    """Transition text between narrative phases."""
    bridge = Text(text, font_size=HEADING_SIZE, color=MUTATION_YELLOW)
    scene.play(FadeIn(bridge, shift=UP * 0.3))
    scene.wait(HOLD_MEDIUM)
    scene.play(FadeOut(bridge, shift=UP * 0.3))
