from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from .read_model_values import (
    is_nonempty_string,
    parse_iso_datetime,
    parse_iso_datetime_or_min,
    string_count_map,
)
from .receipt_abi import ReceiptValidationError


COMPONENT_REFRESH_ROUTE_CLASSES = (
    "observe",
    "revalidate",
    "rebuild",
    "reexport",
    "regenerate",
    "reproject",
    "repair",
    "defer",
)
COMPONENT_REFRESH_DECISION_STATUSES = (
    "chosen",
    "deferred",
    "safe_stop",
    "unreviewed",
)
COMPONENT_REFRESH_CURRENT_STATUSES = (
    "refresh_recommended",
    "refresh_active",
    "current",
    "deferred",
    "recovered",
)
COMPONENT_REFRESH_SIGNAL_DRIFT_CLASSES = {
    "doctor_fail_after_render": "doctor_drift",
    "same_hand_patch_repeated": "manual_repeat",
    "skill_source_changed_without_export_refresh": "export_drift",
    "skill_validation_failed": "validation_drift",
    "profile_changed_without_projection_refresh": "projection_drift",
    "latest_observed_at_stale": "staleness_window",
    "summary_family_out_of_sync": "family_drift",
}
COMPONENT_REFRESH_COMPONENT_DRIFT_CLASSES = {
    "component:codex-plane:shared-root": ("root_drift",),
}


def _normalize_string_sequence(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if is_nonempty_string(item)]


def validate_reviewed_component_refresh_sets(
    hint_set: Mapping[str, Any],
    decision_set: Mapping[str, Any],
) -> tuple[tuple[Mapping[str, Any], ...], tuple[Mapping[str, Any], ...], datetime]:
    if hint_set.get("schema_version") != "aoa_component_drift_hint_set_v1":
        raise ReceiptValidationError(
            "component drift hint example must keep schema_version "
            "aoa_component_drift_hint_set_v1"
        )
    if (
        decision_set.get("schema_version")
        != "aoa_component_refresh_followthrough_decision_set_v1"
    ):
        raise ReceiptValidationError(
            "component refresh followthrough decision example must keep schema_version "
            "aoa_component_refresh_followthrough_decision_set_v1"
        )
    if decision_set.get("reviewed") is not True:
        raise ReceiptValidationError(
            "component refresh followthrough decision example must stay reviewed "
            "before stats summarize it"
        )

    raw_hints = hint_set.get("hints")
    if not isinstance(raw_hints, list) or not raw_hints:
        raise ReceiptValidationError(
            "component drift hint example must expose a non-empty hints list"
        )
    raw_decisions = decision_set.get("decisions")
    if not isinstance(raw_decisions, list) or not raw_decisions:
        raise ReceiptValidationError(
            "component refresh followthrough decision example must expose a "
            "non-empty decisions list"
        )

    hints: list[Mapping[str, Any]] = []
    latest_hint_observed_at: datetime | None = None
    hint_refs: set[str] = set()
    hint_components: set[str] = set()
    hints_by_ref: dict[str, Mapping[str, Any]] = {}
    hints_by_component: dict[str, Mapping[str, Any]] = {}
    for index, hint in enumerate(raw_hints):
        if not isinstance(hint, Mapping):
            raise ReceiptValidationError(
                f"component drift hint example hints[{index}] must be an object"
            )
        hint_ref = hint.get("hint_ref")
        component_ref = hint.get("component_ref")
        owner_repo = hint.get("owner_repo")
        observed_at = hint.get("observed_at")
        route_class = hint.get("recommended_route_class")
        signals = _normalize_string_sequence(hint.get("signals"))
        evidence_refs = _normalize_string_sequence(hint.get("evidence_refs"))
        if not is_nonempty_string(hint_ref):
            raise ReceiptValidationError(
                f"component drift hint example hints[{index}] must expose hint_ref"
            )
        if not is_nonempty_string(component_ref):
            raise ReceiptValidationError(
                f"component drift hint example hints[{index}] must expose component_ref"
            )
        if not is_nonempty_string(owner_repo):
            raise ReceiptValidationError(
                f"component drift hint example hints[{index}] must expose owner_repo"
            )
        if str(hint_ref) in hint_refs:
            raise ReceiptValidationError(
                f"component drift hint example hints[{index}] must not duplicate "
                f"hint_ref {hint_ref!r}"
            )
        if str(component_ref) in hint_components:
            raise ReceiptValidationError(
                f"component drift hint example hints[{index}] must not duplicate "
                f"component_ref {component_ref!r}"
            )
        parsed_observed_at = parse_iso_datetime(observed_at)
        if parsed_observed_at is None:
            raise ReceiptValidationError(
                f"component drift hint example hints[{index}] must expose "
                "observed_at as date-time"
            )
        if route_class not in COMPONENT_REFRESH_ROUTE_CLASSES:
            raise ReceiptValidationError(
                f"component drift hint example hints[{index}] "
                "recommended_route_class is outside the published grammar"
            )
        if not signals:
            raise ReceiptValidationError(
                f"component drift hint example hints[{index}] must expose at least "
                "one signal"
            )
        if not evidence_refs:
            raise ReceiptValidationError(
                f"component drift hint example hints[{index}] must expose at least "
                "one evidence_ref"
            )
        hint_refs.add(str(hint_ref))
        hint_components.add(str(component_ref))
        hints_by_ref[str(hint_ref)] = hint
        hints_by_component[str(component_ref)] = hint
        hints.append(hint)
        if (
            latest_hint_observed_at is None
            or parsed_observed_at > latest_hint_observed_at
        ):
            latest_hint_observed_at = parsed_observed_at

    decisions: list[Mapping[str, Any]] = []
    decision_components: set[str] = set()
    for index, decision in enumerate(raw_decisions):
        if not isinstance(decision, Mapping):
            raise ReceiptValidationError(
                "component refresh followthrough decision example "
                f"decisions[{index}] must be an object"
            )
        component_ref = decision.get("component_ref")
        owner_repo = decision.get("owner_repo")
        route_class = decision.get("route_class")
        decision_status = decision.get("decision_status")
        evidence_refs = _normalize_string_sequence(decision.get("evidence_refs"))
        if not is_nonempty_string(component_ref):
            raise ReceiptValidationError(
                "component refresh followthrough decision example "
                f"decisions[{index}] must expose component_ref"
            )
        if not is_nonempty_string(owner_repo):
            raise ReceiptValidationError(
                "component refresh followthrough decision example "
                f"decisions[{index}] must expose owner_repo"
            )
        if route_class not in COMPONENT_REFRESH_ROUTE_CLASSES:
            raise ReceiptValidationError(
                "component refresh followthrough decision example "
                f"decisions[{index}] route_class is outside the published grammar"
            )
        if decision_status not in COMPONENT_REFRESH_DECISION_STATUSES[:-1]:
            raise ReceiptValidationError(
                "component refresh followthrough decision example "
                f"decisions[{index}] decision_status is outside the published grammar"
            )
        if str(component_ref) in decision_components:
            raise ReceiptValidationError(
                "component refresh followthrough decision example "
                f"decisions[{index}] must not duplicate component_ref "
                f"{component_ref!r}"
            )
        if not evidence_refs:
            raise ReceiptValidationError(
                "component refresh followthrough decision example "
                f"decisions[{index}] must expose at least one evidence_ref"
            )
        component_key = str(component_ref)
        owner_key = str(owner_repo)
        for evidence_ref in evidence_refs:
            referenced_hint = hints_by_ref.get(evidence_ref)
            if referenced_hint is None:
                if evidence_ref.startswith("hint:"):
                    raise ReceiptValidationError(
                        "component refresh followthrough decision example "
                        f"decisions[{index}] cites unknown hint_ref {evidence_ref!r}"
                    )
                continue
            if referenced_hint.get("component_ref") != component_key:
                raise ReceiptValidationError(
                    "component refresh followthrough decision example "
                    f"decisions[{index}] component_ref must match cited hint "
                    f"{evidence_ref!r}"
                )
            if referenced_hint.get("owner_repo") != owner_key:
                raise ReceiptValidationError(
                    "component refresh followthrough decision example "
                    f"decisions[{index}] owner_repo must match cited hint "
                    f"{evidence_ref!r}"
                )

        matching_hint = hints_by_component.get(component_key)
        if matching_hint is not None:
            matching_hint_ref = str(matching_hint["hint_ref"])
            if matching_hint_ref not in evidence_refs:
                raise ReceiptValidationError(
                    "component refresh followthrough decision example "
                    f"decisions[{index}] must cite matching hint_ref "
                    f"{matching_hint_ref!r}"
                )
        decision_components.add(str(component_ref))
        decisions.append(decision)

    assert latest_hint_observed_at is not None
    return tuple(hints), tuple(decisions), latest_hint_observed_at


def component_refresh_status(
    decision: Mapping[str, Any] | None, *, owner_repo: str
) -> str:
    if not isinstance(decision, Mapping):
        return "refresh_recommended"
    decision_status = str(decision.get("decision_status") or "unreviewed")
    if decision_status == "deferred":
        return "deferred"
    if decision_status == "safe_stop":
        return "current"
    if decision_status != "chosen":
        return "refresh_recommended"
    if owner_repo == "aoa-stats":
        return "refresh_recommended"
    return "refresh_active"


def component_refresh_route_class(
    hint: Mapping[str, Any] | None, decision: Mapping[str, Any] | None
) -> str:
    if isinstance(decision, Mapping):
        route_class = decision.get("route_class")
        if route_class in COMPONENT_REFRESH_ROUTE_CLASSES:
            return str(route_class)
    if isinstance(hint, Mapping):
        route_class = hint.get("recommended_route_class")
        if route_class in COMPONENT_REFRESH_ROUTE_CLASSES:
            return str(route_class)
    return "observe"


def component_refresh_drift_classes(
    component_ref: str, signals: Sequence[str]
) -> list[str]:
    classes = list(COMPONENT_REFRESH_COMPONENT_DRIFT_CLASSES.get(component_ref, ()))
    for signal in signals:
        drift_class = COMPONENT_REFRESH_SIGNAL_DRIFT_CLASSES.get(signal)
        if drift_class is not None:
            classes.append(drift_class)
    return classes


def latest_component_hints_by_component(
    hints: Sequence[Mapping[str, Any]],
) -> dict[str, Mapping[str, Any]]:
    latest_by_component: dict[str, Mapping[str, Any]] = {}
    for hint in hints:
        if not isinstance(hint, Mapping):
            continue
        component_ref = hint.get("component_ref")
        if not is_nonempty_string(component_ref):
            continue
        previous = latest_by_component.get(str(component_ref))
        if previous is None or parse_iso_datetime_or_min(
            hint.get("observed_at")
        ) >= parse_iso_datetime_or_min(previous.get("observed_at")):
            latest_by_component[str(component_ref)] = hint
    return latest_by_component


def build_component_refresh_summary(
    source: Mapping[str, Any],
    hints: Sequence[Mapping[str, Any]],
    decisions: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    hints_by_component = latest_component_hints_by_component(hints)
    decisions_by_component = {
        str(decision["component_ref"]): decision
        for decision in decisions
        if isinstance(decision, Mapping)
    }

    component_order: list[str] = []
    seen: set[str] = set()
    for payload in (*hints, *decisions):
        if not isinstance(payload, Mapping):
            continue
        component_ref = payload.get("component_ref")
        if not is_nonempty_string(component_ref) or component_ref in seen:
            continue
        seen.add(str(component_ref))
        component_order.append(str(component_ref))

    owner_repo_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter(
        {status: 0 for status in COMPONENT_REFRESH_CURRENT_STATUSES}
    )
    drift_class_counts: Counter[str] = Counter()
    components: list[dict[str, Any]] = []

    for component_ref in component_order:
        hint = hints_by_component.get(component_ref)
        decision = decisions_by_component.get(component_ref)
        owner_repo = ""
        if isinstance(decision, Mapping) and is_nonempty_string(
            decision.get("owner_repo")
        ):
            owner_repo = str(decision.get("owner_repo"))
        elif isinstance(hint, Mapping) and is_nonempty_string(hint.get("owner_repo")):
            owner_repo = str(hint.get("owner_repo"))
        if not owner_repo:
            raise ReceiptValidationError(
                "component refresh summary could not resolve owner_repo for "
                f"{component_ref}"
            )

        owner_repo_counts[owner_repo] += 1
        signals = (
            _normalize_string_sequence(hint.get("signals"))
            if isinstance(hint, Mapping)
            else []
        )
        for drift_class in component_refresh_drift_classes(component_ref, signals):
            drift_class_counts[drift_class] += 1

        current_status = component_refresh_status(decision, owner_repo=owner_repo)
        status_counts[current_status] += 1
        latest_decision_status = (
            str(decision.get("decision_status") or "unreviewed")
            if isinstance(decision, Mapping)
            else "unreviewed"
        )
        latest_observed_at = (
            str(hint.get("observed_at"))
            if isinstance(hint, Mapping)
            and is_nonempty_string(hint.get("observed_at"))
            else None
        )
        components.append(
            {
                "component_ref": component_ref,
                "owner_repo": owner_repo,
                "latest_decision_status": latest_decision_status,
                "current_status": current_status,
                "latest_route_class": component_refresh_route_class(hint, decision),
                "latest_observed_at": latest_observed_at,
            }
        )

    return {
        "schema_version": "aoa_stats_component_refresh_summary_v1",
        "generated_from": {
            "receipt_input_paths": list(source["receipt_input_paths"]),
            "total_receipts": source["total_receipts"],
            "latest_observed_at": source["latest_observed_at"],
        },
        "owner_repo_counts": string_count_map(owner_repo_counts),
        "status_counts": {
            status: status_counts.get(status, 0)
            for status in COMPONENT_REFRESH_CURRENT_STATUSES
        },
        "drift_class_counts": string_count_map(drift_class_counts),
        "components": components,
    }
