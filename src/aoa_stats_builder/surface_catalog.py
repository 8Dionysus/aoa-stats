from __future__ import annotations

import json

from pathlib import Path
from typing import Any

SURFACE_STRENGTH_MODEL_REF = "stats/surface-catalog/SURFACE_STRENGTH_MODEL.md"
SUMMARY_SURFACE_CATALOG_ARTIFACT_IDENTITY = {
    "artifact_class": "derived_observability_readmodel_catalog",
    "surface_state": "public_generated_summary_surface_catalog",
    "owner_repo": "aoa-stats",
    "authority_ref": "docs/ARCHITECTURE.md",
    "producer": "scripts/build_views.py via aoa_stats_builder.surface_catalog from source-owned receipts and bounded examples",
    "consumer_expectation": (
        "consumers verify schema_version, generated_from, validation_refs, "
        "surface strength refs, owner truth inputs, deferred activation gaps, "
        "and build_views --check before using catalog entries as observability "
        "hints"
    ),
    "privacy_boundary": (
        "public derived summary refs only; no raw private receipts, session "
        "captures, owner payload bodies, or runtime-local evidence"
    ),
    "content_identity": (
        "generated/summary_surface_catalog.min.json rebuilt from the active "
        "receipt feed and compared by build_views --check"
    ),
    "abi_epoch": "aoa_stats_summary_surface_catalog_v2",
    "contract_version": "summary-surface-catalog.schema.json@aoa_stats_summary_surface_catalog_v2#artifact_identity",
    "trust_layer": ["abi_contract_signature", "w3c_prov_lineage"],
    "verification": [
        "python scripts/build_views.py --check",
        "python scripts/validate_repo.py",
        "python -m pytest -q tests/test_summary_surface_catalog.py",
    ],
    "action": "ADD_CONSUMER_EXPECTATION",
}


PROFILE_SCHEMA_VERSION = "aoa_stats_surface_profile_source_v1"
PROFILE_ROOT = Path(__file__).resolve().parents[2] / "stats" / "read-models"

PUBLIC_ACTIVE_FIELDS = (
    "name",
    "surface_ref",
    "schema_ref",
    "primary_question",
    "derivation_rule",
    "input_posture",
    "owner_truth_inputs",
    "authority_ceiling",
    "consumer_risk",
    "live_state_capable",
)
PUBLIC_DEFERRED_FIELDS = (
    "name",
    "status",
    "contract_ref",
    "schema_ref",
    "input_posture",
    "owner_truth_inputs",
    "activation_condition",
    "activation_gaps",
    "authority_ceiling",
    "consumer_risk",
)
ACTIVE_SOURCE_FIELDS = frozenset(
    (
        "schema_version",
        "catalog_order",
        "lifecycle",
        "mechanic_routes",
        *PUBLIC_ACTIVE_FIELDS,
    )
)
DEFERRED_SOURCE_FIELDS = frozenset(
    ("schema_version", "lifecycle", "mechanic_routes", *PUBLIC_DEFERRED_FIELDS)
)
RETIRED_SOURCE_FIELDS = frozenset(
    (
        "schema_version",
        "lifecycle",
        "name",
        "former_catalog_order",
        "retired_surface_ref",
        "schema_ref",
        "retired_on",
        "retirement_reason",
        "replacement_ref",
        "cleanup_scopes",
        "consumer_return_routes",
        "decision_ref",
        "former_mechanic_routes",
    )
)
RETIRED_CLEANUP_SCOPES = frozenset(
    (
        "committed_output",
        "summary_surface_catalog",
        "managed_live_state",
        "consumer_hints",
    )
)


class SurfaceProfileError(ValueError):
    """Raised when an authored stats surface profile is malformed."""


def _load_profile(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SurfaceProfileError(f"surface profile is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SurfaceProfileError(
            f"invalid surface profile JSON: {path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise SurfaceProfileError(f"surface profile must be a JSON object: {path}")
    return payload


def _validate_profile(profile: dict[str, Any], *, path: Path, lifecycle: str) -> None:
    expected_fields = {
        "active": ACTIVE_SOURCE_FIELDS,
        "deferred": DEFERRED_SOURCE_FIELDS,
        "retired": RETIRED_SOURCE_FIELDS,
    }[lifecycle]
    if set(profile) != expected_fields:
        missing = sorted(expected_fields - set(profile))
        extra = sorted(set(profile) - expected_fields)
        raise SurfaceProfileError(
            f"{path}: profile fields do not match {lifecycle} contract; "
            f"missing={missing!r}, extra={extra!r}"
        )
    if profile.get("schema_version") != PROFILE_SCHEMA_VERSION:
        raise SurfaceProfileError(f"{path}: wrong schema_version")
    if profile.get("lifecycle") != lifecycle:
        raise SurfaceProfileError(f"{path}: lifecycle must be {lifecycle!r}")
    name = profile.get("name")
    if not isinstance(name, str) or not name:
        raise SurfaceProfileError(f"{path}: name must be a non-empty string")
    if path.name != f"{name}.profile.json":
        raise SurfaceProfileError(f"{path}: filename must match profile name {name!r}")
    routes_field = (
        "former_mechanic_routes" if lifecycle == "retired" else "mechanic_routes"
    )
    routes = profile.get(routes_field)
    if (
        not isinstance(routes, list)
        or not routes
        or not all(
            isinstance(route, str) and route.startswith("mechanics/")
            for route in routes
        )
    ):
        raise SurfaceProfileError(
            f"{path}: {routes_field} must be a non-empty mechanics path list"
        )
    if len(routes) != len(set(routes)):
        raise SurfaceProfileError(f"{path}: {routes_field} must be unique")
    if lifecycle == "active":
        order = profile.get("catalog_order")
        if not isinstance(order, int) or isinstance(order, bool) or order < 1:
            raise SurfaceProfileError(
                f"{path}: catalog_order must be a positive integer"
            )
    if lifecycle == "deferred":
        for field in ("input_posture", "activation_condition", "authority_ceiling"):
            value = profile.get(field)
            if not isinstance(value, str) or not value.strip():
                raise SurfaceProfileError(f"{path}: {field} must be non-empty")
        for field in ("owner_truth_inputs", "activation_gaps"):
            values = profile.get(field)
            if (
                not isinstance(values, list)
                or not values
                or not all(
                    isinstance(value, str) and bool(value.strip())
                    for value in values
                )
                or len(values) != len(set(values))
            ):
                raise SurfaceProfileError(
                    f"{path}: {field} must be a non-empty unique string list"
                )
        if profile.get("consumer_risk") not in {"low", "medium", "high"}:
            raise SurfaceProfileError(
                f"{path}: consumer_risk must be low, medium, or high"
            )
    if lifecycle == "retired":
        former_order = profile.get("former_catalog_order")
        if (
            not isinstance(former_order, int)
            or isinstance(former_order, bool)
            or former_order < 1
        ):
            raise SurfaceProfileError(
                f"{path}: former_catalog_order must be a positive integer"
            )
        retired_surface_ref = profile.get("retired_surface_ref")
        if not isinstance(retired_surface_ref, str) or not retired_surface_ref:
            raise SurfaceProfileError(
                f"{path}: retired_surface_ref must be a non-empty string"
            )
        if Path(retired_surface_ref).name != f"{name}.min.json":
            raise SurfaceProfileError(
                f"{path}: retired_surface_ref must match profile name {name!r}"
            )
        cleanup_scopes = profile.get("cleanup_scopes")
        if (
            not isinstance(cleanup_scopes, list)
            or len(cleanup_scopes) != len(RETIRED_CLEANUP_SCOPES)
            or set(cleanup_scopes) != set(RETIRED_CLEANUP_SCOPES)
        ):
            raise SurfaceProfileError(
                f"{path}: cleanup_scopes must name the complete retired cleanup set"
            )
        for field in (
            "schema_ref",
            "retired_on",
            "retirement_reason",
            "decision_ref",
        ):
            if not isinstance(profile.get(field), str) or not profile[field].strip():
                raise SurfaceProfileError(f"{path}: {field} must be non-empty")
        consumer_routes = profile.get("consumer_return_routes")
        if (
            not isinstance(consumer_routes, list)
            or not all(isinstance(route, str) and route for route in consumer_routes)
            or len(consumer_routes) != len(set(consumer_routes))
        ):
            raise SurfaceProfileError(
                f"{path}: consumer_return_routes must be a unique string list"
            )
        replacement_ref = profile.get("replacement_ref")
        if replacement_ref is not None and (
            not isinstance(replacement_ref, str) or not replacement_ref.strip()
        ):
            raise SurfaceProfileError(
                f"{path}: replacement_ref must be null or a non-empty string"
            )


def load_surface_profiles(
    profile_root: Path = PROFILE_ROOT,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    """Load, validate, and deterministically order authored surface profiles."""

    active_paths = sorted((profile_root / "active").glob("*.profile.json"))
    deferred_paths = sorted((profile_root / "deferred").glob("*.profile.json"))
    retired_paths = sorted((profile_root / "retired").glob("*.profile.json"))
    if not active_paths:
        raise SurfaceProfileError(
            f"no active surface profiles found under {profile_root / 'active'}"
        )

    active: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
    retired: list[dict[str, Any]] = []
    seen_names: set[str] = set()
    seen_orders: set[int] = set()

    for profile_path in active_paths:
        profile = _load_profile(profile_path)
        _validate_profile(profile, path=profile_path, lifecycle="active")
        name = profile["name"]
        order = profile["catalog_order"]
        if name in seen_names:
            raise SurfaceProfileError(f"duplicate surface profile name: {name}")
        if order in seen_orders:
            raise SurfaceProfileError(f"duplicate surface catalog slot: {order}")
        seen_names.add(name)
        seen_orders.add(order)
        active.append(profile)

    for profile_path in deferred_paths:
        profile = _load_profile(profile_path)
        _validate_profile(profile, path=profile_path, lifecycle="deferred")
        name = profile["name"]
        if name in seen_names:
            raise SurfaceProfileError(f"duplicate surface profile name: {name}")
        seen_names.add(name)
        deferred.append(profile)

    for profile_path in retired_paths:
        profile = _load_profile(profile_path)
        _validate_profile(profile, path=profile_path, lifecycle="retired")
        name = profile["name"]
        if name in seen_names:
            raise SurfaceProfileError(f"duplicate surface profile name: {name}")
        former_order = profile["former_catalog_order"]
        if former_order in seen_orders:
            raise SurfaceProfileError(
                f"duplicate surface catalog slot: {former_order}"
            )
        seen_names.add(name)
        seen_orders.add(former_order)
        retired.append(profile)

    managed_profiles = [
        *((profile, "surface_ref") for profile in active),
        *((profile, "retired_surface_ref") for profile in retired),
    ]
    managed_output_names: set[str] = set()
    for profile, ref_field in managed_profiles:
        output_name = Path(profile[ref_field]).name
        if output_name in managed_output_names:
            raise SurfaceProfileError(
                f"duplicate managed surface output name: {output_name}"
            )
        managed_output_names.add(output_name)

    active.sort(key=lambda profile: profile["catalog_order"])
    deferred.sort(key=lambda profile: profile["name"])
    retired.sort(key=lambda profile: profile["name"])
    return active, deferred, retired


def public_surface_profiles(
    profile_root: Path = PROFILE_ROOT,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Project authored profiles into their public catalog entry shapes."""

    active, deferred, _ = load_surface_profiles(profile_root)
    public_active = [
        {field: profile[field] for field in PUBLIC_ACTIVE_FIELDS} for profile in active
    ]
    public_deferred = [
        {field: profile[field] for field in PUBLIC_DEFERRED_FIELDS}
        for profile in deferred
    ]
    return public_active, public_deferred


def all_profile_surface_output_names(
    profile_root: Path = PROFILE_ROOT,
) -> tuple[str, ...]:
    """Return active outputs plus retired tombstones for stale cleanup."""

    active, _, retired = load_surface_profiles(profile_root)
    return (
        *(Path(profile["surface_ref"]).name for profile in active),
        *(Path(profile["retired_surface_ref"]).name for profile in retired),
    )


def retired_profile_surface_output_names(
    profile_root: Path = PROFILE_ROOT,
) -> tuple[str, ...]:
    """Return retired output basenames that remain cleanup tombstones."""

    _, _, retired = load_surface_profiles(profile_root)
    return tuple(Path(profile["retired_surface_ref"]).name for profile in retired)


def live_profile_surface_output_names(
    profile_root: Path = PROFILE_ROOT,
) -> tuple[str, ...]:
    """Return live-materializable active profile outputs in catalog order."""

    active, _, _ = load_surface_profiles(profile_root)
    return tuple(
        Path(profile["surface_ref"]).name
        for profile in active
        if profile["live_state_capable"] is True
    )


def build_summary_surface_catalog(
    source: dict[str, Any], *, available_output_names: set[str] | None = None
) -> dict[str, Any]:
    surfaces, deferred_surfaces = public_surface_profiles()
    if available_output_names is not None:
        surfaces = [
            surface
            for surface in surfaces
            if Path(surface["surface_ref"]).name in available_output_names
        ]
    return {
        "schema_version": "aoa_stats_summary_surface_catalog_v2",
        "schema_ref": "schemas/summary-surface-catalog.schema.json",
        "owner_repo": "aoa-stats",
        "surface_kind": "runtime_surface",
        "authority_ref": "docs/ARCHITECTURE.md",
        "artifact_identity": SUMMARY_SURFACE_CATALOG_ARTIFACT_IDENTITY,
        "surface_strength_model_ref": SURFACE_STRENGTH_MODEL_REF,
        "generated_from": source,
        "validation_refs": [
            "scripts/build_views.py",
            "scripts/validate_repo.py",
            "tests/test_summary_surface_catalog.py",
        ],
        "deferred_contract_surfaces": deferred_surfaces,
        "surfaces": surfaces,
    }
