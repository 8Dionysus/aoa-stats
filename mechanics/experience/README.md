# Experience mechanic

`mechanics/experience/` is the local implementation of the common
`Agents-of-Abyss/mechanics/experience` mechanic for `aoa-stats`.

It turns Experience-shaped owner signals into bounded, schema-backed stats
contracts without making stats the owner of adoption, governance, service,
release, runtime, or proof truth.

## Active parts

| Part | Operation | Payload files |
| --- | --- | ---: |
| `micro-friction-receipts` | model bounded friction receipt, recurrence, and inbox summaries | 8 |
| `adoption-federation-harvest` | model adoption, federation recurrence, harvest, retention, rollback, and noise signals | 40 |
| `governance-runtime-signals` | model appeal, policy, veto, queue, and bounded governance readouts | 20 |
| `release-watch-office-health` | model certification, watch, rollback, installation, office, and release-train health | 50 |

The 118 payload files are part-local. Root publication and compatibility
surfaces remain separate and must be justified explicitly.

## Route

Start with `PARTS.md`, then read the selected part's `README.md`, `CONTRACT.md`,
and `VALIDATION.md`.
