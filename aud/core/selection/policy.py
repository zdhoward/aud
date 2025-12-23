from __future__ import annotations

from abc import ABC, abstractmethod

from aud.core.models import AudioFile


class SelectionPolicy(ABC):
    """
    Determines whether an AudioFile should be included.
    """

    @abstractmethod
    def include(self, file: AudioFile) -> bool:
        raise NotImplementedError
