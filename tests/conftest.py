import shutil
from pathlib import Path

import pytest


@pytest.fixture
def mock_assets() -> Path:
    return Path(__file__).parent.parent / "mock_assets"


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
