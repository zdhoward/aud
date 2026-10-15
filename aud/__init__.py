"""aud - A tool for batch audio file processing."""

__version__ = "2.0.2"

# Import the Dir class from the aud module
from aud.aud import Dir
from aud.core.ffmpeg import MediaLimits

__all__ = ["Dir", "MediaLimits", "__version__"]
