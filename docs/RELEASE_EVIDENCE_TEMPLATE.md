# aud release-candidate security evidence

Copy this template into private candidate evidence. All items start incomplete.
Do not copy historical development results as current candidate passes.

- Candidate version / full commit SHA:
- Review date / reviewer:
- Supported-platform CI and CodeQL run URLs for this exact commit:
- Python/OS/native-tool versions and vendor patch/backport evidence:
- Reviewed scanner/tool/rule versions and constraints/resolution evidence:
- Wheel/sdist names, SHA-256 hashes, build run, and inspection evidence:
- Findings: status, source/effect, remediation or accepted risk, owner/recheck date:
- Unavailable checks / blockers:
- Final decision: **not approved** until all applicable gates and evidence review:

For each item retain command, exit code, evidence location, result, and reviewer.
Use `not applicable` only with a specific capability/scope rationale.

## Static analysis

- [ ] 01 Bandit source scan, every finding triaged.
- [ ] 02 Semgrep Python security scan, actual rule snapshot/revision retained.
- [ ] 03 Gitleaks full history, working tree, and artifact-content secret scans.
- [ ] 04 Manual findings review, exclusions justified and confirmed high/critical defects fixed/rechecked.

## Dependencies and build supply chain

- [ ] 05 pip-audit runtime and dev/build resolutions, advisories triaged.
- [ ] 06 Direct/transitive inventory, licenses, necessity, maintainers/build hooks, native tools reviewed.
- [ ] 07 Reviewed candidate constraints/resolution and artifact sources/hashes retained.
- [ ] 08 Clean build environment and isolation controls verified for the actual inputs.

## Functional and adversarial checks

- [ ] 09 Full candidate regression/conformance suite passes.
- [ ] 10 Coverage reviewed for critical boundaries, not treated as security proof.
- [ ] 11 Empty/oversized/malformed/wrong-type/deeply nested inputs checked where applicable.
- [ ] 12 Generated-name/archive traversal, aliases, links/reparse points, protected inputs, and publication races checked.
- [ ] 13 Subprocess/filter/metadata injection boundaries checked with intended argument structure intact.
- [ ] 14 Deserialization/config stays non-executable and bounded; no hidden replay/import path.
- [ ] 15 Bounded parser/naming properties/fuzz cases and applicable native decoder cases run with verified isolation.

## Distribution and publication

- [ ] 16 Wheel and sdist build successfully from the reviewed candidate.
- [ ] 17 Metadata, version, entry points, source/wheel consistency and RECORD validated.
- [ ] 18 Archive contents inspected; no secrets, machine inventories, unrelated data, or unexpected executable payloads.
- [ ] 19 Clean wheel and sdist installation/tests/import-side-effect checks use installed code, not checkout fallback.
- [ ] 20 Claimed Python 3.10–3.12 and Linux/macOS/Windows support verified.
- [ ] 21 OIDC scope, live publisher bindings, workflow/environment protections and artifact handoff verified.
- [ ] 22 Release provenance/attestations, tag protections, exact reviewed artifacts and final publication decision verified.

Use [the aud-specific gate](RELEASE_SECURITY.md) for commands, trust boundaries,
evidence requirements, and distinctions between ordinary regression and adversarial
native execution. No scanner combination certifies security.
