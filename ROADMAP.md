# Roadmap

aud moves in planned milestones. Version numbers change only when a milestone
ships (or a hotfix demands it); the version bump lands in the same commit that
is tagged, and the tag, GitHub release, and PyPI publish happen together.

Tracked work lives in the GitHub issue tracker under version milestones;
this file is the overview. See [CHANGELOG.md](CHANGELOG.md) for what shipped.

## v2.1.0: Data safety and performance

The next planned minor release. Focus: making destructive paths explicit and
removing unnecessary re-encodes. Issue numbers and priorities live in the
tracker; the cut line if the milestone grows is **#42, #43, #64+#44+#45, #55**;
everything else can slide to a later v2.x without harm.

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
* **Library logging.** The package uses no `logging` at all; long batch runs
  are silent. Adopt the standard library pattern (package logger with
  `NullHandler`, debug/info at operation boundaries) so CLIs and front ends
  can surface progress. This is distinct from the `Dir.log()` audit file.
* **Scene naming.** `name_scene()` (ASCII transliteration, underscores,
  uppercase, year/source/group affixes, track numbering) and scene-name
  parsing into tags for release-processing workflows (#63).
* **Core simplification.** Collapse the 27 duplicated try/except wrappers in
  `Dir`, unify the three `_execute_*` methods, registry-based adapter
  dispatch, and a shared pydub adapter base. Behavior-neutral, landed with
  the batching/parallelism work so the execution layer is restructured once
  (#64).
* **Test hardening.** Unicode/spaced filename coverage (#65) and a benchmark
  harness plus property-based tests for the pure cores, recorded before the
  performance work lands (#66).
* **Release hygiene slotted into this milestone:** pre-commit pin refresh and
  `eol=lf` (#49), synthetic test assets + `main.py` removal (#54, publish
  workflow already landed, Python 3.13 item deferred to v3.0.0), and
  single-sourcing the package version (#56).

## v2.2.0: CLI

The current `aud` console entry is a stub, while `click`, `rich`, and
`questionary` are already declared in the `[cli]` extra. Build the real CLI:
list/convert/rename/effects/export commands, `--dry-run` backed by
`Plan.preview()`, and export presets.

## v2.3.0: Optional web UI

A separate optional install (`pip install aud[web]`) exposing a small local
web UI over the `Dir` API: directory browsing locked to a chosen root,
operation preview, batch jobs with progress (SSE), FastAPI backend with a
no-build-step static frontend. Additive; the core package stays dependency-light.

## v3.0.0: pydub migration

pydub is unmaintained (0.25.1, June 2021) and imports `audioop`, which was
removed from the stdlib in Python 3.13. The dependency is the single
biggest liability in the stack (#62, high priority). Migrating the audio
execution layer to direct ffmpeg subprocess calls buys three things at once:

* Python 3.13+ support (currently impossible)
* 24-bit output via codec parameters (today `bit_depth` accepts 8/16/32 only)
* Streaming for large files (pydub decodes everything into memory)

Sequencing: after v2.1.0, so the batching rework (#44) lands first and the
migration reworks the same layer once, informed by the registry dispatch.

## Housekeeping (no release vehicle)

* Sanitize newlines in `Dir.log()` messages (log forging).
* Resolve `config_set_log_file()` relative to `self.directory` instead of CWD.

## Maintainer settings actions

* Activate PyPI trusted publishing and upload v2.0.2 (#71, includes
  step-by-step instructions).
* Enable branch protection on `master` (require CI + CodeQL checks): #69.
* Enable GitHub private vulnerability reporting (Settings → Code security),
  so the SECURITY.md instructions work.

## Backlog (needs design decisions)

* Video generation from an image + audio (old issue #21, includes a YouTube
  export profile). Decide whether this belongs in aud's scope.

## Agreed, unscheduled

* Generated API reference + playbooks (#67): blueprint agreed in the issue;
  awaiting a slot.
* Plugin surface: `aud.operations` entry-points (#68), after registry
  dispatch (#64).
