---
name: aoa-stats
description: Answer, diagnose, or evolve a bounded `aoa-stats` surface. Use for measurement compatibility, owner stats-port federation, receipt admission, derived or live read-model drift, source coverage, or stats access. Do not use for generic analytics, owner metric invention, eval verdicts, workflow or routing, or runtime repair.
---

# aoa-stats

## Intent

Provide one owner-local front door for statistical work without turning a
derived view into proof, health, causality, workflow, or source truth. Select
one internal mode: `answer`, `diagnose`, or `evolve`.

## Contract

| Field | Value |
| --- | --- |
| identity | `aoa-stats` home bundle, version `0.1.0` |
| owner | `aoa-stats` repository |
| lifecycle | admitted and advertised in repository scope |
| trust | derived-only; owner evidence and bounded proof remain stronger |
| effects | read-only in `answer` and `diagnose`; owner-authorized source changes only in `evolve` |
| composition | may consume owner-local `stats/` ports, eval verdicts, receipts, profiles, mechanics, generated views, and live access as typed task-local DAG nodes |
| conflicts | global health scoring, central invention of local metrics, missing-as-zero, generated-as-source, dashboard-first reasoning |
| termination | one bounded result, owner handoff, no-change verdict, or explicit blocker |

## Applicability

Use this bundle when the task materially depends on one or more of:

- measurement identity, compatibility, population, unit, dimension, window,
  missingness, uncertainty, privacy, or reporting shape shared by owners;
- an owner-local root `stats/` port and its compatibility with the federation;
- receipt-envelope admission or an event-kind boundary;
- an `aoa-stats` profile, operation contract, mechanic, builder, generated read
  model, live publisher, source-coverage surface, or stats access projection;
- disagreement between a derived statistical view and its stronger owner.

Do not use it for generic analytics, ordinary code edits, an owner's domain
question before that owner defines the measure, proof interpretation owned by
`aoa-evals`, route decisions, workflow execution, runtime remediation, or a
request whose only need is to run an already named validator.

## Inputs

- exactly one intent: answer, diagnose, or evolve;
- named question, symptom, or desired measurement and the affected owner;
- source/runtime boundary, time posture, and effect authority;
- relevant owner port, central contract, profile/operation, mechanic, output,
  consumer, or access surface when known.

## Outputs

Every result states:

- selected mode and exact bounded question;
- strongest owner sources used and weaker projections inspected;
- population/window or failure boundary as applicable;
- compatibility, missingness, freshness, and uncertainty posture;
- authority ceiling: what the result does and does not establish;
- effect performed, verification, skipped checks, owner handoff, and stop line.

## Procedure

### 1. Select exactly one mode

| Mode | Select when | Primary output |
| --- | --- | --- |
| `answer` | A bounded statistical question is already meaningful. | Source-backed answer with measure shape and authority ceiling. |
| `diagnose` | A stats surface is absent, stale, incompatible, misleading, or inconsistent. | Earliest evidenced failure boundary and owner handoff. |
| `evolve` | A confirmed question or consumer lacks an adequate admitted contract or surface. | Smallest owner-first change or explicit no-change decision. |

Do not split the three modes into separately advertised skills unless held-out
trials prove independent triggers, ABIs, composition value, and outcome gain.

### 2. Build the smallest authority chain

Read the nearest owner route first, then only the nodes needed from this chain:

```text
domain owner source
  -> owner-local stats port or bounded proof
  -> central compatibility/intake contract
  -> authored profile or operation contract
  -> owning mechanic and pure implementation
  -> generated/live read model
  -> MCP, KAG, dashboard, or consumer cache
```

Classify every used surface as authored owner meaning, compatibility contract,
bounded proof, deterministic derivation, runtime observation, or access
projection. A later node cannot silently repair or strengthen an earlier one.

### Mode: answer

1. Restate the exact measure or question. Name object, population, sample or
   cohort, window, value/unit, dimensions, numerator/denominator when relevant,
   aggregation, missingness, uncertainty, freshness, and reporting rule.
2. Read the owner-local definition before the central inventory or derived
   view. Use a generated or live surface only after tracing it to its profile,
   inputs, and current observation route.
3. Compare units, versions, populations, windows, dimensions, privacy, and
   temporal posture before combining anything. Preserve `missing`, `unknown`,
   `stale`, zero, fail, and partial as distinct states.
4. Inspect the actual selected records or artifact manually. Return the answer
   with source refs and an explicit authority ceiling. A parseable publisher,
   green command, recent refresh, count, trend, or dashboard never establishes
   owner or OS health by itself.

### Mode: diagnose

1. Record the observed symptom without converting it into a cause.
2. Walk upstream from the visible symptom through access, output, builder,
   mechanic, profile/operation, intake/compatibility, owner port, and producer.
   Stop at the earliest boundary supported by direct evidence.
3. Check at least one plausible competing layer and record why it is or is not
   causal. Distinguish absent source, stale source, missing observation trigger,
   incompatible contract, rejected receipt, non-admitted profile, builder drift,
   stale generated output, and access/projection drift.
4. Return a read-only diagnosis and the smallest owner handoff. Do not mutate a
   producer, service, profile, registry, cache, or generated file in this mode.

### Mode: evolve

1. Require a stable owner question, named consumer, observed no-fit or failure,
   and an explicit authority ceiling. If any is missing, stop with the exact
   discovery task rather than inventing a metric.
2. Decide the owner before the shape:
   - domain meaning and freshness expectation stay in the domain owner's port;
   - shared compatibility or receipt vocabulary belongs in the matching
     `stats/` source family;
   - a derived public question needs an authored profile or operation contract;
   - repeatable projection/refresh work belongs to the reciprocal mechanic;
   - implementation stays pure where possible, with I/O and transport at edges.
3. Compare reuse, extension, activation, retirement, and no-change. Do not add
   a central surface when an owner-local answer or existing profile suffices.
4. Exercise expected, rejected, missing, stale, incompatible, and nearest
   collision cases manually before durable automation. Add a validator or test
   only for a stable long-lived invariant that those trials expose.
5. If authorized, change source before generated companions, rebuild only its
   declared projections, inspect artifacts manually, and report what green
   checks cannot prove. Otherwise return a bounded owner-ready proposal.

## Failure modes and stops

- `not_applicable`: the task belongs to a domain owner, eval, workflow, route,
  runtime, or generic analytics rather than `aoa-stats`.
- `blocked_missing_meaning`: object, population, unit, window, owner, or
  consumer is undefined.
- `blocked_stale_or_unknown`: evidence exists but cannot support the requested
  temporal claim.
- `incompatible`: inputs cannot be combined without changing meaning.
- `owner_handoff`: the earliest evidenced boundary is outside `aoa-stats`.
- `no_change`: an existing source or route already answers the need.
- `verified_bounded`: the selected result or owner-authorized change satisfies
  its acceptance criteria with stated claim limits.

## Manual verification

- trace every material claim to its strongest available source;
- inspect at least one actual record or generated artifact, not only a command
  exit code;
- for diagnosis, disconfirm at least one adjacent layer;
- for evolution, replay the motivating case and the strongest negative case;
- report skipped live, cross-owner, model, host, or consumer checks explicitly;
- keep task-local DAGs, raw trials, and comparison notes in session state rather
  than committing them as skill truth.
