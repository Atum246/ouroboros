"""
Property Tweening — Simplified animation API.

Quick way to animate properties without full keyframe setup.
"""

from typing import Any, Optional, Callable
from ouroboros.animation.easing import linear, EasingFunc, interpolate


class Tween:
    """
    A simple tween between two values.

    Args:
        start: Start value
        end: End value
        start_time: When to start (normalized 0-1)
        end_time: When to end (normalized 0-1)
        easing: Easing function

    Example::

        tween = Tween(0, 100, start_time=0.2, end_time=0.8, easing=ease_in_out)
        value = tween.get_value(0.5)  # some interpolated value
    """

    def __init__(
        self,
        start: Any,
        end: Any,
        start_time: float = 0.0,
        end_time: float = 1.0,
        easing: EasingFunc = linear,
    ):
        self.start = start
        self.end = end
        self.start_time = start_time
        self.end_time = end_time
        self.easing = easing

    def get_value(self, t: float) -> Any:
        """Get value at normalized time t."""
        if t <= self.start_time:
            return self.start
        if t >= self.end_time:
            return self.end

        # Calculate local progress
        duration = self.end_time - self.start_time
        local_t = (t - self.start_time) / duration

        return interpolate(self.start, self.end, local_t, self.easing)


class TweenGroup:
    """
    Group of tweens for animating multiple properties.

    Example::

        group = TweenGroup()
        group.add("x", Tween(0, 100, 0, 0.5, ease_in_out))
        group.add("y", Tween(0, 50, 0.2, 0.8, ease_out))
        group.add("opacity", Tween(0, 1, 0, 1, ease_in))

        props = group.get_properties(0.3)
        # {"x": 40, "y": 0, "opacity": 0.3}
    """

    def __init__(self):
        self.tweens: dict[str, Tween] = {}

    def add(self, property_name: str, tween: Tween):
        """Add a tween for a property."""
        self.tweens[property_name] = tween

    def get_value(self, property_name: str, t: float) -> Any:
        """Get value for a property."""
        if property_name in self.tweens:
            return self.tweens[property_name].get_value(t)
        return None

    def get_properties(self, t: float) -> dict:
        """Get all tweened properties at time t."""
        return {
            name: tween.get_value(t)
            for name, tween in self.tweens.items()
        }
