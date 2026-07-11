from __future__ import annotations

import json

from pathlib import Path
from typing import Any

SURFACE_STRENGTH_MODEL_REF = "docs/SURFACE_STRENGTH_MODEL.md"
SUMMARY_SURFACE_CATALOG_ARTIFACT_IDENTITY = {
    "artifact_class": "derived_observability_readmodel_catalog",
    "surface_state": "public_generated_summary_surface_catalog",
    "owner_repo": "aoa-stats",
    "authority_ref": "docs/ARCHITECTURE.md",
    "producer": "scripts/build_views.py via aoa_stats_builder.surface_catalog from source-owned receipts and bounded examples",
    "consumer_expectation": (
        "consumers verify schema_version, generated_from, validation_refs, "
        "surface strength refs, owner truth inputs, and build_views --check "
        "before using catalog entries as observability hints"
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
    "activation_condition",
    "authority_ceiling",
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
    expected_fields = (
        ACTIVE_SOURCE_FIELDS if lifecycle == "active" else DEFERRED_SOURCE_FIELDS
    )
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
    routes = profile.get("mechanic_routes")
    if (
        not isinstance(routes, list)
        or not routes
        or not all(
            isinstance(route, str) and route.startswith("mechanics/")
            for route in routes
        )
    ):
        raise SurfaceProfileError(
            f"{path}: mechanic_routes must be a non-empty mechanics path list"
        )
    if len(routes) != len(set(routes)):
        raise SurfaceProfileError(f"{path}: mechanic_routes must be unique")
    if lifecycle == "active":
        order = profile.get("catalog_order")
        if not isinstance(order, int) or isinstance(order, bool) or order < 1:
            raise SurfaceProfileError(
                f"{path}: catalog_order must be a positive integer"
            )


def load_surface_profiles(
    profile_root: Path = PROFILE_ROOT,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Load, validate, and deterministically order authored surface profiles."""

    active_paths = sorted((profile_root / "active").glob("*.profile.json"))
    deferred_paths = sorted((profile_root / "deferred").glob("*.profile.json"))
    if not active_paths:
        raise SurfaceProfileError(
            f"no active surface profiles found under {profile_root / 'active'}"
        )

    active: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
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
            raise SurfaceProfileError(f"duplicate surface catalog order: {order}")
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

    active.sort(key=lambda profile: profile["catalog_order"])
    deferred.sort(key=lambda profile: profile["name"])
    return active, deferred


def public_surface_profiles(
    profile_root: Path = PROFILE_ROOT,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Project authored profiles into the unchanged public catalog entry shapes."""

    active, deferred = load_surface_profiles(profile_root)
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
    """Return every active profile output basename in catalog order."""

    active, _ = load_surface_profiles(profile_root)
    return tuple(Path(profile["surface_ref"]).name for profile in active)


def live_profile_surface_output_names(
    profile_root: Path = PROFILE_ROOT,
) -> tuple[str, ...]:
    """Return live-materializable active profile outputs in catalog order."""

    active, _ = load_surface_profiles(profile_root)
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
