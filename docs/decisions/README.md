# Decision Records Index

This directory is the durable decision surface for `aoa-stats`.

Use it when a future contributor needs the rationale for a derived-observability
boundary, receipt-intake rule, summary-strength model, generated read model,
live-source registry posture, MCP posture, validator guard, or consumer
regrounding route.

Ordinary implementation notes, generated output, runtime logs, private
evidence, proof verdicts, source-authored meaning, mutable status, and one-off
planning thoughts route to their owning surfaces instead.

## Operating Card

| Field | Route |
| --- | --- |
| role | durable stats decision rationale entrypoint and index chooser |
| input | changed derived boundary, receipt intake, summary strength, generated read model, live-source registry, MCP posture, validation guard, or consumer-regrounding pressure |
| output | canonical decision note, generated lookup indexes, and route back to the owning stats surface or upstream source owner |
| owner | `docs/decisions/AGENTS.md` for lane law; decision notes for rationale; generated indexes for lookup only |
| next route | owning generated/schema/config/example/script/test surface first, then nearest route card, `README.md`, `ROADMAP.md`, `docs/BOUNDARIES.md`, `docs/ARCHITECTURE.md`, generated lookup indexes, or the affected source owner |
| validation | `python scripts/generate_decision_indexes.py --check` and `python scripts/validate_decision_records.py`, plus the owning validator for the changed surface |

## Authority

Decision notes explain why a stats route was chosen.

They are weaker than the source surface they describe:

- source-owned receipts and verdicts stay with the source repositories;
- generated stats summaries stay in `generated/`;
- receipt-source registries and seed configs stay in `config/`;
- schema contracts stay in `schemas/`;
- public examples stay in `examples/`;
- build and validation behavior stays in `scripts/`;
- regression proof stays in `tests/`;
- stats direction stays in `README.md`, `ROADMAP.md`, `docs/BOUNDARIES.md`, and
  `docs/ARCHITECTURE.md`;
- source repositories keep stronger truth for authored technique, skill, eval,
  memory, role, playbook, routing, center, runtime, and Tree of Sophia meaning.

Generated decision indexes are weaker than the decision notes. They exist to
make lookup cheaper for agents, not to carry decision rationale.

## Index Shape

Each decision owns:

- a canonical `Decision ID: AOST-D-####`;
- a full canonical-ID filename, for example `AOST-D-0001-*.md`;
- an `## Index Metadata` block naming original date, surface classes, stats
  surfaces, source lanes, guard families, and posture.

The lookup indexes under [indexes](indexes/README.md) are generated from that
metadata:

- [Decisions by canonical ID and number](indexes/by-number.md)
- [Decisions by date](indexes/by-date.md)
- [Decisions by surface class](indexes/by-surface.md)
- [Decisions by stats surface](indexes/by-stats-surface.md)
- [Decisions by source lane](indexes/by-source-lane.md)
- [Decisions by validation or guard family](indexes/by-guard.md)

Regenerate the read models after decision metadata changes:

```bash
python scripts/generate_decision_indexes.py
```

Check generated parity before closeout:

```bash
python scripts/generate_decision_indexes.py --check
```

## Lookup Route

Do not hand-maintain a "latest decision" roster in this README. That list drifts
as soon as a new decision lands.

Use the generated indexes instead:

- [by number](indexes/by-number.md) for the complete canonical ledger;
- [by date](indexes/by-date.md) for recent landings;
- [by surface](indexes/by-surface.md), [by stats surface](indexes/by-stats-surface.md),
  and [by source lane](indexes/by-source-lane.md) for route-pressure lookup;
- [by guard](indexes/by-guard.md) for validation, derived-authority,
  receipt-intake, generated-output, source-coverage, canary, or regrounding
  pressure.

## Addressing

Full canonical-ID decision paths are the active source files:

- `docs/decisions/AOST-D-0001-*.md`
- `docs/decisions/AOST-D-0002-*.md`
- `docs/decisions/AOST-D-####-*.md`

Canonical IDs remain stable handles. Previous path names belong to git, PR, or
release history, not to a compatibility lookup layer.

## Naming

Use the full canonical decision ID as the filename prefix:

`AOST-D-0001-short-decision-slug.md`

Prefer short titles that name the stats route, not the whole debate.

## Template

Start from [TEMPLATE.md](TEMPLATE.md) for new decisions. Keep notes concise, but
include enough context, options, rationale, consequences, source surfaces, and
validation for a future agent to avoid repeating the same route question.
