"""aud - A tool for batch audio file processing."""

__version__ = "2.0.2"

# Import the Dir class from the aud module
from aud.aud import Dir
from aud.core.delivery import DELIVERY_PROFILES, DeliveryProfile, delivery_profile
from aud.core.ffmpeg import MediaLimits
from aud.core.metadata import AudioMetadata
from aud.core.naming import NamingProfile
from aud.core.operations.audio.chain import AudioChain
from aud.core.packaging import AlbumPackage
from aud.core.progress import ProgressEvent

__all__ = [
    "Dir",
    "MediaLimits",
    "AudioChain",
    "AudioMetadata",
    "NamingProfile",
    "AlbumPackage",
    "ProgressEvent",
    "DELIVERY_PROFILES",
    "DeliveryProfile",
    "delivery_profile",
    "__version__",
]
