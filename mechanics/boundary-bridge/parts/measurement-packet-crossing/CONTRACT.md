# Measurement packet crossing contract

## Purpose

Check and combine owner-local measurement packets without changing their
metric identity, units, population meaning, evidence, privacy, or authority
ceiling.

## Inputs

- central measurement and packet schemas under `stats/measurement-contract/`
- an owner-local contract admitted by `stats/federation/local-port.schema.json`
- one or more evidence-linked packets written by that contract's owner

## Outputs

- cross-field semantic findings
- stable evidence and statistic identities
- a compatible derived packet when the owner contract explicitly admits the
  requested aggregation
- privacy-bounded distribution summaries and exact finite-sample `pass@k` or
  `pass^k` estimates

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

## Ownership

`stats/measurement-contract/` owns the shared grammar;
`stats/federation/` owns local-port compatibility; each local port owns domain
meaning and evidence. `src/aoa_stats_builder/measurement.py` is the
filesystem-free executable core for this part. Generated views, filesystem
adapters, runtime projection, and MCP remain outside this crossing.

## Crosswalk

This part serves stats source-family ids `measurement_contract` and
`federation`. Reciprocal routes live in `stats/source_home.manifest.json` and
`mechanics/topology.json`.
