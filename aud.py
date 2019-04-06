from pathlib import Path, PurePath
import begin
import colorlog

class AudFile:
    '''
    A wrapper for a file path to ease use
    '''
    filepath = ""
    name = ""
    extension = ""
    dir = ""
    input_file = ""
    output_directory = "_Processed"

    def __init__(self, _input_file, _output_directory="_Processed"):
        path = Path(file).resolve()
        self.filepath = path
        self.name = path.name
        self.extension = path.suffix
        self.dir = path.base

    ### override string and print
    def __repr__(self):
        return str(self.filepath)

    def __str__(self):
        return str(self.filepath)

class AudDir:
    '''
    A wrapper for a directory path to ease use
    '''
    filepath = ""
    name = ""
    extensions = []
    dir = ""
    files = []
    output_directory = "_Processed"

    def __init__(self, _dir, _output_directory="_Processed"):
        _files = listdir(_dir)
        for _file in _files:
            if Path(_file).suffix in extensions:
                files.append(AudFile(_file))


def setupLogger():
    '''
    Config and setup the logger
    '''
    ### SETUP LOGGER ###
    logger = colorlog.getLogger()
    # DEBUG INFO WARNING ERROR CRITICAL #
    logger.setLevel(colorlog.colorlog.logging.DEBUG)
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter())
    logger.addHandler(handler)
    return logger

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
