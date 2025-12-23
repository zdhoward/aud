from __future__ import annotations

from pydub import AudioSegment
from pydub.effects import (
    high_pass_filter,
    invert_phase,
    low_pass_filter,
    normalize,
)

from aud.core.models import AudioFile
from aud.core.operations.audio.effects import (
    Fade,
    Gain,
    HighPassFilter,
    InvertPhase,
    LowPassFilter,
    Normalize,
    Pad,
)


class AudioAdapter:
    """
    Executes audio operations using pydub.
    """

    def execute(self, operation, inputs: list[AudioFile]) -> list[AudioFile]:
        if isinstance(operation, Normalize):
            return self._normalize(operation, inputs)
        if isinstance(operation, Fade):
            return self._fade(operation, inputs)
        if isinstance(operation, Pad):
            return self._pad(operation, inputs)
        if isinstance(operation, Gain):
            return self._gain(operation, inputs)
        if isinstance(operation, LowPassFilter):
            return self._lpf(operation, inputs)
        if isinstance(operation, HighPassFilter):
            return self._hpf(operation, inputs)
        if isinstance(operation, InvertPhase):
            return self._invert(operation, inputs)

        raise TypeError(f"Unsupported audio operation: {operation}")

    def _load(self, file: AudioFile) -> AudioSegment:
        return AudioSegment.from_file(file.path, file.extension)

    def _export(self, audio: AudioSegment, file: AudioFile) -> None:
        audio.export(file.path, format=file.extension)

    def _normalize(self, op: Normalize, files):
        for file in files:
            audio = self._load(file)
            for _ in range(op.passes):
                audio = normalize(audio, headroom=op.target_db)
            self._export(audio, file)
        return files

    def _fade(self, op: Fade, files):
        for file in files:
            audio = self._load(file)
            if op.fade_in > 0:
                audio = audio.fade_in(int(op.fade_in * 1000))
            if op.fade_out > 0:
                audio = audio.fade_out(int(op.fade_out * 1000))
            self._export(audio, file)
        return files

    def _pad(self, op: Pad, files):
        for file in files:
            audio = self._load(file)
            if op.pad_in > 0:
                audio = AudioSegment.silent(duration=int(op.pad_in * 1000)) + audio
            if op.pad_out > 0:
                audio = audio + AudioSegment.silent(duration=int(op.pad_out * 1000))
            self._export(audio, file)
        return files

    def _gain(self, op: Gain, files):
        for file in files:
            audio = self._load(file)
            audio = audio + op.amount_db
            self._export(audio, file)
        return files

    def _lpf(self, op: LowPassFilter, files):
        for file in files:
            audio = self._load(file)
            audio = low_pass_filter(audio, op.cutoff_hz)
            self._export(audio, file)
        return files

    def _hpf(self, op: HighPassFilter, files):
        for file in files:
            audio = self._load(file)
            audio = high_pass_filter(audio, op.cutoff_hz)
            self._export(audio, file)
        return files

    def _invert(self, op: InvertPhase, files):
        channels = {
            "both": (1, 1),
            "left": (1, 0),
            "right": (0, 1),
        }

        for file in files:
            audio = self._load(file)
            audio = invert_phase(audio, channels.get(op.channel, (1, 1)))
            self._export(audio, file)
        return files
