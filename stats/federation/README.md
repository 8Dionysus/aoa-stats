# Stats federation

Every active OS Abyss owner receives a root `stats/` surface unless its owner
boundary proves that a stronger owner must carry the port. The central layer
defines compatibility; each local port defines what is meaningful to measure
there.

## Local port

`local-port.schema.json` describes one owner-local manifest. A port names its
owner boundary, real questions and consumers, measurement contracts, evidence
posture, and any actual exports. It references the shared measurement schemas
instead of copying their doctrine.

A declaration-only measurement is honest when no producer exists. It is not a
live statistic. Reference and live exports must point to owner evidence and
retain missingness, freshness, privacy, and authority ceilings.

Port validation follows each repository-relative packet ref from the local
manifest, checks that the path stays inside the owner root, validates packet
shape and semantics against the embedded measurement contract, and requires
the packet's contract pointer and live/reference posture to match its export.
The local manifest therefore remains the single contract source; owners do not
need duplicate standalone contract files.

## Integration

Owner validation delegates local port and packet checks to the central
validator through an explicit `aoa-stats` dependency root; it does not copy the
shared grammar. A missing central validator is a hard failure, never a silent
skip. Reproducible release lanes pin the central revision they validate
against. An intentionally labelled latest-sibling canary may instead track the
latest central revision so compatibility drift is detected early.

## Inventory

`owner-inventory.json` is the canonical repo-level coverage map and validates
against `owner-inventory.schema.json`. It records owner identities and portable
workspace routes, not local checkout paths. Significant runtime surfaces that
are not separate source owners are routed to their stronger owners rather than
counted twice.

The inventory is updated only when an owner port or owner-level exception has
actually landed. Presence never proves semantic quality; local manual journeys
and owner proof remain necessary.
