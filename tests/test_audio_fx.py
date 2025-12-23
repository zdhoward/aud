from aud.aud import Dir


def test_basic_audio_fx(populated_dir):
    d = Dir(populated_dir)
    d.config_set_extensions(["wav"])

    assert d.afx_fade(1, 1)
    assert d.afx_pad(1, 1)
    assert d.afx_gain(3)
    assert d.afx_gain(-3)
    assert d.afx_normalize(passes=2)
    assert d.afx_low_pass(12000)
    assert d.afx_high_pass(80)
    assert d.afx_invert_phase("both")
