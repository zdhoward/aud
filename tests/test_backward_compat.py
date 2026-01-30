"""Tests for backward compatibility with v1 API."""

from aud.aud import Dir


def test_get_single(populated_dir):
    """Test get_single method returns a single file by index."""
    d = Dir(populated_dir, extensions=["wav"])

    all_files = d.get_all()
    assert len(all_files) == 2

    # Test getting by index
    assert d.get_single(0) in all_files
    assert d.get_single(1) in all_files


def test_log_method(populated_dir, tmp_path):
    """Test log method writes to log file."""
    logfile = tmp_path / "test.log"

    d = Dir(populated_dir)
    d.config_set_log_file(str(logfile))

    # Write some log messages
    assert d.log("Test message 1")
    assert d.log("Test message 2")

    # Check log file exists and has content
    assert logfile.exists()
    content = logfile.read_text()
    assert "Test message 1" in content
    assert "Test message 2" in content


def test_config_get_allowlist(populated_dir):
    """Test config_get_allowlist returns the allowlist."""
    d = Dir(populated_dir)
    d.config_set_allowlist(names=["test.txt", "abc.txt"])

    allowlist = d.config_get_allowlist()
    assert "test.txt" in allowlist
    assert "abc.txt" in allowlist


def test_config_get_denylist(populated_dir):
    """Test config_get_denylist returns the denylist."""
    d = Dir(populated_dir)
    d.config_set_denylist(names=["test.txt"])

    denylist = d.config_get_denylist()
    assert "test.txt" in denylist


def test_zip_alias(populated_dir):
    """Test zip() is an alias for archive_zip()."""
    import zipfile

    d = Dir(populated_dir)
    d.config_set_extensions(["wav"])

    zip_path = populated_dir / "test_alias.zip"
    assert d.zip(zip_path)

    # Verify zip was created
    assert zip_path.exists()

    with zipfile.ZipFile(zip_path) as z:
        assert sorted(z.namelist()) == ["bloop.wav", "song.wav"]


def test_afx_lpf_alias(populated_dir):
    """Test afx_lpf() is an alias for afx_low_pass()."""
    d = Dir(populated_dir, extensions=["wav"])
    assert d.afx_lpf(5000)


def test_afx_hpf_alias(populated_dir):
    """Test afx_hpf() is an alias for afx_high_pass()."""
    d = Dir(populated_dir, extensions=["wav"])
    assert d.afx_hpf(100)


def test_afx_invert_stereo_phase_alias(populated_dir):
    """Test afx_invert_stereo_phase() is an alias for afx_invert_phase()."""
    d = Dir(populated_dir, extensions=["wav"])
    assert d.afx_invert_stereo_phase("both")
    assert d.afx_invert_stereo_phase("left")
    assert d.afx_invert_stereo_phase("right")


def test_convert_to_wav(populated_dir):
    """Test convert_to_wav convenience method."""
    d = Dir(populated_dir, extensions=["wav"])
    assert d.convert_to_wav(sample_rate=44100, bit_depth=16)


def test_convert_to_mp3(populated_dir):
    """Test convert_to_mp3 convenience method."""
    d = Dir(populated_dir, extensions=["wav"])
    assert d.convert_to_mp3(bit_rate=44100, bit_depth=16)

    # Verify conversion happened
    d.config_set_extensions(["mp3"])
    assert len(d.get_all()) == 2


def test_convert_to_flac(populated_dir):
    """Test convert_to_flac convenience method."""
    d = Dir(populated_dir, extensions=["wav"])
    assert d.convert_to_flac(sample_rate=44100, bit_depth=16)

    # Verify conversion happened
    d.config_set_extensions(["flac"])
    assert len(d.get_all()) == 2


def test_convert_to_raw(populated_dir):
    """Test convert_to_raw convenience method."""
    d = Dir(populated_dir, extensions=["wav"])
    assert d.convert_to_raw(sample_rate=44100, bit_depth=16)

    # Verify conversion happened
    d.config_set_extensions(["raw"])
    assert len(d.get_all()) == 2


def test_convert_to_alias(populated_dir):
    """Test convert_to() is an alias for convert_format()."""
    d = Dir(populated_dir, extensions=["wav"])
    assert d.convert_to("mp3", sample_rate=44100)

    # Verify conversion happened
    d.config_set_extensions(["mp3"])
    assert len(d.get_all()) == 2
