"""
Keyframe Animation System.

Define animations with keyframes and the framework interpolates between them.
"""

from typing import List, Optional, Any, Callable, Tuple
from ouroboros.animation.easing import (
    linear, EasingFunc, interpolate, interpolate_color,
)


class Keyframe:
    """
    A single keyframe.

    Args:
        time: Normalized time (0-1 within the animation range)
        value: Value at this keyframe
        easing: Easing function to use when approaching this keyframe
    """

    def __init__(self, time: float, value: Any, easing: EasingFunc = linear):
        self.time = time
        self.value = value
        self.easing = easing

    def __repr__(self) -> str:
        return f"Keyframe(t={self.time}, v={self.value})"


class Animation:
    """
    An animation track with keyframes.

    Supports animating any numeric value or color.

    Args:
        property_name: Name of the property to animate
        keyframes: List of Keyframe objects

    Example::

        anim = Animation("opacity", [
            Keyframe(0, 0),
            Keyframe(0.5, 1, ease_out),
            Keyframe(1, 0),
        ])
        value = anim.get_value(0.7)  # interpolated value
    """

    def __init__(self, property_name: str, keyframes: Optional[List[Keyframe]] = None):
        self.property_name = property_name
        self.keyframes: List[Keyframe] = keyframes or []
        self._sort_keyframes()

    def _sort_keyframes(self):
        """Sort keyframes by time."""
        self.keyframes.sort(key=lambda k: k.time)

    def add_keyframe(self, time: float, value: Any, easing: EasingFunc = linear):
        """Add a keyframe."""
        self.keyframes.append(Keyframe(time, value, easing))
        self._sort_keyframes()

    def get_value(self, t: float) -> Any:
        """
        Get interpolated value at normalized time t.

        Args:
            t: Normalized time (0-1)

        Returns:
            Interpolated value
        """
        if not self.keyframes:
            return 0

        if len(self.keyframes) == 1:
            return self.keyframes[0].value

        # Clamp t
        t = max(0.0, min(1.0, t))

        # Find surrounding keyframes
        before = None
        after = None

        for i, kf in enumerate(self.keyframes):
            if kf.time <= t:
                before = kf
            if kf.time >= t and after is None:
                after = kf

        if before is None:
            return self.keyframes[0].value
        if after is None:
            return self.keyframes[-1].value
        if before is after:
            return before.value

        # Calculate local t between keyframes
        duration = after.time - before.time
        if duration == 0:
            return before.value

        local_t = (t - before.time) / duration

        # Use the easing of the destination keyframe
        eased_t = after.easing(local_t)

        # Interpolate based on value type
        return self._interpolate(before.value, after.value, eased_t)

    def _interpolate(self, start: Any, end: Any, t: float) -> Any:
        """Interpolate between two values."""
        if isinstance(start, (int, float)) and isinstance(end, (int, float)):
            return start + (end - start) * t
        elif isinstance(start, tuple) and isinstance(end, tuple):
            if len(start) == len(end):
                return tuple(
                    s + (e - s) * t
                    for s, e in zip(start, end)
                )
        elif isinstance(start, str) and isinstance(end, str):
            # Try to parse as colors
            try:
                s_color = self._parse_color(start)
                e_color = self._parse_color(end)
                result = interpolate_color(s_color, e_color, t)
                return "#{:02x}{:02x}{:02x}".format(result[0], result[1], result[2])
            except (ValueError, IndexError):
                pass
        return start if t < 0.5 else end

    def _parse_color(self, color: str) -> Tuple[int, int, int, int]:
        """Parse hex color to RGBA."""
        color = color.lstrip("#")
        if len(color) == 6:
            return (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16), 255)
        elif len(color) == 8:
            return (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16), int(color[6:8], 16))
        raise ValueError(f"Invalid color: {color}")

    def __repr__(self) -> str:
        return f"Animation('{self.property_name}', {len(self.keyframes)} keyframes)"


class Animator:
    """
    Manages multiple animations for an object.

    Example::

        animator = Animator()
        animator.add("x", [(0, 0), (0.5, 100), (1, 0)], ease_in_out)
        animator.add("opacity", [(0, 0), (1, 1)], ease_out)

        props = animator.get_properties(0.7)
        # {"x": 60, "opacity": 0.7}
    """

    def __init__(self):
        self.animations: dict[str, Animation] = {}

    def add(
        self,
        property_name: str,
        keyframes: List[Tuple[float, Any]],
        easing: EasingFunc = linear,
    ):
        """
        Add an animation with simple keyframe tuples.

        Args:
            property_name: Property to animate
            keyframes: List of (time, value) tuples
            easing: Default easing for all keyframes
        """
        anim = Animation(property_name)
        for time, value in keyframes:
            anim.add_keyframe(time, value, easing)
        self.animations[property_name] = anim

    def add_animation(self, animation: Animation):
        """Add a pre-built Animation object."""
        self.animations[animation.property_name] = animation

    def get_value(self, property_name: str, t: float) -> Any:
        """Get animated value for a property."""
        if property_name in self.animations:
            return self.animations[property_name].get_value(t)
        return None

    def get_properties(self, t: float) -> dict:
        """Get all animated properties at time t."""
        return {
            name: anim.get_value(t)
            for name, anim in self.animations.items()
        }

    def has_animation(self, property_name: str) -> bool:
        """Check if a property has an animation."""
        return property_name in self.animations
