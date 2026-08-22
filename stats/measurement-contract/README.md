# Measurement contract

This branch defines the smallest shared language by which OS Abyss owners can
publish statistically comparable facts without surrendering domain meaning to
`aoa-stats`.

## Source objects

| Object | Purpose | Source |
| --- | --- | --- |
| measurement contract | owner-authored identity, population, unit, dimensions, aggregation, uncertainty, privacy, and lifecycle | `measurement-contract.schema.json` |
| measurement packet | one evidence-linked observation or derived statistic made under that contract | `measurement-packet.schema.json` |
| outcome receipt | one content-minimized C10 observation of action before/after memory, memory-use state, terminal and delayed outcomes, confounders, accidental success, harm, costs, and attribution uncertainty | `outcome-receipt.schema.json` |
| validation telemetry packet | one owner-linked, content-minimized observation of validation-node resources, result, identity, cache/receipt posture, first failure, rerun amplification, and source coverage | `validation-telemetry-packet.schema.json` |

The contract answers what may be measured. The packet answers what was
observed, over which population and window, with which evidence and reporting
rule. A packet never promotes itself into proof, route state, memory truth, or
runtime authority.

The validation telemetry packet is a compatibility envelope for a later
Claim/Evidence Validation Graph shadow. It does not define the node's claim,
semantic sufficiency, budget, acceptance barrier, or validator meaning; those
remain with the owner. Candidate and environment identities require complete
kind/source/digest triples. Resource fields carry explicit missing, unknown, or
stale states and never encode an unavailable value as zero.

The outcome receipt is upstream measurement input, not a verdict. The task or
source owner owns its action and outcome facts; `aoa-stats` owns only the C10
shape and cross-field compatibility. `aoa-evals` may attach independently
owned counterfactual or verdict refs, but C10 always keeps `causal_claim`,
semantic authority, effect authority, and training use forbidden. Unknown
memory use remains unknown. Missing or incomplete before/after snapshots
cannot be upgraded into supported attribution.

The receipt carries refs and digests instead of raw prompts, memory payloads,
task contents, or transcripts. An actionable after-memory snapshot requires a
separate current-source effect binding owned outside memory. Harm, delayed
outcomes, and costs stay visible even when the terminal task result looks
successful.

C10 also binds the task and consumer, exact experiment assignment, randomized
holdout posture, always-shadow counterfactual, host observations, evaluator,
operator intervention, and evaluation-plane posture. Supported attribution
requires independently owned judge and integrity evidence, model-version
stratification, host evidence, complete action snapshots, task-owner
acceptance, and a paired or randomized counterfactual route. Access count is
never utility. Outcome data may support a policy proposal only; it cannot
authorize semantic promotion, deletion, retraction, or any other memory
transition. An unavailable or degraded eval plane freezes policy updates.

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

`scripts/validate_stats_protocol.py --outcome-receipt <path>` validates C10
shape and pure cross-field semantics. It does not resolve or endorse any
referenced owner fact.

## Compatibility

`OutcomeReceipt` version `1.0.0` is strict and fails closed on unknown fields or
versions. Once landed, v1 is immutable. A semantic change requires a new
versioned schema, explicit old-versus-new fixtures, consumer migration
evidence, and a bounded compatibility window; rewriting this schema in place
is not a migration. No owner-local writer or runtime route is activated by the
central contract alone.

`content_digest` is a normalized self-digest: validation replaces that field
with the v1 all-zero SHA-256 token before canonical JSON hashing. Any content
change therefore invalidates the old receipt digest.
