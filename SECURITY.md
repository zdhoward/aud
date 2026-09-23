# Security Policy

## Supported versions

Only the latest released version receives security fixes. See
[CHANGELOG.md](CHANGELOG.md) for the current release.

## Reporting a vulnerability

Use GitHub's **private vulnerability reporting**: Security tab →
"Report a vulnerability". Please do not open public issues for
suspected vulnerabilities.

Include a reproduction, affected versions, and impact assessment where
possible. Reports are acknowledged as soon as practical; fixes ship as
patch releases under the project's release discipline.

## Hardening context

Known safety-critical areas are tracked with the `security` label —
historically: silent overwrite behavior in rename/copy/move, symlink
handling in the directory scanner, and unguarded user-supplied regex.
See the issues tracker for current status.
