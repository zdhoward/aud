# Contributing to aud

Thanks for helping. This document covers dev setup, the project's commit and
release discipline, and how issues are triaged.

## Development setup

```
pip install -e .[dev]
```

ffmpeg must be on `PATH` for audio operations and the test suite.

```
pytest                      # fast run
pytest --cov=aud            # with coverage (85% gate)
black --check . && ruff check . && mypy aud   # lint gates (same as CI)
```

Pre-commit hooks (formatting, line endings, lint) run on every commit:

```
pre-commit install
```

Line endings are LF everywhere (`.gitattributes` normalizes; the pre-commit
`mixed-line-ending --fix=lf` hook enforces).

## Commit and release discipline

aud is deliberately conservative about history and versions:

* **Commits:** one logical unit per commit, imperative subject line, body with
  the "why". Never mix unrelated changes into a commit. Version bumps never
  ride along with feature work.
* **Versions:** numbers change only at planned milestones or hotfixes. The
  bump lives in the same commit that is tagged. The tag, the GitHub release,
  and the PyPI publish happen in the same session.
* **Behavior changes:** any change to what an existing call does (not just
  what it accepts) must ship with a `DeprecationWarning` window when feasible,
  a CHANGELOG entry under **Changed**, and regression tests. Example: the
  2.0.2 `bit_rate` semantics change should have carried a runtime warning —
  it did not, which is the policy's origin.

## Issue guidelines

### Filing

* **Bug** — the code behaves incorrectly. Include a minimal reproduction,
  your OS, Python and ffmpeg versions, and the aud version.
* **Feature request** — a proposal for new or changed capability. State the
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
* A milestone ships when its issues close; the version bump, tag, release,
  and publish then happen together.

## Pull requests

* Tests for changed behavior; `pytest` and the lint gates pass locally.
* CHANGELOG entry for anything user-facing.
* Don't bump versions in a PR unless the PR *is* the release.
