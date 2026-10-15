"""Import observations reject side effects and permit ordinary module reads."""

import os
import runpy
from pathlib import Path

import pytest

unexpected = runpy.run_path(str(Path(__file__).resolve().parents[1] / "tools/check_import.py"))[
    "unexpected_event"
]


@pytest.mark.parametrize(
    "event",
    ["socket.connect", "subprocess.Popen", "os.system", "os.mkdir", "os.rename", "os.putenv"],
)
def test_import_side_effect_events(event):
    assert unexpected(event, ())


@pytest.mark.parametrize(
    "mode,flags", [("w", 0), ("a", 0), ("r+", 0), (None, os.O_CREAT), (None, os.O_WRONLY)]
)
def test_import_write_events(mode, flags):
    assert unexpected("open", ("sample", mode, flags))


def test_import_reads_are_allowed():
    assert not unexpected("open", ("sample.py", "r", os.O_RDONLY))
    assert not unexpected("import", ("aud",))
