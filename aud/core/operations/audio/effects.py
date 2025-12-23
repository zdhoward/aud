from __future__ import annotations

from aud.core.models import AudioFile
from aud.core.operations.audio.base import AudioOperation


class Normalize(AudioOperation):
    def __init__(self, target_db: float = 0.1, passes: int = 1):
        self.target_db = target_db
        self.passes = passes

    def apply(self, file: AudioFile) -> AudioFile:
        return file


class Fade(AudioOperation):
    def __init__(self, fade_in: float = 0, fade_out: float = 0):
        self.fade_in = fade_in
        self.fade_out = fade_out

    def apply(self, file: AudioFile) -> AudioFile:
        return file


class Pad(AudioOperation):
    def __init__(self, pad_in: float = 0, pad_out: float = 0):
        self.pad_in = pad_in
        self.pad_out = pad_out

    def apply(self, file: AudioFile) -> AudioFile:
        return file


class Gain(AudioOperation):
    def __init__(self, amount_db: float):
        self.amount_db = amount_db

    def apply(self, file: AudioFile) -> AudioFile:
        return file


class LowPassFilter(AudioOperation):
    def __init__(self, cutoff_hz: int):
        self.cutoff_hz = cutoff_hz

    def apply(self, file: AudioFile) -> AudioFile:
        return file


class HighPassFilter(AudioOperation):
    def __init__(self, cutoff_hz: int):
        self.cutoff_hz = cutoff_hz

    def apply(self, file: AudioFile) -> AudioFile:
        return file


class InvertPhase(AudioOperation):
    def __init__(self, channel: str = "both"):
        self.channel = channel.lower()

    def apply(self, file: AudioFile) -> AudioFile:
        return file
