import colorlog
from os import makedirs
from os.path import exists

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

def createFolder(path):
    '''
    Create folder if it does not already exist
    '''
    try:
        if not exists(path):
            makedirs(path)
        return True
    except OSError:
        logger.error("Creating directory failed")
        return False


def program_exists(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return False

def check_dependancies():
    if (not program_exists('ffmpeg')):
        return False
    if (not program_exists('ffmpeg-normalize')):
        return False
    return True
