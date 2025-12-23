class BaseError(Exception):
    def __init__(self, action, exc):
        self.exc = exc
        self.action = action
        self.actionPretty = action[0].upper() + action[1:].lower()

    def __str__(self):
        return f"{self.actionPretty} failure: {self.exc}"


class FileError(BaseError):
    pass


class FilenameError(BaseError):
    pass


class AudioFXError(BaseError):
    pass


class ConvertError(BaseError):
    pass


class ExportError(BaseError):
    pass
