from __future__ import annotations

from collections.abc import Callable

from aud.core.models import AudioFile
from aud.core.progress import ProgressEvent, ProgressReporter
from aud.core.results import BatchResult, FileResult, OperationCancelled
from aud.core.safety import Destination, validate_policy


class BatchAdapter:
    def __init__(self, *, overwrite="error", continue_on_error=False, cancel=None, progress=None):
        self.overwrite = validate_policy(overwrite)
        self.continue_on_error = continue_on_error
        self.result = BatchResult()
        self.cancel = cancel
        self.progress = ProgressReporter.wrap(progress)

    def _record(self, item, total):
        self.result.items.append(item)
        self.progress(
            ProgressEvent(
                "finish",
                item.operation,
                len(self.result.items),
                total,
                item.source,
                item.target,
                item.status,
            )
        )

    def perform(
        self, operation, entries: list[Destination], action: Callable[[Destination], dict | None]
    ) -> list[AudioFile]:
        self.result = BatchResult()
        outputs = []
        for index, entry in enumerate(entries):
            source = str(entry.source) if entry.source is not None else None
            name = type(operation).__name__
            if self.cancel is not None and self.cancel():
                for remaining in entries[index:]:
                    self._record(
                        FileResult(
                            str(remaining.source) if remaining.source is not None else None,
                            str(remaining.target),
                            name,
                            "cancelled",
                        ),
                        len(entries),
                    )
                    if remaining.source is not None and remaining.source.exists():
                        outputs.append(AudioFile(remaining.source))
                break
            if entry.status == "skipped":
                self._record(FileResult(source, str(entry.target), name, "skipped"), len(entries))
                if entry.source is not None:
                    outputs.append(AudioFile(entry.source))
                continue
            try:
                self.progress(
                    ProgressEvent(
                        "start",
                        name,
                        len(self.result.items),
                        len(entries),
                        source,
                        str(entry.target),
                    )
                )
                details = action(entry) or {}
                outputs.append(AudioFile(entry.target))
                self._record(
                    FileResult(source, str(entry.target), name, "success", details=details),
                    len(entries),
                )
            except Exception as error:
                self._record(
                    FileResult(
                        source,
                        str(entry.target),
                        name,
                        "cancelled" if isinstance(error, OperationCancelled) else "failed",
                        str(error),
                    ),
                    len(entries),
                )
                if entry.source is not None and entry.source.exists():
                    outputs.append(AudioFile(entry.source))
                if isinstance(error, OperationCancelled):
                    for remaining in entries[index + 1 :]:
                        self._record(
                            FileResult(
                                str(remaining.source) if remaining.source is not None else None,
                                str(remaining.target),
                                name,
                                "cancelled",
                            ),
                            len(entries),
                        )
                        if remaining.source is not None and remaining.source.exists():
                            outputs.append(AudioFile(remaining.source))
                    break
                if not self.continue_on_error:
                    for remaining in entries[index + 1 :]:
                        self._record(
                            FileResult(
                                str(remaining.source) if remaining.source is not None else None,
                                str(remaining.target),
                                name,
                                "not_run",
                            ),
                            len(entries),
                        )
                    raise
        return outputs
