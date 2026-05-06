"""
🐍 Ouroboros — Animated GIF Showcase
Creates a high-quality GIF that auto-plays on GitHub README.
"""

from ouroboros import *
from ouroboros.layers.shape import Star, Ellipse, Triangle
from ouroboros.effects.distortion import ChromaticAberration
import math

# Create a showcase GIF - compact but impressive
comp = Composition(800, 450, 15, background="#0a0a0a")


# ─── Frame 1: Logo splash ───────────────────────────────────
@comp.scene(duration=2, name="logo")
def logo(t):
    bg = Solid(color="#0a0a0a")

    # Pulsing ring
    ring = Circle(radius=80, fill="#00000000", stroke_width=4, stroke_color="#00ff88",
                  x=400, y=170)
    ring.animate("scale_x", 0, 1, 0, 0.5, ease_out_elastic)
    ring.animate("scale_y", 0, 1, 0, 0.5, ease_out_elastic)

    # Title
    title = Text("OUROBOROS", font_size=64, color="#00ff88", x=400, y=300)
    title.animate("opacity", 0, 1, 0.3, 0.8, ease_out)
    title.animate("y", 330, 300, 0.3, 1, ease_out_back)

    sub = Text("Python Video Framework", font_size=20, color="#ffffff80", x=400, y=360)
    sub.animate("opacity", 0, 1, 0.6, 1.2, ease_out)

    sparks = ParticleSystem.preset_sparks(400, 170)

    return [bg, sparks, ring, title, sub]


# ─── Frame 2: Code demo ─────────────────────────────────────
@comp.scene(duration=2.5, name="code")
def code(t):
    bg = Solid(color="#0d1117")

    # Code window
    window = Rectangle(rect_width=600, rect_height=300, fill="#161b22",
                      corner_radius=10, stroke_width=1, stroke_color="#30363d",
                      x=400, y=225)

    # Window dots
    dot1 = Circle(radius=6, fill="#ff5f56", x=140, y=100)
    dot2 = Circle(radius=6, fill="#ffbd2e", x=160, y=100)
    dot3 = Circle(radius=6, fill="#27c93f", x=180, y=100)

    # Code text
    code = Text('comp = Composition(1920, 1080, 30)\n\n@comp.scene(duration=5)\ndef intro(t):\n    bg = Solid(color="#1a1a2e")\n    title = Text("Hello! 🐍")\n    title.animate("opacity", 0, 1)\n    return [bg, title]\n\ncomp.render("output.mp4")',
               font_size=14, color="#e6edf3", x=400, y=225, font="monospace")
    code.animate("opacity", 0, 1, 0, 0.3, ease_out)

    # Output preview popping in
    preview = Rectangle(rect_width=200, rect_height=112, fill="#1a1a2e",
                       corner_radius=6, stroke_width=2, stroke_color="#00ff88",
                       x=400, y=225)
    preview.animate("opacity", 0, 1, 1.5, 2, ease_out)
    preview.animate("scale_x", 0.3, 1, 1.5, 2, ease_out_back)
    preview.animate("scale_y", 0.3, 1, 1.5, 2, ease_out_back)

    check = Text("✅ rendered!", font_size=18, color="#00ff88", x=400, y=300)
    check.animate("opacity", 0, 1, 1.8, 2.2, ease_out)

    return [bg, window, dot1, dot2, dot3, code, preview, check]


# ─── Frame 3: Effects showcase ───────────────────────────────
@comp.scene(duration=2.5, name="effects")
def effects(t):
    bg = Solid(color="#0a0a0a")

    header = Text("25+ Built-in Effects", font_size=28, color="#ffffff", x=400, y=50)
    header.animate("opacity", 0, 1, 0, 0.3, ease_out)

    # Neon text
    neon = Text("NEON", font_size=52, color="#00ffcc", x=200, y=180)
    neon_fx = Neon(color=(0, 255, 200), radius=6)
    neon.add_effect(neon_fx)
    neon.animate("opacity", 0, 1, 0.2, 0.6, ease_out)

    # Glitch text
    glitch = Text("GLITCH", font_size=52, color="#ff0066", x=600, y=180)
    glitch_fx = Glitch(intensity=0.4, seed=42)
    glitch.add_effect(glitch_fx)
    glitch.animate("opacity", 0, 1, 0.3, 0.7, ease_out)

    # Blur text
    blur_txt = Text("BLUR", font_size=52, color="#ffd700", x=200, y=320)
    blur_fx = GaussianBlur(radius=max(0, 8 * (1 - t)))
    blur_txt.add_effect(blur_fx)
    blur_txt.animate("opacity", 0, 1, 0.4, 0.8, ease_out)

    # Particles text
    particles_txt = Text("PARTICLES", font_size=52, color="#ff6b6b", x=600, y=320)
    particles_txt.animate("opacity", 0, 1, 0.5, 0.9, ease_out)

    return [bg, header, neon, glitch, blur_txt, particles_txt]


# ─── Frame 4: Particles ──────────────────────────────────────
@comp.scene(duration=2.5, name="particles")
def particles(t):
    bg = Solid(color="#0a0a0a")

    header = Text("Particle Systems", font_size=28, color="#ffffff", x=400, y=50)
    header.animate("opacity", 0, 1, 0, 0.3, ease_out)

    fire = ParticleSystem.preset_fire(200, 380)
    snow = ParticleSystem.preset_snow(800, 450)
    confetti = ParticleSystem.preset_confetti(800, 450)

    fire_label = Text("🔥 Fire", font_size=18, color="#ff6600", x=200, y=80)
    snow_label = Text("❄️ Snow", font_size=18, color="#88ccff", x=400, y=80)
    conf_label = Text("🎉 Confetti", font_size=18, color="#ffd700", x=600, y=80)

    return [bg, fire, snow, confetti, header, fire_label, snow_label, conf_label]


# ─── Frame 5: Shapes & animation ─────────────────────────────
@comp.scene(duration=2.5, name="shapes")
def shapes(t):
    bg = Solid(color="#0d1117")

    header = Text("Shapes & Animation", font_size=28, color="#ffffff", x=400, y=50)
    header.animate("opacity", 0, 1, 0, 0.3, ease_out)

    # Rotating star
    star = Star(outer_radius=50, inner_radius=25, points=5, fill="#ffd700",
               x=400, y=250)
    star.animate("rotation", 0, 360, 0, 1, linear)

    # Bouncing circles
    colors = ["#e94560", "#00ff88", "#4ecdc4", "#ff6b6b"]
    for i, color in enumerate(colors):
        angle = (t + i / 4) * math.pi * 2
        cx = 400 + 150 * math.cos(angle)
        cy = 250 + 100 * math.sin(angle)
        c = Circle(radius=20, fill=color, x=cx, y=cy)

    # Pulsing rectangle
    rect = Rectangle(rect_width=80, rect_height=80, fill="#e9456030",
                    corner_radius=10, stroke_width=2, stroke_color="#e94560",
                    x=400, y=250)
    rect.animate("scale_x", 0.8, 1.3, 0, 0.5, ease_in_out)
    rect.animate("scale_x", 1.3, 0.8, 0.5, 1, ease_in_out)
    rect.animate("scale_y", 0.8, 1.3, 0, 0.5, ease_in_out)
    rect.animate("scale_y", 1.3, 0.8, 0.5, 1, ease_in_out)

    return [bg, header, star, rect]


# ─── Frame 6: Social presets ─────────────────────────────────
@comp.scene(duration=2, name="presets")
def presets(t):
    bg = Solid(color="#0d1117")

    header = Text("13 Social Presets", font_size=28, color="#ffffff", x=400, y=50)
    header.animate("opacity", 0, 1, 0, 0.3, ease_out)

    platforms = [
        ("YouTube", "#ff0000"),
        ("TikTok", "#00f2ea"),
        ("Instagram", "#e1306c"),
        ("Twitter", "#1da1f2"),
        ("LinkedIn", "#0077b5"),
        ("Facebook", "#1877f2"),
    ]

    items = []
    for i, (name, color) in enumerate(platforms):
        col = i % 3
        row = i // 3
        x = 180 + col * 220
        y = 180 + row * 160

        card = Rectangle(rect_width=180, rect_height=100, fill=color,
                        corner_radius=10, x=x, y=y)
        card.animate("opacity", 0, 1, i * 0.1, i * 0.1 + 0.3, ease_out)
        card.animate("scale_x", 0, 1, i * 0.1, i * 0.1 + 0.3, ease_out_back)
        card.animate("scale_y", 0, 1, i * 0.1, i * 0.1 + 0.3, ease_out_back)
        items.append(card)

        label = Text(name, font_size=18, color="#ffffff", x=x, y=y)
        label.animate("opacity", 0, 1, i * 0.1 + 0.1, i * 0.1 + 0.4, ease_out)
        items.append(label)

    return [bg, header] + items


# ─── Frame 7: Finale ─────────────────────────────────────────
@comp.scene(duration=2.5, name="finale")
def finale(t):
    bg = Solid(color="#0a0a0a")

    title = Text("OUROBOROS", font_size=80, color="#00ff88", x=400, y=180)
    title.animate("opacity", 0, 1, 0, 0.4, ease_out)
    title.animate("scale_x", 0.5, 1, 0, 0.6, ease_out_elastic)
    title.animate("scale_y", 0.5, 1, 0, 0.6, ease_out_elastic)

    tagline = Text("pip install ouroboros", font_size=24, color="#ffd700", x=400, y=280)
    tagline.animate("opacity", 0, 1, 0.4, 0.8, ease_out)

    github = Text("github.com/Atum246/ouroboros", font_size=16, color="#4ecdc4", x=400, y=330)
    github.animate("opacity", 0, 1, 0.6, 1, ease_out)

    confetti = ParticleSystem.preset_confetti(800, 450)

    return [bg, confetti, title, tagline, github]


# ─── Render as GIF ───────────────────────────────────────────
if __name__ == "__main__":
    print("🐍 Rendering Ouroboros GIF showcase...")
    print()
    comp.render("showcase.gif", progress=True)
    print()
    print("✅ GIF showcase complete!")
