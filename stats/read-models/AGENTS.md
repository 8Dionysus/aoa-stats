# AGENTS.md

Route card for authored stats read-model profiles.

## Ownership

`stats/read-models/` owns the source-authored surface profiles that say what a
derived summary asks, which schema and output carry it, which stronger owners
remain authoritative, and which mechanics produce or refresh it. It does not
own Python implementation, generated output, mechanic payloads, or upstream
facts.

## Conditional route

When a profile is selected, follow the family README, the
`surface-profile.schema.json` schema, the target record under `active/`,
`deferred/`, or `retired/`, and every
schema, output, owner-input, decision, and mechanic route named by that record.
Entering this directory alone does not require the complete profile inventory.

## Profile law

- One active public catalog surface has one authored profile under `active/`.
- Contract-only candidates stay under `deferred/` with input posture, exact
  owner-truth inputs, activation gaps, consumer risk, and an authority ceiling.
- Removed public outputs leave only a minimal retired tombstone when cleanup
  evidence is needed. Retired profiles have no builder, catalog entry, or
  payload archive.
- Preserve `catalog_order` as a stable slot. Retired profiles reserve
  `former_catalog_order`; active profiles may leave gaps and must not reuse it.
- `mechanic_routes` are source-to-operation handoffs and do not move source
  meaning into mechanics.
- `live_state_capable` is executable source meaning. `true` admits local live
  materialization only with an observation route; `false` remains committed or
  reference-only and out of the live catalog.
- Do not add Python, generated catalogs, live receipts, or copied owner payloads
  here. Change authored profiles first and rebuild declared projections.
- Reintroducing a retired question requires a newly reviewed active profile,
  new slot, real owner evidence, a producer, and validation.
- Retired former mechanic routes are provenance, not active topology links.
- Keep profile-specific status in the target profile, mechanic contract,
  focused tests, and indexed decision. Derive focused proof ownership and
  lifecycle membership from topology and profile directories rather than fixed
  counts or a named part map in root tests.
- Do not copy named surface state into this family route card.

## Conditional validation and closeout

Use root `VALIDATION.md` for source-home and generated-parity selection, then
the exact mechanic-part route. Report profile inputs, lifecycle posture,
generated outputs, owner evidence, missing/stale conditions, and the stronger
owner boundary.
