from __future__ import annotations

from aud.core.models import AudioFile
from aud.core.operations.audio.base import AudioOperation


class ConvertFormat(AudioOperation):
    def __init__(
        self,
        target_format: str,
        sample_rate: int | None = None,
        bit_depth: int | None = None,
        tags: dict | None = None,
        cover: str | None = None,
    ):
        self.target_format = target_format.lstrip(".").lower()
        self.sample_rate = sample_rate
        self.bit_depth = bit_depth
        self.tags = tags
        self.cover = cover

    def apply(self, file: AudioFile) -> AudioFile:
        new_path = file.path.with_suffix(f".{self.target_format}")
        return file.with_path(new_path)


class ConvertToMono(AudioOperation):
    def apply(self, file: AudioFile) -> AudioFile:
        return file


class ConvertToStereo(AudioOperation):
    def apply(self, file: AudioFile) -> AudioFile:
        return file
