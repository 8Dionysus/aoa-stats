# AGENTS.md
Local guidance for `schemas/` in `aoa-stats`.

Read the root `AGENTS.md` first. Schema changes are contract changes for the
shared receipt envelope, event families, and derived summary read models.

## Local role
Schemas define what stats builders may accept or emit. They do not define the
meaning of skills, eval verdicts, playbooks, agents, memo objects, or runtime
closeouts.

## Editing posture
Pair schema changes with examples, docs, builders, and tests. Keep required
fields, event-kind names, refs, and surface-strength wording explicit.

## Hard no
Do not loosen contracts to accept ambiguous owner meaning. Do not create a
universal score schema.

## Validation
Run:

```bash
python scripts/validate_receipt_abi.py
python scripts/validate_repo.py
python -m pytest -q tests
```
