from __future__ import annotations

from pathlib import Path

from aud.core.models import AudioFile
from aud.core.operations.base import Operation


class Copy(Operation):
    def __init__(self, target_dir: Path):
        self.target_dir = Path(target_dir)

    def apply(self, file: AudioFile) -> AudioFile:
        new_path = self.target_dir / file.path.name
        return file.with_path(new_path)


class Move(Operation):
    def __init__(self, target_dir: Path):
        self.target_dir = Path(target_dir)

    def apply(self, file: AudioFile) -> AudioFile:
        new_path = self.target_dir / file.path.name
        return file.with_path(new_path)


class Backup(Operation):
    """
    Semantic alias of Copy, kept for clarity.
    """

    def __init__(self, target_dir: Path):
        self.target_dir = Path(target_dir)

    def apply(self, file: AudioFile) -> AudioFile:
        new_path = self.target_dir / file.path.name
        return file.with_path(new_path)
