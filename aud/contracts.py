"""Versioned, JSON-normalized interchange documents; no execution or replay."""

import json
from importlib.resources import files

KINDS = frozenset({"result", "preview", "album_preview", "progress", "list", "inspect", "error"})


def json_document(kind: str, payload, *, version: int = 1) -> dict:
    """Snapshot a payload in a v1 envelope; consumers validate against json_schema()."""
    if type(version) is not int or version != 1:
        raise ValueError("Unsupported JSON contract version")
    if kind not in KINDS:
        raise ValueError(f"Unknown JSON document kind: {kind}")
    if hasattr(payload, "to_dict"):
        payload = payload.to_dict()
    if not isinstance(payload, dict):
        raise TypeError("JSON document payload must be an object")
    return json.loads(
        json.dumps(
            {"schema_version": version, "kind": kind, "payload": payload},
            ensure_ascii=True,
            allow_nan=False,
        )
    )


def json_schema(*, version: int = 1) -> dict:
    """Read the bundled schema without network access; return a fresh object."""
    if type(version) is not int or version != 1:
        raise ValueError("Unsupported JSON contract version")
    return json.loads(
        files("aud").joinpath("schemas").joinpath("v1.json").read_text(encoding="utf-8")
    )
