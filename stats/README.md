# Stats source home

`stats/` is the source-authored home for the meaning and authority ceilings of
`aoa-stats` families. It tells a reader what the repository may derive and
routes that meaning to current contracts, implementation, outputs, validators,
and mechanics.

It is not an importable Python package, generated-output directory, receipt
store, runtime state home, or second copy of root contracts.

## Operating card

| Field | Route |
| --- | --- |
| role | source home for stats-authored meaning and lifecycle |
| source map | `source_home.manifest.json` |
| local law | `AGENTS.md`, then the selected family `AGENTS.md` |
| operation map | `../mechanics/topology.json` |
| generated discovery | `../generated/summary_surface_catalog.min.json` |
| rationale | `../docs/decisions/README.md` and generated indexes |
| validation | `AGENTS.md#verify`, then the selected family or mechanic part owner |

## Shape

```text
stats/
├── AGENTS.md
├── README.md
├── source_home.manifest.json
├── intake-contract/
├── read-models/
│   ├── active/
│   ├── deferred/
│   └── retired/
├── operation-contracts/
└── surface-catalog/
```

## Family map

| Family | Owns | Start here |
| --- | --- | --- |
| intake contract | shared envelope and event-kind admission, below payload owners | `intake-contract/README.md` |
| read models | authored public, deferred, and retired surface lifecycle | `read-models/README.md` |
| operation contracts | bounded non-catalog questions and owner-return posture | `operation-contracts/README.md` |
| surface catalog | compact discovery and consumer caution posture | `surface-catalog/README.md` |

The exact root, implementation, validator, generated, access, and mechanic
routes are declared in `source_home.manifest.json`. Family README files are
human atlases; their nearest `AGENTS.md` and authored records own local law.

## Authority chain

Use the smallest source that owns the question:

| Question | Source |
| --- | --- |
| What does this public summary mean now? | its file under `read-models/active/` |
| Why is a candidate not active? | its deferred profile and linked decision |
| Why is a former output absent? | its retired tombstone and `decision_ref` |
| What may a non-catalog part observe? | its record under `operation-contracts/active/` |
| Where does operation payload live? | reciprocal part in `mechanics/topology.json` |
| What is currently generated? | generated catalog/read model, checked against its source |
| Why was a material boundary chosen? | source decision under `docs/decisions/` |

Do not copy those changing facts into this README. A current roster belongs in
authored records or generated lookup, not in an entrypoint snapshot.

## Root districts

Canonical public schemas remain under `schemas/`; committed derived outputs
remain under `generated/`; implementation remains under `src/`; public and
compatibility commands remain under `scripts/`; focused operation payload and
proof remain under `mechanics/`.

The repo-local MCP reads derived surfaces only. It does not own profile state,
source facts, proof, routing, workflow, memory, or runtime truth.

## Stop lines

- Do not add Python, generated payload, runtime state, or owner-local feeds
  under `stats/`.
- Do not hand-edit a generated catalog as source.
- Do not let a profile or operation record outrank stronger-owner inputs.
- Do not infer live state from a committed example or resolvable adapter.
- Do not keep a named surface-status roster in this entrypoint.

## Validation

Use [`AGENTS.md#verify`](AGENTS.md#verify), then the focused validator and tests
owned by the family or mechanic part you change. Release closeout stays in
[`../docs/RELEASING.md`](../docs/RELEASING.md).
