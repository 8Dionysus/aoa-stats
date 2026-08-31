# `aoa-stats` validation routes

This is the on-demand human procedure surface for repository validation. It is
opened after the touched source, profile, operation, mechanic, or route-card
surface is known. Inherited `AGENTS.md` cards name the applicable owner and
stop-lines; they do not carry executable command batteries.

## Authority and procedure owners

| Concern | Procedure owner |
| --- | --- |
| complete repository gate | `scripts/release_check.py` and this route |
| decision-index parity | `scripts/generate_decision_indexes.py` and `scripts/validate_decision_records.py` |
| nested route-card coverage and structural guards | `scripts/validate_nested_agents.py` |
| source-family membership and reciprocal ownership | `scripts/validate_stats_source_home.py` |
| operation placement and focused-proof placement | `scripts/validate_mechanics_topology.py` |
| shared statistical and receipt compatibility | `scripts/validate_stats_protocol.py` and `scripts/validate_receipt_abi.py` |
| generated projection parity | `scripts/build_views.py --check` and the declared builders |
| focused operation behavior | the nearest mechanic-part `VALIDATION.md` |
| live publisher presence | `mechanics/recurrence/parts/live-receipt-refresh/VALIDATION.md` and its operator guide |
| release, CI, review, and merge procedure | `docs/RELEASING.md` and the observed GitHub owner surface |
| stats-layer eval-port procedure | the stronger `aoa-evals` owner; this repository does not copy its command |

The source manifest remains the authority for stats-family membership and
`mechanics/topology.json` remains the authority for operation placement and
focused-proof ownership. A successful check is evidence for its declared
contract only; it does not prove owner truth, proof sufficiency, runtime
freshness, CI, review, merge, or Goal completion.

## Route-card and source-home changes

Use this focused sequence when changing `AGENTS.md`, `DESIGN.AGENTS.md`, a
README route, a source-home card, or a route validator. Keep the order unless
the touched surface has a narrower owner check.

When decision metadata changes, regenerate the authored indexes before this
check sequence:

```bash
python scripts/generate_decision_indexes.py
```

```bash
python scripts/generate_decision_indexes.py --check
python scripts/validate_decision_records.py
python scripts/validate_nested_agents.py --fail-on-untracked
python scripts/validate_mechanics_topology.py
python scripts/validate_stats_source_home.py
python scripts/validate_stats_protocol.py
python scripts/build_views.py --check
python -m pytest -q tests/test_docs_routes.py tests/test_validate_nested_agents.py tests/test_roadmap_parity.py
python -m pytest -q tests/test_stats_source_home.py tests/test_mechanics_topology.py
git diff --check
```

The route-card checks must report zero active executable fences, runnable
command lines, unconditional README inventories, empty procedural sections,
and extraction orphan lead-ins. They must still report every topology-owned
card and every owner-specific semantic snippet.

## Focused owner routes

For a source, profile, operation, or mechanic change, select the nearest
part-local `VALIDATION.md` named by `mechanics/topology.json` and run its exact
procedure. Part-local validation owns the ordered command sequence and its
negative cases; do not recreate that sequence in an inherited card. For a
schema or shared protocol change, add the matching protocol or receipt-ABI
route from the procedure-owner table and preserve source-first regeneration.

For a shared receipt-ABI change, include this focused owner check:

```bash
python scripts/validate_receipt_abi.py
```

For live-intake changes, use the live-refresh validation and operator guide.
Current publisher availability, receipt freshness, and derived projection
freshness remain separate claims; fixture tests and a recent artifact
modification time do not establish them.

## Complete owner-local gate

Run the complete ordered gate only when release readiness, a broad repository
change, or the task scope explicitly requires it:

```bash
python scripts/release_check.py
```

The ordered `COMMANDS` list in `scripts/release_check.py` is the complete
machine gate. This document routes to it but does not replace or expand its
authority. `docs/RELEASING.md` owns publication sequencing, CI, review, merge,
tag, and post-landing claims.

## Checkpoint review

For a bounded change, capture the exact commit or working-tree checkpoint,
changed paths, checks actually run, unresolved blockers, and the remaining
owner, runtime, freshness, CI, review, merge, and acceptance boundaries. Review
the checkpoint against the declared source and generated surfaces before
handoff. A checkpoint is review evidence, not proof of owner truth, release
admission, runtime currentness, or Goal completion.

## Closeout

Report the selected owner surface, exact procedures actually run, focused and
full results, skipped or unavailable external checks, source/generated
projections touched, and the remaining owner, runtime, freshness, CI, review,
merge, or acceptance boundary. Keep no-push, no-PR, no-merge, and no-Goal-
completion claims explicit when those actions were not authorized or observed.
