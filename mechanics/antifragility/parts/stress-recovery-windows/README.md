# stress-recovery-windows

Derives a bounded Stress Recovery projection from stronger eval and owner
evidence without becoming a proof or recovery authority.

The implementation is split between:

- the filesystem-free projection core at
  `src/aoa_stats_builder/stress_recovery.py`
- the exact `repo:aoa-evals/...` source adapter at
  `src/aoa_stats_builder/stress_recovery_sources.py`
- focused projection and adapter tests under this part's `tests/` district

The current profile is an active public contract but a false-live committed
draft/example surface. Its committed receipt names the current mechanic-owned
`aoa-evals` report path, and the source adapter resolves that exact ref without
translation or fallback.

Read `CONTRACT.md` for the local stop-lines,
`docs/STRESS_RECOVERY_WINDOW_SUMMARIES.md` for the detailed source posture, and
`VALIDATION.md` for executable checks. Live activation is governed by
`docs/decisions/AOST-D-0004-live-admission-requires-refresh-observation.md`.
