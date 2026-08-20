# Measurement packet crossing contract

## Purpose

Check and combine owner-local measurement packets without changing their
metric identity, units, population meaning, evidence, privacy, or authority
ceiling.

## Inputs

- central measurement and packet schemas under `stats/measurement-contract/`
- the central C10 outcome-receipt schema under `stats/measurement-contract/`
- an owner-local contract admitted by `stats/federation/local-port.schema.json`
- one or more evidence-linked packets written by that contract's owner
- a task/source-owner outcome receipt carrying refs rather than raw payloads

## Outputs

- cross-field semantic findings
- stable evidence and statistic identities
- a versioned compatibility-only read result with owner and access authority
  ceilings
- a compatible derived packet when the owner contract explicitly admits the
  requested aggregation
- privacy-bounded distribution summaries and exact finite-sample `pass@k` or
  `pass^k` estimates
- C10 shape and semantic findings for before/after action snapshots,
  memory-use state, terminal and delayed outcomes, confounders, accidental
  success, harm, costs, attribution uncertainty, task/consumer identity,
  holdout and always-shadow assignment, host evidence, evaluator identity,
  and operator intervention
- a descriptive, content-minimized episodic utility aggregate over compatible
  C10 receipts, without a proof verdict or policy decision
- a descriptive agent-local federation aggregate over owner refs and eval
  results, with reconciled promotion, isolation, portability, consumer-zero,
  and solo-operator burden dimensions

## Invariants

- one measurement identity has one owner writer
- units, contract versions, population definitions, windows, cohorts,
  dimensions, and reporting rules are never pooled implicitly
- ratios preserve numerator and denominator
- distributions and quantiles preserve represented sample size
- missing, unknown, and stale packets never become zero or enter aggregation
- dimension cardinality and sensitive-dimension policies are enforced over the
  packet set
- reference-only input cannot become live
- reporting-rule changes alter statistic identity without rewriting evidence
  identity
- partial progress does not imply terminal success
- host-local paths, raw session material, and raw content do not cross the
  boundary
- aggregation does not invent required uncertainty
- `memory_used=true` requires a recall packet ref; false forbids recall and
  intervention refs; unknown stays unknown
- actionable after-memory state requires an external exact-effect binding and
  never receives authority from memory or C10
- pending or overdue delayed outcomes stay partial
- accidental success and harm cannot be hidden behind terminal success
- supported attribution requires complete snapshots and independently owned
  eval and counterfactual evidence, host evidence, reward-hacking and
  tenant-skew checks, and model-version stratification; C10 never carries a
  causal claim
- randomized holdout keeps an exact assignment digest and always-shadow
  counterfactual; a holdout observation cannot claim memory use
- unavailable or degraded eval freezes policy and forbids positive attribution
- access count never becomes utility, and no outcome score can authorize a
  semantic memory transition
- utility aggregates require one tenant, consumer, and policy pin; invalid C10
  receipts are rejected before aggregation
- terminal success without an action change cannot become qualified utility
- unknown accidental-success status cannot qualify positive utility
- delayed adjustments require explicit task-owner acceptance; rejected or
  unknown delayed outcomes cannot strengthen utility
- duplicate receipt ids or idempotency keys are rejected before aggregation
- pending or overdue delayed outcomes keep utility evidence partial
- the aggregate may report critical-event frequency but cannot demote, delete,
  preserve, promote, or otherwise decide an item's lifecycle
- operator intervention remains explicit and evidence-linked rather than
  disappearing into terminal success
- raw content, direct training use, semantic authority, and effect authority
  are forbidden
- agent-local nomination counts must reconcile to memo-candidate,
  duplicate/no-write, conflict-quarantine, rejected, and deferred results
- net operator minutes equal saved re-grounding minutes minus review minutes;
  a positive burden verdict also requires review to remain inside budget
- no aggregate value authorizes promotion, shared truth, role change,
  namespace activation, or consumer removal

## Ownership

`stats/measurement-contract/` owns the shared grammar;
`stats/federation/` owns local-port compatibility; each local port owns domain
meaning and evidence. Task/source owners retain C10 fact meaning and
`aoa-evals` retains attribution verdicts.
`src/aoa_stats_builder/measurement.py` and
`src/aoa_stats_builder/outcome.py` are the filesystem-free executable cores
for this part. `src/aoa_stats_builder/utility.py` adds descriptive aggregation
only. Generated views, filesystem adapters, runtime projection, proof verdict,
policy proposal, and MCP remain outside this crossing.

## Versioning

C10 v1 is immutable after landing. Semantic changes require a new schema
version, old-versus-new negative and positive fixtures, explicit consumer
migration, and a bounded compatibility window. Contract presence never
activates a producer or runtime consumer.

## Crosswalk

This part serves stats source-family ids `measurement_contract` and
`federation`. Reciprocal routes live in `stats/source_home.manifest.json` and
`mechanics/topology.json`.
