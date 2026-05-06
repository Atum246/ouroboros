"""
Shape Layers — Geometric shapes with fills, strokes, and animations.

Supports: Circle, Rectangle, Triangle, Line, Polygon, Ellipse, Star, Arc, Path
"""

import math
from typing import Any, Dict, Optional, Tuple, List
from PIL import Image, ImageDraw

from ouroboros.layers.base import Layer


def _parse_color(color: Any) -> Tuple[int, int, int, int]:
    """Parse color to RGBA."""
    if isinstance(color, str):
        color = color.lstrip("#")
        if len(color) == 6:
            return (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16), 255)
        elif len(color) == 8:
            return (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16), int(color[6:8], 16))
    elif isinstance(color, (tuple, list)):
        if len(color) == 3:
            return (color[0], color[1], color[2], 255)
        elif len(color) == 4:
            return tuple(color)
    return (255, 255, 255, 255)


class Circle(Layer):
    """
    Circle shape layer.

    Args:
        radius: Circle radius
        fill: Fill color
        stroke_width: Stroke width
        stroke_color: Stroke color

    Example::

        ball = Circle(radius=50, fill="#ff0000", x=100, y=100)
        ball.animate("x", 100, 500, 0, 1, ease_in_out)
    """

    def __init__(
        self,
        radius: int = 50,
        fill: Any = "#ffffff",
        stroke_width: int = 0,
        stroke_color: Any = "#000000",
        **kwargs,
    ):
        kwargs.setdefault("width", radius * 2)
        kwargs.setdefault("height", radius * 2)
        super().__init__(**kwargs)
        self.radius = radius
        self.fill = fill
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color

    def _render_content(
        self, t, width, height, fps, frame_idx, props,
    ) -> Optional[Image.Image]:
        r = int(props.get("radius", self.radius))
        size = r * 2 + self.stroke_width * 2 + 4
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        offset = self.stroke_width + 2
        bbox = [offset, offset, offset + r * 2, offset + r * 2]

        fill = _parse_color(props.get("fill", self.fill))
        stroke = _parse_color(props.get("stroke_color", self.stroke_color))
        sw = int(props.get("stroke_width", self.stroke_width))

        draw.ellipse(bbox, fill=fill, outline=stroke if sw > 0 else None, width=sw)
        return img


class Rectangle(Layer):
    """
    Rectangle shape layer.

    Args:
        rect_width: Width
        rect_height: Height
        fill: Fill color
        stroke_width: Stroke width
        stroke_color: Stroke color
        corner_radius: Corner radius for rounded rectangles

    Example::

        box = Rectangle(rect_width=200, rect_height=100, fill="#333333", corner_radius=10)
    """

    def __init__(
        self,
        rect_width: int = 100,
        rect_height: int = 100,
        fill: Any = "#ffffff",
        stroke_width: int = 0,
        stroke_color: Any = "#000000",
        corner_radius: int = 0,
        **kwargs,
    ):
        kwargs.setdefault("width", rect_width)
        kwargs.setdefault("height", rect_height)
        super().__init__(**kwargs)
        self.rect_width = rect_width
        self.rect_height = rect_height
        self.fill = fill
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color
        self.corner_radius = corner_radius

    def _render_content(
        self, t, width, height, fps, frame_idx, props,
    ) -> Optional[Image.Image]:
        w = int(props.get("rect_width", self.rect_width))
        h = int(props.get("rect_height", self.rect_height))
        sw = int(props.get("stroke_width", self.stroke_width))
        cr = int(props.get("corner_radius", self.corner_radius))

        size_w = w + sw * 2 + 4
        size_h = h + sw * 2 + 4
        img = Image.new("RGBA", (size_w, size_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        offset = sw + 2
        bbox = [offset, offset, offset + w, offset + h]

        fill = _parse_color(props.get("fill", self.fill))
        stroke = _parse_color(props.get("stroke_color", self.stroke_color))

        if cr > 0:
            draw.rounded_rectangle(bbox, radius=cr, fill=fill, outline=stroke if sw > 0 else None, width=sw)
        else:
            draw.rectangle(bbox, fill=fill, outline=stroke if sw > 0 else None, width=sw)

        return img


class Triangle(Layer):
    """Triangle shape layer."""

    def __init__(
        self,
        size: int = 100,
        fill: Any = "#ffffff",
        stroke_width: int = 0,
        stroke_color: Any = "#000000",
        **kwargs,
    ):
        kwargs.setdefault("width", size)
        kwargs.setdefault("height", size)
        super().__init__(**kwargs)
        self.size = size
        self.fill = fill
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color

    def _render_content(
        self, t, width, height, fps, frame_idx, props,
    ) -> Optional[Image.Image]:
        s = int(props.get("size", self.size))
        sw = int(props.get("stroke_width", self.stroke_width))

        img = Image.new("RGBA", (s + sw * 2 + 4, s + sw * 2 + 4), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        offset = sw + 2
        points = [
            (offset + s // 2, offset),
            (offset + s, offset + s),
            (offset, offset + s),
        ]

        fill = _parse_color(props.get("fill", self.fill))
        stroke = _parse_color(props.get("stroke_color", self.stroke_color))

        draw.polygon(points, fill=fill, outline=stroke if sw > 0 else None)
        return img


class Line(Layer):
    """Line shape layer."""

    def __init__(
        self,
        x2: int = 100,
        y2: int = 100,
        stroke_width: int = 2,
        stroke_color: Any = "#ffffff",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.x2 = x2
        self.y2 = y2
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color

    def _render_content(
        self, t, width, height, fps, frame_idx, props,
    ) -> Optional[Image.Image]:
        x2 = int(props.get("x2", self.x2))
        y2 = int(props.get("y2", self.y2))
        sw = int(props.get("stroke_width", self.stroke_width))

        img_w = max(abs(x2), 1) + sw * 2 + 4
        img_h = max(abs(y2), 1) + sw * 2 + 4
        img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        offset = sw + 2
        stroke = _parse_color(props.get("stroke_color", self.stroke_color))

        draw.line(
            [(offset, offset), (offset + x2, offset + y2)],
            fill=stroke, width=sw,
        )
        return img


class Ellipse(Layer):
    """Ellipse shape layer."""

    def __init__(
        self,
        radius_x: int = 60,
        radius_y: int = 40,
        fill: Any = "#ffffff",
        stroke_width: int = 0,
        stroke_color: Any = "#000000",
        **kwargs,
    ):
        kwargs.setdefault("width", radius_x * 2)
        kwargs.setdefault("height", radius_y * 2)
        super().__init__(**kwargs)
        self.radius_x = radius_x
        self.radius_y = radius_y
        self.fill = fill
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color

    def _render_content(
        self, t, width, height, fps, frame_idx, props,
    ) -> Optional[Image.Image]:
        rx = int(props.get("radius_x", self.radius_x))
        ry = int(props.get("radius_y", self.radius_y))
        sw = int(props.get("stroke_width", self.stroke_width))

        img = Image.new("RGBA", (rx * 2 + sw * 2 + 4, ry * 2 + sw * 2 + 4), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        offset = sw + 2
        bbox = [offset, offset, offset + rx * 2, offset + ry * 2]

        fill = _parse_color(props.get("fill", self.fill))
        stroke = _parse_color(props.get("stroke_color", self.stroke_color))

        draw.ellipse(bbox, fill=fill, outline=stroke if sw > 0 else None, width=sw)
        return img


class Star(Layer):
    """Star shape layer."""

    def __init__(
        self,
        outer_radius: int = 50,
        inner_radius: int = 25,
        points: int = 5,
        fill: Any = "#ffffff",
        stroke_width: int = 0,
        stroke_color: Any = "#000000",
        **kwargs,
    ):
        kwargs.setdefault("width", outer_radius * 2)
        kwargs.setdefault("height", outer_radius * 2)
        super().__init__(**kwargs)
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius
        self.points = points
        self.fill = fill
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color

    def _render_content(
        self, t, width, height, fps, frame_idx, props,
    ) -> Optional[Image.Image]:
        or_ = int(props.get("outer_radius", self.outer_radius))
        ir = int(props.get("inner_radius", self.inner_radius))
        n = int(props.get("points", self.points))
        sw = int(props.get("stroke_width", self.stroke_width))

        size = or_ * 2 + sw * 2 + 4
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        center = size // 2
        star_points = []
        for i in range(n * 2):
            angle = math.pi * i / n - math.pi / 2
            r = or_ if i % 2 == 0 else ir
            x = center + r * math.cos(angle)
            y = center + r * math.sin(angle)
            star_points.append((x, y))

        fill = _parse_color(props.get("fill", self.fill))
        stroke = _parse_color(props.get("stroke_color", self.stroke_color))

        draw.polygon(star_points, fill=fill, outline=stroke if sw > 0 else None)
        return img


class Arc(Layer):
    """Arc/sector shape layer."""

    def __init__(
        self,
        radius: int = 50,
        start_angle: float = 0,
        end_angle: float = 270,
        fill: Any = "#ffffff",
        stroke_width: int = 0,
        stroke_color: Any = "#000000",
        **kwargs,
    ):
        kwargs.setdefault("width", radius * 2)
        kwargs.setdefault("height", radius * 2)
        super().__init__(**kwargs)
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.fill = fill
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color

    def _render_content(
        self, t, width, height, fps, frame_idx, props,
    ) -> Optional[Image.Image]:
        r = int(props.get("radius", self.radius))
        start = float(props.get("start_angle", self.start_angle))
        end = float(props.get("end_angle", self.end_angle))
        sw = int(props.get("stroke_width", self.stroke_width))

        size = r * 2 + sw * 2 + 4
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        offset = sw + 2
        bbox = [offset, offset, offset + r * 2, offset + r * 2]

        fill = _parse_color(props.get("fill", self.fill))
        stroke = _parse_color(props.get("stroke_color", self.stroke_color))

        draw.arc(bbox, start, end, fill=fill, width=sw)
        return img


class Polygon(Layer):
    """Polygon shape layer with arbitrary points."""

    def __init__(
        self,
        points: List[Tuple[float, float]] = None,
        fill: Any = "#ffffff",
        stroke_width: int = 0,
        stroke_color: Any = "#000000",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.polygon_points = points or [(0, 0), (100, 0), (50, 100)]
        self.fill = fill
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color

    def _render_content(
        self, t, width, height, fps, frame_idx, props,
    ) -> Optional[Image.Image]:
        points = props.get("points", self.polygon_points)
        sw = int(props.get("stroke_width", self.stroke_width))

        max_x = max(p[0] for p in points) + sw * 2 + 4
        max_y = max(p[1] for p in points) + sw * 2 + 4

        img = Image.new("RGBA", (int(max_x), int(max_y)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        offset = sw + 2
        adjusted = [(offset + p[0], offset + p[1]) for p in points]

        fill = _parse_color(props.get("fill", self.fill))
        stroke = _parse_color(props.get("stroke_color", self.stroke_color))

        draw.polygon(adjusted, fill=fill, outline=stroke if sw > 0 else None)
        return img


class Path(Layer):
    """SVG-like path layer (simplified)."""

    def __init__(
        self,
        path_data: str = "",
        stroke_width: int = 2,
        stroke_color: Any = "#ffffff",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.path_data = path_data
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color

    def _render_content(
        self, t, width, height, fps, frame_idx, props,
    ) -> Optional[Image.Image]:
        # Simplified path rendering — draws line segments
        # Full SVG path parsing would be complex; this handles M/L/Z commands
        path = props.get("path_data", self.path_data)
        if not path:
            return None

        sw = int(props.get("stroke_width", self.stroke_width))
        stroke = _parse_color(props.get("stroke_color", self.stroke_color))

        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Parse simple path commands
        import re
        commands = re.findall(r'[MLZmlz]|[-+]?[0-9]*\.?[0-9]+', path)
        points = []
        current = (0, 0)

        i = 0
        while i < len(commands):
            cmd = commands[i]
            if cmd in ('M', 'm'):
                x = float(commands[i + 1])
                y = float(commands[i + 2])
                if cmd == 'm':
                    current = (current[0] + x, current[1] + y)
                else:
                    current = (x, y)
                points.append(current)
                i += 3
            elif cmd in ('L', 'l'):
                x = float(commands[i + 1])
                y = float(commands[i + 2])
                if cmd == 'l':
                    current = (current[0] + x, current[1] + y)
                else:
                    current = (x, y)
                points.append(current)
                i += 3
            elif cmd in ('Z', 'z'):
                if points:
                    points.append(points[0])
                i += 1
            else:
                i += 1

        if len(points) >= 2:
            draw.line(points, fill=stroke, width=sw)

        return img
