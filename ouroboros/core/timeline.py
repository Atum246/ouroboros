"""
Timeline — Manages scene sequencing and timing.

Handles ordering scenes, calculating offsets, and managing transitions.
"""

from typing import List, Optional, Dict, Any, Tuple
from ouroboros.core.scene import Scene


class TimelineEntry:
    """A scene entry on the timeline."""

    def __init__(
        self,
        scene: Scene,
        start_time: float = 0.0,
        index: int = 0,
    ):
        self.scene = scene
        self.start_time = start_time
        self.index = index

    @property
    def end_time(self) -> float:
        return self.start_time + self.scene.duration

    def contains(self, time: float) -> bool:
        return self.start_time <= time < self.end_time

    def __repr__(self) -> str:
        return f"TimelineEntry({self.scene.name}, {self.start_time:.1f}s-{self.end_time:.1f}s)"


class Timeline:
    """
    Manages the sequencing of scenes.

    Tracks start/end times and provides lookup by time.
    """

    def __init__(self):
        self._entries: List[TimelineEntry] = []
        self._current_offset: float = 0.0

    def add_scene(self, scene: Scene, after: int = -1):
        """
        Add a scene to the timeline.

        Args:
            scene: The scene to add
            after: Index to insert after (-1 for append)
        """
        if after >= 0 and after < len(self._entries):
            # Insert after specified entry
            entry = TimelineEntry(
                scene=scene,
                start_time=self._entries[after].end_time,
                index=len(self._entries),
            )
            self._entries.insert(after + 1, entry)
        else:
            entry = TimelineEntry(
                scene=scene,
                start_time=self._current_offset,
                index=len(self._entries),
            )
            self._entries.append(entry)

        # Recalculate offsets
        self._recalculate_offsets()

    def remove_scene(self, index: int):
        """Remove a scene by index."""
        if 0 <= index < len(self._entries):
            self._entries.pop(index)
            self._recalculate_offsets()

    def _recalculate_offsets(self):
        """Recalculate start times for all entries."""
        offset = 0.0
        for entry in self._entries:
            entry.start_time = offset
            offset += entry.scene.duration

    def get_entry_at(self, time: float) -> Optional[TimelineEntry]:
        """Get the timeline entry at a specific time."""
        for entry in self._entries:
            if entry.contains(time):
                return entry
        return None

    def get_scene_at(self, time: float) -> Optional[Scene]:
        """Get the scene at a specific time."""
        entry = self.get_entry_at(time)
        return entry.scene if entry else None

    @property
    def duration(self) -> float:
        """Total timeline duration in seconds."""
        if not self._entries:
            return 0.0
        return self._entries[-1].end_time

    @property
    def entries(self) -> List[TimelineEntry]:
        """All timeline entries."""
        return list(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __repr__(self) -> str:
        return f"Timeline({len(self._entries)} scenes, {self.duration:.1f}s)"
