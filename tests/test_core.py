"""
Tests for Ouroboros core functionality.
"""

import os
import sys
import tempfile
import pytest
from PIL import Image

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ouroboros import (
    Composition, Scene, Solid, Text, Circle, Rectangle,
    ease_in_out, ease_out_bounce, linear,
    GaussianBlur, Brightness, Contrast, Sepia, Grayscale,
    Glow, Neon, Glitch, FilmGrain, Vignette,
    ParticleSystem,
)


class TestComposition:
    """Test Composition class."""

    def test_create(self):
        comp = Composition(1920, 1080, 30)
        assert comp.width == 1920
        assert comp.height == 1080
        assert comp.fps == 30

    def test_scene_decorator(self):
        comp = Composition(1920, 1080, 30)

        @comp.scene(duration=3)
        def test_scene(t):
            return [Solid(color="#000000")]

        assert len(comp._scenes) == 1
        assert comp.duration == 3.0

    def test_multiple_scenes(self):
        comp = Composition(1920, 1080, 30)

        @comp.scene(duration=2)
        def scene1(t):
            return [Solid(color="#ff0000")]

        @comp.scene(duration=3)
        def scene2(t):
            return [Solid(color="#00ff00")]

        assert len(comp._scenes) == 2
        assert comp.duration == 5.0
        assert comp.total_frames == 150

    def test_render_frame(self):
        comp = Composition(640, 480, 30)

        @comp.scene(duration=1)
        def test(t):
            return [Solid(color="#ff0000")]

        frame = comp.render_frame(0)
        assert isinstance(frame, Image.Image)
        assert frame.size == (640, 480)

    def test_render_gif(self):
        comp = Composition(320, 240, 10)

        @comp.scene(duration=1)
        def test(t):
            return [Solid(color="#ff0000")]

        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as f:
            output = f.name

        try:
            comp.render(output, progress=False)
            assert os.path.exists(output)
            assert os.path.getsize(output) > 0
        finally:
            os.unlink(output)

    def test_repr(self):
        comp = Composition(1920, 1080, 30)
        assert "1920" in repr(comp)
        assert "1080" in repr(comp)
        assert "30" in repr(comp)


class TestLayers:
    """Test layer classes."""

    def test_solid(self):
        solid = Solid(color="#ff0000")
        frame = solid.render(0.5, 640, 480, 30, 15)
        assert isinstance(frame, Image.Image)
        assert frame.mode == "RGBA"

    def test_text(self):
        text = Text("Hello", font_size=48, color="#ffffff")
        frame = text.render(0.5, 640, 480, 30, 15)
        assert isinstance(frame, Image.Image)

    def test_circle(self):
        circle = Circle(radius=50, fill="#ff0000")
        frame = circle.render(0.5, 640, 480, 30, 15)
        assert isinstance(frame, Image.Image)

    def test_rectangle(self):
        rect = Rectangle(rect_width=100, rect_height=80, fill="#00ff00", corner_radius=10)
        frame = rect.render(0.5, 640, 480, 30, 15)
        assert isinstance(frame, Image.Image)

    def test_text_animation(self):
        text = Text("Fade", font_size=48)
        text.animate("opacity", 0, 1, 0, 1, ease_in_out)

        frame0 = text.render(0, 640, 480, 30, 0)
        frame1 = text.render(1, 640, 480, 30, 29)
        assert frame0 is not None
        assert frame1 is not None

    def test_shape_layer(self):
        from ouroboros.layers.shape import Star, Ellipse, Triangle
        star = Star(outer_radius=50, inner_radius=25, points=5, fill="#ffd700")
        frame = star.render(0.5, 640, 480, 30, 15)
        assert isinstance(frame, Image.Image)

        ellipse = Ellipse(radius_x=60, radius_y=40, fill="#ff0000")
        frame = ellipse.render(0.5, 640, 480, 30, 15)
        assert isinstance(frame, Image.Image)

        triangle = Triangle(size=100, fill="#00ff00")
        frame = triangle.render(0.5, 640, 480, 30, 15)
        assert isinstance(frame, Image.Image)


class TestEasing:
    """Test easing functions."""

    def test_linear(self):
        assert linear(0) == 0
        assert linear(0.5) == 0.5
        assert linear(1) == 1

    def test_ease_in_out(self):
        assert ease_in_out(0) == 0
        assert ease_in_out(1) == 1
        assert ease_in_out(0.5) > 0.4  # Should be near 0.5

    def test_ease_out_bounce(self):
        assert ease_out_bounce(0) == 0
        assert ease_out_bounce(1) == 1
        # Bounce should have values > 1 at some point
        values = [ease_out_bounce(t / 100) for t in range(101)]
        assert all(0 <= v <= 1.01 for v in values)


class TestEffects:
    """Test effects."""

    def test_gaussian_blur(self):
        img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
        blur = GaussianBlur(radius=5)
        result = blur.apply(img, 0.5, 15)
        assert isinstance(result, Image.Image)
        assert result.size == img.size

    def test_brightness(self):
        img = Image.new("RGBA", (100, 100), (128, 128, 128, 255))
        bright = Brightness(factor=1.5)
        result = bright.apply(img, 0.5, 15)
        assert isinstance(result, Image.Image)

    def test_sepia(self):
        img = Image.new("RGBA", (100, 100), (128, 128, 128, 255))
        sepia = Sepia()
        result = sepia.apply(img, 0.5, 15)
        assert isinstance(result, Image.Image)

    def test_grayscale(self):
        img = Image.new("RGBA", (100, 100), (128, 64, 192, 255))
        gray = Grayscale()
        result = gray.apply(img, 0.5, 15)
        assert isinstance(result, Image.Image)

    def test_glitch(self):
        img = Image.new("RGBA", (100, 100), (128, 128, 128, 255))
        glitch = Glitch(intensity=0.5, seed=42)
        result = glitch.apply(img, 0.5, 15)
        assert isinstance(result, Image.Image)

    def test_vignette(self):
        img = Image.new("RGBA", (100, 100), (128, 128, 128, 255))
        vig = Vignette(strength=0.5)
        result = vig.apply(img, 0.5, 15)
        assert isinstance(result, Image.Image)

    def test_film_grain(self):
        img = Image.new("RGBA", (100, 100), (128, 128, 128, 255))
        grain = FilmGrain(amount=20)
        result = grain.apply(img, 0.5, 15)
        assert isinstance(result, Image.Image)


class TestAnimation:
    """Test animation system."""

    def test_keyframe(self):
        from ouroboros.animation.keyframe import Keyframe, Animation
        anim = Animation("x", [
            Keyframe(0, 0),
            Keyframe(0.5, 100, ease_in_out),
            Keyframe(1, 0),
        ])
        assert anim.get_value(0) == 0
        assert anim.get_value(1) == 0
        assert anim.get_value(0.5) == 100

    def test_tween(self):
        from ouroboros.animation.tween import Tween
        tween = Tween(0, 100, 0, 1, ease_in_out)
        assert tween.get_value(0) == 0
        assert tween.get_value(1) == 100
        assert 40 < tween.get_value(0.5) < 60

    def test_spring(self):
        from ouroboros.animation.spring import Spring
        spring = Spring(stiffness=120, damping=12)
        values = spring.animate(0, 100, duration=1, fps=30)
        assert len(values) == 30
        assert values[0] == 0
        # Should approach 100
        assert abs(values[-1] - 100) < 10


class TestParticles:
    """Test particle system."""

    def test_create(self):
        ps = ParticleSystem(count=50, emitter_x=400, emitter_y=400)
        frame = ps.render(0.5, 800, 600, 30, 15)
        assert isinstance(frame, Image.Image)

    def test_presets(self):
        fire = ParticleSystem.preset_fire(400, 500)
        assert fire is not None

        snow = ParticleSystem.preset_snow(1920, 1080)
        assert snow is not None

        confetti = ParticleSystem.preset_confetti(1920, 1080)
        assert confetti is not None


class TestTimeline:
    """Test timeline system."""

    def test_timeline(self):
        from ouroboros.core.timeline import Timeline
        from ouroboros.core.scene import Scene

        tl = Timeline()
        assert len(tl) == 0
        assert tl.duration == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
