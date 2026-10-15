from aud.aud import Dir


def test_case_only_rename_on_case_insensitive_posix(tmp_path, monkeypatch):
    import os
    from types import SimpleNamespace

    from aud.core.adapters.filesystem import FileSystemAdapter
    from aud.core.models import AudioFile
    from aud.core.operations.names import Uppercase
    from aud.core.safety import Destination

    source = tmp_path / "a.txt"
    target = tmp_path / "A.txt"
    source.write_text("data")
    if not target.exists():
        os.link(source, target)
    renames = []

    def forbidden_link(*args):
        raise AssertionError("An existing same-file target cannot be hard-linked again")

    monkeypatch.setattr(
        "aud.core.adapters.filesystem.os",
        SimpleNamespace(
            name="posix",
            path=os.path,
            rename=lambda *args: renames.append(args),
            link=forbidden_link,
        ),
    )
    adapter = FileSystemAdapter()
    adapter.execute_resolved(
        Uppercase(), [AudioFile(source)], [Destination(source, target, replace=True)]
    )
    assert renames == [(source, target)]
    assert adapter.result.succeeded


def test_name_operations(populated_dir):
    d = Dir(populated_dir)
    d.config_set_extensions(["txt"])

    assert sorted(d.get_all()) == ["abc.txt", "test.txt"]

    d.name_upper()
    assert sorted(d.get_all()) == ["ABC.txt", "TEST.txt"]

    d.name_lower()
    assert sorted(d.get_all()) == ["abc.txt", "test.txt"]

    d.name_prepend("abc_")
    assert sorted(d.get_all()) == ["abc_abc.txt", "abc_test.txt"]

    d.name_append("_test")
    assert sorted(d.get_all()) == ["abc_abc_test.txt", "abc_test_test.txt"]

    d.name_replace("_", "-")
    assert sorted(d.get_all()) == ["abc-abc-test.txt", "abc-test-test.txt"]

    d.name_iterate(zerofill=4, separator="  ")
    assert sorted(d.get_all()) == [
        "0001  abc-abc-test.txt",
        "0002  abc-test-test.txt",
    ]

    d.name_replace_spaces("_")
    assert sorted(d.get_all()) == [
        "0001__abc-abc-test.txt",
        "0002__abc-test-test.txt",
    ]
