"""
Color Effects — Brightness, contrast, saturation, hue, grading.
"""

from PIL import Image, ImageEnhance, ImageOps
import numpy as np

from ouroboros.effects.base import Effect


class Brightness(Effect):
    def __init__(self, factor: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.factor = factor

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        f = self.get_animated_value("factor", t, self.factor)
        return ImageEnhance.Brightness(image).enhance(f)


class Contrast(Effect):
    def __init__(self, factor: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.factor = factor

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        f = self.get_animated_value("factor", t, self.factor)
        return ImageEnhance.Contrast(image).enhance(f)


class Saturation(Effect):
    def __init__(self, factor: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.factor = factor

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        f = self.get_animated_value("factor", t, self.factor)
        return ImageEnhance.Color(image).enhance(f)


class HueShift(Effect):
    def __init__(self, degrees: float = 0, **kwargs):
        super().__init__(**kwargs)
        self.degrees = degrees

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        deg = self.get_animated_value("degrees", t, self.degrees)
        if image.mode != "HSV":
            hsv = image.convert("HSV")
        else:
            hsv = image
        arr = np.array(hsv)
        arr[:, :, 0] = (arr[:, :, 0].astype(int) + int(deg * 255 / 360)) % 256
        return Image.fromarray(arr, "HSV").convert("RGBA")


class Sepia(Effect):
    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        gray = ImageOps.grayscale(image)
        arr = np.array(gray).astype(np.float64)
        r = np.clip(arr * 1.2 + 30, 0, 255).astype(np.uint8)
        g = np.clip(arr * 1.0 + 15, 0, 255).astype(np.uint8)
        b = np.clip(arr * 0.8, 0, 255).astype(np.uint8)
        result = np.stack([r, g, b], axis=-1)
        if image.mode == "RGBA":
            alpha = np.array(image)[:, :, 3:4]
            result = np.concatenate([result, alpha], axis=-1)
            return Image.fromarray(result, "RGBA")
        return Image.fromarray(result, "RGB")


class Grayscale(Effect):
    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        gray = ImageOps.grayscale(image)
        if image.mode == "RGBA":
            alpha = image.split()[3]
            gray = gray.convert("RGBA")
            gray.putalpha(alpha)
        return gray


class Invert(Effect):
    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        if image.mode == "RGBA":
            r, g, b, a = image.split()
            rgb = Image.merge("RGB", (r, g, b))
            inv = ImageOps.invert(rgb)
            return Image.merge("RGBA", (*inv.split(), a))
        return ImageOps.invert(image)


class ColorBalance(Effect):
    def __init__(self, red: float = 0, green: float = 0, blue: float = 0, **kwargs):
        super().__init__(**kwargs)
        self.red = red
        self.green = green
        self.blue = blue

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        r = self.get_animated_value("red", t, self.red)
        g = self.get_animated_value("green", t, self.green)
        b = self.get_animated_value("blue", t, self.blue)

        arr = np.array(image).astype(np.float64)
        arr[:, :, 0] = np.clip(arr[:, :, 0] + r, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] + g, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] + b, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))


class Temperature(Effect):
    def __init__(self, kelvin: float = 6500, **kwargs):
        super().__init__(**kwargs)
        self.kelvin = kelvin

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        k = self.get_animated_value("kelvin", t, self.kelvin)
        # Approximate color temperature
        if k < 6500:
            # Warm
            factor = (6500 - k) / 6500
            r_adj = factor * 30
            b_adj = -factor * 30
        else:
            # Cool
            factor = (k - 6500) / 6500
            r_adj = -factor * 30
            b_adj = factor * 30

        arr = np.array(image).astype(np.float64)
        arr[:, :, 0] = np.clip(arr[:, :, 0] + r_adj, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] + b_adj, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))
