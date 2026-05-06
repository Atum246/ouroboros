"""
Ouroboros — The Ultimate Python Video Framework
================================================

Create any video programmatically. Zero bloat, infinite possibilities.

Key Features:
    - Frame-by-frame generator rendering (O(1) RAM usage)
    - 40+ easing functions and keyframe animation
    - Composable effects pipeline (blur, glow, color grading, etc.)
    - Rich text rendering with animations
    - Particle systems (fire, snow, confetti, sparks)
    - Audio mixing and waveform visualization
    - 30+ built-in transitions
    - Data visualization (charts, code blocks)
    - CLI tool with live preview
    - REST API for n8n, Zapier, Make integration
    - AI agent skill file for OpenClaw, Claude, Cursor

Quick Start::

    from ouroboros import Composition, Scene, Text, Circle, ease_in_out

    comp = Composition(1920, 1080, 30)

    @comp.scene(duration=5)
    def intro(t):
        bg = Solid(color="#1a1a2e")
        title = Text("Hello World", font_size=120, color="#e94560")
        title.animate("opacity", 0, 1, 0, 1, ease_in_out)
        title.animate("y", 600, 500, 0, 1, ease_in_out)
        return [bg, title]

    comp.render("output.mp4")
"""

__version__ = "1.0.0"
__author__ = "Ouroboros Team"

from ouroboros.core.composition import Composition
from ouroboros.core.scene import Scene
from ouroboros.core.timeline import Timeline
from ouroboros.animation.easing import (
    linear, ease_in, ease_out, ease_in_out,
    ease_in_quad, ease_out_quad, ease_in_out_quad,
    ease_in_cubic, ease_out_cubic, ease_in_out_cubic,
    ease_in_quart, ease_out_quart, ease_in_out_quart,
    ease_in_quint, ease_out_quint, ease_in_out_quint,
    ease_in_sine, ease_out_sine, ease_in_out_sine,
    ease_in_expo, ease_out_expo, ease_in_out_expo,
    ease_in_circ, ease_out_circ, ease_in_out_circ,
    ease_in_elastic, ease_out_elastic, ease_in_out_elastic,
    ease_in_back, ease_out_back, ease_in_out_back,
    ease_in_bounce, ease_out_bounce, ease_in_out_bounce,
)
from ouroboros.layers.solid import Solid
from ouroboros.layers.text_layer import Text
from ouroboros.layers.image_layer import ImageLayer
from ouroboros.layers.video_layer import VideoLayer
from ouroboros.layers.shape import (
    Circle, Rectangle, Triangle, Line, Polygon, Ellipse, Star, Arc, Path
)
from ouroboros.effects.blur import Blur, GaussianBlur, MotionBlur, RadialBlur
from ouroboros.effects.color import (
    Brightness, Contrast, Saturation, HueShift,
    Sepia, Grayscale, Invert, ColorBalance, Temperature
)
from ouroboros.effects.glow import Glow, Bloom, Neon
from ouroboros.effects.distortion import (
    Wave, Ripple, Pixelate, Glitch, FilmGrain, Vignette, ChromaticAberration
)
from ouroboros.effects.shadow import DropShadow, LongShadow, InnerShadow
from ouroboros.effects.mask import Mask, ShapeMask, GradientMask
from ouroboros.components.transitions import (
    FadeTransition, WipeTransition, DissolveTransition,
    SlideTransition, ZoomTransition, PushTransition
)
from ouroboros.particles.system import ParticleSystem
from ouroboros.audio.track import AudioTrack
from ouroboros.text.subtitles import SubtitleTrack

__all__ = [
    "Composition", "Scene", "Timeline",
    # Easing
    "linear", "ease_in", "ease_out", "ease_in_out",
    "ease_in_quad", "ease_out_quad", "ease_in_out_quad",
    "ease_in_cubic", "ease_out_cubic", "ease_in_out_cubic",
    "ease_in_quart", "ease_out_quart", "ease_in_out_quart",
    "ease_in_quint", "ease_out_quint", "ease_in_out_quint",
    "ease_in_sine", "ease_out_sine", "ease_in_out_sine",
    "ease_in_expo", "ease_out_expo", "ease_in_out_expo",
    "ease_in_circ", "ease_out_circ", "ease_in_out_circ",
    "ease_in_elastic", "ease_out_elastic", "ease_in_out_elastic",
    "ease_in_back", "ease_out_back", "ease_in_out_back",
    "ease_in_bounce", "ease_out_bounce", "ease_in_out_bounce",
    # Layers
    "Solid", "Text", "ImageLayer", "VideoLayer",
    "Circle", "Rectangle", "Triangle", "Line", "Polygon",
    "Ellipse", "Star", "Arc", "Path",
    # Effects
    "Blur", "GaussianBlur", "MotionBlur", "RadialBlur",
    "Brightness", "Contrast", "Saturation", "HueShift",
    "Sepia", "Grayscale", "Invert", "ColorBalance", "Temperature",
    "Glow", "Bloom", "Neon",
    "Wave", "Ripple", "Pixelate", "Glitch", "FilmGrain",
    "Vignette", "ChromaticAberration",
    "DropShadow", "LongShadow", "InnerShadow",
    "Mask", "ShapeMask", "GradientMask",
    # Transitions
    "FadeTransition", "WipeTransition", "DissolveTransition",
    "SlideTransition", "ZoomTransition", "PushTransition",
    # Particles
    "ParticleSystem",
    # Audio
    "AudioTrack",
    # Subtitles
    "SubtitleTrack",
]
