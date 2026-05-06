# Ouroboros — AI Agent Skill

Create videos programmatically using the Ouroboros Python framework.

## Overview

Ouroboros is a lightweight Python video framework that creates any type of video — animations, motion graphics, data visualizations, social media content, and more. It uses frame-by-frame generator rendering for O(1) memory usage.

## Quick Reference

### Create a Composition

```python
from ouroboros import *

comp = Composition(1920, 1080, 30)  # width, height, fps
```

### Add Scenes

```python
@comp.scene(duration=5)
def my_scene(t):
    # t is normalized time 0-1
    bg = Solid(color="#1a1a2e")
    title = Text("Hello", font_size=120, color="#e94560")
    title.animate("opacity", 0, 1, 0, 0.5, ease_out)
    return [bg, title]
```

### Render

```python
comp.render("output.mp4")  # or .gif, .webm, .mov
```

## Available Layers

- `Solid(color)` — solid/gradient background
- `Text(text, font_size, color)` — text with animations
- `Circle(radius, fill)` — circle shape
- `Rectangle(width, height, fill, corner_radius)` — rectangle
- `Triangle(size, fill)` — triangle
- `Star(outer_radius, inner_radius, points, fill)` — star
- `Ellipse(radius_x, radius_y, fill)` — ellipse
- `ImageLayer(source)` — embed images
- `VideoLayer(source)` — embed video clips
- `ParticleSystem(...)` — particle effects

## Animation

```python
layer.animate("property", start_val, end_val, start_t, end_t, easing)

# Properties: x, y, opacity, rotation, scale_x, scale_y, width, height
# 40+ easings: linear, ease_in, ease_out, ease_in_out, ease_in_bounce, etc.
```

## Effects

```python
layer.add_effect(GaussianBlur(radius=5))
layer.add_effect(Glow(radius=10))
layer.add_effect(Neon(color=(0, 255, 200)))
layer.add_effect(Glitch(intensity=0.5))
layer.add_effect(FilmGrain(amount=20))
layer.add_effect(Vignette(strength=0.5))
```

## Particle Presets

```python
fire = ParticleSystem.preset_fire(x, y)
snow = ParticleSystem.preset_snow(width, height)
confetti = ParticleSystem.preset_confetti(width, height)
sparks = ParticleSystem.preset_sparks(x, y)
smoke = ParticleSystem.preset_smoke(x, y)
```

## Social Presets

```python
from ouroboros.presets.social import youtube_1080p, instagram_square, tiktok
comp = youtube_1080p()
comp = instagram_square()
comp = tiktok()
```

## Audio

```python
from ouroboros import AudioTrack
comp.add_audio(AudioTrack("music.mp3", volume=0.3, fade_in=1.0))
```

## CLI Commands

```bash
ouroboros render file.py            # Render video
ouroboros render file.py -o out.gif # Render as GIF
ouroboros info file.py              # Show info
ouroboros new project_name          # New project
ouroboros effects                   # List effects
ouroboros easings                   # List easings
ouroboros serve                     # Start API server
```

## REST API

```bash
# POST /render — render from JSON spec
# POST /webhook — webhook receiver
# GET /status/:id — check render status
# GET /health — health check
```
