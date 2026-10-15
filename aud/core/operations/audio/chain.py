from __future__ import annotations

from collections.abc import Iterable

from aud.core.effect_chain import validate_effects
from aud.core.models import AudioFile
from aud.core.operations.audio.base import AudioOperation
from aud.core.operations.audio.convert import ConvertFormat


class AudioChain(AudioOperation):
    """Apply ordered effects and optionally convert, publishing one output per file."""

    def __init__(self, effects: Iterable[AudioOperation], *, output: ConvertFormat | None = None):
        self.effects = tuple(effects)
        self.output = output
        validate_effects(self.effects)
        if output is not None and not isinstance(output, ConvertFormat):
            raise TypeError("AudioChain output must be a ConvertFormat")

    def apply(self, file: AudioFile) -> AudioFile:
        return self.output.apply(file) if self.output is not None else file
