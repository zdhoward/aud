from aud.core.operations.archive import Zip
from aud.core.operations.audio.convert import (
    ConvertFormat,
    ConvertToMono,
    ConvertToStereo,
)
from aud.core.operations.base import Operation
from aud.core.operations.files import Backup, Copy, Move
from aud.core.operations.names import (
    Append,
    Iterate,
    Lowercase,
    Prepend,
    Replace,
    ReplaceSpaces,
    Uppercase,
)

__all__ = [
    "Operation",
    "Uppercase",
    "Lowercase",
    "Append",
    "Prepend",
    "Replace",
    "ReplaceSpaces",
    "Iterate",
    "Copy",
    "Move",
    "Backup",
    "Zip",
    "ConvertFormat",
    "ConvertToMono",
    "ConvertToStereo",
]
