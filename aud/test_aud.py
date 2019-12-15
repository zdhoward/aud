import aud
from os.path import abspath, exists, join, isfile, basename, dirname
from os import mkdir, listdir
from shutil import rmtree, copy2
import zipfile


def checkdir(target_directory):
    target_directory = abspath(target_directory)
    if not (exists(target_directory)):
        try:
            mkdir(target_directory)
        except:
            assert False
    return True


def checkfile(target_directory, file_name):
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
    global dir
    if exists(dir):
        rmtree(dir)
    assert not exists(dir)


def test_init():
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
    global dir
    a = aud.Dir(dir)

    print("SETTING EXTENSIONS")
    assert a.config_set_extensions(["txt"])
    assert a.config_get_extensions() == [".txt"]

    print("SETTING BLACKLIST")
    assert a.config_set_blacklist(["test.txt"])
    assert a.config_get_blacklist() == ["test.txt"]
    assert sorted(a.get_all()) == ["abc.txt"]
    assert a.config_set_whitelist(regex="test.txt")
    assert sorted(a.get_all()) == ["abc.txt", "test.txt"]
    assert a.config_set_whitelist([])
    assert a.config_set_blacklist(regex="test.txt")
    assert sorted(a.get_all()) == ["abc.txt"]

    print("SETTING WHITELIST")
    assert a.config_set_whitelist(["test.txt"])
    assert a.config_get_whitelist() == ["test.txt"]
    assert sorted(a.get_all()) == ["abc.txt", "test.txt"]


def test_name():
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
    global dir
    a = aud.Dir(dir)
    a.config_set_extensions(["wav"])

    assert a.afx_fade(2, 2)
    assert a.afx_pad(1, 1)
    assert a.afx_prepend("mock/bloop.wav")
    assert a.afx_append("mock/bloop.wav")

    assert a.afx_watermark("mock/bloop.wav", 1, 10)


def test_afx_2():
    global dir
    a = aud.Dir(dir)
    a.config_set_extensions(["wav"])

    assert a.afx_normalize(passes=2)
    assert a.afx_invert_stereo_phase("both")
    assert a.afx_hpf(80)
    assert a.afx_lpf(12000)


def test_afx_3():
    global dir
    a = aud.Dir(dir)
    a.config_set_extensions(["wav"])

    assert a.afx_strip_silence()
    assert a.afx_join("mock/joined.wav", "wav")
    assert a.afx_gain(3)
    assert a.afx_gain(-3)


def test_convert():
    global dir
    a = aud.Dir(dir)

    a.config_set_extensions(["wav"])
    assert a.convert_to_mp3()
    assert a.convert_to_raw()
    assert len(a.get_all()) == 3

    a.config_set_extensions(["mp3"])
    assert len(a.get_all()) == 3
    assert a.convert_to_wav()

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
    global dir
    a = aud.Dir(dir)

    a.config_set_extensions(["wav"])

    assert a.export_for("amuse", "mock/amuse")
    assert sorted(listdir(join(dir, "amuse"))) == [
        "bloop.wav",
        "joined.wav",
        "song.wav",
    ]
