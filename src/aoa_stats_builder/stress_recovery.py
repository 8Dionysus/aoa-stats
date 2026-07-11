from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .read_model_values import is_nonempty_string, is_number


STRESS_RECOVERY_EVAL_NAME = "aoa-stress-recovery-window"
MISSING_STRESS_RECEIPT_REASON = (
    "no aoa-stress-recovery-window eval_result_receipt was found in the active "
    "receipt feed"
)
UNREADABLE_STRESS_REPORT_REASON = (
    "report_ref for aoa-stress-recovery-window could not be resolved into a "
    "readable aoa-evals JSON report"
)
MALFORMED_STRESS_REPORT_REASON = (
    "resolved aoa-stress-recovery-window report is missing required window, "
    "scope, or inputs objects"
)


def _receipt_sort_key(receipt: Mapping[str, Any]) -> tuple[str, str]:
    return str(receipt.get("observed_at") or ""), str(receipt.get("event_id") or "")


def _stress_recovery_receipts(
    receipts: Sequence[Mapping[str, Any]],
) -> tuple[Mapping[str, Any], ...]:
    return tuple(
        receipt
        for receipt in receipts
        if receipt.get("event_kind") == "eval_result_receipt"
        and isinstance(receipt.get("payload"), Mapping)
        and receipt["payload"].get("eval_name") == STRESS_RECOVERY_EVAL_NAME
    )


def latest_stress_recovery_report_ref(
    receipts: Sequence[Mapping[str, Any]],
) -> str | None:
    relevant_receipts = _stress_recovery_receipts(receipts)
    if not relevant_receipts:
        return None
    latest_receipt = max(relevant_receipts, key=_receipt_sort_key)
    payload = latest_receipt["payload"]
    report_ref = payload.get("report_ref")
    return str(report_ref) if is_nonempty_string(report_ref) else None


def stress_summary_template() -> dict[str, float | None]:
    return {
        "containment": None,
        "route_discipline": None,
        "reentry_quality": None,
        "regrounding_effectiveness": None,
        "evidence_continuity": None,
        "adaptation_followthrough": None,
        "operator_burden": None,
        "trust_calibration": None,
    }


def empty_stress_counts() -> dict[str, int]:
    return {
        "receipt_count": 0,
        "handoff_count": 0,
        "playbook_lane_count": 0,
        "reentry_gate_count": 0,
        "projection_health_count": 0,
        "regrounding_ticket_count": 0,
        "eval_count": 0,
    }


def report_axis_score(report: Mapping[str, Any], axis_name: str) -> float | None:
    axes = report.get("axes")
    if not isinstance(axes, Mapping):
        return None
    axis = axes.get(axis_name)
    if not isinstance(axis, Mapping):
        return None
    score = axis.get("score")
    if not is_number(score):
        return None
    return round(float(score), 2)


def _average_scores(values: Sequence[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    if not present:
        return None
    return round(sum(present) / len(present), 2)


def _latest_or_source_time(
    receipts: Sequence[Mapping[str, Any]], source: Mapping[str, Any]
) -> str:
    if receipts:
        return max(str(receipt["observed_at"]) for receipt in receipts)
    return str(source.get("latest_observed_at") or "1970-01-01T00:00:00Z")


def build_suppressed_stress_recovery_window_summary(
    receipts: Sequence[Mapping[str, Any]],
    source: Mapping[str, Any],
    *,
    status: str,
    reason: str,
) -> dict[str, Any]:
    observed_at = _latest_or_source_time(receipts, source)
    trend_flags = ["stress-recovery-window-unavailable"]
    if status == "low_sample":
        trend_flags = ["low-sample-window"]
    return {
        "schema_version": "aoa_stats_stress_recovery_window_summary_v1",
        "generated_from": dict(source),
        "window": {
            "label": "stress-recovery-window-unavailable",
            "start_utc": observed_at,
            "end_utc": observed_at,
        },
        "scope": {
            "repo_family": ["aoa-evals"],
            "stressor_family": "unresolved",
            "owner_surface": None,
            "surface_family": None,
        },
        "inputs": {
            "receipt_refs": [],
            "eval_report_refs": [],
            "route_hint_refs": [],
            "memo_context_refs": [],
        },
        "counts": empty_stress_counts(),
        "suppression": {
            "status": status,
            "reason": reason,
        },
        "summary": stress_summary_template(),
        "trend_flags": trend_flags,
    }


def build_stress_recovery_window_metrics(
    report: Mapping[str, Any],
    *,
    suppression_status: str,
) -> dict[str, float | None]:
    if suppression_status != "none":
        return stress_summary_template()

    reentry_quality = report_axis_score(report, "reentry_quality")
    regrounding_effectiveness = report_axis_score(
        report, "regrounding_effectiveness"
    )
    operator_burden = report_axis_score(report, "operator_burden")
    return {
        "containment": report_axis_score(report, "handoff_fidelity"),
        "route_discipline": report_axis_score(report, "route_discipline"),
        "reentry_quality": reentry_quality,
        "regrounding_effectiveness": regrounding_effectiveness,
        "evidence_continuity": report_axis_score(report, "evidence_continuity"),
        "adaptation_followthrough": _average_scores(
            [reentry_quality, regrounding_effectiveness, operator_burden]
        ),
        "operator_burden": operator_burden,
        "trust_calibration": report_axis_score(report, "trust_calibration"),
    }


def _nonempty_strings(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [str(item) for item in value if is_nonempty_string(item)]


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    return str(value) if is_nonempty_string(value) else None


def build_stress_recovery_window_summary(
    receipts: Sequence[Mapping[str, Any]],
    source: Mapping[str, Any],
    *,
    report: Mapping[str, Any] | None,
) -> dict[str, Any]:
    relevant_receipts = _stress_recovery_receipts(receipts)
    if not relevant_receipts:
        return build_suppressed_stress_recovery_window_summary(
            receipts,
            source,
            status="insufficient_evidence",
            reason=MISSING_STRESS_RECEIPT_REASON,
        )

    latest_receipt = max(relevant_receipts, key=_receipt_sort_key)
    payload = latest_receipt["payload"]
    report_ref = payload.get("report_ref")
    if report is None:
        return build_suppressed_stress_recovery_window_summary(
            relevant_receipts,
            source,
            status="insufficient_evidence",
            reason=UNREADABLE_STRESS_REPORT_REASON,
        )

    window = report.get("window")
    scope = report.get("scope")
    inputs = report.get("inputs")
    if not all(isinstance(item, Mapping) for item in (window, scope, inputs)):
        return build_suppressed_stress_recovery_window_summary(
            relevant_receipts,
            source,
            status="insufficient_evidence",
            reason=MALFORMED_STRESS_REPORT_REASON,
        )

    source_receipt_refs = _nonempty_strings(inputs.get("source_receipt_refs"))
    handoff_refs = _nonempty_strings(inputs.get("handoff_refs"))
    playbook_lane_refs = _nonempty_strings(inputs.get("playbook_lane_refs"))
    reentry_gate_refs = _nonempty_strings(inputs.get("reentry_gate_refs"))
    projection_health_refs = _nonempty_strings(inputs.get("projection_health_refs"))
    regrounding_ticket_refs = _nonempty_strings(inputs.get("regrounding_ticket_refs"))
    counts = {
        "receipt_count": len(source_receipt_refs),
        "handoff_count": len(handoff_refs),
        "playbook_lane_count": len(playbook_lane_refs),
        "reentry_gate_count": len(reentry_gate_refs),
        "projection_health_count": len(projection_health_refs),
        "regrounding_ticket_count": len(regrounding_ticket_refs),
        "eval_count": 1,
    }

    adjacent_signal_count = (
        counts["handoff_count"]
        + counts["playbook_lane_count"]
        + counts["reentry_gate_count"]
        + counts["projection_health_count"]
        + counts["regrounding_ticket_count"]
    )
    suppression_status = "none"
    suppression_reason: str | None = None
    if counts["receipt_count"] < 1:
        suppression_status = "insufficient_evidence"
        suppression_reason = (
            "owner receipts are missing from the resolved stress recovery window "
            "report"
        )
    elif counts["receipt_count"] < 2 or adjacent_signal_count < 4:
        suppression_status = "low_sample"
        suppression_reason = (
            "owner and adjacent stress signals stay too sparse for a confident "
            "repeated-window derived read"
        )

    trend_flags: list[str] = []
    overall_posture = report.get("overall_posture")
    if is_nonempty_string(overall_posture):
        trend_flags.append(f"overall-posture-{overall_posture}")
    if suppression_status == "low_sample":
        trend_flags.append("low-sample-window")
    elif suppression_status == "insufficient_evidence":
        trend_flags.append("insufficient-evidence-window")
    false_promotion_score = report_axis_score(
        report, "false_promotion_prevention"
    )
    if false_promotion_score is not None and false_promotion_score >= 0.8:
        trend_flags.append("false-promotion-guard-held")

    repo_family = _nonempty_strings(scope.get("repo_roots")) or ["aoa-evals"]
    return {
        "schema_version": "aoa_stats_stress_recovery_window_summary_v1",
        "generated_from": dict(source),
        "window": {
            "label": str(window.get("label") or "stress-recovery-window"),
            "start_utc": str(
                window.get("start_utc") or source["latest_observed_at"]
            ),
            "end_utc": str(window.get("end_utc") or source["latest_observed_at"]),
        },
        "scope": {
            "repo_family": repo_family,
            "stressor_family": str(scope.get("stressor_family") or "unresolved"),
            "owner_surface": _optional_string(scope.get("owner_surface")),
            "surface_family": _optional_string(scope.get("surface_family")),
        },
        "inputs": {
            "receipt_refs": source_receipt_refs,
            "eval_report_refs": (
                [str(report_ref)] if is_nonempty_string(report_ref) else []
            ),
            "route_hint_refs": _nonempty_strings(inputs.get("route_hint_refs")),
            "memo_context_refs": _nonempty_strings(inputs.get("memo_context_refs")),
        },
        "counts": counts,
        "suppression": {
            "status": suppression_status,
            "reason": suppression_reason,
        },
        "summary": build_stress_recovery_window_metrics(
            report, suppression_status=suppression_status
        ),
        "trend_flags": trend_flags,
    }
