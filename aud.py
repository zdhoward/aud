from pathlib import Path, PurePath

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
            files.append(new AudFile(_file))
