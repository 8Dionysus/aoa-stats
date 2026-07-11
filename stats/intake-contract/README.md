# Intake contract

This source family defines the narrow contract by which owner-local facts may
enter stats derivation.

`aoa-stats` owns the shared envelope and event-kind admission table. The
repository named as `payload_owner_repo` owns the meaning and schema of each
event payload. Receipt intake therefore provides a deterministic seam, not a
transfer of domain authority.

## Active route map

| Concern | Current route |
| --- | --- |
| Receipt admission law | `stats/intake-contract/RECEIPT_ABI.md` |
| Derived-only boundary | `docs/BOUNDARIES.md` |
| Canonical envelope | `schemas/stats-event-envelope.schema.json` |
| Active event kinds | `stats/intake-contract/event-kind-registry.json` |
| Bounded build fixture | `stats/intake-contract/examples/session_harvest_family.receipts.example.json` |
| Registered live sources | `mechanics/recurrence/parts/live-receipt-refresh/config/live_receipt_sources.json` |
| Receipt loading and ABI checks | `src/aoa_stats_builder/receipt_abi.py` |
| Public build entry | `scripts/build_views.py` |
| Live refresh entry | `scripts/refresh_live_stats.py` |
| Publisher audit | `scripts/check_live_publishers.py` |
| ABI validator | `scripts/validate_receipt_abi.py` |

The read-only repo-local MCP can expose the current live-source registry, but
that access route does not own or alter the intake contract.

## Operation crosswalk

- repeatable refresh: `mechanics/recurrence/parts/live-receipt-refresh`
- cross-repo envelope and mirror seam:
  `mechanics/boundary-bridge/parts/receipt-abi-crossing`

The authoritative machine-readable mapping is
`stats/source_home.manifest.json`.
