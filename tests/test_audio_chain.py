import json
import struct
import wave

import pytest

from aud import AudioChain, AudioMetadata, Dir
from aud.core.ffmpeg import FFmpegEngine, ProcessRunner
from aud.core.operations.audio.convert import ConvertFormat
from aud.core.operations.audio.effects import (
    Fade,
    Gain,
    HighPassFilter,
    InvertPhase,
    LowPassFilter,
    Normalize,
    Pad,
)
from aud.core.operations.names import Uppercase


def test_chain_has_one_final_encode_and_serializable_preview(populated_dir, monkeypatch):
    calls = []
    original = ProcessRunner.run

    def record(self, arguments, output=None):
        if output is not None:
            calls.append(arguments)
        return original(self, arguments, output)

    monkeypatch.setattr(ProcessRunner, "run", record)
    d = Dir(populated_dir, extensions=["wav"], pattern="bloop.*")
    chain = AudioChain(
        [Gain(-3), Pad(0.05, 0.1), Fade(0.02, 0.03)],
        output=ConvertFormat(
            "flac",
            tags={"track": "2/9", "albumartist": "Artist"},
            output_directory=populated_dir / "out",
        ),
    )
    plan = d.plan().add(chain)
    preview = d.preview(plan).to_dict()
    assert d.preview(plan).to_dict() == preview
    json.dumps(preview)
    result = d.execute(plan)
    json.dumps(result.to_dict())
    assert len(calls) == 1
    assert calls[0].count("-af") == 1
    assert result.items[0].target == preview["steps"][0]["targets"][0]
    details = result.items[0].details
    assert details["effects"] == ["Gain", "Pad", "Fade"]
    assert details["output_metadata"]["track_number"] == 2
    assert details["output_metadata"]["album_artist"] == "Artist"
    assert FFmpegEngine().probe(populated_dir / "out/bloop.flac").duration == pytest.approx(
        0.4, abs=0.001
    )


@pytest.mark.parametrize(
    "effect", [LowPassFilter(1000), HighPassFilter(100), InvertPhase("left"), InvertPhase("right")]
)
def test_native_filters_preserve_sample_properties(populated_dir, effect):
    d = Dir(populated_dir, extensions=["wav"], pattern="bloop.*")
    assert d.afx_chain([effect])
    info = FFmpegEngine().probe(populated_dir / "bloop.wav")
    assert (info.sample_rate, info.channels, info.bit_depth) == (44100, 2, 16)


def test_24bit_phase_chain_preserves_sample_precision(tmp_path):
    source = tmp_path / "pcm.wav"
    values = [-7000000, -1, 0, 1, 7000000] * 100
    samples = b"".join((value & 0xFFFFFF).to_bytes(3, "little") for value in values)
    with wave.open(str(source), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(3)
        audio.setframerate(44100)
        audio.writeframes(samples)
    d = Dir(tmp_path, extensions=["wav"])
    d.afx_chain([InvertPhase(), InvertPhase()], output=ConvertFormat("raw"))
    assert (tmp_path / "pcm.raw").read_bytes() == samples


@pytest.mark.parametrize("channel,expected", [("left", (-1000, 2000)), ("right", (1000, -2000))])
def test_phase_selects_the_requested_channel(tmp_path, channel, expected):
    source = tmp_path / "stereo.wav"
    with wave.open(str(source), "wb") as audio:
        audio.setnchannels(2)
        audio.setsampwidth(2)
        audio.setframerate(44100)
        audio.writeframes(struct.pack("<hh", 1000, 2000) * 256)
    Dir(tmp_path, extensions=["wav"]).afx_chain([InvertPhase(channel)], output=ConvertFormat("raw"))
    assert (tmp_path / "stereo.raw").read_bytes() == struct.pack("<hh", *expected) * 256


def test_lossy_fade_out_uses_decoded_duration(populated_dir):
    import math

    d = Dir(populated_dir, extensions=["wav"], pattern="bloop.*")
    d.convert_to_mp3(bit_rate=320)
    engine = FFmpegEngine()
    assert engine._decoded_duration(populated_dir / "bloop.mp3") == pytest.approx(0.25, abs=0.001)
    d.afx_chain([Fade(fade_out=0.1)], output=ConvertFormat("raw"))
    data = (populated_dir / "bloop.raw").read_bytes()
    samples = struct.unpack(f"<{len(data) // 2}h", data)[::2]

    def rms(values):
        return math.sqrt(sum(value * value for value in values) / len(values))

    assert rms(samples[-220:]) < rms(samples[4400:4620]) * 0.1


def test_chain_failure_does_not_publish_or_run_dependent_names(populated_dir, monkeypatch):
    original = (populated_dir / "bloop.wav").read_bytes()

    def fail(self, source, operation, destination, **kwargs):
        raise OSError("encoder failed")

    monkeypatch.setattr(FFmpegEngine, "convert", fail)
    d = Dir(populated_dir, extensions=["wav"], pattern="bloop.*")
    result = d.execute(
        d.plan().add(AudioChain([Gain(-3)])).add(Uppercase()), continue_on_error=True
    )
    assert [item.status for item in result.items] == ["failed", "not_run"]
    assert d.get_all() == ["bloop.wav"]
    assert (populated_dir / "bloop.wav").read_bytes() == original


@pytest.mark.parametrize(
    "effects",
    [
        [],
        [Normalize()],
        [Gain(float("nan"))],
        [Pad(-1)],
        [Fade(float("inf"))],
        [InvertPhase("unknown")],
    ],
)
def test_invalid_chains_are_rejected(effects):
    with pytest.raises((ValueError, TypeError)):
        AudioChain(effects)


def test_mutated_chain_rejected_before_prior_writes(populated_dir):
    chain = AudioChain([Gain(-3)])
    chain.effects[0].amount_db = float("nan")
    original = (populated_dir / "bloop.wav").read_bytes()
    d = Dir(populated_dir, extensions=["wav"])
    with pytest.raises(ValueError):
        d.execute(d.plan().add(Gain(-1)).add(chain))
    assert (populated_dir / "bloop.wav").read_bytes() == original


@pytest.mark.parametrize(
    "effect,field",
    [
        (Gain(-3), "amount_db"),
        (Fade(0.1, 0.1), "fade_out"),
        (Pad(0.1, 0.1), "pad_in"),
        (LowPassFilter(1000), "cutoff_hz"),
        (InvertPhase(), "channel"),
    ],
)
def test_missing_effect_field_fails_before_prior_copy(populated_dir, effect, field):
    from aud.core.operations.files import Copy

    chain = AudioChain([effect])
    delattr(effect, field)
    output = populated_dir / "out"
    d = Dir(populated_dir, extensions=["wav"])
    with pytest.raises(ValueError):
        d.execute(d.plan().add(Copy(output)).add(chain))
    assert not output.exists()


def test_chain_cancellation_cleans_stage_and_retains_all_inputs(populated_dir, monkeypatch):
    from aud.core.results import OperationCancelled

    original = (populated_dir / "bloop.wav").read_bytes()
    run = ProcessRunner.run

    def cancel_encode(self, arguments, output=None):
        if output is not None:
            output.write_bytes(b"partial")
            raise OperationCancelled("cancelled")
        return run(self, arguments, output)

    monkeypatch.setattr(ProcessRunner, "run", cancel_encode)
    d = Dir(populated_dir, extensions=["wav"])
    result = d.execute(d.plan().add(AudioChain([Gain(-3)])))
    assert [item.status for item in result.items] == ["cancelled", "cancelled"]
    assert d.get_all() == ["bloop.wav", "song.wav"]
    assert (populated_dir / "bloop.wav").read_bytes() == original
    assert not list(populated_dir.glob(".aud-*"))


def test_chain_keeps_artwork_and_tags(populated_dir):
    from test_ffmpeg_engine import _png

    cover = populated_dir / "cover.png"
    _png(cover)
    d = Dir(populated_dir, extensions=["wav"], pattern="bloop.*")
    d.convert_format("flac", cover=str(cover), tags={"artist": "Artist"})
    d.afx_chain([Gain(-3), Fade(0.01, 0.01)])
    info = FFmpegEngine().probe(populated_dir / "bloop.flac")
    assert info.tags["artist"] == "Artist"
    assert len(info.artwork) == 1


@pytest.mark.parametrize("effect", [Fade(fade_out=10), LowPassFilter(30000)])
def test_source_dependent_chain_validation_preserves_file(populated_dir, effect):
    original = (populated_dir / "bloop.wav").read_bytes()
    d = Dir(populated_dir, extensions=["wav"], pattern="bloop.*")
    result = d.execute(d.plan().add(AudioChain([Gain(-3), effect])), continue_on_error=True)
    assert not result
    assert (populated_dir / "bloop.wav").read_bytes() == original
    assert not list(populated_dir.glob(".aud-*"))


def test_metadata_keeps_original_tags_and_canonical_positions():
    tags = {
        "ARTIST": "é",
        "albumartist": "Album artist",
        "tracknumber": "03/12",
        "disc": "1/2",
        "date": "2026-10-14",
        "year": "2026",
        "custom": "untouched",
    }
    metadata = AudioMetadata.from_tags(tags)
    assert (
        metadata.track_number,
        metadata.track_total,
        metadata.disc_number,
        metadata.disc_total,
    ) == (3, 12, 1, 2)
    assert metadata.album_artist == "Album artist"
    assert metadata.year == 2026
    assert not metadata.issues
    assert metadata.tags == tags
    json.dumps(metadata.to_dict())


@pytest.mark.parametrize(
    "tags",
    [
        {"track": "3/2"},
        {"track": "1/9", "tracktotal": "10"},
        {"disc": "-1"},
        {"track": "9" * 10000},
        {"date": "2026-02-30"},
        {"albumartist": "A", "album_artist": "B"},
    ],
)
def test_metadata_issues_do_not_rewrite_tags(tags):
    metadata = AudioMetadata.from_tags(tags)
    assert metadata.issues
    assert metadata.tags == tags
