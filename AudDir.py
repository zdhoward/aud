from AudFile import AudFile
from pathlib import Path, PurePath

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
