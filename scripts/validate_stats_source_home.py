#!/usr/bin/env python3
"""Validate the aoa-stats source home, authored profiles, and mechanics crosswalk."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, SchemaError

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder.surface_catalog import (  # noqa: E402
    SurfaceProfileError,
    load_surface_profiles,
    public_surface_profiles,
)

STATS_ROOT = Path("stats")
MANIFEST_PATH = STATS_ROOT / "source_home.manifest.json"
PROFILE_SCHEMA_PATH = STATS_ROOT / "read-models" / "surface-profile.schema.json"
TOPOLOGY_PATH = Path("mechanics/topology.json")

EXPECTED_FAMILIES = {
    "intake_contract": "stats/intake-contract",
    "read_models": "stats/read-models",
    "operation_contracts": "stats/operation-contracts",
    "surface_catalog": "stats/surface-catalog",
}
EXPECTED_BRANCH_ENTRIES = {
    "stats/intake-contract": {
        "AGENTS.md",
        "README.md",
        "RECEIPT_ABI.md",
        "event-kind-registry.json",
        "examples",
    },
    "stats/read-models": {
        "AGENTS.md",
        "README.md",
        "surface-profile.schema.json",
        "active",
        "deferred",
    },
    "stats/operation-contracts": {
        "AGENTS.md",
        "README.md",
    },
    "stats/surface-catalog": {
        "AGENTS.md",
        "README.md",
        "CODEX_MCP.md",
        "CONSUMER_REGROUNDING.md",
    },
}
REQUIRED_ROOT_FILES = {"AGENTS.md", "README.md", "source_home.manifest.json"}
REQUIRED_ROUTE_FIELDS = (
    "source_routes",
    "public_contract_routes",
    "implementation_routes",
    "validator_routes",
)
OPTIONAL_ROUTE_FIELDS = ("generated_routes", "read_only_access_routes")
EXPECTED_ACTIVE_PROFILE_COUNT = 25
EXPECTED_DEFERRED_PROFILE_COUNT = 1
INTAKE_FIXTURE = Path(
    "stats/intake-contract/examples/session_harvest_family.receipts.example.json"
)


def _load_object(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"{path.as_posix()}: file is missing"
    except json.JSONDecodeError as exc:
        return None, f"{path.as_posix()}: invalid JSON: {exc}"
    if not isinstance(payload, dict):
        return None, f"{path.as_posix()}: must be a JSON object"
    return payload, None


def _entries(path: Path) -> set[str]:
    return {entry.name for entry in path.iterdir()}


def _string_list(value: object, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(isinstance(item, str) and item for item in value)
    )


def _mechanic_path_objects(
    value: object, *, context: str, issues: list[str]
) -> list[str]:
    if not isinstance(value, list) or not value:
        issues.append(f"{context}: mechanic_routes must be a non-empty list")
        return []
    paths: list[str] = []
    for route in value:
        if not isinstance(route, dict):
            issues.append(f"{context}: every mechanic route must be an object")
            continue
        package = route.get("package")
        part = route.get("part")
        path = route.get("path")
        if not all(isinstance(item, str) and item for item in (package, part, path)):
            issues.append(
                f"{context}: mechanic route must name package, part, and path"
            )
            continue
        expected = f"mechanics/{package}/parts/{part}"
        if path != expected:
            issues.append(
                f"{context}: mechanic route path must be {expected!r}, found {path!r}"
            )
            continue
        paths.append(path)
    if len(paths) != len(set(paths)):
        issues.append(f"{context}: mechanic_routes contain duplicates")
    return paths


def _topology_crosswalks(topology: dict[str, Any]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    entries = topology.get("source_family_crosswalks")
    if not isinstance(entries, list):
        return result
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        family = entry.get("stats_source_family_ref")
        routes = entry.get("mechanic_part_refs")
        if isinstance(family, str) and _string_list(routes):
            result[family] = set(routes)
    return result


def _part_back_references(topology: dict[str, Any]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    packages = topology.get("active_packages")
    if not isinstance(packages, list):
        return result
    for package in packages:
        if not isinstance(package, dict) or not isinstance(package.get("path"), str):
            continue
        parts = package.get("active_part_routes")
        if not isinstance(parts, list):
            continue
        for part in parts:
            if not isinstance(part, dict) or not isinstance(part.get("path"), str):
                continue
            family_refs = part.get("stats_source_family_refs")
            if not _string_list(family_refs):
                single_ref = part.get("stats_source_family_ref")
                family_refs = (
                    [single_ref] if isinstance(single_ref, str) and single_ref else []
                )
            route = f"mechanics/{package['path']}/parts/{part['path']}"
            for family in family_refs:
                result.setdefault(family, set()).add(route)
    return result


def _validate_profile_schema(
    repo_root: Path,
    active_paths: list[Path],
    deferred_paths: list[Path],
    issues: list[str],
) -> None:
    schema, error = _load_object(repo_root / PROFILE_SCHEMA_PATH)
    if error:
        issues.append(error)
        return
    assert schema is not None
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        issues.append(
            f"{PROFILE_SCHEMA_PATH.as_posix()}: invalid JSON schema: {exc.message}"
        )
        return
    validator = Draft202012Validator(schema)
    for path in [*active_paths, *deferred_paths]:
        profile, profile_error = _load_object(path)
        if profile_error:
            issues.append(profile_error)
            continue
        assert profile is not None
        for failure in validator.iter_errors(profile):
            location = ".".join(str(part) for part in failure.absolute_path)
            suffix = f":{location}" if location else ""
            rel = path.relative_to(repo_root).as_posix()
            issues.append(f"{rel}{suffix}: {failure.message}")


def _validate_stats_json_allowlist(
    repo_root: Path,
    active_paths: list[Path],
    deferred_paths: list[Path],
    issues: list[str],
) -> None:
    expected = {
        MANIFEST_PATH.as_posix(),
        PROFILE_SCHEMA_PATH.as_posix(),
        "stats/intake-contract/event-kind-registry.json",
        INTAKE_FIXTURE.as_posix(),
        *[path.relative_to(repo_root).as_posix() for path in active_paths],
        *[path.relative_to(repo_root).as_posix() for path in deferred_paths],
    }
    actual = {
        path.relative_to(repo_root).as_posix()
        for path in (repo_root / STATS_ROOT).rglob("*.json")
    }
    if actual != expected:
        issues.append(
            "stats/: JSON source allowlist mismatch; "
            f"missing={sorted(expected - actual)!r}, unexpected={sorted(actual - expected)!r}"
        )
    forbidden_python = sorted(
        path.relative_to(repo_root).as_posix()
        for path in (repo_root / STATS_ROOT).rglob("*.py")
    )
    if forbidden_python:
        issues.append(
            f"stats/: Python implementation is forbidden: {forbidden_python!r}"
        )
    forbidden_dirs = sorted(
        path.relative_to(repo_root).as_posix()
        for name in ("generated", "state")
        for path in (repo_root / STATS_ROOT).rglob(name)
        if path.is_dir()
    )
    if forbidden_dirs:
        issues.append(
            f"stats/: generated or runtime-state directories are forbidden: {forbidden_dirs!r}"
        )


def _validate_profiles(
    repo_root: Path,
    manifest_family: dict[str, Any] | None,
    *,
    require_mechanics: bool,
    issues: list[str],
) -> set[str]:
    active_paths = sorted(
        (repo_root / "stats/read-models/active").glob("*.profile.json")
    )
    deferred_paths = sorted(
        (repo_root / "stats/read-models/deferred").glob("*.profile.json")
    )
    _validate_profile_schema(repo_root, active_paths, deferred_paths, issues)
    _validate_stats_json_allowlist(repo_root, active_paths, deferred_paths, issues)

    if len(active_paths) != EXPECTED_ACTIVE_PROFILE_COUNT:
        issues.append(
            "stats/read-models/active: expected "
            f"{EXPECTED_ACTIVE_PROFILE_COUNT} profiles, found {len(active_paths)}"
        )
    if len(deferred_paths) != EXPECTED_DEFERRED_PROFILE_COUNT:
        issues.append(
            "stats/read-models/deferred: expected "
            f"{EXPECTED_DEFERRED_PROFILE_COUNT} profile, found {len(deferred_paths)}"
        )

    try:
        active, deferred = load_surface_profiles(repo_root / "stats/read-models")
        public_active, public_deferred = public_surface_profiles(
            repo_root / "stats/read-models"
        )
    except SurfaceProfileError as exc:
        issues.append(f"stats/read-models: {exc}")
        return set()

    if [profile["catalog_order"] for profile in active] != list(
        range(1, len(active) + 1)
    ):
        issues.append(
            "stats/read-models/active: catalog_order must be contiguous from 1"
        )

    catalog, catalog_error = _load_object(
        repo_root / "generated/summary_surface_catalog.min.json"
    )
    if catalog_error:
        issues.append(catalog_error)
    else:
        assert catalog is not None
        if catalog.get("surfaces") != public_active:
            issues.append(
                "generated/summary_surface_catalog.min.json: active surfaces do not match authored profiles"
            )
        if catalog.get("deferred_contract_surfaces") != public_deferred:
            issues.append(
                "generated/summary_surface_catalog.min.json: deferred surfaces do not match authored profiles"
            )

    schema_routes: list[str] = []
    generated_routes: list[str] = []
    mechanic_routes: list[str] = []
    for profile in [*active, *deferred]:
        schema_ref = profile["schema_ref"]
        if schema_ref not in schema_routes:
            schema_routes.append(schema_ref)
        if not (repo_root / schema_ref).is_file():
            issues.append(
                f"stats/read-models: profile schema route is missing: {schema_ref}"
            )
        surface_ref = profile.get("surface_ref")
        if isinstance(surface_ref, str):
            if surface_ref not in generated_routes:
                generated_routes.append(surface_ref)
            if not (repo_root / surface_ref).is_file():
                issues.append(
                    f"stats/read-models: profile output route is missing: {surface_ref}"
                )
        contract_ref = profile.get("contract_ref")
        if isinstance(contract_ref, str) and not (repo_root / contract_ref).is_file():
            issues.append(
                f"stats/read-models: deferred contract route is missing: {contract_ref}"
            )
        for route in profile["mechanic_routes"]:
            if route not in mechanic_routes:
                mechanic_routes.append(route)
            if require_mechanics:
                part_root = repo_root / route
                if not part_root.is_dir():
                    issues.append(
                        f"stats/read-models: mechanic route is missing: {route}"
                    )
                    continue
                for required in ("CONTRACT.md", "VALIDATION.md"):
                    if not (part_root / required).is_file():
                        issues.append(
                            f"stats/read-models: mechanic route lacks {required}: {route}"
                        )

    if manifest_family is None:
        return set(mechanic_routes)
    if manifest_family.get("public_contract_routes") != schema_routes:
        issues.append(
            "stats/read-models: manifest public_contract_routes must match profile schema refs"
        )
    if manifest_family.get("generated_routes") != generated_routes:
        issues.append(
            "stats/read-models: manifest generated_routes must match active profile outputs"
        )
    manifest_mechanics = _mechanic_path_objects(
        manifest_family.get("mechanic_routes"),
        context="stats/read-models",
        issues=issues,
    )
    if manifest_mechanics != mechanic_routes:
        issues.append(
            "stats/read-models: manifest mechanic_routes must match profile mechanic_routes"
        )
    return set(mechanic_routes)


def validate(
    repo_root: Path = REPO_ROOT,
    *,
    require_mechanics: bool = True,
) -> list[str]:
    repo_root = repo_root.resolve()
    stats_root = repo_root / STATS_ROOT
    issues: list[str] = []

    if not stats_root.is_dir():
        return ["stats/: directory is missing"]

    manifest, manifest_error = _load_object(repo_root / MANIFEST_PATH)
    if manifest_error:
        return [manifest_error]
    assert manifest is not None

    if manifest.get("schema_version") != "aoa_stats_source_home_v2":
        issues.append(
            "stats/source_home.manifest.json: schema_version must be aoa_stats_source_home_v2"
        )
    if manifest.get("owner_repo") != "aoa-stats":
        issues.append("stats/source_home.manifest.json: owner_repo must be aoa-stats")
    if manifest.get("home") != "stats/":
        issues.append("stats/source_home.manifest.json: home must be stats/")
    if manifest.get("status") != "active_source_home":
        issues.append(
            "stats/source_home.manifest.json: status must be active_source_home"
        )
    if not isinstance(manifest.get("role"), str) or not manifest["role"].strip():
        issues.append("stats/source_home.manifest.json: role must be non-empty")
    if not _string_list(manifest.get("home_rules")):
        issues.append(
            "stats/source_home.manifest.json: home_rules must be a non-empty string list"
        )

    expected_root_entries = REQUIRED_ROOT_FILES | {
        path.removeprefix("stats/") for path in EXPECTED_FAMILIES.values()
    }
    actual_root_entries = _entries(stats_root)
    if actual_root_entries != expected_root_entries:
        issues.append(
            "stats/: entries must match the source-home branches; "
            f"expected={sorted(expected_root_entries)!r}, found={sorted(actual_root_entries)!r}"
        )

    for branch_path, expected_entries in EXPECTED_BRANCH_ENTRIES.items():
        branch_root = repo_root / branch_path
        if not branch_root.is_dir():
            issues.append(f"{branch_path}: branch directory is missing")
        elif _entries(branch_root) != expected_entries:
            issues.append(
                f"{branch_path}: entries must be exactly {sorted(expected_entries)!r}, "
                f"found {sorted(_entries(branch_root))!r}"
            )

    branches = manifest.get("branches")
    if not isinstance(branches, list):
        issues.append("stats/source_home.manifest.json: branches must be a list")
        branches = []
    branch_by_id: dict[str, dict[str, Any]] = {}
    for branch in branches:
        if not isinstance(branch, dict) or not isinstance(branch.get("id"), str):
            issues.append(
                "stats/source_home.manifest.json: every branch must name an id"
            )
            continue
        branch_id = branch["id"]
        if branch_id in branch_by_id:
            issues.append(
                f"stats/source_home.manifest.json: duplicate branch id {branch_id!r}"
            )
        branch_by_id[branch_id] = branch
    if set(branch_by_id) != set(EXPECTED_FAMILIES):
        issues.append(
            "stats/source_home.manifest.json: branch set must be "
            f"{sorted(EXPECTED_FAMILIES)!r}; found {sorted(branch_by_id)!r}"
        )

    families = manifest.get("families")
    if not isinstance(families, list):
        issues.append("stats/source_home.manifest.json: families must be a list")
        families = []
    family_by_id: dict[str, dict[str, Any]] = {}
    source_crosswalks: dict[str, set[str]] = {}
    for family in families:
        if not isinstance(family, dict) or not isinstance(family.get("id"), str):
            issues.append(
                "stats/source_home.manifest.json: every family must name an id"
            )
            continue
        family_id = family["id"]
        if family_id in family_by_id:
            issues.append(
                f"stats/source_home.manifest.json: duplicate family id {family_id!r}"
            )
        family_by_id[family_id] = family

        expected_path = EXPECTED_FAMILIES.get(family_id)
        if expected_path is None:
            issues.append(
                f"stats/source_home.manifest.json: unexpected family id {family_id!r}"
            )
            continue
        expected_owner = f"{expected_path}/AGENTS.md"
        if family.get("branch") != family_id:
            issues.append(f"{expected_path}: family branch must be {family_id!r}")
        if family.get("path") != expected_path:
            issues.append(f"{expected_path}: family path must be {expected_path!r}")
        if family.get("owner_surface") != expected_owner:
            issues.append(f"{expected_path}: owner_surface must be {expected_owner!r}")
        for field in ("source_kind", "meaning", "authority_ceiling"):
            if not isinstance(family.get(field), str) or not family[field].strip():
                issues.append(f"{expected_path}: {field} must be non-empty")

        branch = branch_by_id.get(family_id)
        if branch is not None:
            if branch.get("path") != expected_path:
                issues.append(
                    f"{expected_path}: branch path does not match family path"
                )
            if branch.get("owner_surface") != expected_owner:
                issues.append(
                    f"{expected_path}: branch owner_surface does not match family owner"
                )
            if branch.get("families") != [family_id]:
                issues.append(
                    f"{expected_path}: branch must list only its matching family"
                )
            for field in ("role", "authority_ceiling"):
                if not isinstance(branch.get(field), str) or not branch[field].strip():
                    issues.append(f"{expected_path}: branch {field} must be non-empty")

        for field in REQUIRED_ROUTE_FIELDS:
            routes = family.get(field)
            if not _string_list(routes):
                issues.append(
                    f"{expected_path}: {field} must be a non-empty string list"
                )
                continue
            if len(routes) != len(set(routes)):
                issues.append(f"{expected_path}: {field} contains duplicate routes")
            for route in routes:
                if not (repo_root / route).exists():
                    issues.append(f"{expected_path}: {field} route is missing: {route}")

        for field in OPTIONAL_ROUTE_FIELDS:
            routes = family.get(field, [])
            if not _string_list(routes, allow_empty=True):
                issues.append(f"{expected_path}: {field} must be a string list")
                continue
            if len(routes) != len(set(routes)):
                issues.append(f"{expected_path}: {field} contains duplicate routes")
            for route in routes:
                if not (repo_root / route).exists():
                    issues.append(f"{expected_path}: {field} route is missing: {route}")

        source_routes = family.get("source_routes")
        if _string_list(source_routes):
            for required in (
                f"{expected_path}/AGENTS.md",
                f"{expected_path}/README.md",
            ):
                if required not in source_routes:
                    issues.append(
                        f"{expected_path}: source_routes must include {required}"
                    )
        if not _string_list(family.get("stop_lines")):
            issues.append(
                f"{expected_path}: stop_lines must be a non-empty string list"
            )

        if family_id != "read_models":
            mechanic_paths = _mechanic_path_objects(
                family.get("mechanic_routes"), context=expected_path, issues=issues
            )
            source_crosswalks[family_id] = set(mechanic_paths)
            if require_mechanics:
                for route in mechanic_paths:
                    if not (repo_root / route).is_dir():
                        issues.append(
                            f"{expected_path}: mechanic route is missing: {route}"
                        )

    if set(family_by_id) != set(EXPECTED_FAMILIES):
        issues.append(
            "stats/source_home.manifest.json: family set must be "
            f"{sorted(EXPECTED_FAMILIES)!r}; found {sorted(family_by_id)!r}"
        )

    source_crosswalks["read_models"] = _validate_profiles(
        repo_root,
        family_by_id.get("read_models"),
        require_mechanics=require_mechanics,
        issues=issues,
    )

    root_posture = manifest.get("current_root_route_posture")
    if not isinstance(root_posture, list) or not root_posture:
        issues.append(
            "stats/source_home.manifest.json: current_root_route_posture must be non-empty"
        )
    else:
        seen_posture: set[str] = set()
        for route in root_posture:
            if not isinstance(route, dict) or not isinstance(route.get("path"), str):
                issues.append(
                    "stats/source_home.manifest.json: every root posture entry must name a path"
                )
                continue
            path = route["path"]
            if path in seen_posture:
                issues.append(
                    f"stats/source_home.manifest.json: duplicate root posture path {path!r}"
                )
            seen_posture.add(path)
            if path.startswith("stats/") or not (repo_root / path).exists():
                issues.append(
                    f"stats/source_home.manifest.json: invalid active root posture path {path!r}"
                )
            for field in ("status", "meaning"):
                if not isinstance(route.get(field), str) or not route[field].strip():
                    issues.append(
                        f"stats/source_home.manifest.json: root posture {path!r} needs {field}"
                    )

    stronger_owners = manifest.get("stronger_owner_routes")
    if not isinstance(stronger_owners, list) or not stronger_owners:
        issues.append(
            "stats/source_home.manifest.json: stronger_owner_routes must be non-empty"
        )
    else:
        for route in stronger_owners:
            if not isinstance(route, dict) or not all(
                isinstance(route.get(field), str) and route[field].strip()
                for field in ("pressure", "route")
            ):
                issues.append(
                    "stats/source_home.manifest.json: stronger owner entries need pressure and route"
                )

    if require_mechanics:
        topology, topology_error = _load_object(repo_root / TOPOLOGY_PATH)
        if topology_error:
            issues.append(topology_error)
        else:
            assert topology is not None
            expected_crosswalks = {
                family: set(routes) for family, routes in source_crosswalks.items()
            }
            if _topology_crosswalks(topology) != expected_crosswalks:
                issues.append(
                    "mechanics/topology.json: source-family crosswalks do not match stats source home"
                )
            if _part_back_references(topology) != expected_crosswalks:
                issues.append(
                    "mechanics/topology.json: active part back-references do not match stats source home"
                )

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--allow-missing-mechanics",
        action="store_true",
        help="Validate source-home records before their mechanics routes land; release validation stays strict.",
    )
    args = parser.parse_args(argv)

    issues = validate(
        args.repo_root,
        require_mechanics=not args.allow_missing_mechanics,
    )
    if issues:
        print("Stats source-home validation failed for aoa-stats.")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("[ok] aoa-stats source home, authored profiles, and mechanics crosswalk")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
