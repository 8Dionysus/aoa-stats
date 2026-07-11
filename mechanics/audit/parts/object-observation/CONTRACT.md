# Object-observation contract

## Input and derivation

- Consume the active receipt set only after shared admission and supersession
  resolution.
- Group receipts by their bounded object identity without consulting owner
  repositories or manufacturing an identity that the receipts do not carry.
- Preserve the supplied-order first receipt as `first_observed_at`.
- Select the overall latest receipt by maximum `(observed_at, event_id)` for
  `last_observed_at`, latest session/run refs, and the published `object_ref`.
- Preserve the supplied-order last evaluation verdict and supplied-order last
  progression verdict within their respective event families.
- Do not mutate the admitted receipt collection while projecting the view.

## Output and compatibility

- Publish `generated/object_summary.min.json` against
  `schemas/object-summary.schema.json`.
- `src/aoa_stats_builder/object_observation.py` is the sole deterministic core
  for this part.
- `scripts/build_views.py` retains the historical object helper and builder
  names as compatibility aliases plus repo-wide fan-out; it does not own
  duplicate grouping or recency logic.

## Authority stop-line

Receipt owners retain object identity, event, verdict, progression, and source
health truth. Recency and occurrence counts are derived observations only;
they cannot prove an object is current, valid, healthy, complete, or correctly
routed.

The mixed input-first, temporal-latest, and input-last-within-family selectors
are compatibility debt retained for byte and facade stability. They are not a
canonical owner chronology. Normalizing them requires a separate behavior
change and public-output review.
