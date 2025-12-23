from __future__ import annotations

from pydub import AudioSegment
from pydub.effects import apply_gain_stereo

from aud.core.models import AudioFile
from aud.core.operations.audio.convert import (
    ConvertFormat,
    ConvertToMono,
    ConvertToStereo,
)


class ConversionAdapter:
    """
    Executes format / channel conversions using pydub.
    """

    def execute(self, operation, inputs: list[AudioFile]) -> list[AudioFile]:
        if isinstance(operation, ConvertFormat):
            return self._convert_format(operation, inputs)
        if isinstance(operation, ConvertToMono):
            return self._mono(inputs)
        if isinstance(operation, ConvertToStereo):
            return self._stereo(inputs)

        raise TypeError(f"Unsupported conversion operation: {operation}")

    def _load(self, file: AudioFile) -> AudioSegment:
        return AudioSegment.from_file(file.path, file.extension)

    def _export(self, audio: AudioSegment, file: AudioFile, format: str | None = None, **kwargs):
        audio.export(file.path, format=format or file.extension, **kwargs)

    def _convert_format(self, op: ConvertFormat, files):
        outputs: list[AudioFile] = []

        for file in files:
            audio = self._load(file)

            if op.sample_rate:
                audio = audio.set_frame_rate(op.sample_rate)

            if op.bit_depth:
                audio = audio.set_sample_width(self._bit_depth_to_width(op.bit_depth))

            self._export(
                audio,
                file.with_path(file.path.with_suffix(f".{op.target_format}")),
                format=op.target_format,
                tags=op.tags,
                cover=op.cover,
            )

            outputs.append(file.with_path(file.path.with_suffix(f".{op.target_format}")))

        return outputs

    def _mono(self, files):
        for file in files:
            audio = self._load(file)
            audio = audio.set_channels(1)
            self._export(audio, file)
        return files

    def _stereo(self, files):
        for file in files:
            audio = self._load(file)
            audio = apply_gain_stereo(audio, 0, 0)
            self._export(audio, file)
        return files

    @staticmethod
    def _bit_depth_to_width(bit_depth: int) -> int:
        if bit_depth == 8:
            return 1
        if bit_depth == 16:
            return 2
        # pydub converts 24/32 → 32 internally
        if bit_depth in (24, 32):
            return 4
        raise ValueError(f"Unsupported bit depth: {bit_depth}")
