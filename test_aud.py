import aud.AudLib
import aud.AudFile
import aud.AudDir

## AUDLIB TESTS
def test_lib_program_exists():
    assert aud.AudLib.program_exists("ffmpeg")
    assert aud.AudLib.check_dependencies()
    assert aud.AudLib.createFolder("./test/")

## AUDFILE TESTS
file = aud.AudFile("./test/AudFile/test.wav")
def test_file_move():
    assert file.move(file.base + "../AudDir")
    assert file.move(file.base + "../AudFile")

def test_file_rename():
    assert file.renameUpper()
    assert file.renameLower()
    assert file.renamePrepend("test ")
    assert file.renameReplaceSpaces('_')
    try:
        import os
        os.rename(file.base + "test_test.wav", file.base + "test.wav")
        assert True
    except:
        assert False

def test_file_overloads():
    assert True
    # str(file)
    # file + "test"
    # repr(file)

def test_file_meta():
    assert True
    #Metadata

def test_file_ffmpeg():
    assert True
    #Fade
    #Pad
    #Convert
    #Normalize
