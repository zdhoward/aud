from __future__ import annotations

from aud.core.adapters.audio_io import AudioIO
from aud.core.models import AudioFile
from aud.core.operations.audio.convert import (
    ConvertFormat,
    ConvertToMono,
    ConvertToStereo,
)
from aud.core.safety import destinations


class ConversionAdapter(AudioIO):
    """
    Executes format / channel conversions using pydub.
    """

    def export_to(self, operation, inputs, directory):
        pairs = [
            (f.path, directory / f.path.with_suffix(f".{operation.target_format}").name)
            for f in inputs
        ]
        entries = destinations(pairs, self.overwrite, protected=[f.path for f in inputs])
        return self.execute_resolved(operation, inputs, entries)

    def execute(self, operation, inputs: list[AudioFile]) -> list[AudioFile]:
        if not isinstance(operation, (ConvertFormat, ConvertToMono, ConvertToStereo)):
            raise TypeError(f"Unsupported conversion operation: {operation}")
        pairs = [(f.path, operation.apply(f).path) for f in inputs]
        entries = destinations(
            pairs, self.overwrite, protected=[f.path for f in inputs], in_place=True
        )
        return self.execute_resolved(operation, inputs, entries)

    def execute_resolved(self, operation, inputs, entries):
        def process(entry):
            self.destination = entry
            self._execute_conversion(operation, [AudioFile(entry.source)])

        return self.perform(operation, entries, process)

    def _execute_conversion(self, operation, inputs):
        if isinstance(operation, ConvertFormat):
            return self._convert_format(operation, inputs)
        if isinstance(operation, ConvertToMono):
            return self._mono(inputs)
        if isinstance(operation, ConvertToStereo):
            return self._stereo(inputs)

        raise TypeError(f"Unsupported conversion operation: {operation}")

    def _convert_format(self, op: ConvertFormat, files):
        outputs: list[AudioFile] = []

        for file in files:
            audio = self._load(file)

            if op.sample_rate:
                audio = audio.set_frame_rate(op.sample_rate)

            if op.bit_depth:
                audio = audio.set_sample_width(self._bit_depth_to_width(op.bit_depth))

            target = file.with_path(file.path.with_suffix(f".{op.target_format}"))
            export_kwargs = {}
            if op.bit_rate:
                export_kwargs["bitrate"] = f"{op.bit_rate}k"
            self._export(
                audio,
                target,
                format=op.target_format,
                tags=op.tags,
                cover=op.cover,
                **export_kwargs,
            )

            outputs.append(target)

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
            audio = audio.set_channels(2)
            self._export(audio, file)
        return files

    @staticmethod
    def _bit_depth_to_width(bit_depth: int) -> int:
        if bit_depth == 8:
            return 1
        if bit_depth == 16:
            return 2
        if bit_depth == 32:
            return 4
        raise ValueError(
            f"Unsupported bit depth: {bit_depth} "
            f"(pydub cannot encode {bit_depth}-bit audio; use 8, 16, or 32)"
        )
