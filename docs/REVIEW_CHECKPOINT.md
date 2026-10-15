# Review checkpoint, 2026-10-15

The Python readiness work is still unreleased. Package version remains 2.0.2.
Before integration, all seventeen PRs #74-90 were mergeable, draft, and green on
their latest CI heads through `ebed525`. The maintainer authorized merging after
documentation review. Integration is not a release approval; recheck the final
default-branch head and run candidate evidence collection after integration.

PRs #74-90 were merged in dependency order with merge commits. After every merge,
the resulting default-branch tree matched the corresponding reviewed feature head.
The final integration commit is `683286e`. Integrated CI/CodeQL and the first
[manual evidence run](https://github.com/zdhoward/aud/actions/runs/38750990602)
were started on that exact commit. Their results must be reviewed separately from
the pre-integration checks; this checkpoint does not declare a release candidate.

The first evidence run failed: Bandit findings require triage, scanner-report
upload excluded the hidden evidence directory, and the installed runner resolved
POSIX venv interpreter symlinks to the base Python. The workflow follow-up enables
hidden files only for explicit evidence paths and preserves the venv executable
path. Scanner and installed-regression gates remain pending a successful rerun.

Follow-up [run `38752076905`](https://github.com/zdhoward/aud/actions/runs/38752076905)
passed on `49251f1`: all four scanner steps and distribution checks succeeded,
with 100 installed tests passing for each artifact and successful import
observations. The [security record](SECURITY_REVIEW.md) documents the three narrow
Bandit exclusions and their independent source recheck. These dated development
results do not complete the full release checklist or approve publication.

| Order | PR | Scope |
| --- | --- | --- |
| 1 | [#74](https://github.com/zdhoward/aud/pull/74) | Selection, safe writes, plans/results, publishing policy |
| 2 | [#75](https://github.com/zdhoward/aud/pull/75) | Direct FFmpeg conversion and encoding profiles |
| 3 | [#76](https://github.com/zdhoward/aud/pull/76) | Explicit audio chains and canonical metadata |
| 4 | [#77](https://github.com/zdhoward/aud/pull/77) | Metadata naming profiles |
| 5 | [#78](https://github.com/zdhoward/aud/pull/78) | Album delivery packages |
| 6 | [#79](https://github.com/zdhoward/aud/pull/79) | CLI preparation and execution |
| 7 | [#80](https://github.com/zdhoward/aud/pull/80) | Observational progress |
| 8 | [#81](https://github.com/zdhoward/aud/pull/81) | Versioned JSON contracts |
| 9 | [#82](https://github.com/zdhoward/aud/pull/82) | Portable media/recovery corpus |
| 10 | [#83](https://github.com/zdhoward/aud/pull/83) | Filename parsing and process cleanup race fix |
| 11 | [#84](https://github.com/zdhoward/aud/pull/84) | Codec consent, CLI/config validation, independent review follow-up |
| 12 | [#85](https://github.com/zdhoward/aud/pull/85) | Release security checklist and minimal OIDC publishing job |
| 13 | [#86](https://github.com/zdhoward/aud/pull/86) | Artifact identity/hashes and publication environment handoff |
| 14 | [#87](https://github.com/zdhoward/aud/pull/87) | Manual scanner and packaging evidence workflow |
| 15 | [#88](https://github.com/zdhoward/aud/pull/88) | Shared wheel/sdist integrity validation |
| 16 | [#89](https://github.com/zdhoward/aud/pull/89) | Installed-artifact regressions outside the checkout |
| 17 | [#90](https://github.com/zdhoward/aud/pull/90) | Retained rule snapshots and installed import observations |

`fix/review-follow-up` corrects codec consent and
CLI option presence, rejects non-finite JSON overflow, and enables CodeQL for
all PR bases. Independent source reviewers checked the changes; the
[security record](SECURITY_REVIEW.md) describes evidence and limits.

Keep the dependency order during eventual review/integration. Do not treat each
layer as a release, tag intermediate heads, or publish the unreleased package.
If history or base branches change, recheck the actual final integrated head;
green checks on prior heads do not certify a later combination.

Feature guides, CLI/config references, versioned JSON schema and conformance
fixtures, changelog, roadmap, and project log describe the unreleased behavior.
Release security/evidence documentation distinguishes implemented automation from
pending candidate scans, native isolation, reproducibility, and live provider gates.
No version bump, release tag, or PyPI upload is authorized by this integration.

## Gates still open

The [aud-specific release security process](RELEASE_SECURITY.md) and
[22-item evidence template](RELEASE_EVIDENCE_TEMPLATE.md) define candidate checks.
They are not a completed scanner run or approval. Publication now separates build
from OIDC upload. The build records artifact identity/hashes and the upload job
targets `pypi` for approval of the same files. Live environment protections,
publisher binding, and provider attestations remain open gates before production use.

- A maintainer-reviewed release scope, SemVer choice, consistent version/tag/log,
  and the full local release suite on the final candidate. Development checks
  remain focused; no release candidate is declared by this checkpoint.
- A maintained patched native FFmpeg build or verified vendor backports before
  untrusted-media use. The inspected local binary is still 8.0.1; upstream lists
  later security fixes. See [FFmpeg security](https://ffmpeg.org/security.html).
- A verified adversarial runner with network isolation, allowlisted environment,
  read-only source/toolchain, scratch-only writes, and hard resource limits.
  Source-only review and ordinary regression tests do not close that gap.
- Remaining legacy-effects limits/cancellation and Python 3.13+ dependency work;
  broader metadata/media/effect/provider conformance and documented residual risk.
- Maintainer verification of branch protection, private vulnerability reporting,
  and PyPI trusted-publishing/provider settings. Source workflow review does not
  establish the live settings. PyPI publication remains a separate manual action.

The optional web UI and hostile concurrent filesystem mutation require separate
exposure designs/reviews. No new cross-principal security defect was confirmed
by this focused follow-up; that statement is limited to its recorded scope.
