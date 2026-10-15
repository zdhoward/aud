"""The installed runner preserves virtual-environment interpreter paths."""

import os
import runpy
import sys
import venv
from pathlib import Path


def test_virtual_environment_interpreter_is_not_dereferenced(tmp_path, monkeypatch):
    runner = runpy.run_path(str(Path(__file__).resolve().parents[1] / "tools/check_installed.py"))
    environment = tmp_path / "venv"
    venv.create(environment, with_pip=False, symlinks=os.name != "nt")
    interpreter = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    commands = []
    monkeypatch.setattr("subprocess.run", lambda command, **kwargs: commands.append(command))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "check_installed.py",
            "--python",
            str(interpreter),
            "--scratch",
            str(tmp_path / "checks"),
            "--report",
            str(tmp_path / "report.xml"),
        ],
    )
    runner["main"]()
    assert commands[0][0] == str(interpreter.absolute())
    if interpreter.is_symlink():
        assert commands[0][0] != str(interpreter.resolve())
