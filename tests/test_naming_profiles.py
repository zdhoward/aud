import json
from dataclasses import replace
from pathlib import Path

import pytest

from aud import AudioMetadata, Dir, NamingProfile
from aud.core.ffmpeg import FFmpegEngine
from aud.core.operations.files import Copy
from aud.core.operations.naming import NameWithProfile
from aud.exceptions import FilenameError


def metadata(**changes):
    return replace(
        AudioMetadata(
            album_artist="Été",
            album="Album",
            year=2026,
            disc_number=1,
            track_number=1,
            title="Title",
        ),
        **changes,
    )


def test_multidisc_profile_copy_preview_and_bytes(tmp_path, monkeypatch):
    rows = {}
    for index in (1, 2):
        path = tmp_path / f"disc{index}.flac"
        path.write_bytes(f"audio{index}".encode())
        rows[path.name] = metadata(disc_number=index, title="Café / Song")
    d = Dir(tmp_path, extensions=["flac"])
    profile = NamingProfile(directory="{album_artist} - {album} ({year})/Disc {disc_number:02}")
    plan = d.plan_naming(profile, tmp_path / "out", metadata=rows, copy=True)
    # Supplied metadata needs no codec process; repeated previews are read-only.
    monkeypatch.setattr(FFmpegEngine, "probe", lambda *args: pytest.fail("Unexpected probe"))
    preview = d.preview(plan).to_dict()
    assert d.preview(plan).to_dict() == preview
    json.dumps(preview)
    assert not (tmp_path / "out").exists()
    result = d.execute(plan)
    assert result.succeeded
    assert [item.target for item in result.items] == preview["steps"][0]["targets"]
    for index in (1, 2):
        target = tmp_path / f"out/Été - Album (2026)/Disc {index:02}/01 - Café _ Song.flac"
        assert target.read_bytes() == f"audio{index}".encode()
        assert (tmp_path / f"disc{index}.flac").exists()


def test_profile_move_and_selection(tmp_path):
    (tmp_path / "old.wav").write_bytes(b"audio")
    d = Dir(tmp_path, extensions=["wav"])
    assert d.name_profile(
        NamingProfile(directory="", filename="{title}"),
        tmp_path / "out",
        metadata={"old.wav": metadata()},
    )
    assert not (tmp_path / "old.wav").exists()
    assert [file.path for file in d] == [tmp_path / "out/Title.wav"]


@pytest.mark.parametrize(
    "title,expected",
    [
        ("CON", "_CON"),
        ("LPT¹.txt", "_LPT¹.txt"),
        ("a:b?c*", "a_b_c_"),
        ("x\u202ey", "x_y"),
        ("../escape", "_escape"),
        ("e\u0301", "é"),
    ],
)
def test_portable_component_rules(title, expected):
    profile = NamingProfile(directory="", filename="{title}")
    assert profile.render(metadata(title=title), "flac").name == expected + ".flac"


def test_explicit_context_ascii_case_spacing_and_affixes():
    profile = NamingProfile(
        directory="{album} [{encoding_profile}]",
        filename="{track_number:02d}-{title}",
        case="upper",
        ascii_only=True,
        space_replacement="_",
        prefix="[",
        suffix="]",
        defaults={"encoding_profile": "mp3-v0"},
    )
    assert profile.render(metadata(title="Café Song"), "mp3") == Path(
        "ALBUM_[MP3-V0]/[01-CAFE_SONG].mp3"
    )
    assert metadata(title="Café Song").title == "Café Song"


@pytest.mark.parametrize(
    "options",
    [
        {"directory": "../{album}"},
        {"directory": "/{album}"},
        {"directory": "C:/{album}"},
        {"directory": "//host/share"},
        {"filename": "a/b"},
        {"filename": "{title.__class__}"},
        {"filename": "{title[0]}"},
        {"filename": "{title!r}"},
        {"filename": "{track_number:099999d}"},
        {"filename": "{title:02}"},
        {"filename": "{unknown}"},
        {"missing": "guess"},
        {"space_replacement": "/"},
    ],
)
def test_invalid_templates_rejected(options):
    with pytest.raises(ValueError):
        NamingProfile(**options)


def test_missing_fields_fail_before_prior_copy(tmp_path):
    source = tmp_path / "a.wav"
    source.write_bytes(b"audio")
    d = Dir(tmp_path, extensions=["wav"])
    operation = NameWithProfile(
        NamingProfile(), tmp_path / "out", {tmp_path / "backup/a.wav": metadata(year=None)}
    )
    with pytest.raises(ValueError, match="year"):
        d.execute(d.plan().add(Copy(tmp_path / "backup")).add(operation))
    assert not (tmp_path / "backup").exists()
    assert not (tmp_path / "out").exists()


def test_skip_missing_retains_inputs_and_records_skip(tmp_path):
    source = tmp_path / "a.wav"
    source.write_bytes(b"audio")
    d = Dir(tmp_path, extensions=["wav"])
    plan = d.plan_naming(NamingProfile(missing="skip"), tmp_path / "out", metadata={})
    assert d.preview(plan).steps[0].statuses == ["skipped"]
    assert d.execute(plan).items[0].status == "skipped"
    assert d.get_all() == ["a.wav"]
    assert source.read_bytes() == b"audio"


def test_explicit_defaults_fill_missing_fields():
    profile = NamingProfile(defaults={"album_artist": "Various Artists", "year": 2020})
    result = profile.render(metadata(album_artist=None, year=None), "flac")
    assert result.parent.name == "Various Artists - Album (2020)"


@pytest.mark.parametrize("policy", ["error", "skip", "overwrite", "auto-rename"])
def test_sanitized_collisions_use_existing_policy(tmp_path, policy):
    for name in ("a.wav", "b.wav"):
        (tmp_path / name).write_bytes(name.encode())
    d = Dir(tmp_path, extensions=["wav"], overwrite=policy)
    rows = {"a.wav": metadata(title="A/B"), "b.wav": metadata(title="A:B")}
    plan = d.plan_naming(
        NamingProfile(directory="", filename="{title}"), tmp_path / "out", metadata=rows
    )
    if policy in {"error", "overwrite"}:
        with pytest.raises(FileExistsError):
            d.execute(plan)
        assert not (tmp_path / "out").exists()
    else:
        result = d.execute(plan)
        assert result.succeeded
        assert [item.status for item in result.items] == [
            "success",
            "skipped" if policy == "skip" else "success",
        ]
        assert (tmp_path / "out/A_B.wav").read_bytes() == b"a.wav"
        if policy == "auto-rename":
            assert (tmp_path / "out/A_B (1).wav").read_bytes() == b"b.wav"


def test_directory_case_collisions_fail_before_writes(tmp_path):
    for name in ("a.wav", "b.wav"):
        (tmp_path / name).write_bytes(b"audio")
    d = Dir(tmp_path, extensions=["wav"])
    plan = d.plan_naming(
        NamingProfile(directory="{album}", filename="{title}"),
        tmp_path / "out",
        metadata={
            "a.wav": metadata(album="ALBUM", title="A"),
            "b.wav": metadata(album="album", title="B"),
        },
    )
    with pytest.raises(FileExistsError, match="directories collide"):
        d.preview(plan)
    assert not (tmp_path / "out").exists()


def test_metadata_issues_and_empty_ascii_are_not_guessed():
    with pytest.raises(ValueError, match="metadata issues"):
        NamingProfile().render(metadata(issues=("Conflicting track totals",)), "wav")
    with pytest.raises(ValueError, match="empty"):
        NamingProfile(filename="{title}", directory="", ascii_only=True).render(
            metadata(title="東京"), "wav"
        )


def test_probed_metadata_is_snapshotted_without_writes(populated_dir):
    d = Dir(populated_dir, extensions=["wav"], pattern="bloop.*")
    d.convert_format(
        "flac",
        tags={
            "artist": "Artist",
            "album_artist": "Artist",
            "album": "Album",
            "date": "2026",
            "track": "1",
            "title": "Song",
        },
    )
    source = populated_dir / "bloop.flac"
    original = source.read_bytes()
    plan = d.plan_naming(NamingProfile(), populated_dir / "out", copy=True)
    assert source.read_bytes() == original
    assert not (populated_dir / "out").exists()
    assert d.execute(plan).succeeded
    assert (populated_dir / "out/Artist - Album (2026)/01 - Song.flac").read_bytes() == original


def test_partial_skip_preserves_selection_slots(tmp_path):
    for name in ("a.wav", "b.wav"):
        (tmp_path / name).write_bytes(name.encode())
    d = Dir(tmp_path, extensions=["wav"])
    plan = d.plan_naming(
        NamingProfile(missing="skip"),
        tmp_path / "out",
        metadata={"a.wav": metadata(year=None), "b.wav": metadata()},
    )
    result = d.execute(plan)
    assert [item.status for item in result.items] == ["skipped", "success"]
    assert [file.path for file in d] == [
        tmp_path / "a.wav",
        tmp_path / "out/Été - Album (2026)/01 - Title.wav",
    ]


def test_existing_directory_case_alias_is_rejected(tmp_path):
    (tmp_path / "a.wav").write_bytes(b"audio")
    (tmp_path / "out/ALBUM").mkdir(parents=True)
    d = Dir(tmp_path, extensions=["wav"])
    plan = d.plan_naming(
        NamingProfile(directory="{album}"),
        tmp_path / "out",
        metadata={"a.wav": metadata(album="album")},
    )
    with pytest.raises(FileExistsError, match="aliases"):
        d.execute(plan)
    assert (tmp_path / "a.wav").read_bytes() == b"audio"
    assert not list((tmp_path / "out/ALBUM").iterdir())


def test_profile_move_failure_preserves_original_and_cleans_staging(tmp_path, monkeypatch):
    import shutil

    source = tmp_path / "a.wav"
    source.write_bytes(b"audio")

    def fail(source, target):
        Path(target).write_bytes(b"partial")
        raise OSError("copy failed")

    monkeypatch.setattr(shutil, "copy2", fail)
    d = Dir(tmp_path, extensions=["wav"])
    result = d.execute(
        d.plan_naming(
            NamingProfile(directory=""), tmp_path / "out", metadata={"a.wav": metadata()}
        ),
        continue_on_error=True,
    )
    assert result.items[0].status == "failed"
    assert source.read_bytes() == b"audio"
    assert not list((tmp_path / "out").iterdir())
    assert d.get_all() == ["a.wav"]


def test_profile_cancellation_keeps_unprocessed_input(tmp_path, monkeypatch):
    import shutil
    from threading import Event

    event = Event()
    original = shutil.copy2
    for name in ("a.wav", "b.wav"):
        (tmp_path / name).write_bytes(name.encode())

    def copy_then_cancel(source, target):
        result = original(source, target)
        event.set()
        return result

    monkeypatch.setattr(shutil, "copy2", copy_then_cancel)
    d = Dir(tmp_path, extensions=["wav"])
    rows = {"a.wav": metadata(title="A"), "b.wav": metadata(title="B")}
    plan = d.plan_naming(
        NamingProfile(directory="", filename="{title}"), tmp_path / "out", metadata=rows
    )
    result = d.execute(plan, cancel=event.is_set)
    assert [item.status for item in result.items] == ["success", "cancelled"]
    assert [file.path for file in d] == [tmp_path / "out/A.wav", tmp_path / "b.wav"]
    assert (tmp_path / "b.wav").read_bytes() == b"b.wav"


@pytest.mark.parametrize("title", ["é" * 128, "x" * 252])
def test_portable_length_rejects_instead_of_truncating(title):
    with pytest.raises(ValueError, match="length"):
        NamingProfile(filename="{title}", directory="").render(metadata(title=title), "wav")


def test_file_directory_prefix_conflict_rejected(tmp_path):
    from aud.core.naming import validate_naming_tree

    root = tmp_path / "out"
    with pytest.raises(FileExistsError, match="both a file and directory"):
        validate_naming_tree(root, [root / "album.wav", root / "album.wav/track.wav"])


def test_profile_cannot_write_through_directory_link(tmp_path):
    (tmp_path / "a.wav").write_bytes(b"audio")
    (tmp_path / "out").mkdir()
    (tmp_path / "elsewhere").mkdir()
    try:
        (tmp_path / "out/Album").symlink_to(tmp_path / "elsewhere", target_is_directory=True)
    except OSError:
        pytest.skip("Directory symlinks unavailable")
    d = Dir(tmp_path, extensions=["wav"])
    with pytest.raises(ValueError, match="Link/reparse"):
        d.execute(
            d.plan_naming(
                NamingProfile(directory="{album}"), tmp_path / "out", metadata={"a.wav": metadata()}
            )
        )
    assert not list((tmp_path / "elsewhere").iterdir())


@pytest.mark.parametrize(
    "original_name,output_name", [("Album", "album"), ("Été", "E\u0301te\u0301")]
)
def test_case_variant_output_root_cannot_produce_false_success(
    tmp_path, original_name, output_name
):
    (tmp_path / original_name).mkdir()
    source = tmp_path / original_name / "song.wav"
    source.write_bytes(b"audio")
    output = tmp_path / output_name
    if output.exists():
        pytest.skip("Filesystem aliases directory case; target already resolves to source")
    d = Dir(source.parent, extensions=["wav"])
    plan = d.plan_naming(
        NamingProfile(directory="", filename="{title}"),
        output,
        metadata={"song.wav": metadata(title="song")},
    )
    with pytest.raises(FileExistsError):
        d.execute(plan)
    assert source.read_bytes() == b"audio"
    assert [file.path for file in d] == [source]
    assert not output.exists()


@pytest.mark.parametrize(
    "original_name,output_name", [("Album", "album"), ("Été", "E\u0301te\u0301")]
)
def test_distinct_case_variant_directories_are_not_in_place(tmp_path, original_name, output_name):
    (tmp_path / original_name).mkdir()
    output = tmp_path / output_name
    if output.exists():
        pytest.skip("Filesystem aliases directory case")
    output.mkdir()
    source = tmp_path / original_name / "song.wav"
    source.write_bytes(b"audio")
    d = Dir(source.parent, extensions=["wav"])
    plan = d.plan_naming(
        NamingProfile(directory="", filename="{title}"),
        output,
        metadata={"song.wav": metadata(title="song")},
    )
    with pytest.raises(FileExistsError):
        d.execute(plan)
    assert source.read_bytes() == b"audio"
    assert not list(output.iterdir())


def test_missing_metadata_convenience_error_is_typed(tmp_path):
    (tmp_path / "a.wav").write_bytes(b"audio")
    with pytest.raises(FilenameError):
        Dir(tmp_path, extensions=["wav"]).name_profile(
            NamingProfile(), tmp_path / "out", metadata={}
        )
