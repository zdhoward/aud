# Roadmap

aud moves in planned milestones. Version numbers change only when a milestone
ships (or a hotfix demands it); a reviewed release commit aligns the version,
annotated tag, changelog, and GitHub release notes. PyPI publication is a separate
maintainer-controlled action at significant release points, not a tag-push trigger.

Tracked work lives in the GitHub issue tracker under version milestones;
this file is the overview. See [CHANGELOG.md](CHANGELOG.md) for what shipped.

## Product readiness review (2026-10-14)

The [product readiness plan](reports/Audio%20product%20readiness.md) reviews
the current code, open issues, and common audio preparation conventions.
It proposes safe batch execution, verified audio and metadata handling,
configurable naming profiles, a usable CLI, and a security audit as the
requirements before an experimental port. The proposed sequence brings the audio backend
contract forward to avoid rebuilding the execution layer twice.

The security pass starts with the current source and is repeated for the
changed engine, naming/sidecar processing, CLI, and release candidate. It
covers filesystem boundaries, external tool invocation, untrusted inputs,
resource limits, dependencies, and release automation. Confirmed high/critical
findings must be fixed and independently rechecked before the port readiness
gate; remaining findings and validation gaps require explicit triage. The
optional web UI gets a separate exposure review before shipping.

The milestones below remain the existing tracker allocation. The review
is a proposal for implementation triage, not a claim that features shipped
or that tracker milestones have been changed. Planning alone does not bump
the package version or create a release tag.

## v2.1.0: Data safety and performance

The [2026-10-15 review checkpoint](docs/REVIEW_CHECKPOINT.md) records independent
source follow-up, corrected consent/CLI defects, stack state, and open release/
port gates. It does not declare a release candidate or authorize publication.

### Implemented in the working branch, not released

The first safety slice implements overwrite policies, default link skipping,
staged/validated writes, direct final-output exports, narrowing glob selection,
and public plan/preview/per-file results with cancellation between files.
Synthetic test audio and refreshed tooling are in place; Windows is added to
the configured CI matrix. Existing allowlist/default-selection semantics remain
compatible. See [the processing contract](docs/SAFE_PROCESSING.md) and
[initial security review](docs/SECURITY_REVIEW.md) for guarantees and limits.

The next slice implements direct FFmpeg conversions, 24-bit PCM, encoding profiles,
tag/artwork handling, process/output limits, active cancellation, and effective
settings in results. See [the conversion contract](docs/FFMPEG_CONVERSION.md).
An explicit native `AudioChain` now batches supported effects with a final
conversion and reports canonical metadata fields for future naming profiles.
See [the chain contract](docs/AUDIO_CHAINS.md) for supported effects and boundaries.
Reusable naming profiles now render directory/filename templates over metadata
snapshots, with disc numbering, explicit defaults, transformations, and portable
tree/collision checks. See [the naming contract](docs/NAMING_PROFILES.md).
Album ZIP preparation now includes opaque sidecars, checksums, metadata, and
versioned profiles for eight distributors. See [album packaging](docs/ALBUM_PACKAGING.md)
for supported subsets and manual review requirements. Explicit
[filename parsing](docs/FILENAME_PARSING.md) now supplies candidate metadata to
naming and album preparation without guessing or tag writes. CLI polish and
distributor account integration remain outside this completed slice.
The first [CLI slice](docs/CLI.md) now exposes read/preview/execution commands,
bounded JSON configuration, structured results, and cancellation over these APIs.
Effects migration/batching, comprehensive metadata mapping, hard OS resource
limits, parallelism, recursive scanning, and remaining milestone work are pending.
The tracker allocation below is preserved; this progress note does not close
issues, tag a release, or change the package version.

The next planned minor release. Focus: making destructive paths explicit and
removing unnecessary re-encodes. Issue numbers and priorities live in the
tracker; the cut line if the milestone grows is **#42, #43, #64+#44+#45, #55**;
everything else can slide to a later v2.x without harm.

* **Overwrite policy for rename/copy/move/backup (implemented, unreleased).** In
  released v2.0.2, renames silently
  overwrite targets on POSIX, and `copy`/`move` overwrite existing destinations
  anywhere, including previous backups. A policy (`error` | `skip` |
  `overwrite` | `auto-rename`, default `error`) removes the silent data-loss
  class of bugs. Also covers same-name collisions when converting across
  formats in one directory.
* **Symlink handling in the scanner (implemented, unreleased).** Released
  v2.0.2 followed symlinks. The working branch skips symlinks/reparse points
  by default and resolves selected links only on explicit opt-in.
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
* **Selection and results (partly implemented).** A default common-audio-extensions preset (a bare
  `Dir(path)` currently selects nothing), an optional recursive scan, and a
  per-file results object so one bad file does not abort a batch. Results
  and explicit continuation are now implemented; audio defaults and recursive
  scanning remain pending.
* **FFmpeg presence check (implemented, unreleased).** Audio loading checks for
  ffmpeg and ffprobe and reports actionable missing-tool errors. Bounded tool
  execution remains part of the engine contract.
* **Dir-level dry-run (implemented, unreleased).** `Dir.plan()` and validated
  `Dir.preview()` expose destination and grouped-operation inspection, while
  preserving the existing pure `Plan.preview()` API.
* **Operation logging.** The configured log file is currently write-only via
  manual `Dir.log()` calls; record executed operations automatically.
* **Library logging.** The package uses no `logging` at all; long batch runs
  are silent. Adopt the standard library pattern (package logger with
  `NullHandler`, debug/info at operation boundaries) so CLIs and front ends
  can surface progress. This is distinct from the `Dir.log()` audit file.
* **Naming profiles.** Configurable templates over track and release metadata,
  optional ASCII transliteration, underscores, uppercase, year/source/custom
  affixes, and disc/track numbering (#63). Use neutral profile names rather
  than a convention-specific API. Parse existing names only with an explicit
  grammar and review inferred metadata before writing tags. The readiness
  plan expands the design and the required collision and portability checks.
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

The first unreleased CLI slice replaces the stub with list/inspect, conversion,
naming, native effects, export copies, and album packaging. It reuses core plans,
previews/results, bounded JSON configuration, and cancellation. Standard-library
argparse keeps the base install sufficient; existing `[cli]` extras stay optional.
File-level progress callbacks and opt-in CLI stderr reporting are implemented.
Opt-in [v1 JSON contracts](docs/JSON_CONTRACTS.md) and initial portable conformance
fixtures now cover core outputs. The [media corpus](conformance/v1/README.md)
adds representative PCM fidelity, tags/artwork, lossy settings, staged-error
recovery, album sidecars/checksums, and local delivery-policy boundaries.
Remaining work includes finer media-time progress, interface polish, and broader
media/operation conformance coverage.
See [the CLI contract](docs/CLI.md).

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

* Python 3.13+ support without an audioop compatibility dependency (the
  current declared dependencies do not support it)
* 24-bit output via codec parameters (implemented for unreleased direct conversions)
* Streaming for large files (pydub decodes everything into memory)

The readiness review brings the conversion contract forward; effects migration
and removal of pydub remain pending. Reassess release allocation when the complete
backend contract and Python compatibility checks are ready.

## Housekeeping (no release vehicle)

* Sanitize newlines in `Dir.log()` messages (log forging).
* Resolve `config_set_log_file()` relative to `self.directory` instead of CWD.

## Maintainer settings actions

* Apply the [release security gate](docs/RELEASE_SECURITY.md) to the final candidate,
  using the manual candidate-evidence workflow for initial scans and packaging
  smoke checks, then complete the remaining artifact tests and recorded decisions.
  Candidate and publishing builds share distribution integrity checks; installed
  regression/content review still applies to the actual publication artifacts.
  The manual publishing workflow separates its read-only build and OIDC upload
  jobs. Configure/verify the `pypi` review environment and publisher binding, then review
  the recorded artifact before approving upload. Attestation verification remains
  open before production publication.

* Review PyPI trusted publishing configuration (#71). Publication is manually
  initiated by the maintainer when a significant release is ready; do not infer
  that every tagged release should be uploaded.
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
