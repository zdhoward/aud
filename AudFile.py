from pathlib import Path, PurePath

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
