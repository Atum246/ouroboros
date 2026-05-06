"""
Example: Animated shapes with effects.
"""

from ouroboros import *

comp = Composition(1920, 1080, 30, background="#0a0a0a")


@comp.scene(duration=6)
def shapes(t):
    bg = Solid(color="#0a0a0a")

    # Animated circle
    circle = Circle(radius=60, fill="#e94560", x=300, y=540)
    circle.animate("x", 300, 1600, 0, 1, ease_in_out)
    circle.animate("y", 540, 300, 0, 0.5, ease_out_bounce)
    circle.animate("y", 300, 540, 0.5, 1, ease_in_bounce)

    # Rotating rectangle
    rect = Rectangle(rect_width=120, rect_height=80, fill="#0f3460", corner_radius=10,
                     x=960, y=540)
    rect.animate("rotation", 0, 360, 0, 1, linear)

    # Pulsing star
    star = Star(outer_radius=50, inner_radius=25, points=5, fill="#ffd700",
                x=1600, y=540)
    star.animate("scale_x", 1, 1.5, 0, 0.5, ease_in_out)
    star.animate("scale_x", 1.5, 1, 0.5, 1, ease_in_out)
    star.animate("scale_y", 1, 1.5, 0, 0.5, ease_in_out)
    star.animate("scale_y", 1.5, 1, 0.5, 1, ease_in_out)

    return [bg, circle, rect, star]


if __name__ == "__main__":
    comp.render("shapes.mp4")
