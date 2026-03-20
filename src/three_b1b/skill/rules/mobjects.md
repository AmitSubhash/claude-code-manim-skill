---
name: mobjects
description: Mobject hierarchy, VMobject, VGroup, positioning, styling - first-principles guide
tags: mobject, vmobject, vgroup, positioning, styling
---

# Mobjects

## What is a Mobject?

"Mobject" stands for **Mathematical Object**. It is the base class for *everything*
visible on screen in Manim -- every circle, line, equation, image, and arrow.

A Mobject carries four things:
1. **A position** in 2D/3D space, stored as a numpy array `[x, y, z]`.
2. **A set of points** -- vertices or curve samples that define its shape.
3. **Visual properties** -- color, opacity, stroke width, fill color.
4. **Child objects (submobjects)** -- other Mobjects nested inside it, forming a tree.

You never write `Mobject()` directly. You use subclasses: `Circle`, `Square`,
`Text`, `MathTex`, `Arrow`, etc. Each subclass generates the right points for its shape.

Think of Mobjects as shapes on an infinite canvas. The camera shows a rectangular
window (roughly 14.2 units wide by 8 units tall). Anything outside exists but is hidden.

## The Mobject family tree

Each level adds capabilities the parent lacks.

```
Mobject -- base class with position, submobjects, basic transforms (shift/scale/rotate)
 +-- VMobject (Vector Mobject) -- adds stroke/fill. All curve-based shapes live here.
 |    +-- VGroup -- collection of VMobjects as one unit (move/color/scale together)
 +-- Group -- like VGroup but for ANY Mobject type (use when mixing images + shapes)
 +-- ImageMobject -- raster images (PNG/JPG). Not vector; can't animate parts.
 +-- ValueTracker -- invisible, stores a float. Drives animations via updaters.
```

**Rule of thumb:** grouping shapes/text/equations? Use `VGroup`.
Group includes an `ImageMobject`? Use `Group`.

## Creating shapes

```python
# Circle: radius in Manim units. fill_opacity: 0=hollow, 1=solid.
circle = Circle(radius=1, color=BLUE, fill_opacity=0.5)
# Square: side_length in Manim units.
square = Square(side_length=2, color=RED)
# Rectangle: independent width and height.
rect = Rectangle(width=4, height=2)
# Dot: a tiny filled circle at a point. ORIGIN = screen center (0,0,0).
dot = Dot(point=ORIGIN, radius=0.08, color=WHITE)
# Line: start/end are points (numpy arrays or direction constants).
line = Line(start=LEFT, end=RIGHT, color=YELLOW)
# Arrow: line with tip. buff = gap between tip and endpoint (0 = touching).
arrow = Arrow(start=LEFT, end=RIGHT, buff=0)
# Text: rendered with Pango (system fonts, no LaTeX needed).
text = Text("Hello", font_size=48, color=WHITE)
# MathTex: rendered with LaTeX. Use raw strings so backslashes pass through.
math = MathTex(r"E = mc^2")  # see equations.md for details
```

## Positioning: where things go on screen

### The coordinate system

Manim uses a math coordinate system: origin at screen center, X right, Y up.
Visible area spans roughly X: [-7.1, 7.1] and Y: [-4, 4].

Direction constants (numpy arrays) let you avoid raw numbers:

```python
UP = (0,1,0)    DOWN = (0,-1,0)    LEFT = (-1,0,0)    RIGHT = (1,0,0)
ORIGIN = (0,0,0)
UL = UP+LEFT     UR = UP+RIGHT     DL = DOWN+LEFT     DR = DOWN+RIGHT
```

Scale them: `3 * RIGHT` = point (3,0,0).
Combine them: `2 * UP + 3 * RIGHT` = point (3,2,0).

### Positioning methods

```python
# ABSOLUTE: move center to a specific point.
mob.move_to(ORIGIN)                    # screen center
mob.move_to(2 * UP + 3 * RIGHT)       # point (3, 2)

# RELATIVE: shift from current position.
mob.shift(RIGHT)                       # 1 unit right from current spot

# NEXT TO another mobject. direction = which side, buff = gap size.
mob.next_to(other_mob, RIGHT, buff=0.25)

# SNAP TO EDGE/CORNER. buff = distance from screen boundary.
mob.to_edge(UP, buff=0.5)
mob.to_corner(UL, buff=0.5)

# ALIGN one edge with another mobject's edge.
mob.align_to(other_mob, UP)            # match top edges
```

### Progressive examples

```python
# 1. Circle at center (default position).
circle = Circle(radius=1, color=BLUE)
# 2. Move to upper-right.
circle.move_to(2 * UP + 3 * RIGHT)
# 3. Label next to circle with a small gap.
label = Text("r=1", font_size=36)
label.next_to(circle, RIGHT, buff=0.3)
# 4. Three shapes in a horizontal row.
shapes = VGroup(Circle(), Square(), Triangle())
shapes.arrange(RIGHT, buff=0.5)
```

### Reading positions back

```python
mob.get_center()     mob.get_top()       mob.get_bottom()
mob.get_left()       mob.get_right()     mob.get_corner(UR)
```

## Sizing and scaling

```python
mob.scale(2)                           # multiply size by factor (2=double, 0.5=half)
mob.scale_to_fit_width(4)             # scale to exact width in Manim units
mob.scale_to_fit_height(2)            # scale to exact height
mob.stretch(2, dim=0)                  # non-uniform: dim=0 horizontal, dim=1 vertical
mob.set(width=4)                       # set width directly (calls scale internally)
mob.set(height=2)                      # set height directly

# Rotation: angle in radians by default.
mob.rotate(PI / 4)                     # 45 degrees counterclockwise
mob.rotate(45 * DEGREES)              # same thing using DEGREES constant
mob.rotate(PI / 2, about_point=ORIGIN) # orbit around a point, not own center
```

## Styling: colors and appearance

Manim has ~170 predefined color constants: `RED`, `BLUE`, `GREEN`, `YELLOW`,
`PURPLE`, `TEAL`, `ORANGE`, `PINK`, `WHITE`, `GREY`, etc.

Variants A-E go lightest to darkest: `BLUE_A` (lightest) to `BLUE_E` (darkest).
Plain `BLUE` equals `BLUE_C` (middle). Custom: `ManimColor("#1F77B4")`.

```python
mob.set_color(RED)                     # overall color (stroke + fill)
mob.set_fill(BLUE, opacity=0.5)       # fill interior; 0=transparent, 1=solid
mob.set_stroke(YELLOW, width=4)       # outline; width in pixels
mob.set_opacity(0.5)                   # overall transparency
mob.set_z_index(1)                     # layering: higher = drawn on top (default 0)
mob.set_color_by_gradient(RED, BLUE)  # gradient across the shape
```

## VGroup: working with collections

A `VGroup` holds multiple VMobjects as one unit. Without it, you would have
to move/color/scale each shape individually.

```python
group = VGroup(circle, square, triangle)
group.shift(UP)                        # moves all three together
group.scale(0.5)                       # scales all three together
group.set_color(RED)                   # colors all three
```

### Layout

```python
group.arrange(RIGHT, buff=0.5)        # horizontal row with 0.5-unit gaps
group.arrange(DOWN, buff=0.25)        # vertical stack
group.arrange_in_grid(rows=2, cols=3, buff=0.5)
```

### Indexing and iteration

```python
group[0]             # first element
group[-1]            # last element
group[1:3]           # slice (returns new VGroup)
for mob in group:    # iterate
    mob.set_color(BLUE)
```

### Adding and removing

```python
group.add(new_mob)
group.remove(old_mob)
```

## The .animate syntax (preview)

Any method becomes a smooth animation when called on `.animate`:

```python
circle.shift(RIGHT)                    # instant (no animation)
self.play(circle.animate.shift(RIGHT)) # smooth slide over 1 second
self.play(circle.animate.set_color(RED).scale(2))  # chain multiple changes
self.play(circle.animate.rotate(PI/2), run_time=2, rate_func=smooth)
```

Full details on animations and rate functions in animations.md.

## Copy and state management

```python
circle_copy = circle.copy()            # independent deep copy
circle.save_state()                    # snapshot position, color, size, etc.
circle.set_color(RED).scale(3)         # make temporary changes
self.play(Restore(circle))            # animate back to saved state
```

## Common spacing constants

Used throughout Manim for `buff` parameters. Avoids magic numbers.

```python
SMALL_BUFF     = 0.1     # tight spacing
MED_SMALL_BUFF = 0.25    # default for next_to()
MED_LARGE_BUFF = 0.5     # comfortable spacing
LARGE_BUFF     = 1.0     # generous spacing
```

## Useful geometry reference

```python
# Polygons
Triangle()                              RegularPolygon(n=6)  # hexagon
Polygon(UL, UR, DR, DL)                RoundedRectangle(corner_radius=0.5, width=4, height=2)
# Curves
Arc(radius=1, start_angle=0, angle=PI/2)
ArcBetweenPoints(start, end, angle=PI/4)
CubicBezier(p0, p1, p2, p3)            Ellipse(width=4, height=2)
Annulus(inner_radius=0.5, outer_radius=1)
# Dashed variants
DashedLine(start=LEFT, end=RIGHT, dash_length=0.1)
DashedVMobject(any_vmobject, num_dashes=15)
# Axes and number lines
NumberLine(x_range=[-5, 5, 1], length=10, include_numbers=True)
# Images and SVGs (not VMobjects -- use Group, not VGroup, to mix with shapes)
ImageMobject("path/to/image.png")       SVGMobject("path/to/icon.svg")
```
