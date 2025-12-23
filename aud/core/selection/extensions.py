from __future__ import annotations

from aud.core.models import AudioFile
from aud.core.selection.policy import SelectionPolicy


class ExtensionPolicy(SelectionPolicy):
    def __init__(self, extensions: list[str]):
        self.extensions = {ext.lower().lstrip(".") for ext in extensions}

    def include(self, file: AudioFile) -> bool:
        return file.extension in self.extensions
