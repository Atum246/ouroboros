"""
Image Layer — Embed images with transforms and effects.

Supports PNG, JPG, WebP, GIF (first frame), SVG (via conversion).
"""

import os
from typing import Any, Dict, Optional, Tuple
from PIL import Image, ImageFilter

from ouroboros.layers.base import Layer


class ImageLayer(Layer):
    """
    Image layer for embedding images.

    Args:
        source: Image path, URL, or PIL Image
        fit: How to fit image ('fill', 'contain', 'cover', 'stretch')
        brightness: Brightness adjustment (0-2, 1=normal)
        contrast: Contrast adjustment (0-2, 1=normal)

    Example::

        logo = ImageLayer("logo.png", x=50, y=50, scale_x=0.5, scale_y=0.5)
        logo.animate("opacity", 0, 1, 0, 1, ease_in_out)

        # From URL
        pic = ImageLayer("https://example.com/photo.jpg", fit="cover")
    """

    def __init__(
        self,
        source: Any = None,
        fit: str = "fill",
        brightness: float = 1.0,
        contrast: float = 1.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.source = source
        self.fit = fit
        self.brightness = brightness
        self.contrast = contrast
        self._cached_image: Optional[Image.Image] = None

    def _load_image(self) -> Optional[Image.Image]:
        """Load image from source."""
        if self._cached_image is not None:
            return self._cached_image

        if isinstance(self.source, Image.Image):
            self._cached_image = self.source.convert("RGBA")
            return self._cached_image

        if isinstance(self.source, str):
            if self.source.startswith(("http://", "https://")):
                # Download image
                try:
                    import urllib.request
                    import io
                    req = urllib.request.Request(self.source, headers={"User-Agent": "Ouroboros/1.0"})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        data = resp.read()
                    self._cached_image = Image.open(io.BytesIO(data)).convert("RGBA")
                    return self._cached_image
                except Exception as e:
                    print(f"Warning: Could not load image from {self.source}: {e}")
                    return None
            elif os.path.exists(self.source):
                self._cached_image = Image.open(self.source).convert("RGBA")
                return self._cached_image

        return None

    def _fit_image(
        self,
        img: Image.Image,
        target_w: int,
        target_h: int,
    ) -> Image.Image:
        """Fit image to target size based on fit mode."""
        iw, ih = img.size

        if self.fit == "stretch":
            return img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        elif self.fit == "contain":
            scale = min(target_w / iw, target_h / ih)
            new_w = int(iw * scale)
            new_h = int(ih * scale)
            resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
            offset_x = (target_w - new_w) // 2
            offset_y = (target_h - new_h) // 2
            canvas.paste(resized, (offset_x, offset_y))
            return canvas
        elif self.fit == "cover":
            scale = max(target_w / iw, target_h / ih)
            new_w = int(iw * scale)
            new_h = int(ih * scale)
            resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            # Crop to target
            left = (new_w - target_w) // 2
            top = (new_h - target_h) // 2
            return resized.crop((left, top, left + target_w, top + target_h))
        else:  # fill - use original size or layer dimensions
            w = self._width or iw
            h = self._height or ih
            if w != iw or h != ih:
                return img.resize((w, h), Image.Resampling.LANCZOS)
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
        img = self._load_image()
        if img is None:
            return None

        # Fit to dimensions
        target_w = self._width or img.size[0]
        target_h = self._height or img.size[1]
        img = self._fit_image(img, target_w, target_h)

        # Apply brightness
        brightness = props.get("brightness", self.brightness)
        if brightness != 1.0:
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(brightness)

        # Apply contrast
        contrast = props.get("contrast", self.contrast)
        if contrast != 1.0:
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast)

        return img
