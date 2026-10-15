# JSON interchange contracts (unreleased)

Version 1 is an opt-in envelope for observable outputs, not an executable job
or replay format. Existing Python `to_dict()` and plain CLI `--json` are unchanged.

```shell
aud list masters --extensions wav flac --json --json-version 1
aud convert masters --extensions wav --format flac --dry-run --json --json-version 1
```

```json
{"schema_version": 1, "kind": "list", "payload": {"files": ["first.wav"]}}
```

```python
from aud import json_document, json_schema
from jsonschema import Draft202012Validator  # development dependency

document = json_document("result", result)
schema = json_schema()
Draft202012Validator.check_schema(schema)
Draft202012Validator(schema).validate(document)
```

`json_document(kind, payload, version=1)` accepts a dictionary or an object with
`to_dict()`. It returns a JSON-normalized snapshot: tuples become arrays,
non-finite/non-JSON values fail, and editing the result does not mutate the input.
It checks version, kind, and object payload, but does not validate the full payload
against the schema. No runtime dependency is added.

`json_schema(version=1)` reads a fresh copy of bundled
[`aud/schemas/v1.json`](../aud/schemas/v1.json) without network access. It uses
[JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12) and local
references only. The identifying URN is not a URL to fetch. Development validation
uses the [official jsonschema API](https://python-jsonschema.readthedocs.io/en/stable/validate/).

| Kind | Payload |
| --- | --- |
| `result` | Batch success and ordered file results. |
| `preview` | Resolved operation preview steps. |
| `album_preview` | Grouped album preparation preview. |
| `progress` | One progress event. |
| `list` | Selected filenames. |
| `inspect` | Probed properties, tags, and artwork stream indices. |
| `error` | CLI error text, exit code, optional partial result. |

Versioned CLI dry runs contain the preview directly, without the legacy
`dry_run` wrapper; the kind identifies it. Execution emits `result`, including
non-throwing failed/cancelled batches. Exceptions after parsing emit `error`.
Argument-parser errors retain their legacy shape because valid version selection
has not been established. `--json-version` requires `--json`; help/version stay
plain text. Progress remains human-readable stderr output; Python callers can
envelope individual events.

Envelope and documented core payload fields are fixed in v1. Unknown core fields,
versions, kinds, and terminal statuses fail validation. Settings, result details,
provider profiles, and album track objects are explicitly extensible: this schema
does not freeze their complete operation-specific semantics. Incompatible core
changes require another contract version, independently of package SemVer.

Compare decoded objects, ignoring key order/whitespace and retaining array order.
The schema enforces batch success against terminal statuses. Semantic relations
such as matching preview array lengths and `completed <= total` still need
consumer checks. Validation is not proof of valid media or a security boundary.
Paths are descriptive caller-selected paths, not permission to access files.
Error text, timings, absolute paths, and encoder versions vary by environment.
The archive manifest's existing version is separate; its full schema is not
included in this first interchange contract.

The [portable corpus](../conformance/v1/README.md) starts the port conformance
gate with deterministic copy, naming, status, and document cases. Add metadata
alias, audio fidelity, recovery, sidecar, and provider-specific cases before
claiming complete cross-language equivalence. Wider release tests remain required.
