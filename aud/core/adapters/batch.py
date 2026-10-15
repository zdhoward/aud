from __future__ import annotations

from collections.abc import Callable

from aud.core.models import AudioFile
from aud.core.results import BatchResult, FileResult
from aud.core.safety import Destination, validate_policy


class BatchAdapter:
    def __init__(self, *, overwrite="error", continue_on_error=False, cancel=None):
        self.overwrite = validate_policy(overwrite)
        self.continue_on_error = continue_on_error
        self.result = BatchResult()
        self.cancel = cancel

    def perform(
        self, operation, entries: list[Destination], action: Callable[[Destination], None]
    ) -> list[AudioFile]:
        self.result = BatchResult()
        outputs = []
        for index, entry in enumerate(entries):
            source = str(entry.source) if entry.source is not None else None
            name = type(operation).__name__
            if self.cancel is not None and self.cancel():
                for remaining in entries[index:]:
                    self.result.items.append(
                        FileResult(
                            str(remaining.source) if remaining.source is not None else None,
                            str(remaining.target),
                            name,
                            "cancelled",
                        )
                    )
                    if remaining.source is not None and remaining.source.exists():
                        outputs.append(AudioFile(remaining.source))
                break
            if entry.status == "skipped":
                self.result.items.append(FileResult(source, str(entry.target), name, "skipped"))
                if entry.source is not None:
                    outputs.append(AudioFile(entry.source))
                continue
            try:
                action(entry)
                outputs.append(AudioFile(entry.target))
                self.result.items.append(FileResult(source, str(entry.target), name, "success"))
            except Exception as error:
                self.result.items.append(
                    FileResult(source, str(entry.target), name, "failed", str(error))
                )
                if entry.source is not None and entry.source.exists():
                    outputs.append(AudioFile(entry.source))
                if not self.continue_on_error:
                    for remaining in entries[index + 1 :]:
                        self.result.items.append(
                            FileResult(
                                str(remaining.source) if remaining.source is not None else None,
                                str(remaining.target),
                                name,
                                "not_run",
                            )
                        )
                    raise
        return outputs
