# Diagnose mode

Use this mode when a stats surface is absent, stale, incompatible, misleading,
or inconsistent and the request asks why or where the causal boundary lies.
Keep it read-only. A request that only asks whether the surface has one of
those postures belongs to `answer`.

## Inputs

- observed symptom and affected consumer
- expected source/runtime boundary and time posture
- selected authored profile or operation when known
- relevant owner input, generated/live output, or access observation

## Procedure

1. Record the observed symptom without converting it into a cause.
2. Use `source-return.md` to select one authored route.
3. When the symptom is live, resolve the deployed runtime and live data root
   separately from the procedure source checkout. Treat a worktree-relative
   path failure as a binding defect until the deployed path is checked.
4. Walk upstream only along declared links:

   ```text
   access -> output -> builder -> mechanic -> profile/operation
          -> compatibility/intake -> owner port -> producer
   ```

5. Stop at the earliest boundary supported by direct evidence.
6. Check at least one plausible adjacent layer and record why it is or is not
   causal.
7. Distinguish absent source, stale source, missing observation trigger,
   incompatible contract, rejected receipt, non-admitted profile, builder
   drift, stale generated output, and access drift.
8. Return a `bounded-stats-diagnosis` containing the symptom, earliest evidenced
   boundary, competing layer result, sources, temporal posture, authority
   ceiling, owner handoff, actual effects `none`, skipped checks, and stop line.

## Worktree/runtime-root fast path

Use this bounded path when a root compatibility command reports missing
owner-local sources from an isolated checkout and the question asks whether
the publishers or the binding is wrong. This path replaces the broader
publisher/source-coverage answer chain.

1. Read the authored live-runtime guide and only the checker/refresh lines that
   define the default federation root and repo-relative resolution. Use the
   exact implementation file
   `mechanics/recurrence/parts/live-receipt-refresh/scripts/refresh_live_stats.py`
   and a bounded lookup for `DEFAULT_FEDERATION_ROOT` plus
   `resolve_source_path`; do not search the mechanic tree or guess helper
   names.
2. Inspect the deployed unit files declared by the guide to resolve one
   runtime repository and live federation root. Read the two exact user-unit
   paths; do not enumerate other worktrees or sibling repositories and do not
   read either checker implementation.
3. Reproduce the supplied source-worktree command once with its default.
4. Run that same source-worktree checker once with the explicit deployed
   federation root.
5. Run the deployed checker once with explicit registry and federation-root
   paths as the adjacent-layer control.
6. When the default worktree run fails on resolved source paths while both
   explicit-root runs pass, return
   `boundary=source_worktree_default_federation_binding` and stop.

Do not inspect individual publisher bodies, deprecated sibling aliases,
unrelated source trees, committed summaries, live summaries, or catalogs after
that comparison establishes the boundary. Do not `stat`, list, parse, sample,
or recount the publisher files: the same canonical checker already reports
their status and receipt counts. The three audit results are the terminal
evidence that distinguishes publisher absence from checkout-derived path
binding.

## Termination

Stop after one read-only diagnosis or explicit blocker. Do not mutate a
producer, service, profile, registry, cache, generated file, or access plane.
