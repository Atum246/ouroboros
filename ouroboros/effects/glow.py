"""
Glow and Bloom Effects.
"""

from PIL import Image, ImageFilter
import numpy as np

from ouroboros.effects.base import Effect


class Glow(Effect):
    """Add a glow effect around bright areas."""

    def __init__(self, radius: float = 10, intensity: float = 0.5, color: tuple = None, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        self.glow_intensity = intensity
        self.color = color

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        r = self.get_animated_value("radius", t, self.radius)
        i = self.get_animated_value("glow_intensity", t, self.glow_intensity)

        # Create blurred version
        blurred = image.filter(ImageFilter.GaussianBlur(r))

        if self.color:
            # Color the glow
            color_img = Image.new("RGBA", image.size, self.color)
            blurred = Image.alpha_composite(blurred, color_img)

        # Blend original with glow
        return Image.blend(image, blurred, i)


class Bloom(Effect):
    """Bloom effect — glow on bright areas only."""

    def __init__(self, threshold: int = 200, radius: float = 15, intensity: float = 0.6, **kwargs):
        super().__init__(**kwargs)
        self.threshold = threshold
        self.radius = radius
        self.bloom_intensity = intensity

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        thresh = int(self.get_animated_value("threshold", t, self.threshold))
        r = self.get_animated_value("radius", t, self.radius)
        i = self.get_animated_value("bloom_intensity", t, self.bloom_intensity)

        arr = np.array(image).astype(np.float64)
        # Extract bright areas
        brightness = np.mean(arr[:, :, :3], axis=2)
        mask = brightness > thresh

        bright = np.zeros_like(arr)
        bright[mask] = arr[mask]

        bright_img = Image.fromarray(bright.astype(np.uint8))
        bloom = bright_img.filter(ImageFilter.GaussianBlur(r))

        # Add bloom back
        result = np.array(image).astype(np.float64) + np.array(bloom).astype(np.float64) * i
        result = np.clip(result, 0, 255).astype(np.uint8)
        return Image.fromarray(result)


class Neon(Effect):
    """Neon glow effect with color."""

    def __init__(self, color: tuple = (0, 255, 255), radius: float = 8, **kwargs):
        super().__init__(**kwargs)
        self.color = color
        self.radius = radius

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        r = self.get_animated_value("radius", t, self.radius)

        # Edge detection
        edges = image.filter(ImageFilter.FIND_EDGES)

        # Color the edges
        color_layer = Image.new("RGBA", image.size, self.color + (255,))
        colored_edges = Image.composite(color_layer, Image.new("RGBA", image.size, (0, 0, 0, 0)), edges)

        # Blur for glow
        glow = colored_edges.filter(ImageFilter.GaussianBlur(r))

        # Composite
        result = Image.alpha_composite(image, glow)
        return result
