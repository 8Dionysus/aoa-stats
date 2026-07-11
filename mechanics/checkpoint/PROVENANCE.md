# checkpoint provenance

The common mechanic vocabulary comes from
`Agents-of-Abyss/mechanics/checkpoint`.

The payload in this package was regrouped
from aoa-stats root districts by operation, preserving content and stable
public publication paths.

The topology records current localized and retained public routes only;
former root placement remains recoverable from Git rename history.

The Checkpoint center landed as `Agents-of-Abyss` commit `090fbf2`; agent-side
checkpoint payload and check localization landed as `aoa-agents` commits
`f6d8cf8` and `cb8332b`. The stats-side localization follows that same
part-owned payload/check shape without copying center or agent authority.

`abyss-stack` commit `27b8035` introduced the historical runtime-wave receipt.
At the current tracked owner pin `f41621e`, its active local-trials producer
writes `runtime_trial_closeout_receipt` to `runtime-trial-closeouts.jsonl`,
while the pre-cycle stats registry and abyss-stack watcher snapshot name the
earlier wave receipt and feed. The active repo-local aoa-stats registry now
excludes that feed. At the 2026-07-11 audit, the installed symlinked unit still
launched the older `/srv/AbyssOS/aoa-stats` projection and could admit it
through that projection's registry. Re-grounding the deployed plane requires
an explicit abyss-stack/deploy handoff; the repo installer must not overwrite
the symlink target from an ephemeral checkout. The mismatch is retained as
explicit provenance and blocks live admission; it is not normalized away.
