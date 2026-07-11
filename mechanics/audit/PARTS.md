# audit parts

| Part | Stats operation |
| --- | --- |
| `core-skill-application` | Publishes the bounded core-skill application read model. |
| `object-observation` | Publishes occurrence and recency observations for source objects. |
| `source-coverage` | Audits which owner feeds and event families are represented. |
| `surface-strength-detection` | Exposes advisory detection signals without routing authority. |
| `drift-shadow-review` | Summarizes checked-in drift review posture without replacing source review. |

Only these directories are active parts. Their payload placement and retained
public-root routes are enumerated by `mechanics/topology.json`.
