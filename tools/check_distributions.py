"""Inspect aud release archives without extraction or importing the package."""

from __future__ import annotations

import argparse
import ast
import base64
import configparser
import csv
import hashlib
import io
import json
import stat
import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path, PurePosixPath

MAX_BYTES = 128 * 1024 * 1024
MAX_MEMBERS = 5000


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_names(names: list[str]) -> None:
    require(len(names) <= MAX_MEMBERS, "too many archive members")
    require(len(set(names)) == len(names), "duplicate archive paths")
    for name in names:
        path = PurePosixPath(name)
        require(
            bool(name)
            and not path.is_absolute()
            and ".." not in path.parts
            and "\\" not in name
            and ":" not in name
            and all(part not in {"", "."} for part in name.rstrip("/").split("/")),
            "unsafe archive path",
        )
        require(
            not any(p in {".env", ".git", ".release-evidence", "__pycache__"} for p in path.parts)
            and path.suffix not in {".pyc", ".pyo", ".exe", ".dll", ".so"},
            "unexpected private or executable archive content",
        )


def read_archive(path: Path) -> dict[str, bytes]:
    require(path.is_file() and not path.is_symlink(), "distribution must be a regular file")
    require(path.stat().st_size <= MAX_BYTES, "distribution too large")
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            members = archive.infolist()
            check_names([m.filename for m in members])
            require(sum(m.file_size for m in members) <= MAX_BYTES, "expanded archive too large")
            require(
                all(
                    stat.S_IFMT(m.external_attr >> 16) in {0, stat.S_IFREG, stat.S_IFDIR}
                    for m in members
                ),
                "wheel contains links or special files",
            )
            return {m.filename: archive.read(m) for m in members if not m.is_dir()}
    require(path.name.endswith(".tar.gz"), "unexpected distribution format")
    with tarfile.open(path) as archive:
        tar_members = []
        for member in archive:
            tar_members.append(member)
            require(len(tar_members) <= MAX_MEMBERS, "too many archive members")
        check_names([m.name for m in tar_members])
        require(
            all(m.isfile() or m.isdir() for m in tar_members),
            "sdist contains links or special files",
        )
        require(sum(m.size for m in tar_members) <= MAX_BYTES, "expanded archive too large")
        result = {}
        for member in tar_members:
            if member.isfile():
                stream = archive.extractfile(member)
                if stream is None:
                    raise ValueError("unreadable sdist member")
                with stream:
                    result[member.name] = stream.read()
        return result


def check_record(files: dict[str, bytes], record_name: str) -> None:
    rows = list(csv.reader(io.StringIO(files[record_name].decode("utf-8"))))
    require(all(len(row) == 3 for row in rows), "invalid RECORD row")
    require(len({row[0] for row in rows}) == len(rows), "duplicate RECORD entries")
    require({row[0] for row in rows} == set(files), "RECORD file inventory mismatch")
    for name, digest, size in rows:
        if name == record_name:
            require(digest == size == "", "RECORD must not hash itself")
            continue
        expected = (
            base64.urlsafe_b64encode(hashlib.sha256(files[name]).digest()).rstrip(b"=").decode()
        )
        require(digest == f"sha256={expected}", "RECORD hash mismatch")
        require(size == str(len(files[name])), "RECORD size mismatch")


def inspect_distributions(directory: Path, version: str) -> dict:
    paths = sorted(directory.iterdir())
    require(len(paths) == 2, "expected exactly one wheel and one sdist")
    wheel = directory / f"aud-{version}-py3-none-any.whl"
    sdist = directory / f"aud-{version}.tar.gz"
    require(set(paths) == {wheel, sdist}, "unexpected distribution filenames")
    wheel_files, source_files = read_archive(wheel), read_archive(sdist)
    info = f"aud-{version}.dist-info"
    root = f"aud-{version}/"
    require(all(name.startswith(root) for name in source_files), "unexpected sdist root")
    require(
        all(name.startswith(("aud/", f"{info}/")) for name in wheel_files),
        "unexpected wheel installation location",
    )
    for files, metadata_name in (
        (wheel_files, f"{info}/METADATA"),
        (source_files, f"{root}PKG-INFO"),
    ):
        require(metadata_name in files, "missing distribution metadata")
        metadata = BytesParser().parsebytes(files[metadata_name])
        require(metadata.get_all("Name") == ["aud"], "unexpected distribution name")
        require(metadata.get_all("Version") == [version], "unexpected distribution version")
    for required in ("WHEEL", "RECORD", "entry_points.txt"):
        require(f"{info}/{required}" in wheel_files, f"missing wheel {required}")
    wheel_metadata = BytesParser().parsebytes(wheel_files[f"{info}/WHEEL"])
    require(
        wheel_metadata.get_all("Wheel-Version") == ["1.0"]
        and wheel_metadata.get_all("Root-Is-Purelib") == ["true"]
        and wheel_metadata.get_all("Tag") == ["py3-none-any"],
        "unexpected aud wheel compatibility metadata",
    )
    entry_points = configparser.ConfigParser()
    entry_points.read_string(wheel_files[f"{info}/entry_points.txt"].decode("utf-8"))
    require(
        entry_points.sections() == ["console_scripts"]
        and dict(entry_points["console_scripts"]) == {"aud": "aud.cli:main"},
        "unexpected aud entry points",
    )
    check_record(wheel_files, f"{info}/RECORD")
    wheel_payload = {k: v for k, v in wheel_files.items() if k.startswith("aud/")}
    source_payload = {
        k[len(root) :]: v for k, v in source_files.items() if k.startswith(f"{root}aud/")
    }
    require(
        bool(wheel_payload) and wheel_payload == source_payload,
        "wheel/sdist package payload mismatch",
    )
    require(f"{root}pyproject.toml" in source_files, "missing sdist build configuration")
    require(
        any("license" in n.lower() for n in wheel_files if n.startswith(f"{info}/")),
        "missing wheel license",
    )
    return {
        p.name: {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "members": sorted(files)}
        for p, files in ((wheel, wheel_files), (sdist, source_files))
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, default=Path("dist"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    tree = ast.parse(Path("aud/__init__.py").read_text())
    versions = [
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "__version__" for target in node.targets
        )
    ]
    require(
        len(versions) == 1 and isinstance(versions[0], str), "expected one literal package version"
    )
    version = versions[0]
    report = inspect_distributions(args.dist, version)
    args.output.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
