"""
TRIBE v2 Video - Shared Style Contract
Semantic colors, layout constants, and helpers for all 12 scenes.
Domain: Computational Neuroscience / Multimodal Brain Encoding
"""
from manim import *

# ── Background ──────────────────────────────────────────────────────────
BG_COLOR = "#1a1a2e"

# ── Domain Colors (semantic) ────────────────────────────────────────────
VIDEO_BLUE = "#4A90D9"       # Video modality / V-JEPA 2
AUDIO_GREEN = "#2ECC71"      # Audio modality / Wav2Vec-BERT
TEXT_ORANGE = "#E67E22"      # Text modality / LLaMA
BRAIN_PURPLE = "#9B59B6"     # Brain cortex / neural activity
BOLD_RED = "#E74C3C"         # BOLD signal / fMRI
TRANSFORM_TEAL = "#1ABC9C"   # Transformer / integration
RESULT_GOLD = "#F1C40F"      # Results / highlights / novel contribution
SUBJECT_PINK = "#E91E63"     # Subject-specific components
BASELINE_GRAY = "#7F8C8D"    # Baselines / prior work
DANGER_RED = "#C0392B"       # Limitations / failures
LABEL_GRAY = "#95A5A6"       # Secondary labels / annotations
ACCENT = RESULT_GOLD

# Color shorthand dict
C = {
    "video": VIDEO_BLUE,
    "audio": AUDIO_GREEN,
    "text": TEXT_ORANGE,
    "brain": BRAIN_PURPLE,
    "bold": BOLD_RED,
    "transformer": TRANSFORM_TEAL,
    "result": RESULT_GOLD,
    "subject": SUBJECT_PINK,
    "baseline": BASELINE_GRAY,
    "danger": DANGER_RED,
    "label": LABEL_GRAY,
}

# ── Opacity ─────────────────────────────────────────────────────────────
DIM_OPACITY = 0.1  # Never 0.3 on dark backgrounds

# ── Font Sizes ──────────────────────────────────────────────────────────
TITLE_SIZE = 42
HEADING_SIZE = 34
BODY_SIZE = 28
LABEL_SIZE = 22
SMALL_LABEL = 18
EQ_SIZE = 32
SMALL_EQ = 26

# ── Layout Constants ────────────────────────────────────────────────────
TITLE_Y = 3.0
SUBTITLE_Y = 2.2
BOTTOM_Y = -3.2
LEFT_X = -3.5
RIGHT_X = 3.5
CENTER_X = 0.0
SAFE_WIDTH = 12.0
SAFE_HEIGHT = 6.0

# Panel regions
LEFT_PANEL_X = (-6.0, -0.8)
RIGHT_PANEL_X = (0.8, 6.0)
HEADER_Y = (2.0, 3.2)
HEADER_SCALE = 0.45

# ── Timing ──────────────────────────────────────────────────────────────
HOLD_SHORT = 1.0
HOLD_MEDIUM = 2.0
HOLD_LONG = 3.0

# ── Text Helpers ────────────────────────────────────────────────────────

def safe_text(
    text: str,
    font_size: int = BODY_SIZE,
    color: str = WHITE,
    max_width: float = 12.0,
) -> Text:
    """Single-line text with width cap."""
    t = Text(text, font_size=font_size, color=color)
    if t.width > max_width:
        t.scale_to_fit_width(max_width)
    return t


def safe_multiline(
    *lines: str,
    font_size: int = BODY_SIZE,
    color: str = WHITE,
    line_buff: float = 0.3,
    max_width: float = 12.0,
) -> VGroup:
    """Centered multi-line text. Each line is a separate Text in a VGroup."""
    texts = []
    for line in lines:
        t = Text(line, font_size=font_size, color=color)
        if t.width > max_width:
            t.scale_to_fit_width(max_width)
        texts.append(t)
    return VGroup(*texts).arrange(DOWN, buff=line_buff, center=True)


def section_title(text: str, color: str = WHITE) -> Text:
    """Title at top edge."""
    return Text(text, font_size=TITLE_SIZE, color=color).to_edge(UP, buff=0.5)


def bottom_note(text: str, color: str = RESULT_GOLD) -> Text:
    """Bottom annotation. Animate with FadeIn(shift=UP*0.2), NOT Write()."""
    t = Text(text, font_size=LABEL_SIZE, color=color)
    if t.width > SAFE_WIDTH:
        t.scale_to_fit_width(SAFE_WIDTH)
    return t.to_edge(DOWN, buff=0.5)


# ── Diagram Helpers ─────────────────────────────────────────────────────

def labeled_box(
    label: str,
    width: float = 2.5,
    height: float = 1.0,
    color: str = BLUE_C,
    font_size: int = LABEL_SIZE,
    fill_opacity: float = 0.2,
) -> VGroup:
    """Rounded rectangle with centered label."""
    rect = RoundedRectangle(
        width=width, height=height, corner_radius=0.1,
        color=color, fill_opacity=fill_opacity, stroke_width=2,
    )
    text = Text(label, font_size=font_size, color=color)
    text.move_to(rect)
    if text.width > width - 0.3:
        text.scale_to_fit_width(width - 0.3)
    return VGroup(rect, text)


def pipeline_arrow(
    start: Mobject,
    end: Mobject,
    color: str = WHITE,
    stroke_width: float = 3,
) -> Arrow:
    """Arrow between pipeline boxes with proper spacing."""
    return Arrow(
        start.get_right(), end.get_left(), buff=0.25,
        color=color, stroke_width=stroke_width,
        max_tip_length_to_length_ratio=0.15,
    )


def down_arrow(
    start: Mobject,
    end: Mobject,
    color: str = WHITE,
    stroke_width: float = 3,
) -> Arrow:
    """Vertical arrow from bottom of start to top of end."""
    return Arrow(
        start.get_bottom(), end.get_top(), buff=0.2,
        color=color, stroke_width=stroke_width,
        max_tip_length_to_length_ratio=0.15,
    )


def snowflake_icon(color: str = WHITE, scale: float = 0.3) -> VGroup:
    """Simple snowflake icon indicating frozen weights."""
    lines = VGroup()
    for angle in [0, PI / 3, 2 * PI / 3]:
        line = Line(UP * 0.4, DOWN * 0.4, color=color, stroke_width=2)
        line.rotate(angle)
        lines.add(line)
    return lines.scale(scale)


def subject_icon(color: str = SUBJECT_PINK, scale: float = 0.4) -> VGroup:
    """Simple person icon."""
    head = Circle(radius=0.15, color=color, fill_opacity=0.8, stroke_width=1)
    body = Line(ORIGIN, DOWN * 0.3, color=color, stroke_width=2)
    head.next_to(body, UP, buff=0.0)
    return VGroup(head, body).scale(scale)


def brain_outline(
    width: float = 6.0,
    height: float = 3.5,
    color: str = BRAIN_PURPLE,
) -> Ellipse:
    """Simplified brain surface as ellipse."""
    return Ellipse(
        width=width, height=height,
        color=color, fill_opacity=0.05, stroke_width=2,
    )


def modality_badge(
    label: str,
    color: str,
    width: float = 1.8,
) -> VGroup:
    """Small rounded badge for modality labels."""
    rect = RoundedRectangle(
        width=width, height=0.5, corner_radius=0.15,
        color=color, fill_opacity=0.3, stroke_width=1.5,
    )
    text = Text(label, font_size=SMALL_LABEL, color=color)
    text.move_to(rect)
    if text.width > width - 0.2:
        text.scale_to_fit_width(width - 0.2)
    return VGroup(rect, text)


# ── Scene Helpers ───────────────────────────────────────────────────────

def fade_all(scene: Scene, *mobjects: Mobject) -> None:
    """FadeOut multiple mobjects in one play call."""
    if mobjects:
        scene.play(*[FadeOut(m) for m in mobjects])


def story_bridge(scene: Scene, text: str) -> None:
    """Transition text between phases within a scene."""
    bridge = Text(text, font_size=HEADING_SIZE, color=ACCENT)
    scene.play(FadeIn(bridge, shift=UP * 0.3))
    scene.wait(HOLD_MEDIUM)
    scene.play(FadeOut(bridge, shift=UP * 0.3))


def region_highlight(
    brain: Mobject,
    x_offset: float,
    y_offset: float,
    radius: float = 0.6,
    color: str = RESULT_GOLD,
    opacity: float = 0.4,
) -> Circle:
    """Highlight a region on the brain outline."""
    highlight = Circle(
        radius=radius, color=color,
        fill_opacity=opacity, stroke_width=1.5,
    )
    highlight.move_to(brain.get_center() + RIGHT * x_offset + UP * y_offset)
    return highlight
