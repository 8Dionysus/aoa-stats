# rpg mechanic

`mechanics/rpg/` is the active aoa-stats implementation of the common
`rpg` mechanic.

Observes named route progression across bounded axes without collapsing growth into one score.

Start with `PARTS.md`, then use the selected part's `README.md`,
`CONTRACT.md`, and `VALIDATION.md`.

The importable projection lives in
`src/aoa_stats_builder/route_progression.py`, with focused behavioral checks in
`parts/route-progression/tests/test_route_progression.py`. The root builder is
only the compatibility and publication facade.

This package projects only the committed legacy numeric receipt shape. The RPG
center owns vocabulary and stop-lines, while `aoa-skills`, `aoa-agents`, and
`aoa-sdk` retain receipt, agent-overlay, and typed-contract truth. The current
semantic owner receipt is not scored, and this surface is not live-admitted.
