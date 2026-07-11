from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from .read_model_values import is_nonempty_string, parse_iso_datetime
from .receipt_abi import ReceiptValidationError


TRUST_POSTURES = (
    "unknown",
    "root_mismatch",
    "config_inactive",
    "trusted_ready",
    "rollout_active",
    "rollback_recommended",
)
DEPLOYMENT_STATES = (
    "render_only",
    "dry_run_ready",
    "applied",
    "verified",
    "drifted",
    "rollback_recommended",
)
CODEX_PLANE_V1_STABLE_MCP_NAMES = (
    "aoa_workspace",
    "aoa_stats",
    "dionysus",
    "aoa_memo",
    "aoa_session_memory",
    "aoa_evals",
    "aoa_decisions",
    "abyss_machine",
)
TRUST_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "trust_state_id",
        "workspace_root",
        "detected_project_root",
        "project_root_markers_expected",
        "project_root_marker_match",
        "project_config_active",
        "active_config_layers",
        "hooks_enabled",
        "hook_layers_detected",
        "mcp_server_names_expected",
        "mcp_server_names_detected",
        "stable_names_ok",
        "trust_posture",
        "warnings",
        "captured_at",
    }
)
REGENERATION_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "regeneration_report_id",
        "source_profile_ref",
        "target_workspace_root",
        "render_posture",
        "rendered_files",
        "stable_names",
        "warnings",
        "generated_at",
    }
)
RENDERED_FILE_REQUIRED_FIELDS = frozenset(
    {"relative_path", "source_path", "mode", "changed", "sha256"}
)
RECEIPT_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "rollout_receipt_id",
        "trust_state_id",
        "regeneration_report_id",
        "apply_mode",
        "deployment_state",
        "doctor_result",
        "rollback_plan_ref",
        "stats_refresh_required",
        "verified_at",
    }
)


def _require_exact_fields(
    payload: Mapping[str, Any], *, required: frozenset[str], label: str
) -> None:
    fields = set(payload)
    missing = required - fields
    if missing:
        raise ReceiptValidationError(
            f"{label} is missing required fields: {', '.join(sorted(missing))}"
        )
    extra = fields - required
    if extra:
        raise ReceiptValidationError(
            f"{label} has unsupported fields: "
            + ", ".join(sorted(str(field) for field in extra))
        )


def _require_string(value: Any, *, label: str) -> str:
    if not is_nonempty_string(value):
        raise ReceiptValidationError(f"{label} must be a non-empty string")
    return str(value)


def _require_bool(value: Any, *, label: str) -> bool:
    if not isinstance(value, bool):
        raise ReceiptValidationError(f"{label} must be boolean")
    return value


def _require_string_sequence(
    value: Any, *, label: str, allow_empty: bool, unique: bool = True
) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ReceiptValidationError(f"{label} must be a string list")
    items = tuple(value)
    if not allow_empty and not items:
        raise ReceiptValidationError(f"{label} must be a non-empty string list")
    if not all(is_nonempty_string(item) for item in items):
        raise ReceiptValidationError(f"{label} must be a string list")
    normalized = tuple(str(item) for item in items)
    if unique and len(normalized) != len(set(normalized)):
        raise ReceiptValidationError(f"{label} must not contain duplicates")
    return normalized


def _require_datetime(value: Any, *, label: str) -> datetime:
    if not isinstance(value, str) or re.search(
        r"[Tt].*(?:[Zz]|[+-]\d{2}:\d{2})$", value
    ) is None:
        raise ReceiptValidationError(f"{label} must be a date-time")
    parsed = parse_iso_datetime(value)
    if parsed is None:
        raise ReceiptValidationError(f"{label} must be a date-time")
    return parsed


def _validate_trust_state(trust: Mapping[str, Any]) -> datetime:
    label = "Codex Plane trust state"
    _require_exact_fields(trust, required=TRUST_REQUIRED_FIELDS, label=label)
    if trust.get("schema_version") != "8dionysus_codex_plane_trust_state_v1":
        raise ReceiptValidationError(f"{label} must keep its published v1 schema")

    for field in (
        "trust_state_id",
        "workspace_root",
        "detected_project_root",
    ):
        _require_string(trust.get(field), label=f"{label} {field}")
    _require_string_sequence(
        trust.get("project_root_markers_expected"),
        label=f"{label} project_root_markers_expected",
        allow_empty=False,
    )
    _require_string_sequence(
        trust.get("project_root_marker_match"),
        label=f"{label} project_root_marker_match",
        allow_empty=True,
    )
    _require_string_sequence(
        trust.get("active_config_layers"),
        label=f"{label} active_config_layers",
        allow_empty=True,
    )
    _require_string_sequence(
        trust.get("hook_layers_detected"),
        label=f"{label} hook_layers_detected",
        allow_empty=True,
    )
    expected_names = _require_string_sequence(
        trust.get("mcp_server_names_expected"),
        label=f"{label} mcp_server_names_expected",
        allow_empty=False,
    )
    detected_names = _require_string_sequence(
        trust.get("mcp_server_names_detected"),
        label=f"{label} mcp_server_names_detected",
        allow_empty=True,
    )
    if set(expected_names) != set(CODEX_PLANE_V1_STABLE_MCP_NAMES):
        raise ReceiptValidationError(
            f"{label} expected MCP names must match the published v1 stable set"
        )
    project_config_active = _require_bool(
        trust.get("project_config_active"),
        label=f"{label} project_config_active",
    )
    hooks_enabled = _require_bool(
        trust.get("hooks_enabled"), label=f"{label} hooks_enabled"
    )
    stable_names_ok = _require_bool(
        trust.get("stable_names_ok"), label=f"{label} stable_names_ok"
    )
    required_names_present = set(expected_names) <= set(detected_names)
    if stable_names_ok and not required_names_present:
        raise ReceiptValidationError(
            f"{label} stable_names_ok cannot hide detected-name drift"
        )
    trust_posture = trust.get("trust_posture")
    if trust_posture not in TRUST_POSTURES:
        raise ReceiptValidationError(
            f"{label} trust_posture is outside the published grammar"
        )
    root_matches = trust.get("workspace_root") == trust.get("detected_project_root")
    if trust_posture == "root_mismatch" and root_matches:
        raise ReceiptValidationError(
            f"{label} root_mismatch posture requires an actual root mismatch"
        )
    if trust_posture == "config_inactive" and project_config_active:
        raise ReceiptValidationError(
            f"{label} config_inactive posture requires inactive project config"
        )
    if trust_posture in {"trusted_ready", "rollout_active"} and not all(
        (
            root_matches,
            project_config_active,
            hooks_enabled,
            stable_names_ok,
            required_names_present,
        )
    ):
        raise ReceiptValidationError(
            f"{label} {trust_posture} posture contradicts its trust evidence"
        )
    _require_string_sequence(
        trust.get("warnings"),
        label=f"{label} warnings",
        allow_empty=True,
        unique=False,
    )
    return _require_datetime(trust.get("captured_at"), label=f"{label} captured_at")


def _validate_regeneration_report(regeneration: Mapping[str, Any]) -> datetime:
    label = "Codex Plane regeneration report"
    _require_exact_fields(
        regeneration,
        required=REGENERATION_REQUIRED_FIELDS,
        label=label,
    )
    if (
        regeneration.get("schema_version")
        != "8dionysus_codex_plane_regeneration_report_v1"
    ):
        raise ReceiptValidationError(f"{label} must keep its published v1 schema")
    for field in (
        "regeneration_report_id",
        "source_profile_ref",
        "target_workspace_root",
    ):
        _require_string(regeneration.get(field), label=f"{label} {field}")
    if regeneration.get("render_posture") not in {"dry_run", "check", "execute"}:
        raise ReceiptValidationError(
            f"{label} render_posture is outside the published grammar"
        )

    rendered_files = regeneration.get("rendered_files")
    if not isinstance(rendered_files, Sequence) or isinstance(
        rendered_files, (str, bytes)
    ) or not rendered_files:
        raise ReceiptValidationError(f"{label} rendered_files must be non-empty")
    rendered_paths: set[str] = set()
    for index, item in enumerate(rendered_files):
        if not isinstance(item, Mapping):
            raise ReceiptValidationError(
                f"{label} rendered_files[{index}] must be an object"
            )
        item_label = f"{label} rendered_files[{index}]"
        _require_exact_fields(
            item,
            required=RENDERED_FILE_REQUIRED_FIELDS,
            label=item_label,
        )
        relative_path = _require_string(
            item.get("relative_path"), label=f"{item_label} relative_path"
        )
        _require_string(item.get("source_path"), label=f"{item_label} source_path")
        if item.get("mode") not in {"rewrite", "copy", "render_text", "symlink"}:
            raise ReceiptValidationError(
                f"{item_label} mode is outside the published grammar"
            )
        _require_bool(item.get("changed"), label=f"{item_label} changed")
        sha256 = _require_string(item.get("sha256"), label=f"{item_label} sha256")
        if re.fullmatch(r"[a-f0-9]{64}", sha256) is None:
            raise ReceiptValidationError(f"{item_label} sha256 must be lowercase hex")
        if relative_path in rendered_paths:
            raise ReceiptValidationError(
                f"{label} rendered_files must not duplicate {relative_path!r}"
            )
        rendered_paths.add(relative_path)
    missing_rendered_paths = {
        ".codex/config.toml",
        ".codex/hooks.json",
    } - rendered_paths
    if missing_rendered_paths:
        raise ReceiptValidationError(
            f"{label} is missing required rendered paths: "
            + ", ".join(sorted(missing_rendered_paths))
        )

    stable_names = regeneration.get("stable_names")
    if not isinstance(stable_names, Mapping):
        raise ReceiptValidationError(f"{label} stable_names must be an object")
    stable_name_keys = set(stable_names)
    expected_name_keys = set(CODEX_PLANE_V1_STABLE_MCP_NAMES)
    if stable_name_keys != expected_name_keys:
        raise ReceiptValidationError(
            f"{label} stable_names must match the published v1 stable set"
        )
    for name in CODEX_PLANE_V1_STABLE_MCP_NAMES:
        _require_bool(stable_names.get(name), label=f"{label} stable_names.{name}")
    _require_string_sequence(
        regeneration.get("warnings"),
        label=f"{label} warnings",
        allow_empty=True,
        unique=False,
    )
    return _require_datetime(
        regeneration.get("generated_at"), label=f"{label} generated_at"
    )


def _validate_rollout_receipt(receipt: Mapping[str, Any]) -> datetime:
    label = "Codex Plane rollout receipt"
    _require_exact_fields(receipt, required=RECEIPT_REQUIRED_FIELDS, label=label)
    if receipt.get("schema_version") != "8dionysus_codex_plane_rollout_receipt_v1":
        raise ReceiptValidationError(f"{label} must keep its published v1 schema")
    for field in (
        "rollout_receipt_id",
        "trust_state_id",
        "regeneration_report_id",
        "rollback_plan_ref",
    ):
        _require_string(receipt.get(field), label=f"{label} {field}")
    if receipt.get("apply_mode") not in {"dry_run", "execute"}:
        raise ReceiptValidationError(f"{label} apply_mode is outside the grammar")
    if receipt.get("deployment_state") not in DEPLOYMENT_STATES:
        raise ReceiptValidationError(
            f"{label} deployment_state is outside the published grammar"
        )
    if receipt.get("doctor_result") not in {"pass", "warn", "fail"}:
        raise ReceiptValidationError(
            f"{label} doctor_result is outside the published grammar"
        )
    if (
        receipt.get("deployment_state") == "verified"
        and receipt.get("doctor_result") != "pass"
    ):
        raise ReceiptValidationError(
            f"{label} verified deployment must keep doctor_result=pass"
        )
    _require_bool(
        receipt.get("stats_refresh_required"),
        label=f"{label} stats_refresh_required",
    )
    return _require_datetime(receipt.get("verified_at"), label=f"{label} verified_at")


def validate_codex_plane_deployment_chain(
    trust: Mapping[str, Any],
    regeneration: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> datetime:
    captured_at = _validate_trust_state(trust)
    generated_at = _validate_regeneration_report(regeneration)
    verified_at = _validate_rollout_receipt(receipt)

    if trust.get("workspace_root") != regeneration.get("target_workspace_root"):
        raise ReceiptValidationError(
            "Codex Plane regeneration target must match the trust-state workspace root"
        )
    if receipt.get("trust_state_id") != trust.get("trust_state_id"):
        raise ReceiptValidationError(
            "Codex Plane rollout receipt must reference the loaded trust state"
        )
    if receipt.get("regeneration_report_id") != regeneration.get(
        "regeneration_report_id"
    ):
        raise ReceiptValidationError(
            "Codex Plane rollout receipt must reference the loaded regeneration report"
        )
    if captured_at > verified_at or generated_at > verified_at:
        raise ReceiptValidationError(
            "Codex Plane trust and regeneration timestamps must not postdate "
            "the rollout receipt"
        )
    if trust.get("stable_names_ok") is True and not all(
        regeneration["stable_names"].values()
    ):
        raise ReceiptValidationError(
            "Codex Plane trust and regeneration stable-name evidence must agree"
        )
    return verified_at


def codex_plane_drift_present(
    trust: Mapping[str, Any],
    regeneration: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> bool:
    expected_names = set(trust["mcp_server_names_expected"])
    detected_names = set(trust["mcp_server_names_detected"])
    return any(
        (
            trust.get("trust_posture")
            in {"root_mismatch", "config_inactive", "rollback_recommended"},
            trust.get("workspace_root") != trust.get("detected_project_root"),
            trust.get("project_config_active") is False,
            trust.get("hooks_enabled") is False,
            trust.get("stable_names_ok") is False,
            not expected_names <= detected_names,
            not all(regeneration["stable_names"].values()),
            receipt.get("deployment_state") == "drifted",
            receipt.get("doctor_result") == "fail",
        )
    )


def codex_plane_rollback_recommended(
    trust: Mapping[str, Any],
    regeneration: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> bool:
    expected_names = set(trust["mcp_server_names_expected"])
    detected_names = set(trust["mcp_server_names_detected"])
    explicitly_recommended = any(
        (
            trust.get("trust_posture") == "rollback_recommended",
            receipt.get("deployment_state") == "rollback_recommended",
        )
    )
    if explicitly_recommended or receipt.get("doctor_result") == "fail":
        return True
    deployment_state = receipt.get("deployment_state")
    root_or_config_drift = any(
        (
            trust.get("workspace_root") != trust.get("detected_project_root"),
            trust.get("project_config_active") is False,
            trust.get("trust_posture") in {"root_mismatch", "config_inactive"},
        )
    )
    if root_or_config_drift and deployment_state in {
        "applied",
        "verified",
        "drifted",
    }:
        return True
    hook_or_name_drift = any(
        (
            trust.get("hooks_enabled") is False,
            trust.get("stable_names_ok") is False,
            not expected_names <= detected_names,
            not all(regeneration["stable_names"].values()),
        )
    )
    return hook_or_name_drift and deployment_state in {"applied", "verified"}


def build_codex_plane_deployment_summary(
    source: Mapping[str, Any],
    trust: Mapping[str, Any],
    regeneration: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    latest_observed_at = validate_codex_plane_deployment_chain(
        trust, regeneration, receipt
    )
    receipt_input_paths = _require_string_sequence(
        source.get("receipt_input_paths"),
        label="Codex Plane generated_from receipt_input_paths",
        allow_empty=False,
    )
    if len(receipt_input_paths) != 3:
        raise ReceiptValidationError(
            "Codex Plane generated_from must name exactly three input paths"
        )
    if source.get("total_receipts") != 1:
        raise ReceiptValidationError(
            "Codex Plane generated_from total_receipts must describe one rollout chain"
        )
    source_latest = _require_datetime(
        source.get("latest_observed_at"),
        label="Codex Plane generated_from latest_observed_at",
    )
    if source_latest != latest_observed_at:
        raise ReceiptValidationError(
            "Codex Plane generated_from latest_observed_at must match the rollout receipt"
        )

    trust_posture = str(trust["trust_posture"])
    trust_posture_counts = {posture: 0 for posture in TRUST_POSTURES}
    trust_posture_counts[trust_posture] = 1
    stable_names = regeneration["stable_names"]
    stable_mcp_names = sorted(
        name
        for name in trust["mcp_server_names_detected"]
        if stable_names.get(name) is True
    )
    return {
        "schema_version": "aoa_stats_codex_plane_deployment_summary_v1",
        "generated_from": {
            "receipt_input_paths": list(receipt_input_paths),
            "total_receipts": 1,
            "latest_observed_at": latest_observed_at.isoformat().replace(
                "+00:00", "Z"
            ),
        },
        "workspaces_total": 1,
        "latest_rollout_state": receipt["deployment_state"],
        "trust_posture_counts": trust_posture_counts,
        "drift_count": int(
            codex_plane_drift_present(trust, regeneration, receipt)
        ),
        "rollback_recommended_count": int(
            codex_plane_rollback_recommended(trust, regeneration, receipt)
        ),
        "stable_mcp_name_set": stable_mcp_names,
        "latest_receipt_ref": str(receipt["rollout_receipt_id"]),
    }
