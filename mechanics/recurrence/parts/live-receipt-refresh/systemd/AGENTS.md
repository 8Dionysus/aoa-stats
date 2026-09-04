# AGENTS.md

## Live-receipt-refresh systemd templates

This directory holds checked-in user-service templates for the live refresh
loop. When a unit or installer is selected, follow the template, installer,
and nearest part validation route.

Systemd units are operator installation aids. They do not prove freshness,
authority, or successful owner publication. Templates render concrete user
units from explicit operator paths; keep units user-scoped, paths explicit, and
free of secrets.

Do not add privileged units, private credentials, or auto-start behavior that
silently watches or mutates source repositories. Installation scripts must
keep intended changes visible before activation.

## Conditional validation

Use the live-receipt-refresh `VALIDATION.md` route for installer and template
checks. Report rendering, operator intent, and any runtime/freshness evidence
separately.
