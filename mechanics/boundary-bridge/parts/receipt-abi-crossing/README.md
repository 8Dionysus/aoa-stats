# Receipt ABI crossing

This part routes the narrow crossing by which source-owned event payloads enter
the shared stats receipt envelope without transferring payload ownership.

## Status

- mechanic: `boundary-bridge`
- stats source family: `intake_contract`
- payload route: `mixed localized/public`
- active contract: `CONTRACT.md`
- validation route: `VALIDATION.md`

The focused governance test lives in this part. The published envelope and
public validation command remain at the root paths declared in
`mechanics/topology.json`; the authored registry lives in
`stats/intake-contract/`.
