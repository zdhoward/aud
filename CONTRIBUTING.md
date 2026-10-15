# Contributing to aud

Thanks for helping. This document covers dev setup, the project's commit and
release discipline, and how issues are triaged.

## Development setup

```
pip install -e .[dev]
```

ffmpeg must be on `PATH` for audio operations and the test suite.
The conversion tests also require `ffprobe`, `libmp3lame`, and `libvorbis`; see
[the FFmpeg setup contract](docs/FFMPEG_CONVERSION.md). macOS CI selects
Homebrew's `ffmpeg-full` binaries explicitly.

```
pytest tests/test_names.py   # example: targeted development check
pytest --cov=aud            # full suite and coverage before a release
black --check . && ruff check . && mypy aud   # lint gates (same as CI)
```

Pre-commit hooks (formatting, line endings, lint) run on every commit:

```
pre-commit install
```

During development, test the behavior changed since the last passing check.
Include affected callers or integrations when shared code changes, and broaden
the scope only when failures or unresolved concerns justify it. Do not repeatedly
run the full suite or coverage after every edit. Run the complete suite and release
checks before a new release. CI may continue to run its configured full matrix.
Apply the same scope discipline to local formatting and lint checks.

Line endings are LF everywhere (`.gitattributes` normalizes; the pre-commit
`mixed-line-ending --fix=lf` hook enforces).

## Commit and release discipline

aud is a public open-source project. Develop on descriptive feature, fix, or
documentation branches and submit pull requests against `master`. Do not push
development commits directly to `master` or rewrite shared history. Stacked work
must name its prerequisite branch/PR and keep each review focused.

Update the API reference, examples, architecture notes, and changelog whenever
their documented behavior changes. Use repository-relative links in public docs;
keep local environment inventories and audit scratch evidence outside the repo.

aud is deliberately conservative about history and versions:

* **Commits:** one logical unit per commit, imperative subject line, body with
  the "why". Never mix unrelated changes into a commit. Version bumps never
  ride along with feature work.
* **Versions:** use Semantic Versioning for reviewed milestones or hotfixes.
  Prepare a dedicated release change, run the full release checks, and tag its
  merged commit with an annotated `vMAJOR.MINOR.PATCH` tag. The version declarations,
  changelog, tag, and GitHub release notes must agree. Do not tag intermediate work.
* **PyPI:** publication is a separate maintainer-controlled action at significant
  release points. A tag must not automatically publish. The optional manually
  dispatched `publish.yml` validates an existing release tag before building and
  publishing it; the maintainer decides whether and when to run that flow.
* **Behavior changes:** any change to what an existing call does (not just
  what it accepts) must ship with a `DeprecationWarning` window when feasible,
  a CHANGELOG entry under **Changed**, and regression tests. Example: the
  2.0.2 `bit_rate` semantics change should have carried a runtime warning; it
  did not, which is the policy's origin.

## Issue guidelines

### Filing

* **Bug**: the code behaves incorrectly. Include a minimal reproduction,
  your OS, Python and ffmpeg versions, and the aud version.
* **Feature request**: a proposal for new or changed capability. State the
  *context that backs the argument*: the concrete use case, what today's
  workaround costs, and why it belongs in aud rather than downstream.
  Subjective proposals are welcome, but the argument has to be written down.
  Note any design questions or open decisions explicitly.
* Don't pre-assign milestones when filing; the maintainer triages.

### Labels

Every issue carries exactly one **priority** label:

| Priority label | Meaning |
|---|---|
| `high priority` | Data safety, security, or release-blocking. |
| `medium priority` | Planned core work inside a milestone. |
| `low priority` | Real but unscheduled; fine to sit. |

Category labels:

| Label | Meaning |
|---|---|
| `bug` | Incorrect behavior. Data-loss/safety bugs jump the queue. |
| `enhancement` | New capability or improvement to existing behavior. |
| `security` | Security-relevant hardening or findings. |
| `documentation` | Docs work; must not drift from code behavior. |
| `chore` | Tooling, CI, packaging, refactors with no behavior change. |
| `good first issue`, `beginner` | Self-contained, documented starting points. |
| `help wanted` | Wanted contributions from outside. |
| `dependencies`, `github_actions` | Set automatically by Dependabot. |
| `question`, `duplicate`, `invalid`, `wontfix` | Standard triage outcomes. |

### Milestones

* Bugs and accepted features get a version milestone (`v2.x.0`).
* Housekeeping may stay milestone-less until it's slotted.
* A milestone ships after its scoped issues and release checks complete. Version,
  tag, and GitHub release stay aligned; PyPI publication remains a separate decision.

## Automation

| Workflow | Trigger | What it does |
|---|---|---|
| `ci.yml` | main/master push, all PR bases | lint (black, ruff, mypy); test matrix Linux + macOS + Windows, Python 3.10-3.12; coverage gate at 85% with artifact upload |
| `codeql.yml` | main/master push, all PR bases, weekly | Python security scanning, including stacked PRs |
| `publish.yml` | maintainer manual dispatch | validates an existing release tag/version/changelog, builds, `twine check`, and publishes to PyPI via trusted publishing |
| Dependabot | weekly | pip and github-actions updates, PRs with full CI |

## Writing style

Documentation, issues, commit messages, and release notes are written in
plain punctuation: no em dashes. Use a comma, a colon, parentheses, or a new
sentence instead. Keep prose direct; avoid filler and template-sounding
phrasing. Code comments describe behavior, not reasoning.

## Pull requests

* Tests for changed behavior; affected tests and relevant lint checks pass locally.
  A full local suite is required before a release, not for every development change.
* CHANGELOG entry for anything user-facing.
* Don't bump versions in a PR unless the PR *is* the release.
