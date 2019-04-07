from AudFile import AudFile
from AudDir import AudDir
from AudLib import setupLogger

logger = setupLogger()
#logger.debug("This is a test")

dirpath = AudDir("test")

dirpath.renameUpper()
