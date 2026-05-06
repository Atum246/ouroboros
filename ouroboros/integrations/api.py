"""
REST API — HTTP API for n8n, Zapier, Make, and webhooks.

Endpoints:
    POST /render          — Render a video from JSON spec
    POST /render/template — Render from a saved template
    POST /webhook         — Webhook receiver for automation
    GET  /status/:id      — Check render status
    GET  /formats         — List supported formats
    GET  /effects         — List available effects
    GET  /health          — Health check
"""

import os
import json
import uuid
import time
import threading
from typing import Dict, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


# In-memory job store
_jobs: Dict[str, Dict[str, Any]] = {}


def _parse_color(color: Any):
    """Parse color to RGBA tuple."""
    if isinstance(color, str):
        color = color.lstrip("#")
        if len(color) == 6:
            return (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16), 255)
    elif isinstance(color, (list, tuple)):
        return tuple(color)
    return (0, 0, 0, 255)


def _build_composition(spec: Dict[str, Any]):
    """Build a Composition from a JSON spec."""
    from ouroboros import Composition
    from ouroboros.layers.solid import Solid
    from ouroboros.layers.text_layer import Text
    from ouroboros.layers.shape import Circle, Rectangle
    from ouroboros.particles.system import ParticleSystem

    width = spec.get("width", 1920)
    height = spec.get("height", 1080)
    fps = spec.get("fps", 30)
    background = spec.get("background", "#000000")

    comp = Composition(width, height, fps, background)

    for scene_spec in spec.get("scenes", []):
        duration = scene_spec.get("duration", 5)
        name = scene_spec.get("name", "scene")
        layers_spec = scene_spec.get("layers", [])
        scene_name = name

        def make_scene(ls, sn):
            def scene_func(t):
                layers = []
                for layer_spec in ls:
                    layer_type = layer_spec.get("type", "solid")

                    if layer_type == "solid":
                        layer = Solid(
                            color=layer_spec.get("color", "#000000"),
                            x=layer_spec.get("x", 0),
                            y=layer_spec.get("y", 0),
                        )
                    elif layer_type == "text":
                        layer = Text(
                            text=layer_spec.get("text", ""),
                            font_size=layer_spec.get("font_size", 48),
                            color=layer_spec.get("color", "#ffffff"),
                            x=layer_spec.get("x", 0),
                            y=layer_spec.get("y", 0),
                        )
                    elif layer_type == "circle":
                        layer = Circle(
                            radius=layer_spec.get("radius", 50),
                            fill=layer_spec.get("fill", "#ffffff"),
                            x=layer_spec.get("x", 0),
                            y=layer_spec.get("y", 0),
                        )
                    elif layer_type == "rectangle":
                        layer = Rectangle(
                            rect_width=layer_spec.get("width", 100),
                            rect_height=layer_spec.get("height", 100),
                            fill=layer_spec.get("fill", "#ffffff"),
                            corner_radius=layer_spec.get("corner_radius", 0),
                            x=layer_spec.get("x", 0),
                            y=layer_spec.get("y", 0),
                        )
                    elif layer_type == "particles":
                        preset = layer_spec.get("preset", "fire")
                        if preset == "fire":
                            layer = ParticleSystem.preset_fire(
                                layer_spec.get("x", width // 2),
                                layer_spec.get("y", height - 100),
                            )
                        elif preset == "snow":
                            layer = ParticleSystem.preset_snow(width, height)
                        elif preset == "confetti":
                            layer = ParticleSystem.preset_confetti(width, height)
                        else:
                            layer = ParticleSystem(
                                emitter_x=layer_spec.get("x", width // 2),
                                emitter_y=layer_spec.get("y", height // 2),
                            )
                    else:
                        continue

                    # Apply animations
                    for anim in layer_spec.get("animations", []):
                        layer.animate(
                            anim["property"],
                            anim["start"],
                            anim["end"],
                            anim.get("start_time", 0),
                            anim.get("end_time", 1),
                        )

                    layers.append(layer)
                return layers
            return scene_func

        scene_func = make_scene(layers_spec, scene_name)
        comp.scene(duration=duration, name=scene_name)(scene_func)

    return comp


def _render_async(job_id: str, comp, output_path: str, **kwargs):
    """Render in background thread."""
    try:
        _jobs[job_id]["status"] = "rendering"
        _jobs[job_id]["started_at"] = time.time()

        comp.render(output_path, progress=False, **kwargs)

        _jobs[job_id]["status"] = "completed"
        _jobs[job_id]["output"] = output_path
        _jobs[job_id]["completed_at"] = time.time()
        _jobs[job_id]["size"] = os.path.getsize(output_path)
    except Exception as e:
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["error"] = str(e)


class OuroborosHandler(BaseHTTPRequestHandler):
    """HTTP request handler."""

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/health":
            self._json_response({"status": "ok", "service": "ouroboros", "version": "1.0.0"})

        elif path == "/formats":
            self._json_response({
                "formats": [
                    {"name": "MP4", "ext": ".mp4", "codec": "libx264"},
                    {"name": "GIF", "ext": ".gif"},
                    {"name": "WebM", "ext": ".webm", "codec": "libvpx-vp9"},
                    {"name": "MOV", "ext": ".mov"},
                ]
            })

        elif path == "/effects":
            from ouroboros.effects.blur import Blur, GaussianBlur, MotionBlur
            from ouroboros.effects.color import Brightness, Contrast, Saturation, Sepia, Grayscale
            from ouroboros.effects.glow import Glow, Bloom, Neon
            from ouroboros.effects.distortion import Wave, Ripple, Pixelate, Glitch, FilmGrain, Vignette
            self._json_response({
                "effects": {
                    "blur": ["Blur", "GaussianBlur", "MotionBlur", "RadialBlur"],
                    "color": ["Brightness", "Contrast", "Saturation", "HueShift", "Sepia", "Grayscale", "Invert"],
                    "glow": ["Glow", "Bloom", "Neon"],
                    "distortion": ["Wave", "Ripple", "Pixelate", "Glitch", "FilmGrain", "Vignette", "ChromaticAberration"],
                    "shadow": ["DropShadow", "LongShadow", "InnerShadow"],
                }
            })

        elif path.startswith("/status/"):
            job_id = path.split("/")[-1]
            if job_id in _jobs:
                self._json_response(_jobs[job_id])
            else:
                self._json_response({"error": "Job not found"}, 404)

        else:
            self._json_response({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        spec = json.loads(body) if body else {}

        if parsed.path == "/render":
            job_id = str(uuid.uuid4())[:8]
            output_dir = spec.get("output_dir", "/tmp/ouroboros")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{job_id}.mp4")

            try:
                comp = _build_composition(spec)
                _jobs[job_id] = {
                    "id": job_id,
                    "status": "queued",
                    "spec": spec,
                    "created_at": time.time(),
                }

                thread = threading.Thread(
                    target=_render_async,
                    args=(job_id, comp, output_path),
                    daemon=True,
                )
                thread.start()

                self._json_response({
                    "job_id": job_id,
                    "status": "queued",
                    "status_url": f"/status/{job_id}",
                }, 202)

            except Exception as e:
                self._json_response({"error": str(e)}, 400)

        elif parsed.path == "/webhook":
            # Generic webhook — process and respond
            event_type = spec.get("type", "unknown")
            self._json_response({
                "received": True,
                "event": event_type,
                "timestamp": time.time(),
            })

        else:
            self._json_response({"error": "Not found"}, 404)

    def _json_response(self, data: Dict, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def create_app():
    """Create the HTTP server app."""
    return OuroborosHandler


def start_server(port: int = 8787, host: str = "0.0.0.0"):
    """Start the API server."""
    server = HTTPServer((host, port), OuroborosHandler)
    print(f"  🐍 Ouroboros API running on http://{host}:{port}")
    print(f"  POST /render          — Render video from JSON spec")
    print(f"  POST /webhook         — Webhook receiver")
    print(f"  GET  /status/:id      — Check render status")
    print(f"  GET  /formats         — List formats")
    print(f"  GET  /effects         — List effects")
    print(f"  GET  /health          — Health check")
    server.serve_forever()


if __name__ == "__main__":
    start_server()
