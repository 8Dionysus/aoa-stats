# Rollout Campaign contract

## Exact input context

The committed adapter reads exactly:

- `8Dionysus/examples/rollout_campaign_window.example.json`
- `8Dionysus/examples/drift_review_window.example.json`
- `8Dionysus/examples/rollback_followthrough_window.example.json`

These files form an owner-authored reference example chain. They are not live
cadence state and are not the checked-in trusted rollout history bundle.

## Operation boundary

- `rollout_cadence_sources.py` owns exact path selection, JSON I/O, immutable
  bundle construction, and example provenance
- filesystem-free `rollout_cadence.py` validates the three-example chain and
  projects the campaign summary
- `scripts/build_views.py` retains owner-root resolution, mutable tuple and
  zero-argument compatibility calls, and repo-wide fan-out only
- `drift-shadow-review` owns the separate drift-review projection

## Invariants

- every example keeps its exact published v1 required fields, enums, reference
  grammar, booleans, and parseable timestamp
- review and rollback point to the loaded campaign
- latest and stable rollout refs belong to the campaign's rollout ref set
- both rollback anchors point to the campaign's stable rollout ref
- at least one explicit drift signal is positive
- decision/status and ready-if-needed/post-review combinations are coherent
- campaign, review, and rollback timestamps remain ordered inside the example
  flow

This bounded chain does not prove that its rollout refs still equal the current
`8Dionysus/generated/codex/rollout/rollout_latest.min.json`; owner validation is
the authority for that wider history-to-cadence relationship.

## Authority and live boundary

The result is weaker than owner cadence and review decisions. Its authored
profile is reference-only; local live refresh omits it and cleans stale managed
copies. It never becomes proof, routing, gate, identity, cadence, campaign,
rollout, or rollback truth.
