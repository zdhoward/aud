import pytest

from aud.aud import Dir
from aud.exceptions import ExportError


def test_export_for_amuse(populated_dir):
    """Test export_for with amuse platform."""
    d = Dir(populated_dir)
    d.config_set_extensions(["wav"])

    export_dir = populated_dir / "amuse_export"
    assert d.export_for("amuse", export_dir)

    # Check files were exported
    exported_files = sorted(p.name for p in export_dir.iterdir())
    assert "bloop.wav" in exported_files
    assert "song.wav" in exported_files


def test_export_for_cd(populated_dir):
    """Test export_for with cd platform."""
    d = Dir(populated_dir)
    d.config_set_extensions(["wav"])

    export_dir = populated_dir / "cd_export"
    assert d.export_for("cd", export_dir)

    # Check files were exported
    exported_files = sorted(p.name for p in export_dir.iterdir())
    assert "bloop.wav" in exported_files
    assert "song.wav" in exported_files


def test_export_for_wav(populated_dir):
    """Test export_for with wav platform."""
    d = Dir(populated_dir)
    d.config_set_extensions(["wav"])

    export_dir = populated_dir / "wav_export"
    assert d.export_for("wav", export_dir)

    # Check files were exported
    exported_files = sorted(p.name for p in export_dir.iterdir())
    assert "bloop.wav" in exported_files
    assert "song.wav" in exported_files


def test_export_for_mp3(populated_dir):
    """Test export_for with mp3 platform."""
    d = Dir(populated_dir)
    d.config_set_extensions(["wav"])

    export_dir = populated_dir / "mp3_export"
    assert d.export_for("mp3", export_dir)

    # Check files were exported and converted
    exported_files = sorted(p.name for p in export_dir.iterdir())
    assert "bloop.mp3" in exported_files
    assert "song.mp3" in exported_files


def test_export_for_unsupported_platform(populated_dir):
    """Test export_for raises error for unsupported platform."""
    d = Dir(populated_dir)
    d.config_set_extensions(["wav"])

    with pytest.raises(ExportError):
        d.export_for("unsupported_platform", populated_dir / "export")
