---
name: Production Quality Checklist
description: Spatial layout, alignment, text overlap prevention, container bounds, data viz minimums, and quality checks for Manim animations
tags: [manim, production, quality, alignment, overlap, layout, checklist]
---

# Production Quality Checklist

## 1. Text Overlap Prevention

**Rule: buff >= 0.5 for edge text**
```python
# BAD
label.to_edge(DOWN, buff=0.3)
# GOOD
label.to_edge(DOWN, buff=0.5)
```

**Rule: FadeOut previous bottom text before adding new**
```python
# BAD: overlapping bottom text
self.play(Write(note1))
self.play(Write(note2))  # overlaps note1!

# GOOD
self.play(ReplacementTransform(note1, note2))
# or
self.play(FadeOut(note1))
self.play(Write(note2))
```

**Rule: Reduce font size for dense scenes** -- use LABEL_SIZE (22-24) not BODY_SIZE (30-32) for annotations when many elements are present.

**Rule: Use arrange() / arrange_in_grid() for groups**
```python
# BAD: manual grid positioning
for i in range(16):
    sq.move_to(RIGHT * (i % 4) + DOWN * (i // 4))

# GOOD
grid = VGroup(*[Square() for _ in range(16)])
grid.arrange_in_grid(4, 4, buff=0.05)
```

**Rule: Labels go next_to their target object, not floating at absolute coords.**

## 2. Spatial Layout System

Frame: 14.2 wide x 8 tall, centered at ORIGIN.
Safe bounds: x: [-6.5, 6.5], y: [-3.5, 3.5].

### Named Layout Regions

Partition the screen into regions. Place elements INTO regions, not at arbitrary coordinates.

```
+--------------------------------------------------+
|  TITLE_REGION: y=[2.8, 3.5], full width           |
|--------------------------------------------------|
|  MAIN_LEFT          |  MAIN_RIGHT                  |
|  x=[-6.5, -0.5]    |  x=[0.5, 6.5]               |
|  y=[-2.0, 2.5]     |  y=[-2.0, 2.5]              |
|         MAIN_CENTER: x=[-5, 5], y=[-2, 2.5]       |
|--------------------------------------------------|
|  BOTTOM_REGION: y=[-3.5, -2.5], full width        |
+--------------------------------------------------+
```

**Define in style.py:**
```python
TITLE_Y = 3.0
MAIN_CENTER = ORIGIN + DOWN * 0.2
LEFT_PANEL = LEFT * 3.5
RIGHT_PANEL = RIGHT * 3.5
BOTTOM_Y = -3.2
SAFE_WIDTH = 12.0   # max width for any element
SAFE_HEIGHT = 6.0   # max height for content area
```

### Coordinate Budget Rule

Never use absolute coordinates > 5.5 in x or > 3.2 in y. `shift(RIGHT * 6)` = likely clipped.

```python
# BAD
signal_bar.shift(RIGHT * 6.5 + DOWN * 0.5)
# GOOD: relative positioning
signal_bar.next_to(zoomed_box, RIGHT, buff=0.3)
# GOOD: clamp
x_pos = min(pos, 6.0)
```

### Fill-the-Frame Rule

Visible content should occupy >= 50% of frame area. Fix sparse content by scaling up, adding context, or using full width.

### Dual-Panel Layout

```python
left_panel.move_to(LEFT * 3.2)
right_panel.move_to(RIGHT * 3.2)
divider = DashedLine(UP * 2.5, DOWN * 2.5, color=DIMMED)
```

## 3. Container Boundary Enforcement

Elements inside a container MUST fit within its bounds.

**Rule: Position children relative to the container**
```python
# BAD
container = Rectangle(width=4, height=3).shift(RIGHT * 2)
label = Text("Hello").shift(RIGHT * 5)  # outside!

# GOOD
label = Text("Hello").move_to(container.get_center() + UP * 0.5)
label = Text("Hello").next_to(container.get_top(), DOWN, buff=0.3)
```

**Rule: Scale-to-fit when content might overflow**
```python
if eq.width > container.width - 0.4:
    eq.scale_to_fit_width(container.width - 0.4)
```

**Rule: Cap text width (add safe_text to style.py)**
```python
def safe_text(text: str, max_width: float = 12.0, **kwargs) -> Text:
    """Create text that fits within max_width."""
    t = Text(text, **kwargs)
    if t.width > max_width:
        t.scale_to_fit_width(max_width)
    return t
```

Use for ALL body text and bottom notes (default: 12.0; bottom notes: ~13.0 with 0.5 margin each side).

## 4. Data Visualization Minimums

```python
bar_width >= 0.3       # narrower bars invisible at 720p
bar_height >= 0.2      # shorter bars vanish
fill_opacity >= 0.6    # data elements (bars, dots, areas)
fill_opacity >= 0.3    # background/container elements
stroke_opacity >= 0.8  # lines and borders
dot_radius >= 0.06     # smaller dots vanish at 720p
axes_width >= 5.0      # chart axes >= 40% of frame width
```

## 5. Persistent Element Lifecycle

**Rule: FadeOut titles before reusing their screen region**
```python
# BAD
self.play(pipeline.animate.to_edge(UP))  # overlaps title!

# GOOD
self.play(FadeOut(title), run_time=0.3)
self.play(pipeline.animate.to_edge(UP))
```

**Rule: Track what is on screen.** Before placing a new element, check: "Is anything already in this region?" If yes, FadeOut or move it first.

### Multi-Element Scenes

```python
# always_redraw: geometry changes shape (different endpoints, curves)
curve = always_redraw(lambda: axes.plot(func, ...))

# add_updater: only position/value changes
label.add_updater(lambda m: m.set_value(tracker.get_value()))

# frozen_frame=False during updater sections
self.wait(2, frozen_frame=False)
```

### Scene Length Guidelines

No maximum scene length. Write as much code as the scene needs.
- Simple reveal: 50-100 lines | Parameter sweep: 150-250 lines
- Dual view: 200-300 lines | Full visual proof: 250-350 lines

The 300-line limit applies to SKILL DOCUMENTATION files, not animation code.

## 6. Agent Prompt Requirements

When delegating scene writing to subagents, the prompt MUST include:

1. **Exact paper metadata**: copy exact title, author list, year (never let agents guess)
2. **Alignment**: "Ensure all shapes, labels, annotations are aligned. No flipped/mirrored shapes."
3. **Container rule**: "Elements inside containers must fit within bounds. Use relative positioning."
4. **Lifecycle rule**: "FadeOut persistent elements before new content occupies their region."
5. **Screen bounds**: "All elements fully visible within x:[-7,7] y:[-3.5,3.5]. Scale long text to fit."

## 7. Multi-Scene Render Testing Workflow

`py_compile` catches syntax errors but NOT Manim runtime errors (color type
mismatches, missing mobject attributes, layout overflows). Always use this
two-phase workflow for multi-scene projects:

### Phase 1: Syntax check (fast, ~1s total)
```bash
for f in scene_*.py; do
    python3 -m py_compile "$f" && echo "$f OK" || echo "FAIL: $f"
done
```

### Phase 2: Low-quality render test (~30-60s for 15 scenes)
```bash
for entry in "scene_01.py ClassName" "scene_02.py ClassName" ...; do
    FILE=$(echo "$entry" | awk '{print $1}')
    CLASS=$(echo "$entry" | awk '{print $2}')
    manim -ql "$FILE" "$CLASS" 2>&1 | tail -5
done
```

`-ql` renders at 480p/15fps (10-20x faster than `-qh`) but exercises all
Manim runtime codepaths: color operations, layout math, animation targets.

### Phase 3: Full render only after all scenes pass
```bash
./render_all.sh h   # 1080p, only after ALL -ql tests pass
```

**When to run:** After parallel agent scene generation (agents introduce
subtle runtime issues), style.py changes, or Manim version upgrades.

## 8. Pre-Render Checklist

1. Every text element has a clear position (not default center)
2. Bottom text uses buff >= 0.5
3. Previous bottom text is FadeOut before new text appears
4. Groups use arrange() not manual positioning
5. Labels are next_to their target object
6. All mobjects cleaned up (FadeOut) before next logical section
7. Updaters use frozen_frame=False during wait()
8. Large font text (TITLE_SIZE) scaled down after reveal
9. Child elements fit within parent container bounds
10. No absolute-coordinate elements overflowing containers
11. Persistent titles FadeOut before new content reuses their space
12. Bottom notes width-capped to ~13 Manim units
13. No absolute coordinates > 5.5 in x or > 3.2 in y
14. Content fills >= 50% of the frame (no large dead zones)
15. Data viz bars/dots/lines meet minimum size and opacity thresholds

## 8. Dimming vs FadeOut on Dark Backgrounds

**Rule: DIM_OPACITY = 0.1, never 0.3**

On dark backgrounds (#1e1e2e or similar), elements at 0.3 opacity still compete with primary content. Use 0.1 for aggressive dimming that actually works.

```python
DIM_OPACITY = 0.1  # 0.3 is too visible on dark backgrounds

def dim_mob(scene, *mobs, opacity=DIM_OPACITY):
    scene.play(*[m.animate.set_opacity(opacity) for m in mobs], run_time=0.5)
```

**Rule: Dim BESIDE, FadeOut UNDER**

Use dimming (0.1 opacity) when the dimmed element stays visible as context
BESIDE new content (e.g., dim other metrics while highlighting one).

Use FadeOut when new content will be placed ON TOP of the previous element
(e.g., takeaway text over a pipeline diagram). Even 0.1 opacity colored
elements bleed through white text on dark backgrounds.

```python
# GOOD: dim element that stays to the side while highlighting another
self.play(other_cards.animate.set_opacity(DIM_OPACITY))
self.play(Indicate(active_card))

# GOOD: remove element before overlaying text on the same region
self.play(FadeOut(pipeline))
self.play(Write(takeaway_text))

# BAD: dim then overlay -- colored boxes bleed through white text
self.play(pipeline.animate.set_opacity(DIM_OPACITY))
self.play(Write(takeaway_text))  # text sits on top of visible pipeline
```

## 9. Text Width Enforcement

Manim has NO auto-wrap. Long text will overflow the screen silently.

**Rule: Break all text manually with `\n`**
```python
# BAD: will overflow right edge
Text("This is a very long sentence that explains a complex mathematical concept")

# GOOD: manually broken
Text("This is a very long sentence\nthat explains a complex\nmathematical concept")
```

**Rule: Use safe_text() for all body text**
```python
def safe_text(text: str, max_width: float = 12.0, **kwargs) -> Text:
    t = Text(text, **kwargs)
    if t.width > max_width:
        t.scale_to_fit_width(max_width)
    return t
```

**Rule: Labels near mobjects use font_size <= 18 and short strings (< 30 chars)**

## 10. Only Animate What Visualizes Well

**Rule: If a concept needs explanation before the viewer can understand what they're looking at, choose a different visual.**

Good visuals (self-explanatory):
- Long division showing remainder cycles
- Polygons converging to a circle
- Function plots with shaded areas
- Number lines with marked points
- Side-by-side comparisons

Bad visuals (require narration to decode):
- Abstract coordinate mappings the viewer hasn't seen before
- Wrapping a number line around a circle to "show" irrationality
- Phase space diagrams without buildup
- Any visualization where the axes need explaining first

The test: "Would a first-time viewer understand this visual within 3 seconds of seeing it?"

## 11. Scene Transitions

**Rule: Add connective tissue between scenes**
```python
# Bridge text between scenes
def bridge(scene, text, wait=2.0):
    t = Text(text, font_size=28, color=YELLOW)
    scene.play(FadeIn(t, shift=UP * 0.3))
    scene.wait(wait)
    scene.play(FadeOut(t, shift=UP * 0.3))
```

Use bridge text at act boundaries ("But what does irrational actually mean?") to prevent abrupt jumps.

**Rule: End every scene with fade_all()**
```python
def fade_all(scene, run_time=0.8):
    scene.play(*[FadeOut(m) for m in scene.mobjects], run_time=run_time)
```

## 12. Visual Variety Audit

**Rule: No two consecutive scenes should use the same visual technique.**

Count the distinct visual techniques across all scenes. If > 50% of scenes are "labeled boxes + text," the video will feel flat. Each scene must use at least ONE of:
- `ValueTracker` + `always_redraw` (live updating values)
- `MovingCameraScene` (zoom in/out)
- `interpolate_color` heatmap or gradient
- `Axes` + `plot` (data visualization)
- `BarChart` or manual bar chart with `GrowFromEdge`
- `LaggedStart` with staggered reveals
- Equation dim-and-reveal decomposition

**Minimum variety for an N-scene video:**
- N <= 4: at least 3 distinct techniques
- N = 5-8: at least 5 distinct techniques
- N > 8: at least 6 distinct techniques

**The test:** List each scene and its primary visual technique. If you see "labeled_box pipeline" more than twice, replace one with a live data flow, a heatmap, or a camera zoom.

## 13. Question Frame Minimum

**Rule: At least one question frame per 3 scenes.**

A question frame (catalog pattern #15) poses a question on screen, pauses 2-3 seconds for the viewer to predict, then answers visually. Without them, the viewer is passive. With them, the viewer actively engages.

For an 8-scene video: include at least 2-3 question frames.

```python
# Question frame template
question = Text("Can a small patch of cortex\noutperform surface electrodes?",
                font_size=28, color=YELLOW)
self.play(Write(question))
self.wait(2.5)  # viewer predicts
self.play(FadeOut(question))
# Then show the answer visually (bar chart, number, etc.)
```

## 14. Density Ramp Audit

**Rule: Frame complexity must increase across the video.**

Count the number of visible elements at each scene's midpoint:
- Scene 1-2: 3-5 elements (sparse, inviting)
- Scene 3-5: 6-10 elements (building complexity)
- Scene 6-7: 10-15 elements (peak density)
- Final scene: 3-5 elements (resolution, simplicity)

This creates a narrative arc in visual density. Constant density (every scene has 6 elements) feels monotonous. Starting dense overwhelms.

## 15. Post-Render Checklist

1. No text overlapping other text
2. No text overlapping graphical elements
3. No elements extending off screen
4. Timing feels natural (not too fast, not too slow)
5. Every animation adds meaning (no decorative motion)
6. Equations appear AFTER their visual motivation
7. Author names and paper metadata are correct
8. Visual variety: at least 5 distinct techniques across scenes
9. At least 2 question frames in the video
10. Density ramp: early scenes sparse, middle dense, ending simple
11. At least one scene uses ValueTracker/always_redraw for live values
12. Pipeline scenes show data transforming, not just dots sliding

## 16. Subtitle and Accessibility

**Rule: Add subcaptions on every animation with meaningful content.**

Manim can auto-generate `.srt` subtitle files via `add_subcaption()`. Use this for accessibility and for viewers watching without audio.

```python
class AccessibleScene(Scene):
    def construct(self) -> None:
        eq = MathTex(r"E = mc^2")
        self.add_subcaption("Einstein's mass-energy equivalence equation appears.", duration=2)
        self.play(Write(eq))
        self.wait(1)

        box = SurroundingRectangle(eq, color=YELLOW)
        self.add_subcaption("The equation is highlighted.", duration=1.5)
        self.play(Create(box))
        self.wait(1)
```

To render with subtitles:
```bash
manim -qh --format mp4 scene.py MyScene
# Produces: media/videos/scene/1080p60/MyScene.srt alongside the .mp4
```

**Rule: Minimum font size 20pt for all on-screen text.**

Text smaller than 20pt becomes unreadable at 720p and on mobile devices. Use `font_size=20` as the floor for labels, annotations, and notes.

```python
# BAD: invisible at 720p
label = Text("Source", font_size=14)

# GOOD
label = Text("Source", font_size=20)
```

**Rule: Color contrast for readability.**

All text must be readable against its background. Common failures:

| Bad combination | Fix |
|----------------|-----|
| Light yellow on white/light background | Use YELLOW_D or add a dark text shadow |
| Light gray text on dark gray background | Use WHITE or increase opacity to 1.0 |
| Red text on dark background | Use RED_A (lighter) or add stroke_width=2 |
| Any text over a busy image or gradient | Add a semi-transparent background rectangle |

```python
# When text overlaps a complex background, add a backing rectangle
text = Text("Key insight", font_size=24, color=WHITE)
backing = Rectangle(
    width=text.width + 0.4,
    height=text.height + 0.2,
    fill_color=BLACK,
    fill_opacity=0.7,
    stroke_width=0,
).move_to(text)
readable_text = VGroup(backing, text)
```

## 17. Known Failure Patterns (from production audits)

These bugs recur across builds. Check for each explicitly:

### Text centering with \n
**Bug:** `Text("Line one\nLine two").move_to(ORIGIN)` left-aligns lines.
**Fix:** `safe_multiline("Line one", "Line two").move_to(ORIGIN)`.

### next_to() overflow stacking
**Bug:** `tags.next_to(box, RIGHT)` when box is at x=3.5 pushes tags off-screen.
Guard code clamps them back ON TOP of the box.
**Fix:** Place auxiliary elements BELOW (DOWN) when the source is at |x| > 2.5.

### Title dimmed, not removed
**Bug:** `title.animate.set_opacity(0.35)` -- new text then overlaps the faded title.
**Fix:** Always `FadeOut(title)` completely. Dimming is not lifecycle removal.

### Child covers labeled_box label
**Bug:** `child.move_to(box.get_center())` hides the label text.
**Fix:** `child.move_to(box.get_center() + DOWN * 0.3)`.

### Scale truncates labels
**Bug:** Scaling boxes for split-view makes "Instruction Cache" become "Instr".
**Fix:** Use short labels ("I-Cache") for reduced-size layouts.

### Dim opacity bleeds under overlay text
**Bug:** Pipeline at DIM_OPACITY=0.1 still visible through white text overlay.
**Fix:** `FadeOut(pipeline)` completely when text needs a clean background.

### Empty transition frames
**Bug:** Between phases, only title visible with 80% empty screen.
**Fix:** `self.play(FadeOut(*phase1), Write(new_title))` in same call.

### Arrow tip crowding
**Bug:** Arrow between adjacent boxes has tip overlapping box label.
**Fix:** `pipeline_arrow()` with `buff=0.25` minimum. Increase for close boxes.

### Write() on bottom notes
**Bug:** `Write(note)` creates garbled partial-stroke frames at small font sizes.
**Fix:** `FadeIn(note, shift=UP * 0.2)` for all bottom notes.

### Chart legend overlap
**Bug:** Legend placed in upper-left where curves converge.
**Fix:** Place legend in the corner with LEAST data density.
