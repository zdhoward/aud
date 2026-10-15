import json
import struct
import sys
import time
import wave
import zlib
from pathlib import Path

import pytest

from aud import Dir
from aud.core.operations.audio.convert import ConvertFormat
from aud.exceptions import ConvertError


def test_24bit_pcm_round_trip_preserves_samples(tmp_path):
    source = tmp_path / "original.wav"
    values = [-8388608, -1234567, -1, 0, 1, 7654321, 8388607] * 128
    samples = b"".join((v & 0xFFFFFF).to_bytes(3, "little") for v in values)
    with wave.open(str(source), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(3)
        audio.setframerate(44100)
        audio.writeframes(samples)
    d = Dir(tmp_path, extensions=["wav"])
    d.convert_to_flac(bit_depth=24)
    d.convert_format("wav", bit_depth=24, output_directory=tmp_path / "out")
    from aud.core.ffmpeg import FFmpegEngine

    assert FFmpegEngine().probe(tmp_path / "out" / "original.wav").bit_depth == 24
    # Python <3.12 cannot read WAVE_FORMAT_EXTENSIBLE; compare decoded PCM bytes.
    d.convert_format("raw", bit_depth=24, output_directory=tmp_path / "pcm")
    assert (tmp_path / "pcm" / "original.raw").read_bytes() == samples


def test_source_tags_preserved_with_explicit_override(populated_dir):
    from aud.core.ffmpeg import FFmpegEngine

    d = Dir(populated_dir, extensions=["wav"])
    d.convert_to_mp3(bit_rate=320, tags={"artist": "Artist", "album": "Album", "title": "Old"})
    d.convert_format("flac", tags={"title": "New"})
    info = FFmpegEngine().probe(populated_dir / "song.flac")
    assert info.tags["artist"] == "Artist"
    assert info.tags["album"] == "Album"
    assert info.tags["title"] == "New"


@pytest.mark.parametrize("profile,mode", [("mp3-v0", "vbr"), ("mp3-v2", "vbr"), ("mp3-320", "cbr")])
def test_profiles_record_effective_encoding(populated_dir, profile, mode):
    d = Dir(populated_dir, extensions=["wav"])
    d.convert_format("mp3", profile=profile)
    details = d.last_result.items[0].details
    assert details["profile"] == profile
    assert details["mode"] == mode
    assert details["encoder"] == "libmp3lame"
    json.dumps(d.last_result.to_dict())


def test_profile_requires_explicit_lossy_input_opt_in(populated_dir):
    d = Dir(populated_dir, extensions=["wav"])
    d.convert_to_mp3(bit_rate=192)
    source = (populated_dir / "bloop.mp3").read_bytes()
    with pytest.raises(ConvertError, match="lossless"):
        d.convert_format("flac", profile="flac-preserve")
    assert (populated_dir / "bloop.mp3").read_bytes() == source
    d.convert_format("flac", profile="flac-preserve", allow_lossy=True)


def test_bad_conversion_settings_fail_before_prior_operation(populated_dir):
    from aud.core.operations.audio.effects import Gain

    d = Dir(populated_dir, extensions=["wav"])
    source = (populated_dir / "bloop.wav").read_bytes()
    operation = ConvertFormat("wav")
    operation.sample_rate = -1
    with pytest.raises(ValueError):
        d.execute(d.plan().add(Gain(-3)).add(operation))
    assert (populated_dir / "bloop.wav").read_bytes() == source


@pytest.mark.parametrize(
    "options",
    [
        {"bit_depth": 8.0},
        {"allow_lossy": "false"},
        {"drop_artwork": 1},
        {"profile": "unknown"},
        {"profile": "mp3-v0", "bit_rate": 192},
        {"channels": 0},
        {"tags": {"bad=key": "value"}},
    ],
)
def test_invalid_options_are_rejected(options):
    with pytest.raises(ValueError):
        ConvertFormat("mp3", **options)


def test_cancelled_conversion_is_reported_and_preserves_source(populated_dir, monkeypatch):
    from aud.core.ffmpeg import FFmpegEngine
    from aud.core.results import OperationCancelled

    original = (populated_dir / "bloop.wav").read_bytes()

    def cancel(self, source, operation, destination):
        from aud.core.safety import staged_write

        with staged_write(destination) as temporary:
            temporary.write_bytes(b"partial")
            raise OperationCancelled("cancelled")

    monkeypatch.setattr(FFmpegEngine, "convert", cancel)
    d = Dir(populated_dir, extensions=["wav"])
    result = d.execute(d.plan().add(ConvertFormat("mp3")))
    assert [item.status for item in result.items] == ["cancelled", "cancelled"]
    assert not result
    assert d.get_all() == ["bloop.wav", "song.wav"]
    assert (populated_dir / "bloop.wav").read_bytes() == original
    assert not list(populated_dir.glob(".aud-*"))


def test_timeout_reaps_owned_process():
    from aud.core.ffmpeg import MediaLimits, ProcessRunner

    runner = ProcessRunner(MediaLimits(timeout=0.15))
    before = time.monotonic()
    with pytest.raises(TimeoutError):
        runner.run([sys.executable, "-I", "-c", "import time; time.sleep(10)"])
    assert time.monotonic() - before < 3


def test_active_cancellation_stops_owned_process():
    from aud.core.ffmpeg import MediaLimits, ProcessRunner

    started = None

    def cancel():
        nonlocal started
        if started is None:
            started = time.monotonic()
        return time.monotonic() - started > 0.2

    runner = ProcessRunner(MediaLimits(timeout=5), cancel=cancel)
    with pytest.raises(InterruptedError):
        runner.run([sys.executable, "-I", "-c", "import time; time.sleep(10)"])
    assert started is not None and time.monotonic() - started < 3


def test_diagnostic_output_is_bounded():
    from aud.core.ffmpeg import MediaLimits, ProcessRunner

    runner = ProcessRunner(MediaLimits(stdout_bytes=32))
    with pytest.raises(ValueError, match="output limit"):
        runner.run([sys.executable, "-I", "-c", "print('x' * 4096)"])


@pytest.mark.parametrize("exited", [True, False])
def test_group_cleanup_permission_race_only_ignores_exited_child(monkeypatch, exited):
    from types import SimpleNamespace

    import aud.core.ffmpeg as media
    from aud.core.results import OperationCancelled

    finished = False
    waited = False

    class Process:
        pid = 12345

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def poll(self):
            return 0 if finished else None

        def wait(self):
            nonlocal waited
            waited = True

    def denied(group, signum):
        nonlocal finished
        assert group == 12345
        finished = exited
        raise PermissionError("group signal denied")

    monkeypatch.setattr(media, "sys", SimpleNamespace(platform="darwin"))
    monkeypatch.setattr(media, "signal", SimpleNamespace(SIGKILL=9))
    monkeypatch.setattr(media.subprocess, "Popen", lambda *args, **kwargs: Process())
    monkeypatch.setattr(media.os, "killpg", denied, raising=False)
    runner = media.ProcessRunner(media.MediaLimits(), cancel=lambda: True)
    with pytest.raises(OperationCancelled if exited else PermissionError):
        runner.run(["unused"])
    assert waited is exited


@pytest.mark.parametrize("completion", ["output", "cancel", "timeout"])
def test_completion_rechecks_limits(tmp_path, monkeypatch, completion):
    from aud.core.ffmpeg import MediaLimits, ProcessRunner

    output = tmp_path / "output"
    finished = False
    waited = False

    class Process:
        def poll(self):
            nonlocal finished
            finished = True
            if completion == "output":
                output.write_bytes(b"oversized")
            return 0

        def wait(self):
            nonlocal waited
            waited = True

    monkeypatch.setattr("aud.core.ffmpeg.subprocess.Popen", lambda *args, **kwargs: Process())
    monkeypatch.setattr("aud.core.ffmpeg.time.monotonic", lambda: 2 if finished else 0)
    runner = ProcessRunner(
        MediaLimits(timeout=1, output_bytes=1),
        cancel=lambda: completion == "cancel" and finished,
    )
    error = {"output": ValueError, "cancel": InterruptedError, "timeout": TimeoutError}[completion]
    # Avoid the size fixture also tripping the deadline fixture.
    if completion != "timeout":
        monkeypatch.setattr("aud.core.ffmpeg.time.monotonic", lambda: 0)
    with pytest.raises(error):
        runner.run(["unused"], output)
    assert waited


def test_probe_merges_audio_and_container_tags(tmp_path, monkeypatch):
    from aud.core.ffmpeg import FFmpegEngine

    engine = FFmpegEngine()
    monkeypatch.setattr(engine, "_tool", lambda name: name)
    monkeypatch.setattr(engine, "_input", lambda path: [])
    data = {
        "streams": [
            {
                "codec_type": "audio",
                "codec_name": "vorbis",
                "sample_rate": "44100",
                "channels": 2,
                "tags": {"ARTIST": "Artist", "title": "First", "TITLE": "Stream"},
            }
        ],
        "format": {"tags": {"title": "Container", "encoder": "ignored"}},
    }
    monkeypatch.setattr(engine.runner, "run", lambda arguments: json.dumps(data).encode())
    assert engine.probe(tmp_path / "unused").tags == {"artist": "Artist", "title": "Container"}


def test_ogg_stream_tags_survive_conversion(populated_dir):
    from aud.core.ffmpeg import FFmpegEngine

    d = Dir(populated_dir, extensions=["wav"], pattern="bloop.*")
    d.convert_format("ogg", tags={"artist": "Artist", "title": "Stream"})
    d.convert_format("flac", tags={"title": "Override"})
    assert FFmpegEngine().probe(populated_dir / "bloop.flac").tags["artist"] == "Artist"
    assert "artist" not in d.last_result.items[0].details["unmapped_tags"]


def test_truncated_lossless_output_is_not_published(tmp_path, monkeypatch):
    from aud.core.ffmpeg import AudioInfo, FFmpegEngine
    from aud.core.safety import Destination

    source = tmp_path / "source.wav"
    source.write_bytes(b"source")
    target = tmp_path / "target.flac"
    engine = FFmpegEngine()
    engine._version = "test"
    monkeypatch.setattr(engine, "_tool", lambda name: name)
    monkeypatch.setattr(engine, "_input", lambda path: [])
    monkeypatch.setattr(
        engine,
        "probe",
        lambda path: AudioInfo(
            "pcm_s16le" if path == source else "flac",
            44100,
            1,
            16,
            1.0 if path == source else 0.5,
            None,
        ),
    )

    def encode(arguments, output=None):
        if output is not None:
            output.write_bytes(b"partial")
        return b""

    monkeypatch.setattr(engine.runner, "run", encode)
    with pytest.raises(ValueError, match="duration"):
        engine.convert(source, ConvertFormat("flac"), Destination(source, target))
    assert not target.exists()
    assert source.read_bytes() == b"source"
    assert not list(tmp_path.glob(".aud-*"))


def _png(path: Path):
    def chunk(name, data):
        return (
            struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data))
        )

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress((b"\0" + b"\xff\0\0" * 2) * 2))
        + chunk(b"IEND", b"")
    )


def test_artwork_survives_mp3_to_flac_and_cannot_silently_disappear(populated_dir):
    from aud.core.ffmpeg import FFmpegEngine

    cover = populated_dir / "cover.png"
    _png(cover)
    d = Dir(populated_dir, extensions=["wav"], pattern="bloop.*")
    d.convert_to_mp3(cover=str(cover))
    d.convert_to_flac()
    assert FFmpegEngine().probe(populated_dir / "bloop.flac").artwork
    with pytest.raises(ConvertError, match="artwork"):
        d.convert_format("wav", output_directory=populated_dir / "out")
    d.convert_format("wav", output_directory=populated_dir / "out", drop_artwork=True)


def test_failed_conversion_keeps_source_and_cleans_staging(populated_dir, monkeypatch):
    from aud.core.ffmpeg import FFmpegEngine

    original = (populated_dir / "bloop.wav").read_bytes()

    def fail(self, source, operation, destination):
        from aud.core.safety import staged_write

        with staged_write(destination) as temporary:
            temporary.write_bytes(b"partial")
            raise OSError("encoder failed")

    monkeypatch.setattr(FFmpegEngine, "convert", fail)
    with pytest.raises(ConvertError, match="encoder failed"):
        Dir(populated_dir, extensions=["wav"]).convert_to_mp3()
    assert (populated_dir / "bloop.wav").read_bytes() == original
    assert not list(populated_dir.glob(".aud-*"))
