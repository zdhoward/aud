from __future__ import annotations

from dataclasses import dataclass, field

from aud.core.models import AudioFile
from aud.core.operations.base import Operation


@dataclass(slots=True)
class Plan:
    """
    A Plan represents a sequence of operations to apply to a set of files.

    Plans are inert until executed by an adapter.
    """

    files: list[AudioFile]
    operations: list[Operation] = field(default_factory=list)

    def add(self, operation: Operation) -> Plan:
        self.operations.append(operation)
        return self

    def preview(self) -> list[tuple[AudioFile, AudioFile | list[AudioFile]]]:
        """
        Return a preview of what would happen without executing anything.
        """
        preview = []
        for file in self.files:
            result = file
            for op in self.operations:
                result = op.apply(result)
            preview.append((file, result))
        return preview
