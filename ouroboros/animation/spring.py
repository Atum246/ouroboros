"""
Spring Physics Animation.

Natural-feeling motion with damping, stiffness, and mass.
"""

import math
from typing import Optional


class Spring:
    """
    Spring physics simulation for natural motion.

    Args:
        stiffness: Spring stiffness (higher = faster, default 100)
        damping: Damping ratio (higher = less bounce, default 10)
        mass: Object mass (higher = slower, default 1)
        velocity: Initial velocity

    Example::

        spring = Spring(stiffness=120, damping=12)
        values = spring.animate(0, 100, duration=2, fps=30)
    """

    def __init__(
        self,
        stiffness: float = 100,
        damping: float = 10,
        mass: float = 1.0,
        velocity: float = 0.0,
    ):
        self.stiffness = stiffness
        self.damping = damping
        self.mass = mass
        self.velocity = velocity

    def step(
        self,
        current: float,
        target: float,
        dt: float,
    ) -> tuple:
        """
        Simulate one step of spring physics.

        Args:
            current: Current value
            target: Target value
            dt: Time step

        Returns:
            (new_value, new_velocity)
        """
        displacement = current - target
        spring_force = -self.stiffness * displacement
        damping_force = -self.damping * self.velocity
        acceleration = (spring_force + damping_force) / self.mass

        self.velocity += acceleration * dt
        new_value = current + self.velocity * dt

        return new_value, self.velocity

    def animate(
        self,
        start: float,
        end: float,
        duration: float,
        fps: int = 30,
    ) -> list:
        """
        Generate spring animation values.

        Args:
            start: Start value
            end: End value
            duration: Animation duration in seconds
            fps: Frames per second

        Returns:
            List of values for each frame
        """
        values = []
        current = start
        velocity = 0.0
        dt = 1.0 / fps
        total_frames = int(duration * fps)

        for _ in range(total_frames):
            values.append(current)
            current, velocity = self.step(current, end, dt)

        return values

    def animate_normalized(
        self,
        start: float,
        end: float,
        t: float,
    ) -> float:
        """
        Get spring value at normalized time t (0-1).

        Args:
            start: Start value
            end: End value
            t: Normalized time (0-1)

        Returns:
            Spring-interpolated value
        """
        # Approximate spring with normalized time
        # This gives a quick spring feel without full simulation
        if t <= 0:
            return start
        if t >= 1:
            return end

        # Damped sine wave approximation
        omega = math.sqrt(self.stiffness / self.mass)
        zeta = self.damping / (2 * math.sqrt(self.stiffness * self.mass))

        if zeta < 1:
            # Underdamped (bouncy)
            omega_d = omega * math.sqrt(1 - zeta ** 2)
            envelope = math.exp(-zeta * omega * t)
            oscillation = math.cos(omega_d * t) + (zeta * omega / omega_d) * math.sin(omega_d * t)
            spring_value = 1 - envelope * oscillation
        else:
            # Critically damped or overdamped
            spring_value = 1 - (1 + omega * t) * math.exp(-omega * t)

        return start + (end - start) * spring_value


# Preset springs
SPRING_GENTLE = Spring(stiffness=100, damping=15, mass=1)
SPRING_BOUNCY = Spring(stiffness=180, damping=8, mass=1)
SPRING_SNAPPY = Spring(stiffness=300, damping=20, mass=1)
SPRING_SLUGGISH = Spring(stiffness=50, damping=20, mass=2)
SPRING_WOBBLY = Spring(stiffness=120, damping=4, mass=1)
