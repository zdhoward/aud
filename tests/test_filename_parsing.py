import json
from pathlib import Path
from zipfile import ZipFile

import pytest

from aud import Dir, FilenamePattern, NamingProfile, cli
from aud.core.ffmpeg import FFmpegEngine

CORPUS = json.loads(
    (Path(__file__).parents[1] / "conformance/v1/filename.json").read_text(encoding="utf-8")
)


@pytest.mark.parametrize("case", CORPUS["valid"])
def test_filename_conformance(case):
    metadata = FilenamePattern(case["template"]).parse(case["filename"])
    assert {name: getattr(metadata, name) for name in case["fields"]} == case["fields"]
    assert not metadata.tags and not metadata.issues


@pytest.mark.parametrize("case", CORPUS["invalid"])
def test_filename_mismatch_conformance(case):
    with pytest.raises(ValueError):
        FilenamePattern(case["template"]).parse(case["filename"])


@pytest.mark.parametrize(
    "template",
    [
        "",
        "literal",
        "{unknown}",
        "{title}{artist}",
        "{title}-{title}",
        "{title!r}",
        "{title:02}",
        "{track_number:100}",
        "{title.__class__}",
        "{title[0]}",
        "../{title}",
        "{title}\n",
        "{title:{artist}}",
        "{",
    ],
)
def test_invalid_pattern_grammar(template):
    with pytest.raises(ValueError):
        FilenamePattern(template)


def test_pattern_limits_and_input_types():
    with pytest.raises(ValueError):
        FilenamePattern("x" * 2049)
    pattern = FilenamePattern("{title}")
    with pytest.raises(ValueError):
        pattern.parse("x" * 4097 + ".wav")
    with pytest.raises(TypeError):
        pattern.parse(123)
    assert pattern.parse(Path("Title.wav")).title == "Title"


def test_selection_parsing_is_pure_and_feeds_naming(tmp_path, monkeypatch):
    original = tmp_path / "01 - Café.flac"
    original.write_bytes(b"owned opaque copy fixture")
    monkeypatch.setattr(FFmpegEngine, "probe", lambda *args: pytest.fail("Unexpected probe"))
    d = Dir(tmp_path, extensions=["flac"])
    metadata = d.parse_filenames(FilenamePattern())
    assert metadata[original].title == "Café"
    target = tmp_path / "out"
    plan = d.plan_naming(
        NamingProfile(directory="", filename="{title}"), target, metadata=metadata, copy=True
    )
    assert not target.exists()
    assert d.execute(plan)
    assert (target / "Café.flac").read_bytes() == original.read_bytes()


def test_parse_all_rejects_mismatch_without_changes(tmp_path):
    for name in ("01 - Good.wav", "unmatched.wav"):
        (tmp_path / name).write_bytes(b"original")
    d = Dir(tmp_path, extensions=["wav"])
    before = d.get_all()
    with pytest.raises(ValueError, match="unmatched.wav"):
        d.parse_filenames(FilenamePattern())
    assert d.get_all() == before
    assert all(path.read_bytes() == b"original" for path in tmp_path.glob("*.wav"))


def test_cli_rename_pattern_preview_copy_and_conflict(tmp_path, capsys):
    source = tmp_path / "01 - First.flac"
    source.write_bytes(b"owned opaque copy fixture")
    config = tmp_path / "naming.json"
    payload = {
        "profile": {"directory": "", "filename": "{title}"},
        "filename_pattern": "{track_number:02} - {title}",
    }
    config.write_text(json.dumps(payload))
    args = [
        "rename",
        str(tmp_path),
        "--extensions",
        "flac",
        "--config",
        str(config),
        "--output-directory",
        str(tmp_path / "out"),
        "--copy",
        "--json",
    ]
    assert cli.run(args + ["--dry-run"]) == 0
    assert json.loads(capsys.readouterr().out)["dry_run"]
    assert not (tmp_path / "out").exists()
    assert cli.run(args) == 0
    assert json.loads(capsys.readouterr().out)["succeeded"]
    assert (tmp_path / "out/First.flac").read_bytes() == source.read_bytes()
    payload["metadata"] = {}
    config.write_text(json.dumps(payload))
    assert cli.run(args + ["--dry-run"]) == 2
    assert "implicit merging" in json.loads(capsys.readouterr().out)["error"]


def test_cli_album_pattern_supplies_manifest_metadata(populated_dir, capsys):
    source = populated_dir / "bloop.wav"
    source.rename(populated_dir / "01 - First.wav")
    config = populated_dir / "album.json"
    config.write_text(
        json.dumps(
            {
                "release": {"title": "Album", "artist": "Artist"},
                "filename_pattern": "{track_number:02} - {title}",
            }
        )
    )
    target = populated_dir / "album.zip"
    assert (
        cli.run(
            [
                "album",
                str(populated_dir),
                "--extensions",
                "wav",
                "--pattern",
                "01*",
                "--config",
                str(config),
                "--target",
                str(target),
                "--json",
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["succeeded"]
    with ZipFile(target) as archive:
        metadata = json.loads(archive.read("manifest.json"))["tracks"][0]["metadata"]
        assert metadata["title"] == "First" and metadata["track_number"] == 1
