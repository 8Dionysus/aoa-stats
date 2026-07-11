from __future__ import annotations

from collections import defaultdict
from typing import Any


AXES = (
    "boundary_integrity",
    "execution_reliability",
    "change_legibility",
    "review_sharpness",
    "proof_discipline",
    "provenance_hygiene",
    "deep_readiness",
)


class RouteProgressionContractError(ValueError):
    """Raised when a progression receipt needs an undefined semantic mapping."""


def axis_template() -> dict[str, int]:
    return {axis: 0 for axis in AXES}


def _has_numeric_legacy_axis_deltas(payload: dict[str, Any]) -> bool:
    axis_deltas = payload.get("axis_deltas")
    return isinstance(axis_deltas, dict) and any(
        isinstance(axis_deltas.get(axis), int) for axis in AXES if axis in axis_deltas
    )


def _normalized_verdict(payload: dict[str, Any]) -> str:
    verdict = payload.get("verdict")
    return verdict if isinstance(verdict, str) and verdict else "unknown"


def build_route_progression_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        if receipt["event_kind"] != "progression_delta_receipt":
            continue
        payload = receipt["payload"]
        if "axis_delta_summary" in payload and not _has_numeric_legacy_axis_deltas(
            payload
        ):
            raise RouteProgressionContractError(
                f"{receipt['event_id']}: payload carries current semantic "
                "axis_delta_summary without legacy numeric axis_deltas; "
                "aoa-stats does not map semantic movement labels to numeric scores"
            )
        route_ref = payload.get("route_ref") or receipt["session_ref"]
        grouped[route_ref].append(receipt)

    routes: list[dict[str, Any]] = []
    for route_ref in sorted(grouped):
        group = grouped[route_ref]
        latest = max(
            group,
            key=lambda receipt: (receipt["observed_at"], receipt["event_id"]),
        )
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
                "latest_verdict": _normalized_verdict(latest["payload"]),
                "latest_observed_at": latest["observed_at"],
                "cumulative_axis_deltas": cumulative,
                "caution_count": caution_count,
                "evidence_ref_count": sum(
                    len(receipt["evidence_refs"]) for receipt in group
                ),
            }
        )

    return {
        "schema_version": "aoa_stats_route_progression_summary_v1",
        "generated_from": source,
        "routes": routes,
    }
