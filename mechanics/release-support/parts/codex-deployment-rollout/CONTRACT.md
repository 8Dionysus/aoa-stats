# Codex Plane Deployment contract

## Purpose

Produce one deterministic Codex Plane deployment summary without allowing a
committed example to masquerade as current deploy-local state.

## Source modes

The committed `reference` mode reads exactly these owner-authored examples:

- `8Dionysus/examples/codex_plane_trust_state.example.json`
- `8Dionysus/examples/codex_plane_regeneration_report.example.json`
- `8Dionysus/examples/codex_plane_rollout_receipt.example.json`

The `live` mode reads only the matching deploy-local artifacts below an
explicit workspace root:

- `.codex/generated/rollout/codex_plane_trust_state.current.json`
- `.codex/generated/rollout/codex_plane_regeneration_report.latest.json`
- `.codex/generated/rollout/codex_plane_rollout_receipt.latest.json`

The `aoa-sdk` deploy-status API is a parallel typed consumer of the same live
artifacts. Its checked-in example is not owner truth and is not a stats input.

## Output

`generated/codex_plane_deployment_summary.min.json`, validated by
`schemas/codex-plane-deployment-summary.schema.json`. The compatibility example
remains at `examples/codex_plane_deployment_summary.example.json`.

## Adapter boundary

- `codex_plane_deployment_sources.py` owns path selection, JSON loading,
  immutable input bundles, and the strict separation of reference and live I/O
- filesystem-free `codex_plane_deployment.py` owns chain validation and
  deterministic projection
- `scripts/build_views.py` owns environment/default resolution, zero-argument
  compatibility calls, repo-wide fan-out, and explicit source-mode plumbing
- live refresh passes `live` and its workspace root; it never auto-prefers live
  state and never falls back to reference examples

## Invariants

- trust, regeneration, and receipt schema versions must match the published v1
  contracts
- trust and regeneration must name the same workspace root
- live trust state must name the actual workspace root selected by the adapter
- the receipt must reference the loaded trust-state and regeneration ids
- trust capture and regeneration timestamps must not postdate the rollout
  receipt; their mutual order remains owner-defined
- a `verified` deployment must carry `doctor_result: pass`
- stable MCP names come from the stronger trust/regeneration evidence, never
  from the weaker SDK example
- drift counts come only from explicit trust, regeneration, receipt, root,
  hook, doctor, or required stable-name evidence; additional project MCP names
  are not drift
- rollback counts require an explicit owner recommendation, any doctor failure,
  post-apply root/config drift, or applied/verified hook or stable-name drift;
  other pre-apply or rerollout-class drift remains drift only
- missing live artifacts omit the optional surface and stale cleanup still
  applies; invalid or mismatched artifacts fail validation
- the current authored profile remains `live_state_capable: false`
- the result never becomes proof, routing, gate, identity, workflow, rollout,
  or rollback authority

## Activation boundary

Future live activation is atomic: a real owner producer must emit a coherent
deploy-local trio, the typed SDK readout must succeed against it, the watcher or
refresh trigger must observe the trio, focused live validation must pass, and
only then may the authored profile change to `true`. Adding a new live ABI or
changing owner authority requires a separate decision review.

## Companion stop-line

Checked-in rollout-history operations and cadence Campaign/Drift examples are
not deployment inputs. History belongs to `trusted-rollout-history`; cadence
belongs to `rollout-campaign` and `drift-shadow-review`. This part must not
regain their builders, examples, profiles, tests, or mechanic routes.

## Crosswalk

This operation belongs to stats source family `read_models`; the profile owns
the bounded question and authority ceiling, while this part owns the repeatable
projection route.
