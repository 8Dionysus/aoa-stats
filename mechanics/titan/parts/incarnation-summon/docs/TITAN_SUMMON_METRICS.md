# Retired Titan Summon Metrics Contract

The former committed v1 surface was a compatibility baseline for the case where
no owner swarm-ledger instance was observed. Because it projected no owner fact,
the builder, output, and catalog entry are retired. The v1 schema remains only
as contract history, and the source-home tombstone exists only to remove stale
copies from committed output, live state, and downstream consumer hints.

An observed successor may derive the following only from an owner-local ledger
or closeout artifact whose contract and refresh route are explicit:

- `agents_invoked`
- `reports_received`
- `findings_reported`
- `memory_candidates_created`

Further finding lifecycle, timeout, interruption, grade, orchestration, and
prompt-fault measures require their own public contract review; they are not
silently implied by the retired v1 shape. An observed successor must enter as a
new active profile backed by an owner-local ledger and refresh proof.

Stats are pulse, not verdict.
