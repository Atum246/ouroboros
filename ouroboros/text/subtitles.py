"""
Subtitles — SRT file parsing and subtitle overlay.

Automatically loads and displays subtitles synced to video timing.
"""

import re
import os
from typing import List, Optional, Tuple, Any
from PIL import Image, ImageDraw, ImageFont

from ouroboros.layers.base import Layer
from ouroboros.layers.text_layer import _find_font


class SubtitleEntry:
    """A single subtitle entry."""

    def __init__(self, start: float, end: float, text: str):
        self.start = start
        self.end = end
        self.text = text

    @property
    def duration(self) -> float:
        return self.end - self.start

    def __repr__(self) -> str:
        return f"Subtitle({self.start:.1f}-{self.end:.1f}: '{self.text}')"


def parse_srt(filepath: str) -> List[SubtitleEntry]:
    """
    Parse an SRT subtitle file.

    Args:
        filepath: Path to .srt file

    Returns:
        List of SubtitleEntry objects
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    entries = []
    blocks = re.split(r"\n\s*\n", content.strip())

    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue

        # Parse timestamp line
        timestamp_line = lines[1]
        match = re.match(
            r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})",
            timestamp_line,
        )
        if not match:
            continue

        g = match.groups()
        start = int(g[0]) * 3600 + int(g[1]) * 60 + int(g[2]) + int(g[3]) / 1000
        end = int(g[4]) * 3600 + int(g[5]) * 60 + int(g[6]) + int(g[7]) / 1000
        text = "\n".join(lines[2:])

        entries.append(SubtitleEntry(start, end, text))

    return entries


class SubtitleTrack(Layer):
    """
    Subtitle overlay layer.

    Args:
        source: Path to SRT file or list of SubtitleEntry
        font_size: Font size
        font: Font name
        color: Text color
        stroke_width: Text stroke width
        stroke_color: Stroke color
        background_color: Background box color (None for transparent)
        position: Position ('bottom', 'top', 'center')
        margin: Margin from edge (pixels)

    Example::

        subs = SubtitleTrack("subtitles.srt", font_size=36, color="#ffffff")
        comp.add_scene(subs_scene)
    """

    def __init__(
        self,
        source: Any = None,
        font_size: int = 36,
        font: str = "default",
        color: Any = "#ffffff",
        stroke_width: int = 2,
        stroke_color: Any = "#000000",
        background_color: Any = None,
        position: str = "bottom",
        margin: int = 50,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.font_size = font_size
        self.font = font
        self.color = color
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color
        self.background_color = background_color
        self.position = position
        self.margin = margin

        self._entries: List[SubtitleEntry] = []
        if isinstance(source, str) and os.path.exists(source):
            self._entries = parse_srt(source)
        elif isinstance(source, list):
            self._entries = source

    def _parse_color(self, color: Any) -> Tuple[int, int, int, int]:
        if isinstance(color, str):
            color = color.lstrip("#")
            if len(color) == 6:
                return (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16), 255)
        elif isinstance(color, (tuple, list)):
            if len(color) == 3:
                return (color[0], color[1], color[2], 255)
            return tuple(color)
        return (255, 255, 255, 255)

    def _get_current_subtitle(self, t: float, duration: float) -> Optional[SubtitleEntry]:
        """Get the subtitle at normalized time t."""
        if not self._entries:
            return None

        time_seconds = t * duration
        for entry in self._entries:
            if entry.start <= time_seconds <= entry.end:
                return entry
        return None

    def _render_content(
        self, t, width, height, fps, frame_idx, props,
    ) -> Optional[Image.Image]:
        # Calculate actual time from composition duration
        # We need the composition duration, estimate from frame count
        duration = frame_to_time(frame_idx, fps) / t if t > 0 else 10
        time_seconds = t * duration

        # Find subtitle
        subtitle = None
        for entry in self._entries:
            if entry.start <= time_seconds <= entry.end:
                subtitle = entry
                break

        if not subtitle:
            return None

        # Render text
        font = _find_font(self.font, self.font_size)
        color = self._parse_color(self.color)
        stroke = self._parse_color(self.stroke_color)

        dummy = Image.new("RGBA", (1, 1))
        draw = ImageDraw.Draw(dummy)
        bbox = draw.textbbox((0, 0), subtitle.text, font=font)
        text_w = bbox[2] - bbox[0] + self.stroke_width * 2 + 20
        text_h = bbox[3] - bbox[1] + self.stroke_width * 2 + 20

        img = Image.new("RGBA", (width, text_h + 20), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Position
        x = (width - text_w) // 2
        y = 10

        # Background
        if self.background_color:
            bg_color = self._parse_color(self.background_color)
            draw.rectangle([x - 10, y - 5, x + text_w + 10, y + text_h + 5], fill=bg_color)

        # Text
        draw.text(
            (x + 10, y + 10), subtitle.text, font=font, fill=color,
            stroke_width=self.stroke_width, stroke_fill=stroke,
        )

        return img


def frame_to_time(frame: int, fps: int) -> float:
    """Convert frame number to time in seconds."""
    return frame / max(fps, 1)
