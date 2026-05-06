"""
🐍 Ouroboros — Official Trailer
Showcasing the full power of the framework.
"""

from ouroboros import *
from ouroboros.layers.shape import Star, Ellipse, Triangle, Polygon
from ouroboros.effects.distortion import ChromaticAberration

comp = Composition(1920, 1080, 30, background="#0a0a0a")


# ═══════════════════════════════════════════════════════════
# SCENE 1: Logo Reveal with particles ✨
# ═══════════════════════════════════════════════════════════
@comp.scene(duration=5, name="logo_reveal")
def scene_logo(t):
    bg = Solid(color="#0a0a0a")

    # Ouroboros symbol — pulsing circle
    ring = Circle(radius=150, fill="#00000000", stroke_width=6, stroke_color="#00ff88",
                  x=960, y=440)
    ring.animate("scale_x", 0, 1, 0, 0.6, ease_out_elastic)
    ring.animate("scale_y", 0, 1, 0, 0.6, ease_out_elastic)
    ring.animate("opacity", 0, 1, 0, 0.3, ease_out)

    # Inner glow
    inner = Circle(radius=120, fill="#00ff8830", x=960, y=440)
    inner.animate("scale_x", 0, 1, 0.1, 0.7, ease_out_back)
    inner.animate("scale_y", 0, 1, 0.1, 0.7, ease_out_back)
    inner.animate("opacity", 0, 0.6, 0.1, 0.5, ease_out)

    # Title text
    title = Text("OUROBOROS", font_size=140, color="#00ff88", x=960, y=680)
    title.animate("opacity", 0, 1, 0.4, 0.9, ease_out)
    title.animate("y", 720, 680, 0.4, 1, ease_out_back)

    # Subtitle
    sub = Text("The Ultimate Python Video Framework", font_size=36, color="#ffffff80",
               x=960, y=770)
    sub.animate("opacity", 0, 1, 0.7, 1.2, ease_out)

    # Spark particles
    sparks = ParticleSystem.preset_sparks(960, 440)

    return [bg, sparks, ring, inner, title, sub]


# ═══════════════════════════════════════════════════════════
# SCENE 2: Feature cards flying in 📦
# ═══════════════════════════════════════════════════════════
@comp.scene(duration=5, name="features")
def scene_features(t):
    bg = Solid(color="#0d1117")

    # Header
    header = Text("What can it do?", font_size=60, color="#ffffff", x=960, y=80)
    header.animate("opacity", 0, 1, 0, 0.4, ease_out)

    # Feature cards as rectangles with text
    features = [
        ("🎬 Any Video", "#e94560", 0),
        ("✨ 25+ Effects", "#00ff88", 0.1),
        ("🎯 40+ Easings", "#4ecdc4", 0.2),
        ("🌟 Particles", "#ffd700", 0.3),
        ("🔊 Audio", "#ff6b6b", 0.4),
        ("📝 Subtitles", "#a8e6cf", 0.5),
    ]

    cards = []
    for i, (label, color, delay) in enumerate(features):
        col = i % 3
        row = i // 3
        x = 360 + col * 400
        y = 280 + row * 280

        card = Rectangle(rect_width=320, rect_height=200, fill="#161b22",
                        corner_radius=16, stroke_width=2, stroke_color=color,
                        x=x, y=y)
        card.animate("opacity", 0, 1, delay, delay + 0.4, ease_out)
        card.animate("y", y + 100, y, delay, delay + 0.5, ease_out_back)
        cards.append(card)

        txt = Text(label, font_size=36, color=color, x=x, y=y - 10)
        txt.animate("opacity", 0, 1, delay + 0.2, delay + 0.6, ease_out)
        cards.append(txt)

    return [bg, header] + cards


# ═══════════════════════════════════════════════════════════
# SCENE 3: Code example morphing 💻
# ═══════════════════════════════════════════════════════════
@comp.scene(duration=6, name="code_demo")
def scene_code(t):
    bg = Solid(color="#0d1117")

    # Code background
    code_bg = Rectangle(rect_width=1400, rect_height=600, fill="#161b22",
                       corner_radius=12, stroke_width=1, stroke_color="#30363d",
                       x=960, y=540)

    # Code text with typewriter effect
    code_lines = [
        'from ouroboros import *',
        '',
        'comp = Composition(1920, 1080, 30)',
        '',
        '@comp.scene(duration=5)',
        'def intro(t):',
        '    bg = Solid(color="#1a1a2e")',
        '    title = Text("Hello! 🐍", font_size=120)',
        '    title.animate("opacity", 0, 1, 0, 0.5)',
        '    return [bg, title]',
        '',
        'comp.render("output.mp4")',
    ]

    # Show code appearing line by line
    code = Text("\n".join(code_lines), font_size=28, color="#e6edf3",
                x=960, y=540, font="monospace")

    # Typewriter: reveal progressively
    total_chars = sum(len(line) for line in code_lines)
    progress = min(1.0, t * 1.8)  # Speed of typing
    code.animate("opacity", 0, 1, 0, 0.2, ease_out)

    # Syntax highlight hints via colored overlays
    from_text = Text("from", font_size=28, color="#ff7b72", x=700, y=290)
    import_text = Text("import", font_size=28, color="#ff7b72", x=830, y=290)
    star_text = Text("*", font_size=28, color="#ffa657", x=920, y=290)

    for txt in [from_text, import_text, star_text]:
        txt.animate("opacity", 0, 1, 0.3, 0.6, ease_out)

    # Output preview
    preview = Rectangle(rect_width=400, rect_height=225, fill="#1a1a2e",
                       corner_radius=8, stroke_width=2, stroke_color="#00ff88",
                       x=960, y=540)
    preview.animate("opacity", 0, 1, 3.5, 4.5, ease_out)
    preview.animate("scale_x", 0.5, 1, 3.5, 4.5, ease_out_back)
    preview.animate("scale_y", 0.5, 1, 3.5, 4.5, ease_out_back)

    output_text = Text("output.mp4 ✅", font_size=32, color="#00ff88", x=960, y=540)
    output_text.animate("opacity", 0, 1, 4.0, 4.8, ease_out)

    return [bg, code_bg, code, from_text, import_text, star_text, preview, output_text]


# ═══════════════════════════════════════════════════════════
# SCENE 4: Effects showcase 🌈
# ═══════════════════════════════════════════════════════════
@comp.scene(duration=6, name="effects")
def scene_effects(t):
    bg = Solid(color="#0a0a0a")

    header = Text("Built-in Effects", font_size=60, color="#ffffff", x=960, y=80)
    header.animate("opacity", 0, 1, 0, 0.3, ease_out)

    # Neon text
    neon_text = Text("NEON", font_size=100, color="#00ffcc", x=480, y=350)
    neon = Neon(color=(0, 255, 200), radius=8)
    neon_text.add_effect(neon)
    neon_text.animate("opacity", 0, 1, 0.2, 0.6, ease_out)

    # Glitch text
    glitch_text = Text("GLITCH", font_size=100, color="#ff0066", x=1440, y=350)
    glitch = Glitch(intensity=0, seed=42)
    # Pulse the glitch
    if t > 0.3 and t < 0.8:
        glitch.intensity = 0.6
    elif t > 0.8:
        glitch.intensity = max(0, 0.6 - (t - 0.8) * 2)
    glitch_text.add_effect(glitch)
    glitch_text.animate("opacity", 0, 1, 0.3, 0.7, ease_out)

    # Blur text
    blur_text = Text("BLUR", font_size=100, color="#ffd700", x=480, y=650)
    blur_r = 15 * (1 - t) if t > 0.4 else 0
    blur_effect = GaussianBlur(radius=max(0, blur_r))
    blur_text.add_effect(blur_effect)
    blur_text.animate("opacity", 0, 1, 0.4, 0.8, ease_out)

    # Vignette effect text
    vig_text = Text("VIGNETTE", font_size=100, color="#ff6b6b", x=1440, y=650)
    vig_text.animate("opacity", 0, 1, 0.5, 0.9, ease_out)

    # Global vignette
    vig = Vignette(strength=0, size=0.4)
    vig.animate("strength", 0, 0.7, 0.5, 1, ease_in_out)

    return [bg, header, neon_text, glitch_text, blur_text, vig_text]


# ═══════════════════════════════════════════════════════════
# SCENE 5: Particle explosion 🎆
# ═══════════════════════════════════════════════════════════
@comp.scene(duration=5, name="particles")
def scene_particles(t):
    bg = Solid(color="#0a0a0a")

    header = Text("Particle Systems", font_size=60, color="#ffffff", x=960, y=80)
    header.animate("opacity", 0, 1, 0, 0.3, ease_out)

    # Fire on left
    fire = ParticleSystem.preset_fire(400, 850)
    fire_label = Text("🔥 Fire", font_size=36, color="#ff6600", x=400, y=180)
    fire_label.animate("opacity", 0, 1, 0.2, 0.5, ease_out)

    # Snow in center
    snow = ParticleSystem.preset_snow(1920, 1080)
    snow_label = Text("❄️ Snow", font_size=36, color="#88ccff", x=960, y=180)
    snow_label.animate("opacity", 0, 1, 0.3, 0.6, ease_out)

    # Confetti on right
    confetti = ParticleSystem.preset_confetti(1920, 1080)
    confetti_label = Text("🎉 Confetti", font_size=36, color="#ffd700", x=1520, y=180)
    confetti_label.animate("opacity", 0, 1, 0.4, 0.7, ease_out)

    return [bg, fire, snow, confetti, header, fire_label, snow_label, confetti_label]


# ═══════════════════════════════════════════════════════════
# SCENE 6: Shapes & animation 🎨
# ═══════════════════════════════════════════════════════════
@comp.scene(duration=6, name="shapes")
def scene_shapes(t):
    bg = Solid(color="#0d1117")

    header = Text("Shapes & Animation", font_size=60, color="#ffffff", x=960, y=80)
    header.animate("opacity", 0, 1, 0, 0.3, ease_out)

    # Orbiting circles
    import math
    orbit_r = 200
    for i in range(6):
        angle = (t * 2 + i / 6) * math.pi * 2
        ox = 960 + orbit_r * math.cos(angle)
        oy = 540 + orbit_r * math.sin(angle)
        colors = ["#e94560", "#00ff88", "#4ecdc4", "#ffd700", "#ff6b6b", "#a8e6cf"]
        c = Circle(radius=25, fill=colors[i], x=ox, y=oy)
        # These will be static positions, animated via the loop variable
        c.x = ox
        c.y = oy

    # Central pulsing star
    star = Star(outer_radius=80, inner_radius=40, points=6, fill="#ffd700",
               x=960, y=540)
    star.animate("rotation", 0, 360, 0, 1, linear)
    star.animate("scale_x", 0.8, 1.2, 0, 0.5, ease_in_out)
    star.animate("scale_x", 1.2, 0.8, 0.5, 1, ease_in_out)
    star.animate("scale_y", 0.8, 1.2, 0, 0.5, ease_in_out)
    star.animate("scale_y", 1.2, 0.8, 0.5, 1, ease_in_out)

    # Bouncing rectangles
    rect1 = Rectangle(rect_width=100, rect_height=60, fill="#e94560",
                     corner_radius=10, x=300, y=540)
    rect1.animate("y", 900, 200, 0, 0.5, ease_out_bounce)
    rect1.animate("y", 200, 900, 0.5, 1, ease_in_bounce)
    rect1.animate("rotation", 0, 360, 0, 1, linear)

    rect2 = Rectangle(rect_width=80, rect_height=80, fill="#4ecdc4",
                     corner_radius=10, x=1620, y=540)
    rect2.animate("y", 200, 900, 0, 0.5, ease_in_bounce)
    rect2.animate("y", 900, 200, 0.5, 1, ease_out_bounce)
    rect2.animate("rotation", 360, 0, 0, 1, linear)

    return [bg, header, star, rect1, rect2]


# ═══════════════════════════════════════════════════════════
# SCENE 7: Social media presets 📱
# ═══════════════════════════════════════════════════════════
@comp.scene(duration=5, name="presets")
def scene_presets(t):
    bg = Solid(color="#0d1117")

    header = Text("13 Social Presets", font_size=60, color="#ffffff", x=960, y=80)
    header.animate("opacity", 0, 1, 0, 0.3, ease_out)

    # Platform logos as colored rectangles
    platforms = [
        ("YouTube", "#ff0000", 0),
        ("TikTok", "#00f2ea", 0.1),
        ("Instagram", "#e1306c", 0.2),
        ("Twitter", "#1da1f2", 0.3),
        ("LinkedIn", "#0077b5", 0.4),
        ("Facebook", "#1877f2", 0.5),
    ]

    items = []
    for i, (name, color, delay) in enumerate(platforms):
        col = i % 3
        row = i // 3
        x = 400 + col * 400
        y = 300 + row * 280

        card = Rectangle(rect_width=300, rect_height=180, fill=color,
                        corner_radius=16, x=x, y=y)
        card.animate("opacity", 0, 1, delay, delay + 0.4, ease_out)
        card.animate("scale_x", 0, 1, delay, delay + 0.5, ease_out_back)
        card.animate("scale_y", 0, 1, delay, delay + 0.5, ease_out_back)
        items.append(card)

        label = Text(name, font_size=32, color="#ffffff", x=x, y=y)
        label.animate("opacity", 0, 1, delay + 0.2, delay + 0.5, ease_out)
        items.append(label)

    return [bg, header] + items


# ═══════════════════════════════════════════════════════════
# SCENE 8: Integration showcase 🔌
# ═══════════════════════════════════════════════════════════
@comp.scene(duration=4, name="integrations")
def scene_integrations(t):
    bg = Solid(color="#0d1117")

    header = Text("Integrates With Everything", font_size=60, color="#ffffff", x=960, y=80)
    header.animate("opacity", 0, 1, 0, 0.3, ease_out)

    integrations = [
        ("n8n", "#ea4b71", 0),
        ("Zapier", "#ff4a00", 0.15),
        ("Make", "#6d28d9", 0.3),
        ("REST API", "#00ff88", 0.45),
        ("Webhooks", "#4ecdc4", 0.6),
        ("AI Agents", "#ffd700", 0.75),
    ]

    items = []
    for i, (name, color, delay) in enumerate(integrations):
        x = 320 + (i % 3) * 440
        y = 350 + (i // 3) * 250

        circle = Circle(radius=60, fill=color + "30", stroke_width=3,
                       stroke_color=color, x=x, y=y)
        circle.animate("opacity", 0, 1, delay, delay + 0.4, ease_out)
        circle.animate("scale_x", 0, 1, delay, delay + 0.5, ease_out_elastic)
        circle.animate("scale_y", 0, 1, delay, delay + 0.5, ease_out_elastic)
        items.append(circle)

        label = Text(name, font_size=28, color=color, x=x, y=y)
        label.animate("opacity", 0, 1, delay + 0.2, delay + 0.5, ease_out)
        items.append(label)

    return [bg, header] + items


# ═══════════════════════════════════════════════════════════
# SCENE 9: Performance stats 📊
# ═══════════════════════════════════════════════════════════
@comp.scene(duration=4, name="performance")
def scene_performance(t):
    bg = Solid(color="#0a0a0a")

    header = Text("Lightning Fast ⚡", font_size=60, color="#ffffff", x=960, y=100)
    header.animate("opacity", 0, 1, 0, 0.3, ease_out)

    stats = [
        ("O(1)", "Memory Usage", "#00ff88"),
        ("2", "Dependencies", "#4ecdc4"),
        ("40+", "Easing Functions", "#ffd700"),
        ("25+", "Built-in Effects", "#e94560"),
    ]

    items = []
    for i, (value, label, color) in enumerate(stats):
        x = 300 + i * 400
        y = 500

        val_text = Text(value, font_size=100, color=color, x=x, y=y - 40)
        val_text.animate("opacity", 0, 1, 0.2 + i * 0.1, 0.6 + i * 0.1, ease_out_back)
        val_text.animate("y", y + 50, y - 40, 0.2 + i * 0.1, 0.6 + i * 0.1, ease_out_back)
        items.append(val_text)

        lbl = Text(label, font_size=24, color="#ffffff80", x=x, y=y + 60)
        lbl.animate("opacity", 0, 1, 0.4 + i * 0.1, 0.8 + i * 0.1, ease_out)
        items.append(lbl)

    # Bottom text
    bottom = Text("Only Pillow + numpy. That's it. 🐍", font_size=36, color="#ffffff",
                  x=960, y=800)
    bottom.animate("opacity", 0, 1, 1, 1.5, ease_out)

    return [bg, header, bottom] + items


# ═══════════════════════════════════════════════════════════
# SCENE 10: Grand finale with confetti 🎉
# ═══════════════════════════════════════════════════════════
@comp.scene(duration=6, name="finale")
def scene_finale(t):
    bg = Solid(color="#0a0a0a")

    # Giant title
    title = Text("OUROBOROS", font_size=180, color="#00ff88", x=960, y=400)
    title.animate("opacity", 0, 1, 0, 0.5, ease_out)
    title.animate("scale_x", 0.5, 1, 0, 0.8, ease_out_elastic)
    title.animate("scale_y", 0.5, 1, 0, 0.8, ease_out_elastic)

    # Tagline
    tagline = Text("The limit is your imagination.", font_size=48, color="#ffffff",
                   x=960, y=600)
    tagline.animate("opacity", 0, 1, 0.5, 1, ease_out)

    # GitHub
    github = Text("github.com/Atum246/ouroboros", font_size=32, color="#4ecdc4",
                  x=960, y=720)
    github.animate("opacity", 0, 1, 1, 1.5, ease_out)

    # Install
    install = Text("pip install ouroboros", font_size=36, color="#ffd700",
                   x=960, y=820)
    install.animate("opacity", 0, 1, 1.2, 1.8, ease_out)

    # Confetti explosion
    confetti = ParticleSystem.preset_confetti(1920, 1080)

    # Spark bursts
    sparks1 = ParticleSystem.preset_sparks(600, 400)
    sparks2 = ParticleSystem.preset_sparks(1320, 400)

    return [bg, confetti, sparks1, sparks2, title, tagline, github, install]


# ═══════════════════════════════════════════════════════════
# RENDER 🎬
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("🐍 Rendering Ouroboros Trailer...")
    print()
    comp.render("trailer.mp4", quality=18, preset="fast")
    print()
    print("🎬 Trailer complete!")
