"""Shared style for Fused Gromov-Wasserstein explainer video.

Import in every scene: from utils.style import *
"""
from manim import *  # noqa: F403

# -- Color Palette (semantic) ------------------------------------------------
KG1_COLOR = BLUE_C          # Knowledge Graph 1 entities and edges
KG2_COLOR = RED_C           # Knowledge Graph 2 entities and edges
KG1_EDGE = BLUE_D
KG2_EDGE = RED_D
TRANSPORT_COLOR = YELLOW    # Transport plan / coupling
MATCH_GOOD = GREEN_C        # Correct alignment
MATCH_BAD = RED_D           # Wrong alignment
STRUCTURE_COLOR = TEAL_C    # Structural similarity
FEATURE_COLOR = ORANGE      # Feature / semantic similarity
ANCHOR_COLOR = YELLOW_A     # Anchor pairs
MUTED_GRAY = GRAY_B
DIM_GRAY = GRAY_D

# -- Font Sizes ---------------------------------------------------------------
TITLE_SIZE = 48
SUBTITLE_SIZE = 34
BODY_SIZE = 30
LABEL_SIZE = 22
EQ_SIZE = 40
EQ_SMALL = 30
NODE_LABEL_SIZE = 20

# -- Timing -------------------------------------------------------------------
HOLD_SHORT = 1.0
HOLD_MEDIUM = 2.0
HOLD_LONG = 3.0

# -- Layout -------------------------------------------------------------------
TITLE_Y = 3.0
BOTTOM_Y = -3.2
SAFE_WIDTH = 12.0
LEFT_X = -3.5
RIGHT_X = 3.5


# -- Reusable Components ------------------------------------------------------

def kg_node(
    label: str,
    color=KG1_COLOR,
    radius: float = 0.35,
    font_size: int = NODE_LABEL_SIZE,
    fill_opacity: float = 0.25,
) -> VGroup:
    """A knowledge graph entity node (circle + label)."""
    circ = Circle(radius=radius, color=color, fill_opacity=fill_opacity, stroke_width=2)
    txt = Text(label, font_size=font_size, color=color)
    if txt.width > radius * 1.6:
        txt.scale_to_fit_width(radius * 1.6)
    txt.move_to(circ)
    return VGroup(circ, txt)


def kg_edge(
    start: VGroup,
    end: VGroup,
    label: str = "",
    color=KG1_EDGE,
    font_size: int = 16,
) -> VGroup:
    """An edge between two KG nodes with optional relation label."""
    line = Line(
        start.get_center(), end.get_center(),
        color=color, stroke_width=2, buff=0.35,
    )
    group = VGroup(line)
    if label:
        lbl = Text(label, font_size=font_size, color=color)
        lbl.move_to(line.get_center())
        lbl.shift(UP * 0.2)
        if lbl.width > line.get_length() * 0.8:
            lbl.scale_to_fit_width(line.get_length() * 0.8)
        group.add(lbl)
    return group


def alignment_arrow(
    left_node: VGroup,
    right_node: VGroup,
    color=TRANSPORT_COLOR,
    dashed: bool = True,
) -> VGroup:
    """Dashed alignment arrow between nodes in two KGs."""
    cls = DashedLine if dashed else Line
    return cls(
        left_node.get_right() + RIGHT * 0.05,
        right_node.get_left() + LEFT * 0.05,
        color=color, stroke_width=2,
    )


def transport_cell(
    value: float,
    size: float = 0.5,
    max_opacity: float = 0.9,
) -> Square:
    """A cell in a transport plan matrix, opacity proportional to value."""
    sq = Square(side_length=size, stroke_width=0.5, stroke_color=WHITE)
    sq.set_fill(TRANSPORT_COLOR, opacity=value * max_opacity)
    return sq


def section_title(text: str, color=WHITE) -> Text:
    """Section title at standard top position."""
    return Text(text, font_size=TITLE_SIZE, color=color).to_edge(UP, buff=0.5)


def safe_text(
    text: str,
    font_size: int = BODY_SIZE,
    color=WHITE,
    max_width: float = SAFE_WIDTH,
) -> Text:
    """Single-line text with automatic width capping."""
    t = Text(text, font_size=font_size, color=color)
    if t.width > max_width:
        t.scale_to_fit_width(max_width)
    return t


def safe_lines(
    *lines: str,
    font_size: int = BODY_SIZE,
    color=WHITE,
    line_buff: float = 0.3,
    max_width: float = SAFE_WIDTH,
) -> VGroup:
    """Multi-line centered text block."""
    texts = []
    for line in lines:
        t = Text(line, font_size=font_size, color=color)
        if t.width > max_width:
            t.scale_to_fit_width(max_width)
        texts.append(t)
    return VGroup(*texts).arrange(DOWN, buff=line_buff, center=True)


def bottom_note(text: str, color=YELLOW) -> Text:
    """Bottom annotation with width safety."""
    t = Text(text, font_size=LABEL_SIZE, color=color)
    if t.width > SAFE_WIDTH:
        t.scale_to_fit_width(SAFE_WIDTH)
    return t.to_edge(DOWN, buff=0.5)


def fade_all(scene: Scene, *mobjects) -> None:
    """FadeOut multiple mobjects at once."""
    if mobjects:
        scene.play(*[FadeOut(m) for m in mobjects])
