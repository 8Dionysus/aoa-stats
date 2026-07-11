# AGENTS.md

Guidance for the `aoa-stats` Experience mechanic.

Read the repository root `AGENTS.md`, `DESIGN.md`, and
`mechanics/experience/README.md` before editing this package. Then follow the
nearest part contract and validation route.

## Local role

This package owns repeatable stats-side Experience observability contracts:
micro-friction receipts, adoption and federation readouts, governance signals,
and release/watch/office health contracts.

It does not own Experience policy, source-owner events, release approval,
runtime state, proof verdicts, KAG promotion, or Tree of Sophia canon.

## Edit law

- Keep authored Experience docs, examples, schemas, and focused tests inside
  their owning part.
- Keep one active owner for every payload. Do not restore a second root copy.
- Keep root `generated/` outputs and public stats contracts in their declared
  publication homes; this package does not absorb them by analogy.
- Preserve schema identifiers unless a separate compatibility decision changes
  the public identity.
- Treat examples as illustrative, never as live owner evidence.

## Validation

Run the focused command in each changed part's `VALIDATION.md`. For the whole
package, run the four part-local test modules listed in `PARTS.md`.
