"""Pure validation-telemetry compatibility and coverage projections.

This module deliberately does not decide whether a validation graph is
sufficient, safe, correct, or admissible.  Owners publish those meanings and
their evidence; ``aoa-stats`` checks portable shape and preserves the gaps.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
import math
import re
from typing import Any


VALIDATION_TELEMETRY_FIELDS = (
    "cache_posture",
    "candidate_identity",
    "cost",
    "cpu_ms",
    "environment_identity",
    "first_failure",
    "io_read_bytes",
    "io_write_bytes",
    "peak_rss_bytes",
    "receipt_posture",
    "rerun_amplification",
    "result",
    "semantic_class",
    "source_coverage",
    "time_to_first_failure_ms",
    "wall_ms",
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
OWNER_INPUT_KINDS = frozenset({"direct_owner_source", "central_source_home"})
TELEMETRY_POSTURES = frozenset({"reference", "live"})
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
RFC3339_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
CENTRAL_SOURCE_HOME_OWNER = "aoa-stats"
CENTRAL_SOURCE_HOME_REF = "stats/source_home.manifest.json"
CENTRAL_SOURCE_HOME_SCHEMA_VERSION = "aoa_stats_source_home_v3"
CENTRAL_SOURCE_HOME_STATUS = "active_source_home"
TELEMETRY_PACKET_SCHEMA_REF = (
    "aoa-stats:stats/measurement-contract/validation-telemetry-packet.schema.json"
)
PACKET_REQUIRED_FIELDS = (
    "schema_version",
    "contract_version",
    "owner_repo",
    "telemetry_port_ref",
    "observation_id",
    "observed_at",
    "node",
    "result",
    "candidate_identity",
    "environment_identity",
    "metrics",
    "cache_posture",
    "receipt_posture",
    "first_failure",
    "rerun_amplification",
    "source_coverage",
    "cost",
    "provenance",
    "posture",
)

_HOST_OR_PRIVATE_MARKERS = (
    "/home/",
    "/srv/",
    ".aoa/sessions",
    "transcript",
    "private/",
)


class ValidationTelemetryAdmissionError(ValueError):
    """Raised when a packet cannot cross the typed admission boundary."""

    def __init__(self, issues: Sequence[str]) -> None:
        self.issues = tuple(str(issue) for issue in issues)
        super().__init__("; ".join(self.issues) or "validation telemetry admission failed")


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _packet_digest(packet: Mapping[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(packet)).hexdigest()


@dataclass(frozen=True)
class ValidationTelemetryAdmissionReceipt:
    """A content-bound, non-authoritative receipt for one owner export."""

    schema_version: str
    packet_digest: str
    owner_repo: str
    telemetry_port_ref: str
    observation_id: str
    node_id: str
    lane: str
    port_ref: str
    port_content_digest: str
    owner_source_ref: str
    packet_ref: str
    candidate_digest: str
    environment_digest: str
    source_revision: str | None
    live_state: str
    acceptance_evidenced: bool = False

    def binds(self, packet: Mapping[str, Any]) -> bool:
        node = packet.get("node")
        candidate = packet.get("candidate_identity")
        environment = packet.get("environment_identity")
        provenance = packet.get("provenance")
        posture = packet.get("posture")
        return (
            self.schema_version == "aoa_stats_validation_telemetry_receipt_v1"
            and self.packet_digest == _packet_digest(packet)
            and packet.get("owner_repo") == self.owner_repo
            and packet.get("telemetry_port_ref") == self.telemetry_port_ref
            and packet.get("observation_id") == self.observation_id
            and isinstance(node, Mapping)
            and node.get("node_id") == self.node_id
            and node.get("lane") == self.lane
            and isinstance(candidate, Mapping)
            and candidate.get("digest") == self.candidate_digest
            and isinstance(environment, Mapping)
            and environment.get("digest") == self.environment_digest
            and isinstance(provenance, Mapping)
            and provenance.get("source_revision") == self.source_revision
            and isinstance(posture, Mapping)
            and posture.get("live_state") == self.live_state
            and self.acceptance_evidenced is False
        )


_ADMISSION_TOKEN = object()


@dataclass(frozen=True)
class ValidationTelemetryAdmission:
    """Typed packet plus receipt; raw mappings cannot be passed to the builder."""

    packet: Mapping[str, Any]
    receipt: ValidationTelemetryAdmissionReceipt
    _token: object = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self._token is not _ADMISSION_TOKEN:
            raise TypeError("use admit_validation_telemetry_packet to create an admission")
        object.__setattr__(self, "packet", deepcopy(dict(self.packet)))
        if not self.receipt.binds(self.packet):
            raise ValueError("admission receipt does not bind packet")

    def is_intact(self) -> bool:
        return self.receipt.binds(self.packet)


def _portable_ref(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    lowered = value.lower()
    normalized = value.replace("\\", "/")
    if "\x00" in normalized:
        return False
    if re.match(r"^[a-zA-Z]:/", normalized):
        return False
    if ":" in normalized:
        qualifier, normalized_path = normalized.split(":", 1)
        if re.fullmatch(r"[A-Za-z0-9_.-]+", qualifier) is None:
            return False
    else:
        normalized_path = normalized
    if any(part in {"", ".", ".."} for part in normalized_path.split("/")):
        return False
    if normalized_path.startswith(("/", "~", "@", "//")):
        return False
    if "://" in normalized or normalized.lower().startswith(
        ("file:", "http:", "https:", "urn:")
    ):
        return False
    return not (
        normalized.startswith(("/", "~"))
        or any(marker in lowered for marker in _HOST_OR_PRIVATE_MARKERS)
    )


def _is_number(value: object) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _digest(value: object) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _ref_issues(value: object, label: str) -> list[str]:
    return [] if _portable_ref(value) else [f"{label} must be a portable ref"]


def _rfc3339_issues(value: object, label: str) -> list[str]:
    if not isinstance(value, str) or RFC3339_RE.fullmatch(value) is None:
        return [f"{label} must be a strict RFC3339 date-time"]
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return [f"{label} must be a strict RFC3339 date-time"]
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return [f"{label} must include a timezone offset"]
    return []


def validate_central_source_home_identity(
    source_home: Mapping[str, Any],
    *,
    content_digest: str,
    label: str = "source home",
) -> list[str]:
    """Validate the canonical source-home identity before it becomes input."""

    issues: list[str] = []
    if source_home.get("schema_version") != CENTRAL_SOURCE_HOME_SCHEMA_VERSION:
        issues.append(
            f"{label}: schema_version must be {CENTRAL_SOURCE_HOME_SCHEMA_VERSION!r}"
        )
    if source_home.get("owner_repo") != CENTRAL_SOURCE_HOME_OWNER:
        issues.append(f"{label}: owner_repo must be {CENTRAL_SOURCE_HOME_OWNER!r}")
    if source_home.get("status") != CENTRAL_SOURCE_HOME_STATUS:
        issues.append(f"{label}: status must be {CENTRAL_SOURCE_HOME_STATUS!r}")
    if not _digest(content_digest):
        issues.append(f"{label}: content_digest must be a sha256 digest")
    families = source_home.get("families")
    if not isinstance(families, list) or not families:
        issues.append(f"{label}: families must be a non-empty list")
    else:
        family_by_id = {
            item.get("id"): item
            for item in families
            if isinstance(item, Mapping) and isinstance(item.get("id"), str)
        }
        for family_id, required_path in (
            ("measurement_contract", "stats/measurement-contract"),
            ("federation", "stats/federation"),
        ):
            family = family_by_id.get(family_id)
            if not isinstance(family, Mapping) or family.get("path") != required_path:
                issues.append(
                    f"{label}: family {family_id!r} must bind path {required_path!r}"
                )
    return issues


def _is_authoritative_owner_input(
    owner_repo: str,
    input_entry: object,
) -> bool:
    """Require an explicit, owner-labelled source input before projection."""

    if not isinstance(input_entry, Mapping):
        return False
    if input_entry.get("input_status") == "invalid":
        return False
    if input_entry.get("owner_repo") != owner_repo:
        return False
    source_kind = input_entry.get("source_kind")
    source_ref = input_entry.get("source_ref")
    port_ref = input_entry.get("port_ref")
    payload = input_entry.get("payload")
    if source_kind not in OWNER_INPUT_KINDS:
        return False
    if not isinstance(payload, Mapping) or payload.get("owner_repo") != owner_repo:
        return False
    declared_port_digest = input_entry.get("port_content_digest")
    if declared_port_digest is not None and declared_port_digest != _packet_digest(payload):
        return False
    if not isinstance(port_ref, str) or not _portable_ref(port_ref):
        return False
    if source_kind == "direct_owner_source":
        if port_ref != "stats/port.manifest.json":
            return False
        if source_ref != f"{owner_repo}:{port_ref}":
            return False
    else:
        if (
            owner_repo != CENTRAL_SOURCE_HOME_OWNER
            or source_ref != f"{CENTRAL_SOURCE_HOME_OWNER}:{CENTRAL_SOURCE_HOME_REF}"
            or port_ref != CENTRAL_SOURCE_HOME_REF
            or payload.get("source_home_input") is not True
            or payload.get("source_home_ref") != CENTRAL_SOURCE_HOME_REF
            or payload.get("source_home_schema_version")
            != CENTRAL_SOURCE_HOME_SCHEMA_VERSION
            or payload.get("source_home_status") != CENTRAL_SOURCE_HOME_STATUS
            or not _digest(payload.get("source_home_digest"))
        ):
            return False
    telemetry_port_ref = input_entry.get("telemetry_port_ref")
    return telemetry_port_ref is None or telemetry_port_ref == (
        f"{port_ref}#/validation_telemetry"
    )


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
            issues.extend(
                f"{label}:node_lanes[{index}]: {issue}"
                for issue in _validate_timing_contract(
                    lane.get("timing_contract"),
                    budget_tier=lane.get("budget_tier"),
                    label="timing_contract",
                )
            )
            claim_refs = lane.get("claim_refs", [])
            evidence_refs = lane.get("evidence_refs", [])
            if not isinstance(claim_refs, list) or not claim_refs:
                issues.append(
                    f"{label}:node_lanes[{index}]: claim_refs must be non-empty"
                )
                claim_refs = [] if not isinstance(claim_refs, list) else claim_refs
            if not isinstance(evidence_refs, list) or not evidence_refs:
                issues.append(
                    f"{label}:node_lanes[{index}]: evidence_refs must be non-empty"
                )
                evidence_refs = (
                    [] if not isinstance(evidence_refs, list) else evidence_refs
                )
            if not isinstance(lane.get("acceptance_barrier"), str) or not lane.get(
                "acceptance_barrier"
            ):
                issues.append(
                    f"{label}:node_lanes[{index}]: acceptance_barrier must be non-empty"
                )
            for field in ("validator_ref", *claim_refs, *evidence_refs):
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
    if not isinstance(identity.get("kind"), str) or not identity.get("kind"):
        issues.append(f"{label}.kind must be non-empty")
    if not _digest(identity.get("digest")):
        issues.append(f"{label}.digest must be a complete sha256 identity")
    issues.extend(_ref_issues(identity.get("source"), f"{label}.source"))
    return issues


def _validate_status_object(
    value: object,
    *,
    label: str,
    observed_statuses: set[str],
    missing_statuses: set[str] = MISSING_STATES,
) -> list[str]:
    if not isinstance(value, Mapping):
        return [f"{label} must be an object"]
    status = value.get("status")
    if status not in observed_statuses | missing_statuses:
        return [f"{label}.status is not admitted"]
    return []


def _validate_time_to_first_failure(
    value: object,
    *,
    label: str,
) -> list[str]:
    if not isinstance(value, Mapping):
        return [f"{label} must be an object"]
    status = value.get("status")
    if status == "observed":
        if not _is_number(value.get("value")) or value["value"] < 0:
            return [f"{label}.value must be a non-negative number"]
        if "reason" in value:
            return [f"{label}: observed value must not carry a reason"]
        return []
    if status == "not_applicable":
        return [
            f"{label}: not_applicable must not carry a value or reason"
        ] if any(key in value for key in ("value", "reason")) else []
    if status in MISSING_STATES:
        issues = []
        if not isinstance(value.get("reason"), str) or not value["reason"]:
            issues.append(f"{label}.reason is required for {status}")
        if "value" in value:
            issues.append(f"{label}: {status} value must be omitted")
        return issues
    return [f"{label}.status is not admitted"]


def _validate_timing_contract(
    value: object,
    *,
    budget_tier: object,
    label: str,
) -> list[str]:
    if not isinstance(value, Mapping):
        return [f"{label} must be an object"]
    issues: list[str] = []
    scope = value.get("scope")
    if scope not in {"real_validator_process", "contextual_validator_process"}:
        issues.append(f"{label}.scope is not admitted")
    issues.extend(_ref_issues(value.get("measurement_ref"), f"{label}.measurement_ref"))
    sample_count = value.get("sample_count")
    if not isinstance(sample_count, int) or isinstance(sample_count, bool) or sample_count < 1:
        issues.append(f"{label}.sample_count must be a positive integer")
    p95_budget_ms = value.get("p95_budget_ms")
    if p95_budget_ms is not None and (
        not isinstance(p95_budget_ms, int)
        or isinstance(p95_budget_ms, bool)
        or p95_budget_ms < 1
    ):
        issues.append(f"{label}.p95_budget_ms must be a positive integer or null")
    if budget_tier in {"ultra_fast", "fast"}:
        if scope != "real_validator_process":
            issues.append(
                f"{label}: fast-tier timing must measure the real validator process"
            )
        if p95_budget_ms is None or p95_budget_ms > 1000:
            issues.append(
                f"{label}: fast-tier timing must declare p95_budget_ms <= 1000"
            )
    elif scope == "contextual_validator_process" and p95_budget_ms is not None:
        issues.append(
            f"{label}: contextual timing must not advertise a fast p95 budget"
        )
    return issues


def _telemetry_export_for_packet(
    telemetry_port: Mapping[str, Any],
    *,
    packet_ref: str,
    packet_live_state: str,
    label: str,
) -> Mapping[str, Any] | None:
    exports = telemetry_port.get("exports")
    if not isinstance(exports, list):
        return None
    matches = [
        export
        for export in exports
        if isinstance(export, Mapping)
        and isinstance(export.get("packet_refs"), list)
        and packet_ref in export["packet_refs"]
    ]
    if len(matches) != 1:
        return None
    export = matches[0]
    if export.get("posture") not in TELEMETRY_POSTURES:
        return None
    if export.get("posture") != packet_live_state:
        return None
    return export


def _required_mapping_keys(
    value: object,
    *,
    required: Sequence[str],
    label: str,
) -> tuple[Mapping[str, Any] | None, list[str]]:
    if not isinstance(value, Mapping):
        return None, [f"{label} must be an object"]
    return value, [
        f"{label}: required field {field!r} is missing"
        for field in required
        if field not in value
    ]


def validate_validation_telemetry_packet_against_port(
    packet: Mapping[str, Any],
    telemetry_port: Mapping[str, Any],
    *,
    expected_owner_repo: str | None = None,
    expected_telemetry_port_ref: str | Sequence[str] | None = None,
    label: str = "validation telemetry packet",
) -> list[str]:
    """Join packet identity and claim/evidence boundaries to one owner lane."""

    issues: list[str] = []
    if expected_owner_repo is not None and packet.get("owner_repo") != expected_owner_repo:
        issues.append(f"{label}.owner_repo must match the declared owner port")
    expected_port_refs = (
        {expected_telemetry_port_ref}
        if isinstance(expected_telemetry_port_ref, str)
        else set(expected_telemetry_port_ref or ())
    )
    if expected_port_refs and packet.get("telemetry_port_ref") not in expected_port_refs:
        issues.append(f"{label}.telemetry_port_ref must match the declared owner port")

    node = packet.get("node")
    lanes = telemetry_port.get("node_lanes")
    if not isinstance(node, Mapping) or not isinstance(lanes, list):
        return issues
    matches = [
        lane
        for lane in lanes
        if isinstance(lane, Mapping)
        and lane.get("id") == node.get("node_id")
        and lane.get("lane") == node.get("lane")
    ]
    if len(matches) != 1:
        issues.append(
            f"{label}.node must match exactly one declared telemetry node lane"
        )
        return issues
    lane = matches[0]
    for field in (
        "semantic_class",
        "budget_tier",
        "validator_ref",
        "acceptance_barrier",
    ):
        if node.get(field) != lane.get(field):
            issues.append(
                f"{label}.node.{field} must match the declared telemetry lane"
            )
    for field in ("claim_refs", "evidence_refs"):
        packet_refs = node.get(field)
        lane_refs = lane.get(field)
        if not isinstance(packet_refs, list) or not isinstance(lane_refs, list):
            continue
        if not all(
            isinstance(ref, str)
            for ref in (*packet_refs, *lane_refs)
        ) or set(packet_refs) != set(lane_refs):
            issues.append(
                f"{label}.node.{field} must match the declared telemetry lane"
            )
    first_failure = packet.get("first_failure")
    if isinstance(first_failure, Mapping) and first_failure.get("status") == "observed":
        lane_evidence_refs = lane.get("evidence_refs")
        lane_evidence_set = (
            {
                ref
                for ref in lane_evidence_refs
                if isinstance(ref, str)
            }
            if isinstance(lane_evidence_refs, list)
            else set()
        )
        if first_failure.get("evidence_ref") not in lane_evidence_set:
            issues.append(
                f"{label}.first_failure.evidence_ref must link to the declared lane evidence"
            )
    return issues


def admit_validation_telemetry_packet(
    packet: Mapping[str, Any],
    *,
    schema_issues: Sequence[str] | None = None,
    telemetry_port: Mapping[str, Any] | None,
    owner_port: Mapping[str, Any] | None = None,
    expected_owner_repo: str | None = None,
    expected_telemetry_port_ref: str | None = None,
    expected_port_ref: str | None = None,
    expected_packet_ref: str | None = None,
    owner_source_ref: str | None = None,
    label: str = "validation telemetry packet",
) -> ValidationTelemetryAdmission:
    """Create a content-bound, non-authoritative owner-export admission.

    The canonical JSON Schema check is an explicit caller precondition.  This
    pure function does not load or duplicate that schema; callers must pass
    its findings (an empty sequence means the check passed).  Omitting the
    findings is rejected so nested schema closure cannot be silently bypassed.
    """

    if schema_issues is None:
        raise ValidationTelemetryAdmissionError(
            [
                f"{label}: canonical JSON Schema validation is a required "
                "precondition; pass schema_issues=() after validation or pass "
                "the schema findings"
            ]
        )
    if not isinstance(packet, Mapping):
        raise ValidationTelemetryAdmissionError([f"{label} must be an object"])
    issues = [str(issue) for issue in schema_issues]
    if "admitted" in packet:
        issues.append(f"{label}: admitted sentinel is not a packet field")
    issues.extend(
        f"{label}: required field {field!r} is missing"
        for field in PACKET_REQUIRED_FIELDS
        if field not in packet
    )
    if packet.get("schema_version") != "aoa_stats_validation_telemetry_packet_v1":
        issues.append(
            f"{label}: schema_version must be "
            "'aoa_stats_validation_telemetry_packet_v1'"
        )
    if not isinstance(packet.get("contract_version"), str) or re.fullmatch(
        r"[0-9]+\.[0-9]+\.[0-9]+", str(packet.get("contract_version"))
    ) is None:
        issues.append(f"{label}: contract_version must be semantic version text")
    if not isinstance(packet.get("owner_repo"), str) or not packet.get("owner_repo"):
        issues.append(f"{label}: owner_repo must be non-empty")
    if not isinstance(packet.get("observation_id"), str) or not packet.get(
        "observation_id"
    ):
        issues.append(f"{label}: observation_id must be non-empty")
    if not isinstance(expected_owner_repo, str) or not expected_owner_repo:
        issues.append(f"{label}: expected_owner_repo is required for admission")
    if not isinstance(expected_telemetry_port_ref, str) or not expected_telemetry_port_ref:
        issues.append(
            f"{label}: expected_telemetry_port_ref is required for admission"
        )
    if not isinstance(expected_port_ref, str) or not expected_port_ref:
        issues.append(f"{label}: expected_port_ref is required for admission")
    elif not _portable_ref(expected_port_ref):
        issues.append(f"{label}: expected_port_ref must be a portable ref")
    if not isinstance(expected_packet_ref, str) or not expected_packet_ref:
        issues.append(f"{label}: expected_packet_ref is required for admission")
    elif not _portable_ref(expected_packet_ref):
        issues.append(f"{label}: expected_packet_ref must be a portable ref")
    if not isinstance(owner_source_ref, str) or not owner_source_ref:
        issues.append(f"{label}: owner_source_ref is required for admission")
    elif not _portable_ref(owner_source_ref):
        issues.append(f"{label}: owner_source_ref must be a portable ref")
    elif (
        isinstance(expected_owner_repo, str)
        and isinstance(expected_port_ref, str)
        and owner_source_ref != f"{expected_owner_repo}:{expected_port_ref}"
    ):
        issues.append(
            f"{label}: owner_source_ref must bind the expected owner and port reference"
        )
    issues.extend(validate_validation_telemetry_packet(packet, label=label))
    if telemetry_port is None:
        issues.append(f"{label}: an owner telemetry port is required for admission")
    elif not isinstance(telemetry_port, Mapping):
        issues.append(f"{label}: owner telemetry port must be an object")
    else:
        issues.extend(
            f"{label}: {issue}"
            for issue in validate_validation_telemetry_port(telemetry_port)
        )
        issues.extend(
            validate_validation_telemetry_packet_against_port(
                packet,
                telemetry_port,
                expected_owner_repo=expected_owner_repo,
                expected_telemetry_port_ref=expected_telemetry_port_ref,
                label=label,
            )
        )
        posture = packet.get("posture")
        live_state = posture.get("live_state") if isinstance(posture, Mapping) else None
        if isinstance(expected_packet_ref, str) and isinstance(live_state, str):
            if (
                _telemetry_export_for_packet(
                    telemetry_port,
                    packet_ref=expected_packet_ref,
                    packet_live_state=live_state,
                    label=label,
                )
                is None
            ):
                issues.append(
                    f"{label}: packet must be listed by exactly one reference/live owner export"
                )
    if owner_port is None:
        issues.append(f"{label}: the complete owner port is required for admission")
    elif not isinstance(owner_port, Mapping):
        issues.append(f"{label}: complete owner port must be an object")
    else:
        if owner_port.get("owner_repo") != expected_owner_repo:
            issues.append(f"{label}: owner port owner_repo must match expected_owner_repo")
        if owner_port.get("validation_telemetry") != telemetry_port:
            issues.append(
                f"{label}: telemetry_port must be the validation_telemetry extension of owner_port"
            )
    if issues:
        raise ValidationTelemetryAdmissionError(sorted(set(issues)))

    node = packet["node"]
    assert isinstance(node, Mapping)
    candidate = packet["candidate_identity"]
    environment = packet["environment_identity"]
    provenance = packet["provenance"]
    posture = packet["posture"]
    assert isinstance(candidate, Mapping)
    assert isinstance(environment, Mapping)
    assert isinstance(provenance, Mapping)
    assert isinstance(posture, Mapping)
    receipt = ValidationTelemetryAdmissionReceipt(
        schema_version="aoa_stats_validation_telemetry_receipt_v1",
        packet_digest=_packet_digest(packet),
        owner_repo=str(packet["owner_repo"]),
        telemetry_port_ref=str(packet["telemetry_port_ref"]),
        observation_id=str(packet["observation_id"]),
        node_id=str(node["node_id"]),
        lane=str(node["lane"]),
        port_ref=str(expected_port_ref),
        port_content_digest=_packet_digest(owner_port),
        owner_source_ref=str(owner_source_ref),
        packet_ref=str(expected_packet_ref),
        candidate_digest=str(candidate["digest"]),
        environment_digest=str(environment["digest"]),
        source_revision=(
            str(provenance["source_revision"])
            if provenance.get("source_revision") is not None
            else None
        ),
        live_state=str(posture["live_state"]),
        acceptance_evidenced=False,
    )
    return ValidationTelemetryAdmission(
        packet=packet,
        receipt=receipt,
        _token=_ADMISSION_TOKEN,
    )


def validate_validation_telemetry_packet(
    packet: Mapping[str, Any],
    *,
    label: str = "validation telemetry packet",
) -> list[str]:
    """Check portable packet semantics without judging owner validation."""

    if not isinstance(packet, Mapping):
        return [f"{label} must be an object"]
    issues: list[str] = []
    issues.extend(
        f"{label}: required field {field!r} is missing"
        for field in PACKET_REQUIRED_FIELDS
        if field not in packet
    )
    for field, required in (
        (
            "node",
            (
                "node_id",
                "lane",
                "semantic_class",
                "budget_tier",
                "validator_ref",
                "claim_refs",
                "evidence_refs",
                "acceptance_barrier",
            ),
        ),
        ("result", ("status", "exit_code")),
        (
            "metrics",
            ("wall_ms", "cpu_ms", "peak_rss_bytes", "io_read_bytes", "io_write_bytes"),
        ),
        ("cache_posture", ("status",)),
        ("receipt_posture", ("status",)),
        ("first_failure", ("status",)),
        ("rerun_amplification", ("status",)),
        ("source_coverage", ("status",)),
        ("cost", ("status",)),
        ("provenance", ("evidence_refs", "derivation_ref", "source_revision")),
        ("posture", ("freshness", "live_state", "privacy", "raw_content_included")),
    ):
        _, missing = _required_mapping_keys(
            packet.get(field), required=required, label=f"{label}.{field}"
        )
        issues.extend(missing)
    issues.extend(_rfc3339_issues(packet.get("observed_at"), f"{label}.observed_at"))
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
        evidence_refs = node.get("evidence_refs", [])
        if not isinstance(claim_refs, list) or not claim_refs:
            issues.append(f"{label}.node.claim_refs must be non-empty")
            claim_refs = [] if not isinstance(claim_refs, list) else claim_refs
        if not isinstance(evidence_refs, list) or not evidence_refs:
            issues.append(f"{label}.node.evidence_refs must be non-empty")
            evidence_refs = [] if not isinstance(evidence_refs, list) else evidence_refs
        if not isinstance(node.get("acceptance_barrier"), str) or not node.get(
            "acceptance_barrier"
        ):
            issues.append(f"{label}.node.acceptance_barrier must be non-empty")
        for field in ("validator_ref", *claim_refs, *evidence_refs):
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
                issues.append(f"{label}.metrics.{field} must be an object")
                continue
            status = metric.get("status")
            if status not in {"observed", *MISSING_STATES}:
                issues.append(
                    f"{label}.metrics.{field}.status is not admitted"
                )
            if status == "observed":
                if not _is_number(metric.get("value")) or metric["value"] < 0:
                    issues.append(
                        f"{label}.metrics.{field}: observed value must be non-negative"
                    )
            elif status in MISSING_STATES:
                if not isinstance(metric.get("reason"), str) or not metric["reason"]:
                    issues.append(
                        f"{label}.metrics.{field}.reason is required for {status}"
                    )
                if "value" in metric:
                    issues.append(
                        f"{label}.metrics.{field}: {status} metric must not carry a value"
                    )

    result = packet.get("result")
    if isinstance(result, Mapping):
        result_status = result.get("status")
        exit_code = result.get("exit_code")
        if result_status not in {"pass", "fail", "blocked", "skipped", "cancelled", "unknown"}:
            issues.append(f"{label}.result.status is not admitted")
        if exit_code is not None and (
            not isinstance(exit_code, int) or isinstance(exit_code, bool)
        ):
            issues.append(f"{label}.result.exit_code must be an integer or null")
        if result_status == "pass" and exit_code != 0:
            issues.append(f"{label}.result: pass requires exit_code 0")
        if result_status == "fail" and (not isinstance(exit_code, int) or exit_code == 0):
            issues.append(f"{label}.result: fail requires a non-zero exit_code")
        if result.get("result_ref") is not None:
            issues.extend(_ref_issues(result.get("result_ref"), f"{label}.result.result_ref"))
            if isinstance(node, Mapping) and isinstance(node.get("evidence_refs"), list):
                if result.get("result_ref") not in node["evidence_refs"]:
                    issues.append(
                        f"{label}.result.result_ref must link to packet.node.evidence_refs"
                    )

    cache = packet.get("cache_posture")
    issues.extend(
        _validate_status_object(
            cache,
            label=f"{label}.cache_posture",
            observed_statuses={"hit", "miss", "bypassed", "not_applicable"},
            missing_statuses={"unknown"},
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
            missing_statuses={"missing", "unknown"},
        )
    )
    if isinstance(receipt, Mapping) and receipt.get("receipt_ref") is not None:
        issues.extend(_ref_issues(receipt.get("receipt_ref"), f"{label}.receipt_posture.receipt_ref"))

    first_failure = packet.get("first_failure")
    if isinstance(first_failure, Mapping):
        first_failure_status = first_failure.get("status")
        if first_failure_status not in {"none", "observed", *MISSING_STATES}:
            issues.append(f"{label}.first_failure.status is not admitted")
        if first_failure_status in MISSING_STATES and (
            not isinstance(first_failure.get("reason"), str)
            or not first_failure.get("reason")
        ):
            issues.append(
                f"{label}.first_failure.reason is required for {first_failure_status}"
            )
        if first_failure_status in {"none", "observed"}:
            if (
                first_failure_status == "none"
                and isinstance(result, Mapping)
                and result.get("status") == "fail"
            ):
                issues.append(
                    f"{label}: fail result cannot have first_failure.status=none"
                )
            required_failure_fields = (
                ("status", "time_to_first_failure_ms")
                if first_failure_status == "none"
                else (
                    "status",
                    "node_id",
                    "failure_class",
                    "evidence_ref",
                    "time_to_first_failure_ms",
                )
            )
            _, missing_failure_fields = _required_mapping_keys(
                first_failure,
                required=required_failure_fields,
                label=f"{label}.first_failure",
            )
            issues.extend(missing_failure_fields)
            time_to_first_failure = first_failure.get("time_to_first_failure_ms")
            issues.extend(
                _validate_time_to_first_failure(
                    time_to_first_failure,
                    label=f"{label}.first_failure.time_to_first_failure_ms",
                )
            )
            if first_failure_status == "none" and isinstance(
                time_to_first_failure, Mapping
            ) and time_to_first_failure.get("status") != "not_applicable":
                issues.append(
                    f"{label}.first_failure.time_to_first_failure_ms must be not_applicable when no failure occurred"
                )
            if first_failure_status == "observed" and isinstance(
                time_to_first_failure, Mapping
            ) and time_to_first_failure.get("status") == "not_applicable":
                issues.append(
                    f"{label}.first_failure.time_to_first_failure_ms cannot be not_applicable for an observed failure"
                )
        if first_failure_status == "observed":
            if isinstance(result, Mapping):
                result_status = result.get("status")
                if result_status == "pass":
                    issues.append(
                        f"{label}: pass result cannot have an observed first_failure"
                    )
                if result_status == "fail" and result.get("result_ref") != first_failure.get(
                    "evidence_ref"
                ):
                    issues.append(
                        f"{label}: fail result_ref must match first_failure.evidence_ref"
                    )
            if first_failure.get("failure_class") == "none":
                issues.append(
                    f"{label}.first_failure.failure_class must identify an observed failure"
                )
            if isinstance(node, Mapping) and first_failure.get("node_id") != node.get(
                "node_id"
            ):
                issues.append(
                    f"{label}.first_failure.node_id must match packet.node.node_id"
                )
            issues.extend(
                _ref_issues(first_failure.get("evidence_ref"), f"{label}.first_failure.evidence_ref")
            )
            if isinstance(node, Mapping) and isinstance(node.get("evidence_refs"), list):
                if first_failure.get("evidence_ref") not in node["evidence_refs"]:
                    issues.append(
                        f"{label}.first_failure.evidence_ref must link to packet.node.evidence_refs"
                    )

    cost = packet.get("cost")
    if isinstance(cost, Mapping):
        cost_status = cost.get("status")
        if cost_status == "observed":
            issues.extend(
                _ref_issues(
                    cost.get("measurement_ref"),
                    f"{label}.cost.measurement_ref",
                )
            )
        elif cost_status in MISSING_STATES:
            if not isinstance(cost.get("reason"), str) or not cost["reason"]:
                issues.append(f"{label}.cost.reason is required for {cost_status}")
            if "measurement_ref" in cost:
                issues.append(
                    f"{label}.cost: {cost_status} must not carry a measurement_ref"
                )
        elif cost_status == "not_applicable":
            if any(key in cost for key in ("measurement_ref", "reason")):
                issues.append(
                    f"{label}.cost: not_applicable must not carry a measurement_ref or reason"
                )
        else:
            issues.append(f"{label}.cost.status is not admitted")

    rerun = packet.get("rerun_amplification")
    if isinstance(rerun, Mapping) and rerun.get("status") not in {
        "not_applicable",
        "observed",
        *MISSING_STATES,
    }:
        issues.append(f"{label}.rerun_amplification.status is not admitted")
    if isinstance(rerun, Mapping) and rerun.get("status") == "observed":
        _, missing_rerun_fields = _required_mapping_keys(
            rerun,
            required=(
                "status",
                "attempt_count",
                "distinct_operation_count",
                "repeated_attempt_count",
                "validation_attempt_count",
                "validation_rerun_after_repair_count",
                "attempts_per_distinct_operation",
            ),
            label=f"{label}.rerun_amplification",
        )
        issues.extend(missing_rerun_fields)
        attempts = rerun.get("attempt_count")
        distinct = rerun.get("distinct_operation_count")
        repeated = rerun.get("repeated_attempt_count")
        validation_attempts = rerun.get("validation_attempt_count")
        validation_reruns = rerun.get("validation_rerun_after_repair_count")
        ratio = rerun.get("attempts_per_distinct_operation")
        if not _is_number(ratio) or ratio < 0:
            issues.append(
                f"{label}.rerun_amplification: ratio must be a finite non-negative number"
            )
        for field in (
            "attempt_count",
            "distinct_operation_count",
            "repeated_attempt_count",
            "validation_attempt_count",
            "validation_rerun_after_repair_count",
        ):
            value = rerun.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                issues.append(
                    f"{label}.rerun_amplification.{field} must be a non-negative integer"
                )
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
    if isinstance(rerun, Mapping) and rerun.get("status") in MISSING_STATES:
        if not isinstance(rerun.get("reason"), str) or not rerun.get("reason"):
            issues.append(
                f"{label}.rerun_amplification.reason is required for {rerun.get('status')}"
            )

    coverage = packet.get("source_coverage")
    if isinstance(coverage, Mapping) and coverage.get("status") not in {
        "complete",
        "partial",
        *MISSING_STATES,
    }:
        issues.append(f"{label}.source_coverage.status is not admitted")
    if isinstance(coverage, Mapping) and coverage.get("status") in {"complete", "partial"}:
        _, missing_coverage_fields = _required_mapping_keys(
            coverage,
            required=("status", "expected_owner_count", "observed_owner_count"),
            label=f"{label}.source_coverage",
        )
        issues.extend(missing_coverage_fields)
        expected = coverage.get("expected_owner_count")
        observed = coverage.get("observed_owner_count")
        for field in ("expected_owner_count", "observed_owner_count"):
            value = coverage.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                issues.append(
                    f"{label}.source_coverage.{field} must be a non-negative integer"
                )
        if isinstance(expected, int) and isinstance(observed, int):
            if observed > expected:
                issues.append(f"{label}.source_coverage: observed owners exceed expected owners")
            if coverage.get("status") == "complete" and observed != expected:
                issues.append(f"{label}.source_coverage: complete coverage must have equal counts")
            if coverage.get("status") == "partial" and observed >= expected:
                issues.append(f"{label}.source_coverage: partial coverage must have a gap")
        for ref in coverage.get("missing_owner_repos", []):
            issues.extend(_ref_issues(ref, f"{label}.source_coverage.missing_owner_repos"))
    if isinstance(coverage, Mapping) and coverage.get("status") in MISSING_STATES:
        if not isinstance(coverage.get("reason"), str) or not coverage.get("reason"):
            issues.append(
                f"{label}.source_coverage.reason is required for {coverage.get('status')}"
            )

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
    if isinstance(posture, Mapping):
        if posture.get("freshness") not in {"current", "reference", "stale", "unknown"}:
            issues.append(f"{label}.posture.freshness is not admitted")
        if posture.get("live_state") not in TELEMETRY_POSTURES:
            issues.append(f"{label}.posture.live_state is not admitted")
        if posture.get("privacy") not in {"public", "internal", "sensitive"}:
            issues.append(f"{label}.posture.privacy is not admitted")
        if posture.get("raw_content_included") is not False:
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
    if field == "cost":
        value = packet.get("cost")
        status = value.get("status") if isinstance(value, Mapping) else "missing"
        return str(status) if status in MISSING_STATES | {"not_applicable"} else "observed"
    if field == "first_failure":
        status = packet.get("first_failure", {}).get("status") if isinstance(packet.get("first_failure"), Mapping) else "missing"
        return "observed" if status in {"none", "observed"} else str(status)
    if field == "time_to_first_failure_ms":
        failure = packet.get("first_failure")
        if not isinstance(failure, Mapping):
            return "missing"
        failure_status = failure.get("status")
        if failure_status == "none":
            return "not_applicable"
        time_value = failure.get("time_to_first_failure_ms")
        if isinstance(time_value, Mapping):
            return str(time_value.get("status", "missing"))
        return "missing" if failure_status == "observed" else str(failure_status)
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


def _validate_admission_against_current_owner_input(
    admission: ValidationTelemetryAdmission,
    input_entry: Mapping[str, Any] | None,
    *,
    owner_repo: str,
) -> list[str]:
    """Re-bind an admission to the current explicit owner-port content.

    The receipt is intentionally not an owner signature.  It is a consumer
    barrier: a packet is projectable only while the named owner source,
    complete port content, lane declaration, and packet export still agree.
    """

    label = f"{owner_repo} validation telemetry admission"
    if not isinstance(input_entry, Mapping):
        return [f"{label}: current owner port input is required"]
    if not _is_authoritative_owner_input(owner_repo, input_entry):
        return [
            f"{label}: current owner port input is not an authoritative owner-labelled input"
        ]
    payload = input_entry.get("payload")
    if not isinstance(payload, Mapping):
        return [f"{label}: current owner port payload must be an object"]
    telemetry_port = payload.get("validation_telemetry")
    if not isinstance(telemetry_port, Mapping):
        return [f"{label}: current owner port lacks validation_telemetry"]

    receipt = admission.receipt
    issues: list[str] = []
    issues.extend(
        f"{label}: {issue}"
        for issue in validate_validation_telemetry_port(telemetry_port)
    )
    current_port_ref = input_entry.get("port_ref")
    current_source_ref = input_entry.get("source_ref")
    if receipt.port_ref != current_port_ref:
        issues.append(f"{label}: receipt port_ref does not match current owner input")
    if receipt.owner_source_ref != current_source_ref:
        issues.append(f"{label}: receipt owner_source_ref does not match current owner input")
    if receipt.port_content_digest != _packet_digest(payload):
        issues.append(f"{label}: receipt port content digest does not match current owner input")
    current_telemetry_ref = input_entry.get("telemetry_port_ref") or (
        f"{current_port_ref}#/validation_telemetry"
    )
    if receipt.telemetry_port_ref != current_telemetry_ref:
        issues.append(f"{label}: receipt telemetry_port_ref does not match current owner input")
    issues.extend(
        validate_validation_telemetry_packet_against_port(
            admission.packet,
            telemetry_port,
            expected_owner_repo=owner_repo,
            expected_telemetry_port_ref=(
                current_telemetry_ref if isinstance(current_telemetry_ref, str) else None
            ),
            label=label,
        )
    )
    posture = admission.packet.get("posture")
    live_state = posture.get("live_state") if isinstance(posture, Mapping) else None
    if not isinstance(live_state, str) or _telemetry_export_for_packet(
        telemetry_port,
        packet_ref=receipt.packet_ref,
        packet_live_state=live_state,
        label=label,
    ) is None:
        issues.append(f"{label}: receipt packet_ref is not listed by the current matching export")
    return sorted(set(issues))


def _identity_groups(
    admissions: Sequence[ValidationTelemetryAdmission],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], dict[str, Any]] = {}
    for admission in admissions:
        receipt = admission.receipt
        key = (
            receipt.owner_source_ref,
            receipt.port_content_digest,
            receipt.candidate_digest,
            receipt.environment_digest,
            receipt.live_state,
            receipt.source_revision,
        )
        group = grouped.setdefault(
            key,
            {
                "owner_source_ref": receipt.owner_source_ref,
                "port_content_digest": receipt.port_content_digest,
                "candidate_digest": receipt.candidate_digest,
                "environment_digest": receipt.environment_digest,
                "live_state": receipt.live_state,
                "source_revision": receipt.source_revision,
                "packet_count": 0,
            },
        )
        group["packet_count"] += 1
    return sorted(
        grouped.values(),
        key=lambda group: tuple(
            "" if group[field] is None else str(group[field])
            for field in (
                "owner_source_ref",
                "port_content_digest",
                "candidate_digest",
                "environment_digest",
                "live_state",
                "source_revision",
            )
        ),
    )


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
        entry: dict[str, Any] = {
            "status": status,
            "owner_count": len(owner_repos),
            "expected_owner_count": expected_count,
        }
        if owner_repos:
            entry["owner_repos"] = sorted(owner_repos)
        elif status == "not_applicable":
            entry["reason"] = "all target owners are not applicable to this source family"
        else:
            entry["reason"] = "no owner supplied an admitted validation telemetry packet"
        result[field] = entry
    return result


def build_validation_telemetry_baseline(
    expected_owners: Sequence[Mapping[str, Any]],
    *,
    port_inputs: Mapping[str, Mapping[str, Any]],
    packets: Sequence[ValidationTelemetryAdmission] = (),
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
    admissions_by_owner: dict[str, list[ValidationTelemetryAdmission]] = {}
    seen_observations: set[tuple[str, str]] = set()
    for admission in packets:
        if not isinstance(admission, ValidationTelemetryAdmission):
            raise TypeError(
                "packets must contain ValidationTelemetryAdmission values; "
                "raw packets cannot bypass admission"
            )
        if not admission.is_intact():
            raise ValueError("validation telemetry admission receipt no longer binds packet")
        packet = admission.packet
        owner_repo = packet.get("owner_repo")
        if not isinstance(owner_repo, str) or owner_repo not in owner_repos:
            raise ValueError("validation telemetry admission owner is outside expected_owners")
        current_issues = _validate_admission_against_current_owner_input(
            admission,
            port_inputs.get(owner_repo),
            owner_repo=owner_repo,
        )
        if current_issues:
            raise ValueError("; ".join(current_issues))
        observation_key = (owner_repo, admission.receipt.observation_id)
        if observation_key in seen_observations:
            raise ValueError(
                f"duplicate validation telemetry observation for {owner_repo}: "
                f"{admission.receipt.observation_id}"
            )
        seen_observations.add(observation_key)
        packet_by_owner.setdefault(owner_repo, []).append(packet)
        admissions_by_owner.setdefault(owner_repo, []).append(admission)

    records: list[dict[str, Any]] = []
    for owner in normalized:
        owner_repo = str(owner["repo_id"])
        classification = str(owner.get("classification", "implemented"))
        input_entry = port_inputs.get(owner_repo)
        identity_barrier_status = "not_applicable"
        identity_group_rows: list[dict[str, Any]] = []
        if input_entry is not None and not _is_authoritative_owner_input(
            owner_repo, input_entry
        ):
            port_status = "invalid"
            telemetry_status = "invalid"
            port_ref = (
                input_entry.get("port_ref")
                if isinstance(input_entry, Mapping)
                else None
            )
            telemetry_port_ref = None
            declared_node_count = None
            packet_count = None
            field_coverage = _field_coverage_for_owner(
                owner_repo,
                (),
                reason="explicit owner input lacks an owner identity or source authority",
            )
        elif classification == "routed_to_stronger_owner" and input_entry is None:
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
                        identity_group_rows = _identity_groups(
                            admissions_by_owner.get(owner_repo, [])
                        )
                        if len(identity_group_rows) != 1:
                            identity_barrier_status = "blocked"
                            telemetry_status = "identity_incompatible"
                            field_coverage = _field_coverage_for_owner(
                                owner_repo,
                                (),
                                reason=(
                                    "candidate, environment, port, source, revision, or "
                                    "posture identities were incompatible and were not aggregated"
                                ),
                            )
                        else:
                            identity_barrier_status = "compatible"
                            telemetry_status = (
                                "live"
                                if input_posture == "mixed"
                                and identity_group_rows[0]["live_state"] == "live"
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
                "identity_barrier_status": identity_barrier_status,
                "identity_group_count": len(identity_group_rows),
                "identity_groups": identity_group_rows,
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
        record["telemetry_status"]
        in {"declared_only", "reference", "live", "identity_incompatible"}
        for record in records
    )
    telemetry_packet = sum(
        record["telemetry_status"] in {"reference", "live"} for record in records
    )
    telemetry_gap_repos = [
        record["owner_repo"]
        for record in records
        if record["telemetry_status"] not in {"reference", "live", "not_applicable"}
    ]
    telemetry_incompatible_repos = [
        record["owner_repo"]
        for record in records
        if record["telemetry_status"] == "identity_incompatible"
    ]
    all_not_applicable = bool(records) and all(
        record["telemetry_status"] == "not_applicable" for record in records
    )
    all_owner_not_applicable = bool(records) and all(
        record["port_status"] in {"routed_to_stronger_owner", "not_applicable"}
        for record in records
    )
    owner_coverage_status = (
        "not_applicable"
        if all_owner_not_applicable
        else
        "complete"
        if port_present == expected_count and not port_missing_repos and port_invalid_count == 0
        else "missing"
        if port_present == 0
        else "partial"
    )
    telemetry_coverage_status = (
        "not_applicable"
        if all_not_applicable
        else
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
            "telemetry_incompatible_owner_count": len(telemetry_incompatible_repos),
            "owner_coverage_status": owner_coverage_status,
            "telemetry_coverage_status": telemetry_coverage_status,
            "missing_port_owner_repos": sorted(port_missing_repos),
            "telemetry_gap_owner_repos": sorted(telemetry_gap_repos),
            "identity_barrier_owner_repos": sorted(telemetry_incompatible_repos),
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
