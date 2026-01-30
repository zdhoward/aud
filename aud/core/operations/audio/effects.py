from __future__ import annotations

from pathlib import Path

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


class StripSilence(AudioOperation):
    def __init__(
        self, silence_length: int = 1000, silence_threshold: int = -16, padding: int = 100
    ):
        self.silence_length = silence_length
        self.silence_threshold = silence_threshold
        self.padding = padding

    def apply(self, file: AudioFile) -> AudioFile:
        return file


class Watermark(AudioOperation):
    def __init__(self, watermark_file: str | Path, frequency_min: float, frequency_max: float):
        self.watermark_file = Path(watermark_file)
        self.frequency_min = frequency_min
        self.frequency_max = frequency_max

    def apply(self, file: AudioFile) -> AudioFile:
        return file


class AudioJoin(AudioOperation):
    def __init__(self, target_location: str | Path, file_format: str = "wav"):
        self.target_location = Path(target_location)
        self.file_format = file_format.lstrip(".").lower()

    def apply(self, file: AudioFile) -> AudioFile:
        # This operation combines multiple files into one
        # The result is the target location file
        return AudioFile(self.target_location)


class PrependAudio(AudioOperation):
    def __init__(self, audio_file: str | Path):
        self.audio_file = Path(audio_file)

    def apply(self, file: AudioFile) -> AudioFile:
        return file


class AppendAudio(AudioOperation):
    def __init__(self, audio_file: str | Path):
        self.audio_file = Path(audio_file)

    def apply(self, file: AudioFile) -> AudioFile:
        return file
