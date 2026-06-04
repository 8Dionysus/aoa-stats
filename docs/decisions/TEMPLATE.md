# AOST-D-#### Short Decision Title

## Index Metadata

- Decision ID: AOST-D-####
- Original date: YYYY-MM-DD
- Surface classes: docs/model
- Stats surfaces: derived summary
- Source lanes: none
- Guard families: derived-only authority
- Posture: proposed

## Context

What stats pressure made the decision necessary?

Name the generated, config, schema, example, script, test, docs, MCP, live
refresh, or upstream source-owner surfaces that shaped the choice.

## Decision

State the chosen route in one or two paragraphs.

## Options Considered

- Option A:
- Option B:
- Option C:

## Rationale

Explain why this route fits `aoa-stats` as a derived observability layer where
source repositories own meaning and stats owns bounded read models.

## Consequences

Name what becomes easier, what remains constrained, and what future
contributors must not infer from this decision.

## Source Surfaces

- `AGENTS.md`
- `README.md`
- `ROADMAP.md`
- `docs/BOUNDARIES.md`
- `docs/ARCHITECTURE.md`
- `docs/README.md`

## Validation

Run:

```bash
python scripts/generate_decision_indexes.py
python scripts/generate_decision_indexes.py --check
python scripts/validate_decision_records.py
```

Also run the validator for the owning surface the decision describes.
