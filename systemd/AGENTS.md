# AGENTS.md
Local guidance for `systemd/` in `aoa-stats`.

Read the root `AGENTS.md` first. This directory may hold user-service surfaces
for live refresh loops.

## Local role
Systemd units are operator installation aids. They do not prove freshness,
authority, or successful owner-repo publication by themselves.

## Editing posture
Keep units user-scoped, explicit about repo paths, and free of secrets. Prefer
installation scripts that show what they would change before activating loops.

## Hard no
Do not add privileged units, private credentials, or auto-start behavior that
silently watches or mutates source repos.

## Validation
Run:

```bash
python scripts/check_live_publishers.py
python scripts/install_live_refresh_units.py --help
```
