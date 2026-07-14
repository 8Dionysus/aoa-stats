from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .measurement import (
    evidence_identity,
    semantic_identity,
    validate_packet_semantics,
)
from .schema_validation import schema_issues


PACKET_READ_RESULT_VERSION = "aoa_stats_packet_read_result_v1"
ACCESS_AUTHORITY_CEILING = (
    "Compatibility only; this result does not attest owner truth, evidence "
    "validity, freshness, proof, or permission to act."
)


def build_packet_read_result(
    contract: Mapping[str, Any],
    packet: Mapping[str, Any],
    *,
    contract_schema: Mapping[str, Any],
    packet_schema: Mapping[str, Any],
) -> dict[str, Any]:
    """Check one packet and return a transport-neutral compatibility result."""

    contract_shape_issues = schema_issues(
        contract_schema,
        contract,
        label="contract",
    )
    packet_shape_issues = schema_issues(
        packet_schema,
        packet,
        label="packet",
    )
    issues = [*contract_shape_issues, *packet_shape_issues]
    if not issues:
        issues.extend(
            f"semantic: {issue}"
            for issue in validate_packet_semantics(contract, packet)
        )

    compatible = not issues
    owner_ceiling = contract.get("authority_ceiling") if compatible else None
    return {
        "schema_version": PACKET_READ_RESULT_VERSION,
        "truth_status": "compatibility_check_only",
        "compatible": compatible,
        "measurement_id": (
            packet.get("measurement_id")
            if isinstance(packet.get("measurement_id"), str)
            else None
        ),
        "contract_version": (
            packet.get("contract_version")
            if isinstance(packet.get("contract_version"), str)
            else None
        ),
        "semantic_identity": semantic_identity(packet) if compatible else None,
        "evidence_identity": evidence_identity(packet) if compatible else None,
        "owner_authority_ceiling": owner_ceiling,
        "access_authority_ceiling": ACCESS_AUTHORITY_CEILING,
        "issues": issues,
    }
