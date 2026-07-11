# Runtime Closeout contract

## Owner chain

- `Agents-of-Abyss/mechanics/checkpoint` owns closeout vocabulary, review law,
  owner handoff, and authority stop-lines.
- `abyss-stack` owns runtime trials, gate results, truth posture, and closeout
  receipt publication.
- `aoa-sdk` owns reviewed-closeout packet, queue, and handoff transport.
- `stats/read-models/active/runtime_closeout_summary.profile.json` owns only
  the bounded stats question, evidence posture, public routes, and authority
  ceiling. This part owns the repeatable compatibility projection.

## Historical projection input

The core admits exactly `runtime_wave_closeout_receipt`. It groups receipts by
the payload `program_id` plus `wave_id` when both are non-empty strings. If
either is unavailable, it splits the `object_ref.id` at the final colon; if no
colon exists, it uses `unknown-program` plus `session_ref`.

For each sorted identity it counts gate and reviewed-handoff values, selects
the latest receipt by `(observed_at, event_id)`, projects the four truth-status
booleans, copies bounded latest fields, and counts evidence refs. Missing or
falsey gate and handoff values become `unknown`; a missing next action becomes
`unspecified`.

The historical implementation retains two compatibility behaviors: the
reported `first_observed_at` is the first matching input rather than a sorted
minimum, and `case_count` uses Python integer coercion. Changing either is a
separate behavioral cycle with owner payload and public-schema review.

## Current owner mismatch

At tracked `abyss-stack@f41621e`, the active local-trials producer emits
`runtime_trial_closeout_receipt` to `runtime-trial-closeouts.jsonl`. The stats
compatibility event ABI still admits historical `runtime_wave_closeout_receipt`,
but the active source registry no longer reads its
`runtime-wave-closeouts.jsonl` feed. The abyss-stack watcher snapshot still
names that old path. At the 2026-07-11 audit, the installed service also
launched an older `/srv/AbyssOS/aoa-stats` projection whose registry admitted
the feed, so this repo change does not certify the deployed plane. That plane
needs a symlink-safe abyss-stack/deploy handoff rather than an installer
overwrite from this checkout. The SDK also has a distinct A2A
`runtime_return_closeout_receipt`. These names represent different owner
contracts and must not be silently merged.

Runtime Closeout is therefore `live_state_capable: false`. Live refresh omits
the builder and cleans stale runtime copies. Re-activation requires an explicit
cross-owner agreement for the canonical receipt family, stats ABI registration,
a matching real feed, a watcher that observes it, and proof from a current
receipt.

## Authority and compatibility

- The result is derived observation, never proof, routing, gate, identity, or
  workflow truth.
- Input receipts and the supplied `generated_from` object are not mutated.
- `scripts/build_views.py` retains historical function names as compatibility
  aliases and owns repo-wide fan-out only.
- Public schema and output paths remain stable.
- Every localized and retained route is declared in `mechanics/topology.json`
  and linked from `stats/read-models/`.
