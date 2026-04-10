#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "examples" / "session_harvest_family.receipts.example.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "generated"
DEFAULT_EVALS_ROOT = REPO_ROOT / "aoa-evals" if (REPO_ROOT / "aoa-evals").exists() else REPO_ROOT.parent / "aoa-evals"
CANONICAL_ENVELOPE_SCHEMA_PATH = REPO_ROOT / "schemas" / "stats-event-envelope.schema.json"
CANONICAL_ENVELOPE_SCHEMA_REF = "schemas/stats-event-envelope.schema.json"

AXES = (
    "boundary_integrity",
    "execution_reliability",
    "change_legibility",
    "review_sharpness",
    "proof_discipline",
    "provenance_hygiene",
    "deep_readiness",
)


class ReceiptValidationError(ValueError):
    pass


@lru_cache(maxsize=1)
def supported_event_kinds() -> frozenset[str]:
    payload = json.loads(CANONICAL_ENVELOPE_SCHEMA_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ReceiptValidationError(
            f"{CANONICAL_ENVELOPE_SCHEMA_REF}: canonical envelope schema must be a JSON object"
        )
    properties = payload.get("properties")
    if not isinstance(properties, dict):
        raise ReceiptValidationError(
            f"{CANONICAL_ENVELOPE_SCHEMA_REF}: missing properties object"
        )
    event_kind = properties.get("event_kind")
    if not isinstance(event_kind, dict):
        raise ReceiptValidationError(
            f"{CANONICAL_ENVELOPE_SCHEMA_REF}: missing properties.event_kind object"
        )
    enum = event_kind.get("enum")
    if not isinstance(enum, list) or not enum:
        raise ReceiptValidationError(
            f"{CANONICAL_ENVELOPE_SCHEMA_REF}: properties.event_kind.enum must be a non-empty list"
        )
    supported = {item for item in enum if isinstance(item, str) and item}
    if len(supported) != len(enum):
        raise ReceiptValidationError(
            f"{CANONICAL_ENVELOPE_SCHEMA_REF}: properties.event_kind.enum must contain only non-empty strings"
        )
    return frozenset(supported)


def automation_pipeline_ref(receipt: dict[str, Any]) -> str:
    payload = receipt["payload"]
    for key in ("pipeline_ref", "manual_route_ref"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return receipt["session_ref"]


def fork_option_count(payload: dict[str, Any]) -> int:
    option_count = payload.get("branch_options_count")
    if isinstance(option_count, int) and option_count > 0:
        return option_count
    branch_ids = payload.get("branch_ids")
    if isinstance(branch_ids, list):
        return len([branch_id for branch_id in branch_ids if isinstance(branch_id, str) and branch_id])
    return 0


def runtime_closeout_identity(receipt: dict[str, Any]) -> tuple[str, str]:
    payload = receipt["payload"]
    program_id = payload.get("program_id")
    wave_id = payload.get("wave_id")
    if isinstance(program_id, str) and program_id and isinstance(wave_id, str) and wave_id:
        return program_id, wave_id
    object_id = str(receipt["object_ref"].get("id") or "")
    if ":" in object_id:
        fallback_program_id, fallback_wave_id = object_id.rsplit(":", 1)
        return fallback_program_id or "unknown-program", fallback_wave_id or "unknown-wave"
    return "unknown-program", receipt["session_ref"]


def core_skill_identity(receipt: dict[str, Any]) -> tuple[str, str]:
    payload = receipt["payload"]
    kernel_id = payload.get("kernel_id")
    skill_name = payload.get("skill_name")
    if isinstance(kernel_id, str) and kernel_id and isinstance(skill_name, str) and skill_name:
        return kernel_id, skill_name
    object_id = receipt["object_ref"].get("id")
    if isinstance(object_id, str) and object_id:
        return "unknown-kernel", object_id
    return "unknown-kernel", "unknown-skill"


def surface_detection_context(receipt: dict[str, Any]) -> dict[str, Any]:
    payload = receipt["payload"]
    context = payload.get("surface_detection_context")
    if not isinstance(context, dict):
        return {}
    return context


def receipt_sort_key(receipt: dict[str, Any]) -> tuple[str, str]:
    return receipt["observed_at"], receipt["event_id"]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build aoa-stats derived views.")
    parser.add_argument(
        "--input",
        action="append",
        default=[],
        help=(
            "Path to a JSON or JSONL file containing one receipt object, an array "
            "of receipt envelopes, or one JSON receipt envelope per line."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where generated summary JSON files should live.",
    )
    parser.add_argument(
        "--evals-root",
        default=str(DEFAULT_EVALS_ROOT),
        help="Path to the aoa-evals repository root used to resolve linked report_ref payloads.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate that generated outputs are current instead of rewriting them.",
    )
    return parser.parse_args(argv)


def load_receipts(paths: list[Path]) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for path in paths:
        if path.suffix == ".jsonl":
            receipts.extend(load_receipts_from_jsonl(path))
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            validate_receipt(payload, location=str(path))
            receipts.append(payload)
            continue
        if not isinstance(payload, list):
            raise ReceiptValidationError(f"{path}: receipt feed must be a JSON object or array")
        for index, item in enumerate(payload):
            if not isinstance(item, dict):
                raise ReceiptValidationError(f"{path}[{index}]: receipt must be an object")
            validate_receipt(item, location=f"{path}[{index}]")
            receipts.append(item)
    deduped: dict[str, dict[str, Any]] = {}
    for receipt in receipts:
        deduped[receipt["event_id"]] = receipt
    return sorted(deduped.values(), key=receipt_sort_key)


def load_receipts_from_jsonl(path: Path) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ReceiptValidationError(
                f"{path}:{line_number}: invalid JSONL receipt line"
            ) from exc
        if not isinstance(item, dict):
            raise ReceiptValidationError(f"{path}:{line_number}: receipt must be an object")
        validate_receipt(item, location=f"{path}:{line_number}")
        receipts.append(item)
    return receipts


def validate_receipt(receipt: dict[str, Any], *, location: str) -> None:
    required_fields = (
        "event_kind",
        "event_id",
        "observed_at",
        "run_ref",
        "session_ref",
        "actor_ref",
        "object_ref",
        "evidence_refs",
        "payload",
    )
    for field in required_fields:
        if field not in receipt:
            raise ReceiptValidationError(f"{location}: missing field '{field}'")

    for field in ("event_kind", "event_id", "run_ref", "session_ref", "actor_ref"):
        if not isinstance(receipt[field], str) or not receipt[field]:
            raise ReceiptValidationError(f"{location}.{field}: must be a non-empty string")
    if receipt["event_kind"] not in supported_event_kinds():
        raise ReceiptValidationError(
            f"{location}.event_kind: unsupported event kind {receipt['event_kind']!r}; "
            f"see {CANONICAL_ENVELOPE_SCHEMA_REF}"
        )

    try:
        datetime.fromisoformat(receipt["observed_at"].replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ReceiptValidationError(
            f"{location}.observed_at: must be an ISO datetime"
        ) from exc

    object_ref = receipt["object_ref"]
    if not isinstance(object_ref, dict):
        raise ReceiptValidationError(f"{location}.object_ref: must be an object")
    for field in ("repo", "kind", "id"):
        if not isinstance(object_ref.get(field), str) or not object_ref[field]:
            raise ReceiptValidationError(
                f"{location}.object_ref.{field}: must be a non-empty string"
            )

    evidence_refs = receipt["evidence_refs"]
    if not isinstance(evidence_refs, list):
        raise ReceiptValidationError(f"{location}.evidence_refs: must be a list")
    for index, item in enumerate(evidence_refs):
        if not isinstance(item, dict):
            raise ReceiptValidationError(
                f"{location}.evidence_refs[{index}]: must be an object"
            )
        for field in ("kind", "ref"):
            if not isinstance(item.get(field), str) or not item[field]:
                raise ReceiptValidationError(
                    f"{location}.evidence_refs[{index}].{field}: must be a non-empty string"
                )

    if not isinstance(receipt["payload"], dict):
        raise ReceiptValidationError(f"{location}.payload: must be an object")
    supersedes = receipt.get("supersedes")
    if supersedes is not None and (not isinstance(supersedes, str) or not supersedes):
        raise ReceiptValidationError(f"{location}.supersedes: must be omitted or a non-empty string")


def resolve_active_receipts(receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    receipt_by_id = {receipt["event_id"]: receipt for receipt in receipts}
    supersedes_by_id = {
        receipt["event_id"]: receipt["supersedes"]
        for receipt in receipts
        if isinstance(receipt.get("supersedes"), str)
        and receipt["supersedes"] in receipt_by_id
        and receipt["supersedes"] != receipt["event_id"]
    }
    cycle_nodes = find_supersedes_cycle_nodes(supersedes_by_id)
    effective_supersedes = {
        event_id: target_id
        for event_id, target_id in supersedes_by_id.items()
        if event_id not in cycle_nodes and target_id not in cycle_nodes
    }

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        family_root = resolve_receipt_family_root(
            receipt["event_id"], effective_supersedes
        )
        grouped[family_root].append(receipt)

    active = [
        max(group, key=receipt_sort_key)
        for group in grouped.values()
    ]
    return sorted(active, key=receipt_sort_key)


def find_supersedes_cycle_nodes(supersedes_by_id: dict[str, str]) -> set[str]:
    cycle_nodes: set[str] = set()
    seen_done: set[str] = set()

    for start in supersedes_by_id:
        if start in seen_done:
            continue
        order: list[str] = []
        positions: dict[str, int] = {}
        current = start
        while current in supersedes_by_id:
            if current in seen_done:
                break
            if current in positions:
                cycle_nodes.update(order[positions[current] :])
                break
            positions[current] = len(order)
            order.append(current)
            current = supersedes_by_id[current]
        seen_done.update(order)

    return cycle_nodes


def resolve_receipt_family_root(event_id: str, supersedes_by_id: dict[str, str]) -> str:
    current = event_id
    while current in supersedes_by_id:
        current = supersedes_by_id[current]
    return current


def generated_from(receipts: list[dict[str, Any]], input_paths: list[str]) -> dict[str, Any]:
    latest_observed_at = max(receipt["observed_at"] for receipt in receipts)
    return {
        "receipt_input_paths": input_paths,
        "total_receipts": len(receipts),
        "latest_observed_at": latest_observed_at,
    }


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def ensure_repo_relative_ref_path(raw_path: str) -> str | None:
    if not is_nonempty_string(raw_path):
        return None
    normalized = raw_path.strip().replace("\\", "/")
    if normalized.startswith("/") or normalized.startswith("./"):
        return None
    parts = normalized.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return None
    return normalized


def resolve_repo_ref_path(raw_ref: Any, repo_roots: dict[str, Path]) -> Path | None:
    if not is_nonempty_string(raw_ref):
        return None
    ref = raw_ref.strip()
    if not ref.startswith("repo:"):
        return None
    repo_and_path = ref[len("repo:") :]
    repo_name, separator, relative_path = repo_and_path.partition("/")
    if not separator or repo_name not in repo_roots:
        return None
    normalized = ensure_repo_relative_ref_path(relative_path)
    if normalized is None:
        return None
    return repo_roots[repo_name] / Path(normalized)


def load_optional_json_object(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def stress_summary_template() -> dict[str, Any]:
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


def report_axis_score(report: dict[str, Any], axis_name: str) -> float | None:
    axes = report.get("axes")
    if not isinstance(axes, dict):
        return None
    axis = axes.get(axis_name)
    if not isinstance(axis, dict):
        return None
    score = axis.get("score")
    if not is_number(score):
        return None
    return round(float(score), 2)


def average_scores(values: list[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    if not present:
        return None
    return round(sum(present) / len(present), 2)


def latest_or_source_time(receipts: list[dict[str, Any]], source: dict[str, Any]) -> str:
    if receipts:
        return max(receipt["observed_at"] for receipt in receipts)
    return str(source.get("latest_observed_at") or "1970-01-01T00:00:00Z")


def build_suppressed_stress_recovery_window_summary(
    receipts: list[dict[str, Any]],
    source: dict[str, Any],
    *,
    status: str,
    reason: str,
) -> dict[str, Any]:
    observed_at = latest_or_source_time(receipts, source)
    trend_flags = ["stress-recovery-window-unavailable"]
    if status == "low_sample":
        trend_flags = ["low-sample-window"]
    return {
        "schema_version": "aoa_stats_stress_recovery_window_summary_v1",
        "generated_from": source,
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
    report: dict[str, Any],
    *,
    suppression_status: str,
) -> dict[str, Any]:
    if suppression_status != "none":
        return stress_summary_template()

    reentry_quality = report_axis_score(report, "reentry_quality")
    regrounding_effectiveness = report_axis_score(report, "regrounding_effectiveness")
    operator_burden = report_axis_score(report, "operator_burden")
    return {
        "containment": report_axis_score(report, "handoff_fidelity"),
        "route_discipline": report_axis_score(report, "route_discipline"),
        "reentry_quality": reentry_quality,
        "regrounding_effectiveness": regrounding_effectiveness,
        "evidence_continuity": report_axis_score(report, "evidence_continuity"),
        "adaptation_followthrough": average_scores(
            [reentry_quality, regrounding_effectiveness, operator_burden]
        ),
        "operator_burden": operator_burden,
        "trust_calibration": report_axis_score(report, "trust_calibration"),
    }


def build_stress_recovery_window_summary(
    receipts: list[dict[str, Any]],
    source: dict[str, Any],
    *,
    evals_root: Path,
) -> dict[str, Any]:
    relevant_receipts = [
        receipt
        for receipt in receipts
        if receipt["event_kind"] == "eval_result_receipt"
        and isinstance(receipt.get("payload"), dict)
        and receipt["payload"].get("eval_name") == "aoa-stress-recovery-window"
    ]
    if not relevant_receipts:
        return build_suppressed_stress_recovery_window_summary(
            receipts,
            source,
            status="insufficient_evidence",
            reason="no aoa-stress-recovery-window eval_result_receipt was found in the active receipt feed",
        )

    latest_receipt = max(relevant_receipts, key=receipt_sort_key)
    payload = latest_receipt["payload"]
    report_ref = payload.get("report_ref")
    report_path = resolve_repo_ref_path(report_ref, {"aoa-evals": evals_root})
    report = load_optional_json_object(report_path)
    if report is None:
        return build_suppressed_stress_recovery_window_summary(
            relevant_receipts,
            source,
            status="insufficient_evidence",
            reason="report_ref for aoa-stress-recovery-window could not be resolved into a readable aoa-evals JSON report",
        )

    window = report.get("window")
    scope = report.get("scope")
    inputs = report.get("inputs")
    if not isinstance(window, dict) or not isinstance(scope, dict) or not isinstance(inputs, dict):
        return build_suppressed_stress_recovery_window_summary(
            relevant_receipts,
            source,
            status="insufficient_evidence",
            reason="resolved aoa-stress-recovery-window report is missing required window, scope, or inputs objects",
        )

    counts = {
        "receipt_count": len([item for item in inputs.get("source_receipt_refs", []) if is_nonempty_string(item)]),
        "handoff_count": len([item for item in inputs.get("handoff_refs", []) if is_nonempty_string(item)]),
        "playbook_lane_count": len([item for item in inputs.get("playbook_lane_refs", []) if is_nonempty_string(item)]),
        "reentry_gate_count": len([item for item in inputs.get("reentry_gate_refs", []) if is_nonempty_string(item)]),
        "projection_health_count": len([item for item in inputs.get("projection_health_refs", []) if is_nonempty_string(item)]),
        "regrounding_ticket_count": len([item for item in inputs.get("regrounding_ticket_refs", []) if is_nonempty_string(item)]),
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
        suppression_reason = "owner receipts are missing from the resolved stress recovery window report"
    elif counts["receipt_count"] < 2 or adjacent_signal_count < 4:
        suppression_status = "low_sample"
        suppression_reason = (
            "owner and adjacent stress signals stay too sparse for a confident repeated-window derived read"
        )

    report_refs = [report_ref] if is_nonempty_string(report_ref) else []
    route_hint_refs = [
        item for item in inputs.get("route_hint_refs", []) if is_nonempty_string(item)
    ]
    memo_context_refs = [
        item for item in inputs.get("memo_context_refs", []) if is_nonempty_string(item)
    ]

    trend_flags: list[str] = []
    overall_posture = report.get("overall_posture")
    if isinstance(overall_posture, str) and overall_posture:
        trend_flags.append(f"overall-posture-{overall_posture}")
    if suppression_status == "low_sample":
        trend_flags.append("low-sample-window")
    elif suppression_status == "insufficient_evidence":
        trend_flags.append("insufficient-evidence-window")
    if report_axis_score(report, "false_promotion_prevention") is not None:
        score = report_axis_score(report, "false_promotion_prevention")
        if score is not None and score >= 0.8:
            trend_flags.append("false-promotion-guard-held")

    return {
        "schema_version": "aoa_stats_stress_recovery_window_summary_v1",
        "generated_from": source,
        "window": {
            "label": str(window.get("label") or "stress-recovery-window"),
            "start_utc": str(window.get("start_utc") or source["latest_observed_at"]),
            "end_utc": str(window.get("end_utc") or source["latest_observed_at"]),
        },
        "scope": {
            "repo_family": [
                item for item in scope.get("repo_roots", []) if is_nonempty_string(item)
            ]
            or ["aoa-evals"],
            "stressor_family": str(scope.get("stressor_family") or "unresolved"),
            "owner_surface": scope.get("owner_surface")
            if scope.get("owner_surface") is None or is_nonempty_string(scope.get("owner_surface"))
            else None,
            "surface_family": scope.get("surface_family")
            if scope.get("surface_family") is None or is_nonempty_string(scope.get("surface_family"))
            else None,
        },
        "inputs": {
            "receipt_refs": [
                item for item in inputs.get("source_receipt_refs", []) if is_nonempty_string(item)
            ],
            "eval_report_refs": report_refs,
            "route_hint_refs": route_hint_refs,
            "memo_context_refs": memo_context_refs,
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
        latest = max(group, key=lambda receipt: (receipt["observed_at"], receipt["event_id"]))
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
                "evidence_ref_count": sum(len(receipt["evidence_refs"]) for receipt in group),
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


def build_core_skill_application_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        if receipt["event_kind"] != "core_skill_application_receipt":
            continue
        payload = receipt.get("payload")
        if not isinstance(payload, dict) or payload.get("application_stage") != "finish":
            continue
        grouped[core_skill_identity(receipt)].append(receipt)

    skills: list[dict[str, Any]] = []
    for key in sorted(grouped):
        kernel_id, skill_name = key
        group = grouped[key]
        latest = max(group, key=lambda receipt: (receipt["observed_at"], receipt["event_id"]))
        detail_counts: Counter[str] = Counter()
        for receipt in group:
            detail_event_kind = receipt["payload"].get("detail_event_kind")
            if isinstance(detail_event_kind, str) and detail_event_kind:
                detail_counts[detail_event_kind] += 1
        skills.append(
            {
                "kernel_id": kernel_id,
                "skill_name": skill_name,
                "application_count": len(group),
                "latest_observed_at": latest["observed_at"],
                "latest_session_ref": latest["session_ref"],
                "latest_run_ref": latest["run_ref"],
                "detail_event_kind_counts": dict(sorted(detail_counts.items())),
            }
        )

    return {
        "schema_version": "aoa_stats_core_skill_application_summary_v1",
        "generated_from": source,
        "skills": skills,
    }


def build_repeated_window_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        grouped[receipt["observed_at"][:10]].append(receipt)

    windows: list[dict[str, Any]] = []
    for window_date in sorted(grouped):
        group = grouped[window_date]
        event_counts = Counter(receipt["event_kind"] for receipt in group)
        unique_objects = {object_key(receipt["object_ref"]) for receipt in group}
        windows.append(
            {
                "window_id": f"window:{window_date}",
                "window_date": window_date,
                "total_receipts": len(group),
                "unique_objects": len(unique_objects),
                "event_counts_by_kind": dict(sorted(event_counts.items())),
                "eval_result_count": event_counts.get("eval_result_receipt", 0),
                "progression_delta_count": event_counts.get("progression_delta_receipt", 0),
                "automation_candidate_count": event_counts.get(
                    "automation_candidate_receipt", 0
                ),
                "evidence_ref_count": sum(len(receipt["evidence_refs"]) for receipt in group),
            }
        )

    return {
        "schema_version": "aoa_stats_repeated_window_summary_v1",
        "generated_from": source,
        "windows": windows,
    }


def axis_template() -> dict[str, int]:
    return {axis: 0 for axis in AXES}


def build_route_progression_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        if receipt["event_kind"] != "progression_delta_receipt":
            continue
        route_ref = receipt["payload"].get("route_ref") or receipt["session_ref"]
        grouped[route_ref].append(receipt)

    routes: list[dict[str, Any]] = []
    for route_ref in sorted(grouped):
        group = grouped[route_ref]
        latest = max(group, key=lambda receipt: (receipt["observed_at"], receipt["event_id"]))
        cumulative = axis_template()
        caution_count = 0
        for receipt in group:
            payload = receipt["payload"]
            axis_deltas = payload.get("axis_deltas", {})
            if isinstance(axis_deltas, dict):
                for axis in AXES:
                    value = axis_deltas.get(axis, 0)
                    if isinstance(value, int):
                        cumulative[axis] += value
            cautions = payload.get("cautions", [])
            if isinstance(cautions, list):
                caution_count += len(cautions)
        routes.append(
            {
                "route_ref": route_ref,
                "total_progression_receipts": len(group),
                "latest_verdict": latest["payload"].get("verdict", "unknown"),
                "latest_observed_at": latest["observed_at"],
                "cumulative_axis_deltas": cumulative,
                "caution_count": caution_count,
                "evidence_ref_count": sum(len(receipt["evidence_refs"]) for receipt in group),
            }
        )

    return {
        "schema_version": "aoa_stats_route_progression_summary_v1",
        "generated_from": source,
        "routes": routes,
    }


def build_fork_calibration_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        if receipt["event_kind"] != "decision_fork_receipt":
            continue
        route_ref = receipt["payload"].get("route_ref") or receipt["session_ref"]
        grouped[route_ref].append(receipt)

    routes: list[dict[str, Any]] = []
    for route_ref in sorted(grouped):
        group = grouped[route_ref]
        latest = max(group, key=lambda receipt: (receipt["observed_at"], receipt["event_id"]))
        branch_counts: Counter[str] = Counter()
        max_options = 0
        realized_outcome_link_count = 0
        for receipt in group:
            payload = receipt["payload"]
            branch = payload.get("chosen_branch") or "unrecorded"
            branch_counts[str(branch)] += 1
            option_count = fork_option_count(payload)
            if option_count > max_options:
                max_options = option_count
            realized_refs = payload.get("realized_outcome_refs", [])
            if isinstance(realized_refs, list):
                realized_outcome_link_count += len(realized_refs)
        routes.append(
            {
                "route_ref": route_ref,
                "decision_count": len(group),
                "chosen_branch_counts": dict(sorted(branch_counts.items())),
                "max_option_count": max_options,
                "realized_outcome_link_count": realized_outcome_link_count,
                "evidence_ref_count": sum(len(receipt["evidence_refs"]) for receipt in group),
                "latest_observed_at": latest["observed_at"],
            }
        )

    return {
        "schema_version": "aoa_stats_fork_calibration_summary_v1",
        "generated_from": source,
        "routes": routes,
    }


def build_automation_pipeline_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        if receipt["event_kind"] != "automation_candidate_receipt":
            continue
        pipeline_ref = automation_pipeline_ref(receipt)
        grouped[pipeline_ref].append(receipt)

    pipelines: list[dict[str, Any]] = []
    for pipeline_ref in sorted(grouped):
        group = grouped[pipeline_ref]
        latest = max(group, key=lambda receipt: (receipt["observed_at"], receipt["event_id"]))
        next_artifact_hints: set[str] = set()
        seed_ready_count = 0
        checkpoint_required_count = 0
        deterministic_ready_count = 0
        reversible_ready_count = 0
        for receipt in group:
            payload = receipt["payload"]
            if payload.get("seed_ready") is True:
                seed_ready_count += 1
            if payload.get("checkpoint_required") is True:
                checkpoint_required_count += 1
            if payload.get("deterministic_ready") is True:
                deterministic_ready_count += 1
            if payload.get("reversible_ready") is True:
                reversible_ready_count += 1
            next_hint = payload.get("next_artifact_hint")
            if isinstance(next_hint, str) and next_hint:
                next_artifact_hints.add(next_hint)
        pipelines.append(
            {
                "pipeline_ref": pipeline_ref,
                "candidate_count": len(group),
                "seed_ready_count": seed_ready_count,
                "checkpoint_required_count": checkpoint_required_count,
                "deterministic_ready_count": deterministic_ready_count,
                "reversible_ready_count": reversible_ready_count,
                "next_artifact_hints": sorted(next_artifact_hints),
                "evidence_ref_count": sum(len(receipt["evidence_refs"]) for receipt in group),
                "latest_observed_at": latest["observed_at"],
            }
        )

    return {
        "schema_version": "aoa_stats_automation_pipeline_summary_v1",
        "generated_from": source,
        "pipelines": pipelines,
    }


def build_runtime_closeout_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        if receipt["event_kind"] != "runtime_wave_closeout_receipt":
            continue
        grouped[runtime_closeout_identity(receipt)].append(receipt)

    closeouts: list[dict[str, Any]] = []
    for key in sorted(grouped):
        program_id, wave_id = key
        group = grouped[key]
        latest = max(group, key=lambda receipt: (receipt["observed_at"], receipt["event_id"]))
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
                "latest_gate_result": str(latest_payload.get("gate_result") or "unknown"),
                "gate_result_counts": dict(sorted(gate_counts.items())),
                "latest_reviewed_closeout_handoff_status": str(
                    latest_payload.get("reviewed_closeout_handoff_status") or "unknown"
                ),
                "reviewed_closeout_handoff_status_counts": dict(
                    sorted(handoff_counts.items())
                ),
                "latest_reviewed_closeout_audit_only": bool(
                    latest_payload.get("reviewed_closeout_audit_only")
                ),
                "latest_case_count": int(latest_payload.get("case_count") or 0),
                "latest_next_action": str(latest_payload.get("next_action") or "unspecified"),
                "latest_truth_status": {
                    "source_authored": bool(latest_truth_status.get("source_authored")),
                    "deployed": bool(latest_truth_status.get("deployed")),
                    "trial_proven": bool(latest_truth_status.get("trial_proven")),
                    "live_available": bool(latest_truth_status.get("live_available")),
                },
                "first_observed_at": group[0]["observed_at"],
                "last_observed_at": latest["observed_at"],
                "evidence_ref_count": sum(len(receipt["evidence_refs"]) for receipt in group),
            }
        )

    return {
        "schema_version": "aoa_stats_runtime_closeout_summary_v1",
        "generated_from": source,
        "closeouts": closeouts,
    }


def build_surface_detection_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        if receipt["event_kind"] != "core_skill_application_receipt":
            continue
        if receipt["payload"].get("application_stage") != "finish":
            continue
        grouped[receipt["observed_at"][:10]].append(receipt)

    windows: list[dict[str, Any]] = []
    for window_date in sorted(grouped):
        group = grouped[window_date]
        activation_counts: Counter[str] = Counter()
        adjacent_owner_repo_counts: Counter[str] = Counter()
        handoff_target_counts: Counter[str] = Counter()
        candidate_now_count = 0
        candidate_later_count = 0
        owner_layer_ambiguity_count = 0
        repeated_pattern_signal_count = 0
        promotion_discussion_count = 0
        family_entry_ref_count = 0

        for receipt in group:
            context = surface_detection_context(receipt)
            activation_truth = context.get("activation_truth")
            if isinstance(activation_truth, str) and activation_truth == "manual-equivalent-adjacent":
                activation_counts["manual-equivalent-adjacent"] += 1
            else:
                activation_counts["activated"] += 1

            candidate_counts = context.get("candidate_counts")
            if isinstance(candidate_counts, dict):
                candidate_now_count += int(candidate_counts.get("candidate_now") or 0)
                candidate_later_count += int(candidate_counts.get("candidate_later") or 0)

            if bool(context.get("owner_layer_ambiguity")):
                owner_layer_ambiguity_count += 1

            adjacent_owner_repos = context.get("adjacent_owner_repos")
            if isinstance(adjacent_owner_repos, list):
                for repo in adjacent_owner_repos:
                    if isinstance(repo, str) and repo:
                        adjacent_owner_repo_counts[repo] += 1

            handoff_targets = context.get("suggested_handoff_targets")
            if isinstance(handoff_targets, list):
                for target in handoff_targets:
                    if isinstance(target, str) and target:
                        handoff_target_counts[target] += 1

            if bool(context.get("repeated_pattern_signal")):
                repeated_pattern_signal_count += 1
            if bool(context.get("promotion_discussion_required")):
                promotion_discussion_count += 1

            family_entry_refs = context.get("family_entry_refs")
            if isinstance(family_entry_refs, list):
                family_entry_ref_count += len(
                    [ref for ref in family_entry_refs if isinstance(ref, str) and ref]
                )

        windows.append(
            {
                "window_id": f"window:{window_date}",
                "window_date": window_date,
                "core_skill_receipt_count": len(group),
                "activated_count": activation_counts["activated"],
                "manual_equivalent_adjacent_count": activation_counts["manual-equivalent-adjacent"],
                "candidate_now_count": candidate_now_count,
                "candidate_later_count": candidate_later_count,
                "owner_layer_ambiguity_count": owner_layer_ambiguity_count,
                "adjacent_owner_repo_counts": dict(sorted(adjacent_owner_repo_counts.items())),
                "handoff_target_counts": dict(sorted(handoff_target_counts.items())),
                "repeated_pattern_signal_count": repeated_pattern_signal_count,
                "promotion_discussion_count": promotion_discussion_count,
                "family_entry_ref_count": family_entry_ref_count,
                "evidence_ref_count": sum(len(receipt["evidence_refs"]) for receipt in group),
                "first_observed_at": group[0]["observed_at"],
                "last_observed_at": group[-1]["observed_at"],
            }
        )

    return {
        "schema_version": "aoa_stats_surface_detection_summary_v1",
        "generated_from": source,
        "windows": windows,
    }


def build_summary_surface_catalog(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "aoa_stats_summary_surface_catalog_v2",
        "schema_ref": "schemas/summary-surface-catalog.schema.json",
        "owner_repo": "aoa-stats",
        "surface_kind": "runtime_surface",
        "authority_ref": "docs/ARCHITECTURE.md",
        "generated_from": source,
        "validation_refs": [
            "scripts/build_views.py",
            "scripts/validate_repo.py",
            "tests/test_summary_surface_catalog.py",
        ],
        "surfaces": [
            {
                "name": "core_skill_application_summary",
                "surface_ref": "generated/core_skill_application_summary.min.json",
                "schema_ref": "schemas/core-skill-application-summary.schema.json",
                "primary_question": "Which project-core kernel skills are actually finishing and how often, without inferring usage from general receipt volume?",
                "derivation_rule": "aggregate core_skill_application_receipt payloads by kernel_id and skill_name",
            },
            {
                "name": "object_summary",
                "surface_ref": "generated/object_summary.min.json",
                "schema_ref": "schemas/object-summary.schema.json",
                "primary_question": "How often and how broadly is each source object showing up in the current receipt feed?",
                "derivation_rule": "group receipts by object_ref and keep counts, latest timestamps, and bounded posture flags",
            },
            {
                "name": "repeated_window_summary",
                "surface_ref": "generated/repeated_window_summary.min.json",
                "schema_ref": "schemas/repeated-window-summary.schema.json",
                "primary_question": "What changed across bounded date windows without turning the result into one global score?",
                "derivation_rule": "group receipts by observed_at date and keep counts plus bounded window signals",
            },
            {
                "name": "route_progression_summary",
                "surface_ref": "generated/route_progression_summary.min.json",
                "schema_ref": "schemas/route-progression-summary.schema.json",
                "primary_question": "What bounded multi-axis movement is visible on each named route?",
                "derivation_rule": "aggregate progression_delta_receipt payloads by route_ref and sum axis deltas",
            },
            {
                "name": "fork_calibration_summary",
                "surface_ref": "generated/fork_calibration_summary.min.json",
                "schema_ref": "schemas/fork-calibration-summary.schema.json",
                "primary_question": "How are route forks actually being chosen and how often do they carry realized outcome refs?",
                "derivation_rule": "aggregate decision_fork_receipt payloads by route_ref and chosen_branch",
            },
            {
                "name": "automation_pipeline_summary",
                "surface_ref": "generated/automation_pipeline_summary.min.json",
                "schema_ref": "schemas/automation-pipeline-summary.schema.json",
                "primary_question": "How close is a named automation pipeline to seed-ready bounded use?",
                "derivation_rule": "aggregate automation_candidate_receipt payloads by pipeline_ref and readiness flags",
            },
            {
                "name": "runtime_closeout_summary",
                "surface_ref": "generated/runtime_closeout_summary.min.json",
                "schema_ref": "schemas/runtime-closeout-summary.schema.json",
                "primary_question": "What is the current bounded runtime closeout posture across program waves and how did reviewed handoff land?",
                "derivation_rule": "aggregate runtime_wave_closeout_receipt payloads by program_id and wave_id and keep the latest gate plus handoff posture",
            },
            {
                "name": "stress_recovery_window_summary",
                "surface_ref": "generated/stress_recovery_window_summary.min.json",
                "schema_ref": "schemas/stress-recovery-window-summary.schema.json",
                "primary_question": "What does the current repeated-window stress recovery proof family say without inventing a new canonical event kind or outranking owner evidence?",
                "derivation_rule": "resolve aoa-stress-recovery-window eval_result_receipt report_ref paths through aoa-evals and derive one bounded summary plus suppression posture",
            },
            {
                "name": "surface_detection_summary",
                "surface_ref": "generated/surface_detection_summary.min.json",
                "schema_ref": "schemas/surface-detection-summary.schema.json",
                "primary_question": "What second-wave surface-detection signals are accumulating without turning stats into routing authority?",
                "derivation_rule": "aggregate advisory surface_detection_context payloads on finish-stage core_skill_application_receipt envelopes by observed date",
            },
        ],
    }


def build_all_views(
    receipts: list[dict[str, Any]], input_paths: list[str], *, evals_root: Path | None = None
) -> dict[str, dict[str, Any]]:
    active_receipts = resolve_active_receipts(receipts)
    source = generated_from(active_receipts, input_paths)
    resolved_evals_root = (
        evals_root.expanduser().resolve() if evals_root is not None else DEFAULT_EVALS_ROOT.resolve()
    )
    return {
        "object_summary.min.json": build_object_summary(active_receipts, source),
        "core_skill_application_summary.min.json": build_core_skill_application_summary(
            active_receipts, source
        ),
        "repeated_window_summary.min.json": build_repeated_window_summary(active_receipts, source),
        "route_progression_summary.min.json": build_route_progression_summary(active_receipts, source),
        "fork_calibration_summary.min.json": build_fork_calibration_summary(active_receipts, source),
        "automation_pipeline_summary.min.json": build_automation_pipeline_summary(
            active_receipts, source
        ),
        "runtime_closeout_summary.min.json": build_runtime_closeout_summary(active_receipts, source),
        "stress_recovery_window_summary.min.json": build_stress_recovery_window_summary(
            active_receipts, source, evals_root=resolved_evals_root
        ),
        "surface_detection_summary.min.json": build_surface_detection_summary(active_receipts, source),
        "summary_surface_catalog.min.json": build_summary_surface_catalog(source),
    }


def stable_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_paths = [Path(path).expanduser().resolve() for path in args.input] or [DEFAULT_INPUT]
    output_dir = Path(args.output_dir).expanduser().resolve()
    evals_root = Path(args.evals_root).expanduser().resolve()
    receipts = load_receipts(input_paths)
    outputs = build_all_views(
        receipts,
        [path.name for path in input_paths],
        evals_root=evals_root,
    )

    if args.check:
        mismatches: list[str] = []
        for name, payload in outputs.items():
            target = output_dir / name
            expected = stable_json(payload)
            if not target.exists() or target.read_text(encoding="utf-8") != expected:
                mismatches.append(name)
        if mismatches:
            print(
                "Generated views are out of date: " + ", ".join(sorted(mismatches)),
                file=sys.stderr,
            )
            return 1
        print("[ok] generated views are current")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in outputs.items():
        (output_dir / name).write_text(stable_json(payload), encoding="utf-8")
    print(f"[ok] wrote {len(outputs)} derived summary surfaces to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
