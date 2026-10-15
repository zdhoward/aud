"""Explicit, bounded filename-to-metadata parsing without regular expressions."""

import unicodedata
from dataclasses import dataclass
from pathlib import Path
from string import Formatter
from typing import Any

from aud.core.metadata import AudioMetadata
from aud.core.naming import FIELDS, NUMERIC


@dataclass(frozen=True)
class FilenamePattern:
    """Parse a basename stem using named fields and literal separators."""

    template: str = "{track_number:02} - {title}"

    def _parts(self):
        if not isinstance(self.template, str) or not 1 <= len(self.template) <= 2048:
            raise ValueError("Filename pattern must contain 1..2048 characters")
        parts = list(Formatter().parse(self.template))
        fields = set()
        previous_field = False
        for literal, name, spec, conversion in parts:
            if any(ch in "/\\" or unicodedata.category(ch) in {"Cc", "Cf", "Cs"} for ch in literal):
                raise ValueError("Filename patterns accept basename literals only")
            if name is not None:
                if name not in FIELDS or name in fields or conversion is not None:
                    raise ValueError("Filename fields must be unique canonical metadata names")
                if previous_field and not literal:
                    raise ValueError("Adjacent filename fields require a literal separator")
                if spec and (
                    name not in NUMERIC
                    or spec not in {str(i) for i in range(1, 10)} | {f"0{i}" for i in range(1, 10)}
                ):
                    raise ValueError("Only numeric widths 1..9 are supported")
                fields.add(name)
            previous_field = name is not None
        if not fields:
            raise ValueError("Filename pattern must contain a metadata field")
        return parts

    def __post_init__(self):
        self._parts()

    def parse(self, filename: str | Path) -> AudioMetadata:
        if not isinstance(filename, (str, Path)):
            raise TypeError("Filename must be text or a Path basename")
        name = str(filename)
        if (
            not name
            or len(name) > 4096
            or any(ch in "/\\" or unicodedata.category(ch) in {"Cc", "Cf", "Cs"} for ch in name)
        ):
            raise ValueError("Supply one bounded filename, without path separators or controls")
        # Only the last suffix is removed; callers must supply an extension.
        stem, dot, extension = name.rpartition(".")
        if (
            not dot
            or not stem
            or not extension
            or not extension.isascii()
            or not extension.isalnum()
            or len(extension) > 16
        ):
            raise ValueError("Filename parsing requires an explicit alphanumeric extension")
        parts = self._parts()
        remaining = stem
        values: dict[str, Any] = {}
        for index, (literal, field, spec, _conversion) in enumerate(parts):
            if not remaining.startswith(literal):
                raise ValueError("Filename does not match pattern literal")
            remaining = remaining[len(literal) :]
            if field is None:
                continue
            delimiter = parts[index + 1][0] if index + 1 < len(parts) else ""
            if delimiter:
                captured, found, tail = remaining.partition(delimiter)
                if not found:
                    raise ValueError("Filename does not match pattern separator")
                remaining = delimiter + tail
            else:
                captured, remaining = remaining, ""
            if not captured or not captured.strip():
                raise ValueError(f"Empty filename field: {field}")
            if field in NUMERIC:
                if (
                    not captured.isascii()
                    or not captured.isdigit()
                    or len(captured) > 9
                    or (spec and len(captured) != int(spec))
                    or int(captured) <= 0
                ):
                    raise ValueError(f"Invalid numeric filename field: {field}")
                values[field] = int(captured)
            else:
                values[field] = captured
        if remaining:
            raise ValueError("Filename has unmatched trailing text")
        for field in ("track", "disc"):
            number, total = values.get(field + "_number"), values.get(field + "_total")
            if number is not None and total is not None and number > total:
                raise ValueError(f"Filename {field} number exceeds total")
        return AudioMetadata(**values)
