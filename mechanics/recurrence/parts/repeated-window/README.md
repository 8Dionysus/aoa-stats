# Repeated window

This part routes the deterministic repeated-window summary without moving its
stable public contract merely for directory symmetry.

- status: `public_contract_routed`
- stats source family: `read_models`
- source profile: `stats/read-models/active/repeated_window_summary.profile.json`
- public schema: `schemas/repeated-window-summary.schema.json`
- public output: `generated/repeated_window_summary.min.json`
- shared builder: `scripts/build_views.py`
- checks: `VALIDATION.md`

There is no private payload copy in this part. The route card and contract are
the mechanic boundary; the schema and output intentionally remain public.
