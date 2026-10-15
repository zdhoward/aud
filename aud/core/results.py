from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class FileResult:
    source: str | None
    target: str
    operation: str
    status: str
    error: str | None = None
    sources: tuple[str, ...] = ()


@dataclass
class BatchResult:
    items: list[FileResult] = field(default_factory=list)

    @property
    def succeeded(self) -> bool:
        return not any(item.status in {"failed", "not_run", "cancelled"} for item in self.items)

    def to_dict(self) -> dict:
        return {"succeeded": self.succeeded, "items": [asdict(item) for item in self.items]}

    def __bool__(self) -> bool:
        return self.succeeded
