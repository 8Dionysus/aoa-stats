# AOST-D-0014 - Routing Owner Succession

## Index Metadata

- Decision ID: AOST-D-0014
- Original date: 2026-07-27
- Surface classes: stats/federation, stats/operation-contracts, stats/read-models, mechanics/antifragility, mechanics/boundary-bridge, src/canaries, scripts/release
- Stats surfaces: owner inventory, operation owner returns, Stress Recovery Window, surface catalog, downstream canaries
- Source lanes: aoa-sdk routing control plane, historical aoa-routing provenance, aoa-evals stress-recovery report
- Guard families: derived-only authority, owner succession, consumer regrounding, downstream canaries, no predecessor checkout
- Posture: accepted

## Context

The routing producer and control-plane owner moved from the predecessor
`aoa-routing` repository into `aoa-sdk` while retaining `aoa-routing` as the
stable artifact namespace and runtime layer name. `aoa-stats` still carried the
predecessor as an active federation owner, release dependency, downstream
canary, symbolic operation owner, and current Stress Recovery fixture source.
Those links would keep the old checkout operationally necessary even though
the stronger owner had moved.

## Decision

Current stats-authored owner returns, canaries, release discovery, federation
coverage, and routing-hint fixtures point to `aoa-sdk`. The Stress Recovery
surface uses the SDK-owned bounded compatibility witness rather than copying
or retaining the predecessor's producer tree.

The stable `aoa-routing` compatibility name and historical repository
references remain valid ABI and provenance. Accepted historical decisions and
retired tombstones are not rewritten. Removing the predecessor from the active
owner inventory is not archive authorization; archival still requires
consumer-zero proof, the compatibility window, and explicit operator approval.

## Options Considered

- Keep both repositories as active owners: preserves a duplicate port and
  checkout requirement after authority has moved.
- Rewrite every historical `aoa-routing` reference: destroys provenance and
  confuses stable compatibility identity with current source ownership.
- Return only current consumers to `aoa-sdk`: removes the operational
  dependency while preserving historical and ABI identity.

## Rationale

`aoa-stats` must follow the current stronger owner without absorbing routing
meaning. One SDK owner route and one bounded compatibility witness keep the
derived layer smaller, make release checks independent of the predecessor
checkout, and preserve explicit authority ceilings. Historical references do
not become active dependencies merely because they remain inspectable.

## Consequences

- The active federation inventory no longer counts `aoa-routing` as a current
  owner; the existing `aoa-sdk` port carries current routing-owner pressure.
- Release and downstream-canary checks no longer discover or read an
  `aoa-routing` checkout.
- Symbolic Agon and Experience operation contracts return to the SDK routing
  contract and remain unbound rather than claiming live state.
- Stress Recovery examples and generated output preserve their derived-only
  posture while citing the SDK compatibility witness.
- The stable artifact namespace, historical decisions, and predecessor Git
  history remain valid and do not imply current producer authority.

## Source Surfaces

- `stats/federation/owner-inventory.json`
- `stats/source_home.manifest.json`
- `stats/operation-contracts/active/agon.stats-prebinding.operation.json`
- `stats/operation-contracts/active/experience.adoption-federation-harvest.operation.json`
- `stats/read-models/active/surface_detection_summary.profile.json`
- `stats/surface-catalog/CONSUMER_REGROUNDING.md`
- `mechanics/antifragility/parts/stress-recovery-windows/`
- `src/aoa_stats_builder/downstream_canaries.py`
- `scripts/release_check.py`
- `aoa-sdk:mechanics/boundary-bridge/parts/consumed-surface-posture-gate/docs/routing-consumer-contract.md`

## Validation

Validation follows [`../../VALIDATION.md`](../../VALIDATION.md), the federation
and operation-contract route cards, the Stress Recovery
[`VALIDATION.md`](../../mechanics/antifragility/parts/stress-recovery-windows/VALIDATION.md),
and the consumer-regrounding
[`VALIDATION.md`](../../mechanics/boundary-bridge/parts/consumer-regrounding/VALIDATION.md).
