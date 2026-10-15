"""Local album ZIP preparation with explicit delivery profiles and checksums."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
import tempfile
import unicodedata
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from zipfile import ZIP_STORED, ZipFile

from aud.core.delivery import DeliveryProfile, delivery_profile
from aud.core.ffmpeg import AudioInfo, FFmpegEngine, MediaLimits
from aud.core.metadata import AudioMetadata
from aud.core.models import AudioFile
from aud.core.naming import DEVICES, NamingProfile
from aud.core.operations.audio.convert import ConvertFormat
from aud.core.progress import ProgressEvent, ProgressReporter
from aud.core.results import BatchResult, FileResult, OperationCancelled
from aud.core.safety import Destination, check_path, destinations, staged_write

MANIFEST = "manifest.json"
CHECKSUMS = "checksums.sha256"
MANUAL_REVIEW = (
    "Complete the distributor upload form; this ZIP is not a bulk-import format.",
    "Review track order, titles, artist identities, credits, explicit flags, versions, genre and dates.",
    "Supply or request ISRC/UPC through the distributor; none are invented here.",
    "Review artwork content, text, rights, ICC color profile and DPI in the distributor's current guide.",
    "Listen to full tracks; local properties do not establish mastering quality or source provenance.",
    "Sidecars are copied without resolving or rewriting cue/log references.",
)


def _input_stamp(path: Path) -> tuple[int, int, int, int]:
    check_path(path)
    if not path.is_file():
        raise ValueError(f"Expected a regular package input: {path}")
    info = path.stat()
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


def _member(name: str) -> str:
    if not isinstance(name, str) or len(name) > 4096:
        raise ValueError("Invalid package member name")
    path = PurePosixPath(name)
    if path.is_absolute() or path.as_posix() != name or len(path.parts) > 16:
        raise ValueError("Package members must be normalized relative paths")
    for part in path.parts:
        if part in {"", ".", ".."} or part.endswith((" ", ".")):
            raise ValueError("Invalid package path component")
        if any(ch in '<>:"\\|?*' or unicodedata.category(ch) in {"Cc", "Cf", "Cs"} for ch in part):
            raise ValueError("Nonportable package path component")
        if part.split(".")[0].rstrip(" .").casefold() in DEVICES:
            raise ValueError("Reserved package path component")
        if len(part.encode("utf-8")) > 255 or len(part.encode("utf-16-le")) // 2 > 255:
            raise ValueError("Package path component exceeds portable limits")
    if not path.parts:
        raise ValueError("Empty package member")
    return name


def _check_members(names: Sequence[str]) -> None:
    files: set[str] = set()
    folders: dict[str, str] = {}

    def key(name):
        return unicodedata.normalize("NFC", name).casefold()

    for name in names:
        _member(name)
        if key(name) in files:
            raise FileExistsError("Duplicate normalized package member")
        files.add(key(name))
        parts = PurePosixPath(name).parts
        for index in range(1, len(parts)):
            folder = "/".join(parts[:index])
            if key(folder) in folders and folders[key(folder)] != folder:
                raise FileExistsError("Ambiguous package directory spelling")
            folders[key(folder)] = folder
    if files & folders.keys():
        raise FileExistsError("Package member is both a file and directory")


def _json(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")


def _settings(info, profile, allow_audio_changes, allow_lossy):
    if not info.lossless and not allow_lossy:
        raise ValueError("Delivery requires lossless input unless allow_lossy=True")
    pair = (info.sample_rate, info.bit_depth or 16)
    rate, depth = pair if pair in profile.audio_pairs else (44100, 16)
    changes = []
    if info.sample_rate != rate:
        changes.append("sample_rate")
    if info.bit_depth is not None and info.bit_depth != depth:
        changes.append("bit_depth")
    if info.channels != 2:
        changes.append("channels")
    if changes and not allow_audio_changes:
        raise ValueError(
            "Delivery sample changes require allow_audio_changes=True: " + ", ".join(changes)
        )
    dither = depth == 16 and info.bit_depth is not None and info.bit_depth > 16
    if dither:
        changes.append("triangular_dither")
    changes.append("strip_embedded_metadata_and_artwork")
    if not info.lossless:
        changes.append("lossy_source_derivative")
    return rate, depth, tuple(changes), dither


def _durations(tracks, profile):
    seconds = [track.info.duration for track in tracks]
    if any(value is None or not math.isfinite(value) or value <= 0 for value in seconds):
        raise ValueError("Delivery tracks need known nonzero durations")
    if profile.max_track_seconds and any(
        value > profile.max_track_seconds
        or (profile.track_limit_exclusive and value == profile.max_track_seconds)
        for value in seconds
    ):
        raise ValueError("Track duration exceeds this delivery profile")
    if profile.max_release_seconds and sum(seconds) > profile.max_release_seconds:
        raise ValueError("Release duration exceeds this delivery profile")
    if sum(seconds) / len(seconds) < profile.min_average_seconds:
        raise ValueError("Average track duration is too short for this delivery profile")


def _artwork(path: Path, engine: FFmpegEngine) -> dict:
    if path.suffix.lower() not in {".jpg", ".jpeg"} or path.stat().st_size >= 10_000_000:
        raise ValueError("Delivery artwork must be JPEG smaller than 10 MB")
    data = path.read_bytes()
    if not data.startswith(b"\xff\xd8"):
        raise ValueError("Invalid JPEG artwork")
    offset, dimensions = 2, None
    while offset < len(data):
        if data[offset] != 255:
            raise ValueError("Invalid JPEG marker")
        while offset < len(data) and data[offset] == 255:
            offset += 1
        if offset >= len(data):
            break
        marker = data[offset]
        offset += 1
        if marker in {0xDA, 0xD9}:
            break
        if marker == 1 or 0xD0 <= marker <= 0xD7:
            continue
        length = int.from_bytes(data[offset : offset + 2], "big")
        if length < 2 or offset + length > len(data):
            raise ValueError("Invalid JPEG segment")
        segment = data[offset + 2 : offset + length]
        if marker in {0xC0, 0xC2}:
            if len(segment) < 6 or segment[0] != 8:
                raise ValueError("Invalid JPEG frame")
            dimensions = (
                int.from_bytes(segment[3:5], "big"),
                int.from_bytes(segment[1:3], "big"),
                segment[5],
            )
        offset += length
    if dimensions != (3000, 3000, 3):
        raise ValueError("Delivery artwork must be 3000x3000 JPEG with three color components")
    engine.runner.run(
        [
            engine._tool("ffmpeg"),
            "-nostdin",
            "-v",
            "error",
            "-xerror",
            "-max_alloc",
            "67108864",
            *engine._input(path, image=True),
            "-map",
            "0:v:0",
            "-frames:v",
            "1",
            "-threads",
            "1",
            "-f",
            "null",
            "-",
        ]
    )
    return {"width": 3000, "height": 3000, "jpeg_components": 3, "icc_and_dpi": "manual_review"}


@dataclass(frozen=True)
class PackageTrack:
    source: Path
    member: str
    info: AudioInfo
    metadata: AudioMetadata
    format: str | None = None
    sample_rate: int | None = None
    bit_depth: int | None = None
    changes: tuple[str, ...] = ()
    dither: bool = False

    def preview(self) -> dict:
        return {
            "source": str(self.source),
            "member": self.member,
            "metadata": self.metadata.to_dict(),
            "format": self.format,
            "sample_rate": self.sample_rate,
            "bit_depth": self.bit_depth,
            "changes": self.changes,
            "dither": self.dither,
        }


@dataclass(frozen=True)
class AlbumPreview:
    data: dict

    def to_dict(self) -> dict:
        return copy.deepcopy(self.data)


@dataclass(frozen=True)
class AlbumPackage:
    tracks: tuple[PackageTrack, ...]
    assets: tuple[tuple[Path, str], ...]
    release: dict
    profile: DeliveryProfile
    destination: Destination
    limits: MediaLimits
    stamps: tuple[tuple[Path, tuple[int, int, int, int]], ...]
    artwork: dict | None
    allow_audio_changes: bool = False
    allow_lossy: bool = False

    def _validate(self):
        if self.profile != delivery_profile(self.profile.name):
            raise ValueError("Package profile must match a registered revision")
        if not self.tracks or len(self.tracks) > self.profile.max_tracks or len(self.assets) > 65:
            raise ValueError("Invalid package track/asset count")
        if type(self.allow_audio_changes) is not bool or type(self.allow_lossy) is not bool:
            raise ValueError("Audio change flags must be booleans")
        if any(
            not isinstance(self.release.get(key), str) or not self.release[key].strip()
            for key in ("title", "artist")
        ):
            raise ValueError("Explicit release title and artist are required")
        if self.destination.target.suffix.lower() != ".zip":
            raise ValueError("Album packages use a .zip destination")
        inputs = {track.source for track in self.tracks} | {path for path, name in self.assets}
        if inputs != {path for path, stamp in self.stamps}:
            raise ValueError("Package inputs do not match prepared source stamps")
        if len({track.source for track in self.tracks}) != len(self.tracks):
            raise ValueError("Duplicate package tracks")
        for track in self.tracks:
            if not isinstance(track.metadata, AudioMetadata) or track.metadata.issues:
                raise ValueError("Resolve package metadata issues before execution")
            if self.profile.name == "generic":
                if (
                    track.format,
                    track.sample_rate,
                    track.bit_depth,
                    track.changes,
                    track.dither,
                ) != (None, None, None, (), False):
                    raise ValueError("Generic packages must copy original audio")
            else:
                if not track.metadata.title or not track.metadata.title.strip():
                    raise ValueError("Each delivery track needs an explicit title")
                if track.format not in self.profile.formats or not re.fullmatch(
                    r"audio/[A-Za-z0-9_-]+\." + str(track.format), track.member
                ):
                    raise ValueError("Invalid delivery audio format/member")
                expected = _settings(
                    track.info, self.profile, self.allow_audio_changes, self.allow_lossy
                )
                if (track.sample_rate, track.bit_depth, track.changes, track.dither) != expected:
                    raise ValueError("Delivery settings changed after preparation")
        if self.profile.name != "generic":
            _durations(self.tracks, self.profile)
            if self.artwork is None or sum(name == "cover.jpg" for path, name in self.assets) != 1:
                raise ValueError("Delivery packages require prepared standalone artwork")
        for path, stamp in self.stamps:
            if _input_stamp(path) != stamp:
                raise ValueError(f"Package input changed after preparation: {path}")
        _check_members(
            [track.member for track in self.tracks]
            + [name for path, name in self.assets]
            + [MANIFEST, CHECKSUMS]
        )
        if len(_json(self._manifest([]))) > self.limits.stdout_bytes:
            raise ValueError("Package metadata exceeds its JSON size limit")

    def _manifest(self, files: list[dict]) -> dict:
        return {
            "schema_version": 1,
            "profile": self.profile.to_dict(),
            "release": self.release,
            "tracks": [
                {
                    "sequence": index + 1,
                    "member": track.member,
                    "source_name": track.source.name,
                    "source_codec": track.info.codec,
                    "source_properties": {
                        "sample_rate": track.info.sample_rate,
                        "bit_depth": track.info.bit_depth,
                        "channels": track.info.channels,
                        "duration": track.info.duration,
                    },
                    "output_properties": {
                        "format": track.format,
                        "sample_rate": track.sample_rate,
                        "bit_depth": track.bit_depth,
                        "channels": 2 if track.format else track.info.channels,
                    },
                    "metadata": track.metadata.to_dict(),
                    "changes": track.changes,
                }
                for index, track in enumerate(self.tracks)
            ],
            "files": files,
            "artwork": self.artwork,
            "manual_review_required": list(MANUAL_REVIEW),
            "submission_status": "not_submitted",
        }

    def preview(self) -> AlbumPreview:
        self._validate()
        return AlbumPreview(
            {
                "operation": "AlbumPackage",
                "target": str(self.destination.target),
                "status": self.destination.status,
                "profile": self.profile.to_dict(),
                "tracks": [track.preview() for track in self.tracks],
                "assets": [{"source": str(path), "member": name} for path, name in self.assets],
                "generated": [MANIFEST, CHECKSUMS],
                "manual_review_required": list(MANUAL_REVIEW),
            }
        )

    def execute(
        self,
        result: BatchResult,
        *,
        cancel: Callable[[], bool] | None = None,
        continue_on_error: bool = False,
        progress=None,
    ) -> BatchResult:
        sources = tuple(str(path) for path, stamp in self.stamps)
        destination = self.destination
        progress = ProgressReporter.wrap(progress)
        try:
            progress(ProgressEvent("start", "AlbumPackage", 0, 1, target=str(destination.target)))
            self._validate()
            if destination.status == "skipped":
                result.items.append(
                    FileResult(
                        None, str(destination.target), "AlbumPackage", "skipped", sources=sources
                    )
                )
                progress(
                    ProgressEvent(
                        "finish",
                        "AlbumPackage",
                        1,
                        1,
                        target=str(destination.target),
                        status="skipped",
                    )
                )
                return result
            destinations(
                [(None, destination.target)],
                "overwrite" if destination.replace else "error",
                protected=[path for path, stamp in self.stamps],
            )

            def cancelled():
                if cancel is not None and cancel():
                    raise OperationCancelled("Album packaging cancelled")

            engine = FFmpegEngine(
                replace(
                    self.limits,
                    output_bytes=min(self.limits.output_bytes, self.profile.max_audio_bytes - 1),
                ),
                cancel,
            )
            with (
                staged_write(destination) as temporary,
                tempfile.TemporaryDirectory(prefix="aud-package-", dir=temporary.parent) as scratch,
            ):
                files: list[dict] = []
                with ZipFile(temporary, "w", compression=ZIP_STORED) as archive:

                    def add(path: Path, member: str, maximum: int):
                        progress(
                            ProgressEvent(
                                "start",
                                "AlbumPayload",
                                len(files),
                                len(self.tracks) + len(self.assets),
                                target=member,
                            )
                        )
                        digest, size = hashlib.sha256(), 0
                        assert archive.fp is not None
                        with (
                            path.open("rb") as source,
                            archive.open(member, "w", force_zip64=True) as target,
                        ):
                            while chunk := source.read(1024 * 1024):
                                cancelled()
                                size += len(chunk)
                                if (
                                    size >= maximum
                                    or archive.fp.tell() + len(chunk) > self.limits.output_bytes
                                ):
                                    raise ValueError("Package exceeds its file/output size limit")
                                target.write(chunk)
                                digest.update(chunk)
                        files.append({"path": member, "bytes": size, "sha256": digest.hexdigest()})
                        progress(
                            ProgressEvent(
                                "finish",
                                "AlbumPayload",
                                len(files),
                                len(self.tracks) + len(self.assets),
                                target=member,
                                status="staged",
                            )
                        )

                    for index, track in enumerate(self.tracks):
                        cancelled()
                        path = track.source
                        encoding = None
                        if track.format is not None:
                            path = Path(scratch) / f"{index}.{track.format}"
                            encoding = engine.convert(
                                track.source,
                                ConvertFormat(
                                    track.format,
                                    sample_rate=track.sample_rate,
                                    bit_depth=track.bit_depth,
                                    channels=2,
                                    drop_artwork=True,
                                ),
                                Destination(track.source, path),
                                strip_metadata=True,
                                dither=track.dither,
                            )
                        add(
                            path,
                            track.member,
                            (
                                self.profile.max_audio_bytes
                                if track.format
                                else self.limits.output_bytes + 1
                            ),
                        )
                        if encoding is not None:
                            files[-1]["encoding"] = {
                                key: encoding[key]
                                for key in (
                                    "encoder",
                                    "encoder_version",
                                    "metadata_policy",
                                    "dither",
                                )
                            }
                    for path, member in self.assets:
                        add(path, member, 64 * 1024 * 1024 + 1)
                    self._validate()
                    manifest = _json(self._manifest(files))
                    if len(manifest) > self.limits.stdout_bytes:
                        raise ValueError("Package manifest exceeds JSON size limit")
                    archive.writestr(MANIFEST, manifest)
                    checksums = "".join(f"{item['sha256']}  {item['path']}\n" for item in files)
                    checksums += f"{hashlib.sha256(manifest).hexdigest()}  {MANIFEST}\n"
                    archive.writestr(CHECKSUMS, checksums.encode("utf-8"))
                if temporary.stat().st_size > self.limits.output_bytes:
                    raise ValueError("Package exceeds its output size limit")
                cancelled()
            result.items.append(
                FileResult(
                    None,
                    str(destination.target),
                    "AlbumPackage",
                    "success",
                    sources=sources,
                    details={
                        "profile": self.profile.name,
                        "files": files,
                        "manifest": MANIFEST,
                        "manual_review_required": list(MANUAL_REVIEW),
                    },
                )
            )
            progress(
                ProgressEvent(
                    "finish", "AlbumPackage", 1, 1, target=str(destination.target), status="success"
                )
            )
        except Exception as error:
            result.items.append(
                FileResult(
                    None,
                    str(destination.target),
                    "AlbumPackage",
                    "cancelled" if isinstance(error, OperationCancelled) else "failed",
                    str(error),
                    sources,
                )
            )
            progress(
                ProgressEvent(
                    "finish",
                    "AlbumPackage",
                    1,
                    1,
                    target=str(destination.target),
                    status="cancelled" if isinstance(error, OperationCancelled) else "failed",
                )
            )
            if not isinstance(error, OperationCancelled) and not continue_on_error:
                raise
        return result


def prepare_album(
    files: Sequence[AudioFile],
    target: str | Path,
    *,
    service: str = "generic",
    release: Mapping,
    metadata: Mapping[Path, AudioMetadata] | None = None,
    artwork: str | Path | None = None,
    sidecars: Mapping[str, str | Path] | None = None,
    track_order: Sequence[Path] | None = None,
    default_disc: int | None = None,
    audio_format: str | None = None,
    allow_audio_changes: bool = False,
    allow_lossy: bool = False,
    naming: NamingProfile | None = None,
    limits: MediaLimits | None = None,
    overwrite: str = "error",
    cancel: Callable[[], bool] | None = None,
) -> AlbumPackage:
    profile = delivery_profile(service)
    service = profile.name
    limits = limits or MediaLimits()
    if not files or len(files) > profile.max_tracks or len(sidecars or {}) > 64:
        raise ValueError("Album requires 1..profile.max_tracks tracks and at most 64 sidecars")
    if not isinstance(allow_audio_changes, bool) or not isinstance(allow_lossy, bool):
        raise ValueError("Audio change flags must be booleans")
    if default_disc is not None and (
        isinstance(default_disc, bool) or not isinstance(default_disc, int) or default_disc <= 0
    ):
        raise ValueError("default_disc must be a positive integer")
    release = json.loads(_json(dict(release)))
    if any(
        not isinstance(release.get(key), str) or not release[key].strip()
        for key in ("title", "artist")
    ):
        raise ValueError("Explicit release title and artist are required")
    engine = FFmpegEngine(limits, cancel)
    paths = [Path(os.path.abspath(file.path)) for file in files]
    if len(set(paths)) != len(paths):
        raise ValueError("Duplicate selected package inputs")
    stamps = [(path, _input_stamp(path)) for path in paths]
    rows, metas = [], {}
    metadata_bytes = len(_json(release))
    for path in paths:
        info = engine.probe(path)
        meta = copy.deepcopy(metadata[path] if metadata is not None else info.metadata)
        if not isinstance(meta, AudioMetadata):
            raise TypeError("Package metadata must contain AudioMetadata values")
        metadata_bytes += len(_json(meta.to_dict())) + len(_json(info.tags))
        if metadata_bytes > limits.stdout_bytes:
            raise ValueError("Package metadata exceeds its aggregate size limit")
        rows.append((path, info))
        metas[path] = meta
    if any(not isinstance(meta, AudioMetadata) or meta.issues for meta in metas.values()):
        raise ValueError("Resolve package metadata issues before preparation")
    if track_order is not None:
        order = [Path(os.path.abspath(path)) for path in track_order]
        if len(order) != len(paths) or set(order) != set(paths):
            raise ValueError("track_order must list every selected input exactly once")
    elif service != "generic":
        positions = [
            (meta.disc_number or default_disc, meta.track_number, path)
            for path, meta in metas.items()
        ]
        if any(
            isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 999999999
            for disc, track, path in positions
            for value in (disc, track)
        ):
            raise ValueError("Supply disc/track numbers, default_disc, or an explicit track_order")
        if len({(disc, track) for disc, track, path in positions}) != len(paths):
            raise ValueError("Duplicate album disc/track positions")
        order = [path for disc, track, path in sorted(positions)]
    else:
        order = paths
    info_by_path = dict(rows)
    tracks = []
    if service != "generic" and not artwork:
        raise ValueError("Delivery packages require explicit standalone artwork")
    if audio_format is not None and (service == "generic" or audio_format not in profile.formats):
        raise ValueError("Unsupported delivery output format")
    for index, path in enumerate(order):
        info, meta = info_by_path[path], metas[path]
        format, rate, depth, changes, dither = None, None, None, [], False
        if service != "generic":
            if not meta.title or not meta.title.strip():
                raise ValueError("Each delivery track needs an explicit title")
            format = audio_format or profile.formats[0]
            rate, depth, changes, dither = _settings(
                info, profile, allow_audio_changes, allow_lossy
            )
        member = (
            naming.render(meta, format or path.suffix.lstrip(".")).as_posix()
            if naming
            else (f"{index + 1:04}.{format}" if format else path.name)
        )
        if service != "generic":
            if not re.fullmatch(r"[A-Za-z0-9_-]+\.(wav|flac)", member):
                raise ValueError(
                    "Delivery filenames must have ASCII alphanumeric/hyphen/underscore stems"
                )
            member = "audio/" + member
        tracks.append(
            PackageTrack(path, member, info, meta, format, rate, depth, tuple(changes), dither)
        )
    if service != "generic":
        _durations(tracks, profile)
    assets = []
    artwork_info = None
    if artwork is not None:
        path = Path(os.path.abspath(artwork))
        stamps.append((path, _input_stamp(path)))
        if path.stat().st_size > 64 * 1024 * 1024:
            raise ValueError("Artwork exceeds package sidecar limit")
        artwork_info = _artwork(path, engine) if service != "generic" else None
        assets.append((path, "cover.jpg" if service != "generic" else path.name))
    for name, source in (sidecars or {}).items():
        path = Path(os.path.abspath(source))
        stamps.append((path, _input_stamp(path)))
        if path.stat().st_size > 64 * 1024 * 1024:
            raise ValueError("Sidecar exceeds 64 MiB")
        assets.append((path, ("extras/" if service != "generic" else "") + _member(name)))
    target = Path(os.path.abspath(target))
    if target.suffix.lower() != ".zip":
        raise ValueError("Album packages use a .zip destination")
    destination = destinations(
        [(None, target)], overwrite, protected=[path for path, stamp in stamps]
    )[0]
    package = AlbumPackage(
        tuple(tracks),
        tuple(assets),
        dict(release),
        profile,
        destination,
        limits,
        tuple(stamps),
        artwork_info,
        allow_audio_changes,
        allow_lossy,
    )
    package._validate()
    return package
