from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


def object_key(object_ref: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        object_ref["repo"],
        object_ref["kind"],
        object_ref["id"],
        object_ref.get("version", ""),
    )


def build_object_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        grouped[object_key(receipt["object_ref"])].append(receipt)

    objects: list[dict[str, Any]] = []
    for key in sorted(grouped):
        group = grouped[key]
        by_kind = Counter(receipt["event_kind"] for receipt in group)
        latest = max(
            group,
            key=lambda receipt: (receipt["observed_at"], receipt["event_id"]),
        )
        latest_eval = None
        latest_progression = None
        automation_total = 0
        automation_seed_ready = 0
        automation_checkpoint_required = 0
        for receipt in group:
            payload = receipt["payload"]
            if receipt["event_kind"] == "eval_result_receipt":
                latest_eval = payload.get("verdict")
            if receipt["event_kind"] == "progression_delta_receipt":
                latest_progression = payload.get("verdict")
            if receipt["event_kind"] == "automation_candidate_receipt":
                automation_total += 1
                if payload.get("seed_ready") is True:
                    automation_seed_ready += 1
                if payload.get("checkpoint_required") is True:
                    automation_checkpoint_required += 1

        object_ref = dict(latest["object_ref"])
        objects.append(
            {
                "object_ref": object_ref,
                "receipt_count_total": len(group),
                "receipt_counts_by_event_kind": dict(sorted(by_kind.items())),
                "first_observed_at": group[0]["observed_at"],
                "last_observed_at": latest["observed_at"],
                "latest_session_ref": latest["session_ref"],
                "latest_run_ref": latest["run_ref"],
                "evidence_ref_count": sum(
                    len(receipt["evidence_refs"]) for receipt in group
                ),
                "latest_eval_verdict": latest_eval,
                "latest_progression_verdict": latest_progression,
                "automation_candidate_counts": {
                    "total": automation_total,
                    "seed_ready": automation_seed_ready,
                    "checkpoint_required": automation_checkpoint_required,
                },
            }
        )

    return {
        "schema_version": "aoa_stats_object_summary_v1",
        "generated_from": source,
        "objects": objects,
    }
