"""
Text Layer — Rich text rendering with animations.

Supports fonts, colors, strokes, shadows, and text-specific animations.
"""

import os
import math
from typing import Any, Dict, Optional, Tuple, List
from PIL import Image, ImageDraw, ImageFont

from ouroboros.layers.base import Layer
from ouroboros.animation.easing import linear, EasingFunc


# Default font paths by OS
_FONT_SEARCH_PATHS = [
    "/usr/share/fonts",
    "/usr/local/share/fonts",
    "/System/Library/Fonts",
    "C:\\Windows\\Fonts",
    os.path.expanduser("~/.fonts"),
    os.path.expanduser("~/Library/Fonts"),
]

_font_cache: Dict[str, ImageFont.FreeTypeFont] = {}


def _find_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    """Find and cache a font by name."""
    cache_key = f"{name}:{size}"
    if cache_key in _font_cache:
        return _font_cache[cache_key]

    # Try direct load (absolute path or system font)
    try:
        font = ImageFont.truetype(name, size)
        _font_cache[cache_key] = font
        return font
    except (OSError, IOError):
        pass

    # Search common font directories
    for search_path in _FONT_SEARCH_PATHS:
        if not os.path.exists(search_path):
            continue
        for root, dirs, files in os.walk(search_path):
            for f in files:
                if f.lower().endswith((".ttf", ".otf")):
                    if name.lower() in f.lower():
                        try:
                            font_path = os.path.join(root, f)
                            font = ImageFont.truetype(font_path, size)
                            _font_cache[cache_key] = font
                            return font
                        except (OSError, IOError):
                            continue

    # Fallback to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
        _font_cache[cache_key] = font
        return font
    except (OSError, IOError):
        return ImageFont.load_default()


class Text(Layer):
    """
    Text layer with rich formatting and animation.

    Args:
        text: Text content
        font_size: Font size in pixels
        font: Font name or path
        color: Text color (hex, RGB, RGBA)
        bold: Bold text
        italic: Italic text
        align: Text alignment (left, center, right)
        line_spacing: Line spacing multiplier
        stroke_width: Text stroke/outline width
        stroke_color: Stroke color
        shadow_x: Shadow X offset
        shadow_y: Shadow Y offset
        shadow_color: Shadow color
        shadow_blur: Shadow blur radius
        gradient_text: Gradient fill for text [(stop, color), ...]
        word_wrap: Enable word wrapping
        max_width: Maximum width for word wrapping

    Example::

        title = Text("Hello World", font_size=120, color="#e94560")
        title.animate("opacity", 0, 1, 0, 0.5, ease_in_out)
        title.animate("y", 600, 500, 0, 1, ease_in_out)

        styled = Text(
            "Fancy Text",
            font_size=80,
            color="#ffffff",
            stroke_width=3,
            stroke_color="#000000",
            shadow_x=4, shadow_y=4,
            shadow_color="#000000",
        )
    """

    def __init__(
        self,
        text: str = "",
        font_size: int = 48,
        font: str = "default",
        color: Any = "#ffffff",
        bold: bool = False,
        italic: bool = False,
        align: str = "left",
        line_spacing: float = 1.2,
        stroke_width: int = 0,
        stroke_color: Any = "#000000",
        shadow_x: int = 0,
        shadow_y: int = 0,
        shadow_color: Any = "#000000",
        shadow_blur: int = 0,
        gradient_text: Optional[List[Tuple[float, Any]]] = None,
        word_wrap: bool = False,
        max_width: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = font_size
        self.font = font
        self.color = color
        self.bold = bold
        self.italic = italic
        self.align = align
        self.line_spacing = line_spacing
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color
        self.shadow_x = shadow_x
        self.shadow_y = shadow_y
        self.shadow_color = shadow_color
        self.shadow_blur = shadow_blur
        self.gradient_text = gradient_text
        self.word_wrap = word_wrap
        self.max_width = max_width

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
        return (255, 255, 255, 255)

    def _get_font(self, size: Optional[int] = None) -> ImageFont.FreeTypeFont:
        """Get the font for rendering."""
        font_name = self.font
        if self.bold and self.italic:
            font_name = font_name.replace("Regular", "BoldItalic")
        elif self.bold:
            font_name = font_name.replace("Regular", "Bold")
        elif self.italic:
            font_name = font_name.replace("Regular", "Italic")

        return _find_font(font_name, size or self.font_size)

    def _render_text(
        self,
        text: str,
        font: ImageFont.FreeTypeFont,
        color: Tuple[int, int, int, int],
        stroke_width: int = 0,
        stroke_color: Tuple[int, int, int, int] = (0, 0, 0, 255),
    ) -> Image.Image:
        """Render text to an image."""
        # Measure text
        dummy = Image.new("RGBA", (1, 1))
        draw = ImageDraw.Draw(dummy)

        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0] + stroke_width * 2 + abs(self.shadow_x)
        text_h = bbox[3] - bbox[1] + stroke_width * 2 + abs(self.shadow_y)

        # Create image
        img = Image.new("RGBA", (text_w + 20, text_h + 20), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw shadow
        if self.shadow_x != 0 or self.shadow_y != 0:
            shadow_pos = (10 + self.shadow_x, 10 + self.shadow_y)
            draw.text(
                shadow_pos, text, font=font, fill=self._parse_color(self.shadow_color),
                stroke_width=stroke_width, stroke_fill=self._parse_color(stroke_color),
            )

        # Draw main text
        draw.text(
            (10, 10), text, font=font, fill=color,
            stroke_width=stroke_width, stroke_fill=stroke_color,
        )

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
        text = props.get("text", self.text)
        if not text:
            return None

        # Handle typewriter effect via text_progress
        text_progress = props.get("text_progress", 1.0)
        if text_progress < 1.0:
            char_count = max(1, int(len(text) * text_progress))
            text = text[:char_count]

        font_size = int(props.get("font_size", self.font_size))
        font = self._get_font(font_size)
        color = self._parse_color(props.get("color", self.color))
        stroke_width = int(props.get("stroke_width", self.stroke_width))
        stroke_color = self._parse_color(props.get("stroke_color", self.stroke_color))

        return self._render_text(text, font, color, stroke_width, stroke_color)
