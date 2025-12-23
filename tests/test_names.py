from aud.aud import Dir


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
