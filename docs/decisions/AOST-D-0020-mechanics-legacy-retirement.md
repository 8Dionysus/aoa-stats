# AOST-D-0020 Mechanics Legacy Retirement

## Decision

On 2026-09-04, `mechanics/agon/legacy/` is retired after moving its former
route mapping to `mechanics/agon/former-routes.json`. Active part routes remain
the sole current source. Former content is recoverable from baseline commit
`7363480775555021f300362d0ead4d41de1826f0` and immutable Git history.

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
