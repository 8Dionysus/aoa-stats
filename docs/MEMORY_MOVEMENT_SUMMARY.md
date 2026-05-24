# Memory Movement Summary

## Purpose

`generated/memory_movement_summary.min.json` is the derived stats view for the
current `aoa-memo` reviewed memory corpus and reviewed-intake landing movement.

It answers: how many reviewed corpus objects exist, which kinds and recall
postures they carry, what KAG-lift posture is visible, and what reviewed-intake
packets have landed.

## Inputs

The builder reads `aoa-memo` source-owned memory surfaces:

- `generated/memory-objects/memory_object_catalog.min.json`
- `memo/objects/**/object.json`
- `memo/intake/reviewed/*.json`
- `memo/intake/receipts/*.json`

The object corpus is stronger than this summary. The summary must match the
reviewed object ids exposed by the `aoa-memo` min catalog before it can build.

## Output

The summary publishes:

- `source_kind_counts`
- reviewed corpus counts by kind, review state, recall status, temperature, and
  KAG-lift status
- compact reviewed object refs
- reviewed-intake packet and landing receipt counts
- consumer handoff refs for `aoa-evals`, `aoa-kag`, `aoa-stats`,
  `aoa-playbooks`, and `aoa-agents`

## Authority

This is a derived movement summary only.

It may help consumers see whether reviewed memory is growing and where handoff
pressure exists. It does not decide memory truth, promote objects, land reviewed
intake, approve KAG facts, or replace `aoa-memo` source refs and receipts.

## Memory Consumer Boundary

`aoa-stats` is a route-only/read-only memory consumer for this surface. It may
publish reviewed object ids, provenance-bearing object refs, lifecycle and
recall posture, generated read-model counts, reviewed-intake packet counts, and
landing receipt counts.

It does not create local memo candidates, prepare reviewed-intake exports, run
landing plans as authority, or land durable memory.

Session evidence remains `.aoa` evidence until a reviewed owner route promotes
it through `aoa-memo` reviewed intake. `aoa_memo` MCP
brief/search/status/validation/landing-plan dry-runs are access-plane evidence
for review, not stats truth. Durable memory still lands as a reviewed source
patch in `aoa-memo`.

## Validate

Run:

```bash
python scripts/build_views.py --check
python scripts/validate_repo.py
python -m pytest -q tests/test_memory_movement_summary.py tests/test_summary_surface_catalog.py
```
