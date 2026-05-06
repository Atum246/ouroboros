"""
Scene — A single segment of video.

A scene is a time-bounded section that produces layers via a function.
Scenes are composable and can be sequenced on a timeline.
"""

from typing import Callable, List, Optional, Any, TYPE_CHECKING
from PIL import Image

if TYPE_CHECKING:
    from ouroboros.core.composition import Composition


class Scene:
    """
    A scene in the composition.

    Args:
        func: Function that takes t (0-1) and returns list of layers
        duration: Duration in seconds
        name: Scene name
        composition: Parent composition (set automatically)
        transition_in: Transition to apply at scene start
        transition_out: Transition to apply at scene end
        transition_duration: Duration of transitions in seconds
    """

    def __init__(
        self,
        func: Callable,
        duration: float = 5.0,
        name: Optional[str] = None,
        composition: Optional["Composition"] = None,
        transition_in=None,
        transition_out=None,
        transition_duration: float = 0.5,
    ):
        self.func = func
        self.duration = duration
        self.name = name or func.__name__
        self.composition = composition
        self.transition_in = transition_in
        self.transition_out = transition_out
        self.transition_duration = transition_duration
        self._cached_layers: Optional[List] = None

    def frame_count(self, fps: int) -> int:
        """Calculate number of frames for this scene."""
        return max(1, int(self.duration * fps))

    def render(
        self,
        t: float,
        width: int,
        height: int,
        fps: int,
        frame_idx: int,
    ) -> Image.Image:
        """Render this scene at normalized time t."""
        # Get layers from scene function
        layers = self.func(t)

        if not layers:
            return Image.new("RGBA", (width, height), (0, 0, 0, 0))

        # Composite layers
        result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        from ouroboros.layers.base import Layer

        for layer in layers:
            if isinstance(layer, Layer):
                layer_frame = layer.render(t, width, height, fps, frame_idx)
                if layer_frame is not None:
                    if layer_frame.mode != "RGBA":
                        layer_frame = layer_frame.convert("RGBA")
                    result = Image.alpha_composite(result, layer_frame)

        return result

    def __repr__(self) -> str:
        return f"Scene('{self.name}', {self.duration}s)"
