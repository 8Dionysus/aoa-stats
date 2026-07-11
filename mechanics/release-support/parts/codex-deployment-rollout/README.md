# codex-deployment-rollout

This part owns the bounded Codex Plane Deployment projection and its explicit
committed-reference versus deploy-local source seam. It keeps deployment
observability weaker than the trust, regeneration, rollout, and doctor evidence
that owns current workspace state.

- source profile:
  `stats/read-models/active/codex_plane_deployment_summary.profile.json`
- guide: `docs/CODEX_PLANE_DEPLOYMENT_SUMMARIES.md`
- public schema: `schemas/codex-plane-deployment-summary.schema.json`
- retained public example: `examples/codex_plane_deployment_summary.example.json`
- committed output: `generated/codex_plane_deployment_summary.min.json`
- filesystem-free core: `src/aoa_stats_builder/codex_plane_deployment.py`
- reference/live adapters:
  `src/aoa_stats_builder/codex_plane_deployment_sources.py`
- root compatibility facade: `scripts/build_views.py`
- checks: `VALIDATION.md`

Checked-in rollout history belongs to the sibling
`trusted-rollout-history` part. Cadence examples belong to `rollout-campaign`
and `drift-shadow-review`. They are not deployment inputs.
