"""Reference runner for the data-only media/recovery corpus (trusted fixtures)."""

import hashlib
import json
import struct
import wave
import zlib
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile

import pytest
from jsonschema import Draft202012Validator

from aud import Dir, delivery_profile, json_document, json_schema
from aud.core.ffmpeg import FFmpegEngine
from aud.core.operations.audio.convert import ConvertFormat
from aud.core.packaging import _durations, _settings
from aud.core.results import OperationCancelled
from aud.core.safety import staged_write

CORPUS = json.loads(
    (Path(__file__).parents[1] / "conformance/v1/media.json").read_text(encoding="utf-8")
)


def pcm(path, case=None):
    case = case or CORPUS["pcm"][0]
    width = case["bits"] // 8
    data = b"".join(
        value.to_bytes(width, "little", signed=True)
        for value in case["samples"] * case["repeat"] * case["channels"]
    )
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(case["channels"])
        audio.setsampwidth(width)
        audio.setframerate(case["sample_rate"])
        audio.writeframes(data)
    return data


def validate(result):
    Draft202012Validator(json_schema()).validate(json_document("result", result))


def assert_clean(directory):
    assert not list(directory.rglob(".aud-*"))
    assert not list(directory.rglob("aud-package-*"))


@pytest.mark.parametrize("case", CORPUS["pcm"], ids=lambda case: case["id"])
def test_lossless_pcm_corpus(tmp_path, case):
    source = tmp_path / "master.wav"
    expected = pcm(source, case)
    original = source.read_bytes()
    d = Dir(tmp_path, extensions=["wav"])
    first = d.execute(d.plan().add(ConvertFormat("flac", profile="flac-preserve")))
    validate(first)
    info = FFmpegEngine().probe(tmp_path / "master.flac")
    assert (info.bit_depth, info.sample_rate, info.channels) == (
        case["bits"],
        case["sample_rate"],
        case["channels"],
    )
    d.execute(
        d.plan().add(
            ConvertFormat("raw", bit_depth=case["bits"], output_directory=tmp_path / "decoded")
        )
    )
    assert (tmp_path / "decoded/master.raw").read_bytes() == expected
    assert source.read_bytes() == original
    assert_clean(tmp_path)


def artwork(path):
    case = CORPUS["artwork"]

    def chunk(kind, data):
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", case["width"], case["height"], 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(b"\0" + bytes(case["rgba"])))
        + chunk(b"IEND", b"")
    )


def test_metadata_and_artwork_survive_flac_to_mp3(tmp_path):
    pcm(tmp_path / "master.wav")
    cover = tmp_path / "cover.png"
    artwork(cover)
    d = Dir(tmp_path, extensions=["wav"])
    d.execute(d.plan().add(ConvertFormat("flac", tags=CORPUS["metadata"], cover=str(cover))))
    d.execute(d.plan().add(ConvertFormat("mp3", bit_rate=320)))
    info = FFmpegEngine().probe(tmp_path / "master.mp3")
    for key, value in CORPUS["metadata"].items():
        assert info.tags[key] == value
    assert len(info.artwork) == 1
    assert info.metadata.track_number == 2 and info.metadata.track_total == 3
    assert info.metadata.disc_number == 1 and info.metadata.disc_total == 2
    engine = FFmpegEngine()
    pixels = engine.runner.run(
        [
            engine._tool("ffmpeg"),
            "-nostdin",
            "-v",
            "error",
            *engine._input(tmp_path / "master.mp3"),
            "-map",
            "0:v:0",
            "-frames:v",
            "1",
            "-threads",
            "1",
            "-pix_fmt",
            "rgba",
            "-f",
            "rawvideo",
            "-",
        ]
    )
    assert pixels == bytes(CORPUS["artwork"]["rgba"])
    validate(d.last_result)


@pytest.mark.parametrize("case", CORPUS["lossy"], ids=lambda case: case["profile"])
def test_lossy_settings_corpus(populated_dir, case):
    d = Dir(populated_dir, extensions=["wav"], pattern="bloop.*")
    result = d.execute(d.plan().add(ConvertFormat("mp3", profile=case["profile"])))
    details = result.items[0].details
    assert {key: details[key] for key in ("profile", "mode", "encoder")} == {
        key: case[key] for key in ("profile", "mode", "encoder")
    }
    info = FFmpegEngine().probe(populated_dir / "bloop.mp3")
    assert info.codec == "mp3" and info.channels == 2 and info.sample_rate == 44100
    if "bit_rate" in case:
        assert info.bit_rate == case["bit_rate"]
    validate(result)


@pytest.mark.parametrize("case", CORPUS["recovery"], ids=lambda case: case["id"])
def test_encoder_recovery_corpus(tmp_path, monkeypatch, case):
    for name in ("a.wav", "b.wav"):
        pcm(tmp_path / name)
    originals = {path: path.read_bytes() for path in tmp_path.glob("*.wav")}
    output = tmp_path / "out"
    output.mkdir()
    existing = output / "a.flac"
    existing.write_bytes(b"Existing destination")
    original_convert = FFmpegEngine.convert

    def inject(self, source, operation, destination, **options):
        if source.name == "a.wav":
            with staged_write(destination) as temporary:
                temporary.write_bytes(b"Partial output")
                if case["injected"] == "cancelled":
                    raise OperationCancelled("Conformance cancellation")
                raise RuntimeError("Conformance encoder failure")
        return original_convert(self, source, operation, destination, **options)

    monkeypatch.setattr(FFmpegEngine, "convert", inject)
    d = Dir(tmp_path, extensions=["wav"], overwrite="overwrite")
    plan = d.plan().add(ConvertFormat("flac", output_directory=output))
    if case["injected"] == "failed" and not case["continue_on_error"]:
        with pytest.raises(RuntimeError, match="Conformance encoder failure"):
            d.execute(plan)
        result = d.last_result
    else:
        result = d.execute(plan, continue_on_error=case["continue_on_error"])
    assert [item.status for item in result.items] == case["statuses"]
    assert (
        sorted(path.name for path in output.glob("*.flac") if path != existing) == case["published"]
    )
    assert existing.read_bytes() == b"Existing destination"
    assert all(path.read_bytes() == data for path, data in originals.items())
    assert_clean(tmp_path)
    validate(result)


@pytest.mark.parametrize("case", CORPUS["collisions"], ids=lambda case: case["policy"])
def test_collision_corpus(tmp_path, case):
    source = tmp_path / "a.wav"
    pcm(source)
    output = tmp_path / "out"
    output.mkdir()
    existing = output / "a.flac"
    existing.write_bytes(b"Existing destination")
    d = Dir(tmp_path, extensions=["wav"], overwrite=case["policy"])
    plan = d.plan().add(ConvertFormat("flac", output_directory=output))
    if case["raises"]:
        with pytest.raises(FileExistsError):
            d.execute(plan)
        result = d.last_result
    else:
        preview = d.preview(plan).to_dict()
        result = d.execute(plan)
        assert result.items[0].target == preview["steps"][0]["targets"][0]
    assert result.items[0].status == case["status"]
    assert existing.read_bytes() == b"Existing destination"
    if case["new_name"]:
        assert (output / case["new_name"]).exists()
    assert_clean(tmp_path)
    validate(result)


def test_album_order_sidecars_and_checksum_corpus(tmp_path):
    case = CORPUS["album"]
    originals = {}
    for name in case["order"]:
        pcm(tmp_path / name)
        originals[name] = (tmp_path / name).read_bytes()
    cue = tmp_path / case["sidecar_name"]
    cue.write_bytes(case["sidecar_text"].encode())
    d = Dir(tmp_path, extensions=["wav"])
    target = tmp_path / "album.zip"
    result = d.package_album(
        target,
        release=case["release"],
        track_order=case["order"],
        sidecars={case["sidecar_name"]: cue},
    )
    assert result
    with ZipFile(target) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        assert [track["member"] for track in manifest["tracks"]] == case["order"]
        assert manifest["submission_status"] == case["submission_status"]
        assert all(name in archive.namelist() for name in case["generated"])
        assert archive.read(case["sidecar_name"]) == cue.read_bytes()
        for name, data in originals.items():
            assert archive.read(name) == data and (tmp_path / name).read_bytes() == data
        for line in archive.read("checksums.sha256").decode().splitlines():
            digest, name = line.split("  ", 1)
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest
    assert_clean(tmp_path)
    validate(result)


@pytest.mark.parametrize("case", CORPUS["duration_boundaries"])
def test_provider_duration_boundary_corpus(case):
    tracks = [SimpleNamespace(info=SimpleNamespace(duration=value)) for value in case["durations"]]
    if case["accepted"]:
        _durations(tracks, delivery_profile(case["service"]))
    else:
        with pytest.raises(ValueError):
            _durations(tracks, delivery_profile(case["service"]))


@pytest.mark.parametrize("case", CORPUS["delivery_profiles"], ids=lambda case: case["service"])
def test_delivery_settings_corpus(case):
    profile = delivery_profile(case["service"])
    assert profile.formats[0] == case["format"]
    assert profile.max_tracks == case["max_tracks"]
    info = SimpleNamespace(lossless=True, sample_rate=case["input_rate"], bit_depth=24, channels=2)
    if case["needs_consent"]:
        with pytest.raises(ValueError, match="allow_audio_changes"):
            _settings(info, profile, False, False)
    rate, bits, changes, dither = _settings(info, profile, case["needs_consent"], False)
    assert (rate, bits) == (case["output_rate"], case["output_bits"])
    assert dither is case["needs_consent"]
    assert "strip_embedded_metadata_and_artwork" in changes
