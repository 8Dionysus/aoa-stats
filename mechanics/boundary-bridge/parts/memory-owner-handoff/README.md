# Memory owner handoff

This part derives a bounded committed snapshot from reviewed `aoa-memo`
surfaces and returns consumers to the memory owner. It does not create local
memory truth or convert session evidence into durable memory.

The projection is split between a filesystem-free core at
`src/aoa_stats_builder/memory_movement.py` and the exact four-root source
adapter at `src/aoa_stats_builder/memory_movement_sources.py`.
`scripts/build_views.py` remains the compatibility and publication facade.

Memory Movement is currently reference-only. Its owner corpus is authentic,
but no tested observation route causes local stats refresh whenever that
corpus moves. Read [the detailed guide](docs/MEMORY_MOVEMENT_SUMMARY.md) for
the source boundary, false-live finding, and activation condition.
