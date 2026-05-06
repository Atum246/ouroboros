# 🐍 Ouroboros

**The Ultimate Python Video Framework** — Create any video programmatically with zero bloat.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> *"Like Remotion.dev, but for Python. Lighter, faster, more powerful."*

### 🎬 See it in action

![Ouroboros Showcase](examples/showcase.gif)

*Animated showcase — effects, particles, shapes, presets, all generated with Ouroboros itself* 🐍

---

## ✨ Why Ouroboros?

| Feature | Ouroboros 🐍 | Remotion ⚛️ | MoviePy 🎬 | Manim 📐 |
|---------|-------------|------------|-----------|---------|
| Language | Python | React/JS | Python | Python |
| Memory | O(1) frames | High (DOM) | High | Medium |
| Animations | 40+ easings | Manual | Basic | Math-focused |
| Effects | 25+ built-in | CSS only | Limited | Limited |
| Particles | ✅ Built-in | ❌ | ❌ | ❌ |
| CLI | ✅ Full | ✅ | ❌ | ✅ |
| REST API | ✅ n8n/Zapier | ❌ | ❌ | ❌ |
| AI Skills | ✅ OpenClaw/Cursor | ❌ | ❌ | ❌ |
| Dependencies | 2 (Pillow, numpy) | Node.js + React | Many | Many |

## 🚀 Quick Start

### Install

```bash
pip install ouroboros
```

### Hello World

```python
from ouroboros import *

comp = Composition(1920, 1080, 30)

@comp.scene(duration=5)
def intro(t):
    bg = Solid(color="#1a1a2e")
    title = Text("Hello World! 🐍", font_size=120, color="#e94560")
    title.animate("opacity", 0, 1, 0, 0.5, ease_out)
    title.animate("y", 600, 400, 0, 1, ease_in_out)
    return [bg, title]

comp.render("hello.mp4")
```

### CLI

```bash
ouroboros render video.py           # Render to MP4
ouroboros render video.py -o out.gif  # Render as GIF
ouroboros info video.py             # Show composition info
ouroboros new myproject             # Create new project
ouroboros effects                   # List all effects
ouroboros easings                   # List easing functions
ouroboros serve                     # Start API server
```

---

## 🎨 Features

### 🎬 Core Engine
- Frame-by-frame generator rendering (O(1) RAM)
- Scene-based composition with timeline
- Streaming output via ffmpeg pipe
- Configurable FPS, resolution, quality

### 🎯 Animation System
- **40+ easing functions** — linear, quad, cubic, elastic, bounce, back, etc.
- **Keyframe animation** — multi-step with per-keyframe easing
- **Property tweening** — animate any numeric or color property
- **Spring physics** — natural motion with stiffness, damping, mass

### 🧱 Layers
- **Solid** — solid colors, linear/radial gradients
- **Text** — fonts, stroke, shadow, typewriter effect
- **Image** — PNG, JPG, WebP with fit modes
- **Video** — embed video clips with looping
- **Shapes** — Circle, Rectangle, Triangle, Star, Ellipse, Polygon, Arc, Path

### ✨ Effects (25+)
- **Blur** — Gaussian, motion, radial, box
- **Color** — brightness, contrast, saturation, hue, sepia, grayscale, temperature
- **Glow** — glow, bloom, neon
- **Distortion** — wave, ripple, pixelate, glitch, film grain, vignette, chromatic aberration
- **Shadow** — drop shadow, long shadow, inner shadow
- **Mask** — alpha mask, shape mask, gradient mask

### 🎭 Transitions
Fade, Wipe, Dissolve, Slide, Zoom, Push — with customizable easing.

### 🌟 Particles
Fire, snow, confetti, sparks, smoke — or create custom particle systems.

### 🔊 Audio
- Background music with volume/fade control
- Waveform visualization
- Beat-synced animations

### 📝 Subtitles
- SRT file parsing
- Auto-synced overlay with styling

### 📦 Social Media Presets
YouTube, Instagram, TikTok, Twitter, LinkedIn, Facebook — one line of code.

### 🔌 Integrations
- **REST API** — for n8n, Zapier, Make automation
- **Webhooks** — receive and process automation events
- **JSON rendering** — define videos as JSON specs

### 🤖 AI Agent Skills
- OpenClaw skill file included
- Works with Claude Code, Cursor, and other AI coding tools
- Structured prompts for video generation

---

## 📖 Examples

### Animated Shapes

```python
from ouroboros import *

comp = Composition(1920, 1080, 30, background="#0a0a0a")

@comp.scene(duration=6)
def shapes(t):
    bg = Solid(color="#0a0a0a")
    circle = Circle(radius=60, fill="#e94560")
    circle.animate("x", 300, 1600, 0, 1, ease_in_out)
    circle.animate("y", 540, 300, 0, 0.5, ease_out_bounce)
    circle.animate("y", 300, 540, 0.5, 1, ease_in_bounce)
    return [bg, circle]

comp.render("shapes.mp4")
```

### Particle Effects

```python
from ouroboros import *

comp = Composition(1920, 1080, 30, background="#0a0a0a")

@comp.scene(duration=5)
def fire(t):
    bg = Solid(color="#0a0a0a")
    fire = ParticleSystem.preset_fire(960, 900)
    return [bg, fire]

comp.render("fire.mp4")
```

### Effects

```python
from ouroboros import *

comp = Composition(1920, 1080, 30)

@comp.scene(duration=4)
def neon(t):
    bg = Solid(color="#0a0a0a")
    text = Text("NEON ✨", font_size=120, color="#00ffcc")
    text.add_effect(Neon(color=(0, 255, 200), radius=5))
    return [bg, text]

comp.render("neon.mp4")
```

### REST API (for n8n/Zapier)

```bash
# Start server
ouroboros serve

# Render via API
curl -X POST http://localhost:8787/render \
  -H "Content-Type: application/json" \
  -d '{
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "scenes": [{
      "name": "intro",
      "duration": 5,
      "layers": [
        {"type": "solid", "color": "#1a1a2e"},
        {"type": "text", "text": "Hello API!", "font_size": 120, "color": "#e94560",
         "animations": [{"property": "opacity", "start": 0, "end": 1}]}
      ]
    }]
  }'
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│              User Composition               │
│    (Python functions that describe video)    │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│            Scene Generator                   │
│    (yields one frame at a time — O(1) RAM)   │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│           Effect Pipeline                    │
│  (composable filters applied per-frame)      │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          Frame Encoder (ffmpeg pipe)         │
│    (stream to disk — never hold full video)  │
└─────────────────────────────────────────────┘
```

---

## 📋 Requirements

- Python 3.9+
- Pillow >= 10.0
- numpy >= 1.24
- ffmpeg (system binary)

### Optional
- pydub (for advanced audio processing)

---

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines.

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Made with 🐍 by the Ouroboros Team
  <br>
  <em>The end is the beginning</em>
</p>
