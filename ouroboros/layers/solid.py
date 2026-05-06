"""
Solid Layer — Fills with a solid color or gradient.

Supports solid colors, linear gradients, and radial gradients.
"""

from typing import Any, Dict, Optional, Tuple, List
from PIL import Image, ImageDraw
import math

from ouroboros.layers.base import Layer


class Solid(Layer):
    """
    Solid color/gradient background layer.

    Args:
        color: Fill color (hex string, RGB tuple, or RGBA tuple)
        gradient: Optional gradient spec [(stop, color), ...]
        gradient_type: 'linear' or 'radial'
        gradient_angle: Angle for linear gradients (degrees)
        gradient_center: Center for radial gradients (0-1, 0-1)

    Example::

        bg = Solid(color="#1a1a2e")
        gradient_bg = Solid(gradient=[(0, "#ff0000"), (1, "#0000ff")], gradient_angle=45)
    """

    def __init__(
        self,
        color: Any = "#000000",
        gradient: Optional[List[Tuple[float, Any]]] = None,
        gradient_type: str = "linear",
        gradient_angle: float = 0,
        gradient_center: Tuple[float, float] = (0.5, 0.5),
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.color = color
        self.gradient = gradient
        self.gradient_type = gradient_type
        self.gradient_angle = gradient_angle
        self.gradient_center = gradient_center

    def _parse_color(self, color: Any) -> Tuple[int, int, int, int]:
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
        return (0, 0, 0, 255)

    def _interpolate_color(
        self,
        c1: Tuple[int, int, int, int],
        c2: Tuple[int, int, int, int],
        t: float,
    ) -> Tuple[int, int, int, int]:
        """Interpolate between two RGBA colors."""
        return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

    def _render_gradient(
        self,
        width: int,
        height: int,
    ) -> Image.Image:
        """Render a gradient image."""
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        pixels = img.load()

        stops = sorted(self.gradient, key=lambda x: x[0])
        colors = [(stop, self._parse_color(color)) for stop, color in stops]

        for y in range(height):
            for x in range(width):
                if self.gradient_type == "linear":
                    # Calculate position along gradient angle
                    angle_rad = math.radians(self.gradient_angle)
                    # Normalize position to 0-1
                    if width > height:
                        pos = (x * math.cos(angle_rad) + y * math.sin(angle_rad)) / width
                    else:
                        pos = (x * math.cos(angle_rad) + y * math.sin(angle_rad)) / height
                    pos = max(0, min(1, pos))
                else:
                    # Radial gradient
                    cx = self.gradient_center[0] * width
                    cy = self.gradient_center[1] * height
                    max_dist = math.sqrt(cx ** 2 + cy ** 2)
                    dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                    pos = min(1, dist / max_dist)

                # Find surrounding stops
                color = colors[0][1]
                for i in range(len(colors) - 1):
                    if colors[i][0] <= pos <= colors[i + 1][0]:
                        local_t = (pos - colors[i][0]) / (colors[i + 1][0] - colors[i][0])
                        color = self._interpolate_color(colors[i][1], colors[i + 1][1], local_t)
                        break
                else:
                    color = colors[-1][1]

                pixels[x, y] = color

        return img

    def _render_content(
        self,
        t: float,
        width: int,
        height: int,
        fps: int,
        frame_idx: int,
        props: Dict[str, Any],
    ) -> Optional[Image.Image]:
        if self.gradient:
            return self._render_gradient(width, height)
        else:
            color = self._parse_color(props.get("color", self.color))
            return Image.new("RGBA", (width, height), color)
