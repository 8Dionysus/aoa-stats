# VIA_NEGATIVA_CHECKLIST

This checklist is for `aoa-stats` as the derived observability and
machine-first summaries.

## Keep intact

- derived summaries with clear consumer value
- suppression semantics for low evidence
- vector and window views that preserve signal shape

## Merge, move, suppress, quarantine, deprecate, or remove when found

- scalar prestige views
- summaries with no real reader or consumer
- derived docs that sound canonical rather than derived

## Questions before adding anything new

1. Who consumes this summary and why?
2. Can a vector survive where a score would distort?
3. Should this view suppress itself when evidence is thin?

## Safe exceptions

- a new derived view that unlocks a clear bounded consumer workflow
- short bridge docs needed to migrate away from bad scalar habits

## Exit condition

- Stats should stay derived, useful, and humble.
