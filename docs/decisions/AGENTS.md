# AGENTS.md

## Guidance for `docs/decisions/`

`docs/decisions/` is the durable decision-rationale lane for `aoa-stats`.
Use it when a future contributor needs why a federated measurement,
derived-observability, receipt-intake, summary-strength, generated read-model,
live-source, MCP, validator, or consumer-regrounding boundary was chosen.
Stats surfaces remain owned by their source records; decision notes explain
rationale and do not become source authority.

## Record law

- Decision files use full canonical filenames: `AOST-D-####-short-slug.md`.
- Each decision has an `## Index Metadata` block with `Decision ID`, `Original
  date`, `Surface classes`, `Stats surfaces`, `Source lanes`, `Guard families`,
  and `Posture`.
- Decision IDs are stable handles. Historical date-slug paths belong to Git and
  PR history, not to a compatibility lookup layer.
- Generated indexes under `docs/decisions/indexes/` are read models only; do
  not edit them by hand.
- `modeled_surfaces` is a normalized list of repo-relative decision paths, not
  a roster for root Markdown.
- Material rationale changes should add an explicitly superseding decision
  instead of silently rewriting an accepted route.

## Boundary and conditional routes

Decision notes are weaker than source-owned receipts and verdicts, generated
summaries, configs, schemas, examples, scripts, tests, public docs, and the
stronger owner repositories they describe. Do not use this lane for runtime
logs, private evidence, proof verdicts, mutable status, route dispatch,
workflow, memory promotion, or quest truth.

When a rationale question is known, follow the affected source or operation
first and open its README or owner card only when that human explanation is
needed. Generated lookup indexes support navigation and never carry the note's
rationale.

## Conditional validation

Decision-index parity and decision-record validation are owned by the root
`VALIDATION.md` route. When metadata changes, use the declared index builder
before review; when only prose or routine tests change, retain the existing
decision and run the owning source or part validation. The route card does not
carry a runnable procedure.
