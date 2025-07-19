"""Custom exceptions used by the :mod:`aud` package."""


class BaseError(Exception):
    """Base class for all ``aud`` exceptions."""

    def __init__(self, action, exc):
        """Store the failing ``action`` and original exception."""
        self.exc = exc
        self.action = action
        self.actionPretty = action[0].upper() + action[1:].lower()

    def __str__(self):
        return f"{self.actionPretty} failure: {self.exc}"

class FileError(BaseError):
    """Raised when a filesystem operation fails."""

class FilenameError(BaseError):
    """Raised when a filename operation fails."""

class AudioFXError(BaseError):
    """Raised when an audio effect fails."""

class ConvertError(BaseError):
    """Raised when a file conversion fails."""

class ExportError(BaseError):
    """Raised during export failures."""
