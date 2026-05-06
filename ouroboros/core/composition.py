"""
Composition — The main video container.

A Composition holds scenes, manages the timeline, and orchestrates rendering.
It's the entry point for creating any video.
"""

import os
import sys
import time
import subprocess
import struct
from typing import List, Optional, Callable, Dict, Any, Tuple, Generator
from PIL import Image
import numpy as np

from ouroboros.core.scene import Scene
from ouroboros.core.timeline import Timeline
from ouroboros.layers.base import Layer
from ouroboros.audio.track import AudioTrack


class Composition:
    """
    Main video composition container.

    Args:
        width: Video width in pixels
        height: Video height in pixels
        fps: Frames per second
        background: Default background color (hex or RGBA tuple)

    Example::

        comp = Composition(1920, 1080, 30)

        @comp.scene(duration=5)
        def intro(t):
            return [Solid(color="#1a1a2e"), Text("Hello", font_size=120)]

        comp.render("output.mp4")
    """

    def __init__(
        self,
        width: int = 1920,
        height: int = 1080,
        fps: int = 30,
        background: Any = "#000000",
    ):
        self.width = width
        self.height = height
        self._fps = fps
        self.background = background
        self._scenes: List[Scene] = []
        self._timeline = Timeline()
        self._audio_tracks: List[AudioTrack] = []
        self._global_effects: List = []
        self._metadata: Dict[str, Any] = {}
        self._on_progress: Optional[Callable] = None
        self._preview_server = None

    @property
    def fps(self) -> int:
        return self._fps

    @property
    def duration(self) -> float:
        """Total duration in seconds."""
        return sum(s.duration for s in self._scenes)

    @property
    def total_frames(self) -> int:
        """Total number of frames."""
        return int(self.duration * self._fps)

    def scene(self, duration: float = 5.0, name: Optional[str] = None):
        """
        Decorator to register a scene function.

        The function receives `t` (0.0 to 1.0 normalized time) and should
        return a list of layers to render.

        Args:
            duration: Scene duration in seconds
            name: Optional scene name

        Example::

            @comp.scene(duration=3)
            def fade_in(t):
                bg = Solid(color="#000000")
                txt = Text("Hello", opacity=t)
                return [bg, txt]
        """
        def decorator(func: Callable) -> Callable:
            scene = Scene(
                func=func,
                duration=duration,
                name=name or func.__name__,
                composition=self,
            )
            self._scenes.append(scene)
            self._timeline.add_scene(scene, after=len(self._scenes) - 1)
            return func
        return decorator

    def add_scene(self, scene: Scene):
        """Add a Scene object directly."""
        scene.composition = self
        self._scenes.append(scene)
        self._timeline.add_scene(scene, after=len(self._scenes) - 1)

    def add_audio(self, track: AudioTrack):
        """Add an audio track to the composition."""
        self._audio_tracks.append(track)

    def add_effect(self, effect):
        """Add a global effect applied to all frames."""
        self._global_effects.append(effect)

    def set_metadata(self, key: str, value: Any):
        """Set metadata for the composition."""
        self._metadata[key] = value

    def on_progress(self, callback: Callable):
        """Set a progress callback: callback(current_frame, total_frames, elapsed)."""
        self._on_progress = callback

    def _parse_color(self, color: Any) -> Tuple[int, int, int, int]:
        """Parse color to RGBA tuple."""
        if isinstance(color, str):
            if color.startswith("#"):
                color = color.lstrip("#")
                if len(color) == 6:
                    r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
                    return (r, g, b, 255)
                elif len(color) == 8:
                    r, g, b, a = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16), int(color[6:8], 16)
                    return (r, g, b, a)
            elif color.startswith("rgb"):
                import re
                nums = re.findall(r"[\d.]+", color)
                if len(nums) == 3:
                    return (int(nums[0]), int(nums[1]), int(nums[2]), 255)
                elif len(nums) == 4:
                    return (int(nums[0]), int(nums[1]), int(nums[2]), int(float(nums[3]) * 255))
            # Named colors
            named = {
                "black": (0, 0, 0, 255), "white": (255, 255, 255, 255),
                "red": (255, 0, 0, 255), "green": (0, 128, 0, 255),
                "blue": (0, 0, 255, 255), "yellow": (255, 255, 0, 255),
                "cyan": (0, 255, 255, 255), "magenta": (255, 0, 255, 255),
                "transparent": (0, 0, 0, 0),
            }
            if color.lower() in named:
                return named[color.lower()]
        elif isinstance(color, (tuple, list)):
            if len(color) == 3:
                return (color[0], color[1], color[2], 255)
            elif len(color) == 4:
                return tuple(color)
        return (0, 0, 0, 255)

    def _create_background(self) -> Image.Image:
        """Create the background frame."""
        bg = Image.new("RGBA", (self.width, self.height), self._parse_color(self.background))
        return bg

    def _render_frame(self, scene_idx: int, frame_in_scene: int) -> Image.Image:
        """Render a single frame from a scene."""
        scene = self._scenes[scene_idx]
        t = frame_in_scene / max(1, scene.frame_count(self._fps) - 1)
        t = max(0.0, min(1.0, t))

        # Get layers from scene
        layers = scene.func(t)

        if not layers:
            layers = []

        # Start with background
        frame = self._create_background()

        # Render each layer
        for layer in layers:
            if isinstance(layer, Layer):
                layer_frame = layer.render(
                    t, self.width, self.height, self._fps, frame_in_scene
                )
                if layer_frame is not None:
                    if layer_frame.mode != "RGBA":
                        layer_frame = layer_frame.convert("RGBA")
                    frame = Image.alpha_composite(frame, layer_frame)

        # Apply global effects
        for effect in self._global_effects:
            frame = effect.apply(frame, t, frame_in_scene)

        return frame

    def _generate_frames(self) -> Generator[Tuple[Image.Image, int], None, None]:
        """Generate all frames as a generator (O(1) memory)."""
        global_frame = 0
        for scene_idx, scene in enumerate(self._scenes):
            scene_frames = scene.frame_count(self._fps)
            for f in range(scene_frames):
                frame = self._render_frame(scene_idx, f)
                yield frame, global_frame
                global_frame += 1

    def render(
        self,
        output_path: str = "output.mp4",
        codec: str = "libx264",
        quality: int = 23,
        preset: str = "medium",
        pixel_format: str = "yuv420p",
        audio_codec: str = "aac",
        progress: bool = True,
        preview: bool = False,
    ) -> str:
        """
        Render the composition to a video file.

        Args:
            output_path: Output file path (.mp4, .gif, .webm, .mov)
            codec: Video codec (libx264, libx265, libvpx-vp9)
            quality: CRF quality (0=lossless, 51=worst, 23=default)
            preset: Encoding preset (ultrafast, fast, medium, slow, veryslow)
            pixel_format: Pixel format for output
            audio_codec: Audio codec
            progress: Show progress bar
            preview: Open in default player after render

        Returns:
            Absolute path to rendered file
        """
        if not self._scenes:
            raise ValueError("No scenes added to composition")

        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        # Determine format from extension
        ext = os.path.splitext(output_path)[1].lower()
        if ext == ".gif":
            return self._render_gif(output_path, progress)
        elif ext == ".webm":
            codec = "libvpx-vp9"
        elif ext == ".mov":
            pixel_format = "yuv420p"

        total = self.total_frames
        start_time = time.time()

        # Build ffmpeg command
        cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{self.width}x{self.height}",
            "-pix_fmt", "rgba",
            "-r", str(self._fps),
            "-i", "-",
            "-i", "-" if self._audio_tracks else "/dev/null",
            "-c:v", codec,
            "-crf", str(quality),
            "-preset", preset,
            "-pix_fmt", pixel_format,
            "-c:a", audio_codec,
            "-shortest",
            output_path,
        ]

        # Remove audio input if no audio tracks
        if not self._audio_tracks:
            cmd = [
                "ffmpeg", "-y",
                "-f", "rawvideo",
                "-vcodec", "rawvideo",
                "-s", f"{self.width}x{self.height}",
                "-pix_fmt", "rgba",
                "-r", str(self._fps),
                "-i", "-",
                "-c:v", codec,
                "-crf", str(quality),
                "-preset", preset,
                "-pix_fmt", pixel_format,
                output_path,
            ]

        # Start ffmpeg process
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        try:
            current = 0
            for frame, frame_idx in self._generate_frames():
                # Convert to raw bytes
                raw = frame.tobytes()
                process.stdin.write(raw)
                current += 1

                if progress and self._on_progress:
                    self._on_progress(current, total, time.time() - start_time)
                elif progress:
                    elapsed = time.time() - start_time
                    fps_actual = current / max(elapsed, 0.001)
                    eta = (total - current) / max(fps_actual, 0.001)
                    pct = (current / total) * 100
                    bar_len = 40
                    filled = int(bar_len * current / total)
                    bar = "█" * filled + "░" * (bar_len - filled)
                    sys.stdout.write(
                        f"\r  🐍 Ouroboros [{bar}] {pct:5.1f}% "
                        f"({current}/{total}) {fps_actual:.1f} fps "
                        f"ETA: {eta:.1f}s"
                    )
                    sys.stdout.flush()

            process.stdin.close()
            process.wait()

            if progress:
                elapsed = time.time() - start_time
                print(f"\n  ✅ Rendered in {elapsed:.1f}s → {output_path}")

            if preview:
                self._open_preview(output_path)

            return output_path

        except Exception as e:
            process.kill()
            raise RuntimeError(f"Render failed: {e}") from e

    def _render_gif(self, output_path: str, progress: bool) -> str:
        """Render as animated GIF."""
        frames = []
        total = self.total_frames
        current = 0
        start_time = time.time()

        for frame, frame_idx in self._generate_frames():
            # Convert RGBA to RGB for GIF (with transparency handling)
            if frame.mode == "RGBA":
                bg = Image.new("RGB", frame.size, (0, 0, 0))
                bg.paste(frame, mask=frame.split()[3])
                frame = bg
            frames.append(frame)
            current += 1

            if progress:
                elapsed = time.time() - start_time
                pct = (current / total) * 100
                sys.stdout.write(f"\r  🐍 Ouroboros GIF: {pct:.1f}% ({current}/{total})")
                sys.stdout.flush()

        duration_per_frame = int(1000 / self._fps)
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration_per_frame,
            loop=0,
            optimize=True,
        )

        if progress:
            elapsed = time.time() - start_time
            print(f"\n  ✅ GIF rendered in {elapsed:.1f}s → {output_path}")

        return output_path

    def render_frame(self, time_seconds: float) -> Image.Image:
        """Render a single frame at the given time (for preview)."""
        accumulated = 0.0
        for scene_idx, scene in enumerate(self._scenes):
            if accumulated + scene.duration > time_seconds:
                t_in_scene = time_seconds - accumulated
                frame_idx = int(t_in_scene * self._fps)
                return self._render_frame(scene_idx, frame_idx)
            accumulated += scene.duration
        return self._create_background()

    def render_preview(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fps: int = 15,
    ) -> Generator[Image.Image, None, None]:
        """Generate preview frames at lower resolution."""
        w = width or self.width // 2
        h = height or self.height // 2

        for frame, _ in self._generate_frames():
            yield frame.resize((w, h), Image.Resampling.LANCZOS)

    def _open_preview(self, path: str):
        """Open file in default player."""
        import platform
        system = platform.system()
        if system == "Darwin":
            subprocess.Popen(["open", path])
        elif system == "Windows":
            os.startfile(path)
        else:
            subprocess.Popen(["xdg-open", path])

    def to_dict(self) -> Dict[str, Any]:
        """Serialize composition to dict (for API/webhook)."""
        return {
            "width": self.width,
            "height": self.height,
            "fps": self._fps,
            "duration": self.duration,
            "total_frames": self.total_frames,
            "scenes": [
                {"name": s.name, "duration": s.duration}
                for s in self._scenes
            ],
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        return (
            f"Composition({self.width}x{self.height} @ {self._fps}fps, "
            f"{len(self._scenes)} scenes, {self.duration:.1f}s)"
        )
