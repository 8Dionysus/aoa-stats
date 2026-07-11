# Consumer Re-Grounding Signals

## Purpose

`aoa-stats` exposes enough derived context for consumers to know when they
should re-ground in owner-local truth before using a summary.

The two stats-owned inputs are:

- `generated/summary_surface_catalog.min.json` as the surface-profile catalog
- `generated/source_coverage_summary.min.json` as the intake-coverage audit

These inputs are signals for consumers such as `aoa-sdk` and `aoa-routing`.
They are not proof verdicts, route decisions, or workflow instructions.

## Surface Profile

Each catalog entry acts as one compact `surface_profile`.

Consumers should read:

- `input_posture` to understand the evidence chain behind the surface
- `owner_truth_inputs` to find the stronger owner-local sources
- `authority_ceiling` to know where the summary stops
- `consumer_risk` to decide how cautious a read should be
- `live_state_capable` to know whether a live refresh can update the surface

High-risk profiles should usually send the reader back to owner truth before a
mutation, public-share action, or route/proof claim.

## Source Coverage

`source_coverage_summary` tells the consumer whether the current stats feed is
broad enough to lean on.

Thin-signal flags such as `missing_owner_repos`, `unexpected_owner_repos`,
`owner_share_dominant`, `event_kind_dominant`, `owner_diversity_low`, or
`registry_not_provided` mean the consumer should treat the stats read as
partial and inspect owner-local sources before acting.

## Consumer Contract

The stats layer may say:

- this summary is high-risk to overread
- these owner inputs are stronger
- this feed is missing expected owners
- this feed is skewed toward one owner or event family

The stats layer must not say:

- this route is approved
- this proof passed
- this owner repo is healthy
- this workflow should activate
- this quest or continuity state is canonically true

`aoa-sdk` owns policy application. `aoa-routing` may expose advisory next-read
hints. `aoa-evals` owns bounded proof verdicts.

## Repair Rule

If a stats signal and an owner-local source disagree, repair the derivation or
the source registration. Do not upgrade the stats summary into authority.
