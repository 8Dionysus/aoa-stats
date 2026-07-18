# Answer mode

Use this mode when a bounded statistical question already has owner meaning.
This includes a request asking whether a surface is present, covered, current,
or fresh. A negative, partial, stale, or unknown result remains an answer. Do
not use this mode to invent a metric or explain why a malfunction occurred.

## Inputs

- exact object or question and affected owner
- population, sample or cohort, window, value and unit, dimensions,
  numerator/denominator and aggregation when applicable
- missingness, uncertainty, privacy, freshness, and reporting posture
- selected authored route and requested temporal claim

Stop `blocked_missing_meaning` when material meaning is absent.

## Procedure

1. Restate the exact question and its requested time posture.
2. Use `source-return.md` to choose one authored route. Read owner-local meaning
   before a central inventory or derived view.
3. For current/live work, resolve the deployed runtime and live data root
   separately from the procedure source checkout. Follow only the profile or
   operation's declared inputs, mechanic, schema, output, and current
   observation route.
4. Compare unit, version, population, window, dimensions, privacy, and temporal
   posture before combining inputs.
5. Inspect the selected record or artifact manually. Preserve `missing`,
   `unknown`, `stale`, zero, fail, and partial as distinct states.
6. Return a `bounded-stats-answer` containing:
   - mode and exact question
   - measure/population/window shape when applicable
   - strongest owner sources and weaker observations inspected
   - compatibility, missingness, freshness, uncertainty, and privacy posture
   - bounded answer and authority ceiling
   - actual effects, verification, skipped checks, owner handoff, and stop line

A publisher's existence, parseability, artifact refresh time, count, trend, or
green command never establishes observation freshness, owner health, or OS
health by itself.

## Termination

Stop after one source-backed answer or `blocked_stale_or_unknown`. Do not
repair sources, rebuild outputs, or continue into diagnosis without a separate
selected operation.
