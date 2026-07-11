from __future__ import annotations

from collections.abc import Callable
from collections import Counter, defaultdict
from typing import Any

from .object_observation import object_key


ObjectIdentity = Callable[[dict[str, Any]], tuple[str, str, str, str]]


def build_repeated_window_summary(
    receipts: list[dict[str, Any]],
    source: dict[str, Any],
    *,
    object_identity: ObjectIdentity = object_key,
) -> dict[str, Any]:
    """Group admitted receipt activity by its observed calendar-date label."""

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        grouped[receipt["observed_at"][:10]].append(receipt)

    windows: list[dict[str, Any]] = []
    for window_date in sorted(grouped):
        group = grouped[window_date]
        event_counts = Counter(receipt["event_kind"] for receipt in group)
        unique_objects = {
            object_identity(receipt["object_ref"]) for receipt in group
        }
        windows.append(
            {
                "window_id": f"window:{window_date}",
                "window_date": window_date,
                "total_receipts": len(group),
                "unique_objects": len(unique_objects),
                "event_counts_by_kind": dict(sorted(event_counts.items())),
                "eval_result_count": event_counts.get("eval_result_receipt", 0),
                "progression_delta_count": event_counts.get(
                    "progression_delta_receipt", 0
                ),
                "automation_candidate_count": event_counts.get(
                    "automation_candidate_receipt", 0
                ),
                "evidence_ref_count": sum(
                    len(receipt["evidence_refs"]) for receipt in group
                ),
            }
        )

    return {
        "schema_version": "aoa_stats_repeated_window_summary_v1",
        "generated_from": source,
        "windows": windows,
    }
