# Project log

## 2026-10-14: Cross-platform CI follow-up

- The first remote matrix passed on Linux and Windows; macOS exposed case-only
  renames attempting to hard-link an already identical file on its case-insensitive
  volume. Use rename for a verified same-file destination and keep exclusive linking
  when the destination is absent on case-sensitive POSIX volumes.
- Added focused branch coverage and enabled CI for all PR bases so stacked feature
  branches receive checks. This fixes observed failures without broad local retesting.

## 2026-10-14: Direct FFmpeg conversion slice

- Implemented direct conversion on `feat/ffmpeg-conversion`, stacked on the safety
  branch. Profiles, output directories, 24-bit PCM, tags/artwork, and effective
  result settings make encoding behavior explicit without convention-specific APIs.
- Added per-process deadlines/output limits and active cancellation. Source review
  caught a process-completion limit race and missing audio-stream metadata; fixed
  both with focused regressions. Lossless WAV/FLAC output also checks duration.
- Scoped checks cover new engine behavior and affected conversion/export/result
  integrations; full release validation is deferred. Effects still use pydub;
  limits are application controls and external FFmpeg patching remains required.
- No version bump, release tag, merge, or PyPI upload; the broader milestone remains
  incomplete. Public docs describe the new contract and remaining limitations.

## 2026-10-14: Public contribution and release policy

- Corrected stale private-project/direct-push guidance. Preserved all seven local
  commits on `feat/safe-processing` and returned local `master` to `origin/master`;
  no remote history was rewritten and no work was discarded.
- Document changes accompany implementation and use portable public links.
  Release tags mark reviewed milestones; PyPI publication is a separate maintainer
  decision. Changed the proposed publisher to manual dispatch with validated tag
  input, so merging the policy will decouple tags from package uploads.

## 2026-10-14: Scope development validation

- Per maintainer direction, local checks cover changes since the last passing
  run and affected integrations. Broaden only for failures or unresolved concerns;
  reserve full local suites/coverage for releases. Recorded in CONTRIBUTING.md.
- This documentation-only change requires no product test rerun.

## 2026-10-14: Initial security audit and implementation follow-up

- Completed a quick source audit of `98a9a7c` and a separate independent source
  recheck of the new processing implementation. No confirmed cross-principal
  vulnerabilities; the conditional input-trust/link lead still needs validation.
- Recorded scope, verified environment refresh, fixes, and remaining limits in
  [the security review](docs/SECURITY_REVIEW.md). Detailed evidence stays outside
  the repository; the final follow-up snapshot records source file hashes.
- No fully verified adversarial audit runner was established. Sandbox-dependent
  native checks, global FFmpeg patching and later engine/interface review remain
  work; source review and ordinary regression tests do not certify those areas.

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
