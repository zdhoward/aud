import zipfile

from aud.aud import Dir


def test_filesystem_ops(populated_dir):
    d = Dir(populated_dir)
    d.config_set_extensions(["wav"])

    backup = populated_dir / "backup"
    copy = populated_dir / "copy"
    move = populated_dir / "move"

    d.backup(backup)
    assert sorted(p.name for p in backup.iterdir()) == ["bloop.wav", "song.wav"]

    d.copy(copy)
    assert sorted(p.name for p in copy.iterdir()) == ["bloop.wav", "song.wav"]

    d.move(move)
    assert sorted(p.name for p in move.iterdir()) == ["bloop.wav", "song.wav"]

    # move back
    d.move(populated_dir)
    assert sorted(d.get_all()) == ["bloop.wav", "song.wav"]

    zip_path = populated_dir / "test.zip"
    d.archive_zip(zip_path)

    with zipfile.ZipFile(zip_path) as z:
        assert sorted(z.namelist()) == ["bloop.wav", "song.wav"]
