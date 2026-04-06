"""Shared style for v0.3.0 showcase video."""

from manim import *

# -- Palette -----------------------------------------------------------------
BG = "#0f0f1a"
GOLD = "#FFD700"
TEAL = "#2EC4B6"
CORAL = "#FF6B6B"
ELECTRIC = "#4EA8DE"
VIOLET = "#9B5DE5"
MINT = "#00F5D4"
SLATE = "#6B7280"
WARM_WHITE = "#F5F0EB"
MONO = "Menlo"

TITLE_SIZE = 48
BODY_SIZE = 28
LABEL_SIZE = 20
EQ_SIZE = 40


def safe_text(text, font_size=BODY_SIZE, color=WARM_WHITE, max_width=12.0):
    t = Text(text, font=MONO, font_size=font_size, color=color)
    if t.width > max_width:
        t.scale_to_fit_width(max_width)
    return t
