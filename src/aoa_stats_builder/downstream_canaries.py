from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

REQUIRED_CANARIES = (
    {
        "repo": "aoa-sdk",
        "relative_path": (
            "mechanics/recurrence/parts/downstream-projection-guard/"
            "docs/stats-regrounding-policy.md"
        ),
        "needles": (
            "Stats says what is derived and where its feed is thin.",
            "Owner repos still decide source truth.",
        ),
    },
    {
        "repo": "aoa-sdk",
        "relative_path": (
            "mechanics/boundary-bridge/parts/consumed-surface-posture-gate/"
            "docs/routing-consumer-contract.md"
        ),
        "needles": (
            "aoa-stats/generated/stress_recovery_window_summary.min.json",
            "must not require an `aoa-routing` checkout",
        ),
    },
    {
        "repo": "aoa-memo",
        "relative_path": (
            "mechanics/antifragility/docs/RECOVERY_PATTERN_RECALL.md"
        ),
        "needles": (
            "derived stats summaries and reviewed route hints",
            "does not overrule source-owned receipts, eval proof, or derived stats",
        ),
    },
    {
        "repo": "aoa-evals",
        "relative_path": (
            "mechanics/publication-receipts/parts/receipt-payload/"
            "docs/EVAL_RESULT_RECEIPT_GUIDE.md"
        ),
        "needles": (
            "`aoa-stats` owns the shared cross-repo receipt envelope and active event-kind",
            "vocabulary used for downstream derivation",
        ),
    },
)


def validate_downstream_canaries(
    *,
    workspace_root: Path,
    repo_roots: Mapping[str, Path] | None = None,
) -> dict[str, list[str]]:
    checked: list[str] = []
    skipped: list[str] = []
    errors: list[str] = []
    explicit_roots = dict(repo_roots or {})

    for spec in REQUIRED_CANARIES:
        repo = spec["repo"]
        repo_root = explicit_roots.get(repo, workspace_root / repo)
        path = repo_root / spec["relative_path"]
        label = f"{repo}/{spec['relative_path']}"
        if not path.exists():
            if repo in explicit_roots or repo_root.exists():
                errors.append(
                    f"{label}: required downstream canary is missing from "
                    "the available owner checkout"
                )
            else:
                skipped.append(label)
            continue
        text = path.read_text(encoding="utf-8")
        checked.append(label)
        for needle in spec["needles"]:
            if needle not in text:
                errors.append(f"{label}: missing canary text {needle!r}")

    return {"checked": checked, "skipped": skipped, "errors": errors}
