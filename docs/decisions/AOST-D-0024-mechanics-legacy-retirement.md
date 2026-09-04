# AOST-D-0024 Mechanics Legacy Retirement

## Index Metadata

- Decision ID: AOST-D-0024
- Original date: 2026-09-04
- Surface classes: mechanics/provenance, stats topology, archive retirement
- Stats surfaces: mechanics topology, former-route mapping, recurrence manifests
- Source lanes: stats mechanics source, recurrence component manifests, owner validators
- Guard families: active-route authority, historical recovery, former-name rejection, generated parity
- Posture: accepted

## Decision

On 2026-09-04, `mechanics/agon/legacy/` is retired after moving its former
route mapping to `mechanics/agon/former-routes.json`. Active part routes remain
the sole current source. Former content is recoverable from baseline commit
`7363480775555021f300362d0ead4d41de1826f0` and immutable Git history.

## Baseline historical links

Baseline commit: [`7363480775555021f300362d0ead4d41de1826f0`](https://github.com/8Dionysus/aoa-stats/commit/7363480775555021f300362d0ead4d41de1826f0).

| Retired root | Baseline tree | Full historical tree link |
| --- | --- | --- |
| `mechanics/agon/legacy/` | `bce34caafca28d6ba3a8be5ef9e5b446d1730bd7` | [tree](https://github.com/8Dionysus/aoa-stats/tree/7363480775555021f300362d0ead4d41de1826f0/mechanics/agon/legacy) |

The root is retired because its payload is archive-only and its former-route
map preserves active replacement and old-name rejection semantics. Recovery is
by this immutable commit/tree link or the exact path/blob inventory in
`surface-retirement-20260904/baseline.json`.

## Boundary

The mapping retains old-name rejection and active replacement semantics. Raw
wave/quest files are archive-only and are removed; recurrence manifests retain
immutable historical GitHub references. No stats measurement or behavioral
contract changes are made.

## Recovery

The complete path/blob baseline is recorded in
`surface-retirement-20260904/baseline.json`; every targeted blob was verified
recoverable before removal. No `.aoa`, host, runtime, remote, tag, PR, or merge
surface is part of this decision.
