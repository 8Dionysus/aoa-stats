# Agon parts

| Part | Wave | Operation | Root public output |
| --- | --- | --- | --- |
| `stats-prebinding` | VII | prebind derived stats views before live protocol | `generated/agon_stats_prebinding_registry.min.json` |
| `verdict-delta-scar-observability` | XI | observe verdict, delta, and scar candidate signals | `generated/agon_vds_stats_observability_registry.min.json` |
| `mechanical-trial-observability` | XIII | summarize mechanical-trial candidate surfaces | `generated/agon_mechanical_trial_stats_observability_registry.min.json` |
| `retention-rank-observability` | XIV | summarize retention and rank pressure without action | `generated/agon_retention_rank_stats_observability_registry.min.json` |
| `epistemic-observability` | XV | derive epistemic review summaries | `generated/agon_epistemic_stats_observability_registry.min.json` |
| `schools-lineages-campaigns-observability` | XVI | summarize school, lineage, and campaign signals | `generated/agon_slc_stats_observability_registry.min.json` |
| `kag-observability` | XVII | expose KAG promotion-pressure candidates without promotion | `generated/agon_kag_stats_observability_registry.min.json` |
| `sophian-observability` | XVIII | expose Sophian threshold candidates without canonization | `generated/agon_sophian_stats_observability_registry.min.json` |

Every part is `part_localized`: source payload is local to the operation and
only its declared generated registry remains root-published.
