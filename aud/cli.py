"""Dependency-free command line facade over aud's preparation/execution APIs."""

from __future__ import annotations

import argparse
import json
import signal
import sys
from dataclasses import asdict
from pathlib import Path

from aud import AudioChain, AudioMetadata, Dir, MediaLimits, NamingProfile, __version__
from aud.core.ffmpeg import FORMATS, PROFILES, FFmpegEngine
from aud.core.operations.audio.convert import ConvertFormat
from aud.core.operations.audio.effects import (
    Fade,
    Gain,
    HighPassFilter,
    InvertPhase,
    LowPassFilter,
    Pad,
)
from aud.core.progress import ProgressEvent, ProgressReporter
from aud.core.results import OperationCancelled

COMMANDS = ("list", "inspect", "convert", "rename", "effects", "export", "album")
CONFIG_BYTES = 1024 * 1024
EFFECTS = {
    "gain": Gain,
    "fade": Fade,
    "pad": Pad,
    "low_pass": LowPassFilter,
    "high_pass": HighPassFilter,
    "invert_phase": InvertPhase,
}


class UsageError(ValueError):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise UsageError(message)


def _object(value, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _load(path):
    if not Path(path).is_file():
        raise ValueError("Configuration must be a regular file")
    with Path(path).open("rb") as source:
        data = source.read(CONFIG_BYTES + 1)
    if len(data) > CONFIG_BYTES:
        raise ValueError("Configuration exceeds 1 MiB")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"Duplicate configuration key: {key}")
            result[key] = value
        return result

    def constant(value):
        raise ValueError(f"Non-finite JSON number: {value}")

    return _object(
        json.loads(data.decode("utf-8-sig"), object_pairs_hook=pairs, parse_constant=constant),
        "Configuration",
    )


def _keys(value, allowed, label):
    _object(value, label)
    unknown = set(value) - set(allowed)
    if unknown:
        raise ValueError(f"Unknown {label} fields: {', '.join(sorted(unknown))}")


def _metadata(value):
    result = {}
    numeric = {"year", "track_number", "track_total", "disc_number", "disc_total"}
    text = {"artist", "album_artist", "album", "title"}
    for name, row in _object(value, "Metadata").items():
        _keys(row, numeric | text | {"tags", "issues"}, "track metadata")
        for key, item in row.items():
            if key in text and item is not None and not isinstance(item, str):
                raise ValueError(f"Metadata {key} must be text or null")
            if (
                key in numeric
                and item is not None
                and (type(item) is not int or not 1 <= item <= 999999999)
            ):
                raise ValueError(f"Metadata {key} must be a positive integer or null")
        tags = row.get("tags", {})
        if not isinstance(tags, dict) or any(not isinstance(item, str) for item in tags.values()):
            raise ValueError("Metadata tags must map strings to strings")
        issues = row.get("issues", [])
        if not isinstance(issues, list) or any(not isinstance(item, str) for item in issues):
            raise ValueError("Metadata issues must be an array of strings")
        result[name] = AudioMetadata(**{**row, "issues": tuple(issues)})
    return result


def _parser():
    parser = Parser(prog="aud", allow_abbrev=False)
    parser.add_argument("--version", action="version", version=f"aud {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in COMMANDS:
        command = commands.add_parser(name, allow_abbrev=False)
        command.add_argument("directory", type=Path)
        command.add_argument(
            "--extensions",
            nargs="+",
            default=[],
            metavar="EXT",
            help="Explicit selection; default selects nothing (Python API parity)",
        )
        command.add_argument("--pattern", help="Narrow selection with a filename glob")
        command.add_argument("--json", action="store_true", help="Emit one JSON document on stdout")
        command.add_argument(
            "--progress", action="store_true", help="Write file-level progress to stderr"
        )
        command.add_argument("--timeout", type=float, default=300.0, help="Per-process seconds")
        command.add_argument("--output-bytes", type=int, default=MediaLimits().output_bytes)
        if name in {"list", "inspect"}:
            continue
        command.add_argument("--dry-run", action="store_true")
        command.add_argument(
            "--overwrite", choices=["error", "skip", "overwrite", "auto-rename"], default="error"
        )
        command.add_argument("--continue-on-error", action="store_true")
        if name in {"rename", "effects", "album"}:
            command.add_argument("--config", type=Path, required=True)
        if name == "rename":
            command.add_argument("--output-directory", type=Path, required=True)
            command.add_argument("--copy", action="store_true", help="Copy rather than move")
        if name == "album":
            command.add_argument("--target", type=Path, required=True)
            command.add_argument("--service", default="generic")
        if name in {"convert", "export", "effects"}:
            command.add_argument("--format", choices=sorted(FORMATS), required=name != "effects")
            command.add_argument("--output-directory", type=Path, required=name == "export")
            command.add_argument("--profile", choices=sorted(PROFILES))
            command.add_argument("--sample-rate", type=int)
            command.add_argument("--bit-depth", type=int)
            command.add_argument("--bit-rate", type=int, help="kb/s for lossy formats")
            command.add_argument("--channels", type=int)
            command.add_argument("--allow-lossy", action="store_true")
            command.add_argument("--drop-artwork", action="store_true")
    return parser


def _conversion(args):
    return ConvertFormat(
        args.format,
        sample_rate=args.sample_rate,
        bit_depth=args.bit_depth,
        bit_rate=args.bit_rate,
        channels=args.channels,
        output_directory=args.output_directory,
        profile=args.profile,
        allow_lossy=args.allow_lossy,
        drop_artwork=args.drop_artwork,
    )


def _plan(directory, args, cancel):
    if args.command in {"convert", "export"}:
        if args.command == "export" and args.output_directory.absolute() == directory.directory:
            raise ValueError("Export directory must differ from the source directory")
        return directory.plan().add(_conversion(args))
    config = _load(args.config)
    if args.command == "rename":
        _keys(config, {"profile", "metadata"}, "rename configuration")
        return directory.plan_naming(
            NamingProfile(**_object(config["profile"], "Naming profile")),
            args.output_directory,
            metadata=_metadata(config["metadata"]) if "metadata" in config else None,
            copy=args.copy,
        )
    if args.command == "effects":
        _keys(config, {"effects"}, "effects configuration")
        if not isinstance(config.get("effects"), list) or not 1 <= len(config["effects"]) <= 64:
            raise ValueError("Supply 1..64 ordered effects")
        effects = []
        for row in config["effects"]:
            row = dict(_object(row, "Effect"))
            name = row.pop("type", None)
            if not isinstance(name, str) or name not in EFFECTS:
                raise ValueError("Unknown effect type")
            effects.append(EFFECTS[name](**row))
        if args.format is None and any(
            (
                args.output_directory,
                args.profile,
                args.sample_rate,
                args.bit_depth,
                args.bit_rate,
                args.channels,
                args.allow_lossy,
                args.drop_artwork,
            )
        ):
            raise ValueError("Effects output options require --format")
        return directory.plan().add(
            AudioChain(effects, output=_conversion(args) if args.format else None)
        )
    _keys(
        config,
        {
            "release",
            "metadata",
            "artwork",
            "sidecars",
            "track_order",
            "default_disc",
            "audio_format",
            "allow_audio_changes",
            "allow_lossy",
            "naming",
        },
        "album configuration",
    )
    if "metadata" in config:
        config["metadata"] = _metadata(config["metadata"])
    if "naming" in config:
        config["naming"] = NamingProfile(**_object(config["naming"], "Naming profile"))
    return directory.plan_album(args.target, service=args.service, cancel=cancel, **config)


def _emit(data, machine):
    if machine:
        print(json.dumps(data, ensure_ascii=True, allow_nan=False))
    else:
        # Escape file/tag-controlled terminal control characters.
        print(json.dumps(data, ensure_ascii=True, allow_nan=False, indent=2))


def _progress(event):
    target = json.dumps(event.target or event.source or "", ensure_ascii=True)
    print(
        f"{event.operation} {event.completed}/{event.total} {event.status or event.phase} {target}",
        file=sys.stderr,
        flush=True,
    )


def run(argv=None, *, cancel=None):
    """Run a command; return 0 success, 1 failure, 2 usage/config, or 130 cancelled."""
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        args = _parser().parse_args(argv)
    except UsageError as error:
        data = {"succeeded": False, "error": str(error), "exit_code": 2, "result": None}
        if "--json" in argv:
            _emit(data, True)
        else:
            print("aud: " + json.dumps(str(error), ensure_ascii=True), file=sys.stderr)
        return 2
    directory = None
    progress = ProgressReporter(_progress if args.progress else None)
    try:
        directory = Dir(
            args.directory,
            extensions=args.extensions,
            pattern=args.pattern,
            overwrite=getattr(args, "overwrite", "error"),
            media_limits=MediaLimits(timeout=args.timeout, output_bytes=args.output_bytes),
        )
        if cancel is not None and cancel():
            raise OperationCancelled("Command cancelled")
        if args.command == "list":
            data = {"files": directory.get_all()}
        elif args.command == "inspect":
            engine = FFmpegEngine(directory.media_limits, cancel)
            inspected = []
            files = list(directory)
            for index, file in enumerate(files):
                progress(
                    ProgressEvent("start", "Inspect", index, len(files), source=str(file.path))
                )
                inspected.append({"path": str(file.path), **asdict(engine.probe(file.path))})
                progress(
                    ProgressEvent(
                        "finish",
                        "Inspect",
                        index + 1,
                        len(files),
                        source=str(file.path),
                        status="success",
                    )
                )
            data = {"files": inspected}
        else:
            if not directory.get_all():
                raise ValueError("No selected files; specify --extensions and check --pattern")
            plan = _plan(directory, args, cancel)
            if cancel is not None and cancel():
                raise OperationCancelled("Command cancelled after preparation")
            if args.dry_run:
                data = {"dry_run": True, "preview": directory.preview(plan).to_dict()}
            else:
                result = directory.execute(
                    plan, cancel=cancel, continue_on_error=args.continue_on_error, progress=progress
                )
                _emit(result.to_dict(), args.json)
                return (
                    130
                    if any(item.status == "cancelled" for item in result.items)
                    else (0 if result else 1)
                )
        _emit(data, args.json)
        return 0
    except (Exception, KeyboardInterrupt) as error:
        cancelled = isinstance(error, (OperationCancelled, KeyboardInterrupt))
        result = directory.last_result.to_dict() if directory is not None else None
        code = 130 if cancelled else (1 if result and result["items"] else 2)
        data = {
            "succeeded": False,
            "error": str(error) or "Command cancelled",
            "exit_code": code,
            "result": result,
        }
        if args.json:
            _emit(data, True)
        else:
            print(json.dumps(data, ensure_ascii=True, indent=2), file=sys.stderr)
        return code


def main() -> None:
    argv = sys.argv[1:]
    # Preserve the previous read-only entry form; use subcommands for real work.
    if not argv:
        print("Usage: aud <command> <directory> [options]")
        raise SystemExit(1)
    if len(argv) == 1 and not argv[0].startswith("-") and argv[0] not in COMMANDS:
        directory = Path(argv[0])
        if not directory.is_dir():
            print("Directory does not exist: " + json.dumps(str(directory), ensure_ascii=True))
            raise SystemExit(1)
        print(f"Found {len(Dir(directory).get_all())} files")
        return
    requested = False

    def interrupt(signum, frame):
        nonlocal requested
        requested = True

    previous = signal.signal(signal.SIGINT, interrupt)
    try:
        code = run(argv, cancel=lambda: requested)
    finally:
        signal.signal(signal.SIGINT, previous)
    if code:
        raise SystemExit(code)


if __name__ == "__main__":
    main()
