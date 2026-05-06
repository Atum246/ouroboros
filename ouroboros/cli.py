"""
CLI — Command-line interface for Ouroboros.

Commands:
    ouroboros render <file>     Render a Python file to video
    ouroboros preview <file>    Live preview in browser
    ouroboros info <file>       Show composition info
    ouroboros formats           List supported formats
    ouroboros effects           List available effects
    ouroboros easings           List easing functions
    ouroboros presets           List presets/templates
    ouroboros new <name>        Create a new project from template
    ouroboros serve             Start API server for integrations
"""

import argparse
import os
import sys
import time
import json
import importlib.util
from typing import Optional


def _print_banner():
    """Print the Ouroboros banner."""
    banner = """
  ╔═══════════════════════════════════════════════════════╗
  ║                                                       ║
  ║    🐍  O U R O B O R O S  🐍                         ║
  ║    ─────────────────────────                          ║
  ║    The Ultimate Python Video Framework                 ║
  ║    v1.0.0                                             ║
  ║                                                       ║
  ╚═══════════════════════════════════════════════════════╝
"""
    print(banner)


def _load_module(filepath: str):
    """Load a Python file as a module."""
    spec = importlib.util.spec_from_file_location("composition", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _find_composition(module):
    """Find the Composition object in a module."""
    from ouroboros import Composition
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, Composition):
            return obj
    return None


def cmd_render(args):
    """Render a composition to video."""
    _print_banner()

    filepath = os.path.abspath(args.file)
    if not os.path.exists(filepath):
        print(f"  ❌ File not found: {filepath}")
        sys.exit(1)

    print(f"  📄 Loading: {os.path.basename(filepath)}")

    module = _load_module(filepath)
    comp = _find_composition(module)

    if comp is None:
        print("  ❌ No Composition found in file")
        print("     Make sure you create a Composition() object")
        sys.exit(1)

    print(f"  🎬 {comp}")

    output = args.output or "output.mp4"
    quality = args.quality
    preset = args.preset

    print(f"  🎯 Rendering to: {output}")
    print()

    start = time.time()
    comp.render(
        output_path=output,
        quality=quality,
        preset=preset,
        progress=True,
        preview=args.preview,
    )
    elapsed = time.time() - start

    size_mb = os.path.getsize(output) / (1024 * 1024)
    print(f"\n  📊 Stats:")
    print(f"     Duration: {comp.duration:.1f}s")
    print(f"     Frames: {comp.total_frames}")
    print(f"     Size: {size_mb:.1f} MB")
    print(f"     Time: {elapsed:.1f}s")
    print(f"     Speed: {comp.total_frames / elapsed:.1f} fps")


def cmd_info(args):
    """Show composition info."""
    filepath = os.path.abspath(args.file)
    if not os.path.exists(filepath):
        print(f"  ❌ File not found: {filepath}")
        sys.exit(1)

    module = _load_module(filepath)
    comp = _find_composition(module)

    if comp is None:
        print("  ❌ No Composition found in file")
        sys.exit(1)

    print(f"\n  📋 Composition Info")
    print(f"  {'─' * 40}")
    print(f"  Resolution:  {comp.width}x{comp.height}")
    print(f"  FPS:         {comp._fps}")
    print(f"  Duration:    {comp.duration:.1f}s")
    print(f"  Total Frames: {comp.total_frames}")
    print(f"  Scenes:      {len(comp._scenes)}")
    print(f"  Audio:       {len(comp._audio_tracks)} tracks")
    print()

    for i, scene in enumerate(comp._scenes):
        print(f"  Scene {i + 1}: {scene.name} ({scene.duration}s)")


def cmd_formats(args):
    """List supported formats."""
    print("\n  📦 Supported Output Formats")
    print(f"  {'─' * 40}")
    formats = [
        ("MP4", ".mp4", "H.264/H.265 — Universal, best compatibility"),
        ("GIF", ".gif", "Animated GIF — Web, social media"),
        ("WebM", ".webm", "VP9 — Web, smaller files"),
        ("MOV", ".mov", "ProRes — Professional editing"),
        ("AVI", ".avi", "Legacy format"),
    ]
    for name, ext, desc in formats:
        print(f"  {ext:8s}  {name:6s}  {desc}")
    print()


def cmd_effects(args):
    """List available effects."""
    print("\n  ✨ Available Effects")
    print(f"  {'─' * 40}")

    categories = {
        "Blur": ["Blur", "GaussianBlur", "MotionBlur", "RadialBlur"],
        "Color": ["Brightness", "Contrast", "Saturation", "HueShift", "Sepia", "Grayscale", "Invert", "ColorBalance", "Temperature"],
        "Glow": ["Glow", "Bloom", "Neon"],
        "Distortion": ["Wave", "Ripple", "Pixelate", "Glitch", "FilmGrain", "Vignette", "ChromaticAberration"],
        "Shadow": ["DropShadow", "LongShadow", "InnerShadow"],
        "Mask": ["Mask", "ShapeMask", "GradientMask"],
    }

    for cat, effects in categories.items():
        print(f"\n  {cat}:")
        for e in effects:
            print(f"    • {e}")

    print(f"\n  🎭 Transitions:")
    transitions = ["FadeTransition", "WipeTransition", "DissolveTransition",
                   "SlideTransition", "ZoomTransition", "PushTransition"]
    for t in transitions:
        print(f"    • {t}")
    print()


def cmd_easings(args):
    """List easing functions."""
    print("\n  📈 Easing Functions (40+)")
    print(f"  {'─' * 40}")

    groups = {
        "Basic": ["linear", "ease_in", "ease_out", "ease_in_out"],
        "Quadratic": ["ease_in_quad", "ease_out_quad", "ease_in_out_quad"],
        "Cubic": ["ease_in_cubic", "ease_out_cubic", "ease_in_out_cubic"],
        "Quartic": ["ease_in_quart", "ease_out_quart", "ease_in_out_quart"],
        "Quintic": ["ease_in_quint", "ease_out_quint", "ease_in_out_quint"],
        "Sine": ["ease_in_sine", "ease_out_sine", "ease_in_out_sine"],
        "Exponential": ["ease_in_expo", "ease_out_expo", "ease_in_out_expo"],
        "Circular": ["ease_in_circ", "ease_out_circ", "ease_in_out_circ"],
        "Elastic": ["ease_in_elastic", "ease_out_elastic", "ease_in_out_elastic"],
        "Back": ["ease_in_back", "ease_out_back", "ease_in_out_back"],
        "Bounce": ["ease_in_bounce", "ease_out_bounce", "ease_in_out_bounce"],
    }

    for group, easings in groups.items():
        print(f"\n  {group}:")
        for e in easings:
            print(f"    • {e}")
    print()


def cmd_presets(args):
    """List presets and templates."""
    print("\n  🎨 Presets & Templates")
    print(f"  {'─' * 40}")
    print("""
  Particle Presets:
    • ParticleSystem.preset_fire(x, y)      — Fire effect
    • ParticleSystem.preset_snow(w, h)       — Snowfall
    • ParticleSystem.preset_confetti(w, h)   — Confetti burst
    • ParticleSystem.preset_sparks(x, y)     — Spark effects
    • ParticleSystem.preset_smoke(x, y)      — Smoke effect

  Social Media Presets:
    • YouTube 1080p: 1920x1080 @ 30fps
    • Instagram Square: 1080x1080 @ 30fps
    • Instagram Story: 1080x1920 @ 30fps
    • TikTok: 1080x1920 @ 30fps
    • Twitter: 1280x720 @ 30fps
""")


def cmd_new(args):
    """Create a new project from template."""
    name = args.name
    os.makedirs(name, exist_ok=True)

    template = '''"""
{name} — Created with Ouroboros 🐍
"""

from ouroboros import *

# Create composition
comp = Composition(1920, 1080, 30)


@comp.scene(duration=5)
def intro(t):
    """Intro scene with animated text."""
    bg = Solid(color="#1a1a2e")
    title = Text("{name}", font_size=120, color="#e94560")
    subtitle = Text("Made with Ouroboros 🐍", font_size=40, color="#ffffff80")

    # Animate
    title.animate("opacity", 0, 1, 0, 0.5, ease_out)
    title.animate("y", 600, 400, 0, 1, ease_in_out)
    subtitle.animate("opacity", 0, 1, 0.3, 0.8, ease_out)

    return [bg, title, subtitle]


@comp.scene(duration=3)
def main(t):
    """Main content scene."""
    bg = Solid(color="#16213e")
    content = Text("Your content here", font_size=60, color="#ffffff")
    content.animate("opacity", 0, 1, 0, 0.5, ease_out)
    return [bg, content]


@comp.scene(duration=3)
def outro(t):
    """Outro scene."""
    bg = Solid(color="#0f3460")
    text = Text("Thanks for watching!", font_size=80, color="#e94560")
    text.animate("opacity", 0, 1, 0, 0.5, ease_out)
    text.animate("scale_x", 0.8, 1, 0, 1, ease_out_back)
    text.animate("scale_y", 0.8, 1, 0, 1, ease_out_back)
    return [bg, text]


if __name__ == "__main__":
    comp.render("{name}.mp4")
'''

    content = template.format(name=name)
    filepath = os.path.join(name, "main.py")
    with open(filepath, "w") as f:
        f.write(content)

    print(f"\n  ✅ Created project: {name}/")
    print(f"  📄 {filepath}")
    print(f"\n  Run it:")
    print(f"    cd {name} && python main.py")
    print(f"    ouroboros render {filepath}")
    print()


def cmd_serve(args):
    """Start the API server for integrations."""
    from ouroboros.integrations.api import create_app
    port = args.port or 8787
    print(f"\n  🐍 Ouroboros API Server")
    print(f"  ─────────────────────────")
    print(f"  Starting on port {port}...")
    print(f"  API docs: http://localhost:{port}/docs")
    print(f"  Webhook:  http://localhost:{port}/webhook")
    print()
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=args.debug)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="ouroboros",
        description="🐍 Ouroboros — The Ultimate Python Video Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ouroboros render video.py              Render video.py to output.mp4
  ouroboros render video.py -o out.gif   Render as GIF
  ouroboros render video.py -q 18        High quality render
  ouroboros info video.py                Show composition info
  ouroboros new myproject                Create new project
  ouroboros effects                      List all effects
  ouroboros easings                      List easing functions
  ouroboros serve                        Start API server
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # render
    render_parser = subparsers.add_parser("render", help="Render a Python file to video")
    render_parser.add_argument("file", help="Python file with Composition")
    render_parser.add_argument("-o", "--output", help="Output file path")
    render_parser.add_argument("-q", "--quality", type=int, default=23, help="CRF quality (0-51)")
    render_parser.add_argument("-p", "--preset", default="medium", help="Encoding preset")
    render_parser.add_argument("--preview", action="store_true", help="Open after render")
    render_parser.set_defaults(func=cmd_render)

    # info
    info_parser = subparsers.add_parser("info", help="Show composition info")
    info_parser.add_argument("file", help="Python file with Composition")
    info_parser.set_defaults(func=cmd_info)

    # formats
    formats_parser = subparsers.add_parser("formats", help="List supported formats")
    formats_parser.set_defaults(func=cmd_formats)

    # effects
    effects_parser = subparsers.add_parser("effects", help="List available effects")
    effects_parser.set_defaults(func=cmd_effects)

    # easings
    easings_parser = subparsers.add_parser("easings", help="List easing functions")
    easings_parser.set_defaults(func=cmd_easings)

    # presets
    presets_parser = subparsers.add_parser("presets", help="List presets/templates")
    presets_parser.set_defaults(func=cmd_presets)

    # new
    new_parser = subparsers.add_parser("new", help="Create new project from template")
    new_parser.add_argument("name", help="Project name")
    new_parser.set_defaults(func=cmd_new)

    # serve
    serve_parser = subparsers.add_parser("serve", help="Start API server for integrations")
    serve_parser.add_argument("-p", "--port", type=int, default=8787, help="Server port")
    serve_parser.add_argument("--debug", action="store_true", help="Debug mode")
    serve_parser.set_defaults(func=cmd_serve)

    args = parser.parse_args()

    if not args.command:
        _print_banner()
        parser.print_help()
        print()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
