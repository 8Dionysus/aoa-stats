# method-growth mechanic

`mechanics/method-growth/` is the active aoa-stats implementation of the common
`method-growth` mechanic.

Observes candidate lineage, owner landing, and explicit supersession without deciding promotion.

Start with `PARTS.md`, then use the selected part's `README.md`,
`CONTRACT.md`, and `VALIDATION.md`.

The three parts share deterministic projection code in
`src/aoa_stats_builder/candidate_lifecycle.py` and focused cross-part tests in
`mechanics/method-growth/tests/test_candidate_lifecycle.py`. The root
`scripts/build_views.py` only exposes that core through repo-wide build and
compatibility orchestration.
