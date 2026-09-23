import pytest

from aud.aud import Dir
from aud.exceptions import AudioFXError, ConvertError, FileError


def test_error_message_formatting():
    err = FileError("copy", ValueError("boom"))

    assert str(err) == "Copy failure: boom"


def test_convert_error_wraps_bad_bit_depth(populated_dir):
    d = Dir(populated_dir, extensions=["wav"])

    with pytest.raises(ConvertError):
        d.convert_to_flac(bit_depth=12)


def test_audio_error_wraps_missing_file(populated_dir):
    d = Dir(populated_dir, extensions=["wav"])
    (populated_dir / "song.wav").unlink()

    with pytest.raises(AudioFXError):
        d.afx_gain(3)
