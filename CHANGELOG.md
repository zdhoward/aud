# Changelog

## [Unreleased]

### Added

- Explicit `FilenamePattern` and `Dir.parse_filenames()` produce candidate metadata
  from bounded basename grammars without probing, guessing, merging, or tag writes.
  CLI naming/album config accepts `filename_pattern` instead of explicit metadata;
  portable cases document exact delimiter, width, and mismatch behavior.

- Expanded the portable conformance corpus with signed 16/24-bit PCM, retained
  tags/artwork, explicit MP3 settings, staged-error recovery, collisions, album
  order/sidecars/checksums, and eight local delivery-profile expectations. Cases
  describe observable properties without encoder-version-dependent byte goldens.

- Opt-in v1 JSON envelopes, a bundled Draft 2020-12 schema, and portable
  copy/naming/result conformance fixtures. CLI `--json-version 1` preserves plain
  `--json` compatibility; Python helpers add no runtime dependencies. Full port
  equivalence and complete operation-specific schemas remain pending.

- Optional file-level `ProgressEvent` callbacks for execution and album packages,
  plus CLI `--progress` output on stderr. JSON stdout stays unchanged. Album
  payloads report staging separately from final archive publication.

- Dependency-free CLI commands for list/inspect, convert, rename, native effects,
  export copies, and album packages. Adds shared API dry runs, bounded JSON
  configuration, structured output, stable exit codes, and Ctrl+C cancellation.
  Legacy `aud DIRECTORY` remains available; live progress is pending.

- Local album ZIP plans, previews, grouped results, checksums, and opaque sidecars.
  Generic packages preserve original bytes; delivery profiles prepare audio and
  artwork for Amuse, DistroKid, TuneCore, CD Baby, RouteNote, Ditto, LANDR, and
  UnitedMasters. Profile revisions cite dated provider guides. Sample changes
  and lossy inputs require explicit consent; portal review remains manual.
- Service packaging strips embedded metadata/artwork and applies triangular
  dither when reducing to 16-bit. Ordinary conversions keep their existing defaults.

- Reusable `NamingProfile` directory/filename templates over canonical metadata,
  with disc-aware numbering, explicit defaults, case/spacing/ASCII options, and
  missing-field error/skip policies. `plan_naming()` snapshots metadata for safe
  previews; `name_profile()` provides a boolean copy/move helper without reencoding.
- Naming preflight checks portable components, directory spelling aliases, and
  file/directory prefix conflicts. Same-key in-place paths now require matching
  parent identity, preventing false-success operations across directory aliases.

- Explicit `AudioChain` batches gain, fade, pad, low/high-pass filtering, and phase
  inversion with an optional conversion in one final encode. Preview/result JSON,
  safe publication, artwork retention, and active cancellation use the shared engine.
- `AudioMetadata` provides canonical album/track/disc fields while retaining
  original tags and reporting invalid/conflicting values. Conversion and chain
  results include source/output metadata views.

- Direct FFmpeg conversions with true 24-bit PCM, explicit encoding profiles
  (`flac-preserve`, `mp3-v0`, `mp3-v2`, `mp3-320`), output directories, and
  channel selection. `MediaLimits` bounds process time and output sizes;
  active conversion cancellation cleans staging and records cancelled outcomes.
- Conversion results report effective encoder settings and unmapped metadata.
  Container/audio-stream tags and MP3/FLAC artwork survive supported conversions;
  unsupported artwork requires explicit opt-in to drop it.

- Overwrite policies (`error`, `skip`, `overwrite`, `auto-rename`), link-safe
  scanning, and a narrowing filename `pattern` glob on `Dir`.
- Public `plan()`, validated `preview()`, and `execute()` APIs with per-file
  results, fail-fast/continue behavior, and cancellation between files.

### Changed

- Lossless-input consent now uses an explicit codec allowlist. Companded PCM
  requires opt-in, as do ambiguous/unknown codecs such as WavPack. Package manifests
  distinguish known lossy derivatives from unverified source derivatives.
- Effects CLI rejects supplied output options without `--format`, including zero
  values. JSON config rejects floating-point overflow during parsing.
- CodeQL now checks stacked PRs targeting feature branches.

- Process cleanup rechecks an exited child after a process-group permission error,
  preserving the original limit/cancellation outcome in that race. Permission
  failures for a still-running child remain visible.

- Case-only renames handle case-insensitive POSIX volumes, including default macOS
  filesystems. CI also runs for stacked PRs targeting feature branches.

- File and audio outputs are staged before publication. Collisions now raise
  by default; scripts relying on replacement must explicitly opt into
  `overwrite="overwrite"`. This data-loss guard takes effect immediately
  rather than continuing unsafe writes through a deprecation window.
- Symlinks and Windows reparse points are skipped unless explicitly enabled.
  Explicit in-place effects and same-format conversion remain supported.
- Export writes final outputs directly and never deletes unrelated existing
  intermediate-name files. Exports into the source directory are rejected.
- Effects retain ordinary source tags and nominal MP3 bitrate; output decoding
  validates audio before publication. Artwork/VBR identity remain future work.
- Tests generate synthetic audio; Windows joins the CI matrix; development
  tool floors and pre-commit pins are refreshed and Git enforces LF endings.

## [2.0.2] - 2026-09-22

### Fixed

- `afx_join()` no longer prepends 1 ms of silence to the joined output; the
  joined duration is now the exact sum of the inputs. Joining or archiving an
  empty selection is a no-op instead of writing a 1 ms file or empty archive.
- `convert_stereo()` now actually converts mono sources to stereo
  (`set_channels(2)`); previously it was a no-op on mono input.
- `export_for()` writes only the converted files to the target directory
  (intermediate copies are removed), no longer repoints the current selection
  into the export directory, and rejects unknown platforms with a clear
  `ExportError`.
- `afx_watermark()` validates its interval (`0 < frequency_min <
  frequency_max`) before processing any file, instead of crashing mid-batch.
- `get_single()` raises a clear `IndexError` for out-of-range indices;
  negative indexing is supported.
- `Dir()` raises `FileNotFoundError` up front for missing or non-directory
  paths, instead of failing later during the scan.
- `Plan.preview()` no longer consumes stateful operations (an `Iterate`
  counter advanced by a preview no longer affects execution numbering).
- Exceptions raised by `Dir` operations now chain the original cause
  (`raise ... from e`), preserving tracebacks.

### Changed

- `convert_to_mp3(bit_rate=...)` and `convert_format(..., bit_rate=...)`:
  `bit_rate` is now the real encoder bitrate in kbps (e.g. `192`).
  Previously it was silently applied as a sample rate.
- `bit_depth` supports 8, 16, or 32 only. Requesting 24-bit now raises
  `ConvertError` instead of silently writing 32-bit audio.

### Testing and CI

- Test suite expanded from 37 to 74 tests; coverage is 92%.
- CI enforces a minimum coverage of 85%, uploads coverage artifacts, and runs
  a lint job (black, ruff, mypy).
- Local `pytest` runs no longer force coverage; use `pytest --cov=aud` when a
  report is wanted.

## [2.0.1] - 2026-01-30

Backward compatibility: v1 aliases (`zip`, `afx_lpf`, `afx_hpf`,
`afx_invert_stereo_phase`, `convert_to`), `convert_to_*` convenience methods,
`log()`/`get_single()` API parity, and allowlist/denylist regex support.

## [2.0.0] - 2025-12-23

Core rewrite: operations (intent) separated from adapters (execution),
policy-based selection, plans with previews, modern packaging and tooling.
