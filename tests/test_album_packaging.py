import hashlib
import json
import wave
from dataclasses import replace
from zipfile import ZipFile

import pytest

from aud import DELIVERY_PROFILES, AudioMetadata, Dir, MediaLimits, delivery_profile
from aud.core.ffmpeg import FFmpegEngine
from aud.core.packaging import _check_members

RELEASE = {"title": "Album", "artist": "Artist"}


def rows(directory):
    return {
        path.name: AudioMetadata(title=path.stem, track_number=index + 1, disc_number=1)
        for index, path in enumerate(sorted(directory.glob("*.wav")))
    }


@pytest.fixture(scope="module")
def delivery_art(tmp_path_factory):
    path = tmp_path_factory.mktemp("delivery-art") / "cover.jpg"
    engine = FFmpegEngine()
    engine.runner.run(
        [
            engine._tool("ffmpeg"),
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "color=c=blue:s=3000x3000",
            "-frames:v",
            "1",
            "-threads",
            "1",
            str(path),
        ]
    )
    return path


def test_generic_package_is_byte_exact_and_has_verifiable_manifest(populated_dir):
    cue = populated_dir / "album.cue"
    cue.write_text('FILE "bloop.wav" WAVE\n')
    originals = {path.name: path.read_bytes() for path in populated_dir.glob("*.wav")}
    d = Dir(populated_dir, extensions=["wav"])
    target = populated_dir / "album.zip"
    plan = d.plan_album(target, release=RELEASE, sidecars={"album.cue": cue})
    preview = d.preview(plan).to_dict()
    json.dumps(preview)
    assert not target.exists()
    result = d.execute(plan)
    assert result and d.get_all() == ["bloop.wav", "song.wav"]
    with ZipFile(target) as archive:
        assert archive.testzip() is None
        manifest_bytes = archive.read("manifest.json")
        manifest = json.loads(manifest_bytes)
        assert "AppData" not in manifest_bytes.decode()
        assert manifest["submission_status"] == "not_submitted"
        for item in manifest["files"]:
            assert hashlib.sha256(archive.read(item["path"])).hexdigest() == item["sha256"]
        for line in archive.read("checksums.sha256").decode().splitlines():
            digest, name = line.split("  ", 1)
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest
        assert archive.read("album.cue") == cue.read_bytes()
        for name, data in originals.items():
            assert archive.read(name) == data
            assert (populated_dir / name).read_bytes() == data
    assert not list(populated_dir.glob(".aud-*"))
    assert not list(populated_dir.glob("aud-package-*"))


@pytest.mark.parametrize(
    "service", [name for name in DELIVERY_PROFILES if name not in {"generic", "distrokid"}]
)
def test_service_packages_have_valid_audio_and_standalone_cover(
    populated_dir, delivery_art, service
):
    d = Dir(populated_dir, extensions=["wav"], pattern="bloop.*")
    original = (populated_dir / "bloop.wav").read_bytes()
    plan = d.plan_album(
        populated_dir / f"{service}.zip",
        service=service,
        release=RELEASE,
        artwork=delivery_art,
        metadata=rows(populated_dir),
    )
    assert d.execute(plan)
    format = delivery_profile(service).formats[0]
    with ZipFile(populated_dir / f"{service}.zip") as archive:
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["profile"]["name"] == service
        assert manifest["profile"]["checked_on"]
        assert manifest["files"][0]["encoding"]["encoder_version"]
        assert manifest["files"][0]["encoding"]["metadata_policy"] == "strip"
        assert archive.read("cover.jpg") == delivery_art.read_bytes()
        audio = populated_dir / f"verify.{format}"
        audio.write_bytes(archive.read(f"audio/0001.{format}"))
        info = FFmpegEngine().probe(audio)
        assert (info.sample_rate, info.bit_depth, info.channels) == (44100, 16, 2)
        assert not info.tags and not info.artwork
    assert (populated_dir / "bloop.wav").read_bytes() == original


def test_high_resolution_is_preserved_when_service_accepts_it(tmp_path, delivery_art):
    source = tmp_path / "master.wav"
    values = [-7000000, -1, 0, 1, 7000000] * 100
    with wave.open(str(source), "wb") as audio:
        audio.setnchannels(2)
        audio.setsampwidth(3)
        audio.setframerate(96000)
        audio.writeframes(
            b"".join((value & 0xFFFFFF).to_bytes(3, "little") * 2 for value in values)
        )
    d = Dir(tmp_path, extensions=["wav"])
    metadata = {"master.wav": AudioMetadata(title="Master", track_number=1, disc_number=1)}
    plan = d.plan_album(
        tmp_path / "amuse.zip",
        service="Amuse",
        release=RELEASE,
        artwork=delivery_art,
        metadata=metadata,
    )
    assert (plan.tracks[0].sample_rate, plan.tracks[0].bit_depth) == (96000, 24)
    assert d.execute(plan)
    with pytest.raises(ValueError, match="allow_audio_changes"):
        d.plan_album(
            tmp_path / "cd.zip",
            service="cdbaby",
            release=RELEASE,
            artwork=delivery_art,
            metadata=metadata,
        )
    lowered = d.plan_album(
        tmp_path / "cd.zip",
        service="cdbaby",
        release=RELEASE,
        artwork=delivery_art,
        metadata=metadata,
        allow_audio_changes=True,
    )
    assert lowered.tracks[0].dither
    assert d.execute(lowered)
    assert "triangular_dither" in lowered.tracks[0].changes
    with ZipFile(tmp_path / "cd.zip") as archive:
        output = tmp_path / "verify-cd.wav"
        output.write_bytes(archive.read("audio/0001.wav"))
        info = FFmpegEngine().probe(output)
        assert (info.sample_rate, info.bit_depth, info.channels) == (44100, 16, 2)


def test_explicit_order_supports_untagged_masters(populated_dir, delivery_art):
    d = Dir(populated_dir, extensions=["wav"])
    metadata = {name: AudioMetadata(title=name) for name in ("bloop.wav", "song.wav")}
    with pytest.raises(ValueError, match="track_order"):
        d.plan_album(
            populated_dir / "out.zip",
            service="amuse",
            release=RELEASE,
            artwork=delivery_art,
            metadata=metadata,
        )
    plan = d.plan_album(
        populated_dir / "out.zip",
        service="amuse",
        release=RELEASE,
        artwork=delivery_art,
        metadata=metadata,
        track_order=["song.wav", "bloop.wav"],
    )
    assert [track.source.name for track in plan.tracks] == ["song.wav", "bloop.wav"]


@pytest.mark.parametrize(
    "names",
    [
        ["../outside"],
        ["/root"],
        ["C:stream"],
        ["a\\b"],
        ["CON.txt"],
        ["a/./b"],
        ["manifest.json", "MANIFEST.JSON"],
        ["a", "a/b"],
        ["A/x", "a/y"],
    ],
)
def test_unsafe_or_colliding_members_rejected(names):
    with pytest.raises((ValueError, FileExistsError)):
        _check_members(names)


def test_changed_input_rejected_without_touching_existing_archive(populated_dir):
    d = Dir(populated_dir, extensions=["wav"], overwrite="overwrite")
    target = populated_dir / "out.zip"
    target.write_bytes(b"existing")
    plan = d.plan_album(target, release=RELEASE)
    (populated_dir / "bloop.wav").write_bytes(b"changed")
    result = d.execute(plan, continue_on_error=True)
    assert not result
    assert target.read_bytes() == b"existing"


def test_cancellation_removes_owned_work_and_preserves_source(populated_dir, monkeypatch):

    d = Dir(populated_dir, extensions=["wav"])
    plan = d.plan_album(populated_dir / "out.zip", release=RELEASE)
    assert not d.execute(plan, cancel=lambda: True)
    assert d.last_result.items[0].status == "cancelled"
    assert not (populated_dir / "out.zip").exists()
    assert not list(populated_dir.glob(".aud-*"))
    assert not list(populated_dir.glob("aud-package-*"))
    result = d.package_album(populated_dir / "out.zip", release=RELEASE, cancel=lambda: True)
    assert result.items[0].status == "cancelled"


def test_package_budget_failure_leaves_no_output(populated_dir):
    d = Dir(populated_dir, extensions=["wav"], media_limits=MediaLimits(output_bytes=1000))
    result = d.package_album(populated_dir / "out.zip", release=RELEASE, continue_on_error=True)
    assert not result
    assert not (populated_dir / "out.zip").exists()
    assert not list(populated_dir.glob(".aud-*"))


def test_distrokid_duration_limit_and_profile_labels(populated_dir, delivery_art):
    d = Dir(populated_dir, extensions=["wav"])
    with pytest.raises(ValueError, match="Average track duration"):
        d.plan_album(
            populated_dir / "out.zip",
            service="DistroKid",
            release=RELEASE,
            artwork=delivery_art,
            metadata=rows(populated_dir),
        )
    assert delivery_profile("CD Baby").name == "cdbaby"
    assert delivery_profile("RouteNote").formats == ("flac",)
    with pytest.raises(ValueError, match="Unknown delivery"):
        delivery_profile("invented")


def test_artwork_is_validated_before_package_writes(populated_dir):
    from test_ffmpeg_engine import _png

    cover = populated_dir / "bad.jpg"
    _png(cover)
    with pytest.raises(ValueError, match="Invalid JPEG"):
        Dir(populated_dir, extensions=["wav"]).plan_album(
            populated_dir / "out.zip",
            service="amuse",
            release=RELEASE,
            artwork=cover,
            metadata=rows(populated_dir),
        )
    assert not (populated_dir / "out.zip").exists()


def test_delivery_rejects_lossy_sources_without_opt_in(populated_dir, delivery_art):
    d = Dir(populated_dir, extensions=["wav"], pattern="bloop.*")
    d.convert_to_mp3()
    with pytest.raises(ValueError, match="lossless"):
        d.plan_album(
            populated_dir / "out.zip",
            service="amuse",
            release=RELEASE,
            artwork=delivery_art,
            metadata={"bloop.mp3": AudioMetadata(title="Title", track_number=1, disc_number=1)},
        )


def test_prepared_delivery_revalidates_settings(populated_dir, delivery_art):
    d = Dir(populated_dir, extensions=["wav"])
    plan = d.plan_album(
        populated_dir / "out.zip",
        service="amuse",
        release=RELEASE,
        artwork=delivery_art,
        metadata=rows(populated_dir),
    )
    changed = replace(plan, tracks=(replace(plan.tracks[0], sample_rate=123), *plan.tracks[1:]))
    with pytest.raises(ValueError, match="settings changed"):
        d.execute(changed)
    forged = replace(plan, profile=replace(plan.profile, max_tracks=9999))
    with pytest.raises(ValueError, match="registered revision"):
        d.preview(forged)
    plan.release["title"] = ""
    with pytest.raises(ValueError, match="title and artist"):
        d.preview(plan)
    assert not (populated_dir / "out.zip").exists()


def test_distrokid_package_at_minimum_average_duration(tmp_path, delivery_art):
    source = tmp_path / "minute.wav"
    with wave.open(str(source), "wb") as audio:
        audio.setnchannels(2)
        audio.setsampwidth(2)
        audio.setframerate(44100)
        for _ in range(60):
            audio.writeframes(b"\0" * (44100 * 4))
    d = Dir(tmp_path, extensions=["wav"])
    result = d.package_album(
        tmp_path / "distrokid.zip",
        service="DistroKid",
        release=RELEASE,
        artwork=delivery_art,
        metadata={"minute.wav": AudioMetadata(title="Minute", disc_number=1, track_number=1)},
    )
    assert result
    with ZipFile(tmp_path / "distrokid.zip") as archive:
        assert archive.testzip() is None
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["tracks"][0]["source_properties"]["duration"] == 60
