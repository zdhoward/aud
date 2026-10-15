"""Release archive integrity checks use synthetic packages, never media decoders."""

import base64
import csv
import hashlib
import io
import runpy
import tarfile
import zipfile
from pathlib import Path

import pytest

validator = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "tools/check_distributions.py")
)
inspect_distributions = validator["inspect_distributions"]
check_names = validator["check_names"]


def distributions(tmp_path, *, change=None):
    info = "aud-1.2.3.dist-info"
    files = {
        "aud/__init__.py": b'__version__ = "1.2.3"\n',
        f"{info}/METADATA": b"Metadata-Version: 2.4\nName: aud\nVersion: 1.2.3\n",
        f"{info}/WHEEL": b"Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
        f"{info}/entry_points.txt": b"[console_scripts]\naud = aud.cli:main\n",
        f"{info}/licenses/LICENSE": b"MIT",
    }
    source = {
        "aud-1.2.3/PKG-INFO": files[f"{info}/METADATA"],
        "aud-1.2.3/pyproject.toml": b"[build-system]\nrequires = []\n",
        "aud-1.2.3/aud/__init__.py": files["aud/__init__.py"],
    }
    record = io.StringIO(newline="")
    writer = csv.writer(record)
    for name, data in files.items():
        digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()
        writer.writerow([name, f"sha256={digest}", len(data)])
    writer.writerow([f"{info}/RECORD", "", ""])
    files[f"{info}/RECORD"] = record.getvalue().encode()
    if change:
        change(files, source)
    with zipfile.ZipFile(tmp_path / "aud-1.2.3-py3-none-any.whl", "w") as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    with tarfile.open(tmp_path / "aud-1.2.3.tar.gz", "w:gz") as archive:
        for name, data in source.items():
            member = tarfile.TarInfo(name)
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))


def test_valid_pair(tmp_path):
    distributions(tmp_path)
    report = inspect_distributions(tmp_path, "1.2.3")
    assert len(report) == 2
    assert all(len(item["sha256"]) == 64 for item in report.values())


@pytest.mark.parametrize(
    "name", ["../escape", "/absolute", "a\\b", "C:drive", "a/./b", "a//b", "a/.env"]
)
def test_unsafe_names(name):
    with pytest.raises(ValueError):
        check_names([name])


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda w, s: w.update({"aud/__init__.py": b"tampered"}), "RECORD hash"),
        (lambda w, s: w.update({"aud/extra.py": b"extra"}), "RECORD file inventory"),
        (lambda w, s: s.update({"aud-1.2.3/aud/__init__.py": b"different"}), "payload mismatch"),
        (lambda w, s: w.update({"other.pth": b"import evil"}), "installation location"),
        (lambda w, s: s.update({"other/PKG-INFO": b"unexpected"}), "sdist root"),
        (lambda w, s: w.pop("aud-1.2.3.dist-info/RECORD"), "missing wheel RECORD"),
        (
            lambda w, s: w.update({"aud-1.2.3.dist-info/WHEEL": b"Wheel-Version: 2.0\n"}),
            "compatibility metadata",
        ),
        (
            lambda w, s: w.update({"aud-1.2.3.dist-info/entry_points.txt": b"[other]\nx = evil\n"}),
            "entry points",
        ),
    ],
)
def test_reject_inconsistent_packages(tmp_path, change, message):
    distributions(tmp_path, change=change)
    with pytest.raises(ValueError, match=message):
        inspect_distributions(tmp_path, "1.2.3")
