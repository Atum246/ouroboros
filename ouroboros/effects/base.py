"""
Base Effect — Abstract base class for all effects.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from PIL import Image

from ouroboros.animation.keyframe import Animator


class Effect(ABC):
    """
    Abstract base class for effects.

    Effects are applied to layers or compositions per-frame.
    """

    def __init__(self, intensity: float = 1.0, **kwargs):
        self.intensity = intensity
        self._animator = Animator()
        self._animated_props = {}

        for key, value in kwargs.items():
            setattr(self, key, value)

    def animate(self, property_name: str, start: Any, end: Any,
                start_time: float = 0, end_time: float = 1, easing=None):
        """Animate an effect property."""
        from ouroboros.animation.tween import Tween
        self._animated_props[property_name] = Tween(start, end, start_time, end_time, easing or (lambda x: x))

    def get_animated_value(self, prop: str, t: float, default: Any) -> Any:
        """Get animated value or default."""
        if prop in self._animated_props:
            return self._animated_props[prop].get_value(t)
        return default

    @abstractmethod
    def apply(self, image: Image.Image, t: float, frame_idx: int) -> Image.Image:
        """Apply the effect to an image."""
        pass
