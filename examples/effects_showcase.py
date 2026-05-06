"""
Example: Effects showcase.
"""

from ouroboros import *

comp = Composition(1920, 1080, 30, background="#0a0a0a")


@comp.scene(duration=4)
def blur_scene(t):
    bg = Solid(color="#1a1a2e")
    text = Text("Gaussian Blur", font_size=80, color="#e94560")
    blur_effect = GaussianBlur(radius=0)
    blur_effect.animate("radius", 0, 15, 0, 0.5, ease_in_out)
    blur_effect.animate("radius", 15, 0, 0.5, 1, ease_in_out)
    text.add_effect(blur_effect)
    return [bg, text]


@comp.scene(duration=4)
def glow_scene(t):
    bg = Solid(color="#0a0a0a")
    text = Text("Neon Glow ✨", font_size=100, color="#00ffcc")
    neon = Neon(color=(0, 255, 200), radius=5)
    text.add_effect(neon)
    return [bg, text]


@comp.scene(duration=4)
def glitch_scene(t):
    bg = Solid(color="#1a1a2e")
    text = Text("GLITCH", font_size=120, color="#ff0066")
    glitch = Glitch(intensity=0, seed=42)
    glitch.animate("intensity", 0, 0.8, 0, 0.3, ease_in)
    glitch.animate("intensity", 0.8, 0, 0.3, 0.6, ease_out)
    text.add_effect(glitch)
    return [bg, text]


@comp.scene(duration=4)
def vignette_scene(t):
    bg = Solid(color="#16213e")
    text = Text("Vignette Effect", font_size=80, color="#ffffff")
    vignette = Vignette(strength=0, size=0.5)
    vignette.animate("strength", 0, 0.8, 0, 1, ease_in_out)
    # Apply as global effect
    return [bg, text]


if __name__ == "__main__":
    comp.render("effects.mp4")
