# HANDOFF — aud

Minimal handoff created 2026-09-27 during the system-resync sweep (per Zach) — this repo had no agent docs. /init has not run here yet; it will merge with (never overwrite) this file when a focused session runs it.

## System resync

This repo runs under Zach's universal agent system. Canonical resync/reinit/migration procedure: `S:\ZX\Programming\Global-Project-Management\agent-system\RESYNC.md` (in the GPM repo — on a new machine, clone `zdhoward/Global-Project-Management` first).

- Session start: run /sync. Session end ("wrap up"): run /finish.
- Docs drifted or re-onboarding: run /init — migration-aware, never overwrites existing state.
- Public project policy: work on feature/fix/docs branches and use PRs against
  `master`. Do not push development changes directly to the default branch.
  Release tags follow reviewed milestones; PyPI publication is maintainer-controlled.

Migration notes (this repo):
- Remote: `zdhoward/aud`. Python package — environment specifics live in the code; consult the README before assuming a toolchain.

## Current state
Safe-processing work is preserved on `feat/safe-processing`; local `master` tracks
the published default branch. See ROADMAP.md and PROJECT_LOG.md for current progress.
