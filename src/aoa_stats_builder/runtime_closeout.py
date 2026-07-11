from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


RUNTIME_CLOSEOUT_EVENT_KIND = "runtime_wave_closeout_receipt"


def runtime_closeout_identity(receipt: dict[str, Any]) -> tuple[str, str]:
    payload = receipt["payload"]
    program_id = payload.get("program_id")
    wave_id = payload.get("wave_id")
    if (
        isinstance(program_id, str)
        and program_id
        and isinstance(wave_id, str)
        and wave_id
    ):
        return program_id, wave_id

    object_id = str(receipt["object_ref"].get("id") or "")
    if ":" in object_id:
        fallback_program_id, fallback_wave_id = object_id.rsplit(":", 1)
        return (
            fallback_program_id or "unknown-program",
            fallback_wave_id or "unknown-wave",
        )
    return "unknown-program", receipt["session_ref"]


def build_runtime_closeout_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        if receipt["event_kind"] != RUNTIME_CLOSEOUT_EVENT_KIND:
            continue
        grouped[runtime_closeout_identity(receipt)].append(receipt)

    closeouts: list[dict[str, Any]] = []
    for key in sorted(grouped):
        program_id, wave_id = key
        group = grouped[key]
        latest = max(
            group, key=lambda receipt: (receipt["observed_at"], receipt["event_id"])
        )
        gate_counts: Counter[str] = Counter()
        handoff_counts: Counter[str] = Counter()
        for receipt in group:
            payload = receipt["payload"]
            gate_counts[str(payload.get("gate_result") or "unknown")] += 1
            handoff_counts[
                str(payload.get("reviewed_closeout_handoff_status") or "unknown")
            ] += 1

        latest_payload = latest["payload"]
        latest_truth_status = latest_payload.get("truth_status", {})
        if not isinstance(latest_truth_status, dict):
            latest_truth_status = {}
        closeouts.append(
            {
                "program_id": program_id,
                "wave_id": wave_id,
                "closeout_receipt_count": len(group),
                "latest_gate_result": str(
                    latest_payload.get("gate_result") or "unknown"
                ),
                "gate_result_counts": dict(sorted(gate_counts.items())),
                "latest_reviewed_closeout_handoff_status": str(
                    latest_payload.get("reviewed_closeout_handoff_status")
                    or "unknown"
                ),
                "reviewed_closeout_handoff_status_counts": dict(
                    sorted(handoff_counts.items())
                ),
                "latest_reviewed_closeout_audit_only": bool(
                    latest_payload.get("reviewed_closeout_audit_only")
                ),
                "latest_case_count": int(latest_payload.get("case_count") or 0),
                "latest_next_action": str(
                    latest_payload.get("next_action") or "unspecified"
                ),
                "latest_truth_status": {
                    "source_authored": bool(
                        latest_truth_status.get("source_authored")
                    ),
                    "deployed": bool(latest_truth_status.get("deployed")),
                    "trial_proven": bool(latest_truth_status.get("trial_proven")),
                    "live_available": bool(
                        latest_truth_status.get("live_available")
                    ),
                },
                "first_observed_at": group[0]["observed_at"],
                "last_observed_at": latest["observed_at"],
                "evidence_ref_count": sum(
                    len(receipt["evidence_refs"]) for receipt in group
                ),
            }
        )

    return {
        "schema_version": "aoa_stats_runtime_closeout_summary_v1",
        "generated_from": source,
        "closeouts": closeouts,
    }


__all__ = [
    "RUNTIME_CLOSEOUT_EVENT_KIND",
    "build_runtime_closeout_summary",
    "runtime_closeout_identity",
]
