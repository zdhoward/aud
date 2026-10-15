from __future__ import annotations

from pathlib import Path

from aud.core.ffmpeg import validate_conversion
from aud.core.models import AudioFile
from aud.core.operations.audio.base import AudioOperation


class ConvertFormat(AudioOperation):
    def __init__(
        self,
        target_format: str,
        sample_rate: int | None = None,
        bit_depth: int | None = None,
        bit_rate: int | None = None,
        tags: dict | None = None,
        cover: str | None = None,
        *,
        output_directory: str | Path | None = None,
        profile: str | None = None,
        allow_lossy: bool = False,
        drop_artwork: bool = False,
        channels: int | None = None,
    ):
        self.target_format = target_format.lstrip(".").lower()
        self.sample_rate = sample_rate
        self.bit_depth = bit_depth
        self.bit_rate = bit_rate
        self.tags = tags
        self.cover = cover
        self.output_directory = Path(output_directory) if output_directory is not None else None
        self.profile = profile
        self.allow_lossy = allow_lossy
        self.drop_artwork = drop_artwork
        self.channels = channels
        validate_conversion(self)

    def apply(self, file: AudioFile) -> AudioFile:
        new_path = file.path.with_suffix(f".{self.target_format}")
        if self.output_directory is not None:
            new_path = self.output_directory / new_path.name
        return file.with_path(new_path)


class ConvertToMono(AudioOperation):
    def apply(self, file: AudioFile) -> AudioFile:
        return file


class ConvertToStereo(AudioOperation):
    def apply(self, file: AudioFile) -> AudioFile:
        return file
