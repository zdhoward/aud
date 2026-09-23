import sys

import pytest

from aud import cli


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
