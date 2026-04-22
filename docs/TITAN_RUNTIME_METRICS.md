# Titan Runtime Metrics

Titan runtime metrics are derived from receipts. They do not own session truth.

## Metrics

- sessions opened
- sessions closed
- Forge activation count
- Delta activation count
- receipts with missing closeout
- memory candidates proposed
- validation failures

## Derivation source

`aoa-sdk` Titan receipts are the input. `aoa-stats` may summarize but must not mutate receipts.

## Failure signals

- Forge activated without mutation gate
- Delta activated without judgment gate
- closed receipt missing summary
- receipt with unknown Titan name
