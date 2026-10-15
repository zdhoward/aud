# Initial security review, 2026-10-14

The initial quick source audit reviewed commit `98a9a7c`, before implementation,
across the local library, selection, adapters, operations, packaging and workflows.
Independent reconnaissance, coverage criticism and source verification found no
confirmed cross-principal vulnerability. A conditional lower-trust symlink
processing lead remains dependent on the intended trust model and sandboxed
validation. This is partial source coverage, not a security certification.

A separate review of the new safety implementation identified same-file alias
moves, skipped grouped outputs reaching later operations, and incomplete grouped
failure/results handling. Those data-safety defects were fixed and covered by
regression tests. Grouped results now include their planned source identities,
and invalid archive member duplication fails before writing.

Read-only exact-version dependency inventory and OSV checks initially matched
advisories in ten development/toolchain packages. The repo-local development and
build environment was refreshed. Independent rechecking of 60 third-party Python
packages reported no advisory matches at 2026-10-14 20:48 UTC. This describes that
environment at that time; it does not guarantee future resolutions or absence of
unknown vulnerabilities. Runtime dependency declarations were not expanded.

The machine's FFmpeg 8.0.1 binary was left unchanged. Upstream documents additional
security fixes in 8.0.2 and 8.0.3; update to a maintained patched build or verify
vendor backports before processing untrusted media. This is an external-tool
maintenance limitation, not a confirmed aud exploit. See
[FFmpeg security fixes](https://ffmpeg.org/security.html).

No adversarial target execution was performed by the audit. The security audit
skill requires: "If every control cannot be enforced, do not execute target code".
No fully verified audit runner was established for this pass. Docker is available,
but an isolated runner still needs an audited toolchain, empty allowlisted
environment, network isolation, read-only mounts, scratch-only writes, and resource
limits. Windows protected-input reading also prevented the validator CLI path;
the official exported validators passed over trusted parent-owned in-memory data.
Ordinary development regression tests and package smoke checks were separate from
the adversarial audit.

The direct-conversion slice received a focused source follow-up. Fixed argument
arrays, input protocol/demuxer restrictions, staged verification, and owned-process
cleanup were reviewed. Completion now rechecks deadline/cancellation/output limits;
stream metadata is included in preservation/loss accounting. Focused regressions
cover those fixes. This does not add adversarial native-execution evidence.

The explicit chain follow-up reviewed numeric-only filter compilation, metadata
parsing, and publication/results handling. Required effect fields are now checked
explicitly during structural preflight, including caller-mutated operations.
Timing-sensitive lossy fade-out measures decoded duration through the same bounded
runner. Ordinary regressions cover these corrections; source review does not
substitute for sandboxed adversarial decoder validation.

The naming follow-up reviewed metadata-controlled paths, restricted format fields,
portable components, tree conflicts, and results. It found a false-success alias
case across distinct directories. In-place planning now verifies parent identity;
naming also rejects distinct root aliases. Case/Unicode regressions cover the fix.
No further concrete blocker was found in this source scope. No adversarial target
execution was performed for this follow-up.

The album packaging source follow-up checked archive traversal/portable aliases,
input changes, copied sidecar references, bounded writes, conversion flags, and
publication cleanup. Prepared packages now revalidate profile revisions, output
settings, explicit consent, source coverage, and release metadata. Ordinary
regressions cover these checks, cancellation, and preserved existing output.
Artwork parsing uses a bounded JPEG subset followed by the existing restricted
decoder. Checksums establish file integrity, not provenance or trust. This was
a maintainer-agent source review; independent packaging review and sandboxed
adversarial native execution remain outstanding.

The CLI source follow-up reviewed config-to-operation dispatch, output escaping,
path semantics, cancellation, and error/results handling. Config uses bounded
JSON reads, rejects duplicate/non-finite values, and selects fixed operation
constructors; it accepts no shell commands, dynamic imports, or raw filters.
CLI paths are trusted local caller choices, not a containment boundary. Terminal
path/tag/error strings are escaped. This focused source review does not provide
independent security verification or adversarial native-execution evidence.

Remaining work includes sandboxed native validation, OS-enforced decoder memory
limits, effects process limits/cancellation, stronger metadata/sidecar validation,
and release/provider settings verification. Hostile concurrent directory/source
replacement is outside the implemented filesystem guarantees. The future web UI
requires its own exposure review before shipping.

Detailed reports, the coverage ledger, and findings/validation records are retained
in the maintainer's local audit archive. Raw environment inventories, machine-specific
locations, and audit scratch data are not committed in this public repository.
