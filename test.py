from AudFile import AudFile
from AudDir import AudDir
from AudLib import setupLogger

logger = setupLogger()
#logger.debug("This is a test")

dirpath = AudDir("test")

#dirpath.pad(2.0,2.0)
#dirpath.renameReplaceSpaces()
dirpath.convertTo(".wav", _target_samplerate=44100)
