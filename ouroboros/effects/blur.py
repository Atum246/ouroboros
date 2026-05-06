"""
Blur Effects — Gaussian, motion, radial, and box blur.
"""

from typing import Optional
from PIL import Image, ImageFilter
import numpy as np

from ouroboros.effects.base import Effect


class Blur(Effect):
    """Simple box blur."""

    def __init__(self, radius: int = 5, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        r = self.get_animated_value("radius", t, self.radius)
        return image.filter(ImageFilter.BoxBlur(r))


class GaussianBlur(Effect):
    """Gaussian blur effect."""

    def __init__(self, radius: float = 5, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        r = self.get_animated_value("radius", t, self.radius)
        return image.filter(ImageFilter.GaussianBlur(r))


class MotionBlur(Effect):
    """Motion blur effect (directional)."""

    def __init__(self, radius: int = 10, angle: float = 0, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        self.angle = angle

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        r = int(self.get_animated_value("radius", t, self.radius))
        angle = self.get_animated_value("angle", t, self.angle)

        # Create motion blur kernel
        import math
        img_array = np.array(image)
        h, w = img_array.shape[:2]

        # Simple motion blur via averaging shifted copies
        result = np.zeros_like(img_array, dtype=np.float64)
        rad = math.radians(angle)
        dx = math.cos(rad)
        dy = math.sin(rad)

        for i in range(-r, r + 1):
            shift_x = int(dx * i)
            shift_y = int(dy * i)
            shifted = np.roll(img_array, shift_x, axis=1)
            shifted = np.roll(shifted, shift_y, axis=0)
            result += shifted.astype(np.float64)

        result /= (2 * r + 1)
        return Image.fromarray(result.astype(np.uint8))


class RadialBlur(Effect):
    """Radial/zoom blur effect."""

    def __init__(self, strength: float = 0.5, center: tuple = (0.5, 0.5), **kwargs):
        super().__init__(**kwargs)
        self.strength = strength
        self.center = center

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        s = self.get_animated_value("strength", t, self.strength)
        if s <= 0:
            return image

        img_array = np.array(image).astype(np.float64)
        h, w = img_array.shape[:2]
        cx = int(self.center[0] * w)
        cy = int(self.center[1] * h)

        result = np.zeros_like(img_array)
        steps = max(3, int(s * 10))

        for i in range(steps):
            scale = 1.0 + s * (i / steps) * 0.1
            # Simple scale approximation
            from PIL import Image
            pil = Image.fromarray(img_array.astype(np.uint8))
            new_w = int(w * scale)
            new_h = int(h * scale)
            pil = pil.resize((new_w, new_h), Image.Resampling.LANCZOS)
            # Crop back to center
            left = (new_w - w) // 2
            top = (new_h - h) // 2
            pil = pil.crop((left, top, left + w, top + h))
            result += np.array(pil).astype(np.float64)

        result /= steps
        return Image.fromarray(result.astype(np.uint8))
