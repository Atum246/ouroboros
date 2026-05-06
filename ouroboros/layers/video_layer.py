"""
Video Layer — Embed video clips as layers.

Extracts frames from video files and composites them.
Requires ffmpeg to be installed.
"""

import os
import subprocess
import tempfile
from typing import Any, Dict, Optional, Tuple
from PIL import Image

from ouroboros.layers.base import Layer


class VideoLayer(Layer):
    """
    Video layer for embedding video clips.

    Args:
        source: Path to video file
        loop: Whether to loop the video
        speed: Playback speed (1.0 = normal)
        start_at: Start time in the source video (seconds)
        volume: Volume for embedded audio (0-1)

    Example::

        clip = VideoLayer("clip.mp4", x=100, y=100, loop=True)
        clip.animate("opacity", 0, 1, 0, 0.5)
    """

    def __init__(
        self,
        source: str = "",
        loop: bool = False,
        speed: float = 1.0,
        start_at: float = 0.0,
        volume: float = 1.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.source = source
        self.loop = loop
        self.speed = speed
        self.start_at = start_at
        self.volume = volume
        self._frame_cache: Dict[int, Image.Image] = {}
        self._video_fps: Optional[int] = None
        self._video_duration: Optional[float] = None
        self._temp_dir: Optional[str] = None

    def _probe_video(self):
        """Get video metadata."""
        if self._video_fps is not None:
            return

        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_streams", "-show_format", self.source,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            import json
            data = json.loads(result.stdout)

            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video":
                    # Parse FPS
                    r_frame_rate = stream.get("r_frame_rate", "30/1")
                    num, den = map(int, r_frame_rate.split("/"))
                    self._video_fps = num / den if den else 30
                    break

            self._video_duration = float(data.get("format", {}).get("duration", 0))
        except Exception:
            self._video_fps = 30
            self._video_duration = 0

    def _extract_frame(self, frame_idx: int) -> Optional[Image.Image]:
        """Extract a single frame from the video."""
        if frame_idx in self._frame_cache:
            return self._frame_cache[frame_idx]

        self._probe_video()

        # Calculate timestamp
        if self._video_fps and self._video_fps > 0:
            timestamp = self.start_at + (frame_idx / self._video_fps) * self.speed
        else:
            timestamp = self.start_at + frame_idx * self.speed / 30

        if self._video_duration and timestamp > self._video_duration:
            if self.loop:
                timestamp = timestamp % self._video_duration
            else:
                return None

        try:
            # Extract frame using ffmpeg
            cmd = [
                "ffmpeg", "-ss", str(timestamp), "-i", self.source,
                "-vframes", "1", "-f", "image2pipe", "-vcodec", "png",
                "-loglevel", "error", "-",
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=10)

            if result.returncode == 0 and result.stdout:
                import io
                img = Image.open(io.BytesIO(result.stdout)).convert("RGBA")

                # Resize if layer has dimensions
                if self._width and self._height:
                    img = img.resize((self._width, self._height), Image.Resampling.LANCZOS)

                self._frame_cache[frame_idx] = img
                return img
        except Exception:
            pass

        return None

    def _render_content(
        self,
        t: float,
        width: int,
        height: int,
        fps: int,
        frame_idx: int,
        props: Dict[str, Any],
    ) -> Optional[Image.Image]:
        if not self.source or not os.path.exists(self.source):
            return None

        return self._extract_frame(frame_idx)

    def __del__(self):
        """Cleanup temp directory."""
        if self._temp_dir and os.path.exists(self._temp_dir):
            import shutil
            try:
                shutil.rmtree(self._temp_dir)
            except Exception:
                pass
