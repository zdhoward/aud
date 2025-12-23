from __future__ import annotations

from pathlib import Path

from aud.core.models import AudioFile
from aud.core.selection.policy import SelectionPolicy


class DirectoryScanner:
    def __init__(self, directory: Path, policy: SelectionPolicy):
        self.directory = Path(directory)
        self.policy = policy

    def scan(self) -> list[AudioFile]:
        files: list[AudioFile] = []

        for path in sorted(self.directory.iterdir()):
            if not path.is_file():
                continue

            audio = AudioFile(path)

            if self.policy.include(audio):
                files.append(audio)

        return files
