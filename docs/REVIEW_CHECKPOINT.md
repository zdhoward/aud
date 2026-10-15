# Review checkpoint, 2026-10-15

The Python readiness work is still unreleased. Package version remains 2.0.2.
The stack was inspected at `918ce49`; all ten existing PRs were mergeable, draft,
and green on their latest CI heads. This snapshot is not a release approval.

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

`fix/review-follow-up` is layered above these PRs. It corrects codec consent and
CLI option presence, rejects non-finite JSON overflow, and enables CodeQL for
all PR bases. Independent source reviewers checked the changes; the
[security record](SECURITY_REVIEW.md) describes evidence and limits.

Keep the dependency order during eventual review/integration. Do not treat each
layer as a release, tag intermediate heads, or publish the unreleased package.
If history or base branches change, recheck the actual final integrated head;
green checks on prior heads do not certify a later combination.

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
