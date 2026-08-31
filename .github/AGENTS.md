# AGENTS.md

## Guidance for `.github/`

`.github/` is the GitHub platform surface: workflows, PR templates, issue
templates, CODEOWNERS, and repository metadata. Read the root route card and
the nearest platform file when a GitHub surface is the named task.

Keep this district public-safe, deterministic, and weaker than authored source
docs. Do not encode sibling-repo doctrine, private workspace assumptions,
secrets, or hidden release behavior. Workflow changes must not mutate sibling
repositories or weaken a guard merely to obtain a green result.

## Platform sync

Keep `.github/CODEOWNERS`, PR templates, and workflow names aligned with the
root route and the procedure in `docs/RELEASING.md`. `Repo Validation` is the
landing check named by the repository release surface; its meaning and any
rename must be reflected in the owning route docs.

## Conditional validation and closeout

When this district changes, open the root `VALIDATION.md` and the affected
workflow or template's static checks. Report the GitHub surface touched, local
checks actually run, whether `Repo Validation` was added, renamed, skipped, or
changed, and remaining platform risk. CI, review, merge, and post-landing
acceptance remain separate observations owned by the GitHub/release surfaces.
