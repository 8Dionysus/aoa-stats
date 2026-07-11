#!/usr/bin/env python3
"""Validate localized mechanics, profile crosswalks, and root exceptions."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
TOPOLOGY_PATH = Path("mechanics/topology.json")
SOURCE_MANIFEST_PATH = Path("stats/source_home.manifest.json")
PROFILE_ROOT = Path("stats/read-models")
REQUIRED_MECHANICS_ROOT_FILES = {"AGENTS.md", "README.md", "topology.json"}
REQUIRED_PACKAGE_FILES = {"AGENTS.md", "README.md", "PARTS.md", "PROVENANCE.md"}
REQUIRED_PARTS_ROOT_FILES = {"AGENTS.md", "README.md"}
REQUIRED_PART_FILES = {"README.md", "CONTRACT.md", "VALIDATION.md"}
FORBIDDEN_MECHANICS_ROOT_ENTRIES = {
    "_meta",
    "backlog",
    "legacy",
    "notes",
    "scratch",
    "templates",
}
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
IGNORED_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache"}


def _load_object(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"{path.as_posix()}: file is missing"
    except json.JSONDecodeError as exc:
        return None, f"{path.as_posix()}: invalid JSON: {exc}"
    if not isinstance(value, dict):
        return None, f"{path.as_posix()}: must be a JSON object"
    return value, None


def _entries(path: Path) -> set[str]:
    return {
        child.name
        for child in path.iterdir()
        if child.name not in IGNORED_NAMES and not child.name.endswith((".pyc", ".pyo"))
    }


def _files(path: Path, repo_root: Path) -> set[str]:
    if not path.exists():
        return set()
    return {
        child.relative_to(repo_root).as_posix()
        for child in path.rglob("*")
        if child.is_file()
        and not any(part in IGNORED_NAMES for part in child.relative_to(repo_root).parts)
        and not child.name.endswith((".pyc", ".pyo"))
    }


def _string_list(value: object, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(isinstance(item, str) and item for item in value)
    )


def _profile_routes(repo_root: Path) -> tuple[set[str], set[str], set[str], list[str]]:
    mechanic_routes: set[str] = set()
    schema_routes: set[str] = set()
    generated_routes: set[str] = set()
    issues: list[str] = []
    profile_paths = sorted(
        [
            *(repo_root / PROFILE_ROOT / "active").glob("*.profile.json"),
            *(repo_root / PROFILE_ROOT / "deferred").glob("*.profile.json"),
        ]
    )
    if not profile_paths:
        return set(), set(), set(), ["stats/read-models: no authored profiles"]
    for path in profile_paths:
        profile, error = _load_object(path)
        if error:
            issues.append(error)
            continue
        assert profile is not None
        routes = profile.get("mechanic_routes")
        if not _string_list(routes):
            issues.append(f"{path.relative_to(repo_root).as_posix()}: mechanic_routes must be non-empty")
        else:
            mechanic_routes.update(routes)
        schema_ref = profile.get("schema_ref")
        if isinstance(schema_ref, str):
            schema_routes.add(schema_ref)
        surface_ref = profile.get("surface_ref")
        if isinstance(surface_ref, str):
            generated_routes.add(surface_ref)
    return mechanic_routes, schema_routes, generated_routes, issues


def _manifest_crosswalks(manifest: dict[str, Any]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    families = manifest.get("families")
    if not isinstance(families, list):
        return result
    for family in families:
        if not isinstance(family, dict) or not isinstance(family.get("id"), str):
            continue
        routes = family.get("mechanic_routes")
        if not isinstance(routes, list):
            continue
        result[family["id"]] = {
            route["path"]
            for route in routes
            if isinstance(route, dict) and isinstance(route.get("path"), str)
        }
    return result


def _topology_crosswalks(topology: dict[str, Any]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    crosswalks = topology.get("source_family_crosswalks")
    if not isinstance(crosswalks, list):
        return result
    for crosswalk in crosswalks:
        if not isinstance(crosswalk, dict):
            continue
        family = crosswalk.get("stats_source_family_ref")
        routes = crosswalk.get("mechanic_part_refs")
        if isinstance(family, str) and _string_list(routes):
            result[family] = set(routes)
    return result


def _validate_root_payload_contract(
    repo_root: Path,
    topology: dict[str, Any],
    profile_schemas: set[str],
    profile_outputs: set[str],
    issues: list[str],
) -> None:
    contract = topology.get("root_payload_contract")
    if not isinstance(contract, dict):
        issues.append("mechanics/topology.json: root_payload_contract must be an object")
        return

    empty_districts = contract.get("must_be_empty")
    if not _string_list(empty_districts):
        issues.append("mechanics/topology.json: must_be_empty must be a non-empty string list")
    else:
        for district in empty_districts:
            remaining = _files(repo_root / district, repo_root)
            if remaining:
                issues.append(f"{district}/: expected no active files, found {sorted(remaining)!r}")

    allowed_exact = contract.get("allowed_exact")
    allowed_prefixes = contract.get("allowed_prefixes", {})
    if not isinstance(allowed_exact, dict) or not isinstance(allowed_prefixes, dict):
        issues.append("mechanics/topology.json: root allowlists must be objects")
        return
    for district, paths in allowed_exact.items():
        if not isinstance(district, str) or not _string_list(paths, allow_empty=True):
            issues.append(f"mechanics/topology.json: invalid allowlist for {district!r}")
            continue
        prefixes = allowed_prefixes.get(district, [])
        if not _string_list(prefixes, allow_empty=True):
            issues.append(f"mechanics/topology.json: invalid prefix allowlist for {district!r}")
            prefixes = []
        expected = set(paths)
        missing = {path for path in expected if not (repo_root / path).is_file()}
        actual = _files(repo_root / district, repo_root)
        unexpected = {
            path
            for path in actual
            if path not in expected and not any(path.startswith(prefix) for prefix in prefixes)
        }
        if missing or unexpected:
            issues.append(
                f"{district}/: root payload allowlist mismatch; "
                f"missing={sorted(missing)!r}, unexpected={sorted(unexpected)!r}"
            )

    public = contract.get("derived_public_districts")
    if not isinstance(public, dict):
        issues.append("mechanics/topology.json: derived_public_districts must be an object")
        return
    extra_schemas = public.get("additional_schema_routes")
    extra_outputs = public.get("additional_generated_routes")
    if not _string_list(extra_schemas, allow_empty=True) or not _string_list(
        extra_outputs, allow_empty=True
    ):
        issues.append("mechanics/topology.json: additional public routes must be string lists")
        return
    expected_schemas = {
        "schemas/AGENTS.md",
        *[route for route in profile_schemas if route.startswith("schemas/")],
        *extra_schemas,
    }
    expected_outputs = {
        "generated/AGENTS.md",
        *[route for route in profile_outputs if route.startswith("generated/")],
        *extra_outputs,
    }
    for district, expected in (("schemas", expected_schemas), ("generated", expected_outputs)):
        actual = _files(repo_root / district, repo_root)
        missing = {path for path in expected if not (repo_root / path).is_file()}
        unexpected = actual - expected
        if missing or unexpected:
            issues.append(
                f"{district}/: public district mismatch; "
                f"missing={sorted(missing)!r}, unexpected={sorted(unexpected)!r}"
            )


def _validate_agon_legacy(repo_root: Path, issues: list[str]) -> None:
    ledger_path = repo_root / "mechanics/agon/legacy/former-routes.json"
    if not ledger_path.is_file():
        return
    ledger, error = _load_object(ledger_path)
    if error:
        issues.append(error)
        return
    assert ledger is not None
    for route in ledger.get("active_routes", []):
        if not isinstance(route, dict):
            continue
        current_root = route.get("current_root")
        if isinstance(current_root, str) and not (repo_root / current_root).is_dir():
            issues.append(f"mechanics/agon/legacy: missing current part {current_root}")
        output = route.get("root_public_output")
        if isinstance(output, str) and not (repo_root / output).is_file():
            issues.append(f"mechanics/agon/legacy: missing public output {output}")
        for former in route.get("former_paths", []):
            if isinstance(former, str) and (repo_root / former).exists():
                issues.append(f"mechanics/agon/legacy: former active route still exists: {former}")
    for field in ("historical_routes", "package_doc_routes"):
        for route in ledger.get(field, []):
            if not isinstance(route, dict):
                continue
            former = route.get("former_path")
            current = route.get("current_path")
            if isinstance(former, str) and (repo_root / former).exists():
                issues.append(f"mechanics/agon/legacy: former route still exists: {former}")
            if isinstance(current, str) and not (repo_root / current).is_file():
                issues.append(f"mechanics/agon/legacy: current route is missing: {current}")


def validate(repo_root: Path = REPO_ROOT) -> list[str]:
    repo_root = repo_root.resolve()
    issues: list[str] = []
    topology, error = _load_object(repo_root / TOPOLOGY_PATH)
    if error:
        return [error]
    assert topology is not None
    source_manifest, source_error = _load_object(repo_root / SOURCE_MANIFEST_PATH)
    if source_error:
        issues.append(source_error)
        source_manifest = {}
    assert source_manifest is not None

    if topology.get("schema_version") != "aoa_stats_mechanics_topology_v2":
        issues.append("mechanics/topology.json: wrong schema_version")
    if topology.get("layer") != "aoa-stats":
        issues.append("mechanics/topology.json: layer must be aoa-stats")
    if topology.get("common_mechanic_source") != "Agents-of-Abyss/mechanics":
        issues.append("mechanics/topology.json: common_mechanic_source is not canonical")
    if topology.get("stats_source_manifest") != SOURCE_MANIFEST_PATH.as_posix():
        issues.append("mechanics/topology.json: stats_source_manifest is not canonical")
    if topology.get("stats_profile_root") != PROFILE_ROOT.as_posix():
        issues.append("mechanics/topology.json: stats_profile_root is not canonical")

    mechanics_root = repo_root / "mechanics"
    root_contract = topology.get("root_contract")
    if not isinstance(root_contract, dict):
        issues.append("mechanics/topology.json: root_contract must be an object")
    else:
        if set(root_contract.get("allowed_root_files", [])) != REQUIRED_MECHANICS_ROOT_FILES:
            issues.append("mechanics/topology.json: allowed_root_files mismatch")
        if set(root_contract.get("forbidden_root_entries", [])) != FORBIDDEN_MECHANICS_ROOT_ENTRIES:
            issues.append("mechanics/topology.json: forbidden_root_entries mismatch")

    activation = topology.get("package_activation")
    activation_paths: set[str] = set()
    if not isinstance(activation, dict) or not _string_list(
        activation.get("active_package_paths") if isinstance(activation, dict) else None
    ):
        issues.append("mechanics/topology.json: active_package_paths must be non-empty")
    else:
        activation_paths = set(activation["active_package_paths"])
        if activation.get("unlisted_package_status") != "inactive_not_mapped":
            issues.append("mechanics/topology.json: unlisted packages must be inactive_not_mapped")

    packages = topology.get("active_packages")
    if not isinstance(packages, list):
        issues.append("mechanics/topology.json: active_packages must be a list")
        packages = []
    package_names = {
        package.get("path")
        for package in packages
        if isinstance(package, dict) and isinstance(package.get("path"), str)
    }
    if package_names != activation_paths:
        issues.append("mechanics/topology.json: package activation and active_packages disagree")
    expected_root_entries = REQUIRED_MECHANICS_ROOT_FILES | package_names
    if mechanics_root.is_dir() and _entries(mechanics_root) != expected_root_entries:
        issues.append(
            "mechanics/: entries do not match topology; "
            f"expected={sorted(expected_root_entries)!r}, actual={sorted(_entries(mechanics_root))!r}"
        )

    profile_mechanics, profile_schemas, profile_outputs, profile_issues = _profile_routes(repo_root)
    issues.extend(profile_issues)
    part_crosswalks: dict[str, set[str]] = {}
    seen_parts: set[str] = set()

    for package in packages:
        if not isinstance(package, dict) or not isinstance(package.get("path"), str):
            issues.append("mechanics/topology.json: invalid package record")
            continue
        package_name = package["path"]
        if not SLUG.fullmatch(package_name):
            issues.append(f"mechanics/topology.json: invalid package slug {package_name!r}")
        package_root = mechanics_root / package_name
        package_payload_roots = package.get("package_payload_roots", [])
        if not _string_list(package_payload_roots, allow_empty=True):
            issues.append(f"mechanics/{package_name}: package_payload_roots must be a string list")
            package_payload_roots = []
        expected_package_entries = REQUIRED_PACKAGE_FILES | {"parts"} | set(package_payload_roots)
        if package_root.is_dir() and _entries(package_root) != expected_package_entries:
            issues.append(
                f"mechanics/{package_name}: entries mismatch; "
                f"expected={sorted(expected_package_entries)!r}, actual={sorted(_entries(package_root))!r}"
            )
        for payload_root in package_payload_roots:
            path = package_root / payload_root
            if not _files(path, repo_root):
                issues.append(f"mechanics/{package_name}/{payload_root}: empty package payload root")
        if package_name == "titan":
            if package.get("mechanic_class") != "shared-owner":
                issues.append("mechanics/titan: mechanic_class must be shared-owner")
            if package.get("owner_mechanic_ref") != "aoa-agents/mechanics/titan":
                issues.append("mechanics/titan: owner_mechanic_ref mismatch")
            if "center_mechanic_ref" in package:
                issues.append("mechanics/titan: nonexistent center_mechanic_ref is forbidden")
        else:
            if package.get("mechanic_class") != "common-center":
                issues.append(
                    f"mechanics/{package_name}: mechanic_class must be common-center"
                )
            if package.get("center_mechanic_ref") != f"Agents-of-Abyss/mechanics/{package_name}":
                issues.append(f"mechanics/{package_name}: center_mechanic_ref mismatch")
        if package.get("local_status") != "localized_active":
            issues.append(f"mechanics/{package_name}: local_status must be localized_active")
        if not isinstance(package.get("local_function"), str) or not package["local_function"].strip():
            issues.append(f"mechanics/{package_name}: local_function must be non-empty")

        parts = package.get("active_part_routes")
        if not isinstance(parts, list) or not parts:
            issues.append(f"mechanics/{package_name}: active_part_routes must be non-empty")
            parts = []
        part_names = {
            part.get("path")
            for part in parts
            if isinstance(part, dict) and isinstance(part.get("path"), str)
        }
        parts_root = package_root / "parts"
        expected_parts_entries = REQUIRED_PARTS_ROOT_FILES | part_names
        if parts_root.is_dir() and _entries(parts_root) != expected_parts_entries:
            issues.append(
                f"mechanics/{package_name}/parts: entries mismatch; "
                f"expected={sorted(expected_parts_entries)!r}, actual={sorted(_entries(parts_root))!r}"
            )

        for part in parts:
            if not isinstance(part, dict) or not isinstance(part.get("path"), str):
                issues.append(f"mechanics/{package_name}: invalid part record")
                continue
            part_name = part["path"]
            route = f"mechanics/{package_name}/parts/{part_name}"
            if not SLUG.fullmatch(part_name) or route in seen_parts:
                issues.append(f"{route}: invalid or duplicate part route")
            seen_parts.add(route)
            part_root = repo_root / route
            localized = part.get("localized_payload_roots", [])
            retained = part.get("retained_root_routes", [])
            materialized = part.get("materialized_root_routes", [])
            family_refs = part.get("stats_source_family_refs", [])
            if not _string_list(localized, allow_empty=True):
                issues.append(f"{route}: localized_payload_roots must be a string list")
                localized = []
            if not _string_list(retained, allow_empty=True):
                issues.append(f"{route}: retained_root_routes must be a string list")
                retained = []
            if not _string_list(materialized, allow_empty=True):
                issues.append(f"{route}: materialized_root_routes must be a string list")
                materialized = []
            if not _string_list(family_refs):
                issues.append(f"{route}: stats_source_family_refs must be a non-empty string list")
                family_refs = []
            expected_part_entries = REQUIRED_PART_FILES | set(localized)
            if part_root.is_dir() and _entries(part_root) != expected_part_entries:
                issues.append(
                    f"{route}: entries mismatch; expected={sorted(expected_part_entries)!r}, "
                    f"actual={sorted(_entries(part_root))!r}"
                )
            for filename in REQUIRED_PART_FILES:
                if not (part_root / filename).is_file():
                    issues.append(f"{route}: missing {filename}")
            if part.get("owner_surface") != f"{route}/CONTRACT.md":
                issues.append(f"{route}: owner_surface mismatch")
            if part.get("validation_surface") != f"{route}/VALIDATION.md":
                issues.append(f"{route}: validation_surface mismatch")
            for payload_root in localized:
                if not _files(part_root / payload_root, repo_root):
                    issues.append(f"{route}/{payload_root}: localized payload root is empty")
            for retained_route in retained:
                if not (repo_root / retained_route).exists():
                    issues.append(f"{route}: retained root route is missing: {retained_route}")
            for materialized_route in materialized:
                if not materialized_route.startswith("dist/"):
                    issues.append(
                        f"{route}: materialized root route must stay under dist/: "
                        f"{materialized_route}"
                    )
                if materialized_route in retained:
                    issues.append(
                        f"{route}: materialized root route cannot also be retained: "
                        f"{materialized_route}"
                    )
            if not localized and not retained and not materialized and route not in profile_mechanics:
                issues.append(f"{route}: active part has no payload, public route, or profile handoff")
            for family in family_refs:
                part_crosswalks.setdefault(family, set()).add(route)

    topology_crosswalks = _topology_crosswalks(topology)
    manifest_crosswalks = _manifest_crosswalks(source_manifest)
    if topology_crosswalks != part_crosswalks:
        issues.append("mechanics/topology.json: crosswalks do not match part back-references")
    if topology_crosswalks != manifest_crosswalks:
        issues.append("mechanics/topology.json: crosswalks do not match stats source home")
    if topology_crosswalks.get("read_models", set()) != profile_mechanics:
        issues.append("mechanics/topology.json: read_models crosswalk does not match profiles")
    for route in profile_mechanics:
        if route not in seen_parts:
            issues.append(f"stats/read-models: profile points outside active mechanics: {route}")

    _validate_root_payload_contract(
        repo_root, topology, profile_schemas, profile_outputs, issues
    )
    _validate_agon_legacy(repo_root, issues)
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    issues = validate(args.repo_root)
    if issues:
        print("Mechanics topology validation failed for aoa-stats.")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("[ok] localized mechanics topology, profile crosswalks, and root exceptions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
