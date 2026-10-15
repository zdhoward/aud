# Project log

## 2026-10-15: Review the built artifact before publication

- Added distribution hashes and immutable artifact identity to the build summary.
  Publication targets the `pypi` environment and downloads the same artifact,
  allowing candidate validation after building and before approval without a rebuild.
- Documented required live reviewer/ref protections and exact PyPI environment
  binding. YAML does not create approval rules; no provider settings were changed.
  Attestation verification remains open. Prior PR #85 CI and CodeQL passed.
- Validation is scoped to workflow structure and summary generation with synthetic
  distribution bytes. No aud runtime suite, scanner, workflow dispatch, release,
  version/tag change, or publication is part of this work.

## 2026-10-15: Aud-specific pre-publication security process

- Adapted the supplied general checklist into 22 aud release-candidate gates,
  with concrete source paths/tool commands, evidence fields, applicability, and
  residual-risk rules. Intentional caller-selected paths are distinguished from
  generated path/archive containment. Native adversarial checks still need the
  verified isolation boundary; no prior development result is a candidate pass.
- Split manual publishing into read-only build/metadata/artifact storage and a
  minimal download/PyPI job with OIDC. Pinned all publishing-workflow actions to
  upstream commit SHAs resolved on this date. No live provider settings changed.
- Bound publication to the build's immutable artifact ID and included attempt
  numbers in upload names, avoiding artifact collisions on workflow retries.
- Documented open reviewed-artifact handoff and attestation gates. The workflow
  still rebuilds at dispatch, so the process does not claim that an unchecked
  rebuild is a reviewed candidate artifact. Evidence output is ignored by Git.
- This is process/workflow work, not a release candidate. No scanner runs,
  full local test suite, publishing dispatch, tag, version bump, or PyPI upload.

## 2026-10-15: Independent source follow-up and stack checkpoint

- Reviewed the ten-layer draft stack at `918ce49`; every existing head was
  mergeable and green in CI. Keep integration ordered; no merge or release action.
- Independent delivery/interface reviewers found two correctness/data-policy
  defects: companded PCM bypassed lossless consent, and zero CLI output options
  could fall through to in-place effects. The maintainer traced both, corrected
  them, and obtained source rechecks. WavPack/unknown codecs now fail conservatively
  and receive unverified derivative labels when explicitly permitted.
- Also reject JSON exponent overflow and extend CodeQL to stacked PR bases.
  All 100 affected development checks pass; full local release tests stay deferred.
  Exact-version OSV query: zero matches across 65 Python packages at 11:47 UTC.
- No cross-principal defect confirmed in this focused source scope. Native
  adversarial validation, FFmpeg patch maintenance, OS resource limits, and live
  provider/release settings remain open. See the review checkpoint for gates.
  No version bump, tag, release, or PyPI publication.

## 2026-10-15: Explicit filename candidate metadata

- Added `feat/filename-parsing` above media conformance. `FilenamePattern` uses
  unique canonical fields, literal separators, bounded input, and optional exact
  numeric widths; `Dir.parse_filenames()` snapshots selected basenames without I/O.
- Chose deterministic first-separator matching rather than heuristic confidence
  scores or backtracking. Preserve text exactly and reject mismatches; candidates
  require deliberate use. No implicit tag merging or tag writes. CLI rename/album
  config selects either filename patterns or explicit metadata.
- All 57 focused filename/CLI checks passed, including portable extraction cases,
  invalid grammar, untouched sources, naming copies, and album manifest metadata.
  Lint/types pass. Full local release tests remain deferred. Independent security
  follow-up and PR-stack review remain open. No merge, release, tag, version bump,
  or PyPI publication.

- Cross-platform CI exposed a subprocess cleanup race on macOS: group signalling
  can fail after the child exits, masking the original limit error. Recheck child
  completion before suppressing that permission error; a live-child denial still
  raises. Deterministic tests cover both branches, alongside focused runner checks.

## 2026-10-15: Media and recovery conformance corpus

- Added `test/media-conformance` above JSON contracts. Data-only media fixtures
  record exact decoded PCM, metadata/artwork pixels, lossy settings, recovery
  outcomes, collisions, album payload/checksum behavior, and local delivery rules.
  The Python reference runner validates actual results against the v1 schema.
- Controlled failure/cancellation injection happens after staging and before
  publication. Cases preserve sources/existing destinations and check owned
  cleanup. Duration boundaries use policy checks without encoding hours of audio.
- All 28 new corpus cases passed across scoped runs (20 initial cases; then the
  eight added delivery cases and two changed MP3 assertions). Lint/format checks
  pass. Runtime behavior is unchanged; full local release tests remain deferred.
  Broader media/effect/alias coverage and independent security validation remain
  open. No version bump, merge, tag, release, or PyPI publication.

## 2026-10-15: Versioned JSON contracts and initial corpus

- Added `feat/json-contracts` above progress. Opt-in v1 envelopes and a bundled
  Draft 2020-12 schema give integrations/ports a concrete output contract while
  preserving Python `to_dict()` and plain CLI JSON. Schema version is separate
  from package SemVer; executable job replay remains outside scope.
- Added portable copy/naming/status fixtures and actual-output schema checks.
  Core fields are fixed; settings/details and complete provider/media semantics
  remain extensible. The initial corpus is not the full port acceptance gate.
- All 55 focused contract/CLI/progress tests passed. Full local release testing
  remains deferred. Touched-source lint/types pass; an isolated wheel build and
  separate target installation verified bundled schema access. No release,
  version bump, tag, merge, or PyPI publication.

## 2026-10-15: Observational execution progress

- Added `feat/cli-progress` above the CLI layer. Immutable progress events report
  adapter file decisions and package payload staging; final package success is
  emitted only after publication. Results remain authoritative, with counters
  scoped to each adapter operation rather than speculative time percentages.
- CLI `--progress` writes escaped, flushed lines on stderr and preserves JSON
  stdout. Reporting is opt-in. Ordinary callback errors disable that reporter
  with a static warning rather than changing file/result outcomes.
- All 86 focused progress/CLI/package/execution checks passed. Touched-source
  static checks passed. Full local release tests remain deferred. Versioned
  conformance schemas and finer media-time progress remain open; no release,
  merge, version bump, tag, or PyPI publication.

## 2026-10-15: CLI preparation and execution

- Added `feat/cli` above album packaging: list/inspect, conversion, naming,
  ordered native effects, export copies, and album commands reuse core APIs.
  Standard-library argparse keeps the base installation sufficient; retain
  optional CLI extras and legacy count-only invocation for compatibility.
- Added explicit selection, dry runs, overwrite policies, bounded JSON config,
  structured results/errors, partial-failure exit codes, and Ctrl+C cancellation.
  Output escapes terminal controls; source review checked fixed dispatch and
  config boundaries. Independent/adversarial validation remains outstanding.
- All 25 focused CLI checks and touched-source lint/type checks pass. Full local
  release testing remains deferred. Live progress, schema versioning, and other
  readiness items remain open. No version bump, merge, tag, or publication.

## 2026-10-15: Album packaging and distributor preparation

- Added grouped album plans on `feat/album-packaging`, stacked on naming profiles.
  One staged ZIP provides a clear publication boundary; generic audio remains
  byte-exact, with explicitly selected opaque sidecars and SHA-256 checksums.
- Added revisioned, dated preparation subsets for Amuse, DistroKid, TuneCore,
  CD Baby, RouteNote, Ditto, LANDR, and UnitedMasters from official guides.
  Manual portal upload/review stays explicit; this is not account integration.
- Preserve supported input properties; require consent for sample changes/lossy
  derivatives. Service audio strips embedded metadata/artwork and dithers depth
  reductions. Shared artwork policy deliberately accepts a narrow JPEG subset.
- Source follow-up tightened prepared-plan revalidation. Independent packaging
  review and sandboxed adversarial decoder validation remain open. Focused
  packaging/conversion checks: 56 passed; touched-source lint/type checks pass.
  Full local release validation remains deferred; version stays 2.0.2. No merge,
  tag, release, or PyPI upload.
- Draft PR #78 is linked above the naming layer. CI lint and all nine supported
  Linux/macOS/Windows Python 3.10-3.12 jobs passed for implementation `fdabd15`.

## 2026-10-14: Metadata naming profiles

- Added reusable profiles on `feat/naming-profiles`, stacked on audio chains.
  Directory/filename templates, explicit context/defaults, disc numbers, and
  transformations cover common preparation conventions through neutral APIs.
- Metadata preparation snapshots supplied/probed tags; rendering stays pure.
  Missing fields error or skip explicitly. Copies/moves retain exact audio bytes
  and use the shared destination, staging, results, and cancellation contracts.
- Added portable component/tree checks and bounded template formats. Source review
  found a false-success directory-alias path; in-place planning now checks actual
  parent identity and naming rejects distinct root aliases. Regression cases cover
  case-sensitive and Unicode-sensitive filesystems.
- Focused naming, execution, and safety checks pass. Full local release validation
  remains deferred; no merge, tag, release, or PyPI upload. Sidecar packaging,
  explicit filename parsing, and CLI work remain pending.

## 2026-10-14: Explicit audio chains and canonical metadata

- Added `AudioChain` on `feat/audio-chains`, stacked on direct conversions. Explicit
  chains perform supported native effects and optional conversion with one final
  encode; separate legacy calls retain their current behavior. This avoids repeated
  lossy encoding without silently changing legacy effect rounding/filter behavior.
- Added canonical metadata as a read-only view of retained tags. Invalid/conflicting
  positions, aliases, and dates report issues; missing values remain null, giving
  future naming profiles deterministic inputs without guessing from filenames.
- Focused checks cover encode count, 24-bit PCM, padding, filter/channel behavior,
  previews/results, metadata, artwork, cancellation, and failure dependencies.
  Existing conversion checks pass. Full local release validation remains deferred.
- Focused source review found missing-field preflight and lossy fade timing gaps.
  Validate required fields explicitly; measure decoded duration for timing-sensitive
  lossy chains using the bounded runner. Regression checks cover both corrections.
- Linux CI exposed version-dependent progress timestamps. Timing analysis now
  counts bounded temporary PCM frames so fade endpoints follow decoded samples.
- Remaining effects and pydub removal are incomplete. No release, tag, merge, or
  PyPI publication; version remains 2.0.2.

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
- Linux CI exposed a Windows-only subprocess constant in type analysis. Use an
  explicit platform guard and check the runner with Linux and Windows type targets.
- The Ogg regression exposed missing libvorbis in the standard macOS FFmpeg build.
  Select Homebrew's full build in CI and document codec requirements for users.
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
