# Recurrence part routes

Five recurrence parts are active:

- `live-receipt-refresh/` — source-registry audit and deterministic live view
  rebuilds
- `component-manifests/` — component recurrence and hook declarations for
  stats surfaces
- `component-refresh/` — bounded component-refresh summary posture
- `continuity-window/` — bounded continuity-window summary posture
- `repeated-window/` — repeated-window derivation and public-contract route

Operation-owned payload is local to the selected part. Consult
`mechanics/topology.json` for exact public compatibility routes and the paired
stats source-family crosswalk.
