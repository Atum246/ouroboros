"""
Particle System — Fire, snow, confetti, sparks, smoke, and custom particles.

Generates animated particle effects as layers.
"""

import math
import random
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image, ImageDraw
import numpy as np

from ouroboros.layers.base import Layer


class Particle:
    """A single particle."""

    def __init__(
        self,
        x: float, y: float,
        vx: float, vy: float,
        life: float, max_life: float,
        size: float, color: Tuple[int, int, int, int],
        gravity: float = 0, friction: float = 0,
        fade: bool = True, shrink: bool = True,
        shape: str = "circle",
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = max_life
        self.size = size
        self.color = color
        self.gravity = gravity
        self.friction = friction
        self.fade = fade
        self.shrink = shrink
        self.shape = shape
        self.alive = True

    def update(self, dt: float):
        """Update particle physics."""
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return

        self.vy += self.gravity * dt
        self.vx *= (1 - self.friction * dt)
        self.vy *= (1 - self.friction * dt)
        self.x += self.vx * dt
        self.y += self.vy * dt

    def render(self, image: Image.Image):
        """Draw particle on image."""
        if not self.alive:
            return

        life_ratio = self.life / self.max_life
        draw = ImageDraw.Draw(image)

        alpha = int(self.color[3] * life_ratio) if self.fade else self.color[3]
        size = self.size * life_ratio if self.shrink else self.size

        if size < 0.5 or alpha < 1:
            return

        color = (self.color[0], self.color[1], self.color[2], max(0, min(255, alpha)))
        x, y = int(self.x), int(self.y)
        s = int(size)

        if self.shape == "circle":
            draw.ellipse([x - s, y - s, x + s, y + s], fill=color)
        elif self.shape == "square":
            draw.rectangle([x - s, y - s, x + s, y + s], fill=color)
        elif self.shape == "star":
            points = []
            for i in range(10):
                angle = math.pi * i / 5 - math.pi / 2
                r = s if i % 2 == 0 else s * 0.5
                points.append((x + r * math.cos(angle), y + r * math.sin(angle)))
            draw.polygon(points, fill=color)


class ParticleSystem(Layer):
    """
    Particle system layer.

    Args:
        count: Number of particles
        emitter_x: Emitter X position
        emitter_y: Emitter Y position
        emit_width: Width of emission area
        emit_height: Height of emission area
        speed_min: Minimum particle speed
        speed_max: Maximum particle speed
        angle_min: Minimum emission angle (degrees)
        angle_max: Maximum emission angle (degrees)
        life_min: Minimum particle life (seconds)
        life_max: Maximum particle life (seconds)
        size_min: Minimum particle size
        size_max: Maximum particle size
        color: Particle color (or list of colors for random selection)
        gravity: Gravity force
        friction: Friction coefficient
        fade: Whether particles fade out
        shrink: Whether particles shrink
        shape: Particle shape ('circle', 'square', 'star')
        continuous: Whether to continuously emit particles
        seed: Random seed for reproducibility

    Presets:
        ParticleSystem.preset_fire(x, y)
        ParticleSystem.preset_snow(width, height)
        ParticleSystem.preset_confetti(width, height)
        ParticleSystem.preset_sparks(x, y)
        ParticleSystem.preset_smoke(x, y)
    """

    def __init__(
        self,
        count: int = 100,
        emitter_x: float = 400,
        emitter_y: float = 400,
        emit_width: float = 0,
        emit_height: float = 0,
        speed_min: float = 50,
        speed_max: float = 150,
        angle_min: float = 0,
        angle_max: float = 360,
        life_min: float = 1.0,
        life_max: float = 3.0,
        size_min: float = 2,
        size_max: float = 8,
        color: Any = (255, 200, 50, 255),
        gravity: float = 100,
        friction: float = 0.01,
        fade: bool = True,
        shrink: bool = True,
        shape: str = "circle",
        continuous: bool = True,
        seed: int = 42,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.count = count
        self.emitter_x = emitter_x
        self.emitter_y = emitter_y
        self.emit_width = emit_width
        self.emit_height = emit_height
        self.speed_min = speed_min
        self.speed_max = speed_max
        self.angle_min = angle_min
        self.angle_max = angle_max
        self.life_min = life_min
        self.life_max = life_max
        self.size_min = size_min
        self.size_max = size_max
        self.particle_color = color
        self.gravity = gravity
        self.friction = friction
        self.fade = fade
        self.shrink = shrink
        self.particle_shape = shape
        self.continuous = continuous
        self.seed = seed

        self._particles: List[Particle] = []
        self._rng = random.Random(seed)
        self._initialized = False

    def _parse_color(self, color: Any) -> Tuple[int, int, int, int]:
        if isinstance(color, (tuple, list)):
            if len(color) == 3:
                return (color[0], color[1], color[2], 255)
            return tuple(color)
        elif isinstance(color, str):
            color = color.lstrip("#")
            if len(color) == 6:
                return (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16), 255)
        return (255, 255, 255, 255)

    def _emit_particle(self) -> Particle:
        """Create a new particle."""
        x = self.emitter_x + self._rng.uniform(-self.emit_width / 2, self.emit_width / 2)
        y = self.emitter_y + self._rng.uniform(-self.emit_height / 2, self.emit_height / 2)

        angle = self._rng.uniform(self.angle_min, self.angle_max)
        speed = self._rng.uniform(self.speed_min, self.speed_max)
        rad = math.radians(angle)
        vx = math.cos(rad) * speed
        vy = math.sin(rad) * speed

        life = self._rng.uniform(self.life_min, self.life_max)
        size = self._rng.uniform(self.size_min, self.size_max)

        if isinstance(self.particle_color, list):
            color = self._parse_color(self._rng.choice(self.particle_color))
        else:
            color = self._parse_color(self.particle_color)

        return Particle(
            x=x, y=y, vx=vx, vy=vy,
            life=life, max_life=life,
            size=size, color=color,
            gravity=self.gravity, friction=self.friction,
            fade=self.fade, shrink=self.shrink,
            shape=self.particle_shape,
        )

    def _update_particles(self, dt: float):
        """Update all particles and emit new ones."""
        # Update existing
        for p in self._particles:
            p.update(dt)

        # Remove dead
        self._particles = [p for p in self._particles if p.alive]

        # Emit new
        if self.continuous:
            while len(self._particles) < self.count:
                self._particles.append(self._emit_particle())

    def _render_content(
        self, t, width, height, fps, frame_idx, props,
    ) -> Optional[Image.Image]:
        dt = 1.0 / max(fps, 1)

        if not self._initialized:
            # Initial burst
            for _ in range(self.count):
                self._particles.append(self._emit_particle())
            self._initialized = True

        self._update_particles(dt)

        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        for p in self._particles:
            p.render(img)

        return img

    # ─── Presets ─────────────────────────────────────────────────────

    @classmethod
    def preset_fire(cls, x: float = 400, y: float = 500, **kwargs) -> "ParticleSystem":
        """Fire effect preset."""
        return cls(
            emitter_x=x, emitter_y=y, emit_width=60, emit_height=10,
            count=80, speed_min=30, speed_max=100,
            angle_min=250, angle_max=290,
            life_min=0.5, life_max=1.5,
            size_min=3, size_max=12,
            color=[(255, 100, 0, 255), (255, 200, 0, 255), (255, 50, 0, 200)],
            gravity=-50, friction=0.02, shape="circle",
            **kwargs,
        )

    @classmethod
    def preset_snow(cls, width: int = 1920, height: int = 1080, **kwargs) -> "ParticleSystem":
        """Snow effect preset."""
        return cls(
            emitter_x=width / 2, emitter_y=-20, emit_width=width + 200, emit_height=10,
            count=150, speed_min=10, speed_max=40,
            angle_min=80, angle_max=100,
            life_min=3, life_max=8,
            size_min=2, size_max=6,
            color=(255, 255, 255, 200),
            gravity=30, friction=0.005, shape="circle",
            **kwargs,
        )

    @classmethod
    def preset_confetti(cls, width: int = 1920, height: int = 1080, **kwargs) -> "ParticleSystem":
        """Confetti effect preset."""
        return cls(
            emitter_x=width / 2, emitter_y=-20, emit_width=width, emit_height=10,
            count=200, speed_min=20, speed_max=80,
            angle_min=60, angle_max=120,
            life_min=2, life_max=5,
            size_min=4, size_max=10,
            color=[
                (255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255),
                (255, 255, 0, 255), (255, 0, 255, 255), (0, 255, 255, 255),
            ],
            gravity=80, friction=0.01, shape="square",
            **kwargs,
        )

    @classmethod
    def preset_sparks(cls, x: float = 400, y: float = 400, **kwargs) -> "ParticleSystem":
        """Sparks effect preset."""
        return cls(
            emitter_x=x, emitter_y=y, emit_width=20, emit_height=20,
            count=50, speed_min=100, speed_max=300,
            angle_min=0, angle_max=360,
            life_min=0.3, life_max=1.0,
            size_min=1, size_max=4,
            color=[(255, 255, 100, 255), (255, 200, 50, 255)],
            gravity=200, friction=0.03, shape="circle",
            **kwargs,
        )

    @classmethod
    def preset_smoke(cls, x: float = 400, y: float = 500, **kwargs) -> "ParticleSystem":
        """Smoke effect preset."""
        return cls(
            emitter_x=x, emitter_y=y, emit_width=40, emit_height=10,
            count=40, speed_min=10, speed_max=40,
            angle_min=260, angle_max=280,
            life_min=2, life_max=5,
            size_min=10, size_max=30,
            color=(150, 150, 150, 100),
            gravity=-20, friction=0.01, shape="circle",
            **kwargs,
        )
