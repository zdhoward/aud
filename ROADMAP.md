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
* **Selection power-ups.** Regex filtering exists today but uses prefix
  matching (`re.match`) with no safety guard, and only allow/denylist support
  patterns. Move to `fullmatch` semantics (with a compatibility note), add
  glob patterns (`fnmatch`) as the friendly alternative, accept custom
  predicates and full `SelectionPolicy` objects on `Dir`, and support
  metadata filters (duration, size, sample rate, channels). Bound regex
  compile/eval cost before the web UI makes it a ReDoS surface.
* **Selection and results.** A default common-audio-extensions preset (a bare
  `Dir(path)` currently selects nothing), an optional recursive scan, and a
  per-file results object so one bad file does not abort a batch.
* **FFmpeg presence check.** pydub failures without ffmpeg installed surface
  as confusing wrapped tracebacks (old issue #11, closed unimplemented).
  Check once at operation time with a clear actionable message.
* **Dir-level dry-run.** `Plan.preview()` exists but is not reachable from
  the `Dir` facade; expose a preview/dry-run API so users (and the future
  CLI's `--dry-run`) can see renames and targets before executing.
* **Operation logging.** The configured log file is currently write-only via
  manual `Dir.log()` calls; record executed operations automatically.
* **Library logging.** The package uses no `logging` at all — long batch runs
  are silent. Adopt the standard library pattern (package logger with
  `NullHandler`, debug/info at operation boundaries) so CLIs and front ends
  can surface progress. This is distinct from the `Dir.log()` audit file.
* **Scene naming.** `name_scene()` (ASCII transliteration, underscores,
  uppercase, year/source/group affixes, track numbering) and scene-name
  parsing into tags for release-processing workflows (#63).
* **Core simplification.** Collapse the 27 duplicated try/except wrappers in
  `Dir`, unify the three `_execute_*` methods, registry-based adapter
  dispatch, and a shared pydub adapter base — behavior-neutral, landed with
  the batching/parallelism work so the execution layer is restructured once
  (#64).
* **Test hardening.** Unicode/spaced filename coverage (#65) and a benchmark
  harness plus property-based tests for the pure cores, recorded before the
  performance work lands (#66).

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
* Replace the 27MB `song.wav` test asset with generated short synthetic audio —
  the audio tests decode/encode it repeatedly and dominate the ~50s suite run
  (old issue #31, closed unimplemented).
* Add Python 3.13 to the CI matrix and trove classifiers.
* Add a PyPI publish workflow triggered on tag push (build + twine), so the
  tag/release/publish sequence is mechanical.
* Remove the stale `main.py` dev shim at the repo root (references a `mock/`
  directory; superseded by the test suite).
* Single-source the package version — it is declared in both `pyproject.toml`
  and `aud/__init__.py`, which is how the v2.0.1 tag/metadata mismatch
  happened. Use hatch's dynamic version from `aud.__init__`.
* Add community files: `CONTRIBUTING.md`, `SECURITY.md`, and GitHub
  PR/issue templates.
* Sanitize newlines in `Dir.log()` messages (log forging).
* Resolve `config_set_log_file()` relative to `self.directory` instead of CWD.

## Backlog (needs design decisions)

* **Migrate off pydub.** pydub is unmaintained (0.25.1, June 2021) and imports
  `audioop`, which was removed from the stdlib in Python 3.13 — this blocks
  3.13 support and makes the dependency a growing liability. Options: direct
  ffmpeg subprocess calls, `ffmpeg-python`, or PyAV. Best combined with the
  op-batching rework (#44), since both touch the audio execution layer.
* Video generation from an image + audio (old issue #21, includes a YouTube
  export profile) — decide whether this belongs in aud's scope.
* Generated API reference (`mkdocstrings` + GitHub Pages) so `API.md` cannot
  drift (#67).
* Plugin surface: `aud.operations` entry-points once registry dispatch lands
  (#68).
* Direct ffmpeg filter-chain pipelines for large files (streaming instead of
  full in-memory decode).
* 24-bit output support via ffmpeg codec parameters (today `bit_depth` accepts
  8/16/32 only and raises otherwise).
