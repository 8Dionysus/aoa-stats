from __future__ import annotations

from collections.abc import Mapping
import math
from typing import Any


INFERENCE_ECONOMY_OBSERVATION_SCHEMA = (
    "aoa_stats_inference_economy_observation_v1"
)
COUNT_METRIC_PATHS = (
    "tokens.input",
    "tokens.cached_input",
    "tokens.output",
    "activity.turns",
    "activity.model_calls",
    "activity.intermediate_volume.items",
    "activity.intermediate_volume.bytes",
    "activity.intermediate_volume.tokens",
    "activity.compactions",
    "activity.losses",
    "activity.retries",
    "activity.rework",
    "tools.schema_bytes",
    "tools.schema_tokens",
    "tools.calls",
)
DURATION_METRIC_PATHS = ("wall_time_seconds",)
METRIC_PATHS = COUNT_METRIC_PATHS + DURATION_METRIC_PATHS
LIFECYCLE_PATHS = (
    "runtime_outcome",
    "eval_verdict",
    "closeout",
    "owner_acceptance",
)
METRIC_STATUSES = frozenset({"observed", "missing", "unknown", "stale"})
METRIC_BASES = frozenset(
    {
        "provider_reported",
        "exact_tokenizer",
        "estimated",
        "unknown",
        "not_applicable",
    }
)
METRIC_UNCERTAINTIES = frozenset(
    {"exact", "estimated", "not_estimated", "not_applicable"}
)
AUTHORITY_CEILING = (
    "Descriptive provider-neutral execution-economy observations only; they do not "
    "authorize activation, promotion, proof, policy, routing, or owner acceptance."
)


def _path_value(payload: Mapping[str, Any], path: str) -> Any:
    current: Any = payload
    for part in path.split("."):
        if not isinstance(current, Mapping):
            return None
        current = current.get(part)
    return current


def _portable_ref(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    lowered = value.lower()
    return not (
        value.startswith(("/", "~"))
        or "/home/" in lowered
        or "/srv/" in lowered
        or ".aoa/sessions" in lowered
        or "transcript" in lowered
    )


def _validate_evidence_refs(
    value: Any, *, label: str, issues: list[str]
) -> None:
    if not isinstance(value, list):
        return
    for index, entry in enumerate(value):
        if not isinstance(entry, Mapping):
            continue
        ref = entry.get("ref")
        if isinstance(ref, str) and not _portable_ref(ref):
            issues.append(f"{label}[{index}] must remain a portable evidence ref")


def _validate_metric(
    metric: Any,
    *,
    path: str,
    integer: bool,
    issues: list[str],
) -> None:
    if not isinstance(metric, Mapping):
        issues.append(f"{path} must be a metric object")
        return
    status = metric.get("status")
    basis = metric.get("basis")
    uncertainty = metric.get("uncertainty")
    value = metric.get("value")
    evidence_refs = metric.get("evidence_refs")
    reason = metric.get("reason")
    if status not in METRIC_STATUSES:
        issues.append(f"{path}.status is not a supported observation status")
    if basis not in METRIC_BASES:
        issues.append(f"{path}.basis is not a supported count basis")
    if uncertainty not in METRIC_UNCERTAINTIES:
        issues.append(f"{path}.uncertainty is not a supported uncertainty state")
    _validate_evidence_refs(evidence_refs, label=f"{path}.evidence_refs", issues=issues)

    if status == "observed":
        if basis in {"unknown", "not_applicable"}:
            issues.append(f"{path}.basis cannot be {basis!r} for an observed value")
        if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
            issues.append(f"{path}.value must be numeric when observed")
        elif not math.isfinite(float(value)) or value < 0:
            issues.append(f"{path}.value must be finite and non-negative when observed")
        elif integer and not isinstance(value, int):
            issues.append(f"{path}.value must be an integer when observed")
        if not isinstance(evidence_refs, list) or not evidence_refs:
            issues.append(f"{path}.evidence_refs must be non-empty when observed")
    else:
        if value is not None:
            issues.append(f"{path}.value must remain null when {status}")
        if not isinstance(reason, str) or not reason:
            issues.append(f"{path}.reason must explain a non-observed metric")


def _validate_lifecycle_observation(
    value: Any, *, path: str, value_field: str, issues: list[str]
) -> None:
    if not isinstance(value, Mapping):
        issues.append(f"{path} must be an observation object")
        return
    status = value.get("observation_status")
    evidence_refs = value.get("evidence_refs")
    observed_value = value.get(value_field)
    _validate_evidence_refs(evidence_refs, label=f"{path}.evidence_refs", issues=issues)
    if status not in METRIC_STATUSES:
        issues.append(f"{path}.observation_status is not supported")
    if status == "observed":
        if observed_value is None:
            issues.append(f"{path}.{value_field} is required when observed")
        if not isinstance(evidence_refs, list) or not evidence_refs:
            issues.append(f"{path}.evidence_refs must be non-empty when observed")
    else:
        if observed_value is not None:
            issues.append(f"{path}.{value_field} must remain null when {status}")
        reason = value.get("reason")
        if not isinstance(reason, str) or not reason:
            issues.append(f"{path}.reason must explain a non-observed lifecycle field")


def _expected_unknown_fields(observation: Mapping[str, Any]) -> list[str]:
    unresolved: list[str] = []
    for path in METRIC_PATHS:
        metric = _path_value(observation, path)
        if not isinstance(metric, Mapping) or metric.get("status") != "observed":
            unresolved.append(path)
    for path in LIFECYCLE_PATHS:
        lifecycle = observation.get(path)
        if (
            not isinstance(lifecycle, Mapping)
            or lifecycle.get("observation_status") != "observed"
        ):
            unresolved.append(path)
    return sorted(unresolved)


def validate_inference_economy_observation(
    observation: Mapping[str, Any],
) -> list[str]:
    """Validate cross-field semantics for one opt-in economy observation."""

    issues: list[str] = []
    if not isinstance(observation, Mapping):
        return ["observation must be an object"]
    if observation.get("schema_version") != INFERENCE_ECONOMY_OBSERVATION_SCHEMA:
        issues.append(
            "schema_version does not identify the inference economy observation"
        )
    if observation.get("authority_ceiling") != AUTHORITY_CEILING:
        issues.append("authority_ceiling must preserve the descriptive-only boundary")

    for path in COUNT_METRIC_PATHS:
        _validate_metric(
            _path_value(observation, path), path=path, integer=True, issues=issues
        )
    for path in DURATION_METRIC_PATHS:
        _validate_metric(
            _path_value(observation, path), path=path, integer=False, issues=issues
        )

    _validate_lifecycle_observation(
        observation.get("runtime_outcome"),
        path="runtime_outcome",
        value_field="outcome",
        issues=issues,
    )
    _validate_lifecycle_observation(
        observation.get("eval_verdict"),
        path="eval_verdict",
        value_field="verdict",
        issues=issues,
    )
    _validate_lifecycle_observation(
        observation.get("closeout"),
        path="closeout",
        value_field="state",
        issues=issues,
    )
    _validate_lifecycle_observation(
        observation.get("owner_acceptance"),
        path="owner_acceptance",
        value_field="state",
        issues=issues,
    )

    runtime_outcome = observation.get("runtime_outcome")
    if (
        isinstance(runtime_outcome, Mapping)
        and runtime_outcome.get("observation_status") == "observed"
        and observation.get("runtime_ref") is None
    ):
        issues.append("runtime_ref is required when runtime_outcome is observed")

    provenance = observation.get("provenance")
    if isinstance(provenance, Mapping):
        _validate_evidence_refs(
            provenance.get("evidence_refs"),
            label="provenance.evidence_refs",
            issues=issues,
        )
    progress = observation.get("progress")
    if isinstance(progress, Mapping):
        completed = progress.get("completed")
        total = progress.get("total")
        if isinstance(completed, int) and not isinstance(completed, bool):
            if isinstance(total, int) and not isinstance(total, bool) and completed > total:
                issues.append("progress.completed cannot exceed progress.total")
            if progress.get("state") == "terminal" and total is None:
                issues.append("terminal progress requires a known total")
            if (
                progress.get("state") == "terminal"
                and isinstance(total, int)
                and completed != total
            ):
                issues.append("terminal progress requires completed to equal total")

    expected_unknown = _expected_unknown_fields(observation)
    actual_unknown = observation.get("unknown_fields")
    if not isinstance(actual_unknown, list) or sorted(actual_unknown) != expected_unknown:
        issues.append(
            "unknown_fields must exactly list unresolved metric and lifecycle fields"
        )

    overall_status = observation.get("observation_status")
    if overall_status == "complete":
        if expected_unknown:
            issues.append("complete observation cannot contain unresolved fields")
        if not isinstance(progress, Mapping) or progress.get("state") != "terminal":
            issues.append("complete observation requires terminal progress")
    elif overall_status == "partial":
        if not expected_unknown and not (
            isinstance(progress, Mapping) and progress.get("state") == "partial"
        ):
            issues.append(
                "partial observation requires an unresolved field or partial progress"
            )
    elif overall_status in {"missing", "unknown", "stale"} and not expected_unknown:
        issues.append(f"{overall_status} observation must identify an unresolved field")

    return issues
