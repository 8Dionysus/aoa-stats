# AOST-D-0019 Owner-Safe Validation Telemetry Is a Derived Federation Extension

## Index Metadata

- Decision ID: AOST-D-0019
- Original date: 2026-08-21
- Surface classes: stats/measurement-contract, stats/federation, derived-observability, validation
- Stats surfaces: validation telemetry packet, validation telemetry port, coverage baseline
- Source lanes: owner-local validator manifests, owner validation receipts, aoa-stats source inventory
- Guard families: derived-only authority, source coverage, identity binding, missingness, no sufficiency promotion
- Posture: accepted

## Context

The validation-architecture direction needs comparable wall, CPU, RSS, IO,
result, semantic class, candidate/environment identity, cache and receipt
posture, first failure, rerun amplification, and source-coverage observations
before a real cross-owner shadow comparison can be admitted. Current owner
ports contain adjacent domain measurements but no canonical validation
telemetry contract, and several active owners are unavailable in the observed
checkout family.

## Decision

`aoa-stats` adds a versioned validation-telemetry packet to the shared
measurement contract and an optional validation-telemetry declaration to each
owner-local federation port. The packet requires complete candidate and
environment identities, explicit missing/unknown/stale states, portable refs,
and a reference/live posture. The owner still defines the validator, claim,
semantic class, budget, evidence, and acceptance barrier.

The central derived baseline consumes the canonical owner inventory plus
explicitly supplied port and packet inputs. It reports per-owner and per-field
coverage, preserves unavailable owners, and remains reference-only until
owner receipts establish a stronger posture. Port presence, packet counts, or
resource values do not create proof, health, sufficiency, routing authority,
or a whole-family success claim.

## Options Considered

- Reuse generic measurements and infer validation meaning from measurement IDs.
- Centralize a validation graph and its semantic or sufficiency rules in `aoa-stats`.
- Add an owner-declared typed extension plus a deterministic derived coverage baseline.

## Rationale

The generic measurement grammar provides identity and missingness but cannot
bind the validation-specific node/lane fields without encouraging task-local
conventions. A central graph would take authority from owner validators and
would turn absent evidence into a misleadingly complete projection. The
extension keeps the reusable compatibility boundary in `aoa-stats`, while the
explicit-input builder makes current gaps measurable without repository
discovery or invented metrics.

## Consequences

- A later shadow can ingest a stable packet shape and compare admitted fields
  without relying on wall-time proxies alone.
- The current baseline can state exact target, port, telemetry, packet, and
  field coverage even when owner checkouts or receipts are absent.
- Owner repositories must land their own declarations and receipts before
  their telemetry becomes reference/live coverage.
- The baseline remains weaker than owner validator reports, KAG relations,
  proof verdicts, and the master sufficiency decision.

## Source Surfaces

- `stats/measurement-contract/validation-telemetry-packet.schema.json`
- `stats/federation/validation-telemetry-port.schema.json`
- `stats/federation/local-port.schema.json`
- `schemas/validation-telemetry-baseline.schema.json`
- `src/aoa_stats_builder/validation_telemetry.py`
- `scripts/build_validation_telemetry_baseline.py`
- `scripts/validate_stats_protocol.py`
- `stats/source_home.manifest.json`

## Validation

Use [`../../VALIDATION.md`](../../VALIDATION.md), the measurement-contract and
federation route cards, the telemetry focused tests, the source-home and
protocol validators, and the full repository release gate. Generated decision
indexes are rebuilt from this authored note; no generated index is an
authority source.
