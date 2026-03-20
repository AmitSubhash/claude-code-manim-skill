"""Safe wrappers around Manim APIs that silently handle known gotchas.

Import this instead of writing raw Manim calls for the tricky APIs.
Usage: from safe_manim import *
"""

from manim import *
from typing import Any


def safe_arrow(start, end, color=WHITE, stroke_width=3, **kwargs) -> Arrow:
    """Arrow that avoids the interpolate_color tip crash.

    Never pass interpolate_color() to Arrow's color param.
    Use this instead of Arrow() when color might be dynamic.
    """
    arr = Arrow(start=start, end=end, color=color, stroke_width=stroke_width,
                **{k: v for k, v in kwargs.items()
                   if k not in ("stroke_opacity",)})
    if "stroke_opacity" in kwargs:
        arr.set_opacity(kwargs["stroke_opacity"])
    return arr


def safe_brace_label(brace: Brace, text: str, font_size: int = 24,
                     color=WHITE) -> Tex:
    """Create a brace label without the font_size kwarg crash.

    Brace.get_text(font_size=) crashes. This creates the Tex
    separately and positions it at the tip.
    """
    label = Tex(text, font_size=font_size, color=color)
    brace.put_at_tip(label)
    return label


def safe_lagged_write(group, lag_ratio: float = 0.2,
                      run_time: float = 1.5) -> LaggedStart:
    """LaggedStart with Write that doesn't crash on Text objects.

    LaggedStartMap(Write, group) crashes. This uses the safe pattern.
    """
    return LaggedStart(
        *[Write(m) for m in group],
        lag_ratio=lag_ratio,
        run_time=run_time,
    )


def safe_get_part(eq: MathTex, tex: str, fallback_color=None) -> Any:
    """get_part_by_tex that doesn't return None silently.

    Returns the part if found. If not found and fallback_color is set,
    returns None without crashing. Otherwise raises ValueError.
    """
    part = eq.get_part_by_tex(tex)
    if part is None and fallback_color is None:
        raise ValueError(
            f"get_part_by_tex('{tex}') returned None. "
            f"Check that '{tex}' appears in your equation as a separate submobject. "
            f"Use {{ }} notation or substrings_to_isolate to isolate it."
        )
    return part


def safe_replacement_transform(source, target, scene, **kwargs):
    """ReplacementTransform that's explicit about what it does.

    Use this instead of Transform to avoid ghost object confusion.
    After this call, target is in the scene and source is removed.
    """
    scene.play(ReplacementTransform(source, target, **kwargs))
    return target  # return the live object for chaining
