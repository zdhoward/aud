# Portable conformance corpus v1

`cases.json` contains data only; `tests/test_contracts.py` is its reference runner.
Run `pytest tests/test_contracts.py -q`.

`media.json` adds the media/recovery corpus, run with
`pytest tests/test_media_conformance.py -q` (FFmpeg/ffprobe required).

`filename.json` records explicit filename grammar extraction/mismatch cases;
`pytest tests/test_filename_parsing.py -q` also checks grammar rejection and API/CLI
integration. Preserve exact captured text and first-separator behavior.

- PCM cases specify signed integer samples, bit depth, rate, channels, and repeat
  count. Repeat the sample array `repeat * channels` times, encode each integer
  as signed little-endian PCM, and write interleaved frames to WAV. Convert to
  FLAC and decode to the same raw PCM width. Compare all decoded bytes exactly,
  source bytes unchanged, and probed rate/depth/channels. WAV container bytes
  are not golden output: container headers can differ by encoder version.
- Metadata/artwork uses a project-owned one-pixel RGBA PNG. Preserve its decoded
  pixel and tags through WAV -> tagged/artwork FLAC -> MP3. Compare canonical
  disc/track totals too. PNG compressed bytes and encoder tags are not golden.
- Lossy profiles compare effective profile/mode/encoder, sample properties, and
  the specified CBR bitrate. Do not compare lossy encoded bytes across versions.
- Recovery injects a controlled encoder error/cancellation after writing owned
  staging bytes for `a.wav`, before publication. `b.wav` follows normally when
  allowed. Match statuses/published names, preserve existing `a.flac` and both
  sources, and check owned temporary cleanup. This is deterministic error
  injection, not an adversarial decoder test or proof of process termination.
- Collision cases preserve an existing destination under error/skip/auto-rename
  and compare preview with execution where applicable.
- Album cases check explicit order, original payload bytes, opaque cue contents,
  manual submission state, and every checksum. The cue references an absent
  external name deliberately: the packager must not follow that reference.
- Delivery cases pin local profile choices, explicit sample-change consent,
  dither, track caps, and DistroKid/LANDR duration boundaries. Settings/boundary
  checks do not encode giant files or certify portal acceptance. Existing
  end-to-end package tests remain necessary for actual encoded service outputs.

- `copy`: write the named UTF-8 input, preview Copy to `out`, execute, and compare
  expected v1 documents and byte equality. Its `.flac` extension exercises
  selection only: the contents are owned opaque text, not playable audio.
- `naming`: render canonical metadata/profile and compare exact relative POSIX
  paths, including Unicode/ASCII behavior.
- `results`: preserve status order and compare batch success semantics.
- `progress` and `error`: representative versioned document fixtures.

`$ROOT` represents the disposable working directory. Replace that prefix only
in path fields and use `/` separators for comparison. Do not rewrite metadata,
normalize Unicode/case, sort arrays, or drop unexpected fields. Compare decoded
JSON values, not object key order. Do not compare temporary paths, timestamps,
or encoder-version-dependent bytes.

These are representative deterministic cases, not the full release/port gate.
Active process cancellation, broader metadata aliases/effects, provider changes,
and other platform checks in the wider suite remain necessary. See
[JSON contracts](../../docs/JSON_CONTRACTS.md) for scope and policy.
