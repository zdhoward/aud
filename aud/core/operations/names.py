from __future__ import annotations

from aud.core.models import AudioFile
from aud.core.operations.base import Operation


class Uppercase(Operation):
    def apply(self, file: AudioFile) -> AudioFile:
        new_name = f"{file.stem.upper()}{file.suffix}"
        return file.with_path(file.path.with_name(new_name))


class Lowercase(Operation):
    def apply(self, file: AudioFile) -> AudioFile:
        new_name = f"{file.stem.lower()}{file.suffix}"
        return file.with_path(file.path.with_name(new_name))


class Append(Operation):
    def __init__(self, suffix: str):
        self.suffix = suffix

    def apply(self, file: AudioFile) -> AudioFile:
        new_name = f"{file.stem}{self.suffix}{file.suffix}"
        return file.with_path(file.path.with_name(new_name))


class Prepend(Operation):
    def __init__(self, prefix: str):
        self.prefix = prefix

    def apply(self, file: AudioFile) -> AudioFile:
        new_name = f"{self.prefix}{file.name}"
        return file.with_path(file.path.with_name(new_name))


class Replace(Operation):
    def __init__(self, target: str, replacement: str):
        self.target = target
        self.replacement = replacement

    def apply(self, file: AudioFile) -> AudioFile:
        new_name = file.name.replace(self.target, self.replacement)
        return file.with_path(file.path.with_name(new_name))


class ReplaceSpaces(Operation):
    def __init__(self, replacement: str = "_"):
        self.replacement = replacement

    def apply(self, file: AudioFile) -> AudioFile:
        new_name = file.name.replace(" ", self.replacement)
        return file.with_path(file.path.with_name(new_name))


class Iterate(Operation):
    def __init__(self, start: int = 1, zerofill: int = 0, separator: str = "_"):
        self.start = start
        self.zerofill = zerofill
        self.separator = separator
        self._counter = start

    def apply(self, file: AudioFile) -> AudioFile:
        num = str(self._counter).zfill(self.zerofill)
        self._counter += 1
        new_name = f"{num}{self.separator}{file.name}"
        return file.with_path(file.path.with_name(new_name))
