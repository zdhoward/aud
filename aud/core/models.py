from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class AudioFile:
    """
    Immutable representation of an audio file on disk.

    This object represents identity and metadata only.
    It does NOT perform IO or mutation.
    """

    path: Path

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def stem(self) -> str:
        return self.path.stem

    @property
    def suffix(self) -> str:
        return self.path.suffix

    @property
    def extension(self) -> str:
        return self.path.suffix.lstrip(".").lower()

    def with_path(self, new_path: Path) -> AudioFile:
        return AudioFile(new_path)
