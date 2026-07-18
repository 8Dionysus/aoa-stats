---
name: aoa-stats
description: Answer, diagnose, or evolve a bounded `aoa-stats` surface. Use for measurement compatibility, owner stats-port federation, receipt admission, derived or live read-model drift, source coverage, or stats access. Do not use for generic analytics, owner metric invention, eval verdicts, workflow or routing, or runtime repair.
---

# aoa-stats

## Intent

Provide one owner-local front door for statistical work without turning a
derived view into proof, health, causality, workflow, or source truth. Keep
`answer`, `diagnose`, and `evolve` as internal modes until held-out work proves
that separate prompt-visible skills add value.

## Applicability preflight

Inspect the request before resolving an owner checkout:

- use this bundle when the task depends on shared measurement compatibility,
  an owner stats port, receipt admission, an authored stats profile or
  operation, a generated or live read model, source coverage, or stats access
- return `not_applicable` for generic analytics, ordinary code edits, an
  owner's undefined domain metric, central eval interpretation, routing,
  workflow execution, runtime repair, or a request whose only need is to run
  an already named validator
- do not inspect the workspace or search for an owner repository when the
  negative boundary already decides the route

## Start

1. Record `<bundle_dir>` as the directory containing this loaded `SKILL.md`.
2. Read `references/contract.yaml` and `references/source-return.md` to EOF.
3. Select exactly one mode from the requested operation:

   | Mode | Select when | Read |
   | --- | --- | --- |
   | `answer` | The request asks whether, how much, which, present, covered, current, or fresh for an already meaningful surface. A negative, partial, stale, or unknown result stays `answer`. | `references/answer.md` |
   | `diagnose` | The request asks why an observed stats symptom occurred or where its earliest causal boundary lies. | `references/diagnose.md` |
   | `evolve` | A confirmed question or consumer lacks an adequate admitted contract or surface. | `references/evolve.md` |

   Missing inputs block the selected mode; they do not change its identity.
   Do not select `diagnose` merely because an `answer` may expose stale,
   missing, misleading, or inconsistent data.
4. Read only the selected mode reference. Do not preload the other procedures.
5. Only after the selected mode reference is loaded, execute the source-return
   gate before any owner-relative read. Reading `source-return.md` does not
   execute that gate: do not open `.aoa-skill-source.json`, the owner manifest,
   or any owner document before the mode reference.
6. Follow the selected procedure and return its typed output.

The owner source checkout locates authored procedure and contract truth. It
does not by itself identify the deployed runtime or the federation root used
for a live observation. Resolve those separately when the requested time
posture is current/live.

## Owner and authority boundary

- `aoa-stats` owns shared measurement compatibility, federation, receipt
  admission, stats-authored profiles, deterministic derivation, and the shape
  of its weaker read models.
- Domain owners retain metric meaning, populations, dimensions, evidence,
  privacy, freshness expectations, and current exports.
- `aoa-evals` retains proof and verdict interpretation.
- MCP, KAG, dashboards, catalogs, generated files, and the installed bundle
  remain access or projection layers; none gains source authority.
- `answer` and `diagnose` are read-only. `evolve` may change owner source only
  with explicit effect authority and the repository's normal approval route.

## Composition

Build only the task-local edges required by the question:

```text
domain owner or registered receipt
  -> compatible stats contract
  -> authored profile or operation
  -> owning mechanic
  -> generated or live observation
  -> bounded answer, diagnosis, or evolution result
```

A valid chain is not execution evidence. Record the procedure loaded, owner
sources read, commands actually invoked, typed result produced, verification,
effects, and stop line.

## Verification and stop

- trace every material claim to the strongest source actually read
- separate procedure-source, deployed-runtime, and live-data roots in every
  current-state claim
- inspect at least one selected record or artifact, not only a command exit
- preserve `missing`, `unknown`, `stale`, zero, fail, and partial as distinct
- for diagnosis, disconfirm at least one adjacent layer
- for evolution, exercise the motivating and strongest negative cases before
  durable automation
- stop after one bounded result, owner handoff, no-change decision, or explicit
  blocker
- keep raw trials and task-local DAGs in session state
