# Architecture

aud v2 is a layered batch audio processor. The design goal is that *what
should happen* (operations) is completely separate from *how it happens*
(adapters), so behavior is deterministic, previewable, and testable.

## Layers

```
Dir (facade, aud/aud.py)
  |
  |  selection: DirectoryScanner + SelectionPolicy chain
  v
Plan (aud/core/plan.py) -- a file set + an ordered list of Operations
  |
  |  execution: adapters
  v
FileSystemAdapter | AudioAdapter | ConversionAdapter
  |                    |                |
  shutil/path ops     pydub (ffmpeg)  pydub (ffmpeg)
```

### Dir

`Dir` is the public facade. It owns a working directory and a current file
selection, builds selection policies from configuration (extensions,
allowlist, denylist — each optionally regex), and turns method calls into
`Plan` objects that it hands to the right adapter.

Selection is evaluated as `(valid_extension AND NOT denylisted) OR allowlisted`.
If no extensions are configured, only allowlisted files are included. The
directory is re-scanned on construction and after every `config_set_*` call.

### Operations

Operations (`aud/core/operations/`) are immutable intent objects. Their
`apply(file)` is a **pure function**: it returns the `AudioFile` (or path)
the file would become, and performs no I/O. This is what makes
`Plan.preview()` safe — since v2.0.2 preview also copies operations, so
stateful operations (like `Iterate`'s counter) are never consumed by
previewing.

`Operation` is the base class; `AudioOperation` marks audio-processor
operations. Audio operations' `apply()` is intentionally a no-op stub — audio
results are computed by the adapter, not by the intent object.

### Adapters

Adapters (`aud/core/adapters/`) execute a plan's operations and perform all
I/O. Dispatch is by `isinstance` on the operation type; unknown operations
raise `TypeError`. Audio and conversion adapters wrap pydub, which shells out
to ffmpeg — ffmpeg must be installed for audio work. Adapters return the
updated file list, which becomes the new selection.

Operations on an empty selection are no-ops (since v2.0.2: no empty archives,
no placeholder audio files).

### Plans

A `Plan` pairs a snapshot of the file selection with an ordered operation
list. It is inert until an adapter executes it. `Plan.add()` returns the plan,
so plans can be built fluently.

## Error handling

`Dir` methods raise typed exceptions (`FilenameError`, `FileError`,
`AudioFXError`, `ConvertError`, `ExportError`) that wrap and chain the
original cause (`raise ... from e` since v2.0.2). One bad file aborts the
batch; a per-file results API is planned for v2.1.0 (see
[ROADMAP.md](../ROADMAP.md)).

## Extension points

* **New operation**: subclass `Operation` (or `AudioOperation`), add a
  dispatch branch in the appropriate adapter, and expose it on `Dir`.
  A registry-based dispatch and third-party operation registration is
  planned.
* **New selection policy**: subclass `SelectionPolicy` and implement
  `include(file)`. Policies compose with `CompositePolicy` (AND) or the
  allowlist-override wrapper used by `Dir`.
* **New export preset**: add an entry to `Dir._EXPORT_PRESETS`
  (platform -> format, sample rate, bit depth).

## Invariants

* Operations never perform I/O; adapters never contain intent.
* `Plan.preview()` has no side effects on disk or on operation state.
* The audio pipeline requires ffmpeg on `PATH`.
* Files are processed in sorted order; naming operations are deterministic.

## Known limitations

* Non-recursive scanning only (recursive option planned).
* pydub decodes entire files into memory; very large files are costly
  (streaming is backlog).
* Silent-overwrite behavior in rename/copy/move is a known data-loss risk
  being addressed by the overwrite policy in v2.1.0.
* The scanner follows symlinks (guard planned for v2.1.0).
