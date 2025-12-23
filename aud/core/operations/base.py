from __future__ import annotations

from abc import ABC, abstractmethod

from aud.core.models import AudioFile


class Operation(ABC):
    """
    Base class for all operations.

    Operations describe intent and return new AudioFile(s).
    They do NOT perform filesystem or audio IO.
    """

    @abstractmethod
    def apply(self, file: AudioFile) -> AudioFile | list[AudioFile]:
        raise NotImplementedError
