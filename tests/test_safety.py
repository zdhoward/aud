from pathlib import Path

import pytest
from pydub import AudioSegment
from pydub.utils import mediainfo_json

from aud import Dir
from aud.exceptions import AudioFXError, ConvertError, ExportError, FileError, FilenameError


def test_default_copy_refuses_collision_before_copying_any_file(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "a.txt").write_text("a")
    (source / "b.txt").write_text("b")
    (target / "b.txt").write_text("original")
    d = Dir(source, extensions=["txt"])
    with pytest.raises(FileError, match="exists"):
        d.copy(target)
    assert not (target / "a.txt").exists()
    assert (target / "b.txt").read_text() == "original"


@pytest.mark.parametrize("policy", ["skip", "overwrite", "auto-rename"])
def test_copy_collision_policies(tmp_path, policy):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "song.txt").write_text("new")
    (target / "song.txt").write_text("old")
    d = Dir(source, extensions=["txt"], overwrite=policy)
    assert d.copy(target)
    if policy == "overwrite":
        assert (target / "song.txt").read_text() == "new"
    else:
        assert (target / "song.txt").read_text() == "old"
    if policy == "auto-rename":
        assert (target / "song (1).txt").read_text() == "new"
    if policy == "skip":
        assert d.last_result.items[0].status == "skipped"
        assert d.get_all() == ["song.txt"]
        assert next(iter(d)).path == source / "song.txt"


def test_rename_collision_preserves_all_inputs(tmp_path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    d = Dir(tmp_path, extensions=["txt"])
    with pytest.raises(FilenameError):
        d.name_replace("a", "b")
    assert (tmp_path / "a.txt").read_text() == "a"
    assert (tmp_path / "b.txt").read_text() == "b"


def test_conversion_cannot_overwrite_another_selected_source(populated_dir):
    d = Dir(populated_dir, extensions=["wav"])
    d.convert_to_mp3(bit_rate=192)
    original = (populated_dir / "bloop.mp3").read_bytes()
    d = Dir(populated_dir, extensions=["wav", "mp3"], overwrite="overwrite")
    with pytest.raises(ConvertError):
        d.convert_to_mp3()
    assert (populated_dir / "bloop.mp3").read_bytes() == original


def test_failed_copy_cleans_staging_preserves_destination(tmp_path, monkeypatch):
    import aud.core.adapters.filesystem as filesystem

    (tmp_path / "a.txt").write_text("source")
    target = tmp_path / "out"
    target.mkdir()
    (target / "a.txt").write_text("old")

    def fail(source, destination):
        Path(destination).write_text("partial")
        raise OSError("disk error")

    monkeypatch.setattr(filesystem.shutil, "copy2", fail)
    with pytest.raises(FileError):
        Dir(tmp_path, extensions=["txt"], overwrite="overwrite").copy(target)
    assert (target / "a.txt").read_text() == "old"
    assert sorted(p.name for p in target.iterdir()) == ["a.txt"]


def test_gain_keeps_tags_bitrate_and_valid_audio(populated_dir):
    d = Dir(populated_dir, extensions=["wav"])
    d.convert_to_mp3(bit_rate=320, tags={"artist": "Artist", "title": "Title"})
    d.afx_gain(-3)
    info = mediainfo_json(str(populated_dir / "song.mp3"))
    assert info["format"]["tags"]["artist"] == "Artist"
    assert info["format"]["tags"]["title"] == "Title"
    stream = next(s for s in info["streams"] if s["codec_type"] == "audio")
    assert int(stream["bit_rate"]) == 320000


def test_failed_audio_export_preserves_original(populated_dir, monkeypatch):
    original = (populated_dir / "bloop.wav").read_bytes()

    def fail(self, out_f, *args, **kwargs):
        Path(out_f).write_bytes(b"partial")
        raise OSError("encoder failed")

    monkeypatch.setattr(AudioSegment, "export", fail)
    with pytest.raises(AudioFXError, match="encoder failed"):
        Dir(populated_dir, extensions=["wav"]).afx_gain(-3)
    assert (populated_dir / "bloop.wav").read_bytes() == original
    assert not list(populated_dir.glob(".aud-*"))


def test_pattern_intersects_existing_selection(populated_dir):
    d = Dir(populated_dir, extensions=["wav"], pattern="song.*")
    assert d.get_all() == ["song.wav"]


def test_same_directory_export_rejected_before_modification(populated_dir):
    original = (populated_dir / "bloop.wav").read_bytes()
    with pytest.raises(ExportError):
        Dir(populated_dir, extensions=["wav"]).export_for("mp3", populated_dir)
    assert (populated_dir / "bloop.wav").read_bytes() == original


def test_symlink_scan_is_opt_in(tmp_path):
    source = tmp_path / "outside.txt"
    source.write_text("outside")
    directory = tmp_path / "inside"
    directory.mkdir()
    try:
        (directory / "link.txt").symlink_to(source)
    except OSError:
        pytest.skip("symlink creation is unavailable")
    assert Dir(directory, extensions=["txt"]).get_all() == []
    selected = list(Dir(directory, extensions=["txt"], follow_symlinks=True))
    assert selected[0].path == source.resolve()
