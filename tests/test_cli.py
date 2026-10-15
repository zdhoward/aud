import json
import signal
import sys
from zipfile import ZipFile

import pytest

from aud import cli
from aud.core.results import BatchResult, FileResult


def invoke(capsys, *args, **options):
    code = cli.run([str(arg) for arg in args] + ["--json"], **options)
    captured = capsys.readouterr()
    assert not captured.err
    return code, json.loads(captured.out)


def config(tmp_path, value):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_cli_reports_file_count(populated_dir, capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["aud", str(populated_dir)])

    cli.main()

    assert "Found" in capsys.readouterr().out


def test_cli_requires_directory_argument(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["aud"])

    with pytest.raises(SystemExit) as excinfo:
        cli.main()

    assert excinfo.value.code == 1
    assert "Usage" in capsys.readouterr().out


def test_cli_rejects_missing_directory(tmp_path, capsys, monkeypatch):
    missing = tmp_path / "does-not-exist"
    monkeypatch.setattr(sys, "argv", ["aud", str(missing)])

    with pytest.raises(SystemExit) as excinfo:
        cli.main()

    assert excinfo.value.code == 1
    assert "Directory does not exist" in capsys.readouterr().out


def test_list_selection_defaults_and_pattern(populated_dir, capsys):
    assert invoke(capsys, "list", populated_dir) == (0, {"files": []})
    assert invoke(capsys, "list", populated_dir, "--extensions", "wav", "--pattern", "bloop.*") == (
        0,
        {"files": ["bloop.wav"]},
    )


def test_inspection_reports_real_properties(populated_dir, capsys):
    code, data = invoke(
        capsys, "inspect", populated_dir, "--extensions", "wav", "--pattern", "bloop.*"
    )
    assert code == 0
    assert data["files"][0]["sample_rate"] == 44100
    assert data["files"][0]["channels"] == 2


def test_convert_preview_then_execute_and_collision(populated_dir, capsys):
    args = (
        "convert",
        populated_dir,
        "--extensions",
        "wav",
        "--pattern",
        "bloop.*",
        "--format",
        "flac",
    )
    code, data = invoke(capsys, *args, "--dry-run")
    assert code == 0 and data["dry_run"]
    target = populated_dir / "bloop.flac"
    assert not target.exists()
    code, result = invoke(capsys, *args)
    assert code == 0 and result["succeeded"] and target.exists()
    before = target.read_bytes()
    code, error = invoke(capsys, *args)
    assert code == 1 and not error["succeeded"]
    assert target.read_bytes() == before


def test_export_rejects_source_directory_and_writes_copy(populated_dir, capsys):
    source = populated_dir / "bloop.wav"
    before = source.read_bytes()
    args = (
        "export",
        populated_dir,
        "--extensions",
        "wav",
        "--pattern",
        "bloop.*",
        "--format",
        "flac",
        "--output-directory",
    )
    code, _ = invoke(capsys, *args, populated_dir)
    assert code == 2
    target = populated_dir / "delivery"
    assert invoke(capsys, *args, target)[0] == 0
    assert (target / "bloop.flac").exists() and source.read_bytes() == before


def test_rename_profile_copy_preview_and_execution(populated_dir, capsys):
    path = config(
        populated_dir,
        {
            "profile": {"directory": "", "filename": "{track_number:02} - {title}"},
            "metadata": {"bloop.wav": {"title": "First", "track_number": 1}},
        },
    )
    output = populated_dir / "named"
    args = (
        "rename",
        populated_dir,
        "--extensions",
        "wav",
        "--pattern",
        "bloop.*",
        "--config",
        path,
        "--copy",
        "--output-directory",
        output,
    )
    assert invoke(capsys, *args, "--dry-run")[0] == 0
    assert not output.exists()
    assert invoke(capsys, *args)[0] == 0
    assert (output / "01 - First.wav").read_bytes() == (populated_dir / "bloop.wav").read_bytes()


def test_ordered_effects_use_native_chain(populated_dir, capsys):
    path = config(
        populated_dir,
        {"effects": [{"type": "gain", "amount_db": -3}, {"type": "pad", "pad_out": 0.1}]},
    )
    args = (
        "effects",
        populated_dir,
        "--extensions",
        "wav",
        "--pattern",
        "bloop.*",
        "--config",
        path,
        "--format",
        "flac",
    )
    assert invoke(capsys, *args, "--dry-run")[0] == 0
    code, result = invoke(capsys, *args)
    assert code == 0
    assert result["items"][0]["details"]["effects"] == ["Gain", "Pad"]


def test_generic_album_cli_preview_and_checksums(populated_dir, capsys):
    path = config(populated_dir, {"release": {"title": "Album", "artist": "Artist"}})
    target = populated_dir / "album.zip"
    args = ("album", populated_dir, "--extensions", "wav", "--config", path, "--target", target)
    assert invoke(capsys, *args, "--dry-run")[0] == 0
    assert not target.exists()
    assert invoke(capsys, *args)[0] == 0
    with ZipFile(target) as archive:
        assert "checksums.sha256" in archive.namelist()
        assert archive.read("bloop.wav") == (populated_dir / "bloop.wav").read_bytes()


@pytest.mark.parametrize(
    "contents",
    [
        '{"effects":[],"effects":[]}',
        '{"effects":NaN}',
        "[]",
        '{"effects":[],"unexpected":true}',
        '{"effects":[{"type":"system","command":"ignored"}]}',
    ],
)
def test_invalid_config_is_machine_readable_and_does_not_write(populated_dir, capsys, contents):
    path = populated_dir / "config.json"
    path.write_text(contents)
    before = (populated_dir / "bloop.wav").read_bytes()
    code, data = invoke(capsys, "effects", populated_dir, "--extensions", "wav", "--config", path)
    assert code == 2 and data["exit_code"] == 2
    assert (populated_dir / "bloop.wav").read_bytes() == before


def test_config_budget_and_empty_selection(populated_dir, capsys):
    path = populated_dir / "big.json"
    path.write_bytes(b" " * (cli.CONFIG_BYTES + 1))
    code, data = invoke(capsys, "effects", populated_dir, "--extensions", "wav", "--config", path)
    assert code == 2 and "1 MiB" in data["error"]
    code, data = invoke(capsys, "convert", populated_dir, "--format", "wav")
    assert code == 2 and "No selected files" in data["error"]


def test_usage_errors_and_cancel_are_json(populated_dir, capsys):
    code, data = invoke(capsys, "convert", populated_dir)
    assert code == 2 and data["exit_code"] == 2
    code, data = invoke(capsys, "inspect", populated_dir, cancel=lambda: True)
    assert code == 130 and data["exit_code"] == 130


def test_main_restores_signal_handler(populated_dir, monkeypatch, capsys):
    previous = signal.getsignal(signal.SIGINT)
    monkeypatch.setattr(sys, "argv", ["aud", "list", str(populated_dir), "--json"])
    cli.main()
    assert signal.getsignal(signal.SIGINT) == previous
    assert json.loads(capsys.readouterr().out) == {"files": []}


@pytest.mark.parametrize("option", ["--sample-rate", "--bit-depth", "--bit-rate", "--channels"])
def test_explicit_zero_effect_output_option_rejected_before_execution(
    populated_dir, capsys, monkeypatch, option
):
    path = config(populated_dir, {"effects": [{"type": "gain", "amount_db": -3}]})
    monkeypatch.setattr(
        cli.Dir, "execute", lambda *args, **kwargs: pytest.fail("Unexpected execution")
    )
    code, data = invoke(
        capsys, "effects", populated_dir, "--extensions", "wav", "--config", path, option, "0"
    )
    assert code == 2 and "require --format" in data["error"]


@pytest.mark.parametrize("number", ["1e999", "-1e999"])
def test_config_rejects_floating_point_overflow(populated_dir, capsys, number):
    path = populated_dir / "overflow.json"
    path.write_text('{"effects":[{"type":"gain","amount_db":' + number + "}]}")
    code, data = invoke(capsys, "effects", populated_dir, "--extensions", "wav", "--config", path)
    assert code == 2 and "Non-finite JSON number" in data["error"]


def test_execution_failure_keeps_partial_result(populated_dir, monkeypatch, capsys):
    def fail(directory, plan, **options):
        directory.last_result = BatchResult(
            [FileResult("source", "target", "ConvertFormat", "failed", "encode failed")]
        )
        raise RuntimeError("encode failed")

    monkeypatch.setattr(cli.Dir, "execute", fail)
    code, data = invoke(capsys, "convert", populated_dir, "--extensions", "wav", "--format", "flac")
    assert code == 1 and data["result"]["items"][0]["error"] == "encode failed"


def test_cancelled_execution_has_exit_130(populated_dir, monkeypatch, capsys):
    monkeypatch.setattr(
        cli.Dir,
        "execute",
        lambda *args, **kwargs: BatchResult(
            [FileResult("source", "target", "ConvertFormat", "cancelled")]
        ),
    )
    code, data = invoke(capsys, "convert", populated_dir, "--extensions", "wav", "--format", "flac")
    assert code == 130 and data["items"][0]["status"] == "cancelled"


@pytest.mark.parametrize(
    "row",
    [{"title": 123}, {"track_number": True}, {"tags": []}, {"issues": "bad"}, {"unknown": "bad"}],
)
def test_metadata_config_types_are_explicit(populated_dir, capsys, row):
    path = config(
        populated_dir,
        {"profile": {"directory": "", "filename": "{title}"}, "metadata": {"bloop.wav": row}},
    )
    code, data = invoke(
        capsys,
        "rename",
        populated_dir,
        "--extensions",
        "wav",
        "--pattern",
        "bloop.*",
        "--config",
        path,
        "--output-directory",
        populated_dir / "named",
        "--dry-run",
    )
    assert code == 2 and not data["succeeded"]
