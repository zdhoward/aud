"""Tests for new audio operations added for backward compatibility."""

import pytest
from pydub import AudioSegment

from aud.aud import Dir
from aud.exceptions import AudioFXError


def test_afx_strip_silence(populated_dir):
    """Test strip_silence operation."""
    d = Dir(populated_dir, extensions=["wav"])

    # Basic strip silence with defaults
    assert d.afx_strip_silence()

    # With custom parameters
    assert d.afx_strip_silence(silence_length=500, silence_threshold=-20, padding=50)


def test_afx_watermark(populated_dir, mock_assets):
    """Test watermark operation."""
    d = Dir(populated_dir, extensions=["wav"])

    # Use bloop.wav as watermark for song.wav
    watermark_file = mock_assets / "bloop.wav"

    # Only watermark song.wav
    d.config_set_allowlist(names=["song.wav"])

    assert d.afx_watermark(watermark_file=watermark_file, frequency_min=1.0, frequency_max=3.0)


def test_afx_join(populated_dir):
    """Test audio join operation."""
    d = Dir(populated_dir, extensions=["wav"])

    output_file = populated_dir / "joined.wav"
    assert d.afx_join(target_location=output_file, format="wav")

    # Verify output file was created
    assert output_file.exists()


def test_afx_prepend(populated_dir, mock_assets):
    """Test prepend audio operation."""
    d = Dir(populated_dir, extensions=["wav"])

    # Only prepend to song.wav
    d.config_set_allowlist(names=["song.wav"])

    # Use bloop.wav as the audio to prepend
    prepend_file = mock_assets / "bloop.wav"

    assert d.afx_prepend(file=prepend_file)


def test_afx_append(populated_dir, mock_assets):
    """Test append audio operation."""
    d = Dir(populated_dir, extensions=["wav"])

    # Only append to song.wav
    d.config_set_allowlist(names=["song.wav"])

    # Use bloop.wav as the audio to append
    append_file = mock_assets / "bloop.wav"

    assert d.afx_append(file=append_file)


def test_afx_join_different_format(populated_dir):
    """Test audio join with different output format."""
    d = Dir(populated_dir, extensions=["wav"])

    output_file = populated_dir / "joined.mp3"
    assert d.afx_join(target_location=output_file, format="mp3")

    # Verify output file was created
    assert output_file.exists()


def test_multiple_audio_operations_chained(populated_dir):
    """Test chaining multiple audio operations."""
    d = Dir(populated_dir, extensions=["wav"])

    # Chain multiple operations
    assert d.afx_normalize(target_level=-0.5)
    assert d.afx_fade(in_fade=0.5, out_fade=1.0)
    assert d.afx_strip_silence(silence_threshold=-30)
    assert d.afx_pad(in_pad=0.1, out_pad=0.1)


def test_afx_join_duration_is_exact_sum(populated_dir, mock_assets):
    """Joined output must not gain or lose audio (regression: 1ms silence prefix)."""
    d = Dir(populated_dir, extensions=["wav"])
    output_file = populated_dir / "joined.wav"
    assert d.afx_join(target_location=output_file, format="wav")

    bloop = AudioSegment.from_file(mock_assets / "bloop.wav")
    song = AudioSegment.from_file(mock_assets / "song.wav")
    joined = AudioSegment.from_file(output_file)
    assert len(joined) == len(bloop) + len(song)


def test_afx_join_empty_selection_is_noop(populated_dir):
    d = Dir(populated_dir)
    d.config_set_extensions(["flac"])  # selects nothing

    output_file = populated_dir / "joined.wav"
    assert d.afx_join(target_location=output_file, format="wav")
    assert not output_file.exists()


def test_afx_watermark_rejects_invalid_interval(populated_dir, mock_assets):
    d = Dir(populated_dir, extensions=["wav"])

    with pytest.raises(AudioFXError):
        d.afx_watermark(mock_assets / "bloop.wav", frequency_min=3.0, frequency_max=1.0)

    with pytest.raises(AudioFXError):
        d.afx_watermark(mock_assets / "bloop.wav", frequency_min=0, frequency_max=1.0)
