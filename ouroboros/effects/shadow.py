"""
Shadow Effects — Drop shadow, long shadow, inner shadow.
"""

from PIL import Image, ImageFilter, ImageDraw
import numpy as np

from ouroboros.effects.base import Effect


class DropShadow(Effect):
    """Drop shadow effect."""

    def __init__(self, offset_x: int = 4, offset_y: int = 4, blur: float = 5,
                 color: tuple = (0, 0, 0, 128), **kwargs):
        super().__init__(**kwargs)
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.blur = blur
        self.color = color

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        ox = int(self.get_animated_value("offset_x", t, self.offset_x))
        oy = int(self.get_animated_value("offset_y", t, self.offset_y))
        b = self.get_animated_value("blur", t, self.blur)

        w, h = image.size
        # Expand canvas for shadow
        pad = abs(ox) + abs(oy) + int(b) + 10
        canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))

        # Create shadow
        shadow = Image.new("RGBA", (w, h), self.color)
        if image.mode == "RGBA":
            alpha = image.split()[3]
            shadow.putalpha(alpha)

        shadow = shadow.filter(ImageFilter.GaussianBlur(b))
        canvas.paste(shadow, (pad + ox, pad + oy))
        canvas.paste(image, (pad, pad), image if image.mode == "RGBA" else None)

        return canvas


class LongShadow(Effect):
    """Long shadow effect (45-degree)."""

    def __init__(self, length: int = 50, color: tuple = (0, 0, 0, 100), angle: float = 135, **kwargs):
        super().__init__(**kwargs)
        self.length = length
        self.color = color
        self.angle = angle

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        lng = int(self.get_animated_value("length", t, self.length))
        angle = self.get_animated_value("angle", t, self.angle)

        w, h = image.size
        rad = np.radians(angle)
        dx = np.cos(rad)
        dy = np.sin(rad)

        canvas = Image.new("RGBA", (w + lng, h + lng), (0, 0, 0, 0))

        # Create shadow by stacking shifted copies
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        alpha = image.split()[3]
        shadow_base = Image.new("RGBA", image.size, self.color)
        shadow_base.putalpha(alpha)

        for i in range(lng):
            offset_x = int(dx * i)
            offset_y = int(dy * i)
            canvas.paste(shadow_base, (offset_x, offset_y), shadow_base)

        canvas.paste(image, (0, 0), image)
        return canvas


class InnerShadow(Effect):
    """Inner shadow effect."""

    def __init__(self, offset_x: int = 3, offset_y: int = 3, blur: float = 5,
                 color: tuple = (0, 0, 0, 100), **kwargs):
        super().__init__(**kwargs)
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.blur = blur
        self.color = color

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        if image.mode != "RGBA":
            return image

        ox = int(self.get_animated_value("offset_x", t, self.offset_x))
        oy = int(self.get_animated_value("offset_y", t, self.offset_y))
        b = self.get_animated_value("blur", t, self.blur)

        # Create inverted alpha mask
        alpha = image.split()[3]
        mask = alpha.copy()

        # Shift and blur mask
        arr = np.array(mask)
        shifted = np.roll(arr, -oy, axis=0)
        shifted = np.roll(shifted, -ox, axis=1)
        mask = Image.fromarray(shifted)
        mask = mask.filter(ImageFilter.GaussianBlur(b))

        # Create shadow layer
        shadow = Image.new("RGBA", image.size, self.color + (0,))
        shadow.putalpha(mask)

        # Composite
        result = image.copy()
        result = Image.alpha_composite(result, shadow)

        # Clip to original alpha
        result.putalpha(alpha)
        return result
