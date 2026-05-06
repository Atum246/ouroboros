"""
Mask Effects — Alpha masks, shape masks, gradient masks.
"""

from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import math

from ouroboros.effects.base import Effect


class Mask(Effect):
    """Apply an alpha mask."""

    def __init__(self, mask_image: Image.Image = None, invert: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.mask_image = mask_image
        self.invert = invert

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        if self.mask_image is None:
            return image

        w, h = image.size
        mask = self.mask_image.resize((w, h)).convert("L")

        if self.invert:
            mask = Image.fromarray(255 - np.array(mask))

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        result = image.copy()
        result.putalpha(mask)
        return result


class ShapeMask(Effect):
    """Mask with a geometric shape."""

    def __init__(self, shape: str = "circle", feather: float = 0, **kwargs):
        super().__init__(**kwargs)
        self.shape = shape
        self.feather = feather

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        w, h = image.size
        mask = Image.new("L", (w, h), 0)
        draw = ImageDraw.Draw(mask)

        feather = self.get_animated_value("feather", t, self.feather)

        if self.shape == "circle":
            r = min(w, h) // 2
            cx, cy = w // 2, h // 2
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
        elif self.shape == "rectangle":
            margin = min(w, h) // 10
            draw.rectangle([margin, margin, w - margin, h - margin], fill=255)
        elif self.shape == "diamond":
            points = [(w // 2, 0), (w, h // 2), (w // 2, h), (0, h // 2)]
            draw.polygon(points, fill=255)
        elif self.shape == "star":
            points = []
            for i in range(10):
                angle = math.pi * i / 5 - math.pi / 2
                r = min(w, h) // 2 if i % 2 == 0 else min(w, h) // 4
                points.append((w // 2 + r * math.cos(angle), h // 2 + r * math.sin(angle)))
            draw.polygon(points, fill=255)

        if feather > 0:
            mask = mask.filter(ImageFilter.GaussianBlur(feather))

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        result = image.copy()
        result.putalpha(mask)
        return result


class GradientMask(Effect):
    """Gradient-based alpha mask."""

    def __init__(self, direction: str = "vertical", invert: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.direction = direction
        self.invert = invert

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        w, h = image.size
        mask = Image.new("L", (w, h), 0)
        pixels = mask.load()

        for y in range(h):
            for x in range(w):
                if self.direction == "vertical":
                    val = int(255 * y / h)
                elif self.direction == "horizontal":
                    val = int(255 * x / w)
                elif self.direction == "radial":
                    cx, cy = w / 2, h / 2
                    dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                    max_dist = math.sqrt(cx ** 2 + cy ** 2)
                    val = int(255 * (1 - dist / max_dist))
                elif self.direction == "diagonal":
                    val = int(255 * (x / w + y / h) / 2)
                else:
                    val = 255

                if self.invert:
                    val = 255 - val
                pixels[x, y] = max(0, min(255, val))

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        result = image.copy()
        result.putalpha(mask)
        return result
