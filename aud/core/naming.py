"""Deterministic metadata templates and portable destination-tree validation."""

from __future__ import annotations

import os
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from string import Formatter

from aud.core.metadata import AudioMetadata
from aud.core.safety import check_path, path_key

FIELDS = {
    "artist",
    "album_artist",
    "album",
    "title",
    "year",
    "track_number",
    "track_total",
    "disc_number",
    "disc_total",
}
NUMERIC = {"year", "track_number", "track_total", "disc_number", "disc_total"}
DEVICES = {"con", "prn", "aux", "nul", "conin$", "conout$"} | {
    prefix + number for prefix in ("com", "lpt") for number in "123456789¹²³"
}


class MissingNamingField(ValueError):
    pass


@dataclass(frozen=True)
class NamingProfile:
    filename: str = "{track_number:02} - {title}"
    directory: str = "{album_artist} - {album} ({year})"
    case: str = "preserve"
    ascii_only: bool = False
    space_replacement: str = " "
    prefix: str = ""
    suffix: str = ""
    missing: str = "error"
    defaults: dict[str, str | int] = field(default_factory=dict)

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        if self.case not in {"preserve", "lower", "upper"} or self.missing not in {"error", "skip"}:
            raise ValueError("Invalid naming case or missing-field policy")
        if not isinstance(self.ascii_only, bool):
            raise ValueError("ascii_only must be a boolean")
        if not isinstance(self.space_replacement, str) or not re.fullmatch(
            r"[ ._-]{1,8}", self.space_replacement
        ):
            raise ValueError(
                "Space replacement must contain 1-8 spaces, dots, underscores or hyphens"
            )
        for template_value in (self.filename, self.directory, self.prefix, self.suffix):
            if not isinstance(template_value, str) or len(template_value) > 4096:
                raise ValueError(
                    "Naming templates and affixes must be strings of at most 4096 characters"
                )
        for key, value in self.defaults.items():
            if not isinstance(key, str) or not re.fullmatch(r"[a-z][a-z_]{0,63}", key):
                raise ValueError("Invalid default field name")
            if isinstance(value, bool) or not isinstance(value, (str, int)):
                raise ValueError("Naming defaults must be strings or integers")
            if isinstance(value, int) and not 0 <= value <= 999999999:
                raise ValueError("Integer defaults must contain at most nine digits")
            if key in NUMERIC and (not isinstance(value, int) or not 1 <= value <= 999999999):
                raise ValueError(
                    "Numeric naming defaults must be positive integers of at most nine digits"
                )
        parts = self.directory.split("/") if self.directory else []
        if len(parts) > 16 or not self.filename or any(p in {"", ".", ".."} for p in parts):
            raise ValueError("Invalid naming directory or filename template")
        if "/" in self.filename or "\\" in self.filename or "\\" in self.directory:
            raise ValueError("Use '/' only between directory template components")
        for template in [*parts, self.filename]:
            for literal, name, spec, conversion in Formatter().parse(template):
                if ":" in literal or "\0" in literal:
                    raise ValueError("Drive paths and NUL are not allowed in templates")
                if name is None:
                    continue
                if name not in FIELDS | self.defaults.keys() or conversion:
                    raise ValueError(f"Unknown field or unsupported conversion: {name}")
                if spec and (name not in NUMERIC or not re.fullmatch(r"0?[1-9]d?", spec)):
                    raise ValueError("Only numeric widths 1-9 are supported in templates")

    def _component(self, value: str) -> str:
        if len(value) > 4096:
            raise ValueError("Naming component input exceeds 4096 characters")
        value = unicodedata.normalize("NFC", value)
        if self.ascii_only:
            value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
        if self.case != "preserve":
            value = value.upper() if self.case == "upper" else value.lower()
        value = "".join(
            "_" if ch in '<>:"/\\|?*' or unicodedata.category(ch) in {"Cc", "Cf", "Cs"} else ch
            for ch in value
        )
        value = re.sub(r"\s+", lambda match: self.space_replacement, value).strip(" .")
        if not value or value in {".", ".."}:
            raise ValueError("Naming produced an empty component")
        if value.split(".")[0].rstrip(" .").casefold() in DEVICES:
            value = "_" + value
        if len(value.encode("utf-8")) > 255 or len(value.encode("utf-16-le")) // 2 > 255:
            raise ValueError("Naming component exceeds portable length limits")
        return value

    def render(self, metadata: AudioMetadata, extension: str) -> Path:
        self.validate()
        if metadata.issues:
            raise ValueError("Resolve metadata issues before naming: " + "; ".join(metadata.issues))
        if not re.fullmatch(r"[A-Za-z0-9]{1,16}", extension):
            raise ValueError("Invalid file extension for naming")
        values = dict(self.defaults)
        values.update(
            {
                name: getattr(metadata, name)
                for name in FIELDS
                if getattr(metadata, name) not in (None, "")
                and not (
                    isinstance(getattr(metadata, name), str) and not getattr(metadata, name).strip()
                )
            }
        )

        def render_part(template, prefix="", suffix=""):
            chunks = []
            for literal, name, spec, _conversion in Formatter().parse(template):
                chunks.append(literal)
                if name is not None:
                    value = values.get(name)
                    if value in (None, "") or (isinstance(value, str) and not value.strip()):
                        raise MissingNamingField(f"Missing naming field: {name}")
                    if name in NUMERIC and (
                        isinstance(value, bool)
                        or not isinstance(value, int)
                        or not 1 <= value <= 999999999
                    ):
                        raise ValueError(f"Invalid numeric naming field: {name}")
                    if not isinstance(value, (str, int)) or isinstance(value, bool):
                        raise ValueError(f"Invalid naming field: {name}")
                    # Bound each field before expanding repeated placeholders.
                    formatted = format(value, spec or "")
                    if len(formatted) > 4096:
                        raise ValueError(f"Naming field is too long: {name}")
                    chunks.append(formatted)
            return self._component(prefix + "".join(chunks) + suffix)

        directories = (
            [render_part(part) for part in self.directory.split("/")] if self.directory else []
        )
        filename = render_part(self.filename, self.prefix, self.suffix)
        filename = filename + "." + extension
        if len(filename.encode("utf-8")) > 255 or len(filename.encode("utf-16-le")) // 2 > 255:
            raise ValueError("Filename including extension exceeds portable length limits")
        return Path(*directories, filename)


def validate_naming_tree(root: Path, targets: list[Path]) -> None:
    """Reject ambiguous directory spellings and file/directory prefix conflicts."""
    check_path(root)
    if root.exists() and not root.is_dir():
        raise ValueError("Naming output root must be a directory")
    if root.parent.is_dir():
        for existing in root.parent.iterdir():
            if path_key(existing) == path_key(root) and not (
                root.exists() and os.path.samefile(existing, root)
            ):
                raise FileExistsError("Naming root aliases an existing directory")
    directories: dict[str, Path] = {}
    files = {path_key(target) for target in targets}
    for target in targets:
        relative = target.relative_to(root)
        for part in relative.parts:
            if len(part.encode("utf-8")) > 255 or len(part.encode("utf-16-le")) // 2 > 255:
                raise ValueError("Resolved naming component exceeds portable length limits")
        parent = root
        for name in relative.parts[:-1]:
            directory = parent / name
            key = path_key(directory)
            if key in files:
                raise FileExistsError("Naming target is both a file and directory")
            if key in directories and str(directories[key]) != str(directory):
                raise FileExistsError("Naming directories collide after case/Unicode normalization")
            directories[key] = directory
            if parent.is_dir():
                for existing in parent.iterdir():
                    same_unicode_directory = (
                        unicodedata.normalize("NFC", existing.name) == name
                        and directory.exists()
                        and os.path.samefile(existing, directory)
                    )
                    if (
                        path_key(existing) == key
                        and existing.name != name
                        and not same_unicode_directory
                    ):
                        raise FileExistsError(
                            f"Naming directory aliases an existing name: {directory}"
                        )
            check_path(directory)
            if directory.exists() and not directory.is_dir():
                raise FileExistsError(f"Naming directory is an existing file: {directory}")
            parent = directory
