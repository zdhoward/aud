from pathlib import Path, PurePath
import begin

@begin.start(auto_convert=True)
def main(file: 'File' = "", dir: 'Directory' = ""):
    '''
    aud: Quick tools for an audio studio environment
    '''
    logger = setupLogger()
    ## Decipher arguments and run the right command
    ## Designed to work well in the interpreter
    logger.debug("Testing")
    pass
