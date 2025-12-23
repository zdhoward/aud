from aud.aud import Dir


def test_config_set_get_extensions(populated_dir):
    d = Dir(populated_dir)
    d.config_set_extensions(["txt"])
    assert d.config_get_extensions() == ["txt"]
    assert sorted(d.get_all()) == ["abc.txt", "test.txt"]


def test_config_allowlist_regex(populated_dir):
    d = Dir(populated_dir)
    d.config_set_extensions(["txt"])
    d.config_set_allowlist(regex="test")
    assert sorted(d.get_all()) == ["abc.txt", "test.txt"]


def test_config_denylist_regex(populated_dir):
    d = Dir(populated_dir)
    d.config_set_extensions(["txt"])
    d.config_set_denylist(regex="test")
    assert d.get_all() == ["abc.txt"]
