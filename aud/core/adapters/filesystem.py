from __future__ import annotations

import shutil
from pathlib import Path
from zipfile import ZipFile

from aud.core.models import AudioFile
from aud.core.operations.archive import Zip
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


class FileSystemAdapter:
    """
    Executes filesystem-related operations.

    This includes:
    - file movement (copy, move, backup)
    - renaming (name operations)
    - archiving (zip)
    """

    def ensure_dir(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    def execute(self, operation, inputs: list[AudioFile]) -> list[AudioFile]:
        # Naming / rename operations
        if isinstance(
            operation,
            (
                Uppercase,
                Lowercase,
                Append,
                Prepend,
                Replace,
                ReplaceSpaces,
                Iterate,
            ),
        ):
            return self._rename(operation, inputs)

        # File movement operations
        if isinstance(operation, (Copy, Backup)):
            return self._copy(operation, inputs)

        if isinstance(operation, Move):
            return self._move(operation, inputs)

        # Archive operations
        if isinstance(operation, Zip):
            return self._zip(operation, inputs)

        raise TypeError(f"Unsupported operation: {operation}")

    # ------------------------------------------------------------------
    # rename operations
    # ------------------------------------------------------------------

    def _rename(self, operation, inputs: list[AudioFile]) -> list[AudioFile]:
        outputs: list[AudioFile] = []

        for file in inputs:
            new_file = operation.apply(file)

            # Ensure target directory exists (paranoia-safe)
            self.ensure_dir(new_file.path.parent)

            # Perform rename on disk
            file.path.rename(new_file.path)

            outputs.append(new_file)

        return outputs

    # ------------------------------------------------------------------
    # file movement operations
    # ------------------------------------------------------------------

    def _copy(self, operation, inputs: list[AudioFile]) -> list[AudioFile]:
        self.ensure_dir(operation.target_dir)
        outputs: list[AudioFile] = []

        for file in inputs:
            dest = operation.target_dir / file.path.name
            shutil.copy2(file.path, dest)
            outputs.append(file.with_path(dest))

        return outputs

    def _move(self, operation, inputs: list[AudioFile]) -> list[AudioFile]:
        self.ensure_dir(operation.target_dir)
        outputs: list[AudioFile] = []

        for file in inputs:
            dest = operation.target_dir / file.path.name
            shutil.move(file.path, dest)
            outputs.append(file.with_path(dest))

        return outputs

    # ------------------------------------------------------------------
    # archive operations
    # ------------------------------------------------------------------

    def _zip(self, operation, inputs: list[AudioFile]) -> list[AudioFile]:
        archive = operation.archive_path
        self.ensure_dir(archive.parent)

        with ZipFile(archive, "w") as zipf:
            for file in inputs:
                zipf.write(file.path, arcname=file.path.name)

        return [AudioFile(archive)]
