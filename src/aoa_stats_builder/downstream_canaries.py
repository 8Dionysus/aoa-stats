from __future__ import annotations

from pathlib import Path

REQUIRED_CANARIES = (
    {
        "repo": "aoa-sdk",
        "relative_path": "docs/aoa-surface-detection-second-wave.md",
        "needles": ("aoa-stats", "descriptive only"),
    },
    {
        "repo": "aoa-routing",
        "relative_path": "README.md",
        "needles": (
            "aoa-stats/generated/stress_recovery_window_summary.min.json",
            "does not replace `recommended_paths.min.json`, `owner_layer_shortlist.min.json`",
        ),
    },
    {
        "repo": "aoa-memo",
        "relative_path": "docs/RECOVERY_PATTERN_RECALL.md",
        "needles": (
            "derived stats summaries and reviewed route hints",
            "does not overrule source-owned receipts, eval proof, or derived stats",
        ),
    },
    {
        "repo": "aoa-evals",
        "relative_path": "docs/EVAL_RESULT_RECEIPT_GUIDE.md",
        "needles": (
            "`aoa-stats` owns the shared cross-repo receipt envelope and active event-kind",
            "vocabulary used for downstream derivation",
        ),
    },
)


def validate_downstream_canaries(*, workspace_root: Path) -> dict[str, list[str]]:
    checked: list[str] = []
    skipped: list[str] = []
    errors: list[str] = []

    for spec in REQUIRED_CANARIES:
        path = workspace_root / spec["repo"] / spec["relative_path"]
        label = f"{spec['repo']}/{spec['relative_path']}"
        if not path.exists():
            skipped.append(label)
            continue
        text = path.read_text(encoding="utf-8")
        checked.append(label)
        for needle in spec["needles"]:
            if needle not in text:
                errors.append(f"{label}: missing canary text {needle!r}")

    return {"checked": checked, "skipped": skipped, "errors": errors}
