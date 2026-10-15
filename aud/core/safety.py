from __future__ import annotations

import os
import stat
import tempfile
import unicodedata
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

POLICIES = {"error", "skip", "overwrite", "auto-rename"}


def validate_policy(policy: str) -> str:
    if policy not in POLICIES:
        raise ValueError(f"Unknown overwrite policy: {policy}")
    return policy


def is_link(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    )


def check_path(path: Path) -> None:
    for part in (path, *path.parents):
        if is_link(part):
            raise ValueError(f"Link/reparse path is not writable: {part}")


def path_key(path: Path) -> str:
    return unicodedata.normalize("NFC", os.path.abspath(path)).casefold()


@dataclass(frozen=True)
class Destination:
    source: Path | None
    target: Path
    status: str = "ready"
    replace: bool = False


def destinations(
    pairs: Sequence[tuple[Path | None, Path]],
    policy: str,
    *,
    protected: list[Path] | None = None,
    in_place: bool = False,
) -> list[Destination]:
    validate_policy(policy)
    protected_keys = {path_key(p) for p in (protected or [])}
    reserved: set[str] = set()
    result = []
    for source, target in pairs:
        check_path(target.absolute())
        target = Path(os.path.abspath(target))
        same = source is not None and path_key(source) == path_key(target)
        same_identity = (
            source is not None
            and source.exists()
            and target.exists()
            and os.path.samefile(source, target)
        )
        if same_identity and not same:
            raise ValueError(f"Source and destination refer to the same file: {target}")
        if (
            same
            and source is not None
            and target.exists()
            and source.exists()
            and not os.path.samefile(source, target)
        ):
            raise FileExistsError(f"Destination exists as a different case/Unicode alias: {target}")
        if same and in_place:
            if path_key(target) in reserved:
                raise FileExistsError(f"Duplicate in-place destination: {target}")
            result.append(Destination(source, target, replace=True))
            reserved.add(path_key(target))
            continue
        if same:
            raise ValueError(f"Source and destination are identical: {target}")
        base = target
        number = 0
        while True:
            key = path_key(target)
            protected_identity = target.exists() and any(
                p.exists() and os.path.samefile(p, target) for p in (protected or [])
            )
            # Listing catches case/Unicode collisions even on case-sensitive hosts.
            existing = target.exists() or (
                target.parent.is_dir() and any(path_key(p) == key for p in target.parent.iterdir())
            )
            collision = existing or key in reserved or key in protected_keys or protected_identity
            if not collision:
                break
            if policy == "auto-rename":
                number += 1
                target = base.with_name(f"{base.stem} ({number}){base.suffix}")
                continue
            if policy == "skip":
                result.append(Destination(source, target, "skipped"))
                break
            if (
                policy == "overwrite"
                and key not in reserved
                and key not in protected_keys
                and not protected_identity
            ):
                if not target.is_file():
                    raise ValueError(f"Destination is not a regular file: {target}")
                result.append(Destination(source, target, replace=True))
                reserved.add(key)
                break
            raise FileExistsError(f"Destination exists or collides with an input: {target}")
        if collision:
            continue
        result.append(Destination(source, target))
        reserved.add(path_key(target))
    return result


@contextmanager
def staged_write(destination: Destination) -> Iterator[Path]:
    target = destination.target
    check_path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".aud-", suffix=target.suffix, dir=target.parent)
    temporary = Path(name)
    try:
        yield temporary
        if not temporary.is_file():
            raise ValueError(f"Output is invalid: {target}")
        os.fsync(fd)
        os.close(fd)
        fd = -1
        check_path(target)
        if destination.replace:
            os.replace(temporary, target)
        elif os.name == "nt":
            # Windows rename refuses an existing destination, including on FAT.
            os.rename(temporary, target)
        else:
            # Exclusive publication: no check-then-rename overwrite race.
            os.link(temporary, target)
    finally:
        if fd >= 0:
            os.close(fd)
        if os.name == "nt" and temporary.exists():
            temporary.chmod(temporary.stat().st_mode | stat.S_IWRITE)
        temporary.unlink(missing_ok=True)
