from __future__ import annotations

from pathlib import Path

from aud.core.models import AudioFile
from aud.core.safety import is_link
from aud.core.selection.policy import SelectionPolicy


class DirectoryScanner:
    def __init__(self, directory: Path, policy: SelectionPolicy, *, follow_symlinks=False):
        self.directory = Path(directory)
        self.policy = policy
        self.follow_symlinks = follow_symlinks

    def scan(self) -> list[AudioFile]:
        files: list[AudioFile] = []

        for path in sorted(self.directory.iterdir()):
            if is_link(path) and not self.follow_symlinks:
                continue
            if not path.is_file():
                continue

            audio = AudioFile(path)

            if self.policy.include(audio):
                files.append(AudioFile(path.resolve()) if self.follow_symlinks else audio)

        return files
