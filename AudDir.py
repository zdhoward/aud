from AudFile import AudFile
from os import listdir
import arrow
import os

class AudDir:
    '''
    A wrapper for a directory path to ease use
    '''
    filepath = ""
    name = ""
    extensions = [".wav"]
    dir = ""
    files = []
    output_directory = "_Processed"

    def __init__(self, _dir, _output_directory="_Processed"):
        '''
        Initialization
        '''
        _files = listdir(_dir)
        for _file in _files:
            _file = AudFile(os.path.abspath(_dir + '\\' + _file))
            if str(_file.extension).lower() in str(self.extensions).lower():
                self.files.append(_file)

    ### UTILITIES ###
    def log(self, _dirpath):
        '''
        log the files that match the list of extensions into a meta file
        '''
        output = ""
        count = 0
        path = os.path.abspath(_dirpath)
        _files = listdir(path)
        ## Analyse each file
        for file in _files:
            filepath = os.path.abspath(file)
            if filepath.suffix in self.extensions:
                output += '' + str(path) + "\\" + str(filepath) + '\n'
                count += 1

        ## Summary of files
        output += '\n\nSUMMARY\n'
        output += "Count: " + str(count) + '\n'
        output += "Timestamp: " + str(arrow.now())
        self.writeFile(_dirpath, "meta", output)

    def writeFile(self, _dirpath, name, content, filetype=".txt"):
        '''
        A quick helper to create a simple file cleanly
        '''
        file = open(_dirpath + "/" + name + filetype, "w")
        file.write(content)
        file.close()

    ### SET METHODS ###
    def setOutputDir(self, _dirpath):
        '''
        Select an output directory
        '''
        if (Path(_dirpath).is_dir()):
            self.output_directory = _dirpath

    ### OS IO METHODS ###
    def renameUpper(self):
        '''
        Rename file to UPPERCASE
        '''
        for file in self.files:
            print(str(file))
            file.renameUpper()

    def renameLower(self):
        '''
        Rename file to lowercase
        '''
        for file in self.files:
            file.renameLower()

    def renameReplaceSpaces(self):
        '''
        Rename file to replace_all_spaces_with_underscored
        '''
        for file in self.files:
            file.renameReplaceSpaces()
