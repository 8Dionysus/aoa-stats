# Titan Summon Metrics

The committed v1 surface is a compatibility baseline for the case where no
owner swarm-ledger instance was observed. Its four zero fields mean “no ledger
was projected”; they are not measurements of a zero-activity swarm.

An observed successor may derive the following only from an owner-local ledger
or closeout artifact whose contract and refresh route are explicit:

- `agents_invoked`
- `reports_received`
- `findings_reported`
- `memory_candidates_created`

Further finding lifecycle, timeout, interruption, grade, orchestration, and
prompt-fault measures require their own public contract review; they are not
silently implied by the current v1 shape.

Stats are pulse, not verdict.
