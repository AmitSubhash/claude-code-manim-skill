---
name: Troubleshooting
description: Common Manim errors, their causes, and fixes - from LaTeX failures to rendering issues
tags: [manim, troubleshooting, errors, debugging, common-mistakes]
---

# Troubleshooting Manim

## LaTeX errors

### "LaTeX compilation error" or "failed to compile"

**Cause:** Your LaTeX string has a syntax error, or LaTeX is not installed.

**Check LaTeX is installed:**
```bash
# macOS
which pdflatex   # should return a path
# If missing:
brew install --cask mactex-no-gui

# Linux
which pdflatex
# If missing:
sudo apt install texlive-full
```

**Common LaTeX syntax errors:**
```python
# BAD: forgot raw string - Python interprets \f as form-feed
MathTex("\frac{1}{2}")

# GOOD: raw string
MathTex(r"\frac{1}{2}")

# BAD: unbalanced braces
MathTex(r"\frac{1}{2")

# GOOD
MathTex(r"\frac{1}{2}")

# BAD: percent sign (starts LaTeX comment, eats rest of line)
MathTex(r"50%")

# GOOD
MathTex(r"50\%")
```

### "Package not found" (e.g., physics, bm)

**Cause:** Your LaTeX string uses a package not in Manim's default template.

```python
template = TexTemplate()
template.add_to_preamble(r"\usepackage{physics}")
eq = MathTex(r"\bra{\psi}", tex_template=template)
```

## Animation errors

### "Mobject not found in scene" after Transform

**Cause:** You used `Transform(A, B)` then tried to animate `B`. But Transform keeps `A` in the scene (just makes it look like `B`). `B` was never added.

**Fix:** Use `ReplacementTransform(A, B)` instead. After this, `B` is in the scene and `A` is removed.

### Nothing happens when I call self.play()

**Cause 1:** The mobject is not in the scene. You need `self.add(mob)` or a creation animation first.

**Cause 2:** The animation does not change anything. e.g., `self.play(mob.animate.move_to(mob.get_center()))` moves to where it already is.

### Updaters stop running during self.wait()

**Cause:** By default, `self.wait()` freezes the frame for performance. Updaters do not run.

**Fix:** `self.wait(frozen_frame=False)`

### Late-binding closure bug in loops

```python
# BAD: all updaters reference the LAST value of `obj`
for obj in objects:
    label.add_updater(lambda m: m.next_to(obj, UP))

# GOOD: capture `obj` with default argument
for obj in objects:
    label.add_updater(lambda m, o=obj: m.next_to(o, UP))
```

### LaggedStartMap(Write, group) crashes

**Cause:** `Write` wraps `DrawBorderThenFill` internally, and `LaggedStartMap` tries to call it as `Write(submobject)` which fails on some mobject types (especially `Text`).

**Fix:** Use `LaggedStart` with an explicit list comprehension:
```python
# BAD: crashes on Text/Tex groups
self.play(LaggedStartMap(Write, text_group, lag_ratio=0.2))

# GOOD: explicit list comprehension
self.play(LaggedStart(*[Write(m) for m in text_group], lag_ratio=0.2))
```

Note: `LaggedStartMap(FadeIn, group)` and `LaggedStartMap(Create, group)` work fine. The issue is specific to `Write`.

### interpolate_color crashes with hex string constants

**Cause:** `interpolate_color()` calls `.interpolate()` on its arguments, which
requires `ManimColor` objects. Custom hex string constants (e.g., `CHIP_BLUE = "#4A90D9"`)
are plain strings and lack this method. `py_compile` does NOT catch this -- it only
surfaces at render time as `AttributeError: 'str' object has no attribute 'interpolate'`.

**Fix:** Wrap hex strings in `ManimColor()`:
```python
# BAD: crashes at render time
color = interpolate_color(CHIP_BLUE, SUCCESS_GREEN, alpha)
Dot(color=interpolate_color(CHIP_BLUE, SUCCESS_GREEN, 0.5))

# GOOD: wrap in ManimColor()
color = interpolate_color(ManimColor(CHIP_BLUE), ManimColor(SUCCESS_GREEN), alpha)

# ALSO GOOD: define constants as ManimColor in style.py
CHIP_BLUE = ManimColor("#4A90D9")

# ALSO GOOD: use built-in Manim colors (already ManimColor objects)
color = interpolate_color(BLUE_C, GREEN_C, alpha)
```

This also applies to `average_color()` and any Manim utility that calls
`.interpolate()` internally. For Arrows specifically, avoid `interpolate_color`
entirely and use a plain color constant:
```python
# Arrow tip can also crash -- use plain color
Arrow(start, end, color=YELLOW)
```

### Brace.get_text() with font_size kwarg

**Cause:** `brace.get_text("label", font_size=24)` crashes because `font_size` is passed through to `next_to()` which does not accept it.

**Fix:** Create the Tex object separately and position it:
```python
# BAD
label = brace.get_text("label", font_size=24)

# GOOD
label = Tex(r"label", font_size=24)
brace.put_at_tip(label)
```

### MathTex with $...$ delimiters crashes

**Cause:** `MathTex` already wraps your string in `align*` math mode. Adding `$...$` creates double math mode, which LaTeX rejects.

```python
# BAD: crashes with "latex error converting to dvi"
MathTex(r"$E = mc^2$")

# GOOD: no dollar signs needed
MathTex(r"E = mc^2")

# If you need mixed text+math, use Tex (not MathTex):
Tex(r"Energy is $E = mc^2$")
```

### .animate added to VGroup crashes

**Cause:** `.animate` returns an `_AnimationBuilder`, not a VMobject. You cannot add it to a VGroup.

```python
# BAD: crashes with "Only values of type VMobject can be added as submobjects"
group = VGroup()
for obj in objects:
    group.add(obj.animate.move_to(ORIGIN))

# GOOD: use .animate only inside self.play()
self.play(*[obj.animate.move_to(ORIGIN) for obj in objects])

# GOOD: if you need target positions, create copies
targets = VGroup(*[obj.copy().move_to(ORIGIN) for obj in objects])
```

**Lint check:** After generating scene code, grep for `\.add\(.*\.animate` to catch this pattern before rendering.

## Silent bugs (no crash, wrong output)

These are worse than crashes because you don't notice until you watch the video.

### .animate chain order matters

`mob.animate.shift(RIGHT).scale(2)` and `mob.animate.scale(2).shift(RIGHT)` produce different results. Scale changes the coordinate system, so shift distances change after scaling. Apply transforms in the order you'd do them mentally.

### Transform chains leave ghost objects

```python
self.play(Transform(a, b))   # a looks like b, but a is still the scene object
self.play(Transform(a, c))   # a looks like c now. b and c were never added!
# If you later try self.play(b.animate.shift(UP)) -- nothing happens.
```

**Fix:** Use `ReplacementTransform` for each step, or use `TransformMatchingTex` for equations.

### Updaters freeze during self.wait()

By default `self.wait()` uses `frozen_frame=True` for performance. Updaters do NOT run. The animation looks frozen.

```python
# BAD: updater stops during wait
self.wait(3)

# GOOD: updater keeps running
self.wait(3, frozen_frame=False)
```

### copy vs reference

```python
reference = original      # same object! modifying one modifies both
copy = original.copy()    # independent. modifying copy leaves original alone
```

Always use `.copy()` when you need a separate instance.

### get_part_by_tex returns None silently

If the substring doesn't exist, `get_part_by_tex()` returns `None` instead of raising an error. If you chain `.set_color()` on it, you get `AttributeError: 'NoneType'`.

```python
# BAD: crashes later if "z" isn't in the equation
eq.get_part_by_tex("z").set_color(RED)

# GOOD: check first
part = eq.get_part_by_tex("z")
if part is not None:
    part.set_color(RED)
```

### Long text overflows screen silently

Manim does not wrap text. A long `Text(...)` or `MathTex(...)` simply extends off-screen. You must set `font_size` small enough or manually break lines with `\n`.

## Rendering issues

### Video is black / nothing appears

**Cause 1:** You forgot `self.add()` or `self.play()` - objects were created but never added to the scene.

**Cause 2:** Objects are positioned off-screen. The visible area is roughly x: [-7, 7], y: [-4, 4]. Check positions with `print(mob.get_center())`.

**Cause 3:** Fill opacity is 0 and stroke width is 0. The object exists but is invisible.

### Render is extremely slow

**Use low quality during development:**
```bash
manim -pql scene.py MyScene    # 480p, 15fps - very fast
```

**Only render the scene you're working on** - don't use `-a` (all scenes) during development.

**Reduce resolution of 3D surfaces:**
```python
# Slow
Surface(func, resolution=(64, 64))

# Fast for development
Surface(func, resolution=(16, 16))
```

### Transparent background not working

**mp4 does NOT support alpha channels.** Use webm:
```bash
manim -qh --format webm -t scene.py MyScene
```

### Output file location

Manim writes to `media/` in the current directory:
```
media/videos/{filename}/{quality}/SceneName.mp4
```

Quality folder names: `480p15`, `720p30`, `1080p60`, `2160p60`

## 3D issues

### 2D text looks distorted in ThreeDScene

**Cause:** Text/equations are projected in 3D space and rotate with the camera.

**Fix:** Pin them to the screen:
```python
label = Text("Fixed label")
self.add_fixed_in_frame_mobjects(label)
label.to_corner(UL)
```

### Objects render in wrong order (back object covers front)

**Cause:** Cairo renderer sorts by z-index, not by z-coordinate in 3D.

**Fix:** Set z_index manually: `front_obj.set_z_index(1)`

Or use the OpenGL renderer which handles depth correctly:
```bash
manim --renderer opengl scene.py MyScene
```

## Performance tips

| Situation | Fast approach |
|---|---|
| Development iteration | `manim -pql` (480p, 15fps) |
| Testing one scene | Name the scene explicitly, don't use `-a` |
| 3D surfaces | Lower resolution during dev: `resolution=(16, 16)` |
| Many objects | Use `VGroup` and batch operations instead of individual animations |
| Long videos | Use `self.next_section()` to render sections independently |
| Final render | `manim -qh` (1080p) or `manim -qk` (4K) |

## Production Audit Failures

These 10 patterns recur across multi-scene builds. Each was found via frame-by-frame
audit and is now a mandatory check.

### Text centering with \n

**Bug:** `Text("Line one\nLine two").move_to(ORIGIN)` left-aligns lines within the bounding box.

**Fix:** Use `safe_multiline()` or build a VGroup of separate Text objects:
```python
# BAD
question = Text("Line one\nLine two")
question.move_to(ORIGIN)

# GOOD
question = safe_multiline("Line one", "Line two")
question.move_to(ORIGIN)
```

### next_to() overflow stacking

**Bug:** `tags.next_to(box, RIGHT)` when box is at x=3.5 pushes tags off-screen. Guard code that clamps x drops them ON TOP of the box.

**Fix:** Place auxiliary elements BELOW (DOWN) when the source is at |x| > 2.5:
```python
# BAD
label.next_to(edge_box, RIGHT, buff=0.4)

# GOOD
label.next_to(edge_box, DOWN, buff=0.3)
```

### Title dimmed, not removed

**Bug:** `title.animate.set_opacity(0.35)` leaves a ghost. New text then overlaps the faded title.

**Fix:** Always `FadeOut(title)` completely. Dimming is not lifecycle removal.

### Child covers labeled_box label

**Bug:** `child.move_to(box.get_center())` hides the label text inside a labeled_box.

**Fix:** Offset children downward: `child.move_to(box.get_center() + DOWN * 0.3)`.

### Scale truncates labels

**Bug:** Scaling boxes for split-view makes "Instruction Cache" become "Instr".

**Fix:** Use short labels for reduced-size layouts: `labeled_box("I-Cache", width=2.0)`.

### Dim opacity bleeds under overlay text

**Bug:** Pipeline at DIM_OPACITY=0.1 still visible through white text overlay on dark backgrounds.

**Fix:** `FadeOut(pipeline)` completely when text needs a clean background. Only dim when the dimmed element stays BESIDE new content, never UNDER it.

### Empty transition frames

**Bug:** Between phases, only the title visible with 80% empty screen.

**Fix:** Combine FadeOut and Write in the same `self.play()` call:
```python
# BAD
self.play(FadeOut(*phase1))
self.play(Write(new_title))

# GOOD
self.play(FadeOut(*phase1), Write(new_title))
```

### Arrow tip crowding

**Bug:** Arrow between adjacent boxes has tip overlapping box label.

**Fix:** Use `buff=0.25` minimum. For boxes less than 1.5 units apart, use `buff=0.3` or set `max_tip_length_to_length_ratio=0.15`.

### Write() on bottom notes

**Bug:** `Write(note)` creates garbled partial-stroke frames at small font sizes.

**Fix:** Use `FadeIn(note, shift=UP * 0.2)` for all bottom notes.

### Chart legend overlap

**Bug:** Legend placed in upper-left where curves converge.

**Fix:** Place the legend in the corner with LEAST data density. For rising curves, use lower-right. For falling curves, use upper-right.

## Agent Code Generation Errors

These bugs come from parallel agent scene generation and are not caught by `py_compile`.

### .animate added to VGroup (silent dead code)

**Bug:** Agent writes `group.add(obj.animate.move_to(ORIGIN))`. `.animate` returns an `_AnimationBuilder`, not a VMobject. The line silently does nothing useful.

**Fix:** Only use `.animate` inside `self.play()`. After generation, grep for `\.add\(.*\.animate` as a lint check.

### manim not in PATH

**Bug:** `render_all.sh` fails with "manim: command not found" because pip installed it to a venv not on the user's PATH.

**Fix:** Verify with `which manim` before creating render scripts. Use `python3 -m manim` as a fallback in scripts:
```bash
MANIM_CMD="${MANIM_CMD:-$(command -v manim || echo 'python3 -m manim')}"
$MANIM_CMD -ql "$FILE" "$CLASS"
```

### ffmpeg concat needs absolute paths

**Bug:** `ffmpeg -f concat` with relative paths resolves them relative to the list file location, not the working directory.

**Fix:** Always use absolute paths in ffmpeg concat file lists:
```bash
# Generate list with absolute paths
for f in media/videos/*/1080p60/*.mp4; do
    echo "file '$(realpath "$f")'"
done > /tmp/concat_list.txt
ffmpeg -f concat -safe 0 -i /tmp/concat_list.txt -c copy output.mp4
```
