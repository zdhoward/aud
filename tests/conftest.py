import math
import shutil
import struct
import wave
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def mock_assets(tmp_path_factory) -> Path:
    directory = tmp_path_factory.mktemp("synthetic-audio")
    for name, duration in [("bloop.wav", 0.25), ("song.wav", 6.0)]:
        samples = bytearray()
        for index in range(int(44100 * duration)):
            value = int(8000 * math.sin(2 * math.pi * 440 * index / 44100))
            if name == "song.wav" and 2 <= index / 44100 < 2.75:
                value = 0
            samples.extend(struct.pack("<hh", value, value))
        with wave.open(str(directory / name), "wb") as audio:
            audio.setnchannels(2)
            audio.setsampwidth(2)
            audio.setframerate(44100)
            audio.writeframes(samples)
    return directory


def touch(path: Path) -> None:
    path.write_text("")


@pytest.fixture
def populated_dir(tmp_path: Path, mock_assets: Path) -> Path:
    """
    Creates a directory with:
    - text files
    - wav files copied from mock_assets
    """
    touch(tmp_path / "test.txt")
    touch(tmp_path / "abc.txt")

    shutil.copy(mock_assets / "bloop.wav", tmp_path / "bloop.wav")
    shutil.copy(mock_assets / "song.wav", tmp_path / "song.wav")

    return tmp_path
