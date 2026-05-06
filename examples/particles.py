"""
Example: Particle effects showcase.
"""

from ouroboros import *

comp = Composition(1920, 1080, 30, background="#0a0a0a")


@comp.scene(duration=5)
def fire_scene(t):
    bg = Solid(color="#0a0a0a")
    fire = ParticleSystem.preset_fire(960, 900)
    label = Text("🔥 Fire", font_size=60, color="#ff6600", x=960, y=100)
    return [bg, fire, label]


@comp.scene(duration=5)
def snow_scene(t):
    bg = Solid(color="#1a1a2e")
    snow = ParticleSystem.preset_snow(1920, 1080)
    label = Text("❄️ Snow", font_size=60, color="#ffffff", x=960, y=100)
    return [bg, snow, label]


@comp.scene(duration=5)
def confetti_scene(t):
    bg = Solid(color="#16213e")
    confetti = ParticleSystem.preset_confetti(1920, 1080)
    label = Text("🎉 Confetti", font_size=60, color="#ffd700", x=960, y=100)
    return [bg, confetti, label]


@comp.scene(duration=5)
def sparks_scene(t):
    bg = Solid(color="#0a0a0a")
    sparks = ParticleSystem.preset_sparks(960, 540)
    label = Text("⚡ Sparks", font_size=60, color="#ffff00", x=960, y=100)
    return [bg, sparks, label]


if __name__ == "__main__":
    comp.render("particles.mp4")
