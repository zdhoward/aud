from aud.aud import Dir


def test_conversion_basic(populated_dir):
    d = Dir(populated_dir)
    d.config_set_extensions(["wav"])

    assert d.convert_format("mp3")
    d.config_set_extensions(["mp3"])
    assert len(d.get_all()) == 2

    assert d.convert_mono()
    assert d.convert_stereo()
