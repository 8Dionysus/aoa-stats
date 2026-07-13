# AOST-D-0011 Antifragility Vector Remains An Evidence-Gated Incubator

## Index Metadata

- Decision ID: AOST-D-0011
- Original date: 2026-07-11
- Surface classes: stats/read-models, mechanics/antifragility, schemas/deferred-contract, generated/catalog
- Stats surfaces: Antifragility Vector, deferred contract surfaces, surface strength, activation gaps
- Source lanes: aoa-stats, ATM10-Agent, aoa-evals
- Guard families: derived-only authority, deferred lifecycle, owner evidence, activation gaps, live admission, consumer safety
- Posture: accepted

## Status

Accepted

## Context

AOST-D-0001 kept `antifragility_vector` contract-only until a real
owner-linked repeated stress family existed. The candidate retained a schema,
an example, one activation sentence, and an authority ceiling, but its public
deferred catalog entry did not say which parts of the intended chain had
become real or which parts were still missing.

A current owner audit found meaningful progress. ATM10-Agent
`scripts/hybrid_query_demo.py` now writes a source-owned
`stressor_receipt_v1` when the hybrid planner truthfully falls back to
`retrieval_only_fallback`. The repository owns the receipt schema and a
reviewed example, so the candidate is no longer an ungrounded symmetry
placeholder.

The rest of the activation chain is not current. ATM10-Agent
`adaptation_delta_v1` remains schema/example only and is not emitted by the
runtime. The `aoa-antifragility-posture` eval is still draft and its
machine-readable report is an example rather than an executed report over
current owner receipts. The runtime stressor receipt is not registered in the
aoa-stats live receipt source registry. No repeated owner/eval window for the
same stressor family demonstrates movement or adaptation.

The checked-in vector example also assigned numeric axes while describing a
low-sample contract-only surface. Those numbers were useful as an early shape
illustration but could be mistaken for a grounded measurement even though no
producer or derivation rule exists.

## Decision

Antifragility Vector remains the sole deferred read-model candidate. It is not
retired, because the ATM10-Agent runtime publisher and owner/eval contracts
form a real incubation path. It is not activated, because the current chain
cannot support a derived vector or a movement claim.

The authored deferred profile and its public catalog projection now carry:

- `input_posture=partial_owner_runtime_draft_eval_chain`;
- exact `owner_truth_inputs` for the ATM10-Agent publisher, receipt and
  adaptation contracts/examples, and the aoa-evals draft/report surfaces;
- four non-empty unique `activation_gaps`;
- `consumer_risk=high`;
- the existing authority ceiling and a stronger all-gaps activation
  condition.

The four gaps are:

1. the ATM10-Agent runtime stressor receipts are not registered in the
   aoa-stats live receipt source registry;
2. ATM10-Agent adaptation deltas have no runtime publisher;
3. the bounded aoa-evals posture bundle has no executed report chain over the
   current runtime receipts;
4. no repeated owner/eval window demonstrates movement for the same stressor
   family.

The mechanic-local schema now names `adaptation_delta_refs` separately and
requires explicit suppression. The checked-in example has no adaptation ref,
declares `insufficient_evidence`, and leaves every numeric axis null. Focused
schema, profile, catalog, and non-publication proof moves from the root build
suite to the Antifragility Vector part.

No builder, package export, root facade alias, generated vector payload,
active catalog slot, live receipt registration, refresh route, or MCP
promotion is added. Activation is a future bounded decision that must close
all four gaps for one stressor family and review producer, schema/output,
active profile and new slot, validation, live-state posture, and consumers
together.

## Options Considered

- Activate from the current owner and eval examples: rejected because one
  runtime stressor publisher plus draft/example companions cannot establish
  adaptation or repeated-window movement.
- Retire the candidate because no external consumer reads a vector today:
  rejected because the owner runtime receipt and matching eval contracts
  provide a real, bounded incubation path that AOST-D-0001 intended to grow.
- Keep the old opaque deferred entry: rejected because it hides the difference
  between the real publisher and the three still-proposed or unconnected
  evidence layers, making future consumers more likely to overread it.
- Keep an evidence-gated deferred entry with exact owner inputs, risk, and
  activation gaps: chosen because it preserves the future shape without
  presenting unfinished evidence as a product.

## Rationale

Repository necessity and surface necessity are judged by authority plus real
owner and consumer paths, not by symmetry alone. The runtime stressor
publisher is enough to make this candidate materially grounded, but a schema
and draft eval do not make a derived statistic necessary or honest yet.

Deferred status should carry more truth as a candidate matures. Publishing the
partial input posture and activation gaps makes the read-only catalog useful
to agents and future MCP consumers without turning visibility into
capability. Reusing the active-profile vocabulary for input posture, owner
truth, authority, and consumer risk avoids a second semantic model.

Numeric nulls are the correct contract example while no derivation and
repeated evidence exist. They demonstrate suppression without fabricating a
prestige score or implying that aoa-stats has evaluated ATM10-Agent.

## Consequences

- The authored inventory remains 22 active profiles, one deferred profile,
  and three retired profiles.
- The active and live-admitted inventories remain unchanged; no output enters
  committed or local live state.
- The public deferred catalog entry grows from six to ten fields and exposes
  exact owner grounding plus closure obligations.
- The Antifragility Vector mechanic gains a real part-local test district;
  root `tests/test_build_views.py` loses its remaining vector-specific
  schema test.
- The example becomes explicitly suppressed and cannot be read as a current
  measurement.
- A future read-only MCP route may report this deferred posture, but may not
  infer readiness or trigger activation from it.
- AOST-D-0001 remains authoritative for the original contract-only boundary;
  this decision refines how that boundary is represented after the first real
  owner publisher appeared.

## Source Surfaces

- `AGENTS.md`
- `DESIGN.md`
- `stats/read-models/AGENTS.md`
- `stats/read-models/README.md`
- `stats/read-models/deferred/antifragility_vector.profile.json`
- `stats/read-models/surface-profile.schema.json`
- `mechanics/antifragility/parts/antifragility-vector/`
- `mechanics/topology.json`
- `schemas/summary-surface-catalog.schema.json`
- `generated/summary_surface_catalog.min.json`
- `ATM10-Agent/scripts/hybrid_query_demo.py`
- `ATM10-Agent/schemas/stressor_receipt_v1.json`
- `ATM10-Agent/schemas/adaptation_delta_v1.json`
- `aoa-evals/evals/stress/aoa-antifragility-posture/EVAL.md`
- `aoa-evals/evals/stress/aoa-antifragility-posture/reports/summary.schema.json`
- `aoa-evals/evals/stress/aoa-antifragility-posture/reports/example-report.json`

## Validation

Decision-lane checks are owned by [`AGENTS.md#verify`](AGENTS.md#verify).
Affected source-home and mechanic checks route through their owning
`AGENTS.md` or `VALIDATION.md`, then the root
[`AGENTS.md#verify`](../../AGENTS.md#verify) gate and the release runbook.
