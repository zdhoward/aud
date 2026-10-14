import json
from pathlib import Path

import pytest

from aud import Dir
from aud.core.operations.archive import Zip
from aud.core.operations.audio.effects import AudioJoin, Gain
from aud.core.operations.files import Copy
from aud.core.operations.names import Iterate, Uppercase
from aud.core.safety import Destination, staged_write
from aud.exceptions import AudioFXError, FileError


def test_public_preview_repeatable_matches_executed_names(tmp_path):
    (tmp_path / "été.txt").write_text("data", encoding="utf-8")
    d = Dir(tmp_path, extensions=["txt"])
    plan = d.plan().add(Iterate(zerofill=2)).add(Uppercase())
    first = d.preview(plan).to_dict()
    assert d.preview(plan).to_dict() == first
    json.dumps(first)
    assert (tmp_path / "été.txt").exists()
    result = d.execute(plan)
    assert result.succeeded
    assert result.items[-1].target == first["steps"][-1]["targets"][0]
    assert (tmp_path / "01_ÉTÉ.txt").read_text(encoding="utf-8") == "data"
    assert plan.operations[0]._counter == 1


def test_auto_rename_preview_matches_execution(tmp_path):
    (tmp_path / "a.txt").write_text("source")
    target = tmp_path / "out"
    target.mkdir()
    (target / "a.txt").write_text("existing")
    d = Dir(tmp_path, extensions=["txt"], overwrite="auto-rename")
    plan = d.plan().add(Copy(target))
    predicted = d.preview(plan).steps[0].targets
    result = d.execute(plan)
    assert [i.target for i in result.items] == predicted
    assert (target / "a (1).txt").read_text() == "source"


@pytest.mark.parametrize("operation", [Zip, AudioJoin])
def test_grouped_preview_shows_multiple_inputs_one_output(populated_dir, operation):
    d = Dir(populated_dir, extensions=["wav"])
    preview = d.preview(operation(populated_dir / "joined.wav"))
    assert len(preview.steps[0].sources) == 2
    assert len(preview.steps[0].targets) == 1


def test_continue_on_error_records_partial_success(tmp_path, monkeypatch):
    import aud.core.adapters.filesystem as filesystem

    for name in ("a.txt", "b.txt"):
        (tmp_path / name).write_text(name)
    original_copy = filesystem.shutil.copy2

    def fail_one(source, target):
        if Path(source).name == "a.txt":
            raise OSError("read failed")
        return original_copy(source, target)

    monkeypatch.setattr(filesystem.shutil, "copy2", fail_one)
    d = Dir(tmp_path, extensions=["txt"])
    result = d.execute(d.plan().add(Copy(tmp_path / "out")), continue_on_error=True)
    assert not result
    assert [i.status for i in result.items] == ["failed", "success"]
    assert (tmp_path / "out" / "b.txt").read_text() == "b.txt"
    assert (tmp_path / "a.txt").read_text() == "a.txt"
    json.dumps(result.to_dict())


def test_failed_dependency_does_not_process_stale_target(tmp_path, monkeypatch):
    import aud.core.adapters.filesystem as filesystem

    (tmp_path / "a.txt").write_text("original")
    monkeypatch.setattr(
        filesystem.shutil, "copy2", lambda *args: (_ for _ in ()).throw(OSError("fail"))
    )
    d = Dir(tmp_path, extensions=["txt"])
    result = d.execute(
        d.plan().add(Copy(tmp_path / "out")).add(Uppercase()), continue_on_error=True
    )
    assert [i.status for i in result.items] == ["failed", "not_run"]
    assert not (tmp_path / "out" / "A.txt").exists()


def test_fail_fast_results_include_not_run_files(tmp_path, monkeypatch):
    import aud.core.adapters.filesystem as filesystem

    for name in ("a.txt", "b.txt"):
        (tmp_path / name).write_text(name)
    monkeypatch.setattr(
        filesystem.shutil, "copy2", lambda *args: (_ for _ in ()).throw(OSError("fail"))
    )
    d = Dir(tmp_path, extensions=["txt"])
    with pytest.raises(FileError):
        d.copy(tmp_path / "out")
    assert [i.status for i in d.last_result.items] == ["failed", "not_run"]
    assert d.get_all() == ["a.txt", "b.txt"]


def test_late_destination_creation_is_not_overwritten(tmp_path):
    target = tmp_path / "target.txt"
    with pytest.raises(FileExistsError):
        with staged_write(Destination(None, target)) as temporary:
            temporary.write_text("new")
            target.write_text("late arrival")
    assert target.read_text() == "late arrival"
    assert not list(tmp_path.glob(".aud-*"))


def test_empty_files_are_valid_copy_inputs(tmp_path):
    (tmp_path / "empty.txt").touch()
    d = Dir(tmp_path, extensions=["txt"])
    assert d.copy(tmp_path / "out")
    assert (tmp_path / "out" / "empty.txt").stat().st_size == 0


def test_entire_plan_preflight_precedes_audio_changes(populated_dir):
    target = populated_dir / "out"
    target.mkdir()
    (target / "bloop.wav").write_bytes(b"existing")
    original = (populated_dir / "bloop.wav").read_bytes()
    d = Dir(populated_dir, extensions=["wav"])
    with pytest.raises(FileExistsError):
        d.execute(d.plan().add(Gain(-3)).add(Copy(target)))
    assert (populated_dir / "bloop.wav").read_bytes() == original
    assert d.last_result.items[0].operation == "preflight"


def test_invalid_policy_and_invalid_preview_input(tmp_path):
    with pytest.raises(ValueError, match="policy"):
        Dir(tmp_path, overwrite="unknown")
    with pytest.raises(TypeError):
        Dir(tmp_path).preview("not a plan")


def test_export_preserves_unselected_existing_sidecars(populated_dir):
    target = populated_dir / "out"
    target.mkdir()
    (target / "bloop.wav").write_bytes(b"original sidecar")
    d = Dir(populated_dir, extensions=["wav"])
    assert d.export_for("mp3", target)
    assert (target / "bloop.wav").read_bytes() == b"original sidecar"
    assert (target / "bloop.mp3").exists()


def test_missing_ffmpeg_is_actionable(populated_dir, monkeypatch):
    import aud.core.adapters.audio_io as audio_io

    monkeypatch.setattr(audio_io.shutil, "which", lambda name: None)
    with pytest.raises(AudioFXError, match="ffmpeg is required"):
        Dir(populated_dir, extensions=["wav"]).afx_gain(-1)


def test_read_only_source_copy_does_not_leave_staging_file(tmp_path):
    import stat

    source = tmp_path / "a.txt"
    source.write_text("data")
    source.chmod(stat.S_IREAD)
    target = tmp_path / "out"
    try:
        Dir(tmp_path, extensions=["txt"]).copy(target)
        assert (target / "a.txt").read_text() == "data"
        assert not list(target.glob(".aud-*"))
    finally:
        source.chmod(stat.S_IREAD | stat.S_IWRITE)
        if (target / "a.txt").exists():
            (target / "a.txt").chmod(stat.S_IREAD | stat.S_IWRITE)


def test_skipped_archive_never_becomes_input_to_later_operations(tmp_path):
    (tmp_path / "a.txt").write_text("source")
    existing = tmp_path / "archive.zip"
    existing.write_bytes(b"unrelated archive")
    d = Dir(tmp_path, extensions=["txt"], overwrite="skip")
    plan = d.plan().add(Zip(existing)).add(Uppercase())
    assert d.preview(plan).steps[1].sources == []
    d.execute(plan)
    assert existing.read_bytes() == b"unrelated archive"
    assert "ARCHIVE.zip" not in [p.name for p in tmp_path.iterdir()]
    assert d.get_all() == ["a.txt"]


def test_move_to_dotdot_alias_never_deletes_source(tmp_path):
    (tmp_path / "a.txt").write_text("original")
    d = Dir(tmp_path, extensions=["txt"], overwrite="overwrite")
    with pytest.raises(FileError, match="identical"):
        d.move(tmp_path / ".." / tmp_path.name)
    assert (tmp_path / "a.txt").read_text() == "original"


def test_move_to_hardlink_alias_never_deletes_source(tmp_path):
    import os

    source = tmp_path / "a.txt"
    source.write_text("original")
    target = tmp_path / "out"
    target.mkdir()
    try:
        os.link(source, target / "a.txt")
    except OSError:
        pytest.skip("hard links unavailable")
    with pytest.raises(FileError, match="same file"):
        Dir(tmp_path, extensions=["txt"], overwrite="overwrite").move(target)
    assert source.read_text() == "original"
    assert (target / "a.txt").read_text() == "original"


def test_failed_join_retains_group_selection_and_reports_sources(populated_dir, monkeypatch):
    from pydub import AudioSegment

    def fail(self, *args, **kwargs):
        raise OSError("encoder failed")

    monkeypatch.setattr(AudioSegment, "export", fail)
    d = Dir(populated_dir, extensions=["wav"])
    result = d.execute(
        d.plan().add(AudioJoin(populated_dir / "joined.wav")), continue_on_error=True
    )
    assert not result
    assert d.get_all() == ["bloop.wav", "song.wav"]
    assert len(result.items[0].sources) == 2
    assert not (populated_dir / "joined.wav").exists()


def test_duplicate_archive_members_fail_during_preflight(tmp_path):
    from aud.core.models import AudioFile
    from aud.core.plan import Plan

    for folder in ("one", "two"):
        (tmp_path / folder).mkdir()
        (tmp_path / folder / "a.txt").write_text(folder)
    plan = Plan([AudioFile(tmp_path / f / "a.txt") for f in ("one", "two")]).add(
        Zip(tmp_path / "archive.zip")
    )
    d = Dir(tmp_path)
    with pytest.raises(ValueError, match="Duplicate archive"):
        d.preview(plan)
    with pytest.raises(ValueError, match="Duplicate archive"):
        d.execute(plan)
    assert not (tmp_path / "archive.zip").exists()
    assert all(item.operation == "preflight" for item in d.last_result.items)


def test_failed_group_after_copy_retains_current_inputs(tmp_path, monkeypatch):
    import aud.core.adapters.filesystem as filesystem

    (tmp_path / "a.txt").write_text("source")
    target = tmp_path / "out"

    def fail(*args, **kwargs):
        raise OSError("archive failed")

    monkeypatch.setattr(filesystem, "ZipFile", fail)
    d = Dir(tmp_path, extensions=["txt"])
    result = d.execute(
        d.plan().add(Copy(target)).add(Zip(tmp_path / "archive.zip")), continue_on_error=True
    )
    assert [item.status for item in result.items] == ["success", "failed"]
    assert [f.path for f in d] == [target / "a.txt"]
    assert (tmp_path / "a.txt").read_text() == "source"


def test_blocked_group_keeps_successful_copy_and_failed_original(tmp_path, monkeypatch):
    import aud.core.adapters.filesystem as filesystem

    for name in ("a.txt", "b.txt"):
        (tmp_path / name).write_text(name)
    copy = filesystem.shutil.copy2

    def fail_one(source, target):
        if Path(source).name == "a.txt":
            raise OSError("read failed")
        return copy(source, target)

    monkeypatch.setattr(filesystem.shutil, "copy2", fail_one)
    target = tmp_path / "out"
    d = Dir(tmp_path, extensions=["txt"])
    result = d.execute(
        d.plan().add(Copy(target)).add(Zip(tmp_path / "archive.zip")), continue_on_error=True
    )
    assert [i.status for i in result.items] == ["failed", "success", "not_run"]
    assert len(result.items[-1].sources) == 2
    assert {f.path for f in d} == {tmp_path / "a.txt", target / "b.txt"}
    assert not (tmp_path / "archive.zip").exists()


def test_unsupported_effect_fails_preflight_before_prior_effect(populated_dir):
    from aud.core.operations.audio.base import AudioOperation

    class UnknownEffect(AudioOperation):
        def apply(self, file):
            return file

    original = (populated_dir / "bloop.wav").read_bytes()
    d = Dir(populated_dir, extensions=["wav"])
    with pytest.raises(TypeError, match="Unsupported operation"):
        d.execute(d.plan().add(Gain(-3)).add(UnknownEffect()))
    assert (populated_dir / "bloop.wav").read_bytes() == original


def test_fail_fast_selection_keeps_outputs_and_unprocessed_inputs(tmp_path, monkeypatch):
    import aud.core.adapters.filesystem as filesystem

    for name in ("a.txt", "b.txt"):
        (tmp_path / name).write_text(name)
    copy = filesystem.shutil.copy2

    def fail_second(source, target):
        if Path(source).name == "b.txt":
            raise OSError("read failed")
        return copy(source, target)

    monkeypatch.setattr(filesystem.shutil, "copy2", fail_second)
    d = Dir(tmp_path, extensions=["txt"])
    target = tmp_path / "out"
    with pytest.raises(FileError):
        d.copy(target)
    assert [item.status for item in d.last_result.items] == ["success", "failed"]
    assert [file.path for file in d] == [target / "a.txt", tmp_path / "b.txt"]
    assert (tmp_path / "a.txt").read_text() == "a.txt"


def test_cancellation_stops_between_files_and_retains_sources(tmp_path, monkeypatch):
    from threading import Event

    import aud.core.adapters.filesystem as filesystem

    event = Event()
    for name in ("a.txt", "b.txt"):
        (tmp_path / name).write_text(name)
    copy = filesystem.shutil.copy2

    def copy_then_cancel(source, target):
        result = copy(source, target)
        event.set()
        return result

    monkeypatch.setattr(filesystem.shutil, "copy2", copy_then_cancel)
    d = Dir(tmp_path, extensions=["txt"])
    result = d.execute(d.plan().add(Copy(tmp_path / "out")), cancel=event.is_set)
    assert [i.status for i in result.items] == ["success", "cancelled"]
    assert not result
    assert not (tmp_path / "out" / "b.txt").exists()
    assert (tmp_path / "b.txt").read_text() == "b.txt"


def test_corrupt_encoded_output_does_not_replace_source(populated_dir, monkeypatch):
    from pydub import AudioSegment

    original = (populated_dir / "bloop.wav").read_bytes()

    def corrupt(self, target, **kwargs):
        Path(target).write_bytes(b"invalid audio")
        return open(target, "rb")

    monkeypatch.setattr(AudioSegment, "export", corrupt)
    with pytest.raises(AudioFXError):
        Dir(populated_dir, extensions=["wav"]).afx_gain(-1)
    assert (populated_dir / "bloop.wav").read_bytes() == original
    assert not list(populated_dir.glob(".aud-*"))
