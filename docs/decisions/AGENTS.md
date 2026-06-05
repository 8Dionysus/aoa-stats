# AGENTS.md

## Guidance for `docs/decisions/`

`docs/decisions/` is the durable decision-rationale lane for `aoa-stats`.

Use it when the repository needs to preserve why a derived-observability
boundary, receipt-intake rule, summary-strength model, generated read model,
live-source registry posture, MCP posture, validator guard, or consumer
regrounding route was chosen.

Do not use this lane for source-authored meaning, proof verdicts, live runtime
logs, generated summary payloads, private evidence, broad planning notes,
mutable status tracking, route dispatch, memory promotion, or quest-state
truth. `aoa-stats` describes movement from owner-linked evidence; it does not
become the owner of that movement.

## Record Law

- Decision files use full canonical filenames:
  `AOST-D-####-short-slug.md`.
- Each decision has an `## Index Metadata` block with:
  `Decision ID`, `Original date`, `Surface classes`, `Stats surfaces`,
  `Source lanes`, `Guard families`, and `Posture`.
- Decision IDs are stable handles. Historical date-slug paths belong to git and
  PR history, not to a compatibility lookup layer.
- Generated indexes under `docs/decisions/indexes/` are read models only. Do
  not edit them by hand.
- `modeled_surfaces` in `docs/decisions/indexes/index_contract.yaml` is a
  top-level list of normalized repo-relative paths under `docs/decisions/`; do
  not use it for root non-record Markdown.
- Material changes to rationale should usually add a new decision with explicit
  supersession prose instead of silently rewriting an accepted route.

## Boundary

Decision notes explain why `aoa-stats` chose a route. They are weaker than the
surfaces they describe:

- source-owned receipts and verdicts stay with the source repositories;
- generated stats summaries stay in `generated/`;
- receipt-source registries and seed configs stay in `config/`;
- schema contracts stay in `schemas/`;
- public examples stay in `examples/`;
- build and validation behavior stays in `scripts/`;
- regression evidence stays in `tests/`;
- stats direction stays in `README.md`, `ROADMAP.md`, `docs/BOUNDARIES.md`, and
  `docs/ARCHITECTURE.md`;
- source repositories keep stronger truth for authored technique, skill, eval,
  memory, role, playbook, routing, center, runtime, and Tree of Sophia meaning.

## When To Add A Decision

Add or update a decision record when a change materially affects:

- which owner source `aoa-stats` follows or refuses to absorb;
- whether a derived summary surface may widen;
- receipt ABI, event-kind registry, or live-source admission policy;
- surface-strength, source-coverage, consumer-regrounding, or downstream-canary
  posture;
- MCP, live refresh, generated-output, or validator authority boundaries;
- validation/index policy for durable stats rationale.

Small copy edits, generated-output refreshes, local schema fixes, and routine
test maintenance do not need a decision unless they change one of those routes.

## Verify

Run:

```bash
python scripts/generate_decision_indexes.py --check
python scripts/validate_decision_records.py
```

When decision metadata changes, regenerate first:

```bash
python scripts/generate_decision_indexes.py
```

Also run the owning validator for the changed surface, usually:

```bash
python scripts/validate_nested_agents.py
python scripts/validate_repo.py
python -m pytest -q tests
```
