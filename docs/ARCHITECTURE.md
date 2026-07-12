# Architecture

## One sentence

`aoa-stats` is an evidence-linked observability layer built from owner-local
receipts, bounded eval verdicts, small progression deltas, and explicit intake
governance.

## Five layers

### 1. Event facts

Append-only receipts say what happened.

The canonical shared receipt envelope and active event family live in
`schemas/stats-event-envelope.schema.json`.
`aoa-stats` owns that shared input contract for cross-repo derivation only.
Owner repos still own the payload contracts that travel inside the envelope.

Examples:

- a harvest packet closed
- a fork was offered and one branch was chosen
- a repair cycle ended
- an automation candidate was detected
- one bounded eval publication happened
- one runtime wave closeout reached a gate and attempted a reviewed handoff

These are facts, not proof.

Corrections stay append-only too. If a newer receipt sets `supersedes`, the raw
log keeps both events while the active stats view collapses to the latest
resolvable correction inside the current feed.

### 2. Evidence links

Each receipt should point to inspectable artifacts through `evidence_refs`
instead of copying raw patches, logs, or reports.

### 3. Bounded evaluations

Quality enters through bounded eval verdicts and review surfaces.
`aoa-stats` may quote or summarize verdicts, but it must not replace them.

### 4. Progression readings

Progression stays route-scoped or quest-scoped and multi-axis.
The stats layer may accumulate deltas, cautions, holds, advances, reanchors,
and downgrades without pretending one total score explains everything.

### 5. Derived views

Derived views stay machine-first.

Current v0 derived views:

- core-skill-application summary
- object summary
- candidate-lineage summary
- supersession-drop summary
- repeated-window summary
- route-progression summary
- fork-calibration summary
- automation-pipeline summary
- source-coverage summary
- surface-detection summary
- memory-movement summary
- summary-surface catalog

`generated/summary_surface_catalog.min.json` is the compact owner-owned
runtime-entry capsule for `aoa-stats`. It points back to derived view families
without replacing the underlying receipts or owner-local authority.

`generated/candidate_lineage_summary.min.json` is the first growth-refinery
funnel slice. It reads reviewed owner-local lineage entries only and does not
pull raw checkpoint carry into stats.

`generated/supersession_drop_summary.min.json` is the bounded
growth-refinery followthrough slice. It reads explicit reviewed turnover
signals, including those carried by reviewed owner landing bundles and
seed-owner landing traces, without claiming owner truth. The standalone Owner
Landing aggregate is retired; its receipt vocabulary remains only because this
active turnover projection consumes it.

`generated/continuity_window_summary.min.json` is a committed cross-owner
reference slice. Its adapter reads the `aoa-agents` Continuity Window example,
the experimental `aoa-playbooks` route, the `aoa-memo` provenance example, and
the `aoa-evals` catalog definitions. A filesystem-free core validates ref,
timeline, playbook, and eval coherence before projection. The represented
status is not current workspace state, and reanchor counts require explicit
timeline actions rather than status inference.

`generated/component_refresh_summary.min.json` is the wave-ten component
refresh reference slice. Its committed adapter reads reviewed `aoa-sdk`
example drift hints and followthrough decisions, then passes an explicit bundle
to a filesystem-free projection core. The output preserves the represented
owner counts and refresh-status posture; it is not current workspace state and
does not outrank owner laws, owner receipts, or refresh validation.

`generated/memory_movement_summary.min.json` is the reviewed memory movement
slice. It reads `aoa-memo` reviewed corpus objects, the memory-object min
catalog, reviewed intake packets, and landing receipts. It keeps object counts,
recall posture, KAG-lift posture, and landing movement descriptive; `aoa-memo`
remains the memory authority. Its route boundary is read-only: `.aoa` session
evidence stays evidence until reviewed intake, local memo candidates require a
repo-local memo port, and durable memory still lands through reviewed source
patches in `aoa-memo`.

The published runtime-entry capsule is the schema-backed v2 contract:

- `schema_version`
- `schema_ref`
- `owner_repo`
- `surface_kind`
- `authority_ref`
- `artifact_identity`
- `surface_strength_model_ref`
- `generated_from`
- `validation_refs`
- `deferred_contract_surfaces`
- `surfaces`

Each entry in `surfaces` stays compact and low-context:

- `name`
- `surface_ref`
- `schema_ref`
- `primary_question`
- `derivation_rule`
- `input_posture`
- `owner_truth_inputs`
- `authority_ceiling`
- `consumer_risk`
- `live_state_capable`

Each entry in `deferred_contract_surfaces` keeps the same caution vocabulary
without pretending to be active:

- `name`
- `status=contract_only`
- `contract_ref`
- `schema_ref`
- `input_posture`
- `owner_truth_inputs`
- `activation_condition`
- `activation_gaps`
- `authority_ceiling`
- `consumer_risk`

The committed catalog contains every active public profile, including bounded
reference-only surfaces. Local live refresh treats `live_state_capable` as an
executable admission contract: it materializes only `true` profiles, writes a
live catalog only for outputs actually present, and cleans stale files across
the active outputs plus retired-output tombstones. The active read-model
inventory is 22, the retired cleanup inventory is three, and the authored
live-admitted inventory is 11. One additional Antifragility Vector profile is
deferred and has no output or catalog slot. Component Refresh, Continuity
Window, Codex Plane Deployment, trusted rollout-history, cadence examples,
Route Progression, Memory Movement, Stress Recovery, and Titan Incarnation are
active but excluded from live mode. Owner Landing, Titan Summon, and Runtime
Closeout are retired and remain cleanup targets only. The
selector and stale-cleanup
precedent is
`docs/decisions/AOST-D-0003-component-refresh-fixtures-are-not-live-state.md`,
which decides the Component Refresh case only. The cross-profile requirement
that live state have both a current owner source and an observable refresh
route is
`docs/decisions/AOST-D-0004-live-admission-requires-refresh-observation.md`.

Antifragility Vector remains an evidence-gated incubator. ATM10-Agent has a
real runtime publisher for one bounded `stressor_receipt_v1`, while its
`adaptation_delta_v1` is still schema/example only. The linked
`aoa-antifragility-posture` eval and report are draft/example surfaces, and
no repeated same-family window exists. The deferred profile projects these
exact owner refs, the partial input posture, high consumer risk, and all four
activation gaps. Its mechanic-local example is suppressed with null axes; no
builder, generated vector, live source registration, or MCP promotion follows
from catalog visibility. AOST-D-0011 records this incubation boundary.

Profile `catalog_order` values are stable slots rather than a dense ordinal.
Retired profiles reserve their former slots, active profiles may leave gaps,
and lifecycle removal does not renumber unrelated surfaces. Former mechanic
routes on a tombstone preserve provenance without forcing an empty operation
part to remain active. AOST-D-0009 records this source-home law.
Route Progression remains reference-only because its stable public bytes are a
legacy numeric compatibility projection while the current `aoa-skills` owner
receipt is semantic and deliberately not score-shaped. AOST-D-0005 forbids an
invented semantic-to-numeric mapping and requires semantic-only receipts to be
rejected rather than flattened into zero deltas.
Runtime Closeout is retired because its historical
`runtime_wave_closeout_receipt` snapshot has no current publisher or direct
consumer. The event kind remains generic intake evidence for active Object,
Repeated Window, and Source Coverage summaries, while the schema and slot 22
remain contract and cleanup history. AOST-D-0010 records the retirement;
AOST-D-0006 continues to forbid implicit aliasing with current `abyss-stack`
trial and `aoa-sdk` return contracts.
Titan Incarnation remains reference-only because it validates three committed
owner examples rather than current incarnations. Titan Summon had no observed
owner ledger, so its self-identifying no-ledger zero baseline is retired rather
than presented as an active statistic. The output, builder, and catalog entry
are absent; its schema remains contract history and its retired profile keeps
stale cleanup explicit. AOST-D-0008 records that lifecycle. Any observed
successor requires a new active profile, owner-local ledger, refresh
observation, and public-contract review.
Continuity Window remains
reference-only because its current cross-owner inputs are examples, an
experimental playbook, and draft catalog definitions rather than a real
owner-runtime artifact or receipt. Codex Plane Deployment remains
reference-only because its three committed owner examples are weaker than the
deploy-local trust, regeneration, and rollout artifacts. Its explicit live
adapter has no example fallback.
Trusted rollout-history is reference-only because its four inputs are
checked-in owner history, not deploy-local state. Rollout Campaign and Drift
Review are reference-only because they project a separate three-example chain,
not an active cadence producer.
Owner Landing is retired because its event kinds have no real publisher and no
direct consumer requires the standalone example aggregate. Its stable schema
and event ABI remain, while explicit landing turnover continues to feed
Supersession Drop. AOST-D-0009 also reserves its former catalog slot and
forbids preserving an empty mechanic part. Stress Recovery remains
reference-only because its eval/report chain is draft and example-backed.
Memory Movement reads authentic reviewed
`aoa-memo` corpus truth, but no automatic refresh trigger observes that corpus;
the committed snapshot is retained without advertising stale local live state.

`artifact_identity` describes the catalog as a public generated observability
read-model with an ABI epoch, contract version, consumer checks, privacy
boundary, and provenance lineage posture. It is not a release signature and it
does not make stats stronger than the owner-local receipts, verdicts, or source
surfaces it summarizes.

The OS Abyss artifact-bundle validator wraps this catalog with ABI verification,
SBOM-lite subject inventory, lifecycle registration, and a registry latest
read-model. It also rehearses trust-gate admission and isolated subject-store
materialization without making stats stronger than owner-local evidence. It does
not claim SLSA, Sigstore/Cosign, or C2PA until the catalog becomes an external
release/export bundle or public media export.

## Canonical split

- counts answer: how often and how widely
- kernel usage answers: which project-core skills are really finishing and with which bounded detail receipts
- verdicts answer: how well on one bounded surface
- progression answers: what changed on named axes
- evidence refs answer: where to inspect next

`object_summary`, `repeated_window_summary`, and
`surface_detection_summary` are inclusive of active receipts only, not of
superseded raw history.

`repeated_window_summary` groups those admitted receipts by the calendar-date
prefix carried in `observed_at`. Its deterministic counts describe activity
seen in each bucket; they do not compare state or prove change, recurrence,
cadence, causality, or owner chronology. The pure transformation lives in
`src/aoa_stats_builder/repeated_window.py`, with focused proof under the
Recurrence mechanic and root publication paths preserved.

`source_coverage_summary` is the self-audit that says which owner repos are
actually represented in the active feed and where the stats layer is still
thin. It stays weaker than both the live source registry and the owner-local
receipt logs it counts.
