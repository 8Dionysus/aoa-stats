# AGENTS.md
Local guidance for the live-receipt-refresh systemd templates.

Read the repository root and recurrence route cards first. This directory
holds the checked-in user-service templates for the live refresh loop.

## Local role
Systemd units are operator installation aids. They do not prove freshness,
authority, or successful owner-repo publication by themselves.
The checked-in unit files are templates; `scripts/install_live_refresh_units.py`
renders concrete user units from explicit operator paths.

## Editing posture
Keep units user-scoped, explicit about repo paths, and free of secrets. Prefer
installation scripts that show what they would change before activating loops.

## Hard no
Do not add privileged units, private credentials, or auto-start behavior that
silently watches or mutates source repos.

## Validation
Run:

```bash
python scripts/install_live_refresh_units.py --help
python -m pytest -q mechanics/recurrence/parts/live-receipt-refresh/tests/test_install_live_refresh_units.py
```
