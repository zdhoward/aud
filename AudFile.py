import os

class AudFile:
    '''
    A wrapper for a file path to ease use
    '''
    filepath = ""
    name = ""
    extension = ""
    base = ""
    input_file = ""
    output_directory = "_Processed"

    def __init__(self, _input_file, _output_directory="_Processed"):
        path = os.path.abspath(_input_file)
        self.output_directory = _output_directory
        self.filepath = path
        self.name = os.path.basename(path)
        self.base = path.rstrip(self.name)
        #self.extension = str('.' + self.name.split('.')[1])

    ### override string and print
    def __repr__(self):
        return str(self.filepath)

    def __str__(self):
        return str(self.filepath)

    ### OS IO METHODS ###
    def renameUpper(self):
        '''
        Rename file to UPPERCASE
        '''
        os.rename(self.filepath, self.base + '\\' + self.name.upper())

    def renameLower(self):
        '''
        Rename file to lowercase
        '''
        os.rename(self.filepath, self.base + '\\' + self.name.lower())

    def renameReplaceSpaces(self):
        '''
        Rename file to replace_all_spaces_with_underscored
        '''
        os.rename(self.filepath, self.base + '\\' + self.name.replace(" ", "_"))
