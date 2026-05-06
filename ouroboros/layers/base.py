"""
Base Layer — Abstract base for all layers.

Every visual element in Ouroboros is a Layer.
Layers have properties that can be animated, and they render to PIL Images.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Callable
from PIL import Image
import numpy as np

from ouroboros.animation.keyframe import Animation, Animator
from ouroboros.animation.tween import Tween, TweenGroup
from ouroboros.animation.easing import linear, EasingFunc


class Layer(ABC):
    """
    Abstract base class for all layers.

    Layers are visual elements that can be positioned, transformed,
    and animated within a composition.

    Args:
        x: X position (pixels from left)
        y: Y position (pixels from top)
        width: Width in pixels
        height: Height in pixels
        opacity: Opacity (0-1)
        rotation: Rotation in degrees
        scale_x: Horizontal scale
        scale_y: Vertical scale
        anchor_x: Anchor point X (0-1, 0.5 = center)
        anchor_y: Anchor point Y (0-1, 0.5 = center)
        blend_mode: Blend mode (normal, multiply, screen, overlay, etc.)
        visible: Whether layer is visible
        name: Layer name for debugging
    """

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
        opacity: float = 1.0,
        rotation: float = 0.0,
        scale_x: float = 1.0,
        scale_y: float = 1.0,
        anchor_x: float = 0.5,
        anchor_y: float = 0.5,
        blend_mode: str = "normal",
        visible: bool = True,
        name: Optional[str] = None,
        **kwargs,
    ):
        self.x = x
        self.y = y
        self._width = width
        self._height = height
        self.opacity = opacity
        self.rotation = rotation
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.blend_mode = blend_mode
        self.visible = visible
        self.name = name or self.__class__.__name__

        # Animation system
        self._animator = Animator()
        self._tween_group = TweenGroup()
        self._effects: List = []
        self._filters: List = []
        self._parent: Optional[Layer] = None
        self._children: List[Layer] = []

        # Store any extra kwargs as properties
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def width(self) -> int:
        return self._width or 0

    @property
    def height(self) -> int:
        return self._height or 0

    def animate(
        self,
        property_name: str,
        start_value: Any,
        end_value: Any,
        start_time: float = 0.0,
        end_time: float = 1.0,
        easing: EasingFunc = linear,
    ):
        """
        Animate a property.

        Args:
            property_name: Property to animate (x, y, opacity, rotation, etc.)
            start_value: Starting value
            end_value: Ending value
            start_time: When to start (0-1 normalized)
            end_time: When to end (0-1 normalized)
            easing: Easing function

        Example::

            layer.animate("opacity", 0, 1, 0, 0.5, ease_in_out)
            layer.animate("x", 0, 100, 0.2, 0.8, ease_out)
        """
        tween = Tween(start_value, end_value, start_time, end_time, easing)
        self._tween_group.add(property_name, tween)

    def animate_keyframes(
        self,
        property_name: str,
        keyframes: List[Tuple[float, Any]],
        easing: EasingFunc = linear,
    ):
        """
        Animate a property with multiple keyframes.

        Args:
            property_name: Property to animate
            keyframes: List of (time, value) tuples
            easing: Default easing
        """
        self._animator.add(property_name, keyframes, easing)

    def add_effect(self, effect):
        """Add an effect to this layer."""
        self._effects.append(effect)

    def add_filter(self, filter_func: Callable):
        """Add a pixel filter function."""
        self._filters.append(filter_func)

    def add_child(self, child: "Layer"):
        """Add a child layer."""
        child._parent = self
        self._children.append(child)

    def _resolve_properties(self, t: float) -> Dict[str, Any]:
        """Resolve all animated properties at time t."""
        props = {}

        # Get tweened values
        tween_values = self._tween_group.get_properties(t)
        props.update(tween_values)

        # Get keyframe values
        kf_values = self._animator.get_properties(t)
        props.update(kf_values)

        # Override with static values if not animated
        static_props = {
            "x": self.x,
            "y": self.y,
            "opacity": self.opacity,
            "rotation": self.rotation,
            "scale_x": self.scale_x,
            "scale_y": self.scale_y,
            "anchor_x": self.anchor_x,
            "anchor_y": self.anchor_y,
        }
        for key, value in static_props.items():
            if key not in props:
                props[key] = value

        return props

    def _apply_transform(
        self,
        image: Image.Image,
        props: Dict[str, Any],
    ) -> Image.Image:
        """Apply position, rotation, scale transforms."""
        w, h = image.size

        # Apply scale
        sx = props.get("scale_x", 1.0)
        sy = props.get("scale_y", 1.0)
        if sx != 1.0 or sy != 1.0:
            new_w = max(1, int(w * abs(sx)))
            new_h = max(1, int(h * abs(sy)))
            image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Apply rotation
        rotation = props.get("rotation", 0)
        if rotation != 0:
            image = image.rotate(
                -rotation,  # PIL rotates counter-clockwise
                resample=Image.Resampling.BICUBIC,
                expand=True,
                fillcolor=(0, 0, 0, 0),
            )

        # Apply opacity
        opacity = props.get("opacity", 1.0)
        if opacity < 1.0:
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            alpha = image.split()[3]
            alpha = alpha.point(lambda p: int(p * opacity))
            image.putalpha(alpha)

        return image

    def _composite_onto(
        self,
        layer_image: Image.Image,
        canvas_size: Tuple[int, int],
        props: Dict[str, Any],
    ) -> Image.Image:
        """Composite layer image onto a canvas at the correct position."""
        canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))

        x = int(props.get("x", self.x))
        y = int(props.get("y", self.y))

        # Handle anchor point
        anchor_x = props.get("anchor_x", 0.5)
        anchor_y = props.get("anchor_y", 0.5)
        lw, lh = layer_image.size
        offset_x = int(x - lw * anchor_x)
        offset_y = int(y - lh * anchor_y)

        # Paste with alpha
        if layer_image.mode == "RGBA":
            canvas.paste(layer_image, (offset_x, offset_y), layer_image)
        else:
            canvas.paste(layer_image, (offset_x, offset_y))

        return canvas

    @abstractmethod
    def _render_content(
        self,
        t: float,
        width: int,
        height: int,
        fps: int,
        frame_idx: int,
        props: Dict[str, Any],
    ) -> Optional[Image.Image]:
        """
        Render the layer's content. Must be implemented by subclasses.

        Returns:
            RGBA Image or None
        """
        pass

    def render(
        self,
        t: float,
        width: int,
        height: int,
        fps: int,
        frame_idx: int,
    ) -> Optional[Image.Image]:
        """
        Render this layer at normalized time t.

        Args:
            t: Normalized time (0-1)
            width: Canvas width
            height: Canvas height
            fps: Frames per second
            frame_idx: Current frame index

        Returns:
            RGBA Image composited onto canvas, or None if not visible
        """
        if not self.visible:
            return None

        # Resolve animated properties
        props = self._resolve_properties(t)

        # Render content
        content = self._render_content(t, width, height, fps, frame_idx, props)
        if content is None:
            return None

        # Apply transforms
        content = self._apply_transform(content, props)

        # Apply effects
        for effect in self._effects:
            content = effect.apply(content, t, frame_idx)

        # Apply filters
        for filter_func in self._filters:
            content = filter_func(content, t)

        # Composite onto canvas
        result = self._composite_onto(content, (width, height), props)

        # Render children
        for child in self._children:
            child_frame = child.render(t, width, height, fps, frame_idx)
            if child_frame is not None:
                result = Image.alpha_composite(result, child_frame)

        return result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', pos=({self.x},{self.y}))"
