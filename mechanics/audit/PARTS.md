# audit parts

| Part | Stats operation |
| --- | --- |
| `core-skill-application` | Publishes finish-stage application observations through the shared core-skill observation core. |
| `object-observation` | Publishes deterministic occurrence and recency observations through its own part-specific core. |
| `source-coverage` | Audits which owner feeds and event families are represented. |
| `surface-strength-detection` | Exposes explicit advisory detection context through the shared core-skill observation core. |
| `drift-shadow-review` | Projects review posture from committed cadence examples without replacing source review. |

Only these directories are active parts. Their payload placement and retained
public-root routes are enumerated by `mechanics/topology.json`.

`core-skill-application` and `surface-strength-detection` share one package
test district because both consume the same finish-stage core-skill receipt
family. `object-observation` has a separate core and part-local test district
because it groups the wider active receipt set by object identity. This shared
code boundary does not extend to `source-coverage` or `drift-shadow-review`.
