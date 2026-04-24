# AGENTS.md
Local guidance for `examples/` in `aoa-stats`.

Read the root `AGENTS.md` first. Examples demonstrate derived stats contracts
without becoming canonical evidence.

## Local role
Examples pair schemas, docs, and validators. They should show the smallest
public-safe shape needed to test a contract.

## Editing posture
When a schema changes, update paired examples and tests in the same bounded diff.
Make fake or sample status explicit. Keep evidence refs illustrative unless the
example is intentionally tied to a real public surface.

## Hard no
Do not make example receipts look like live source truth. Do not use examples to
smuggle owner meaning into stats.

## Validation
Run:

```bash
python scripts/validate_repo.py
python -m pytest -q tests
```
