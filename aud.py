"""
This is the documentation for aud
"""

__version__ = "0.1.0"

from AudFile import AudFile
from AudDir import AudDir
from AudLib import setupLogger, createFolder
import begin

@begin.start(auto_convert=True)
def main(file: 'File' = "", dir: 'Directory' = ""):
    '''
    aud: Quick tools for an audio studio environment
    '''
    logger = setupLogger()
    ## Decipher arguments and run the right command
    ## Designed to work well in the interpreter
    logger.debug("Import to start")
    pass
