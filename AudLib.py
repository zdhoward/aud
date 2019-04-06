import colorlog

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
