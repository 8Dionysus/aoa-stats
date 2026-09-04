# AGENTS.md

Local guidance for `examples/` in `aoa-stats`.

Examples demonstrate derived stats contracts without becoming canonical
evidence. Open the paired schema, human explanation, or validator only when
the selected example requires it.

## Local role

Examples pair schemas, docs, and validators. They show the smallest
public-safe shape needed to test a contract.

## Editing posture

When a schema changes, update paired examples and tests in the same bounded
diff. Make fake or sample status explicit. Keep evidence refs illustrative
unless the example is intentionally tied to a real public surface.

## Hard no

Do not make example receipts look like live source truth or use examples to
smuggle owner meaning into stats.

## Conditional validation

Use the root `VALIDATION.md` route for repository checks and the nearest
operation-part validation when an example belongs to a mechanic payload. Report
whether a check exercised a fixture, a committed projection, or a live owner
source; those evidence classes remain separate.
