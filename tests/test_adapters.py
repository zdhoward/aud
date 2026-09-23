from pathlib import Path

import pytest

from aud.core.adapters.audio import AudioAdapter
from aud.core.adapters.convert import ConversionAdapter
from aud.core.adapters.filesystem import FileSystemAdapter
from aud.core.models import AudioFile
from aud.core.operations.archive import Zip
from aud.core.operations.base import Operation
from aud.core.operations.files import Backup, Copy, Move


class _Unsupported(Operation):
    def apply(self, file: AudioFile) -> AudioFile:
        return file


def test_filesystem_adapter_rejects_unknown_operation():
    with pytest.raises(TypeError):
        FileSystemAdapter().execute(_Unsupported(), [])


def test_audio_adapter_rejects_unknown_operation():
    with pytest.raises(TypeError):
        AudioAdapter().execute(_Unsupported(), [])


def test_conversion_adapter_rejects_unknown_operation():
    with pytest.raises(TypeError):
        ConversionAdapter().execute(_Unsupported(), [])


def test_file_operations_are_pure():
    file = AudioFile(Path("dir") / "song.wav")

    assert Copy(Path("target")).apply(file) == AudioFile(Path("target") / "song.wav")
    assert Move(Path("target")).apply(file) == AudioFile(Path("target") / "song.wav")
    assert Backup(Path("target")).apply(file) == AudioFile(Path("target") / "song.wav")


def test_zip_apply_returns_archive():
    result = Zip(Path("archive.zip")).apply(AudioFile(Path("dir") / "song.wav"))

    assert result == AudioFile(Path("archive.zip"))


@pytest.mark.parametrize(
    "bit_depth,expected_width",
    [
        (8, 1),
        (16, 2),
        (24, 4),
        (32, 4),
    ],
)
def test_bit_depth_to_width(bit_depth, expected_width):
    assert ConversionAdapter._bit_depth_to_width(bit_depth) == expected_width


def test_bit_depth_to_width_rejects_unsupported_depth():
    with pytest.raises(ValueError):
        ConversionAdapter._bit_depth_to_width(12)
