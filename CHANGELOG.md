# Changelog

## [2.0.2] — 2026-09-22

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

## [2.0.1] — 2026-01-30

Backward compatibility: v1 aliases (`zip`, `afx_lpf`, `afx_hpf`,
`afx_invert_stereo_phase`, `convert_to`), `convert_to_*` convenience methods,
`log()`/`get_single()` API parity, and allowlist/denylist regex support.

## [2.0.0] — 2025-12-23

Core rewrite: operations (intent) separated from adapters (execution),
policy-based selection, plans with previews, modern packaging and tooling.
