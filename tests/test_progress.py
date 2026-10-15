import json
from pathlib import Path

import pytest

from aud import Dir, cli
from aud.core.operations.files import Copy
from aud.core.progress import ProgressEvent


def test_file_progress_is_live_and_matches_results(populated_dir):
    d = Dir(populated_dir, extensions=["wav"])
    events = []
    published = []
    target = populated_dir / "copies"

    def observe(event):
        events.append(event)
        if event.phase == "finish" and event.status == "success":
            published.append(Path(event.target).exists())

    result = d.execute(d.plan().add(Copy(target)), progress=observe)
    assert result
    assert published == [True, True]
    assert [(event.phase, event.completed, event.total) for event in events] == [
        ("start", 0, 2),
        ("finish", 1, 2),
        ("start", 1, 2),
        ("finish", 2, 2),
    ]
    assert [event.status for event in events if event.phase == "finish"] == [
        item.status for item in result.items
    ]
    json.dumps(events[-1].to_dict())


def test_callback_failure_does_not_change_published_result(populated_dir, caplog):
    d = Dir(populated_dir, extensions=["wav"])
    calls = []

    def broken(event):
        calls.append(event)
        raise RuntimeError("private error details")

    assert d.execute(d.plan().add(Copy(populated_dir / "copies")), progress=broken)
    assert len(calls) == 1
    assert "further events disabled" in caplog.text
    assert "private error details" not in caplog.text


def test_skip_and_cancel_finish_events(populated_dir):
    target = populated_dir / "copies"
    d = Dir(populated_dir, extensions=["wav"], overwrite="skip")
    d.execute(d.plan().add(Copy(target)))
    d = Dir(populated_dir, extensions=["wav"], overwrite="skip")
    events = []
    assert d.execute(d.plan().add(Copy(target)), progress=events.append)
    assert [event.status for event in events] == ["skipped", "skipped"]
    events.clear()
    assert not d.execute(d.plan().add(Copy(target)), cancel=lambda: True, progress=events.append)
    assert [event.status for event in events] == ["cancelled", "cancelled"]


def test_failed_file_and_unattempted_files_report_terminal_status(populated_dir):
    def fail(*args, **kwargs):
        raise OSError("copy unavailable")

    # Inject at the action boundary, leaving normal batch/result behavior intact.
    from aud.core.adapters.batch import BatchAdapter
    from aud.core.safety import Destination

    adapter = BatchAdapter(progress=(events := []).append)
    entries = [
        Destination(path, populated_dir / "copies" / path.name)
        for path in sorted(populated_dir.glob("*.wav"))
    ]
    with pytest.raises(OSError, match="copy unavailable"):
        adapter.perform(Copy(populated_dir / "copies"), entries, fail)
    assert [event.status for event in events if event.phase == "finish"] == ["failed", "not_run"]


def test_album_payload_staged_then_archive_published(populated_dir):
    d = Dir(populated_dir, extensions=["wav"])
    events = []
    staged_visibility = []
    final_visibility = []
    target = populated_dir / "album.zip"

    def observe(event):
        events.append(event)
        if event.operation == "AlbumPayload":
            staged_visibility.append(target.exists())
        if event.status == "success":
            final_visibility.append(target.exists())

    assert d.package_album(target, release={"title": "Album", "artist": "Artist"}, progress=observe)
    assert events[-1].operation == "AlbumPackage" and events[-1].status == "success"
    assert not any(staged_visibility) and final_visibility == [True]
    assert [
        event.status
        for event in events
        if event.operation == "AlbumPayload" and event.phase == "finish"
    ] == ["staged", "staged"]


def test_album_cancel_never_reports_success(populated_dir):
    d = Dir(populated_dir, extensions=["wav"])
    plan = d.plan_album(populated_dir / "album.zip", release={"title": "Album", "artist": "Artist"})
    events = []
    assert not d.execute(plan, cancel=lambda: True, progress=events.append)
    assert events[-1].status == "cancelled"
    assert not any(event.status == "success" for event in events)


def test_cli_progress_is_stderr_and_stdout_stays_json(populated_dir, capsys):
    code = cli.run(
        [
            "convert",
            str(populated_dir),
            "--extensions",
            "wav",
            "--pattern",
            "bloop.*",
            "--format",
            "flac",
            "--progress",
            "--json",
        ]
    )
    output = capsys.readouterr()
    assert code == 0 and json.loads(output.out)["succeeded"]
    assert "ConvertFormat 0/1 start" in output.err
    assert "ConvertFormat 1/1 success" in output.err


def test_progress_dry_run_has_no_execution_events(populated_dir, capsys):
    assert (
        cli.run(
            [
                "convert",
                str(populated_dir),
                "--extensions",
                "wav",
                "--format",
                "flac",
                "--progress",
                "--dry-run",
                "--json",
            ]
        )
        == 0
    )
    assert not capsys.readouterr().err


def test_cli_inspection_progress_and_escaping(populated_dir, capsys):
    assert (
        cli.run(
            [
                "inspect",
                str(populated_dir),
                "--extensions",
                "wav",
                "--pattern",
                "bloop.*",
                "--progress",
                "--json",
            ]
        )
        == 0
    )
    output = capsys.readouterr()
    assert json.loads(output.out)["files"]
    assert "Inspect 1/1 success" in output.err
    cli._progress(ProgressEvent("start", "Test", 0, 1, target="bad\x1b[31m\nname"))
    text = capsys.readouterr().err
    assert "\x1b" not in text and "\\u001b" in text and "\\n" in text
