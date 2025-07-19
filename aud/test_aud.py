from aud import aud
from os.path import abspath, exists, join, isfile, basename, dirname
from os import mkdir, listdir
from shutil import rmtree, copy2
import zipfile


def checkdir(target_directory):
    """Create ``target_directory`` if it does not exist."""
    target_directory = abspath(target_directory)
    if not (exists(target_directory)):
        try:
            mkdir(target_directory)
        except:
            assert False
    return True


def checkfile(target_directory, file_name):
    """Ensure ``file_name`` exists within ``target_directory``."""
    if not exists(join(target_directory, file_name)):
        try:
            file = open(join(target_directory, file_name), "w")
            file.close()
        except:
            assert False
    return True


### START TESTS ###
dir = abspath("mock")


def test_cleanup():
    """Remove the mock directory before tests run."""
    global dir
    if exists(dir):
        rmtree(dir)
    assert not exists(dir)


def test_init():
    """Set up the mock directory with sample files."""
    global dir
    print("SETTING UP FOR TEST")
    test_cleanup()
    checkdir(dir)
    checkfile(dir, "test.txt")
    checkfile(dir, "abc.txt")
    copy2(join(abspath("mock_assets"), "bloop.wav"), join(abspath("mock"), "bloop.wav"))
    copy2(join(abspath("mock_assets"), "song.wav"), join(abspath("mock"), "song.wav"))
    assert True


def test_dir():
    """Exercise basic directory operations (backup, copy, move, zip)."""
    global dir
    a = aud.Dir(dir)
    a.config_set_extensions(["wav"])

    a.config_set_log_file("mock/test.log")
    assert a.log("TESTING LOG")

    assert sorted(a.get_all()) == ["bloop.wav", "song.wav"]

    assert a.get_single(0) == "bloop.wav"  # doesn't work because its not sorted

    assert a.backup(join(dir, "backup"))
    assert sorted(a.get_all()) == ["bloop.wav", "song.wav"]
    assert sorted(listdir(join(dir, "backup"))) == ["bloop.wav", "song.wav"]

    assert a.copy(join(dir, "copy"))
    assert sorted(a.get_all()) == ["bloop.wav", "song.wav"]
    assert sorted(listdir(join(dir, "copy"))) == ["bloop.wav", "song.wav"]

    assert a.move(join(dir, "move"))
    assert sorted(a.get_all()) == ["bloop.wav", "song.wav"]
    assert sorted(listdir(join(dir, "move"))) == ["bloop.wav", "song.wav"]

    assert a.move(dir)
    assert sorted(a.get_all()) == ["bloop.wav", "song.wav"]
    assert sorted(listdir(dir)) == [
        "abc.txt",
        "backup",
        "bloop.wav",
        "copy",
        "move",
        "song.wav",
        "test.log",
        "test.txt",
    ]

    assert a.zip("mock/test.zip")
    assert isfile("mock/test.zip")
    with zipfile.ZipFile("mock/test.zip") as file:
        assert sorted(file.namelist()) == ["bloop.wav", "song.wav"]


def test_config():
    """Test allow/deny lists and extension configuration."""
    global dir
    a = aud.Dir(dir)

    print("SETTING EXTENSIONS")
    assert a.config_set_extensions(["txt"])
    assert a.config_get_extensions() == [".txt"]

    print("SETTING denylist")
    assert a.config_set_denylist(["test.txt"])
    assert a.config_get_denylist() == ["test.txt"]
    assert sorted(a.get_all()) == ["abc.txt"]
    assert a.config_set_allowlist(regex="test.txt")
    assert sorted(a.get_all()) == ["abc.txt", "test.txt"]
    assert a.config_set_allowlist([])
    assert a.config_set_denylist(regex="test.txt")
    assert sorted(a.get_all()) == ["abc.txt"]

    print("SETTING allowlist")
    assert a.config_set_allowlist(["test.txt"])
    assert a.config_get_allowlist() == ["test.txt"]
    assert sorted(a.get_all()) == ["abc.txt", "test.txt"]


def test_name():
    """Verify filename manipulation helpers."""
    global dir
    a = aud.Dir(dir)

    a.config_set_extensions(["txt"])
    assert a.config_get_extensions() == [".txt"]
    assert sorted(a.get_all()) == ["abc.txt", "test.txt"]

    assert a.name_upper()
    assert sorted(a.get_all()) == ["ABC.txt", "TEST.txt"]

    assert a.name_lower()
    assert sorted(a.get_all()) == ["abc.txt", "test.txt"]

    assert a.name_prepend("abc_")
    assert sorted(a.get_all()) == ["abc_abc.txt", "abc_test.txt"]

    assert a.name_append("_test")
    assert sorted(a.get_all()) == ["abc_abc_test.txt", "abc_test_test.txt"]

    assert a.name_replace("_", "-")
    assert sorted(a.get_all()) == ["abc-abc-test.txt", "abc-test-test.txt"]

    # doesn't work because its not sorted
    assert a.name_iterate(4, "  ")
    assert sorted(a.get_all()) == ["0001  abc-abc-test.txt", "0002  abc-test-test.txt"]

    assert a.name_replace_spaces("_")
    assert sorted(a.get_all()) == ["0001__abc-abc-test.txt", "0002__abc-test-test.txt"]


def test_afx_1():
    """Test basic audio effects that modify length."""
    global dir
    a = aud.Dir(dir)
    a.config_set_extensions(["wav"])

    assert a.afx_fade(2, 2)
    assert a.afx_pad(1, 1)
    assert a.afx_prepend("mock/bloop.wav")
    assert a.afx_append("mock/bloop.wav")

    assert a.afx_watermark("mock/bloop.wav", 1, 10)


def test_afx_2():
    """Test normalization and filtering audio effects."""
    global dir
    a = aud.Dir(dir)
    a.config_set_extensions(["wav"])

    assert a.afx_normalize(passes=2)
    assert a.afx_invert_stereo_phase("both")
    assert a.afx_hpf(80)
    assert a.afx_lpf(12000)


def test_afx_3():
    """Test silence stripping, joining and gain operations."""
    global dir
    a = aud.Dir(dir)
    a.config_set_extensions(["wav"])

    assert a.afx_strip_silence()
    assert a.afx_join("mock/joined.wav", "wav")
    assert a.afx_gain(3)
    assert a.afx_gain(-3)


def test_convert():
    """Test file format conversion helpers."""
    global dir
    a = aud.Dir(dir)

    def check_sample_rate(file, rate):
        """Return True if ``file`` has the expected sample rate."""
        info = mediainfo(file)
        print ("Checking " + str(rate) + " vs " + str(info.get("sample_rate")))
        if str(info.get("sample_rate")) == str(rate):
            print (str(info.get("sample_rate")) + " == " + str(rate))
            return True
        else:
            print (str(info.get("sample_rate")) + " != " + str(rate))
            return False


    ## TODO: THIS NEEDS TO BE UPDATED
    ## must also test and check sample rate conversion
    from pydub.utils import mediainfo

    a.config_set_extensions(["wav"])
    assert a.convert_to_mp3()
    assert a.convert_to_raw()
    assert len(a.get_all()) == 3

    a.config_set_extensions(["mp3"])
    assert len(a.get_all()) == 3
    assert a.convert_to_wav(44100)
    assert check_sample_rate(join(a.directory_path, a.filtered_files[0]), 44100)
    #assert a.convert_to_wav(48000)
    #assert check_sample_rate(join(a.directory_path, a.filtered_files[0]), 48000)

    a.config_set_extensions(["wav"])
    assert a.convert_to("ogg")
    a.config_set_extensions(["ogg"])
    assert len(a.get_all()) == 3

    a.config_set_extensions(["wav"])
    assert a.convert_to("flac")
    a.config_set_extensions(["flac"])
    assert len(a.get_all()) == 3

    a.config_set_extensions(["wav", "mp3"])
    assert a.convert_to_mono()
    assert a.convert_to_stereo()


def test_export():
    """Ensure export helpers create the expected output."""
    global dir
    a = aud.Dir(dir)

    a.config_set_extensions(["wav"])

    assert a.export_for("amuse", "mock/amuse")
    assert sorted(listdir(join(dir, "amuse"))) == [
        "bloop.wav",
        "joined.wav",
        "song.wav",
    ]
