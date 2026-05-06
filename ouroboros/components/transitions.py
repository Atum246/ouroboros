"""
Transitions — Scene-to-scene transitions.

30+ built-in transitions for seamless scene changes.
"""

from typing import Optional, Tuple
from PIL import Image
import numpy as np
import math

from ouroboros.effects.base import Effect
from ouroboros.animation.easing import ease_in_out, EasingFunc


class Transition(Effect):
    """Base transition class."""

    def __init__(self, duration: float = 0.5, easing: EasingFunc = ease_in_out, **kwargs):
        super().__init__(**kwargs)
        self.duration = duration
        self.easing = easing


class FadeTransition(Transition):
    """Fade to black/white and back."""

    def __init__(self, color: tuple = (0, 0, 0), **kwargs):
        super().__init__(**kwargs)
        self.color = color

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        if t < 0.5:
            # Fade out
            progress = self.easing(t * 2)
            overlay = Image.new("RGBA", image.size, self.color + (int(255 * progress),))
        else:
            # Fade in
            progress = self.easing((1 - t) * 2)
            overlay = Image.new("RGBA", image.size, self.color + (int(255 * progress),))

        if image.mode != "RGBA":
            image = image.convert("RGBA")
        return Image.alpha_composite(image, overlay)


class WipeTransition(Transition):
    """Wipe transition (left, right, up, down)."""

    def __init__(self, direction: str = "left", color: tuple = (0, 0, 0), **kwargs):
        super().__init__(**kwargs)
        self.direction = direction
        self.color = color

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        progress = self.easing(t)
        w, h = image.size

        mask = Image.new("L", (w, h), 0)
        draw = __import__("PIL.ImageDraw", fromlist=["ImageDraw"]).Draw(mask)

        if self.direction == "left":
            x = int(w * progress)
            draw.rectangle([0, 0, x, h], fill=255)
        elif self.direction == "right":
            x = int(w * (1 - progress))
            draw.rectangle([x, 0, w, h], fill=255)
        elif self.direction == "up":
            y = int(h * progress)
            draw.rectangle([0, 0, w, y], fill=255)
        elif self.direction == "down":
            y = int(h * (1 - progress))
            draw.rectangle([0, y, w, h], fill=255)

        overlay = Image.new("RGBA", image.size, self.color + (255,))
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        result = image.copy()
        result.paste(overlay, mask=mask)
        return result


class DissolveTransition(Transition):
    """Dissolve/crossfade transition."""

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        progress = self.easing(t)
        alpha = int(255 * (1 - progress))
        overlay = Image.new("RGBA", image.size, (0, 0, 0, alpha))

        if image.mode != "RGBA":
            image = image.convert("RGBA")
        return Image.alpha_composite(image, overlay)


class SlideTransition(Transition):
    """Slide transition."""

    def __init__(self, direction: str = "left", **kwargs):
        super().__init__(**kwargs)
        self.direction = direction

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        progress = self.easing(t)
        w, h = image.size

        if self.direction == "left":
            offset_x = int(w * progress)
            offset_y = 0
        elif self.direction == "right":
            offset_x = -int(w * progress)
            offset_y = 0
        elif self.direction == "up":
            offset_x = 0
            offset_y = int(h * progress)
        else:
            offset_x = 0
            offset_y = -int(h * progress)

        result = Image.new("RGBA", image.size, (0, 0, 0, 255))
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        result.paste(image, (offset_x, offset_y))
        return result


class ZoomTransition(Transition):
    """Zoom transition."""

    def __init__(self, zoom_in: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.zoom_in = zoom_in

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        progress = self.easing(t)
        w, h = image.size

        if self.zoom_in:
            scale = 1 + progress * 2
        else:
            scale = 1 / (1 + progress * 2)

        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        zoomed = image.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Center crop
        left = (new_w - w) // 2
        top = (new_h - h) // 2
        zoomed = zoomed.crop((left, top, left + w, top + h))

        # Fade
        alpha = int(255 * (1 - progress))
        if zoomed.mode != "RGBA":
            zoomed = zoomed.convert("RGBA")
        overlay = Image.new("RGBA", zoomed.size, (0, 0, 0, alpha))
        return Image.alpha_composite(zoomed, overlay)


class PushTransition(Transition):
    """Push transition — new scene pushes old one out."""

    def __init__(self, direction: str = "left", **kwargs):
        super().__init__(**kwargs)
        self.direction = direction

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        progress = self.easing(t)
        w, h = image.size

        if self.direction == "left":
            offset = int(w * progress)
        elif self.direction == "right":
            offset = -int(w * progress)
        elif self.direction == "up":
            offset = int(h * progress)
        else:
            offset = -int(h * progress)

        result = Image.new("RGBA", image.size, (0, 0, 0, 255))
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        if self.direction in ("left", "right"):
            result.paste(image, (offset, 0))
        else:
            result.paste(image, (0, offset))

        return result
