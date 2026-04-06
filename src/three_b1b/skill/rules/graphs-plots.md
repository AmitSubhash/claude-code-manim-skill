---
name: Graphs and Plots
description: Axes, function plotting, parametric curves, bar charts, and data visualization in Manim
tags: [manim, plotting, axes, graphs, data-visualization, parametric]
---

# Graphs, Plots, and Data Visualization

## Conceptual Overview

What are Axes in Manim? Axes are a coordinate system that maps your data values to screen positions. Without Axes, you'd have to manually convert every data point (like x=3.5) to a screen position (like 2.1 units right of center). Axes handle this conversion via `coords_to_point` (`c2p`). They also draw tick marks, labels, and gridlines. NumberPlane adds a background grid for visualizing transformations.

Key idea: Axes define a mapping between "data space" (your function's x/y values) and "scene space" (Manim's coordinate system). Every plotting method -- `axes.plot()`, `axes.get_area()`, `axes.get_vertical_line()` -- uses this mapping internally. When you place a Dot at `axes.c2p(2, 3)`, you're saying "put this dot where x=2, y=3 in my data."

## Axes

```python
from manim import *

axes = Axes(
    x_range=[-3, 3, 1],       # [min, max, step]
    y_range=[-2, 2, 0.5],
    x_length=8,                # screen units
    y_length=5,
    axis_config={
        "include_numbers": True,
        "include_tip": True,
        "tip_width": 0.2,
        "tip_height": 0.2,
        "font_size": 24,
    },
    tips=True,
)
```

### Axis labels

```python
x_label = axes.get_x_axis_label(r"x", direction=DOWN)
y_label = axes.get_y_axis_label(r"f(x)", direction=LEFT)
self.play(Create(axes), Write(x_label), Write(y_label))
```

## NumberPlane

Coordinate grid with background lines:

```python
plane = NumberPlane(
    x_range=[-5, 5, 1],
    y_range=[-3, 3, 1],
    background_line_style={
        "stroke_color": BLUE_D,
        "stroke_width": 1,
        "stroke_opacity": 0.5,
    },
)
```

## Plotting Functions

### axes.plot

```python
graph = axes.plot(
    lambda x: np.sin(x),
    x_range=[-PI, PI],
    color=BLUE,
    use_smoothing=True,     # bezier smoothing (default True)
)
self.play(Create(graph))
```

### FunctionGraph (standalone, no axes)

```python
graph = FunctionGraph(
    lambda x: x**2,
    x_range=[-3, 3],
    color=RED,
)
```

### Parametric curves

```python
# On axes
curve = axes.plot_parametric_curve(
    lambda t: np.array([np.cos(t), np.sin(t), 0]),
    t_range=[0, TAU],
    color=GREEN,
)

# Standalone
curve = ParametricFunction(
    lambda t: np.array([np.cos(t), np.sin(t), 0]),
    t_range=[0, TAU],
    color=YELLOW,
)
```

## Coordinate Conversion

```python
# Scene point from data coordinates
point = axes.coords_to_point(2, 3)    # or axes.c2p(2, 3)

# Data coordinates from scene point
x, y = axes.point_to_coords(point)    # or axes.p2c(point)

# Place a dot at data coordinates
dot = Dot(axes.c2p(1, 1), color=RED)
```

## Graph Labels

```python
graph = axes.plot(lambda x: x**2, color=BLUE)

label = axes.get_graph_label(
    graph,
    label=MathTex(r"x^2"),
    x_val=2,
    direction=UR,
    buff=0.2,
)
self.play(Create(graph), Write(label))
```

## Lines and Areas

### Vertical and horizontal lines

```python
# Vertical line from x-axis to graph at x=2
v_line = axes.get_vertical_line(
    axes.c2p(2, 4),   # point on graph
    color=YELLOW,
    line_func=DashedLine,
)

# Horizontal line
h_line = axes.get_horizontal_line(
    axes.c2p(2, 4),
    color=YELLOW,
)
```

### Shaded area under curve

```python
graph = axes.plot(lambda x: x**2, x_range=[0, 3], color=BLUE)

area = axes.get_area(
    graph,
    x_range=[0, 2],
    color=[BLUE, GREEN],   # gradient
    opacity=0.5,
)
self.play(Create(graph), FadeIn(area))
```

## Animated Graph Tracing

Draw the graph progressively:

```python
graph = axes.plot(lambda x: np.sin(x), x_range=[0, 2 * PI], color=BLUE)
self.play(Create(graph), rate_func=linear, run_time=3)
```

### Tracing dot

```python
t = ValueTracker(0)
dot = always_redraw(
    lambda: Dot(
        axes.c2p(t.get_value(), np.sin(t.get_value())),
        color=RED,
    )
)
self.add(dot)
self.play(t.animate.set_value(2 * PI), run_time=4, rate_func=linear)
```

## Tangent Line / Secant Slope Group

```python
graph = axes.plot(lambda x: x**2, color=BLUE)

secant = axes.get_secant_slope_group(
    x=1,
    graph=graph,
    dx=0.01,
    secant_line_color=YELLOW,
    secant_line_length=4,
)
self.play(Create(secant))
```

## NumberLine

```python
number_line = NumberLine(
    x_range=[-5, 5, 1],
    length=10,
    include_numbers=True,
    include_tip=True,
    font_size=20,
)

# Add a labeled point
dot = Dot(number_line.n2p(3), color=RED)
label = MathTex("3").next_to(dot, UP)
```

## BarChart

```python
chart = BarChart(
    values=[4, 6, 2, 8, 5],
    bar_names=["A", "B", "C", "D", "E"],
    y_range=[0, 10, 2],
    y_length=5,
    x_length=8,
    bar_colors=[RED, BLUE, GREEN, YELLOW, PURPLE],
    bar_width=0.6,
)
self.play(Create(chart))

# Animate changing values
self.play(chart.animate.change_bar_values([2, 8, 4, 3, 7]))
```

## ThreeDAxes

```python
axes_3d = ThreeDAxes(
    x_range=[-3, 3, 1],
    y_range=[-3, 3, 1],
    z_range=[-2, 2, 1],
    x_length=6,
    y_length=6,
    z_length=4,
)
```

## Common Patterns

### Multiple functions on same axes

```python
axes = Axes(x_range=[-3, 3], y_range=[-2, 4])
g1 = axes.plot(lambda x: x**2, color=BLUE)
g2 = axes.plot(lambda x: x**3, color=RED)
g3 = axes.plot(lambda x: np.exp(x), color=GREEN, x_range=[-3, 1.5])

l1 = axes.get_graph_label(g1, r"x^2", x_val=1.5)
l2 = axes.get_graph_label(g2, r"x^3", x_val=1.2)
l3 = axes.get_graph_label(g3, r"e^x", x_val=1.2)

self.play(Create(axes))
self.play(Create(g1), Write(l1))
self.play(Create(g2), Write(l2))
self.play(Create(g3), Write(l3))
```

### Animated area that changes

```python
t = ValueTracker(0.5)

area = always_redraw(
    lambda: axes.get_area(
        graph,
        x_range=[0, t.get_value()],
        color=BLUE,
        opacity=0.4,
    )
)
self.add(area)
self.play(t.animate.set_value(3), run_time=3)
```

### Probability distribution

```python
axes = Axes(x_range=[-4, 4, 1], y_range=[0, 0.5, 0.1], axis_config={"include_numbers": True})
gaussian = lambda x: np.exp(-x**2 / 2) / np.sqrt(2 * np.pi)
curve = axes.plot(gaussian, color=BLUE)
area = axes.get_area(curve, x_range=[-1, 1], color=BLUE, opacity=0.3)
label = axes.get_graph_label(curve, r"\mathcal{N}(0,1)")
self.play(Create(axes), Create(curve), Write(label))
self.play(FadeIn(area))
```

## Graph Theory

Manim provides `Graph` and `DiGraph` mobjects for network visualization. These are distinct from function-plotting graphs. They represent nodes (vertices) and connections (edges) and support automatic layout algorithms.

### Basic Graph

```python
from manim import *

class SimpleGraph(Scene):
    def construct(self) -> None:
        vertices = [1, 2, 3, 4, 5]
        edges = [(1, 2), (1, 3), (2, 4), (3, 4), (4, 5)]

        g = Graph(
            vertices, edges,
            layout="spring",
            vertex_config={"radius": 0.2, "fill_color": BLUE},
            edge_config={"stroke_color": GRAY, "stroke_width": 2},
        )
        self.play(Create(g))
        self.wait(1)
```

### Directed Graph (DiGraph)

```python
class DirectedGraph(Scene):
    def construct(self) -> None:
        vertices = ["Q", "K", "V", "Attn", "Out"]
        edges = [("Q", "Attn"), ("K", "Attn"), ("V", "Attn"), ("Attn", "Out")]

        dg = DiGraph(
            vertices, edges,
            layout="tree",
            root_vertex="Out",
            vertex_config={"radius": 0.25, "fill_color": BLUE_D},
            edge_config={"stroke_color": WHITE, "tip_config": {"tip_length": 0.15}},
        )
        self.play(Create(dg))
        self.wait(1)
```

### Layout Algorithms

| Layout | Best for | Notes |
|--------|----------|-------|
| `"spring"` | General networks | Force-directed, good default |
| `"circular"` | Cycle graphs, ring topologies | Vertices on a circle |
| `"kamada_kawai"` | Small-medium graphs | Energy-minimized, often cleaner than spring |
| `"tree"` | Hierarchies, DAGs | Requires `root_vertex` parameter |
| `"partite"` | Bipartite/multipartite graphs | Requires `partitions` parameter |
| `"planar"` | Planar graphs | No edge crossings if graph is planar |
| `"shell"` | Concentric rings | Vertices arranged in shells |
| `"spectral"` | Graphs with community structure | Uses eigenvectors of adjacency matrix |
| Custom dict | Precise control | `layout={1: LEFT*2, 2: RIGHT*2, ...}` |

### Custom Vertex Mobjects

Replace default dots with any mobject using `vertex_type` or a label dictionary:

```python
class LabeledGraph(Scene):
    def construct(self) -> None:
        vertices = ["Encoder", "Attention", "FFN", "Decoder"]
        edges = [("Encoder", "Attention"), ("Attention", "FFN"), ("FFN", "Decoder")]

        # Custom labels via vertex_type factory
        def make_vertex(v):
            label = Text(str(v), font_size=16, color=WHITE)
            rect = Rectangle(
                width=label.width + 0.4, height=0.5,
                fill_color=BLUE_E, fill_opacity=0.8,
                stroke_color=BLUE_A,
            )
            return VGroup(rect, label)

        g = DiGraph(
            vertices, edges,
            layout="tree",
            root_vertex="Decoder",
            vertex_type=make_vertex,
            edge_config={"stroke_color": GRAY_A, "tip_config": {"tip_length": 0.15}},
        )
        self.play(Create(g))
        self.wait(1)
```

### Edge Styling

```python
# Per-edge configuration
edge_config = {
    ("A", "B"): {"stroke_color": RED, "stroke_width": 3},
    ("B", "C"): {"stroke_color": BLUE, "stroke_width": 1},
    "default": {"stroke_color": GRAY, "stroke_width": 2},
}

g = Graph(vertices, edges, edge_config=edge_config)
```

### Animated Graph Changes

```python
class GraphAnimation(Scene):
    def construct(self) -> None:
        vertices = [1, 2, 3, 4]
        edges = [(1, 2), (2, 3), (3, 4)]

        g = Graph(vertices, edges, layout="circular")
        self.play(Create(g))
        self.wait(0.5)

        # Change layout with animation
        self.play(g.animate.change_layout("spring"))
        self.wait(0.5)

        # Add vertices and edges
        g.add_vertices(5, positions={5: RIGHT * 2})
        g.add_edges((4, 5))
        self.play(Create(g))
        self.wait(1)
```

### Knowledge Graph Example

A complete example showing a labeled directed graph with semantic coloring:

```python
class KnowledgeGraph(Scene):
    """Directed knowledge graph with labeled nodes and typed edges."""

    def construct(self) -> None:
        # Define the graph structure
        vertices = ["Transformer", "Attention", "FFN", "Encoder", "Decoder", "Embeddings"]
        edges = [
            ("Transformer", "Encoder"),
            ("Transformer", "Decoder"),
            ("Encoder", "Attention"),
            ("Encoder", "FFN"),
            ("Decoder", "Attention"),
            ("Decoder", "FFN"),
            ("Embeddings", "Encoder"),
            ("Embeddings", "Decoder"),
        ]

        # Color by node type
        node_colors = {
            "Transformer": YELLOW,
            "Encoder": BLUE,
            "Decoder": GREEN,
            "Attention": RED,
            "FFN": ORANGE,
            "Embeddings": PURPLE,
        }

        def make_node(name):
            label = Text(name, font_size=14, color=WHITE)
            circle = Circle(
                radius=max(label.width / 2 + 0.15, 0.35),
                fill_color=node_colors.get(name, GRAY),
                fill_opacity=0.3,
                stroke_color=node_colors.get(name, GRAY),
            )
            return VGroup(circle, label)

        g = DiGraph(
            vertices, edges,
            layout="kamada_kawai",
            vertex_type=make_node,
            edge_config={
                "stroke_color": GRAY_A,
                "stroke_width": 1.5,
                "tip_config": {"tip_length": 0.12, "tip_width": 0.08},
            },
        ).scale(1.2)

        # Animate: nodes first, then edges
        self.play(
            LaggedStart(*[FadeIn(g[v], scale=0.5) for v in vertices], lag_ratio=0.15),
            run_time=2,
        )
        self.play(
            LaggedStart(*[Create(g.edges[e]) for e in edges], lag_ratio=0.1),
            run_time=2,
        )
        self.wait(2)
```
