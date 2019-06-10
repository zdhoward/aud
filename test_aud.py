import aud.AudLib
import aud.AudFile
import aud.AudDir

## AUDLIB TESTS
def test_lib_program_exists():
    assert aud.AudLib.program_exists("ffmpeg")

def test_lib_check_dependencies():
    assert aud.AudLib.check_dependencies()

def test_lib_create_folder():
    assert aud.AudLib.createFolder("./test/")

## AUDFILE TESTS
file = aud.AudFile("./test/AudFile/test.wav")
def test_file_moveTo():
    assert file.move(file.base + "../AudDir")
    assert file.move(file.base + "../AudFile")

#def test_file_moveBack():
#    assert file.move(file.base + "../AudFile")

def test_file_renameUpper():
    assert file.renameUpper()

def test_file_renameLower():
    assert file.renameLower()

def test_file_renamePrepend():
    assert file.renamePrepend("test ")

def test_file_renameReplaceSpaces():
    assert file.renameReplaceSpaces('_')

def test_file_cleanupAudFile():
    try:
        import os
        os.rename(file.base + "test_test.wav", file.base + "test.wav")
        assert True
    except:
        assert False

## CLEANUP AFTER TESTS
#def test_cleanup():
#    import shutil
#    try:
#        shutil.rmtree('./test/')
#        return True
#    except:
#        return False
