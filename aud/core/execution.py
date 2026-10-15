from __future__ import annotations

import copy
from dataclasses import asdict, dataclass, field, is_dataclass, replace
from pathlib import Path

from aud.core.adapters.audio import AudioAdapter
from aud.core.adapters.convert import ConversionAdapter
from aud.core.adapters.filesystem import FileSystemAdapter
from aud.core.effect_chain import validate_effects
from aud.core.ffmpeg import validate_conversion
from aud.core.models import AudioFile
from aud.core.naming import validate_naming_tree
from aud.core.operations.archive import Zip
from aud.core.operations.audio.base import AudioOperation
from aud.core.operations.audio.chain import AudioChain
from aud.core.operations.audio.convert import ConvertFormat, ConvertToMono, ConvertToStereo
from aud.core.operations.audio.effects import AudioJoin
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
from aud.core.operations.naming import NameWithProfile
from aud.core.plan import Plan
from aud.core.results import BatchResult, FileResult
from aud.core.safety import Destination, destinations, path_key

NAME_OPERATIONS = (Append, Iterate, Lowercase, Prepend, Replace, ReplaceSpaces, Uppercase)


@dataclass
class PreviewStep:
    operation: str
    sources: list[str]
    targets: list[str]
    statuses: list[str]
    settings: dict


@dataclass
class PlanPreview:
    steps: list[PreviewStep] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"steps": [asdict(step) for step in self.steps]}


@dataclass
class Step:
    operation: object
    files: list[AudioFile]
    entries: list[Destination]
    adapter_type: type


def resolve(plan: Plan, overwrite: str) -> list[Step]:
    files = list(plan.files)
    steps = []
    original_paths = [f.path for f in files]
    for operation in copy.deepcopy(plan.operations):
        skipped = set()
        pairs: list[tuple[Path | None, Path]]
        adapter: type
        if isinstance(operation, (Zip, AudioJoin)):
            if isinstance(operation, Zip):
                keys = [path_key(Path(f.name)) for f in files]
                if len(set(keys)) != len(keys):
                    raise ValueError("Duplicate archive member names")
            target = (
                operation.archive_path if isinstance(operation, Zip) else operation.target_location
            )
            pairs = [(None, target)] if files else []
            adapter = FileSystemAdapter if isinstance(operation, Zip) else AudioAdapter
            in_place = False
        elif isinstance(operation, NameWithProfile):
            operation.validate()
            targets = [operation.target(file) for file in files]
            skipped = {index for index, target in enumerate(targets) if target is None}
            pairs = [
                (file.path, target or file.path)
                for file, target in zip(files, targets, strict=True)
            ]
            adapter = FileSystemAdapter
            in_place = not operation.copy
        elif isinstance(operation, NAME_OPERATIONS):
            pairs = [(f.path, operation.apply(f).path) for f in files]
            adapter = FileSystemAdapter
            in_place = True
        elif isinstance(operation, (Copy, Backup, Move)):
            pairs = [(f.path, operation.apply(f).path) for f in files]
            adapter = FileSystemAdapter
            in_place = False
        elif isinstance(operation, (ConvertFormat, ConvertToMono, ConvertToStereo, AudioChain)):
            if isinstance(operation, ConvertFormat):
                validate_conversion(operation)
            elif isinstance(operation, AudioChain):
                validate_effects(operation.effects)
                if operation.output is not None:
                    if not isinstance(operation.output, ConvertFormat):
                        raise TypeError("AudioChain output must be a ConvertFormat")
                    validate_conversion(operation.output)
            pairs = [(f.path, operation.apply(f).path) for f in files]
            adapter = ConversionAdapter
            in_place = True
        elif isinstance(operation, AudioOperation) and isinstance(
            operation, AudioAdapter.supported_effects
        ):
            pairs = [(f.path, f.path) for f in files]
            adapter = AudioAdapter
            in_place = True
        else:
            raise TypeError(f"Unsupported operation: {type(operation).__name__}")
        ready = iter(
            destinations(
                [pair for index, pair in enumerate(pairs) if index not in skipped],
                overwrite,
                protected=original_paths + [f.path for f in files],
                in_place=in_place,
            )
        )
        entries = [
            Destination(source, target, "skipped") if index in skipped else next(ready)
            for index, (source, target) in enumerate(pairs)
        ]
        if isinstance(operation, NameWithProfile):
            validate_naming_tree(
                operation.output_directory,
                [entry.target for entry in entries if entry.status == "ready"],
            )
        steps.append(Step(operation, files, entries, adapter))
        files = [
            AudioFile(e.source if e.status == "skipped" and e.source else e.target)
            for e in entries
            if not (e.status == "skipped" and e.source is None)
        ]
    return steps


def preview(steps: list[Step]) -> PlanPreview:
    def value(item):
        if isinstance(item, Path):
            return str(item)
        if isinstance(item, dict):
            return {str(k): value(v) for k, v in item.items()}
        if isinstance(item, (tuple, list)):
            return [value(v) for v in item]
        if is_dataclass(item) and not isinstance(item, type):
            return value(asdict(item))
        if isinstance(item, AudioOperation):
            return {"operation": type(item).__name__, "settings": value(vars(item))}
        return item

    return PlanPreview(
        [
            PreviewStep(
                type(step.operation).__name__,
                [str(f.path) for f in step.files],
                [str(e.target) for e in step.entries],
                [e.status for e in step.entries],
                {k: value(v) for k, v in vars(step.operation).items() if not k.startswith("_")},
            )
            for step in steps
        ]
    )


def execute_steps(
    steps: list[Step],
    result: BatchResult,
    *,
    continue_on_error=False,
    cancel=None,
    media_limits=None,
    progress=None,
) -> None:
    failed_sources: set[str] = set()
    for step_index, step in enumerate(steps):
        options = {"continue_on_error": continue_on_error, "cancel": cancel, "progress": progress}
        if step.adapter_type is ConversionAdapter:
            options["media_limits"] = media_limits
        adapter = step.adapter_type(**options)
        operation = step.operation
        grouped = isinstance(operation, (Zip, AudioJoin))
        entries = []
        for entry in step.entries:
            blocked = str(entry.source) in failed_sources or (
                grouped and any(str(f.path) in failed_sources for f in step.files)
            )
            if blocked:
                result.items.append(
                    FileResult(
                        str(entry.source) if entry.source else None,
                        str(entry.target),
                        type(operation).__name__,
                        "not_run",
                        "Dependency failed",
                        tuple(str(f.path) for f in step.files) if grouped else (),
                    )
                )
                failed_sources.add(str(entry.target))
            else:
                entries.append(entry)
        try:
            adapter.execute_resolved(operation, step.files, entries)
        except Exception:
            if grouped:
                adapter.result.items = [
                    replace(item, sources=tuple(str(f.path) for f in step.files))
                    for item in adapter.result.items
                ]
            result.items.extend(adapter.result.items)
            for later in steps[step_index + 1 :]:
                result.items.extend(
                    FileResult(
                        str(e.source) if e.source else None,
                        str(e.target),
                        type(later.operation).__name__,
                        "not_run",
                        sources=(
                            tuple(str(f.path) for f in later.files)
                            if isinstance(later.operation, (Zip, AudioJoin))
                            else ()
                        ),
                    )
                    for e in later.entries
                )
            raise
        if grouped:
            adapter.result.items = [
                replace(item, sources=tuple(str(f.path) for f in step.files))
                for item in adapter.result.items
            ]
        result.items.extend(adapter.result.items)
        failed_sources.update(
            item.target for item in adapter.result.items if item.status in {"failed", "cancelled"}
        )
