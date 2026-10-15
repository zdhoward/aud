from __future__ import annotations

import json
import math
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aud.core.metadata import AudioMetadata
from aud.core.results import OperationCancelled
from aud.core.safety import Destination, check_path, staged_write


@dataclass(frozen=True)
class MediaLimits:
    timeout: float = 300.0
    stdout_bytes: int = 4 * 1024 * 1024
    stderr_bytes: int = 128 * 1024
    output_bytes: int = 8 * 1024 * 1024 * 1024

    def __post_init__(self):
        if (
            isinstance(self.timeout, bool)
            or not isinstance(self.timeout, (int, float))
            or not math.isfinite(self.timeout)
            or self.timeout <= 0
        ):
            raise ValueError("Media timeout must be finite and positive")
        for value in (self.stdout_bytes, self.stderr_bytes, self.output_bytes):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError("Media byte limits must be positive integers")


class ProcessRunner:
    def __init__(self, limits: MediaLimits, cancel: Callable[[], bool] | None = None):
        self.limits = limits
        self.cancel = cancel

    def run(self, arguments: list[str], output: Path | None = None) -> bytes:
        environment = {
            key: os.environ[key]
            for key in ("SystemRoot", "WINDIR", "TEMP", "TMP")
            if key in os.environ
        }
        environment["LANG"] = "C.UTF-8"
        options: dict[str, Any]
        if sys.platform == "win32":
            options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
        else:
            options = {"start_new_session": True}
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            process = subprocess.Popen(
                arguments,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                shell=False,
                env=environment,
                **options,
            )
            started = time.monotonic()

            def check_limits():
                if self.cancel is not None and self.cancel():
                    raise OperationCancelled("Media operation cancelled")
                if time.monotonic() - started > self.limits.timeout:
                    raise TimeoutError("Media process exceeded its timeout")
                if (
                    os.fstat(stdout.fileno()).st_size > self.limits.stdout_bytes
                    or os.fstat(stderr.fileno()).st_size > self.limits.stderr_bytes
                    or (
                        output is not None
                        and output.exists()
                        and output.stat().st_size > self.limits.output_bytes
                    )
                ):
                    raise ValueError("Media process exceeded its output limit")

            try:
                while True:
                    check_limits()
                    code = process.poll()
                    if code is not None:
                        check_limits()
                        break
                    time.sleep(0.05)
                stderr.seek(0)
                if code:
                    message = (
                        stderr.read(self.limits.stderr_bytes)
                        .decode("utf-8", errors="replace")
                        .strip()
                    )
                    raise RuntimeError(f"Media process failed ({code}): {message}")
                stdout.seek(0)
                return stdout.read(self.limits.stdout_bytes)
            finally:
                if process.poll() is None:
                    if sys.platform == "win32":
                        process.kill()
                    else:
                        try:
                            os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                process.wait()


@dataclass(frozen=True)
class AudioInfo:
    codec: str
    sample_rate: int
    channels: int
    bit_depth: int | None
    duration: float | None
    bit_rate: int | None
    tags: dict[str, str] = field(default_factory=dict)
    artwork: tuple[int, ...] = ()

    @property
    def metadata(self) -> AudioMetadata:
        return AudioMetadata.from_tags(self.tags)

    @property
    def lossless(self) -> bool:
        return self.codec.startswith("pcm_") or self.codec in {"flac", "alac", "wavpack", "ape"}


PROFILES = {
    "flac-preserve": ("flac", None, None),
    "mp3-v0": ("mp3", 0, None),
    "mp3-v2": ("mp3", 2, None),
    "mp3-320": ("mp3", None, 320),
}
FORMATS = {"wav", "raw", "flac", "mp3", "ogg"}
PCM = {8: "pcm_u8", 16: "pcm_s16le", 24: "pcm_s24le", 32: "pcm_s32le"}
RAW = {8: "u8", 16: "s16le", 24: "s24le", 32: "s32le"}
INPUT_FORMATS = "wav,mp3,flac,ogg,mov,matroska,aiff,ape,wv,aac,asf"


def validate_conversion(operation) -> None:
    if operation.target_format not in FORMATS:
        raise ValueError(f"Unsupported conversion format: {operation.target_format}")
    for name in ("sample_rate", "bit_rate"):
        value = getattr(operation, name)
        if value is not None and (
            isinstance(value, bool) or not isinstance(value, int) or value <= 0
        ):
            raise ValueError(f"{name} must be a positive integer")
    if operation.channels is not None and (
        isinstance(operation.channels, bool)
        or not isinstance(operation.channels, int)
        or not 1 <= operation.channels <= 64
    ):
        raise ValueError("channels must be an integer from 1 to 64")
    if operation.bit_depth is not None and (
        isinstance(operation.bit_depth, bool)
        or not isinstance(operation.bit_depth, int)
        or operation.bit_depth not in PCM
    ):
        raise ValueError(f"Unsupported bit depth: {operation.bit_depth} (use 8, 16, 24, or 32)")
    if operation.target_format == "flac" and operation.bit_depth not in (None, 16, 24):
        raise ValueError("The FLAC encoding path supports 16 or 24 bits")
    if operation.profile is not None:
        if not isinstance(operation.profile, str):
            raise ValueError("Encoding profile must be a string")
        if operation.profile not in PROFILES:
            raise ValueError(f"Unknown encoding profile: {operation.profile}")
        format, _, _ = PROFILES[operation.profile]
        if format != operation.target_format:
            raise ValueError("Encoding profile does not match the target format")
        if operation.bit_rate is not None:
            raise ValueError("Use either an encoding profile or an explicit bit_rate")
    for name in ("allow_lossy", "drop_artwork"):
        if not isinstance(getattr(operation, name), bool):
            raise ValueError(f"{name} must be a boolean")
    if operation.bit_rate is not None and operation.target_format not in {"mp3", "ogg"}:
        raise ValueError("bit_rate applies only to lossy output")
    for key, value in (operation.tags or {}).items():
        if (
            not isinstance(key, str)
            or not isinstance(value, str)
            or not key
            or "=" in key
            or "\0" in key + value
        ):
            raise ValueError("Tags must have nonempty string keys and string values without NUL")


class FFmpegEngine:
    def __init__(self, limits: MediaLimits | None = None, cancel: Callable[[], bool] | None = None):
        self.limits = limits or MediaLimits()
        self.runner = ProcessRunner(self.limits, cancel)
        self._tools: dict[str, str] = {}
        self._version: str | None = None

    def _tool(self, name: str) -> str:
        if name not in self._tools:
            path = shutil.which(name)
            if not path:
                raise RuntimeError(
                    f"{name} is required for audio processing; install FFmpeg and add it to PATH"
                )
            if os.name == "nt" and Path(path).suffix.lower() != ".exe":
                raise ValueError(f"Expected a native {name} executable")
            self._tools[name] = str(Path(path).absolute())
        return self._tools[name]

    def _input(self, path: Path, *, image=False) -> list[str]:
        check_path(path.absolute())
        if not path.is_file():
            raise ValueError(f"Expected a regular local media file: {path}")
        formats = "image2,jpeg_pipe,png_pipe" if image else INPUT_FORMATS
        return [
            "-protocol_whitelist",
            "file,pipe",
            "-format_whitelist",
            formats,
            "-threads",
            "1",
            "-i",
            str(path.absolute()),
        ]

    def probe(self, path: Path) -> AudioInfo:
        data = json.loads(
            self.runner.run(
                [
                    self._tool("ffprobe"),
                    "-v",
                    "error",
                    "-max_alloc",
                    "67108864",
                    *self._input(path),
                    "-show_streams",
                    "-show_format",
                    "-of",
                    "json",
                ]
            )
        )
        streams = data.get("streams", [])
        audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
        if audio is None:
            raise ValueError("Input has no audio stream")
        bits = int(audio.get("bits_per_raw_sample") or audio.get("bits_per_sample") or 0)
        duration = audio.get("duration") or data.get("format", {}).get("duration")
        duration = float(duration) if duration not in (None, "N/A") else None
        if duration is not None and (not math.isfinite(duration) or duration < 0):
            raise ValueError("Invalid media duration")
        # Container values take precedence over matching primary-audio values.
        tags: dict[str, str] = {}
        for scope in (audio.get("tags", {}), data.get("format", {}).get("tags", {})):
            tags.update(
                {
                    str(k).casefold(): str(v)
                    for k, v in scope.items()
                    if str(k).casefold() != "encoder"
                }
            )
        return AudioInfo(
            str(audio["codec_name"]),
            int(audio["sample_rate"]),
            int(audio["channels"]),
            bits or None,
            duration,
            int(audio["bit_rate"]) if audio.get("bit_rate") else None,
            tags,
            tuple(
                int(s["index"])
                for s in streams
                if s.get("codec_type") == "video" and s.get("disposition", {}).get("attached_pic")
            ),
        )

    def _decoded_duration(self, source: Path) -> float:
        progress = self.runner.run(
            [
                self._tool("ffmpeg"),
                "-nostdin",
                "-v",
                "error",
                "-xerror",
                "-max_alloc",
                "67108864",
                *self._input(source),
                "-map",
                "0:a:0",
                "-threads",
                "1",
                "-progress",
                "pipe:1",
                "-stats_period",
                "60",
                "-f",
                "null",
                "-",
            ]
        )
        times = [
            line.partition(b"=")[2]
            for line in progress.splitlines()
            if line.startswith(b"out_time_us=")
        ]
        if not times:
            raise ValueError("Decoded duration is unavailable")
        duration = int(times[-1]) / 1_000_000
        if not math.isfinite(duration) or duration < 0:
            raise ValueError("Invalid decoded duration")
        return duration

    def convert(self, source: Path, operation, destination: Destination, *, effects=()) -> dict:
        from aud.core.effect_chain import compile_effects, validate_effects
        from aud.core.operations.audio.effects import Fade

        validate_conversion(operation)
        info = self.probe(source)
        duration = info.duration
        if effects:
            validate_effects(effects)
            if any(isinstance(effect, Fade) and effect.fade_out for effect in effects) and (
                not info.lossless or duration is None
            ):
                duration = self._decoded_duration(source)
        filters, expected_duration = (
            compile_effects(effects, info.sample_rate, info.channels, duration)
            if effects
            else ([], info.duration)
        )
        format = operation.target_format
        if operation.profile and not info.lossless and not operation.allow_lossy:
            raise ValueError(
                "Encoding profiles require lossless input; allow_lossy=True permits a deliberate derivative"
            )
        rate = operation.sample_rate or info.sample_rate
        channels = operation.channels or info.channels
        depth = operation.bit_depth or info.bit_depth or 16
        if operation.profile == "flac-preserve" and (
            rate != info.sample_rate
            or channels != info.channels
            or (info.bit_depth is not None and depth != info.bit_depth)
            or info.codec in {"pcm_f32le", "pcm_f64le"}
        ):
            raise ValueError("Preservation profile cannot change source sample properties")
        if format == "flac" and depth not in (16, 24):
            raise ValueError(
                "The FLAC encoding path supports 16 or 24 bits; select an explicit supported depth"
            )
        if format == "mp3" and rate not in {
            8000,
            11025,
            12000,
            16000,
            22050,
            24000,
            32000,
            44100,
            48000,
        }:
            raise ValueError(
                "MP3 cannot preserve this sample rate; select an explicit supported sample_rate"
            )
        if format == "mp3" and channels > 2:
            raise ValueError("MP3 needs explicit mono/stereo conversion for multichannel input")
        cover = Path(operation.cover) if operation.cover else None
        has_art = bool(info.artwork or cover)
        if has_art and format not in {"mp3", "flac"} and not operation.drop_artwork:
            raise ValueError("Target cannot preserve artwork; set drop_artwork=True explicitly")
        if cover is not None and (not cover.is_file() or cover.stat().st_size > 32 * 1024 * 1024):
            raise ValueError("Artwork must be a local image no larger than 32 MiB")
        codecs = {
            "wav": PCM.get(depth),
            "raw": PCM.get(depth),
            "flac": "flac",
            "mp3": "libmp3lame",
            "ogg": "libvorbis",
        }
        codec = codecs[format]
        if codec is None:
            raise ValueError(f"Unsupported PCM depth: {depth}")
        if format in {"wav", "raw"} and operation.bit_depth is None and info.codec == "pcm_f32le":
            codec = "pcm_f32le"
        if self._version is None:
            self._version = (
                self.runner.run([self._tool("ffmpeg"), "-version"])
                .decode("utf-8", errors="replace")
                .splitlines()[0]
            )
        args = [
            self._tool("ffmpeg"),
            "-hide_banner",
            "-nostdin",
            "-v",
            "error",
            "-y",
            "-xerror",
            "-max_alloc",
            "67108864",
            "-filter_threads",
            "1",
            *self._input(source),
        ]
        if cover is not None and not operation.drop_artwork:
            args.extend(self._input(cover, image=True))
        args.extend(
            [
                "-map",
                "0:a:0",
                "-map_metadata",
                "0",
                "-map_metadata:g",
                "0:s:a:0",
                "-metadata",
                "encoder=",
                "-c:a",
                codec,
                "-ar",
                str(rate),
                "-ac",
                str(channels),
                "-threads",
                "1",
            ]
        )
        art_count = 0
        if has_art and not operation.drop_artwork:
            if cover is not None:
                args.extend(["-map", "1:v:0"])
                art_count = 1
            else:
                for index in info.artwork:
                    args.extend(["-map", f"0:{index}"])
                art_count = len(info.artwork)
            args.extend(["-c:v", "copy", "-disposition:v", "attached_pic"])
        if format == "flac":
            args.extend(
                ["-sample_fmt", "s16" if depth == 16 else "s32", "-bits_per_raw_sample", str(depth)]
            )
        elif format in {"mp3", "ogg"} and operation.bit_depth is not None:
            filters.append(f"aformat=sample_fmts={ {8:'u8',16:'s16',24:'s32',32:'s32'}[depth] }")
        if filters:
            args.extend(["-af", ",".join(filters)])
        mode = None
        bit_rate = operation.bit_rate
        if operation.profile:
            _, quality, bit_rate = PROFILES[operation.profile]
            if quality is not None:
                args.extend(["-q:a", str(quality)])
                mode = "vbr"
        if format == "mp3" and mode != "vbr":
            if bit_rate is None:
                nominal = round((info.bit_rate or 0) / 1000)
                bit_rate = (
                    nominal
                    if info.codec == "mp3"
                    and nominal in {32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320}
                    else 192
                )
            mode = "cbr"
        if bit_rate is not None:
            args.extend(["-b:a", f"{bit_rate}k"])
        for key, value in (operation.tags or {}).items():
            args.extend(["-metadata", f"{key}={value}"])
        raw_format = "f32le" if codec == "pcm_f32le" else RAW.get(depth, "s16le")
        with staged_write(destination) as temporary:
            self.runner.run(
                [*args, "-f", raw_format if format == "raw" else format, str(temporary)],
                output=temporary,
            )
            if format == "raw":
                if not temporary.stat().st_size or temporary.stat().st_size % (
                    channels * (depth // 8)
                ):
                    raise ValueError("Raw output is empty or not frame-aligned")
                verification_input = [
                    "-protocol_whitelist",
                    "file,pipe",
                    "-f",
                    raw_format,
                    "-ar",
                    str(rate),
                    "-ac",
                    str(channels),
                    "-i",
                    str(temporary),
                ]
                output_info = None
            else:
                output_info = self.probe(temporary)
                expected_codec = {"mp3": "mp3", "ogg": "vorbis"}.get(format, codec)
                if output_info.codec != expected_codec:
                    raise ValueError("Output codec validation failed")
                if output_info.sample_rate != rate or output_info.channels != channels:
                    raise ValueError("Output sample rate/channel validation failed")
                if format in {"wav", "flac"} and output_info.bit_depth != depth:
                    raise ValueError("Output bit-depth validation failed")
                if (
                    info.lossless
                    and expected_duration is not None
                    and expected_duration > 0
                    and format in {"wav", "flac"}
                ):
                    if output_info.duration is None or abs(
                        output_info.duration - expected_duration
                    ) > max(0.001, 2 / rate):
                        raise ValueError("Output duration validation failed")
                if len(output_info.artwork) != art_count:
                    raise ValueError("Output artwork validation failed")
                if mode == "cbr" and output_info.bit_rate != bit_rate * 1000:
                    raise ValueError("Output MP3 bitrate validation failed")
                verification_input = self._input(temporary)
            self.runner.run(
                [
                    self._tool("ffmpeg"),
                    "-nostdin",
                    "-v",
                    "error",
                    "-xerror",
                    "-max_alloc",
                    "67108864",
                    *verification_input,
                    "-map",
                    "0:a:0",
                    "-threads",
                    "1",
                    "-f",
                    "null",
                    "-",
                ]
            )
            if self.runner.cancel is not None and self.runner.cancel():
                raise OperationCancelled("Media operation cancelled before publication")
        expected_tags = dict(info.tags)
        expected_tags.update(
            {key.casefold(): value for key, value in (operation.tags or {}).items()}
        )
        unmapped = [
            key
            for key, value in expected_tags.items()
            if output_info is None or output_info.tags.get(key) != value
        ]
        return {
            "encoder": codec,
            "encoder_version": self._version,
            "profile": operation.profile,
            "mode": mode,
            "sample_rate": rate,
            "channels": channels,
            "bit_depth": depth if format in {"wav", "raw", "flac"} else None,
            "input_codec": info.codec,
            "artwork": art_count,
            "unmapped_tags": unmapped,
            "effects": [type(effect).__name__ for effect in effects],
            "source_metadata": info.metadata.to_dict(),
            "output_metadata": output_info.metadata.to_dict() if output_info is not None else None,
        }
