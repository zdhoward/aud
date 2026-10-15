"""Canonical views of tags; original values are never rewritten or discarded."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from datetime import date as calendar_date


@dataclass(frozen=True)
class AudioMetadata:
    artist: str | None = None
    album_artist: str | None = None
    album: str | None = None
    title: str | None = None
    year: int | None = None
    track_number: int | None = None
    track_total: int | None = None
    disc_number: int | None = None
    disc_total: int | None = None
    tags: dict[str, str] = field(default_factory=dict)
    issues: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_tags(cls, source: Mapping[str, str]) -> AudioMetadata:
        tags = {key.casefold(): value for key, value in source.items()}
        issues = []

        def text(*keys):
            present = [tags[key] for key in keys if tags.get(key)]
            if len(set(present)) > 1:
                issues.append(f"Conflicting aliases: {', '.join(keys)}")
                return None
            return present[0] if present else None

        def number(value, label):
            if value is None:
                return None
            if not re.fullmatch(r"[0-9]{1,9}", value) or int(value) <= 0:
                issues.append(f"Invalid {label}")
                return None
            return int(value)

        def position(prefix):
            value = text(prefix, f"{prefix}number")
            total_value = text(f"{prefix}total", f"total{prefix}s")
            parts = value.split("/") if value is not None else []
            if len(parts) > 2:
                issues.append(f"Invalid {prefix} position")
                return None, number(total_value, f"{prefix} total")
            index = number(parts[0], f"{prefix} number") if parts else None
            embedded = number(parts[1], f"{prefix} total") if len(parts) == 2 else None
            explicit = number(total_value, f"{prefix} total")
            if explicit is not None and embedded is not None and explicit != embedded:
                issues.append(f"Conflicting {prefix} totals")
                total = None
            else:
                total = explicit if explicit is not None else embedded
            if index is not None and total is not None and index > total:
                issues.append(f"{prefix.capitalize()} number exceeds total")
                return None, None
            return index, total

        track, tracks = position("track")
        disc, discs = position("disc")
        years = []
        for key in ("date", "year"):
            value = tags.get(key)
            if value:
                try:
                    if not re.fullmatch(r"[0-9]{4}(?:-[0-9]{2}(?:-[0-9]{2})?)?", value):
                        raise ValueError
                    full_date = value + (
                        "-01-01" if len(value) == 4 else "-01" if len(value) == 7 else ""
                    )
                    years.append(calendar_date.fromisoformat(full_date).year)
                except ValueError:
                    issues.append("Invalid year/date")
        year = years[0] if years and len(set(years)) == 1 else None
        if len(set(years)) > 1:
            issues.append("Conflicting year/date")
        return cls(
            artist=text("artist"),
            album_artist=text("album_artist", "albumartist", "album artist"),
            album=text("album"),
            title=text("title"),
            year=year,
            track_number=track,
            track_total=tracks,
            disc_number=disc,
            disc_total=discs,
            tags=dict(source),
            issues=tuple(issues),
        )
