# AOST-D-0013 aoa-stats Owner Skill Bundle

## Index Metadata

- Decision ID: AOST-D-0013
- Original date: 2026-07-15
- Surface classes: skills/home, agent interface, repository projection, owner boundary
- Stats surfaces: measurement contract, federation, intake, read models, live refresh, source coverage, access
- Source lanes: aoa-stats owner sources, owner-local stats ports, bounded proof, runtime observation
- Guard families: derived-only authority, manual admission, source/projection parity, negative applicability
- Posture: accepted

## Status

Accepted

## Context

The repository exposed 25 copied shared bundles under `.agents/skills` but had
no canonical home for its own callable procedure. Those copies competed with
the shared user profile, carried obsolete skill names, and could not express
the stats-specific authority ladder. A prior prototype proposed several narrow
visible skills, but their triggers, result shape, and owner boundaries largely
overlapped.

Manual work exercised a bounded owner-inventory answer, a stale live-publisher
diagnosis, a proposed global freshness score, retired-lifecycle and
committed-versus-live held-out cases, a newly missing owner-catalog metric, and
negative/coexistence requests. The procedure repeatedly prevented counts,
parseability, systemd success, or generated freshness from becoming owner
health. It also returned the global score proposal to owner-local freshness
meaning and disconfirmed the service layer before naming an upstream receipt
boundary.

## Decision

Admit one repository-owned `aoa-stats` bundle with internal `answer`,
`diagnose`, and `evolve` modes. Its canonical source lives at
`skills/aoa-stats/SKILL.md`; `skills/port.manifest.json` declares version and
admission. The exact repo-scoped Codex copy is generated at
`.agents/skills/aoa-stats` through the common `aoa-skills` home-port contract.

Remove the 25 undeclared shared copies from the repository projection. Do not
split the three modes into separate prompt-visible bundles unless later
held-out trials establish independent triggers, ABIs, composition value, and
outcome benefit.

Remove the root test that imported `bringup_contract.py` from the copied
`aoa-local-stack-bringup` projection. The tested behavior belongs to a target
runtime owner's stack workflow, not to `aoa-stats`; retaining the test would
make a generated foreign projection a hidden source and release dependency.

## Options Considered

- Keep the copied shared catalog and rely on generic procedures: preserves no
  source migration, but retains routing interference and no stats owner ABI.
- Advertise a separate skill for each stats operation or internal mode: makes
  names explicit, but multiplies semantically adjacent candidates before
  independent benefit is demonstrated.
- Admit one owner bundle with three internal modes and one exact derived
  projection: preserves a small discovery footprint and one authority chain.
- Keep no skill and rely only on root guidance: avoids prompt cost, but manual
  comparisons showed repeated value from the bounded result ABI, negative
  applicability, adjacent-layer disconfirmation, and explicit no-change route.

## Rationale

The three modes select different actions but share applicability, owner
sources, authority ordering, output fields, failure vocabulary, and collision
boundaries. One bundle is the smallest callable unit supported by the observed
work. The repository owns its adaptation; `aoa-skills` owns only the common
projection grammar, and KAG remains a source-linked retrieval layer.

Raw trials and task-local DAGs stay in the session. The durable record keeps
only the admission rationale and claim limits.

## Consequences

- Codex sees one stats-specific repository skill instead of 25 copied shared
  names.
- The repository gate no longer claims ownership of a retired portable
  local-stack helper through a copied projection.
- Answer and diagnosis remain read-only; source mutation requires explicit
  `evolve` authority.
- Generic analytics, eval-verdict interpretation, routing, workflows, runtime
  repair, and already-named validator execution remain negative cases.
- Structural validation can prove owner and byte parity but cannot prove
  routing quality, cross-model transfer, safety, or outcome improvement.
- A material model, workflow, or bundle change requires new isolated,
  negative, held-out, and coexistence work before lifecycle expansion.

## Source Surfaces

- `AGENTS.md`
- `DESIGN.md`
- `docs/BOUNDARIES.md`
- `skills/AGENTS.md`
- `skills/README.md`
- `skills/aoa-stats/SKILL.md`
- `skills/port.manifest.json`
- `stats/source_home.manifest.json`
- `mechanics/topology.json`
- `aoa-skills:docs/decisions/AOA-SK-D-0040-owner-skill-homes-and-projection-boundaries.md`
- `aoa-skills:docs/decisions/AOA-SK-D-0041-minimal-owner-home-port-contract.md`

## Validation

Decision indexes, portable `SKILL.md` validation, the pinned common home-port
action, prompt-visible fresh-session inspection, repo-local KAG parity, and the
root release gate protect the durable shape. Manual trials remain the semantic
admission evidence; green checks do not replace them.

## Current Applicability

As of 2026-07-17:

- Still valid: `skills/aoa-stats/` is the canonical one-bundle owner home, and
  its internal modes retain the admitted trigger and result contract. Version
  `0.2.1` keeps one short front door and conditionally loads the shared
  contract, source-return procedure, and exactly one of `answer`, `diagnose`,
  or `evolve`.
- Changed: `skills/port.manifest.json` now selects the bundle for the single
  OS-level `os-user-default` profile; no repository `.agents/skills` copy is
  part of the active architecture.
- Superseded: the repo-scoped projection portion of this decision is replaced
  by the v2 owner-home exposure contract. Manual admission evidence remains.

## Review Log

### 2026-07-16 - Move discovery to the single OS user profile

- Previous assumption: an admitted owner home needed an exact repository copy
  under `.agents/skills`.
- New reality: the canonical owner package is installed once into the managed
  Codex user catalog and remains globally discoverable from neutral sessions.
- Reason: duplicate user and repository definitions create routing ambiguity,
  while a repo-only copy hides the stats capability until after navigation.
- Source surfaces updated: `skills/port.manifest.json`, `skills/README.md`,
  `skills/AGENTS.md`, `README.md`, `DESIGN.md`, and `docs/ARCHITECTURE.md`.
- Validation: manual OS-profile installation and fresh-session discovery are
  required before closeout; source checks prove only identity and package
  shape.

### 2026-07-17 - Separate procedure source, deployed runtime, and live data

- Observed defect: an early diagnosis ran the live-publisher checker from an
  isolated owner worktree and treated that checkout's default federation root
  as the deployed OS surface. The command reported six missing publishers, but
  that result described the worktree binding rather than current `/srv`
  deployment state. A correct-looking diagnosis therefore remained invalid.
- Correction: version `0.2.1` requires every current/live result to resolve
  three independent roots: the owner checkout that supplies the skill
  procedure, the deployed `aoa-stats` runtime, and the live federation/data
  root. Source return locates authored procedure only; it cannot silently
  select runtime or live data.
- Manual diagnosis result: the corrected `diagnose` route disconfirmed an
  owner outage. The same checker that failed under the worktree default passed
  against the explicit deployed federation root, as did the deployed checker.
  The earliest evidenced boundary was the worktree default-root binding, not
  absent OS publishers.
- Manual answer result: the corrected `answer` route read the owner profile and
  live-refresh contract, then inspected the deployed publisher audit and live
  source-coverage artifact. All six required publisher files were present,
  readable, non-empty, and parseable. The live summary covered all five owner
  repositories declared by the registry. It did not prove freshness: no
  owner-authored freshness window exists, and artifact rebuild time cannot
  substitute for evidence observation time. The exact result was therefore
  present and registry-covered with freshness `unknown`, not globally fresh.
- Manual evolution result: a request for one cross-publisher numeric freshness
  score selected `evolve` and returned `no_change` /
  `blocked_missing_meaning`. It refused to invent windows, weights,
  thresholds, missing-value substitution, or a health score before publisher
  owners and the consuming operator define their meanings.
- Negative and coexistence results: an already named repository validator ran
  directly without loading `aoa-stats`; a central eval-candidate authority
  question selected `aoa-evals` alone. No trial created a stats source,
  generated view, test, validator, or runtime write.
- Efficiency limit: the final current/live answer was semantically correct and
  bounded to the selected owner route, but required 22 read-only commands and
  395,717 raw input tokens on the exercised Codex host/model. This record makes
  no general token or latency improvement claim.
- Verdict and limit: version `0.2.1` is behaviorally retained for the exercised
  `answer`, `diagnose`, `evolve`, negative, and adjacent-owner coexistence
  cases. The result does not prove every wording, all AoA owners beyond the
  registry, cross-model or cross-host parity, security, live systemd control,
  or general cost superiority. Recheck after a material model, host, source,
  runtime, live-data, or package change.
