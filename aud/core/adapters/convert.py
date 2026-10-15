from __future__ import annotations

from aud.core.adapters.batch import BatchAdapter
from aud.core.ffmpeg import FFmpegEngine
from aud.core.models import AudioFile
from aud.core.operations.audio.convert import (
    ConvertFormat,
    ConvertToMono,
    ConvertToStereo,
)
from aud.core.safety import destinations


class ConversionAdapter(BatchAdapter):
    """
    Executes format/channel conversions without decoding tracks into Python.
    """

    def __init__(self, *, media_limits=None, **kwargs):
        super().__init__(**kwargs)
        self.engine = FFmpegEngine(media_limits, cancel=self.cancel)

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
            conversion = operation
            if isinstance(operation, (ConvertToMono, ConvertToStereo)):
                conversion = ConvertFormat(
                    entry.source.suffix.lstrip("."),
                    channels=1 if isinstance(operation, ConvertToMono) else 2,
                )
            return self.engine.convert(entry.source, conversion, entry)

        return self.perform(operation, entries, process)

    @staticmethod
    def _bit_depth_to_width(bit_depth: int) -> int:
        if bit_depth == 8:
            return 1
        if bit_depth == 16:
            return 2
        if bit_depth == 24:
            return 3
        if bit_depth == 32:
            return 4
        raise ValueError(f"Unsupported bit depth: {bit_depth} " "(use 8, 16, 24, or 32)")
