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
    except OSError:
        logger.error("Creating directory failed")
