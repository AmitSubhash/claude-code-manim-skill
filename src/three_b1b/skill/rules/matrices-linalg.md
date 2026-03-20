---
name: Matrices and Linear Algebra
description: Matrix display, linear transformations, eigenvectors, and vector space visualization in Manim
tags: [manim, matrix, linear-algebra, vectors, transformation]
---

# Matrices and Linear Algebra Visualization

**What is Matrix in Manim?** Matrix is a Mobject that displays a 2D array of values
with brackets, just like you'd write on a whiteboard. **Why it exists:** matrices are
central to linear algebra, and Manim's Matrix lets you access individual entries, rows,
and columns as separate Mobjects so you can color, highlight, and animate them
independently. This is critical for showing matrix operations step by step -- you can
highlight the row being multiplied, color the pivot element, or animate one column
sliding to a new position. Manim also provides `LinearTransformationScene` for
visualizing how a matrix maps the entire plane, complete with grid deformation and
ghost vectors showing before/after.

## Matrix Display

### Basic Matrix

```python
from manim import *

mat = Matrix(
    [[1, 2],
     [3, 4]],
    left_bracket="(",     # or "[", "\\{"
    right_bracket=")",
    v_buff=0.8,           # vertical spacing between rows
    h_buff=1.0,           # horizontal spacing between columns
)
self.play(Write(mat))
```

### Typed Matrix Variants

```python
# Integer-only (no decimals)
int_mat = IntegerMatrix([[1, 0], [0, 1]])

# Decimal display
dec_mat = DecimalMatrix(
    [[1.5, 2.3], [0.1, 4.7]],
    num_decimal_places=1,
)

# Arbitrary mobjects as entries
mob_mat = MobjectMatrix([
    [MathTex("a"), MathTex("b")],
    [MathTex("c"), MathTex("d")],
])
```

## Accessing Matrix Parts

```python
mat = Matrix([[1, 2, 3], [4, 5, 6]])

# Get columns as VGroups
cols = mat.get_columns()   # list of VGroups
col0 = cols[0]             # first column entries

# Get rows as VGroups
rows = mat.get_rows()
row1 = rows[1]             # second row entries

# Get all entries as a flat VGroup
entries = mat.get_entries()
entries[0]  # top-left entry ("1")

# Get brackets
left_bracket, right_bracket = mat.get_brackets()
```

## Column and Row Coloring

```python
mat = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# Color each column differently
mat.set_column_colors(RED, GREEN, BLUE)

# Color each row differently
mat.set_row_colors(RED, GREEN, BLUE)

# Color a specific entry
mat.get_entries()[4].set_color(YELLOW)  # entry at index 4 (row 1, col 1)
```

## Vectors as Arrows

```python
# 2D vector arrow
vec = Arrow(ORIGIN, [2, 1, 0], buff=0, color=YELLOW)
vec_label = MathTex(r"\vec{v}").next_to(vec.get_end(), UR, buff=0.1)

# Column vector notation
col_vec = Matrix([[2], [1]], left_bracket="[", right_bracket="]")
```

## LinearTransformationScene

A specialized scene for visualizing 2D linear transformations on the number plane:

```python
class LinearTransformExample(LinearTransformationScene):
    def __init__(self, **kwargs):
        super().__init__(
            show_coordinates=True,
            leave_ghost_vectors=True,  # show original vectors faintly
            **kwargs,
        )

    def construct(self) -> None:
        # Add basis vectors (automatically tracked)
        vec = self.add_vector([1, 2], color=YELLOW)

        # Apply a matrix transformation
        matrix = [[2, 1], [0, 1]]  # shear
        self.apply_matrix(matrix)
        self.wait()

        # Apply another transformation
        rotation = [[0, -1], [1, 0]]  # 90-degree rotation
        self.apply_matrix(rotation)
        self.wait()
```

## ApplyMatrix Animation

For transforming mobjects by a matrix without `LinearTransformationScene`:

```python
class MatrixApply(Scene):
    def construct(self) -> None:
        plane = NumberPlane()
        circle = Circle(radius=1, color=BLUE)

        self.add(plane, circle)

        # Shear transformation
        matrix = [[1, 0.5], [0, 1]]
        self.play(ApplyMatrix(matrix, plane), ApplyMatrix(matrix, circle))
```

## Matrix Multiplication Animation

```python
class MatMul(Scene):
    def construct(self) -> None:
        mat_a = Matrix([[1, 2], [3, 4]], left_bracket="[", right_bracket="]")
        times = MathTex(r"\times")
        mat_b = Matrix([[5, 6], [7, 8]], left_bracket="[", right_bracket="]")
        equals = MathTex(r"=")
        mat_c = Matrix([[19, 22], [43, 50]], left_bracket="[", right_bracket="]")

        equation = VGroup(mat_a, times, mat_b, equals, mat_c).arrange(RIGHT, buff=0.3)
        equation.scale(0.8)

        # Animate step by step
        self.play(Write(mat_a))
        self.play(Write(times), Write(mat_b))
        self.play(Write(equals))

        # Highlight the computation for entry (0,0): row 0 of A * col 0 of B
        row_0 = mat_a.get_rows()[0].copy().set_color(RED)
        col_0 = mat_b.get_columns()[0].copy().set_color(BLUE)
        result_entry = mat_c.get_entries()[0]

        self.play(Indicate(row_0), Indicate(col_0))

        # Show computation
        computation = MathTex(r"1 \cdot 5 + 2 \cdot 7 = 19", font_size=36)
        computation.next_to(equation, DOWN, buff=0.5)
        self.play(Write(computation))
        self.play(result_entry.animate.set_color(GREEN))
        self.wait()
        self.play(FadeOut(computation))

        # Reveal full result
        self.play(Write(mat_c))
```

## Eigenvector Visualization

```python
class EigenDemo(LinearTransformationScene):
    def __init__(self, **kwargs):
        super().__init__(show_coordinates=True, **kwargs)

    def construct(self) -> None:
        matrix = [[2, 1], [1, 2]]
        # Eigenvalues: 3, 1
        # Eigenvectors: [1,1], [-1,1]

        # Add eigenvectors
        ev1 = self.add_vector([1, 1], color=GREEN)
        ev2 = self.add_vector([-1, 1], color=RED)

        # Add non-eigenvector for comparison
        other = self.add_vector([1, 0], color=YELLOW)

        # Labels
        ev1_label = MathTex(r"\lambda_1 = 3", color=GREEN, font_size=28)
        ev1_label.add_updater(lambda l: l.next_to(ev1.get_end(), UR, buff=0.1))

        ev2_label = MathTex(r"\lambda_2 = 1", color=RED, font_size=28)
        ev2_label.add_updater(lambda l: l.next_to(ev2.get_end(), UL, buff=0.1))

        self.add(ev1_label, ev2_label)

        # Apply the transformation
        self.apply_matrix(matrix)
        self.wait(2)
```

## Determinant Visualization

```python
class DeterminantArea(Scene):
    def construct(self) -> None:
        plane = NumberPlane()
        self.add(plane)

        # Unit square
        square = Polygon(
            ORIGIN, RIGHT, RIGHT + UP, UP,
            fill_color=BLUE, fill_opacity=0.3, stroke_color=BLUE,
        )
        area_label = MathTex(r"\text{Area} = 1", font_size=32).move_to(square)
        self.play(Create(square), Write(area_label))

        # Apply matrix with det = 2
        matrix = [[2, 0], [1, 1]]
        det = 2 * 1 - 0 * 1  # = 2

        new_square = Polygon(
            ORIGIN,
            np.array([2, 1, 0]),
            np.array([2, 2, 0]),
            np.array([0, 1, 0]),
            fill_color=GREEN, fill_opacity=0.3, stroke_color=GREEN,
        )
        new_label = MathTex(
            rf"\text{{Area}} = |\det(A)| = {det}", font_size=32
        ).move_to(new_square)

        self.play(
            Transform(square, new_square),
            Transform(area_label, new_label),
        )
        self.wait()
```

## Matrix with Annotations

```python
class AnnotatedMatrix(Scene):
    def construct(self) -> None:
        mat = Matrix(
            [["a_{11}", "a_{12}"],
             ["a_{21}", "a_{22}"]],
        )
        self.play(Write(mat))

        # Brace for first column
        col_brace = Brace(mat.get_columns()[0], DOWN, color=RED)
        col_label = col_brace.get_tex(r"\vec{v}_1").set_color(RED)
        self.play(Create(col_brace), Write(col_label))

        # Highlight diagonal
        diag = VGroup(mat.get_entries()[0], mat.get_entries()[3])
        rect = SurroundingRectangle(diag, color=YELLOW, buff=0.1)
        self.play(Create(rect))
        self.wait()
```
