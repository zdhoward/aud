from pathlib import Path

from aud.core.models import AudioFile
from aud.core.operations.files import Copy
from aud.core.operations.names import Iterate, Uppercase
from aud.core.plan import Plan


def _plan_files(populated_dir: Path) -> list[AudioFile]:
    return [
        AudioFile(populated_dir / "bloop.wav"),
        AudioFile(populated_dir / "song.wav"),
    ]


def test_preview_renames_without_touching_disk(populated_dir):
    plan = Plan(_plan_files(populated_dir)).add(Uppercase())

    preview = plan.preview()

    assert [(src.path.name, dst.path.name) for src, dst in preview] == [
        ("bloop.wav", "BLOOP.wav"),
        ("song.wav", "SONG.wav"),
    ]
    assert (populated_dir / "bloop.wav").exists()
    assert "BLOOP.wav" not in [p.name for p in populated_dir.iterdir()]


def test_preview_is_repeatable_for_stateful_operations(populated_dir):
    plan = Plan(_plan_files(populated_dir)).add(Iterate(zerofill=2))

    first = [dst.path.name for _, dst in plan.preview()]
    second = [dst.path.name for _, dst in plan.preview()]

    assert first == ["01_bloop.wav", "02_song.wav"]
    assert second == first


def test_preview_does_not_consume_operations(populated_dir):
    plan = Plan(_plan_files(populated_dir)).add(Iterate())

    plan.preview()

    renamed = plan.operations[0].apply(AudioFile(populated_dir / "bloop.wav"))
    assert renamed.path.name.startswith("1_")


def test_preview_of_copy_requires_no_target_directory(populated_dir, tmp_path):
    target = tmp_path / "new_directory"
    plan = Plan(_plan_files(populated_dir)).add(Copy(target))

    preview = plan.preview()

    assert all(dst.path.parent == target for _, dst in preview)
    assert not target.exists()
