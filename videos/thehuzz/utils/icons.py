"""Reusable icon mobjects for TheHuzz explainer video scenes."""

from manim import *
from utils.style import (
    BUG_RED,
    MUTATION_YELLOW,
    OPTIMIZER_PURPLE,
    SMALL_SIZE,
    DIM_GRAY,
)


def branch_tree_icon(color: str = BUG_RED) -> VGroup:
    """Simple branching tree: root -> two branches -> four leaves.

    Parameters
    ----------
    color : str
        Stroke color for all lines.

    Returns
    -------
    VGroup
        Root + branch lines.
    """
    root = Line(ORIGIN, UP * 0.4, color=color, stroke_width=3)

    bl = Line(root.get_end(), root.get_end() + LEFT * 0.3 + UP * 0.3, color=color, stroke_width=2)
    br = Line(root.get_end(), root.get_end() + RIGHT * 0.3 + UP * 0.3, color=color, stroke_width=2)

    ll = Line(bl.get_end(), bl.get_end() + LEFT * 0.2 + UP * 0.25, color=color, stroke_width=1.5)
    lr = Line(bl.get_end(), bl.get_end() + RIGHT * 0.2 + UP * 0.25, color=color, stroke_width=1.5)
    rl = Line(br.get_end(), br.get_end() + LEFT * 0.2 + UP * 0.25, color=color, stroke_width=1.5)
    rr = Line(br.get_end(), br.get_end() + RIGHT * 0.2 + UP * 0.25, color=color, stroke_width=1.5)

    return VGroup(root, bl, br, ll, lr, rl, rr)


def magnifying_glass_icon(color: str = MUTATION_YELLOW) -> VGroup:
    """Circle with a diagonal handle line.

    Parameters
    ----------
    color : str
        Stroke color.

    Returns
    -------
    VGroup
        Lens circle + handle line.
    """
    lens = Circle(radius=0.3, color=color, stroke_width=3)
    handle = Line(
        lens.get_center() + RIGHT * 0.21 + DOWN * 0.21,
        lens.get_center() + RIGHT * 0.5 + DOWN * 0.5,
        color=color,
        stroke_width=3,
    )
    return VGroup(lens, handle)


def dual_rect_icon(color: str = OPTIMIZER_PURPLE) -> VGroup:
    """Two labelled rectangles side by side (RFUZZ / DifuzzRTL).

    Parameters
    ----------
    color : str
        Fill and stroke color.

    Returns
    -------
    VGroup
        Two rectangle+label pairs arranged horizontally.
    """
    r1 = Rectangle(
        width=0.4, height=0.55,
        color=color, fill_color=color, fill_opacity=0.4, stroke_width=2,
    )
    r2 = Rectangle(
        width=0.4, height=0.55,
        color=color, fill_color=color, fill_opacity=0.4, stroke_width=2,
    )
    label1 = Text("R", font_size=SMALL_SIZE, color=color)
    label1.move_to(r1)
    label2 = Text("D", font_size=SMALL_SIZE, color=color)
    label2.move_to(r2)
    group = VGroup(VGroup(r1, label1), VGroup(r2, label2))
    group.arrange(RIGHT, buff=0.2)
    return group
