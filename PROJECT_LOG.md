# Project log

## 2026-10-14: Safe processing implementation

- Added collision policies, link-safe selection and a narrowing glob. Shared
  destination resolution drives public previews and execution; staged writes
  protect sources on encoder/copy failure and refuse late new-file collisions.
- Added per-file/group results, continuation and cancellation between files.
  Selection follows successful transitions and retains failed inputs. Exports
  write final outputs directly; ordinary tags and nominal MP3 bitrate survive
  effects. Artwork/VBR preservation and bounded codec execution remain pending.
- Independent source review caught alias moves and grouped-output propagation;
  regression tests cover the fixes. Final checks: 111 tests passed, 92.23%
  coverage; Black/Ruff/mypy and focused checked function bodies passed; wheel/sdist
  build, metadata checks and isolated installed-wheel import passed.
- Changes are recorded under Unreleased. Version 2.0.2 is unchanged; the broader
  milestone is incomplete, so no release tag or publication is appropriate.

## 2026-10-14: Reproducible audio fixtures

- Replaced recorded mock audio in tests with session-scoped generated PCM tone,
  silence, and watermark-duration fixtures. The corpus is reproducible without
  recorded media and suitable for later conformance work.
- The unchanged 74-test baseline passed with the new fixtures in 5.43 seconds,
  compared with the earlier 68.34-second run. This fixture change preserves
  existing product behavior.

## 2026-10-14: Verification tooling refresh

- Updated development tool floors and pre-commit pins to the verified current
  versions, enforced LF through Git, and added Windows to the CI configuration
  with unique per-platform coverage artifact names.
- Refreshed the repo-local development/build environment after advisory matches.
  Independent exact-version OSV rechecking found zero matches across 60 Python
  dependencies; `pip check` passed. The global FFmpeg binary remains separate
  maintenance work. The configured CI matrix has not yet run remotely.

## 2026-10-14: Add the security audit gate

- Added work package S to the readiness plan: source-first review now in the
  implementation sequence, targeted rechecks after engine/naming/CLI changes,
  and independently verified findings before the port readiness gate.
- Defined scope around actual trust boundaries, safe local validation,
  dependency/release checks, remediation, and explicit coverage gaps. Future
  web exposure requires its own review. The audit is planned, not completed;
  no runtime or release changes were made.

## 2026-10-14: Product readiness review

- Reviewed the Python core, public API, tests, documentation, automation,
  releases, and open issues. Recorded the proposed implementation sequence
  and acceptance gates in [the readiness plan](reports/Audio%20product%20readiness.md).
- Reviewed all eight reference Knowledge pages and the sample log/cue extras.
  Kept source evidence in [research notes](research_notes/Audio%20product%20readiness/audio-reference.md).
  Product concepts use naming profiles, encoding profiles, source provenance,
  and validation reports, so conventions can be supported without branding APIs
  around a particular community.
- Proposed advancing the audio execution contract before performance work,
  avoiding a pydub pipeline rewrite followed by another backend rewrite.
  Existing release allocations remain pending implementation triage.
- Baseline: 74 tests passed on Windows/Python 3.10.11 in 68.34 seconds;
  coverage 92.43%; Black, Ruff, and mypy passed. Targeted temporary-file probes
  confirmed allowlists add to extension selection and MP3 gain removes
  artist/title tags while changing encoding defaults. These checks establish
  the baseline, not proof that the uncovered product requirements already work.
- PyPI reported 2.0.1 while the checkout and latest GitHub release are 2.0.2.
  Publication and maintainer settings remain tracked work. No runtime changes,
  release, remote issue updates, or port were made during this review.
