# Receipt ABI crossing

This part routes the narrow crossing by which source-owned event payloads enter
the shared stats receipt envelope without transferring payload ownership.

## Status

- mechanic: `boundary-bridge`
- stats source family: `intake_contract`
- payload route: `mixed localized/public`
- active contract: `CONTRACT.md`
- validation route: `VALIDATION.md`

Focused governance and feed-resolution tests live in this part. They constrain
the canonical crossing plus deterministic JSON/JSONL loading, latest-event
deduplication, and conservative supersedes handling. The published envelope,
root build facade, and public validation command remain at their declared
compatibility paths; the authored registry lives in `stats/intake-contract/`.
