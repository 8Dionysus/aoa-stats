# Drift Shadow Review contract

This part projects explicit review posture from the immutable three-example
cadence bundle loaded and validated by `rollout_cadence_sources.py` and
filesystem-free `rollout_cadence.py`.

The review and rollback examples must point to the campaign example; reference
grammars, exact v1 fields, booleans, timestamps, positive drift evidence,
decision/status combinations, and rollback-review posture must all validate
before projection. Missing decision or status fields are invalid and may not be
converted into empty, closed, or retired defaults.

The part does not own campaign projection, checked-in trusted-history drift,
rollback decisions, or the wider owner check against
`rollout_latest.min.json`. Its authored profile is reference-only; local live
refresh omits it and cleans stale managed copies.

The result never becomes proof, routing, gate, identity, campaign, review,
rollout, or rollback truth.
