# Portable conformance corpus v1

`cases.json` contains data only; `tests/test_contracts.py` is its reference runner.
Run `pytest tests/test_contracts.py -q`.

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

These are initial deterministic cases, not the full release/port gate. Actual
media, cancellation, failure, and platform checks in the wider suite remain
necessary. See [JSON contracts](../../docs/JSON_CONTRACTS.md) for scope and policy.
