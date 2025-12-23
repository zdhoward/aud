from __future__ import annotations

import sys
from pathlib import Path

from aud import Dir


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: aud <directory>")
        sys.exit(1)

    directory = Path(sys.argv[1])

    if not directory.exists():
        print(f"Directory does not exist: {directory}")
        sys.exit(1)

    a = Dir(directory)
    files = a.get_all()
    print(f"Found {len(files)} files")
