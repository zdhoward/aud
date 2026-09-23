import pytest
from pydub import AudioSegment

from aud.aud import Dir
from aud.exceptions import ExportError


def test_export_for_amuse(populated_dir):
    d = Dir(populated_dir)
    d.config_set_extensions(["wav"])

    export_dir = populated_dir / "amuse_export"
    assert d.export_for("amuse", export_dir)

    # Export directory contains only the converted files
    assert sorted(p.name for p in export_dir.iterdir()) == ["bloop.wav", "song.wav"]

    # Amuse preset: 44.1 kHz, 16-bit
    for name in ["bloop.wav", "song.wav"]:
        audio = AudioSegment.from_file(export_dir / name)
        assert audio.frame_rate == 44100
        assert audio.sample_width == 2


def test_export_for_cd(populated_dir):
    d = Dir(populated_dir)
    d.config_set_extensions(["wav"])

    export_dir = populated_dir / "cd_export"
    assert d.export_for("cd", export_dir)

    assert sorted(p.name for p in export_dir.iterdir()) == ["bloop.wav", "song.wav"]

    # CD preset: 44.1 kHz, 16-bit
    for name in ["bloop.wav", "song.wav"]:
        audio = AudioSegment.from_file(export_dir / name)
        assert audio.frame_rate == 44100
        assert audio.sample_width == 2


def test_export_for_wav(populated_dir):
    d = Dir(populated_dir)
    d.config_set_extensions(["wav"])

    export_dir = populated_dir / "wav_export"
    assert d.export_for("wav", export_dir)

    exported_files = sorted(p.name for p in export_dir.iterdir())
    assert exported_files == ["bloop.wav", "song.wav"]


def test_export_for_mp3(populated_dir):
    d = Dir(populated_dir)
    d.config_set_extensions(["wav"])

    export_dir = populated_dir / "mp3_export"
    assert d.export_for("mp3", export_dir)

    # Only converted files remain; intermediate copies are removed
    assert sorted(p.name for p in export_dir.iterdir()) == ["bloop.mp3", "song.mp3"]

    # The selection and the source files are untouched
    assert sorted(d.get_all()) == ["bloop.wav", "song.wav"]
    assert (populated_dir / "bloop.wav").exists()
    assert (populated_dir / "song.wav").exists()


def test_export_for_unsupported_platform(populated_dir):
    d = Dir(populated_dir)
    d.config_set_extensions(["wav"])

    with pytest.raises(ExportError) as excinfo:
        d.export_for("unsupported_platform", populated_dir / "export")

    assert "Unsupported platform" in str(excinfo.value)


def test_export_for_empty_selection_is_noop(populated_dir):
    d = Dir(populated_dir)
    d.config_set_extensions(["flac"])  # selects nothing

    export_dir = populated_dir / "export"
    assert d.export_for("wav", export_dir)
    assert not export_dir.exists()
