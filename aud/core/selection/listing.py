from __future__ import annotations

import re

from aud.core.models import AudioFile
from aud.core.selection.policy import SelectionPolicy


class AllowlistPolicy(SelectionPolicy):
    def __init__(self, names: list[str] | None = None, regex: str | None = None):
        self.names = set(names or [])
        self.regex = re.compile(regex) if regex else None

    def include(self, file: AudioFile) -> bool:
        if file.name in self.names:
            return True
        if self.regex and self.regex.match(file.name):
            return True
        return False


class DenylistPolicy(SelectionPolicy):
    def __init__(self, names: list[str] | None = None, regex: str | None = None):
        self.names = set(names or [])
        self.regex = re.compile(regex) if regex else None

    def include(self, file: AudioFile) -> bool:
        if file.name in self.names:
            return False
        if self.regex and self.regex.match(file.name):
            return False
        return True
