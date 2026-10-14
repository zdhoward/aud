from __future__ import annotations

import os
import shutil
from pathlib import Path
from zipfile import ZipFile

from aud.core.adapters.batch import BatchAdapter
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
from aud.core.safety import check_path, destinations, path_key, staged_write


class FileSystemAdapter(BatchAdapter):
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
            Uppercase | Lowercase | Append | Prepend | Replace | ReplaceSpaces | Iterate,
        ):
            return self._rename(operation, inputs)

        # File movement operations
        if isinstance(operation, Copy | Backup):
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
        entries = destinations(
            [(f.path, operation.apply(f).path) for f in inputs],
            self.overwrite,
            protected=[f.path for f in inputs],
            in_place=True,
        )
        return self.execute_resolved(operation, inputs, entries)

    # ------------------------------------------------------------------
    # file movement operations
    # ------------------------------------------------------------------

    def _copy(self, operation, inputs: list[AudioFile]) -> list[AudioFile]:
        entries = destinations(
            [(f.path, operation.target_dir / f.path.name) for f in inputs],
            self.overwrite,
            protected=[f.path for f in inputs],
        )
        return self.execute_resolved(operation, inputs, entries)

    def _move(self, operation, inputs: list[AudioFile]) -> list[AudioFile]:
        entries = destinations(
            [(f.path, operation.target_dir / f.path.name) for f in inputs],
            self.overwrite,
            protected=[f.path for f in inputs],
        )
        return self.execute_resolved(operation, inputs, entries)

    # ------------------------------------------------------------------
    # archive operations
    # ------------------------------------------------------------------

    def _zip(self, operation, inputs: list[AudioFile]) -> list[AudioFile]:
        if not inputs:
            return []

        entries = destinations(
            [(None, operation.archive_path)], self.overwrite, protected=[f.path for f in inputs]
        )
        return self.execute_resolved(operation, inputs, entries)

    def execute_resolved(self, operation, inputs, entries):
        naming = isinstance(
            operation, (Uppercase, Lowercase, Append, Prepend, Replace, ReplaceSpaces, Iterate)
        )
        if isinstance(operation, Zip):

            def action(entry):
                if len({path_key(Path(f.name)) for f in inputs}) != len(inputs):
                    raise ValueError("Duplicate archive member names")
                with staged_write(entry) as temporary:
                    with ZipFile(temporary, "w") as zipf:
                        for file in inputs:
                            check_path(file.path)
                            zipf.write(file.path, arcname=file.name)

        else:

            def action(entry):
                check_path(entry.source)
                if naming and path_key(entry.source) == path_key(entry.target):
                    if entry.source.name != entry.target.name:
                        if os.name == "nt":
                            os.rename(entry.source, entry.target)
                        else:
                            os.link(entry.source, entry.target)
                            entry.source.unlink()
                    return
                with staged_write(entry) as temporary:
                    shutil.copy2(entry.source, temporary)
                if naming or isinstance(operation, Move):
                    entry.source.unlink()

        return self.perform(operation, entries, action)
