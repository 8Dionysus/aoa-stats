# AOST-D-0020 Codex Reference Builds Require Exact Owner Snapshots

## Index Metadata

- Decision ID: AOST-D-0020
- Original date: 2026-08-23
- Surface classes: stats/read-models, generated-read-model, validation, release-support
- Stats surfaces: Codex Plane deployment summary
- Source lanes: 8Dionysus owner examples, aoa-stats source adapter, release validation workflow
- Guard families: source currentness, generated-output parity, derived-only authority
- Posture: accepted

## Context

The published `aoa-stats` v0.2.1 Codex Plane summary was built from an exact
`8Dionysus` owner snapshot, but a zero-configuration local build selected a
dirty divergent sibling checkout. That checkout carried a different stable MCP
name variant and made `build_views.py --check` report a generated-view drift
even though the committed bytes matched the pinned CI dependency. A generated
reader edit or a weakened check would hide the source-selection defect.

## Decision

The Codex Plane reference source adapter pins the owner snapshot to
`8Dionysus@3baafa395906e93dee23a9479ef4f9aed576bd8a` and admits only a clean
Git checkout at that exact revision. The root build facade applies this check
before the Codex Plane and related 8Dionysus reference views are loaded. Missing,
dirty, or differently revised roots fail closed; explicit CI and release
dependency roots remain the reproducible route.

The generated Codex Plane JSON remains builder-owned and unchanged. A later
owner-input refresh must update the source pin and validation dependency
together, regenerate through the builder, and rerun the complete release gate.

## Options Considered

- Regenerate the committed JSON from the ambient dirty checkout.
- Suppress or weaken `build_views.py --check` for this optional view.
- Pin and authenticate the owner snapshot in the source adapter, then fail closed.

## Rationale

The third route preserves the stronger owner/source boundary and makes a
currentness failure observable instead of converting it into a misleading
generated-byte diff. A clean exact checkout is sufficient to reproduce the
published reference chain without making `aoa-stats` responsible for upstream
owner meaning or live deployment state.

## Consequences

- Local reference builds must use the exact clean dependency checkout; ambient
  dirty workspace state is never an implicit input.
- CI's existing dependency pin is checked against the source adapter pin.
- The committed summary stays a derived reference view and does not become
  rollout, trust, proof, workflow, or owner-acceptance authority.
- Upstream example movement requires an explicit pin, builder, validation, and
  release review rather than silent fallback.

## Source Surfaces

- `src/aoa_stats_builder/codex_plane_deployment_sources.py`
- `scripts/build_views.py`
- `.github/workflows/validate.yml`
- `mechanics/release-support/parts/codex-deployment-rollout/CONTRACT.md`
- `mechanics/release-support/parts/codex-deployment-rollout/tests/test_codex_plane_deployment_projection.py`
- `stats/read-models/active/codex_plane_deployment_summary.profile.json`

## Validation

Use [`AGENTS.md#verify`](AGENTS.md#verify), the Codex Plane
[`VALIDATION.md`](../../mechanics/release-support/parts/codex-deployment-rollout/VALIDATION.md),
the source-home and mechanics validators, the decision-index checks, and the
full repository release gate against the pinned dependency roots.
