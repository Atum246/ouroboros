"""
Audio Track — Audio management for compositions.

Supports background music, voiceover, SFX, and audio visualization.
"""

import os
import subprocess
import struct
from typing import Optional, List, Tuple
from PIL import Image, ImageDraw
import numpy as np


class AudioTrack:
    """
    Audio track for compositions.

    Args:
        source: Path to audio file (mp3, wav, ogg, etc.)
        volume: Volume level (0-1)
        start_at: When to start playing (seconds)
        fade_in: Fade in duration (seconds)
        fade_out: Fade out duration (seconds)
        loop: Whether to loop the audio
        trim_start: Trim from start (seconds)
        trim_end: Trim from end (seconds)

    Example::

        music = AudioTrack("bgm.mp3", volume=0.3, fade_in=1.0)
        comp.add_audio(music)
    """

    def __init__(
        self,
        source: str = "",
        volume: float = 1.0,
        start_at: float = 0.0,
        fade_in: float = 0.0,
        fade_out: float = 0.0,
        loop: bool = False,
        trim_start: float = 0.0,
        trim_end: float = 0.0,
    ):
        self.source = source
        self.volume = volume
        self.start_at = start_at
        self.fade_in = fade_in
        self.fade_out = fade_out
        self.loop = loop
        self.trim_start = trim_start
        self.trim_end = trim_end
        self._duration: Optional[float] = None

    @property
    def duration(self) -> float:
        """Get audio duration in seconds."""
        if self._duration is not None:
            return self._duration
        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", self.source,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            import json
            data = json.loads(result.stdout)
            self._duration = float(data.get("format", {}).get("duration", 0))
            return self._duration
        except Exception:
            return 0.0

    def get_ffmpeg_args(self) -> List[str]:
        """Get ffmpeg arguments for mixing this audio track."""
        args = ["-i", self.source]

        # Build filter
        filters = []

        # Volume
        if self.volume != 1.0:
            filters.append(f"volume={self.volume}")

        # Fade in
        if self.fade_in > 0:
            filters.append(f"afade=t=in:st=0:d={self.fade_in}")

        # Fade out
        if self.fade_out > 0 and self._duration:
            fade_start = self._duration - self.fade_out
            filters.append(f"afade=t=out:st={fade_start}:d={self.fade_out}")

        # Delay
        if self.start_at > 0:
            filters.append(f"adelay={int(self.start_at * 1000)}|{int(self.start_at * 1000)}")

        if filters:
            args.extend(["-af", ",".join(filters)])

        return args

    def get_waveform_data(self, num_points: int = 100) -> List[float]:
        """Extract waveform data for visualization."""
        try:
            cmd = [
                "ffmpeg", "-i", self.source, "-ac", "1", "-ar", "8000",
                "-f", "s16le", "-loglevel", "error", "-",
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=30)

            if result.returncode != 0:
                return [0.0] * num_points

            # Parse raw audio data
            samples = np.frombuffer(result.stdout, dtype=np.int16).astype(np.float64)

            # Normalize
            if len(samples) > 0:
                samples = samples / np.max(np.abs(samples))

            # Downsample to num_points
            chunk_size = max(1, len(samples) // num_points)
            waveform = []
            for i in range(num_points):
                start = i * chunk_size
                end = min(start + chunk_size, len(samples))
                if start < len(samples):
                    chunk = samples[start:end]
                    waveform.append(float(np.max(np.abs(chunk))))
                else:
                    waveform.append(0.0)

            return waveform
        except Exception:
            return [0.0] * num_points


def render_waveform(
    waveform_data: List[float],
    width: int = 800,
    height: int = 200,
    color: Tuple[int, int, int, int] = (0, 255, 200, 255),
    background: Tuple[int, int, int, int] = (0, 0, 0, 0),
    bar_width: int = 2,
    gap: int = 1,
) -> Image.Image:
    """
    Render waveform data as an image.

    Args:
        waveform_data: List of amplitude values (0-1)
        width: Image width
        height: Image height
        color: Bar color
        background: Background color
        bar_width: Width of each bar
        gap: Gap between bars

    Returns:
        RGBA Image
    """
    img = Image.new("RGBA", (width, height), background)
    draw = ImageDraw.Draw(img)

    num_bars = min(len(waveform_data), width // (bar_width + gap))
    if num_bars == 0:
        return img

    for i in range(num_bars):
        amplitude = waveform_data[i] if i < len(waveform_data) else 0
        bar_h = int(amplitude * height * 0.9)
        x = i * (bar_width + gap)
        y_top = (height - bar_h) // 2
        y_bottom = y_top + bar_h

        draw.rectangle([x, y_top, x + bar_width, y_bottom], fill=color)

    return img
