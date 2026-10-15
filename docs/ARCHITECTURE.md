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
  shutil/path ops     pydub (ffmpeg)  FFmpegEngine
```

### Dir

`Dir` is the public facade. It owns a working directory and a current file
selection, builds selection policies from configuration (extensions,
allowlist, denylist, each optionally regex), and turns method calls into
`Plan` objects that it hands to the right adapter.

Selection is evaluated as `(valid_extension AND NOT denylisted) OR allowlisted`.
If no extensions are configured, only allowlisted files are included. The
directory is re-scanned on construction and after every `config_set_*` call.

### Operations

Operations (`aud/core/operations/`) describe intent. Their
`apply(file)` is a **pure function**: it returns the `AudioFile` (or path)
the file would become, and performs no I/O. This is what makes
`Plan.preview()` safe. Since v2.0.2, preview also copies operations, so
stateful operations (like `Iterate`'s counter) are never consumed by
previewing.

`Operation` is the base class; `AudioOperation` marks audio-processor
operations. Audio operations' `apply()` is intentionally a no-op stub: audio
results are computed by the adapter, not by the intent object.

### Adapters

Adapters (`aud/core/adapters/`) execute a plan's operations and perform all
I/O. Dispatch is by `isinstance` on the operation type; unknown operations
raise `TypeError`. Effects use pydub; conversions use `FFmpegEngine` with explicit
argument arrays, probe/encode/decode verification, process limits, and cancellation.
Both require FFmpeg on PATH. The shared executor preflights all steps and records
per-file results; only successful transitions change the selection.
`AudioChain` is routed through the conversion adapter and compiles supported
effect intents into numeric FFmpeg filters, retaining one staged output per file.
It does not automatically fuse existing separate plan steps or legacy calls.

Operations on an empty selection are no-ops (since v2.0.2: no empty archives,
no placeholder audio files).

### Plans

A `Plan` pairs a snapshot of the file selection with an ordered operation
list. It is inert until an adapter executes it. `Plan.add()` returns the plan,
so plans can be built fluently.

## Error handling

`Dir` methods raise typed exceptions (`FilenameError`, `FileError`,
`AudioFXError`, `ConvertError`, `ExportError`) that wrap and chain the
original cause (`raise ... from e` since v2.0.2). Convenience methods fail fast
and retain partial outcomes in `last_result`. `Dir.execute()` returns per-file
results and optionally continues independent files. Failed/cancelled dependencies
do not reach later steps. A batch does not roll back completed outputs.

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
* Effects still decode entire files through pydub and lack active cancellation;
  direct conversions avoid loading decoded tracks into Python memory.
* Conversion limits are application controls, not OS quotas or a sandbox.
* Source editing and ancestor replacement during processing are unsupported.
* Full Python 3.13+ support requires effects migration and removal of pydub.

The unreleased [filesystem](SAFE_PROCESSING.md) and
[conversion](FFMPEG_CONVERSION.md) contracts define the implemented guarantees.
