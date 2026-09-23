# Roadmap

aud moves in planned milestones. Version numbers change only when a milestone
ships (or a hotfix demands it); the version bump lands in the same commit that
is tagged, and the tag, GitHub release, and PyPI publish happen together.

Tracked work lives in the GitHub issue tracker under version milestones;
this file is the overview. See [CHANGELOG.md](CHANGELOG.md) for what shipped.

## v2.1.0 — Data safety and performance

The next planned minor release. Focus: making destructive paths explicit and
removing unnecessary re-encodes.

* **Overwrite policy for rename/copy/move/backup.** Today renames silently
  overwrite targets on POSIX, and `copy`/`move` overwrite existing destinations
  anywhere, including previous backups. A policy (`error` | `skip` |
  `overwrite` | `auto-rename`, default `error`) removes the silent data-loss
  class of bugs. Also covers same-name collisions when converting across
  formats in one directory.
* **Symlink handling in the scanner.** `DirectoryScanner` currently follows
  symlinks, so files outside the working tree can be copied, zipped, or
  processed. Default should skip or opt in explicitly.
* **Batch audio operations.** Chained operations currently decode and
  re-encode once per operation per file (generation loss, 2 ffmpeg spawns per
  op). Restructure adapters to decode once, apply all operations, encode once.
* **Parallel processing.** pydub work is ffmpeg-subprocess bound; a thread
  pool over files gives near-linear speedup with a `max_workers` option.
* **Selection and results.** A default common-audio-extensions preset (a bare
  `Dir(path)` currently selects nothing), an optional recursive scan, and a
  per-file results object so one bad file does not abort a batch.

## v2.2.0 — CLI

The current `aud` console entry is a stub, while `click`, `rich`, and
`questionary` are already declared in the `[cli]` extra. Build the real CLI:
list/convert/rename/effects/export commands, `--dry-run` backed by
`Plan.preview()`, and export presets.

## v2.3.0 — Optional web UI

A separate optional install (`pip install aud[web]`) exposing a small local
web UI over the `Dir` API: directory browsing locked to a chosen root,
operation preview, batch jobs with progress (SSE), FastAPI backend with a
no-build-step static frontend. Additive; the core package stays dependency-light.

## Housekeeping (no release vehicle)

* Refresh pre-commit hook pins (black 24.1.1 → 26.x, ruff 0.1.15 → 0.14.x,
  mypy 1.8.0 → 1.19.x) to match tooling used in CI.
* Set `eol=lf` in `.gitattributes` so Windows checkouts get LF endings, matching
  the pre-commit `mixed-line-ending --fix=lf` hook.
* Sanitize newlines in `Dir.log()` messages (log forging).
* Resolve `config_set_log_file()` relative to `self.directory` instead of CWD.

## Backlog (needs design decisions)

* Video generation from an image + audio (old issue #21, includes a YouTube
  export profile) — decide whether this belongs in aud's scope.
* Direct ffmpeg filter-chain pipelines for large files (streaming instead of
  full in-memory decode).
* 24-bit output support via ffmpeg codec parameters (today `bit_depth` accepts
  8/16/32 only and raises otherwise).
