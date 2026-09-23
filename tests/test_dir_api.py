import pytest

from aud.aud import Dir


def test_get_single_returns_exact_file(populated_dir):
    d = Dir(populated_dir, extensions=["wav"])

    assert d.get_single(0) == "bloop.wav"
    assert d.get_single(1) == "song.wav"


def test_get_single_supports_negative_index(populated_dir):
    d = Dir(populated_dir, extensions=["wav"])

    assert d.get_single(-1) == "song.wav"
    assert d.get_single(-2) == "bloop.wav"


@pytest.mark.parametrize("num", [2, 3, -3, -100])
def test_get_single_rejects_out_of_range_index(populated_dir, num):
    d = Dir(populated_dir, extensions=["wav"])

    with pytest.raises(IndexError) as excinfo:
        d.get_single(num)

    assert "out of range" in str(excinfo.value)


def test_dir_rejects_missing_directory(tmp_path):
    with pytest.raises(FileNotFoundError) as excinfo:
        Dir(tmp_path / "does-not-exist")

    assert "Not a directory" in str(excinfo.value)


def test_dir_rejects_file_path(populated_dir):
    with pytest.raises(FileNotFoundError):
        Dir(populated_dir / "bloop.wav")
