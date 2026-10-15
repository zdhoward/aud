"""Observe installed aud imports for unexpected Python audit events, not sandboxing."""

from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
from pathlib import Path

MUTATIONS = {
    "os.chdir",
    "os.chmod",
    "os.chown",
    "os.link",
    "os.mkdir",
    "os.remove",
    "os.rename",
    "os.rmdir",
    "os.symlink",
    "os.truncate",
    "os.utime",
    "os.putenv",
    "os.unsetenv",
    "shutil.copyfile",
    "shutil.copymode",
    "shutil.copystat",
    "shutil.rmtree",
    "shutil.move",
}


def unexpected_event(event: str, args: tuple) -> bool:
    if event in MUTATIONS or event in {
        "os.system",
        "os.fork",
        "pty.spawn",
        "_winapi.CreateProcess",
    }:
        return True
    if event.startswith(("socket.", "subprocess.", "os.exec", "os.spawn")):
        return True
    if event == "open":
        _, mode, flags = args
        return bool(
            (isinstance(mode, str) and any(letter in mode for letter in "wax+"))
            or (
                isinstance(flags, int)
                and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
            )
        )
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = args.report.resolve()
    attempted: set[str] = set()
    active = True
    sys.dont_write_bytecode = True

    def observe(event, arguments):
        if active and unexpected_event(event, arguments):
            attempted.add(event)
            raise RuntimeError(f"unexpected import side effect: {event}")

    sys.addaudithook(observe)
    error = None
    try:
        for name in ("aud", "aud.cli"):
            module = importlib.import_module(name)
            if module.__file__ is None:
                raise RuntimeError("imported public module has no file location")
            location = Path(module.__file__).resolve()
            if not location.is_relative_to(Path(sys.prefix).resolve()):
                raise RuntimeError("import did not use the installed package")
    except Exception as exc:
        error = type(exc).__name__
    finally:
        active = False
    passed = error is None and not attempted
    report.write_text(
        json.dumps({"passed": passed, "events": sorted(attempted), "error": error}, indent=2) + "\n"
    )
    if not passed:
        raise SystemExit("installed import observation failed; see report")


if __name__ == "__main__":
    main()
