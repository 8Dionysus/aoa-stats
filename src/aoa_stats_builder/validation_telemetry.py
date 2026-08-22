"""Pure validation-telemetry compatibility and coverage projections.

This module deliberately does not decide whether a validation graph is
sufficient, safe, correct, or admissible.  Owners publish those meanings and
their evidence; ``aoa-stats`` checks portable shape and preserves the gaps.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import math
import re
from typing import Any


VALIDATION_TELEMETRY_FIELDS = (
    "wall_ms",
    "cpu_ms",
    "peak_rss_bytes",
    "io_read_bytes",
    "io_write_bytes",
    "result",
    "semantic_class",
    "candidate_identity",
    "environment_identity",
    "cache_posture",
    "receipt_posture",
    "first_failure",
    "rerun_amplification",
    "source_coverage",
)
METRIC_FIELDS = (
    "wall_ms",
    "cpu_ms",
    "peak_rss_bytes",
    "io_read_bytes",
    "io_write_bytes",
)
SEMANTIC_CLASSES = frozenset(
    {
        "structural",
        "local_functional_unit_property",
        "contract_abi_api",
        "invariant",
        "integration",
        "compatibility",
        "generated_fixed_point",
        "regression",
        "adversarial_robustness",
        "artifact_package_install_portable",
        "behavioral_task_eval",
        "system_e2e",
        "semantic_agent_trajectory_eval",
    }
)
BUDGET_TIERS = frozenset({"ultra_fast", "fast", "contextual", "expensive"})
MISSING_STATES = frozenset({"missing", "unknown", "stale"})
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

_HOST_OR_PRIVATE_MARKERS = (
    "/home/",
    "/srv/",
    ".aoa/sessions",
    "transcript",
    "private/",
)


def _portable_ref(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    lowered = value.lower()
    return not (
        value.startswith(("/", "~"))
        or any(marker in lowered for marker in _HOST_OR_PRIVATE_MARKERS)
    )


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _digest(value: object) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _ref_issues(value: object, label: str) -> list[str]:
    return [] if _portable_ref(value) else [f"{label} must be a portable ref"]


def validate_validation_telemetry_port(
    telemetry: Mapping[str, Any],
    *,
    label: str = "validation_telemetry",
) -> list[str]:
    """Check owner-declared telemetry-port invariants beyond JSON Schema."""

    issues: list[str] = []
    if telemetry.get("packet_schema_ref") != (
        "aoa-stats:stats/measurement-contract/validation-telemetry-packet.schema.json"
    ):
        issues.append(f"{label}: packet_schema_ref must name the canonical packet schema")

    required_fields = telemetry.get("required_fields")
    if isinstance(required_fields, list):
        if len(required_fields) != len(set(required_fields)):
            issues.append(f"{label}: required_fields must be unique")
        if set(required_fields) != set(VALIDATION_TELEMETRY_FIELDS):
            issues.append(
                f"{label}: required_fields must cover the canonical telemetry fields"
            )
        if required_fields != sorted(required_fields):
            issues.append(f"{label}: required_fields must be sorted")

    lanes = telemetry.get("node_lanes")
    lane_ids: list[str] = []
    if isinstance(lanes, list):
        for index, lane in enumerate(lanes):
            if not isinstance(lane, Mapping):
                continue
            lane_id = lane.get("id")
            if isinstance(lane_id, str):
                lane_ids.append(lane_id)
            semantic_class = lane.get("semantic_class")
            if semantic_class not in SEMANTIC_CLASSES:
                issues.append(
                    f"{label}:node_lanes[{index}]: semantic_class is not admitted"
                )
            if lane.get("budget_tier") not in BUDGET_TIERS:
                issues.append(
                    f"{label}:node_lanes[{index}]: budget_tier is not admitted"
                )
            claim_refs = lane.get("claim_refs", [])
            if not isinstance(claim_refs, list):
                claim_refs = []
            for field in ("validator_ref", *claim_refs):
                issues.extend(
                    f"{label}:node_lanes[{index}]: {issue}"
                    for issue in _ref_issues(field, "reference")
                )
        if len(lane_ids) != len(set(lane_ids)):
            issues.append(f"{label}: node-lane ids must be unique")

    exports = telemetry.get("exports")
    export_ids: list[str] = []
    if isinstance(exports, list):
        for index, export in enumerate(exports):
            if not isinstance(export, Mapping):
                continue
            export_id = export.get("id")
            if isinstance(export_id, str):
                export_ids.append(export_id)
            posture = export.get("posture")
            packet_refs = export.get("packet_refs")
            if posture == "declaration_only" and packet_refs:
                issues.append(
                    f"{label}:exports[{index}]: declaration_only must not name packets"
                )
            if posture in {"reference", "live"} and not packet_refs:
                issues.append(
                    f"{label}:exports[{index}]: {posture} requires packet_refs"
                )
            for field in ("packet_refs", "evidence_refs"):
                for ref in export.get(field, []):
                    issues.extend(
                        f"{label}:exports[{index}]: {issue}"
                        for issue in _ref_issues(ref, f"{field} reference")
                    )
        if len(export_ids) != len(set(export_ids)):
            issues.append(f"{label}: export ids must be unique")
    return issues


def _validate_identity(identity: object, label: str) -> list[str]:
    if not isinstance(identity, Mapping):
        return [f"{label} must be an object"]
    issues: list[str] = []
    if not _digest(identity.get("digest")):
        issues.append(f"{label}.digest must be a complete sha256 identity")
    issues.extend(_ref_issues(identity.get("source"), f"{label}.source"))
    return issues


def _validate_status_object(
    value: object,
    *,
    label: str,
    observed_statuses: set[str],
) -> list[str]:
    if not isinstance(value, Mapping):
        return [f"{label} must be an object"]
    status = value.get("status")
    if status not in observed_statuses | MISSING_STATES:
        return [f"{label}.status is not admitted"]
    return []


def validate_validation_telemetry_packet(
    packet: Mapping[str, Any],
    *,
    label: str = "validation telemetry packet",
) -> list[str]:
    """Check portable packet semantics without judging owner validation."""

    issues: list[str] = []
    issues.extend(_ref_issues(packet.get("telemetry_port_ref"), f"{label}.telemetry_port_ref"))
    node = packet.get("node")
    if not isinstance(node, Mapping):
        issues.append(f"{label}.node must be an object")
    else:
        if node.get("semantic_class") not in SEMANTIC_CLASSES:
            issues.append(f"{label}.node.semantic_class is not admitted")
        if node.get("budget_tier") not in BUDGET_TIERS:
            issues.append(f"{label}.node.budget_tier is not admitted")
        claim_refs = node.get("claim_refs", [])
        if not isinstance(claim_refs, list):
            claim_refs = []
        for field in ("validator_ref", *claim_refs):
            issues.extend(
                f"{label}.node: {issue}"
                for issue in _ref_issues(field, "reference")
            )

    issues.extend(
        _validate_identity(packet.get("candidate_identity"), f"{label}.candidate_identity")
    )
    issues.extend(
        _validate_identity(packet.get("environment_identity"), f"{label}.environment_identity")
    )

    metrics = packet.get("metrics")
    if isinstance(metrics, Mapping):
        for field in METRIC_FIELDS:
            metric = metrics.get(field)
            if not isinstance(metric, Mapping):
                continue
            status = metric.get("status")
            if status == "observed":
                if not _is_number(metric.get("value")) or metric["value"] < 0:
                    issues.append(
                        f"{label}.metrics.{field}: observed value must be non-negative"
                    )
            elif status in MISSING_STATES and "value" in metric:
                issues.append(
                    f"{label}.metrics.{field}: {status} metric must not carry a value"
                )

    result = packet.get("result")
    if isinstance(result, Mapping):
        issues.extend(_ref_issues(result.get("result_ref"), f"{label}.result.result_ref")) if result.get("result_ref") is not None else None

    cache = packet.get("cache_posture")
    issues.extend(
        _validate_status_object(
            cache,
            label=f"{label}.cache_posture",
            observed_statuses={"hit", "miss", "bypassed", "not_applicable"},
        )
    )
    if isinstance(cache, Mapping):
        key_digest = cache.get("key_digest")
        if key_digest is not None and not _digest(key_digest):
            issues.append(f"{label}.cache_posture.key_digest must be a sha256 digest")
        if cache.get("receipt_ref") is not None:
            issues.extend(_ref_issues(cache.get("receipt_ref"), f"{label}.cache_posture.receipt_ref"))

    receipt = packet.get("receipt_posture")
    issues.extend(
        _validate_status_object(
            receipt,
            label=f"{label}.receipt_posture",
            observed_statuses={"emitted", "not_emitted", "rejected"},
        )
    )
    if isinstance(receipt, Mapping) and receipt.get("receipt_ref") is not None:
        issues.extend(_ref_issues(receipt.get("receipt_ref"), f"{label}.receipt_posture.receipt_ref"))

    first_failure = packet.get("first_failure")
    if isinstance(first_failure, Mapping):
        if first_failure.get("status") == "observed":
            issues.extend(
                _ref_issues(first_failure.get("evidence_ref"), f"{label}.first_failure.evidence_ref")
            )

    rerun = packet.get("rerun_amplification")
    if isinstance(rerun, Mapping) and rerun.get("status") == "observed":
        attempts = rerun.get("attempt_count")
        distinct = rerun.get("distinct_operation_count")
        repeated = rerun.get("repeated_attempt_count")
        validation_attempts = rerun.get("validation_attempt_count")
        validation_reruns = rerun.get("validation_rerun_after_repair_count")
        ratio = rerun.get("attempts_per_distinct_operation")
        if isinstance(attempts, int) and isinstance(distinct, int):
            if distinct < 1 or attempts < distinct:
                issues.append(f"{label}.rerun_amplification: attempts must cover distinct operations")
            elif _is_number(ratio) and not math.isclose(ratio, attempts / distinct, rel_tol=1e-9, abs_tol=1e-9):
                issues.append(
                    f"{label}.rerun_amplification: ratio must equal attempts/distinct operations"
                )
        if isinstance(repeated, int) and isinstance(attempts, int) and repeated > attempts:
            issues.append(f"{label}.rerun_amplification: repeated attempts exceed attempts")
        if isinstance(validation_reruns, int) and isinstance(validation_attempts, int) and validation_reruns > validation_attempts:
            issues.append(
                f"{label}.rerun_amplification: repair reruns exceed validation attempts"
            )

    coverage = packet.get("source_coverage")
    if isinstance(coverage, Mapping) and coverage.get("status") in {"complete", "partial"}:
        expected = coverage.get("expected_owner_count")
        observed = coverage.get("observed_owner_count")
        if isinstance(expected, int) and isinstance(observed, int):
            if observed > expected:
                issues.append(f"{label}.source_coverage: observed owners exceed expected owners")
            if coverage.get("status") == "complete" and observed != expected:
                issues.append(f"{label}.source_coverage: complete coverage must have equal counts")
            if coverage.get("status") == "partial" and observed >= expected:
                issues.append(f"{label}.source_coverage: partial coverage must have a gap")
        for ref in coverage.get("missing_owner_repos", []):
            issues.extend(_ref_issues(ref, f"{label}.source_coverage.missing_owner_repos"))

    provenance = packet.get("provenance")
    if isinstance(provenance, Mapping):
        for index, evidence in enumerate(provenance.get("evidence_refs", [])):
            if isinstance(evidence, Mapping):
                issues.extend(
                    _ref_issues(
                        evidence.get("ref"),
                        f"{label}.provenance.evidence_refs[{index}].ref",
                    )
                )
        issues.extend(_ref_issues(provenance.get("derivation_ref"), f"{label}.provenance.derivation_ref"))
        if provenance.get("source_revision") is not None:
            issues.extend(_ref_issues(provenance.get("source_revision"), f"{label}.provenance.source_revision"))

    posture = packet.get("posture")
    if isinstance(posture, Mapping) and posture.get("raw_content_included") is not False:
        issues.append(f"{label}.posture.raw_content_included must be false")
    return issues


def _packet_field_status(packet: Mapping[str, Any], field: str) -> str:
    if field in METRIC_FIELDS:
        metric = packet.get("metrics", {}).get(field)
        return str(metric.get("status", "missing")) if isinstance(metric, Mapping) else "missing"
    if field == "result":
        result = packet.get("result")
        return "observed" if isinstance(result, Mapping) and result.get("status") != "unknown" else "unknown"
    if field == "semantic_class":
        return "observed" if isinstance(packet.get("node"), Mapping) else "missing"
    if field in {"candidate_identity", "environment_identity"}:
        return "observed" if isinstance(packet.get(field), Mapping) else "missing"
    if field == "cache_posture":
        status = packet.get("cache_posture", {}).get("status") if isinstance(packet.get("cache_posture"), Mapping) else "missing"
        return "not_applicable" if status == "not_applicable" else ("unknown" if status == "unknown" else "observed")
    if field == "receipt_posture":
        status = packet.get("receipt_posture", {}).get("status") if isinstance(packet.get("receipt_posture"), Mapping) else "missing"
        return status if status in MISSING_STATES else "observed"
    if field == "first_failure":
        status = packet.get("first_failure", {}).get("status") if isinstance(packet.get("first_failure"), Mapping) else "missing"
        return "observed" if status in {"none", "observed"} else str(status)
    if field == "rerun_amplification":
        value = packet.get("rerun_amplification")
        return str(value.get("status", "missing")) if isinstance(value, Mapping) else "missing"
    if field == "source_coverage":
        value = packet.get("source_coverage")
        if not isinstance(value, Mapping):
            return "missing"
        status = value.get("status")
        return "observed" if status == "complete" else str(status)
    return "missing"


def _merge_statuses(statuses: Sequence[str]) -> str:
    if not statuses:
        return "missing"
    if all(status == "not_applicable" for status in statuses):
        return "not_applicable"
    if all(status == "observed" for status in statuses):
        return "observed"
    if any(status in {"observed", "partial"} for status in statuses):
        return "partial"
    if len(set(statuses)) == 1:
        return statuses[0]
    return "partial"


def _field_coverage_for_owner(
    owner_repo: str,
    packets: Sequence[Mapping[str, Any]],
    *,
    reason: str | None = None,
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for field in VALIDATION_TELEMETRY_FIELDS:
        status = _merge_statuses([_packet_field_status(packet, field) for packet in packets])
        entry: dict[str, Any] = {
            "status": status,
            "owner_count": 1 if status in {"observed", "partial"} else 0,
            "expected_owner_count": 1,
        }
        if status in {"observed", "partial"}:
            entry["owner_repos"] = [owner_repo]
        else:
            entry["reason"] = reason or "field was not observed in an admitted packet"
        result[field] = entry
    return result


def _aggregate_field_coverage(
    owner_records: Sequence[Mapping[str, Any]],
    expected_owner_repos: Sequence[str],
) -> dict[str, dict[str, Any]]:
    expected_count = len(expected_owner_repos)
    result: dict[str, dict[str, Any]] = {}
    for field in VALIDATION_TELEMETRY_FIELDS:
        statuses: list[str] = []
        owner_repos: list[str] = []
        for record in owner_records:
            coverage = record["field_coverage"][field]
            statuses.append(str(coverage["status"]))
            if coverage.get("status") in {"observed", "partial"}:
                owner_repos.append(str(record["owner_repo"]))
        status = _merge_statuses(statuses)
        if status == "not_applicable" and len(owner_repos) < expected_count:
            status = "partial"
        entry: dict[str, Any] = {
            "status": status,
            "owner_count": len(owner_repos),
            "expected_owner_count": expected_count,
        }
        if owner_repos:
            entry["owner_repos"] = sorted(owner_repos)
        else:
            entry["reason"] = "no owner supplied an admitted validation telemetry packet"
        result[field] = entry
    return result


def build_validation_telemetry_baseline(
    expected_owners: Sequence[Mapping[str, Any]],
    *,
    port_inputs: Mapping[str, Mapping[str, Any]],
    packets: Sequence[Mapping[str, Any]] = (),
    inventory_ref: str = "stats/federation/owner-inventory.json",
    routed_surface_ids: Sequence[str] = (),
    source_revision: str | None = None,
    input_posture: str = "reference_only",
) -> dict[str, Any]:
    """Build a deterministic coverage/read model from explicit owner inputs."""

    normalized = sorted(
        [dict(owner) for owner in expected_owners],
        key=lambda owner: str(owner.get("repo_id", "")),
    )
    owner_repos = [str(owner.get("repo_id", "")) for owner in normalized]
    if not owner_repos or any(not repo for repo in owner_repos):
        raise ValueError("expected_owners must contain non-empty repo_id values")
    if len(owner_repos) != len(set(owner_repos)):
        raise ValueError("expected_owners must contain unique repo_id values")
    if input_posture not in {"reference_only", "mixed"}:
        raise ValueError("input_posture must be reference_only or mixed")

    packet_by_owner: dict[str, list[Mapping[str, Any]]] = {}
    for packet in packets:
        if not isinstance(packet, Mapping):
            continue
        owner_repo = packet.get("owner_repo")
        if isinstance(owner_repo, str) and packet.get("admitted", True) is not False:
            packet_by_owner.setdefault(owner_repo, []).append(packet)

    records: list[dict[str, Any]] = []
    for owner in normalized:
        owner_repo = str(owner["repo_id"])
        classification = str(owner.get("classification", "implemented"))
        input_entry = port_inputs.get(owner_repo)
        if classification == "routed_to_stronger_owner" and input_entry is None:
            port_status = "routed_to_stronger_owner"
            telemetry_status = "not_applicable"
            port_ref = None
            telemetry_port_ref = None
            declared_node_count = None
            packet_count = None
            field_coverage = _field_coverage_for_owner(
                owner_repo,
                (),
                reason="owner is routed to a stronger source owner",
            )
            for field in field_coverage.values():
                field["status"] = "not_applicable"
                field["owner_count"] = None
                field.pop("reason", None)
        elif classification == "not_applicable" and input_entry is None:
            port_status = "not_applicable"
            telemetry_status = "not_applicable"
            port_ref = None
            telemetry_port_ref = None
            declared_node_count = None
            packet_count = None
            field_coverage = _field_coverage_for_owner(
                owner_repo,
                (),
                reason="owner is not applicable to this source family",
            )
            for field in field_coverage.values():
                field["status"] = "not_applicable"
                field["owner_count"] = None
                field.pop("reason", None)
        elif input_entry is None:
            port_status = "missing"
            telemetry_status = "missing_port"
            port_ref = None
            telemetry_port_ref = None
            declared_node_count = None
            packet_count = None
            field_coverage = _field_coverage_for_owner(
                owner_repo,
                (),
                reason="no explicit owner port input was supplied",
            )
        else:
            port_ref = input_entry.get("port_ref")
            payload = input_entry.get("payload")
            if input_entry.get("input_status") == "invalid" or not isinstance(payload, Mapping):
                port_status = "invalid"
                telemetry_status = "invalid"
                telemetry_port_ref = None
                declared_node_count = None
                packet_count = None
                field_coverage = _field_coverage_for_owner(
                    owner_repo,
                    (),
                    reason="owner port input failed compatibility validation",
                )
            else:
                port_status = "observed"
                telemetry = payload.get("validation_telemetry")
                owner_packets = packet_by_owner.get(owner_repo, [])
                if not isinstance(telemetry, Mapping):
                    telemetry_status = "port_without_telemetry"
                    telemetry_port_ref = None
                    declared_node_count = None
                    packet_count = 0
                    field_coverage = _field_coverage_for_owner(
                        owner_repo,
                        (),
                        reason="owner port has no validation_telemetry declaration",
                    )
                else:
                    telemetry_port_ref = input_entry.get("telemetry_port_ref") or (
                        f"{port_ref}#/validation_telemetry"
                    )
                    declared_node_count = len(telemetry.get("node_lanes", []))
                    packet_count = len(owner_packets)
                    if owner_packets:
                        telemetry_status = (
                            "live"
                            if any(
                                isinstance(packet.get("posture"), Mapping)
                                and packet["posture"].get("live_state") == "live"
                                for packet in owner_packets
                            )
                            else "reference"
                        )
                        field_coverage = _field_coverage_for_owner(owner_repo, owner_packets)
                    else:
                        telemetry_status = "declared_only"
                        field_coverage = _field_coverage_for_owner(
                            owner_repo,
                            (),
                            reason="telemetry port is declaration-only until an admitted packet exists",
                        )

        records.append(
            {
                "owner_repo": owner_repo,
                "classification": classification,
                "port_status": port_status,
                "telemetry_status": telemetry_status,
                "port_ref": port_ref,
                "telemetry_port_ref": telemetry_port_ref,
                "declared_node_count": declared_node_count,
                "packet_count": packet_count,
                "field_coverage": field_coverage,
            }
        )

    expected_count = len(owner_repos)
    port_present = sum(record["port_status"] == "observed" for record in records)
    port_missing_repos = [
        record["owner_repo"] for record in records if record["port_status"] == "missing"
    ]
    port_invalid_count = sum(record["port_status"] == "invalid" for record in records)
    telemetry_declared = sum(
        record["telemetry_status"] in {"declared_only", "reference", "live"}
        for record in records
    )
    telemetry_packet = sum(
        record["telemetry_status"] in {"reference", "live"} for record in records
    )
    telemetry_gap_repos = [
        record["owner_repo"]
        for record in records
        if record["telemetry_status"] not in {"reference", "live"}
    ]
    owner_coverage_status = (
        "complete"
        if port_present == expected_count and not port_missing_repos and port_invalid_count == 0
        else "missing"
        if port_present == 0
        else "partial"
    )
    telemetry_coverage_status = (
        "complete"
        if telemetry_packet == expected_count
        else "missing"
        if telemetry_packet == 0
        else "partial"
    )
    field_coverage = _aggregate_field_coverage(records, owner_repos)
    evidence_refs: list[dict[str, str]] = [
        {"kind": "owner-inventory", "ref": inventory_ref}
    ]
    for record in records:
        if record["port_ref"] is not None:
            evidence_refs.append(
                {
                    "kind": "owner-port",
                    "ref": f"{record['owner_repo']}:{record['port_ref']}",
                }
            )

    return {
        "schema_version": "aoa_stats_validation_telemetry_baseline_v1",
        "contract_version": "1.0.0",
        "source_mode": "owner_inventory_plus_explicit_port_inputs",
        "input_posture": input_posture,
        "target_universe": {
            "inventory_ref": inventory_ref,
            "expected_owner_repos": owner_repos,
            "expected_owner_count": expected_count,
            "routed_surface_ids": sorted(set(str(item) for item in routed_surface_ids)),
        },
        "owner_records": records,
        "summary": {
            "expected_owner_count": expected_count,
            "port_present_count": port_present,
            "port_missing_count": len(port_missing_repos),
            "port_invalid_count": port_invalid_count,
            "telemetry_declared_owner_count": telemetry_declared,
            "telemetry_packet_owner_count": telemetry_packet,
            "owner_coverage_status": owner_coverage_status,
            "telemetry_coverage_status": telemetry_coverage_status,
            "missing_port_owner_repos": sorted(port_missing_repos),
            "telemetry_gap_owner_repos": sorted(telemetry_gap_repos),
            "field_coverage": field_coverage,
        },
        "provenance": {
            "evidence_refs": evidence_refs,
            "derivation_ref": "aoa-stats:scripts/build_validation_telemetry_baseline.py",
            "source_revision": source_revision,
        },
        "authority_ceiling": (
            "Derived coverage and compatibility only; owner validators retain claims, "
            "semantic meaning, budgets, evidence sufficiency, and acceptance authority."
        ),
    }
