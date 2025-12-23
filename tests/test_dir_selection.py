from aud.aud import Dir


def test_extension_filtering(populated_dir):
    d = Dir(populated_dir, extensions=["wav"])
    assert sorted(d.get_all()) == ["bloop.wav", "song.wav"]


def test_extensions_empty_matches_nothing(populated_dir):
    d = Dir(populated_dir)
    assert d.get_all() == []


def test_allowlist_overrides_extensions(populated_dir):
    d = Dir(
        populated_dir,
        extensions=["wav"],
        allowlist=["test.txt"],
    )
    assert sorted(d.get_all()) == ["bloop.wav", "song.wav", "test.txt"]


def test_denylist_excludes(populated_dir):
    d = Dir(
        populated_dir,
        extensions=["txt"],
        denylist=["test.txt"],
    )
    assert d.get_all() == ["abc.txt"]


def test_allowlist_overrides_denylist(populated_dir):
    d = Dir(
        populated_dir,
        extensions=["txt"],
        denylist=["test.txt"],
        allowlist=["test.txt"],
    )
    assert sorted(d.get_all()) == ["abc.txt", "test.txt"]
