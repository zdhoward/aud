from __future__ import annotations

from pathlib import Path

from aud.core.models import AudioFile
from aud.core.operations.base import Operation


class Zip(Operation):
    def __init__(self, archive_path: Path):
        self.archive_path = Path(archive_path)

    def apply(self, file: AudioFile) -> AudioFile:
        """
        Zip is a terminal operation.

        It returns a reference to the archive itself.
        Execution logic will collect inputs elsewhere.
        """
        return AudioFile(self.archive_path)
