# Pre-publication security gate for aud

Apply this gate to a reviewed release candidate, before any PyPI dispatch or
distribution to other developers. During development, run only affected tests
and checks; ordinary CI retains its supported-platform matrix. A green scanner
or coverage percentage does not certify security.

Create candidate evidence from [the template](RELEASE_EVIDENCE_TEMPLATE.md).
Record the exact commit, tool/rule versions, environment, commands, exit codes,
artifact hashes, findings/decisions, and reviewer. A missing tool, failed scan,
unreviewed finding, or unavailable sandbox is an incomplete check, not a pass.
An exclusion requires source evidence, applicability, rationale, owner, and
expiry/recheck trigger. No blanket scanner suppression or automatic dependency fix.

## aud's actual trust boundaries

- Caller-selected source/output directories are intentional local API inputs.
  There is no universal working-directory containment promise. Test containment
  for generated naming trees and archive members; separately test link/reparse
  policy, aliases, protected inputs, late collisions, and staged publication.
- Media, artwork, filenames, tags, configuration, and sidecars may be lower-trust.
  Subprocess arguments must remain separate arguments, with fixed filters and
  local input restrictions. Sidecar references must not be followed implicitly.
- Config is bounded JSON, not pickle/YAML or executable job replay. Check numeric
  overflow, duplicate keys, wrong types, deep nesting, and explicit option presence.
- Native FFmpeg/ffprobe remain external trust dependencies. Use patched builds or
  verified vendor backports. Application timeout/output limits are not hard OS
  memory quotas or a sandbox. See [the security record](SECURITY_REVIEW.md).
- No web/auth/payment service currently exists. Desktop/client/web standards
  supply applicable ideas, not blanket certification requirements for this library.

## Required candidate checks

Use the 22-item evidence template. All applicable checks must be complete; any
accepted residual risk must be explicit in the release decision. Confirmed high/
critical defects block release until fixed and independently rechecked. Scanner
severity alone is not confirmation: review source, affected principal/resource,
conditions, and effect. Lower-priority findings need triage too.

| Area | aud requirement |
| --- | --- |
| Static analysis | Bandit, Semgrep Python security rules, existing CodeQL, Gitleaks history/tree scan, manual findings review. |
| Dependencies | pip-audit over candidate runtime and development/build environments; direct/transitive inventory, licenses/necessity, native decoder inventory; reviewed repeatable resolution. |
| Behavior | Full release suite and coverage on the exact candidate; supported Linux/macOS/Windows and Python 3.10–3.12 matrix; targeted adversarial/parser properties where applicable. |
| Distribution | Wheel and sdist build/metadata validation; explicit archive-content review; fresh installed-artifact tests and import-side-effect checks. |
| Publication | Reviewed tag/version/changelog, protected settings, narrow OIDC job, reviewed pinned actions, evidence/provenance and exact artifact handling. |

CodeQL and Semgrep overlap; review their distinct findings rather than interpreting
agreement as independent proof. Run these heavier scans at candidate/release time,
not after every development edit. Hypothesis/property tests should target actual
parser/naming invariants, with bounded examples and retained seeds for failures.
They supplement existing deterministic conformance cases, not replace them.

## Candidate commands

These commands assume a dedicated candidate environment with reviewed tool versions
installed and the repository root as cwd. Record exact tool and rule versions
before running them. Do not install an unbounded latest toolchain halfway through
validation. Keep reports under ignored `.release-evidence/`; inspect them before
sharing because diagnostics can include paths or candidate secrets.

```text
bandit -r aud -f json -o .release-evidence/bandit.json
semgrep scan --config p/python --error --metrics=off --json --output .release-evidence/semgrep.json aud
gitleaks git --redact --report-format json --report-path .release-evidence/gitleaks-history.json .
gitleaks dir --redact --report-format json --report-path .release-evidence/gitleaks-tree.json aud
python -m pip_audit --format json --output .release-evidence/pip-audit.json
pytest --cov=aud --cov-report=term-missing --cov-report=xml:.release-evidence/coverage.xml
python -m build
python -m twine check dist/*
```

Create the evidence directory first. Run each command separately and preserve its
exit status; a report file is not evidence of success. The wildcard in the twine
command needs shell expansion; on PowerShell use:

```powershell
$artifacts = Get-ChildItem -LiteralPath dist -File | Select-Object -ExpandProperty FullName
python -m twine check $artifacts
if ($LASTEXITCODE -ne 0) { throw 'Distribution metadata validation failed' }
```

The Semgrep registry rule set can change independently of its executable. Retain
the actual rule IDs/config revision or a reviewed local rules snapshot and its
hash for reproducibility; do not claim that `p/python` is an immutable rules pin.
Gitleaks must cover complete Git history, not only a shallow checkout. Also scan
the unpacked candidate distributions in disposable scratch after safe member-path,
type, count, and size checks. Redaction reduces exposure; it is not permission to
publish unreviewed scanner reports. If a real secret is found, revoke/rotate it;
removing the text from a later commit is not sufficient.

These are official tool interfaces, not claims they already ran for this candidate:
[Bandit](https://bandit.readthedocs.io/en/latest/man/bandit.html),
[Semgrep](https://docs.semgrep.dev/cli-reference),
[Gitleaks](https://github.com/gitleaks/gitleaks), and
[pip-audit](https://github.com/pypa/pip-audit).
pip-audit checks known vulnerabilities, not malicious-package absence. Treat
dependency resolution/build hooks as code execution; audit them only in an
appropriate isolated environment when inputs are untrusted.

## Repeatable build and artifact review

1. Use a clean checkout of the reviewed candidate SHA, a dedicated environment,
   and reviewed constraints for the build/test tools and resolved dependencies.
   Keep consumer dependency ranges in `pyproject.toml`; candidate constraints are
   evidence for a specific Python/OS resolution, not a universal library lock.
2. Capture exact resolved versions, sources/hashes, licenses, and tool/native
   versions. Review new maintainers/build hooks and unnecessary dependencies.
   Preserve resolution evidence privately; raw `pip freeze` may reveal local paths.
3. Build wheel and sdist in isolated build environments. Build isolation alone
   is not a security sandbox or a reproducible version pin: build requirements
   such as Hatchling also need reviewed constraints/resolution evidence.
4. List archive members before extraction. Reject traversal/absolute/aliased paths,
   links/special files, unexpected executables, credentials, local inventories,
   caches, and unrelated material. Review `METADATA`/`PKG-INFO`, license, scripts,
   bundled schema, package version, `RECORD`, and correspondence of source/wheel.
5. Create a fresh venv outside the checkout, install the wheel and declared
   dependencies without editable/source fallback, and run `pip check`, CLI/import
   smoke checks, and tests against that installed package. Stage only tests and
   conformance data outside the source tree, verify `aud.__file__` points into the
   venv, and run from that scratch cwd. Do not accidentally test checkout imports.
   Repeat build/install validation from the sdist to expose missing source data.
6. Check imports in an isolated environment for unexpected network, subprocess,
   and filesystem side effects. Exercise malformed native inputs only in the
   verified adversarial runner; do not use scanner/test commands to bypass that
   boundary. Preserve minimum non-secret evidence and artifact SHA-256 digests.

See the [Packaging User Guide](https://packaging.python.org/en/latest/guides/section-build-and-publish/).
Full artifact inspection, installed-release testing, scanner execution, and
property/adversarial tests remain required candidate work; their appearance in
this document does not mark them complete.

## Publishing and final decision

`publish.yml` stays manual. Its build job has read-only permissions; only the
artifact-download/PyPI job receives `id-token: write`. Publishing actions are
pinned to reviewed commit SHAs. The workflow validates tag/version/changelog and
metadata, but does not automatically enforce every checklist item. It rebuilds
at dispatch: compare/revalidate those outputs and their resolution against the
candidate evidence before using this flow; do not assume byte identity.

Before enabling a production release, finish the artifact-review/approval handoff
or reviewed-artifact reuse design so that unchecked rebuilds cannot be published.
This is an open automation gate, not something a checklist alone solves. Keep
ordinary CI/scanners/builds free of publishing tokens. Verify live PyPI publisher
bindings, branch/tag/workflow protections, and any dedicated release environment
separately; repository YAML cannot prove those settings. Attestations are currently
disabled pending provider verification, so record that gap rather than marking
provenance complete. See [PyPI's security model](https://docs.pypi.org/trusted-publishers/security-model/).

Release only after evidence review, applicable gates, and explicit residual-risk
triage on the final candidate. Update SemVer/changelog/project log together and
tag the reviewed release commit. PyPI publication remains the maintainer's
separate action at significant release points. This process does not declare the
current branch a release candidate or authorize a publication.
