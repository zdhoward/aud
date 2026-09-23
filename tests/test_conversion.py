import pytest
from pydub import AudioSegment

from aud.aud import Dir
from aud.exceptions import ConvertError


def test_conversion_basic(populated_dir):
    d = Dir(populated_dir)
    d.config_set_extensions(["wav"])

    assert d.convert_format("mp3")
    d.config_set_extensions(["mp3"])
    assert len(d.get_all()) == 2

    assert d.convert_mono()
    mono = AudioSegment.from_file(populated_dir / "bloop.mp3")
    assert mono.channels == 1

    assert d.convert_stereo()
    stereo = AudioSegment.from_file(populated_dir / "bloop.mp3")
    assert stereo.channels == 2


def test_bit_rate_controls_encoded_bitrate(populated_dir):
    d = Dir(populated_dir, extensions=["wav"])
    assert d.convert_to_mp3(bit_rate=32)
    low = (populated_dir / "bloop.mp3").stat().st_size

    d.config_set_extensions(["mp3"])
    assert d.convert_to_mp3(bit_rate=320)
    high = (populated_dir / "bloop.mp3").stat().st_size

    assert high > low


def test_unsupported_bit_depth_raises_clear_error(populated_dir):
    d = Dir(populated_dir, extensions=["wav"])

    with pytest.raises(ConvertError) as excinfo:
        d.convert_to_wav(bit_depth=24)

    assert "Unsupported bit depth: 24" in str(excinfo.value)
