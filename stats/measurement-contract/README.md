# Measurement contract

This branch defines the smallest shared language by which OS Abyss owners can
publish statistically comparable facts without surrendering domain meaning to
`aoa-stats`.

## Two source objects

| Object | Purpose | Source |
| --- | --- | --- |
| measurement contract | owner-authored identity, population, unit, dimensions, aggregation, uncertainty, privacy, and lifecycle | `measurement-contract.schema.json` |
| measurement packet | one evidence-linked observation or derived statistic made under that contract | `measurement-packet.schema.json` |

The contract answers what may be measured. The packet answers what was
observed, over which population and window, with which evidence and reporting
rule. A packet never promotes itself into proof, route state, memory truth, or
runtime authority.

## Vocabulary

`semantic_class` distinguishes a raw measure, a reusable metric, a statistic,
a reporting view, a bounded signal, and an explicitly scoped score.
`statistic` names the mathematical shape. `pass_at_k` means at least one
success among `k`; `pass_all_k` is the portable identifier for `pass^k`, where
all selected attempts succeed.

An observed zero is data only when the owner contract says so. Missing,
unknown, and stale packets carry no numeric value. Quantiles and distributions
retain sample size and population identity; they are not silently pooled when
their source representation cannot support valid aggregation.

## Ownership

The shared schema owns compatibility. A local root `stats/` port owns the
question, object, population definition, admissible dimensions, evidence
handoff, privacy posture, and whether a live export exists. The pure semantic
implementation is reached through the reciprocal Boundary Bridge part;
filesystem, runtime, generated, and MCP surfaces remain adapters.

## Read boundary

`packet-read-request.schema.json` and `packet-read-result.schema.json` define
the stable transport-neutral boundary for checking one supplied contract and
packet. A successful result carries deterministic evidence and semantic
identities plus the owner and access authority ceilings. An incompatible
packet remains an inspectable compatibility result with no identity claim;
an invalid request envelope is a protocol error.

The public entrypoint is `scripts/read_measurement_packet.py`. It accepts the
versioned request on standard input and emits the versioned result on standard
output. It does not discover repositories, open owner files, validate source
truth, or require an MCP runtime.
