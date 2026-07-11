#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import AbstractSet, Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder.candidate_lifecycle import (  # noqa: E402
    build_candidate_lineage_summary,
    build_owner_landing_summary,
    build_supersession_drop_summary,
)
from aoa_stats_builder.component_refresh import (  # noqa: E402
    COMPONENT_REFRESH_COMPONENT_DRIFT_CLASSES as COMPONENT_REFRESH_COMPONENT_DRIFT_CLASSES,
    COMPONENT_REFRESH_CURRENT_STATUSES as COMPONENT_REFRESH_CURRENT_STATUSES,
    COMPONENT_REFRESH_DECISION_STATUSES as COMPONENT_REFRESH_DECISION_STATUSES,
    COMPONENT_REFRESH_ROUTE_CLASSES as COMPONENT_REFRESH_ROUTE_CLASSES,
    COMPONENT_REFRESH_SIGNAL_DRIFT_CLASSES as COMPONENT_REFRESH_SIGNAL_DRIFT_CLASSES,
    build_component_refresh_summary as build_component_refresh_summary_from_inputs,
    component_refresh_drift_classes as component_refresh_drift_classes,
    component_refresh_route_class as component_refresh_route_class,
    component_refresh_status as component_refresh_status,
    latest_component_hints_by_component as latest_component_hints_by_component,
)
from aoa_stats_builder.component_refresh_sources import (  # noqa: E402
    ComponentRefreshInputBundle,
    load_reviewed_sdk_example_bundle,
    reviewed_sdk_example_paths,
)
from aoa_stats_builder.continuity_window import (  # noqa: E402
    CONTINUITY_EVAL_ANCHORS as CONTINUITY_EVAL_ANCHORS,
    CONTINUITY_STATUSES as CONTINUITY_STATUSES,
    build_continuity_window_summary as build_continuity_window_summary_from_inputs,
    continuity_drift_flags as continuity_drift_flags,
    continuity_reanchor_counts as continuity_reanchor_counts,
)
from aoa_stats_builder.continuity_window_sources import (  # noqa: E402
    ContinuityWindowInputBundle,
    continuity_window_reference_paths,
    load_continuity_window_reference_bundle,
)
from aoa_stats_builder.growth_cycle import (  # noqa: E402
    build_automation_followthrough_summary,
    build_automation_pipeline_summary,
    build_fork_calibration_summary,
    build_session_growth_branch_summary,
)
from aoa_stats_builder.receipt_abi import (  # noqa: E402
    ReceiptValidationError,
    generated_from,
    load_receipts,
    resolve_active_receipts,
    validate_receipt as validate_receipt,
)
from aoa_stats_builder.receipt_abi import receipt_sort_key  # noqa: E402
from aoa_stats_builder.read_model_values import (  # noqa: E402
    collect_datetime_candidates,
    is_nonempty_string,
    is_number,
    normalize_string_list,
    parse_iso_datetime_or_min,
    string_count_map,
)
from aoa_stats_builder.source_coverage import build_source_coverage_summary  # noqa: E402
from aoa_stats_builder.surface_catalog import build_summary_surface_catalog  # noqa: E402

DEFAULT_INPUT = (
    REPO_ROOT
    / "stats"
    / "intake-contract"
    / "examples"
    / "session_harvest_family.receipts.example.json"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "generated"
LIVE_SOURCE_REGISTRY_RELATIVE = Path(
    "mechanics/recurrence/parts/live-receipt-refresh/config/live_receipt_sources.json"
)
DEFAULT_SOURCE_REGISTRY = REPO_ROOT / LIVE_SOURCE_REGISTRY_RELATIVE


def default_neighbor_root(repo_name: str, *, allow_nested: bool = False) -> Path:
    candidates = []
    if allow_nested:
        candidates.append(REPO_ROOT / repo_name)
    candidates.extend(
        [
            REPO_ROOT / ".deps" / repo_name,
            Path("/srv/AbyssOS") / repo_name,
            REPO_ROOT.parent / repo_name,
        ]
    )
    return next((candidate.resolve() for candidate in candidates if candidate.is_dir()), candidates[-1])


DEFAULT_EVALS_ROOT = default_neighbor_root("aoa-evals", allow_nested=True)
DEFAULT_PUBLIC_PROFILE_ROOT = default_neighbor_root("8Dionysus")
DEFAULT_AOA_AGENTS_ROOT = default_neighbor_root("aoa-agents")
DEFAULT_AOA_PLAYBOOKS_ROOT = default_neighbor_root("aoa-playbooks")
DEFAULT_AOA_MEMO_ROOT = default_neighbor_root("aoa-memo")
DEFAULT_AOA_SDK_ROOT = default_neighbor_root("aoa-sdk")

AXES = (
    "boundary_integrity",
    "execution_reliability",
    "change_legibility",
    "review_sharpness",
    "proof_discipline",
    "provenance_hygiene",
    "deep_readiness",
)
TRUST_POSTURES = (
    "unknown",
    "root_mismatch",
    "config_inactive",
    "trusted_ready",
    "rollout_active",
    "rollback_recommended",
)
MEMORY_CONSUMER_REFS = (
    "repo:aoa-evals",
    "repo:aoa-kag",
    "repo:aoa-stats",
    "repo:aoa-playbooks",
    "repo:aoa-agents",
)
MEMORY_ROUTE_BOUNDARY = {
    "operation_mode": "read_only",
    "local_candidate_route": "none_without_repo_memo_port",
    "session_evidence_route": ".aoa_session_evidence_until_reviewed_intake",
    "durable_landing_route": "aoa-memo_reviewed_source_patch",
    "mcp_boundary": "aoa_memo_brief_search_status_validate_and_landing_plan_dry_run_only",
}


def repo_root_from_env(env_name: str, default: Path) -> Path:
    override = os.environ.get(env_name)
    if not override:
        return default
    return Path(override).expanduser().resolve()


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
        default=str(repo_root_from_env("AOA_EVALS_ROOT", DEFAULT_EVALS_ROOT)),
        help="Path to the aoa-evals repository root used to resolve linked report_ref payloads.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate that generated outputs are current instead of rewriting them.",
    )
    return parser.parse_args(argv)


def display_input_path(path: Path) -> str:
    for base in (REPO_ROOT, REPO_ROOT.parent):
        try:
            return str(path.relative_to(base))
        except ValueError:
            continue
    return str(path)


def display_repo_input_path(path: Path, *, repo_roots: tuple[tuple[str, Path], ...]) -> str:
    for repo_name, repo_root in repo_roots:
        try:
            relative_path = path.relative_to(repo_root)
        except ValueError:
            continue
        return f"{repo_name}/{relative_path.as_posix()}"
    return display_input_path(path)


def load_json_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ReceiptValidationError(f"missing {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ReceiptValidationError(f"invalid JSON in {label}: {path}") from exc
    if not isinstance(payload, dict):
        raise ReceiptValidationError(f"{label} must be a JSON object: {path}")
    return payload


def load_jsonl_objects(path: Path, *, label: str) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise ReceiptValidationError(f"missing {label}: {path}") from exc

    rows: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ReceiptValidationError(
                f"invalid JSON line in {label}: {path}:{line_number}"
            ) from exc
        if not isinstance(payload, dict):
            raise ReceiptValidationError(
                f"{label} entries must be JSON objects: {path}:{line_number}"
            )
        rows.append(payload)
    if not rows:
        raise ReceiptValidationError(f"{label} must expose at least one JSON object: {path}")
    return rows


def codex_plane_example_paths() -> tuple[Path, Path, Path]:
    public_profile_root = repo_root_from_env("AOA_8DIONYSUS_ROOT", DEFAULT_PUBLIC_PROFILE_ROOT)
    sdk_root = repo_root_from_env("AOA_SDK_ROOT", DEFAULT_AOA_SDK_ROOT)
    return (
        public_profile_root / "examples" / "codex_plane_trust_state.example.json",
        sdk_root
        / "mechanics"
        / "codex-projection"
        / "parts"
        / "live-rollout-status-readout"
        / "examples"
        / "live-rollout-status-snapshot.example.json",
        public_profile_root / "examples" / "codex_plane_rollout_receipt.example.json",
    )


def codex_plane_generated_from() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    trust_path, status_path, receipt_path = codex_plane_example_paths()
    public_profile_root = repo_root_from_env("AOA_8DIONYSUS_ROOT", DEFAULT_PUBLIC_PROFILE_ROOT)
    sdk_root = repo_root_from_env("AOA_SDK_ROOT", DEFAULT_AOA_SDK_ROOT)
    trust = load_json_object(trust_path, label="codex plane trust-state example")
    status = load_json_object(status_path, label="codex plane deploy-status example")
    receipt = load_json_object(receipt_path, label="codex plane rollout receipt example")
    latest_observed_at = max(
        parse_iso_datetime_or_min(trust.get("captured_at")),
        parse_iso_datetime_or_min(status.get("observed_at")),
        parse_iso_datetime_or_min(receipt.get("verified_at")),
    ).isoformat().replace("+00:00", "Z")
    source = {
        "receipt_input_paths": [
            display_repo_input_path(
                trust_path,
                repo_roots=(("8Dionysus", public_profile_root), ("aoa-sdk", sdk_root)),
            ),
            display_repo_input_path(
                status_path,
                repo_roots=(("8Dionysus", public_profile_root), ("aoa-sdk", sdk_root)),
            ),
            display_repo_input_path(
                receipt_path,
                repo_roots=(("8Dionysus", public_profile_root), ("aoa-sdk", sdk_root)),
            ),
        ],
        "total_receipts": 1,
        "latest_observed_at": latest_observed_at,
    }
    return source, trust, status, receipt


def codex_trusted_rollout_paths() -> tuple[Path, Path, Path, Path]:
    public_profile_root = repo_root_from_env("AOA_8DIONYSUS_ROOT", DEFAULT_PUBLIC_PROFILE_ROOT)
    rollout_root = public_profile_root / "generated" / "codex" / "rollout"
    return (
        rollout_root / "deploy_history.jsonl",
        rollout_root / "regeneration_campaigns.min.json",
        rollout_root / "rollback_windows.min.json",
        rollout_root / "rollout_latest.min.json",
    )


def codex_trusted_rollout_generated_from() -> tuple[
    dict[str, Any], list[dict[str, Any]], dict[str, Any], dict[str, Any], dict[str, Any]
]:
    (
        deploy_history_path,
        regeneration_path,
        rollback_path,
        latest_path,
    ) = codex_trusted_rollout_paths()
    public_profile_root = repo_root_from_env("AOA_8DIONYSUS_ROOT", DEFAULT_PUBLIC_PROFILE_ROOT)
    deploy_history = load_jsonl_objects(
        deploy_history_path,
        label="codex trusted rollout deploy history",
    )
    regeneration = load_json_object(
        regeneration_path,
        label="codex trusted rollout regeneration campaigns",
    )
    rollback = load_json_object(
        rollback_path,
        label="codex trusted rollout rollback windows",
    )
    latest = load_json_object(
        latest_path,
        label="codex trusted rollout latest summary",
    )
    observed_candidates: list[datetime] = []
    for payload in (deploy_history, regeneration, rollback, latest):
        observed_candidates.extend(collect_datetime_candidates(payload))
    if not observed_candidates:
        raise ReceiptValidationError(
            "codex trusted rollout sources must expose at least one parseable timestamp"
        )
    latest_observed_at = max(observed_candidates).isoformat().replace("+00:00", "Z")
    source = {
        "receipt_input_paths": [
            display_repo_input_path(
                deploy_history_path,
                repo_roots=(("8Dionysus", public_profile_root),),
            ),
            display_repo_input_path(
                regeneration_path,
                repo_roots=(("8Dionysus", public_profile_root),),
            ),
            display_repo_input_path(
                rollback_path,
                repo_roots=(("8Dionysus", public_profile_root),),
            ),
            display_repo_input_path(
                latest_path,
                repo_roots=(("8Dionysus", public_profile_root),),
            ),
        ],
        "total_receipts": len(deploy_history),
        "latest_observed_at": latest_observed_at,
    }
    return source, deploy_history, regeneration, rollback, latest


def codex_rollout_campaign_paths() -> tuple[Path, Path, Path]:
    public_profile_root = repo_root_from_env("AOA_8DIONYSUS_ROOT", DEFAULT_PUBLIC_PROFILE_ROOT)
    return (
        public_profile_root / "examples" / "rollout_campaign_window.example.json",
        public_profile_root / "examples" / "drift_review_window.example.json",
        public_profile_root / "examples" / "rollback_followthrough_window.example.json",
    )


def codex_rollout_campaign_generated_from() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    campaign_path, review_path, rollback_path = codex_rollout_campaign_paths()
    public_profile_root = repo_root_from_env("AOA_8DIONYSUS_ROOT", DEFAULT_PUBLIC_PROFILE_ROOT)
    campaign = load_json_object(campaign_path, label="rollout campaign window example")
    review = load_json_object(review_path, label="drift review window example")
    rollback = load_json_object(rollback_path, label="rollback followthrough window example")
    latest_observed_at = max(
        parse_iso_datetime_or_min(campaign.get("window_opened_at")),
        parse_iso_datetime_or_min(review.get("reviewed_at")),
        parse_iso_datetime_or_min(rollback.get("prepared_at")),
    ).isoformat().replace("+00:00", "Z")
    source = {
        "receipt_input_paths": [
            display_repo_input_path(campaign_path, repo_roots=(("8Dionysus", public_profile_root),)),
            display_repo_input_path(review_path, repo_roots=(("8Dionysus", public_profile_root),)),
            display_repo_input_path(rollback_path, repo_roots=(("8Dionysus", public_profile_root),)),
        ],
        "total_receipts": 1,
        "latest_observed_at": latest_observed_at,
    }
    return source, campaign, review, rollback


def latest_rollout_history_row(
    deploy_history: list[dict[str, Any]], latest: dict[str, Any]
) -> dict[str, Any]:
    latest_rollout_campaign_ref = latest.get("latest_rollout_campaign_ref")
    if is_nonempty_string(latest_rollout_campaign_ref):
        for row in reversed(deploy_history):
            if row.get("rollout_campaign_ref") == latest_rollout_campaign_ref:
                return row
        raise ReceiptValidationError(
            "latest rollout campaign ref does not resolve inside deploy history"
        )
    return deploy_history[-1]


def continuity_window_source_paths() -> tuple[Path, Path, Path, Path]:
    agents_root = repo_root_from_env("AOA_AGENTS_ROOT", DEFAULT_AOA_AGENTS_ROOT)
    playbooks_root = repo_root_from_env("AOA_PLAYBOOKS_ROOT", DEFAULT_AOA_PLAYBOOKS_ROOT)
    memo_root = repo_root_from_env("AOA_MEMO_ROOT", DEFAULT_AOA_MEMO_ROOT)
    evals_root = repo_root_from_env("AOA_EVALS_ROOT", DEFAULT_EVALS_ROOT)
    return continuity_window_reference_paths(
        agents_root=agents_root,
        playbooks_root=playbooks_root,
        memo_root=memo_root,
        evals_root=evals_root,
    )


def continuity_window_input_bundle() -> ContinuityWindowInputBundle:
    agents_root = repo_root_from_env("AOA_AGENTS_ROOT", DEFAULT_AOA_AGENTS_ROOT)
    playbooks_root = repo_root_from_env("AOA_PLAYBOOKS_ROOT", DEFAULT_AOA_PLAYBOOKS_ROOT)
    memo_root = repo_root_from_env("AOA_MEMO_ROOT", DEFAULT_AOA_MEMO_ROOT)
    evals_root = repo_root_from_env("AOA_EVALS_ROOT", DEFAULT_EVALS_ROOT)
    return load_continuity_window_reference_bundle(
        agents_root=agents_root,
        playbooks_root=playbooks_root,
        memo_root=memo_root,
        evals_root=evals_root,
    )

def continuity_window_generated_from() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Preserve the legacy mutable tuple facade for compatibility callers."""

    return continuity_window_input_bundle().mutable_parts()


def component_refresh_source_paths() -> tuple[Path, Path]:
    sdk_root = repo_root_from_env("AOA_SDK_ROOT", DEFAULT_AOA_SDK_ROOT)
    return reviewed_sdk_example_paths(sdk_root)


def component_refresh_input_bundle() -> ComponentRefreshInputBundle:
    sdk_root = repo_root_from_env("AOA_SDK_ROOT", DEFAULT_AOA_SDK_ROOT)
    return load_reviewed_sdk_example_bundle(sdk_root)


def component_refresh_generated_from() -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """Preserve the legacy mutable tuple facade for compatibility callers."""

    return component_refresh_input_bundle().mutable_parts()


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
    if report is None and report_ref == "repo:aoa-evals/bundles/aoa-stress-recovery-window/reports/example-report.json":
        report_path = (
            evals_root
            / "evals"
            / "comparison"
            / "longitudinal-window"
            / "aoa-stress-recovery-window"
            / "reports"
            / "example-report.json"
        )
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


def build_codex_plane_deployment_summary() -> dict[str, Any]:
    source, trust, status, receipt = codex_plane_generated_from()
    trust_posture = str(trust.get("trust_posture") or "unknown")
    trust_posture_counts = {posture: 0 for posture in TRUST_POSTURES}
    if trust_posture in trust_posture_counts:
        trust_posture_counts[trust_posture] = 1

    stable_mcp_name_set = sorted(
        {
            str(name)
            for name in status.get("active_mcp_servers", [])
            if isinstance(name, str) and name
        }
    )
    drift_count = 1 if status.get("drift_detected") is True or receipt.get("deployment_state") == "drifted" else 0
    rollback_recommended_count = 1 if (
        trust_posture == "rollback_recommended"
        or receipt.get("deployment_state") == "rollback_recommended"
        or status.get("next_action") == "rollback"
    ) else 0

    return {
        "schema_version": "aoa_stats_codex_plane_deployment_summary_v1",
        "generated_from": source,
        "workspaces_total": 1,
        "latest_rollout_state": receipt.get("deployment_state") or "render_only",
        "trust_posture_counts": trust_posture_counts,
        "drift_count": drift_count,
        "rollback_recommended_count": rollback_recommended_count,
        "stable_mcp_name_set": stable_mcp_name_set,
        "latest_receipt_ref": receipt.get("rollout_receipt_id") or "",
    }


def build_codex_rollout_operations_summary() -> dict[str, Any]:
    source, deploy_history, _, _, latest = codex_trusted_rollout_generated_from()
    counts_by_state = Counter(
        str(row.get("state"))
        for row in deploy_history
        if isinstance(row.get("state"), str) and row.get("state")
    )
    return {
        "schema_version": "aoa_stats_codex_rollout_operations_summary_v1",
        "generated_from": source,
        "latest_rollout_campaign_ref": latest.get("latest_rollout_campaign_ref") or "",
        "latest_state": latest.get("latest_state") or "unknown",
        "active_drift_window_ref": latest.get("active_drift_window_ref"),
        "active_rollback_window_ref": latest.get("active_rollback_window_ref"),
        "latest_stable_rollout_campaign_ref": latest.get("latest_stable_rollout_campaign_ref") or "",
        "counts_by_state": dict(sorted(counts_by_state.items())),
        "source_refs": list(normalize_string_list(latest.get("source_refs"))),
    }


def build_codex_rollout_drift_summary() -> dict[str, Any]:
    source, deploy_history, _, _, latest = codex_trusted_rollout_generated_from()
    latest_history = latest_rollout_history_row(deploy_history, latest)
    drift_refs = normalize_string_list(latest_history.get("drift_window_refs"))
    rollback_refs = normalize_string_list(latest_history.get("rollback_window_refs"))
    latest_state = str(latest.get("latest_state") or latest_history.get("state") or "unknown")
    return {
        "schema_version": "aoa_stats_codex_rollout_drift_summary_v1",
        "generated_from": source,
        "latest_rollout_campaign_ref": latest.get("latest_rollout_campaign_ref") or "",
        "drift_window_ref": drift_refs[0] if drift_refs else None,
        "drift_state": str(latest_history.get("drift_state") or "quiet"),
        "repair_attempted": bool(latest_history.get("repair_attempted")),
        "rollback_required": bool(rollback_refs) or latest_state in {"rollback_open", "rolled_back"},
        "source_refs": [
            "8Dionysus/generated/codex/rollout/deploy_history.jsonl",
            "8Dionysus/generated/codex/rollout/rollback_windows.min.json",
        ],
    }


def build_rollout_campaign_summary() -> dict[str, Any]:
    source, campaign, review, rollback = codex_rollout_campaign_generated_from()
    lineage_refs = campaign.get("lineage_refs")
    if not isinstance(lineage_refs, dict):
        lineage_refs = {}
    review_status = str(review.get("status") or "closed")
    rollback_status = str(rollback.get("status") or "retired")
    return {
        "schema_version": "aoa_stats_rollout_campaign_summary_v1",
        "generated_from": source,
        "campaign_ref": str(campaign.get("campaign_ref") or ""),
        "campaign_state": str(campaign.get("state") or "review_required"),
        "open_batches": 1 if campaign.get("state") == "open" else 0,
        "pending_reviews": 1 if review_status in {"review_required", "reanchor", "rollback_considered"} else 0,
        "rollback_ready_windows": 1 if rollback_status in {"ready_if_needed", "armed"} else 0,
        "stage_counts": {
            "candidate_refs": len(normalize_string_list(lineage_refs.get("candidate_refs"))),
            "seed_refs": len(normalize_string_list(lineage_refs.get("seed_refs"))),
            "object_refs": len(normalize_string_list(lineage_refs.get("object_refs"))),
        },
        "source_refs": list(source["receipt_input_paths"]),
    }


def build_drift_review_summary() -> dict[str, Any]:
    source, campaign, review, rollback = codex_rollout_campaign_generated_from()
    signals = review.get("signals")
    signal_counts: Counter[str] = Counter()
    if isinstance(signals, dict):
        for name in sorted(signals):
            signal_counts[name] = 1 if signals.get(name) is True else 0
    decision_counts: dict[str, int] = {}
    decision = review.get("decision")
    if is_nonempty_string(decision):
        decision_counts[str(decision)] = 1
    rollback_status = str(rollback.get("status") or "retired")
    return {
        "schema_version": "aoa_stats_drift_review_summary_v1",
        "generated_from": source,
        "campaign_ref": str(campaign.get("campaign_ref") or ""),
        "review_ref": str(review.get("review_ref") or ""),
        "review_status": str(review.get("status") or "closed"),
        "review_windows_total": 1,
        "signals_seen": dict(sorted(signal_counts.items())),
        "decision_counts": decision_counts,
        "rollback_ref": str(rollback.get("rollback_ref") or ""),
        "rollback_ready": rollback_status in {"ready_if_needed", "armed"},
        "source_refs": list(source["receipt_input_paths"]),
    }


def build_continuity_window_summary() -> dict[str, Any]:
    bundle = continuity_window_input_bundle()
    return build_continuity_window_summary_from_inputs(
        bundle.source,
        bundle.continuity_window,
        bundle.memo_thread,
    )


def memory_movement_source_paths() -> tuple[Path, Path, Path, Path]:
    memo_root = repo_root_from_env("AOA_MEMO_ROOT", DEFAULT_AOA_MEMO_ROOT)
    return (
        memo_root / "generated" / "memory-objects" / "memory_object_catalog.min.json",
        memo_root / "memo" / "objects",
        memo_root / "memo" / "intake" / "reviewed",
        memo_root / "memo" / "intake" / "receipts",
    )


def load_json_file_set(path: Path, *, label: str) -> list[tuple[Path, dict[str, Any]]]:
    if not path.exists():
        raise ReceiptValidationError(f"missing {label}: {path}")
    return [
        (item_path, load_json_object(item_path, label=f"{label} JSON"))
        for item_path in sorted(path.glob("*.json"))
    ]


def load_memory_object_set(path: Path) -> list[tuple[Path, dict[str, Any]]]:
    if not path.exists():
        raise ReceiptValidationError(f"missing reviewed memory object corpus: {path}")
    return [
        (object_path, load_json_object(object_path, label="reviewed memory object"))
        for object_path in sorted(path.rglob("object.json"))
    ]


def memory_object_recall_status(memory_object: dict[str, Any]) -> str:
    lifecycle = memory_object.get("lifecycle")
    if not isinstance(lifecycle, dict):
        return "unknown"
    current_recall = lifecycle.get("current_recall")
    if not isinstance(current_recall, dict):
        return "unknown"
    status = current_recall.get("status")
    return str(status) if is_nonempty_string(status) else "unknown"


def memory_object_bridge_status(memory_object: dict[str, Any]) -> str:
    bridges = memory_object.get("bridges")
    if not isinstance(bridges, dict):
        return "absent"
    status = bridges.get("kag_lift_status")
    return str(status) if is_nonempty_string(status) else "unknown"


def memory_object_datetime(memory_object: dict[str, Any], key: str) -> datetime:
    time_payload = memory_object.get("time")
    if not isinstance(time_payload, dict):
        return datetime.min.replace(tzinfo=UTC)
    return parse_iso_datetime_or_min(time_payload.get(key))


def memory_movement_generated_from() -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    list[tuple[Path, dict[str, Any]]],
    list[tuple[Path, dict[str, Any]]],
    list[tuple[Path, dict[str, Any]]],
]:
    catalog_path, objects_path, reviewed_path, receipts_path = memory_movement_source_paths()
    memo_root = repo_root_from_env("AOA_MEMO_ROOT", DEFAULT_AOA_MEMO_ROOT)
    catalog = load_json_object(catalog_path, label="aoa-memo memory object min catalog")
    catalog_objects = catalog.get("memory_objects")
    if not isinstance(catalog_objects, list):
        raise ReceiptValidationError("aoa-memo memory object min catalog must expose memory_objects")
    if catalog.get("source_of_truth") != "aoa-memo-object-read-models-v2":
        raise ReceiptValidationError(
            "aoa-memo memory object catalog must keep source_of_truth "
            "aoa-memo-object-read-models-v2"
        )

    memory_objects = load_memory_object_set(objects_path)
    reviewed_intakes = load_json_file_set(reviewed_path, label="aoa-memo reviewed intake packets")
    landing_receipts = load_json_file_set(receipts_path, label="aoa-memo landing receipts")

    object_ids = {
        item.get("id")
        for _, item in memory_objects
        if isinstance(item.get("id"), str) and item.get("id")
    }
    catalog_reviewed_ids = {
        item.get("id")
        for item in catalog_objects
        if isinstance(item, dict) and item.get("source_kind") == "reviewed_corpus"
    }
    if object_ids != catalog_reviewed_ids:
        missing_in_catalog = sorted(object_ids - catalog_reviewed_ids)
        missing_in_objects = sorted(catalog_reviewed_ids - object_ids)
        raise ReceiptValidationError(
            "aoa-memo reviewed corpus object/catalog mismatch: "
            f"missing_in_catalog={missing_in_catalog}; missing_in_objects={missing_in_objects}"
        )

    latest_candidates = [
        memory_object_datetime(item, "observed_at")
        for _, item in memory_objects
    ]
    latest_candidates.extend(
        parse_iso_datetime_or_min(receipt.get("landed_at"))
        for _, receipt in landing_receipts
    )
    latest_candidates.extend(
        parse_iso_datetime_or_min(packet.get("created_at"))
        for _, packet in reviewed_intakes
    )
    latest_observed_at = max(latest_candidates or [datetime.min.replace(tzinfo=UTC)])
    if latest_observed_at == datetime.min.replace(tzinfo=UTC):
        raise ReceiptValidationError("aoa-memo memory movement inputs have no observable timestamp")

    source = {
        "receipt_input_paths": [
            display_repo_input_path(catalog_path, repo_roots=(("aoa-memo", memo_root),)),
            display_repo_input_path(objects_path, repo_roots=(("aoa-memo", memo_root),)),
            display_repo_input_path(reviewed_path, repo_roots=(("aoa-memo", memo_root),)),
            display_repo_input_path(receipts_path, repo_roots=(("aoa-memo", memo_root),)),
        ],
        "total_receipts": len(memory_objects) + len(reviewed_intakes) + len(landing_receipts),
        "latest_observed_at": latest_observed_at.isoformat().replace("+00:00", "Z"),
    }
    return source, catalog_objects, memory_objects, reviewed_intakes, landing_receipts


def build_memory_movement_summary() -> dict[str, Any]:
    source, catalog_objects, memory_objects, reviewed_intakes, landing_receipts = (
        memory_movement_generated_from()
    )
    memo_root = repo_root_from_env("AOA_MEMO_ROOT", DEFAULT_AOA_MEMO_ROOT)

    source_kind_counts: Counter[str] = Counter()
    for item in catalog_objects:
        if isinstance(item, dict):
            source_kind_counts[str(item.get("source_kind") or "unknown")] += 1

    kind_counts: Counter[str] = Counter()
    review_state_counts: Counter[str] = Counter()
    recall_status_counts: Counter[str] = Counter()
    temperature_counts: Counter[str] = Counter()
    kag_lift_status_counts: Counter[str] = Counter()
    reviewed_object_rows: list[dict[str, Any]] = []

    for object_path, memory_object in memory_objects:
        object_id = str(memory_object.get("id") or "")
        if not object_id:
            raise ReceiptValidationError(f"reviewed memory object is missing id: {object_path}")
        kind = str(memory_object.get("kind") or "unknown")
        lifecycle = memory_object.get("lifecycle")
        trust = memory_object.get("trust")
        if not isinstance(lifecycle, dict):
            lifecycle = {}
        if not isinstance(trust, dict):
            trust = {}
        review_state = str(lifecycle.get("review_state") or "unknown")
        temperature = str(trust.get("temperature") or "unknown")
        recall_status = memory_object_recall_status(memory_object)
        kag_lift_status = memory_object_bridge_status(memory_object)

        kind_counts[kind] += 1
        review_state_counts[review_state] += 1
        recall_status_counts[recall_status] += 1
        temperature_counts[temperature] += 1
        kag_lift_status_counts[kag_lift_status] += 1
        reviewed_object_rows.append(
            {
                "id": object_id,
                "kind": kind,
                "review_state": review_state,
                "current_recall_status": recall_status,
                "temperature": temperature,
                "kag_lift_status": kag_lift_status,
                "object_ref": display_repo_input_path(
                    object_path,
                    repo_roots=(("aoa-memo", memo_root),),
                ),
            }
        )

    landing_result_counts = Counter(
        str(receipt.get("result") or "unknown")
        for _, receipt in landing_receipts
    )
    landed_object_refs = sorted({
        str(receipt.get("object_ref"))
        for _, receipt in landing_receipts
        if is_nonempty_string(receipt.get("object_ref"))
    })

    return {
        "schema_version": "aoa_stats_memory_movement_summary_v1",
        "generated_from": source,
        "authority": {
            "summary_owner": "aoa-stats",
            "memory_owner": "aoa-memo",
            "authority_ceiling": (
                "Derived movement summary only; weaker than aoa-memo reviewed "
                "memory objects, landing receipts, and source refs."
            ),
        },
        "source_kind_counts": string_count_map(source_kind_counts),
        "reviewed_corpus": {
            "object_count": len(memory_objects),
            "by_kind": string_count_map(kind_counts),
            "by_review_state": string_count_map(review_state_counts),
            "by_recall_status": string_count_map(recall_status_counts),
            "by_temperature": string_count_map(temperature_counts),
            "by_kag_lift_status": string_count_map(kag_lift_status_counts),
            "objects": reviewed_object_rows,
        },
        "reviewed_intake": {
            "packet_count": len(reviewed_intakes),
            "landing_receipt_count": len(landing_receipts),
            "landing_result_counts": string_count_map(landing_result_counts),
            "landed_object_refs": landed_object_refs,
        },
        "consumer_handoff": {
            "consumer_refs": list(MEMORY_CONSUMER_REFS),
            "handoff_memory_ref": "memo.decision.2026-05-22.reviewed-memory-consumer-handoff-spine",
            "posture": "derived_consumer_summary",
            "memory_route_boundary": dict(MEMORY_ROUTE_BOUNDARY),
        },
    }


def build_component_refresh_summary() -> dict[str, Any]:
    bundle = component_refresh_input_bundle()
    return build_component_refresh_summary_from_inputs(
        bundle.source,
        bundle.hints,
        bundle.decisions,
    )


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


def build_titan_incarnation_summary() -> dict[str, Any]:
    return {
        "schema_version": "titan_incarnation_summary/v1",
        "summary_ref": "generated:titan-incarnation-summary:seed",
        "source_receipt_refs": ["seed:titan-fifteenth-wave"],
        "counts": {
            "seeded_titans": 5,
            "default_active": 3,
            "locked_by_gate": 2,
        },
    }


def build_titan_summon_summary() -> dict[str, Any]:
    return {
        "schema_version": "titan_summon_summary/v1",
        "summary_ref": "generated:titan-summon-summary:seed",
        "source_ledger_refs": ["seed:titan-sixteenth-wave"],
        "counts": {
            "agents_invoked": 0,
            "reports_received": 0,
            "findings_reported": 0,
            "memory_candidates_created": 0,
        },
    }


def build_all_views(
    receipts: list[dict[str, Any]],
    input_paths: list[str],
    *,
    evals_root: Path | None = None,
    source_registry: dict[str, Any] | None = None,
    source_registry_ref: str | None = None,
    optional_output_names: AbstractSet[str] | None = None,
) -> dict[str, dict[str, Any]]:
    active_receipts = resolve_active_receipts(receipts)
    source = generated_from(active_receipts, input_paths)
    resolved_evals_root = (
        evals_root.expanduser().resolve()
        if evals_root is not None
        else repo_root_from_env("AOA_EVALS_ROOT", DEFAULT_EVALS_ROOT).resolve()
    )
    resolved_source_registry = source_registry
    resolved_source_registry_ref = source_registry_ref
    if resolved_source_registry is None and DEFAULT_SOURCE_REGISTRY.exists():
        resolved_source_registry = load_json_object(
            DEFAULT_SOURCE_REGISTRY,
            label=LIVE_SOURCE_REGISTRY_RELATIVE.as_posix(),
        )
        resolved_source_registry_ref = LIVE_SOURCE_REGISTRY_RELATIVE.as_posix()
    outputs = {
        "object_summary.min.json": build_object_summary(active_receipts, source),
        "candidate_lineage_summary.min.json": build_candidate_lineage_summary(
            active_receipts, source
        ),
        "owner_landing_summary.min.json": build_owner_landing_summary(active_receipts, source),
        "supersession_drop_summary.min.json": build_supersession_drop_summary(
            active_receipts, source
        ),
        "core_skill_application_summary.min.json": build_core_skill_application_summary(
            active_receipts, source
        ),
        "repeated_window_summary.min.json": build_repeated_window_summary(active_receipts, source),
        "route_progression_summary.min.json": build_route_progression_summary(active_receipts, source),
        "fork_calibration_summary.min.json": build_fork_calibration_summary(active_receipts, source),
        "session_growth_branch_summary.min.json": build_session_growth_branch_summary(
            active_receipts, source
        ),
        "automation_pipeline_summary.min.json": build_automation_pipeline_summary(
            active_receipts, source
        ),
        "automation_followthrough_summary.min.json": build_automation_followthrough_summary(
            active_receipts, source
        ),
        "runtime_closeout_summary.min.json": build_runtime_closeout_summary(active_receipts, source),
        "stress_recovery_window_summary.min.json": build_stress_recovery_window_summary(
            active_receipts, source, evals_root=resolved_evals_root
        ),
        "source_coverage_summary.min.json": build_source_coverage_summary(
            active_receipts,
            source,
            source_registry=resolved_source_registry,
            source_registry_ref=resolved_source_registry_ref,
        ),
        "surface_detection_summary.min.json": build_surface_detection_summary(active_receipts, source),
    }
    allowed_optional_outputs = (
        None if optional_output_names is None else frozenset(optional_output_names)
    )
    for name, builder in (
        ("codex_plane_deployment_summary.min.json", build_codex_plane_deployment_summary),
        ("codex_rollout_operations_summary.min.json", build_codex_rollout_operations_summary),
        ("codex_rollout_drift_summary.min.json", build_codex_rollout_drift_summary),
        ("rollout_campaign_summary.min.json", build_rollout_campaign_summary),
        ("drift_review_summary.min.json", build_drift_review_summary),
        ("continuity_window_summary.min.json", build_continuity_window_summary),
        ("component_refresh_summary.min.json", build_component_refresh_summary),
        ("memory_movement_summary.min.json", build_memory_movement_summary),
        ("titan_incarnation_summary.min.json", build_titan_incarnation_summary),
        ("titan_summon_summary.min.json", build_titan_summon_summary),
    ):
        if allowed_optional_outputs is not None and name not in allowed_optional_outputs:
            continue
        try:
            outputs[name] = builder()
        except ReceiptValidationError as exc:
            if not str(exc).startswith("missing "):
                raise
    outputs["summary_surface_catalog.min.json"] = build_summary_surface_catalog(
        source,
        available_output_names=set(outputs),
    )
    return outputs


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
        [display_input_path(path) for path in input_paths],
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
