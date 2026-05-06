"""
Distortion Effects — Wave, ripple, pixelate, glitch, grain, vignette.
"""

from PIL import Image, ImageFilter
import numpy as np
import math

from ouroboros.effects.base import Effect


class Wave(Effect):
    """Wave distortion effect."""

    def __init__(self, amplitude: float = 20, frequency: float = 0.05, speed: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.amplitude = amplitude
        self.frequency = frequency
        self.speed = speed

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        amp = self.get_animated_value("amplitude", t, self.amplitude)
        freq = self.get_animated_value("frequency", t, self.frequency)
        spd = self.get_animated_value("speed", t, self.speed)

        arr = np.array(image)
        h, w = arr.shape[:2]

        # Create displacement maps
        x_indices = np.arange(w)[np.newaxis, :].repeat(h, axis=0).astype(np.float64)
        y_indices = np.arange(h)[:, np.newaxis].repeat(w, axis=1).astype(np.float64)

        # Apply wave
        x_indices += amp * np.sin(y_indices * freq + frame_idx * spd * 0.1)

        # Clip indices
        x_indices = np.clip(x_indices, 0, w - 1).astype(int)
        y_indices = np.clip(y_indices, 0, h - 1).astype(int)

        result = arr[y_indices, x_indices]
        return Image.fromarray(result)


class Ripple(Effect):
    """Ripple distortion effect."""

    def __init__(self, amplitude: float = 10, frequency: float = 0.1, center: tuple = (0.5, 0.5), **kwargs):
        super().__init__(**kwargs)
        self.amplitude = amplitude
        self.frequency = frequency
        self.center = center

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        amp = self.get_animated_value("amplitude", t, self.amplitude)
        freq = self.get_animated_value("frequency", t, self.frequency)

        arr = np.array(image)
        h, w = arr.shape[:2]

        cx = self.center[0] * w
        cy = self.center[1] * h

        y_coords, x_coords = np.mgrid[0:h, 0:w]
        dx = x_coords - cx
        dy = y_coords - cy
        dist = np.sqrt(dx ** 2 + dy ** 2)

        # Apply ripple displacement
        displacement = amp * np.sin(dist * freq)
        factor = displacement / (dist + 1)

        new_x = np.clip(x_coords + dx * factor, 0, w - 1).astype(int)
        new_y = np.clip(y_coords + dy * factor, 0, h - 1).astype(int)

        result = arr[new_y, new_x]
        return Image.fromarray(result)


class Pixelate(Effect):
    """Pixelation effect."""

    def __init__(self, block_size: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.block_size = block_size

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        bs = int(self.get_animated_value("block_size", t, self.block_size))
        if bs <= 1:
            return image

        w, h = image.size
        small = image.resize((max(1, w // bs), max(1, h // bs)), Image.Resampling.NEAREST)
        return small.resize((w, h), Image.Resampling.NEAREST)


class Glitch(Effect):
    """Digital glitch effect."""

    def __init__(self, intensity: float = 0.5, seed: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.intensity = intensity
        self.seed = seed

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        i = self.get_animated_value("intensity", t, self.intensity)
        if i <= 0:
            return image

        arr = np.array(image).astype(np.float64)
        h, w = arr.shape[:2]
        rng = np.random.RandomState(self.seed + frame_idx)

        # Random horizontal shifts
        num_slices = max(1, int(i * 20))
        for _ in range(num_slices):
            y = rng.randint(0, h)
            slice_h = rng.randint(1, max(2, int(h * 0.05 * i)))
            shift = rng.randint(-int(w * 0.1 * i), int(w * 0.1 * i))
            arr[y:min(y + slice_h, h)] = np.roll(arr[y:min(y + slice_h, h)], shift, axis=1)

        # RGB channel split
        if i > 0.3:
            shift_r = int(i * 10)
            arr[:, :, 0] = np.roll(arr[:, :, 0], shift_r, axis=1)
            arr[:, :, 2] = np.roll(arr[:, :, 2], -shift_r, axis=1)

        # Random noise blocks
        if i > 0.5:
            num_blocks = int(i * 5)
            for _ in range(num_blocks):
                bx = rng.randint(0, w - 20)
                by = rng.randint(0, h - 10)
                bw = rng.randint(5, 20)
                bh = rng.randint(2, 10)
                arr[by:by + bh, bx:bx + bw] = rng.randint(0, 255, (bh, bw, arr.shape[2]))

        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


class FilmGrain(Effect):
    """Film grain / noise effect."""

    def __init__(self, amount: float = 30, seed: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.amount = amount
        self.seed = seed

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        amt = self.get_animated_value("amount", t, self.amount)
        if amt <= 0:
            return image

        arr = np.array(image).astype(np.float64)
        rng = np.random.RandomState(self.seed + frame_idx)
        noise = rng.normal(0, amt, arr.shape[:2])

        for c in range(min(3, arr.shape[2])):
            arr[:, :, c] = np.clip(arr[:, :, c] + noise, 0, 255)

        return Image.fromarray(arr.astype(np.uint8))


class Vignette(Effect):
    """Vignette effect — darken edges."""

    def __init__(self, strength: float = 0.5, size: float = 0.5, **kwargs):
        super().__init__(**kwargs)
        self.strength = strength
        self.size = size

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        s = self.get_animated_value("strength", t, self.strength)
        sz = self.get_animated_value("size", t, self.size)

        w, h = image.size
        arr = np.array(image).astype(np.float64)

        y_coords, x_coords = np.mgrid[0:h, 0:w]
        cx, cy = w / 2, h / 2
        max_dist = math.sqrt(cx ** 2 + cy ** 2)

        dist = np.sqrt((x_coords - cx) ** 2 + (y_coords - cy) ** 2) / max_dist
        vignette = 1 - np.clip((dist - sz) / (1 - sz), 0, 1) * s

        for c in range(min(3, arr.shape[2])):
            arr[:, :, c] *= vignette

        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


class ChromaticAberration(Effect):
    """Chromatic aberration — RGB channel offset."""

    def __init__(self, offset: int = 5, **kwargs):
        super().__init__(**kwargs)
        self.offset = offset

    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        off = int(self.get_animated_value("offset", t, self.offset))
        if off == 0:
            return image

        arr = np.array(image)
        result = arr.copy()

        # Shift red channel right
        result[:, :, 0] = np.roll(arr[:, :, 0], off, axis=1)
        # Shift blue channel left
        result[:, :, 2] = np.roll(arr[:, :, 2], -off, axis=1)

        return Image.fromarray(result)
