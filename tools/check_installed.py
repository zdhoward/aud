"""Run selected aud regressions outside the checkout against an installed artifact."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path

TESTS = (
    "test_names.py",
    "test_naming_profiles.py",
    "test_filename_parsing.py",
    "test_contracts.py",
)

GUARD = """

def pytest_sessionstart(session):
    import aud
    _check_installed_aud()


def pytest_sessionfinish(session, exitstatus):
    _check_installed_aud()


def _check_installed_aud():
    import sys
    from pathlib import Path
    root = Path(sys.prefix).resolve()
    for name, module in tuple(sys.modules.items()):
        if name == "aud" or name.startswith("aud."):
            location = getattr(module, "__file__", None)
            locations = [location] if location is not None else list(getattr(module, "__path__", ()))
            assert locations, f"missing installed module location: {name}"
            assert all(Path(p).resolve().is_relative_to(root) for p in locations), f"checkout import: {name}: {locations}"
"""


def prepare_checks(source: Path, scratch: Path) -> None:
    """Create a fresh test-only tree, with no aud source or repository config."""
    scratch.mkdir()
    tests = scratch / "tests"
    tests.mkdir()
    for name in TESTS:
        shutil.copyfile(source / "tests" / name, tests / name)
    fixtures = (source / "tests/conftest.py").read_text(encoding="utf-8")
    (tests / "conftest.py").write_text(fixtures + GUARD, encoding="utf-8")
    shutil.copytree(source / "conformance/v1", scratch / "conformance/v1")
    (scratch / "pytest.ini").write_text("[pytest]\ntestpaths = tests\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    scratch = args.scratch.resolve()
    if scratch.is_relative_to(source):
        raise ValueError("installed tests must run outside the checkout")
    prepare_checks(source, scratch)
    env = os.environ.copy()
    env.pop("PYTEST_ADDOPTS", None)
    env.pop("PYTEST_PLUGINS", None)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    subprocess.run(
        [
            str(args.python.absolute()),
            "-I",
            "-m",
            "pytest",
            "-c",
            str(scratch / "pytest.ini"),
            "--import-mode=importlib",
            f"--junitxml={args.report.resolve()}",
            "-q",
            "-ra",
        ],
        cwd=scratch,
        env=env,
        check=True,
        timeout=300,
    )


if __name__ == "__main__":
    main()
