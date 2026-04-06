from manim import *

BG_COLOR = "#0f172a"
PAPER_BLUE = "#60a5fa"
ATTN_GOLD = "#fbbf24"
TOKEN_GREEN = "#34d399"
PATH_RED = "#f87171"
SOFT_PURPLE = "#a78bfa"
MUTED_GRAY = "#94a3b8"
CARD_FILL = "#111827"

config.background_color = BG_COLOR

TITLE_SIZE = 40
BODY_SIZE = 26
LABEL_SIZE = 22
SMALL_SIZE = 18
EQ_SIZE = 34
SAFE_WIDTH = 12.0


def safe_text(
    text: str,
    font_size: int = BODY_SIZE,
    color: str = WHITE,
    max_width: float = SAFE_WIDTH,
) -> Text:
    """Text with a simple width cap."""
    mob = Text(text, font_size=font_size, color=color)
    if mob.width > max_width:
        mob.scale_to_fit_width(max_width)
    return mob


def safe_lines(
    *lines: str,
    font_size: int = BODY_SIZE,
    color: str = WHITE,
    max_width: float = SAFE_WIDTH,
    buff: float = 0.2,
) -> VGroup:
    """Stack several text lines vertically."""
    groups = [safe_text(line, font_size=font_size, color=color, max_width=max_width) for line in lines]
    return VGroup(*groups).arrange(DOWN, buff=buff, aligned_edge=LEFT)


def section_title(text: str, color: str = WHITE) -> Text:
    """Title aligned to the top edge."""
    return safe_text(text, font_size=TITLE_SIZE, color=color).to_edge(UP, buff=0.45)


def bottom_note(text: str, color: str = ATTN_GOLD) -> Text:
    """Bottom annotation line."""
    return safe_text(text, font_size=LABEL_SIZE, color=color).to_edge(DOWN, buff=0.4)


def token_box(
    label: str,
    color: str = PAPER_BLUE,
    width: float = 1.35,
    height: float = 0.72,
    fill_opacity: float = 0.22,
) -> VGroup:
    """Rounded token card."""
    rect = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.14,
        color=color,
        fill_color=color,
        fill_opacity=fill_opacity,
        stroke_width=2,
    )
    text = safe_text(label, font_size=LABEL_SIZE, color=WHITE, max_width=width - 0.18)
    text.move_to(rect)
    return VGroup(rect, text)


def attention_cell(value: float, color: str = ATTN_GOLD, size: float = 0.52) -> Square:
    """Small heatmap square with value-driven opacity."""
    return Square(
        side_length=size,
        color=color,
        fill_color=color,
        fill_opacity=max(0.08, min(0.95, value)),
        stroke_width=1.5,
    )


def fade_all(scene: Scene, *mobjects: Mobject) -> None:
    """Fade out many mobjects at once."""
    if mobjects:
        scene.play(*[FadeOut(mob) for mob in mobjects])

