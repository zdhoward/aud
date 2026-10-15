from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

from aud.core.metadata import AudioMetadata
from aud.core.models import AudioFile
from aud.core.naming import MissingNamingField, NamingProfile
from aud.core.operations.base import Operation
from aud.core.safety import path_key


class NameWithProfile(Operation):
    def __init__(
        self,
        profile: NamingProfile,
        output_directory: str | Path,
        metadata: Mapping[str | Path, AudioMetadata],
        *,
        copy: bool = False,
    ):
        self.profile = profile
        self.output_directory = Path(os.path.abspath(output_directory))
        self.copy = copy
        self._metadata: dict[str, AudioMetadata] = {}
        for path, value in metadata.items():
            key = path_key(Path(path))
            if key in self._metadata:
                raise ValueError("Metadata paths collide after case/Unicode normalization")
            if not isinstance(value, AudioMetadata):
                raise TypeError("Naming metadata must contain AudioMetadata values")
            self._metadata[key] = value
        self.validate()

    def validate(self):
        if not isinstance(self.profile, NamingProfile) or not isinstance(self.copy, bool):
            raise TypeError("Expected a NamingProfile and boolean copy option")
        if not isinstance(self.output_directory, Path) or not self.output_directory.is_absolute():
            raise ValueError("Naming output_directory must remain an absolute Path")
        self.profile.validate()

    def target(self, file: AudioFile) -> Path | None:
        self.validate()
        metadata = self._metadata.get(path_key(file.path))
        try:
            if metadata is None:
                raise MissingNamingField(f"No naming metadata for {file.path}")
            return self.output_directory / self.profile.render(metadata, file.extension)
        except MissingNamingField:
            if self.profile.missing == "skip":
                return None
            raise

    def apply(self, file: AudioFile) -> AudioFile:
        return file.with_path(self.target(file) or file.path)
