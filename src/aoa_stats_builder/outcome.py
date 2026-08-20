from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime
import hashlib
import json
from math import isfinite
from typing import Any


ACTIONABLE_STATES = frozenset({"selected", "attempted", "completed", "failed"})
EXECUTED_STATES = frozenset({"attempted", "completed", "failed"})
NONFINAL_TERMINAL_STATES = frozenset({"pending", "missed"})
ZERO_DIGEST = "sha256:" + ("0" * 64)


def normalized_outcome_receipt_digest(receipt: Mapping[str, Any]) -> str:
    """Hash a C10 receipt with its self-digest replaced by the v1 zero token."""

    normalized = dict(receipt)
    normalized["content_digest"] = ZERO_DIGEST
    encoded = json.dumps(
        normalized,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _aware_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def _portable_ref(value: object) -> bool:
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


def _iter_mappings(value: object) -> Iterable[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        yield value
        for child in value.values():
            yield from _iter_mappings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_mappings(child)


def _provenance_key(value: object) -> tuple[object, ...] | None:
    if not isinstance(value, Mapping):
        return None
    required = ("owner_repo", "artifact_ref", "artifact_version", "artifact_digest")
    if not all(field in value for field in required):
        return None
    return tuple(value[field] for field in required)


def _validate_unique_refs(
    values: object,
    *,
    label: str,
    issues: list[str],
) -> None:
    if not isinstance(values, list):
        return
    keys = [key for value in values if (key := _provenance_key(value)) is not None]
    if len(keys) != len(set(keys)):
        issues.append(f"{label} must contain unique provenance refs")


def _validate_action_snapshot(
    snapshot: object,
    *,
    expected_phase: str,
    issues: list[str],
) -> None:
    if not isinstance(snapshot, Mapping):
        return
    if snapshot.get("phase") != expected_phase:
        issues.append(f"{expected_phase} snapshot must carry phase {expected_phase!r}")
    state = snapshot.get("decision_state")
    completeness = snapshot.get("completeness")
    if state in ACTIONABLE_STATES:
        required = (
            "action_class",
            "target_ref",
            "operation_id",
            "parameters_digest",
            "source_snapshot_ref",
        )
        missing = [field for field in required if snapshot.get(field) is None]
        if missing:
            issues.append(
                f"{expected_phase} actionable snapshot lacks {', '.join(missing)}"
            )
        if completeness != "complete":
            issues.append(f"{expected_phase} actionable snapshot must be complete")
    if state in EXECUTED_STATES:
        missing = [
            field
            for field in ("approval_ref", "rollback_ref")
            if snapshot.get(field) is None
        ]
        if missing:
            issues.append(
                f"{expected_phase} executed snapshot lacks {', '.join(missing)}"
            )
    if state in {"no_action", "unknown"}:
        action_fields = (
            "action_class",
            "target_ref",
            "operation_id",
            "parameters_digest",
            "source_snapshot_ref",
            "approval_ref",
            "rollback_ref",
        )
        if any(snapshot.get(field) is not None for field in action_fields):
            issues.append(
                f"{expected_phase} {state} snapshot must not carry action binding fields"
            )


def _validate_outcome(
    outcome: object,
    *,
    expected_kind: str,
    issues: list[str],
) -> None:
    if not isinstance(outcome, Mapping):
        return
    if outcome.get("kind") != expected_kind:
        issues.append(f"{expected_kind} outcome must carry kind {expected_kind!r}")
    state = outcome.get("state")
    observed_at = outcome.get("observed_at")
    fact_ref = outcome.get("owner_fact_ref")
    if state in {"success", "failure", "partial", "no_effect", "harm"}:
        if observed_at is None or fact_ref is None:
            issues.append(
                f"{expected_kind} observed outcome requires observed_at and owner_fact_ref"
            )
    if state in {"pending", "unknown"} and observed_at is not None:
        issues.append(f"{expected_kind} {state} outcome cannot claim observed_at")
    if state == "pending" and outcome.get("expected_at") is None:
        issues.append(f"{expected_kind} pending outcome requires expected_at")
    _validate_unique_refs(
        outcome.get("quality_measurement_refs"),
        label=f"{expected_kind}.quality_measurement_refs",
        issues=issues,
    )


def _validate_costs(costs: object, issues: list[str]) -> None:
    if not isinstance(costs, list):
        return
    ids: list[object] = []
    for index, cost in enumerate(costs):
        if not isinstance(cost, Mapping):
            continue
        ids.append(cost.get("measurement_id"))
        status = cost.get("status")
        number = cost.get("number")
        packet_ref = cost.get("measurement_packet_ref")
        if status == "observed":
            if (
                not isinstance(number, (int, float))
                or isinstance(number, bool)
                or not isfinite(float(number))
                or float(number) < 0
                or packet_ref is None
                or cost.get("sample_size") == 0
            ):
                issues.append(
                    f"cost_observations[{index}] observed cost requires a "
                    "non-negative finite number, non-zero sample, and packet ref"
                )
        elif number is not None:
            issues.append(
                f"cost_observations[{index}] non-observed cost must not carry number"
            )
    if len(ids) != len(set(ids)):
        issues.append("cost_observations measurement_id values must be unique")


def validate_outcome_receipt_semantics(receipt: Mapping[str, Any]) -> list[str]:
    """Validate C10 rules that JSON Schema intentionally leaves cross-field."""

    issues: list[str] = []

    for mapping in _iter_mappings(receipt):
        artifact_ref = mapping.get("artifact_ref")
        if artifact_ref is not None and not _portable_ref(artifact_ref):
            issues.append(f"non-portable artifact_ref: {artifact_ref!r}")
        decision_ref = mapping.get("decision_ref")
        if decision_ref is not None and not _portable_ref(decision_ref):
            issues.append(f"non-portable decision_ref: {decision_ref!r}")

    for mapping in _iter_mappings(receipt):
        for field, value in mapping.items():
            if value is None:
                continue
            if field.endswith("_at") or field in {"produced_at", "retention_until"}:
                if _aware_datetime(value) is None:
                    issues.append(f"{field} must be a timezone-aware date-time")

    produced_at = _aware_datetime(receipt.get("produced_at"))
    retention_until = _aware_datetime(receipt.get("retention_until"))
    if (
        produced_at is not None
        and retention_until is not None
        and retention_until <= produced_at
    ):
        issues.append("retention_until must follow produced_at")

    before = receipt.get("action_before_memory")
    after = receipt.get("action_after_memory")
    _validate_action_snapshot(before, expected_phase="before_memory", issues=issues)
    _validate_action_snapshot(after, expected_phase="after_memory", issues=issues)

    if isinstance(before, Mapping) and isinstance(after, Mapping):
        before_at = _aware_datetime(before.get("observed_at"))
        after_at = _aware_datetime(after.get("observed_at"))
        if before_at is not None and after_at is not None and after_at < before_at:
            issues.append("action_after_memory cannot precede action_before_memory")

    memory_used = receipt.get("memory_used")
    recall_packet_refs = receipt.get("recall_packet_refs")
    recall_count = len(recall_packet_refs) if isinstance(recall_packet_refs, list) else 0
    intervention_ref = receipt.get("intervention_decision_ref")
    attribution = receipt.get("attribution")
    attribution_status = (
        attribution.get("status") if isinstance(attribution, Mapping) else None
    )
    confidence = (
        attribution.get("confidence") if isinstance(attribution, Mapping) else None
    )
    if memory_used is True and recall_count == 0:
        issues.append("memory_used true requires at least one recall_packet_ref")
    if memory_used is False:
        if recall_count or intervention_ref is not None:
            issues.append(
                "memory_used false forbids recall packet and intervention decision refs"
            )
        if attribution_status in {"possible", "supported"}:
            issues.append("memory_used false forbids positive memory attribution")
    if memory_used == "unknown" and (
        attribution_status not in {"unknown", "not_evaluated"}
        or confidence not in {"unknown", "none"}
    ):
        issues.append("memory_used unknown requires unknown or unevaluated attribution")

    assignment = receipt.get("experiment_assignment")
    if isinstance(assignment, Mapping):
        design = assignment.get("design")
        arm_id = assignment.get("arm_id")
        assignment_digest = assignment.get("assignment_digest")
        holdout = assignment.get("holdout")
        shadow_ref = assignment.get("always_shadow_counterfactual_ref")
        manifest_ref = receipt.get("experiment_manifest_ref")
        if design == "randomized_holdout" and (
            manifest_ref is None
            or arm_id is None
            or assignment_digest is None
            or shadow_ref is None
        ):
            issues.append(
                "randomized holdout requires manifest, arm, assignment, "
                "and always-shadow counterfactual refs"
            )
        if design == "not_assigned" and (
            arm_id is not None
            or assignment_digest is not None
            or holdout != "unknown"
            or shadow_ref is not None
            or manifest_ref is not None
        ):
            issues.append(
                "not-assigned experiment posture must not claim assignment evidence"
            )
        if holdout is True and memory_used is not False:
            issues.append("randomized holdout arm must keep memory_used false")

    after_state = after.get("decision_state") if isinstance(after, Mapping) else None
    if after_state in ACTIONABLE_STATES and receipt.get("exact_effect_binding_ref") is None:
        issues.append("actionable after-memory state requires exact_effect_binding_ref")
    effect_binding = receipt.get("exact_effect_binding_ref")
    after_target = after.get("target_ref") if isinstance(after, Mapping) else None
    if (
        isinstance(effect_binding, Mapping)
        and isinstance(after_target, Mapping)
        and effect_binding.get("owner_repo") != after_target.get("owner_repo")
    ):
        issues.append("exact effect binding owner must match after-memory target owner")

    terminal = receipt.get("terminal_outcome")
    _validate_outcome(terminal, expected_kind="terminal", issues=issues)
    if isinstance(terminal, Mapping) and terminal.get("state") in NONFINAL_TERMINAL_STATES:
        issues.append("terminal_outcome cannot use pending or missed state")
    terminal_fact_ref = (
        terminal.get("owner_fact_ref") if isinstance(terminal, Mapping) else None
    )
    if (
        isinstance(terminal_fact_ref, Mapping)
        and terminal_fact_ref.get("owner_repo") != receipt.get("fact_owner")
    ):
        issues.append("terminal owner_fact_ref owner must match fact_owner")

    delayed = receipt.get("delayed_outcomes")
    delayed_items = delayed if isinstance(delayed, list) else []
    for item in delayed_items:
        _validate_outcome(item, expected_kind="delayed", issues=issues)
    delayed_posture = receipt.get("delayed_outcome_posture")
    delayed_states = {
        item.get("state") for item in delayed_items if isinstance(item, Mapping)
    }
    if delayed_posture == "none_expected" and delayed_items:
        issues.append("none_expected delayed posture requires an empty delayed_outcomes")
    elif delayed_posture == "pending" and "pending" not in delayed_states:
        issues.append("pending delayed posture requires a pending delayed outcome")
    elif delayed_posture == "observed" and not delayed_states.intersection(
        {"success", "failure", "partial", "no_effect", "harm"}
    ):
        issues.append("observed delayed posture requires an observed delayed outcome")
    elif delayed_posture == "overdue" and "missed" not in delayed_states:
        issues.append("overdue delayed posture requires a missed delayed outcome")
    if delayed_posture in {"pending", "overdue"} and receipt.get(
        "validation_status"
    ) == "valid":
        issues.append("pending or overdue delayed outcome requires partial validation")

    confounders = receipt.get("confounders")
    if isinstance(confounders, list):
        confounder_ids = [
            item.get("confounder_id")
            for item in confounders
            if isinstance(item, Mapping)
        ]
        if len(confounder_ids) != len(set(confounder_ids)):
            issues.append("confounder_id values must be unique")

    accidental = receipt.get("accidental_success")
    if isinstance(accidental, Mapping) and accidental.get("value") is True:
        evidence_refs = accidental.get("evidence_refs")
        terminal_state = terminal.get("state") if isinstance(terminal, Mapping) else None
        if terminal_state != "success":
            issues.append("accidental_success true requires terminal success")
        if not isinstance(evidence_refs, list) or not evidence_refs:
            issues.append("accidental_success true requires evidence_refs")
        if not isinstance(confounders, list) or not confounders:
            issues.append("accidental_success true requires at least one confounder")
        if attribution_status == "supported" or confidence in {"medium", "high"}:
            issues.append(
                "accidental success forbids supported, medium, or high attribution"
            )

    harm = receipt.get("harm")
    if isinstance(harm, Mapping):
        observed = harm.get("observed")
        severity = harm.get("severity")
        harm_refs = harm.get("harm_refs")
        stop_triggered = harm.get("immediate_stop_triggered")
        if observed is True and (
            severity not in {"low", "medium", "high", "critical"}
            or not isinstance(harm_refs, list)
            or not harm_refs
        ):
            issues.append("observed harm requires severity and harm_refs")
        if observed is False and (severity != "none" or harm_refs):
            issues.append("harm observed false requires severity none and no harm_refs")
        if observed == "unknown" and severity != "unknown":
            issues.append("unknown harm requires unknown severity")
        if severity in {"high", "critical"} and stop_triggered is False:
            issues.append("high or critical harm cannot report immediate stop false")

    _validate_costs(receipt.get("cost_observations"), issues)

    evaluator = receipt.get("evaluator")
    if isinstance(evaluator, Mapping):
        evaluator_role = evaluator.get("role")
        evaluator_ref = evaluator.get("evidence_ref")
        if evaluator_role in {"independent_judge", "same_model_declared"}:
            if evaluator_ref is None:
                issues.append("evaluated receipt requires evaluator evidence_ref")
        elif evaluator_role == "not_evaluated" and evaluator_ref is not None:
            issues.append("not-evaluated receipt cannot carry evaluator evidence")

    operator = receipt.get("operator_intervention")
    if isinstance(operator, Mapping):
        occurred = operator.get("occurred")
        intervention_class = operator.get("intervention_class")
        evidence_refs = operator.get("evidence_refs")
        time_ref = operator.get("time_measurement_ref")
        if occurred is False and (
            intervention_class != "none" or evidence_refs or time_ref is not None
        ):
            issues.append(
                "no operator intervention requires class none and no evidence"
            )
        if occurred is True and (
            intervention_class in {"none", "unknown"}
            or not isinstance(evidence_refs, list)
            or not evidence_refs
        ):
            issues.append(
                "operator intervention requires a concrete class and evidence"
            )
        if occurred == "unknown" and intervention_class != "unknown":
            issues.append("unknown operator intervention requires unknown class")

    evaluation = receipt.get("evaluation_posture")
    eval_plane_status = (
        evaluation.get("eval_plane_status")
        if isinstance(evaluation, Mapping)
        else None
    )
    if isinstance(evaluation, Mapping):
        policy_update_state = evaluation.get("policy_update_state")
        if (
            eval_plane_status in {"degraded", "unavailable"}
            and policy_update_state != "frozen"
        ):
            issues.append("unavailable or degraded eval plane must freeze policy")
        if eval_plane_status != "available" and attribution_status in {
            "possible",
            "supported",
        }:
            issues.append(
                "unavailable or degraded eval plane forbids positive attribution"
            )

    if isinstance(attribution, Mapping):
        eval_ref = attribution.get("eval_verdict_ref")
        counterfactual_ref = attribution.get("counterfactual_ref")
        basis = attribution.get("basis")
        if attribution_status == "not_evaluated" and (
            confidence not in {"none", "unknown"}
            or eval_ref is not None
            or counterfactual_ref is not None
        ):
            issues.append("not_evaluated attribution cannot carry proof or confidence")
        if attribution_status == "unknown" and confidence not in {"unknown", "none"}:
            issues.append("unknown attribution requires unknown or no confidence")
        if attribution_status == "supported" and (
            memory_used is not True
            or (eval_ref is None and counterfactual_ref is None)
            or not isinstance(before, Mapping)
            or before.get("completeness") != "complete"
            or not isinstance(after, Mapping)
            or after.get("completeness") != "complete"
            or not isinstance(terminal, Mapping)
            or terminal.get("task_owner_acceptance") is not True
            or eval_plane_status != "available"
            or not isinstance(evaluator, Mapping)
            or evaluator.get("role") != "independent_judge"
            or not isinstance(evaluation, Mapping)
            or evaluation.get("independent_judge_ref") is None
            or evaluation.get("reward_hacking_check_ref") is None
            or evaluation.get("fairness_tenant_skew_ref") is None
            or evaluation.get("model_version_stratum_ref") is None
            or not receipt.get("host_observation_refs")
        ):
            issues.append(
                "supported attribution requires used memory, complete snapshots, "
                "task-owner acceptance, host evidence, independent evaluation, "
                "integrity checks, and eval or counterfactual evidence"
            )
        if confidence == "high" and (
            attribution_status != "supported"
            or eval_ref is None
            or counterfactual_ref is None
            or basis not in {"paired_evidence", "randomized_evidence"}
        ):
            issues.append(
                "high confidence requires supported paired or randomized evidence"
            )

    _validate_unique_refs(
        recall_packet_refs,
        label="recall_packet_refs",
        issues=issues,
    )
    _validate_unique_refs(
        receipt.get("source_refs"),
        label="source_refs",
        issues=issues,
    )
    source_refs = receipt.get("source_refs")
    source_keys = {
        key
        for value in source_refs
        if (key := _provenance_key(value)) is not None
    } if isinstance(source_refs, list) else set()
    terminal_fact_key = _provenance_key(terminal_fact_ref)
    if terminal_fact_key is not None and terminal_fact_key not in source_keys:
        issues.append("terminal owner_fact_ref must be retained in source_refs")
    task_ref = receipt.get("task_ref")
    task_key = _provenance_key(task_ref)
    if (
        isinstance(task_ref, Mapping)
        and task_ref.get("owner_repo") != receipt.get("fact_owner")
    ):
        issues.append("task_ref owner must match fact_owner")
    if task_key is not None and task_key not in source_keys:
        issues.append("task_ref must be retained in source_refs")
    _validate_unique_refs(
        receipt.get("host_observation_refs"),
        label="host_observation_refs",
        issues=issues,
    )
    expected_digest = normalized_outcome_receipt_digest(receipt)
    if receipt.get("content_digest") != expected_digest:
        issues.append(
            "content_digest must match normalized outcome receipt digest"
        )

    return issues
