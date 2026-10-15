"""Observational progress events; results remain the execution authority."""

import logging
from collections.abc import Callable
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ProgressEvent:
    phase: str
    operation: str
    completed: int
    total: int
    source: str | None = None
    target: str | None = None
    status: str | None = None

    def to_dict(self):
        return asdict(self)


class ProgressReporter:
    def __init__(self, callback: Callable[[ProgressEvent], None] | None = None):
        if callback is not None and not callable(callback):
            raise TypeError("progress must be callable or None")
        self.callback = callback

    def __call__(self, event: ProgressEvent):
        if self.callback is None:
            return
        try:
            self.callback(event)
        except Exception:
            self.callback = None
            logging.getLogger(__name__).warning("Progress callback failed; further events disabled")

    @classmethod
    def wrap(cls, callback):
        return callback if isinstance(callback, cls) else cls(callback)
