from pathlib import Path, PurePath
import begin
import colorlog

class AudFile:
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

class AudDir:
    filepath = ""
    name = ""
    extensions = []
    dir = ""
    files = []
    output_directory = "_Processed"

    def __init__(self, _dir, _output_directory="_Processed"):
        _files = listdir(_dir)
        for _file in _files:
            files.append(AudFile(_file))

def setupLogger(level="ERROR"):
    '''
    Config and setup the logger
    '''
    pass

def main():
    '''
    aud: Quick tools for an audio studio environment
    '''
    setupLogger("DEBUG")
    ## Decipher arguments and run the right command
    ## Designed to work well in the interpreter
    pass
