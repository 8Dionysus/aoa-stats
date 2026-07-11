from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_mechanics_topology.py"
SPEC = importlib.util.spec_from_file_location("validate_mechanics_topology", SCRIPT_PATH)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)

EXPECTED_PACKAGES = {
    "agon",
    "antifragility",
    "audit",
    "boundary-bridge",
    "checkpoint",
    "experience",
    "growth-cycle",
    "method-growth",
    "recurrence",
    "release-support",
    "rpg",
    "titan",
}


def load_json(relative_path: str) -> dict:
    payload = json.loads((REPO_ROOT / relative_path).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def copy_repo(tmp_path: Path) -> Path:
    copied_root = tmp_path / "repo"
    shutil.copytree(
        REPO_ROOT,
        copied_root,
        ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__"),
    )
    return copied_root


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def operation_parts(topology: dict) -> list[tuple[str, dict]]:
    return [
        (f"mechanics/{package['path']}/parts/{part['path']}", part)
        for package in topology["active_packages"]
        for part in package["active_part_routes"]
        if "operation_contracts" in part["stats_source_family_refs"]
    ]


def test_live_mechanics_topology_passes() -> None:
    assert validator.validate(REPO_ROOT) == []


def test_only_payload_backed_packages_are_active() -> None:
    topology = load_json("mechanics/topology.json")
    activation = topology["package_activation"]
    assert set(activation["active_package_paths"]) == EXPECTED_PACKAGES
    assert activation["unlisted_package_status"] == "inactive_not_mapped"
    assert {package["path"] for package in topology["active_packages"]} == EXPECTED_PACKAGES
    assert "codex-projection" not in EXPECTED_PACKAGES
    assert "runtime-seam" not in EXPECTED_PACKAGES
    assert "questbook" not in EXPECTED_PACKAGES


def test_titan_routes_to_its_real_shared_owner_not_a_nonexistent_center_package() -> None:
    topology = load_json("mechanics/topology.json")
    titan = next(package for package in topology["active_packages"] if package["path"] == "titan")

    assert titan["mechanic_class"] == "shared-owner"
    assert titan["owner_mechanic_ref"] == "aoa-agents/mechanics/titan"
    assert "center_mechanic_ref" not in titan


def test_every_active_part_has_payload_public_route_or_profile_handoff() -> None:
    topology = load_json("mechanics/topology.json")
    profile_routes = {
        route
        for lifecycle in ("active", "deferred")
        for path in (REPO_ROOT / "stats/read-models" / lifecycle).glob("*.profile.json")
        for route in json.loads(path.read_text(encoding="utf-8"))["mechanic_routes"]
    }
    for package in topology["active_packages"]:
        for part in package["active_part_routes"]:
            route = f"mechanics/{package['path']}/parts/{part['path']}"
            assert (
                part["localized_payload_roots"]
                or part["retained_root_routes"]
                or route in profile_routes
            ), route


def test_every_active_part_has_a_stats_source_family_back_reference() -> None:
    topology = load_json("mechanics/topology.json")
    for package in topology["active_packages"]:
        for part in package["active_part_routes"]:
            assert part["stats_source_family_refs"], (
                f"mechanics/{package['path']}/parts/{part['path']}"
            )


def test_source_family_crosswalks_match_manifest_and_part_backrefs() -> None:
    topology = load_json("mechanics/topology.json")
    source_manifest = load_json("stats/source_home.manifest.json")
    from_topology = {
        entry["stats_source_family_ref"]: set(entry["mechanic_part_refs"])
        for entry in topology["source_family_crosswalks"]
    }
    from_manifest = {
        family["id"]: {route["path"] for route in family["mechanic_routes"]}
        for family in source_manifest["families"]
    }
    from_parts: dict[str, set[str]] = {}
    for package in topology["active_packages"]:
        for part in package["active_part_routes"]:
            route = f"mechanics/{package['path']}/parts/{part['path']}"
            for family in part["stats_source_family_refs"]:
                from_parts.setdefault(family, set()).add(route)
    assert from_topology == from_manifest == from_parts


def test_operation_contract_records_and_parts_have_exact_reciprocal_links() -> None:
    topology = load_json("mechanics/topology.json")
    part_entries = operation_parts(topology)
    part_refs = [part["stats_operation_contract_ref"] for _, part in part_entries]
    record_paths = sorted(
        (REPO_ROOT / "stats" / "operation-contracts" / "active").glob(
            "*.operation.json"
        )
    )
    record_bindings = {}
    for path in record_paths:
        record = json.loads(path.read_text(encoding="utf-8"))
        operation_id = path.name.removesuffix(".operation.json")
        assert record["operation_id"] == operation_id
        package, part = record["mechanic_route"].removeprefix("mechanics/").split(
            "/parts/",
            1,
        )
        assert operation_id == f"{package}.{part}"
        record_bindings[path.relative_to(REPO_ROOT).as_posix()] = record[
            "mechanic_route"
        ]

    assert len(part_entries) == len(part_refs) == len(set(part_refs)) == 15
    assert len(record_bindings) == 15
    assert {
        part["stats_operation_contract_ref"]: route for route, part in part_entries
    } == record_bindings


def test_operation_contract_part_cannot_swap_to_another_record(tmp_path: Path) -> None:
    copied_root = copy_repo(tmp_path)
    topology_path = copied_root / "mechanics" / "topology.json"
    topology = json.loads(topology_path.read_text(encoding="utf-8"))
    parts = operation_parts(topology)
    parts[0][1]["stats_operation_contract_ref"], parts[1][1][
        "stats_operation_contract_ref"
    ] = (
        parts[1][1]["stats_operation_contract_ref"],
        parts[0][1]["stats_operation_contract_ref"],
    )
    write_json(topology_path, topology)

    issues = validator.validate(copied_root)

    assert sum("stats operation contract binds" in issue for issue in issues) == 2


def test_operation_contract_part_requires_its_backlink(tmp_path: Path) -> None:
    copied_root = copy_repo(tmp_path)
    topology_path = copied_root / "mechanics" / "topology.json"
    topology = json.loads(topology_path.read_text(encoding="utf-8"))
    route, part = operation_parts(topology)[0]
    part.pop("stats_operation_contract_ref")
    write_json(topology_path, topology)

    issues = validator.validate(copied_root)

    assert f"{route}: stats_operation_contract_ref is required" in issues
    assert any("operation contract backlinks do not match" in issue for issue in issues)


def test_non_operation_part_cannot_claim_operation_contract_backlink(
    tmp_path: Path,
) -> None:
    copied_root = copy_repo(tmp_path)
    topology_path = copied_root / "mechanics" / "topology.json"
    topology = json.loads(topology_path.read_text(encoding="utf-8"))
    operation_ref = operation_parts(topology)[0][1]["stats_operation_contract_ref"]
    route, part = next(
        (
            f"mechanics/{package['path']}/parts/{candidate['path']}",
            candidate,
        )
        for package in topology["active_packages"]
        for candidate in package["active_part_routes"]
        if "operation_contracts" not in candidate["stats_source_family_refs"]
    )
    part["stats_operation_contract_ref"] = operation_ref
    write_json(topology_path, topology)

    issues = validator.validate(copied_root)

    assert (
        f"{route}: stats_operation_contract_ref is forbidden outside "
        "operation_contracts"
    ) in issues


def test_flat_operation_districts_are_empty_and_public_districts_are_explicit() -> None:
    topology = load_json("mechanics/topology.json")
    contract = topology["root_payload_contract"]
    for district in contract["must_be_empty"]:
        root = REPO_ROOT / district
        assert not root.exists() or not any(path.is_file() for path in root.rglob("*"))
    assert contract["allowed_exact"]["examples"] == [
        "examples/AGENTS.md",
        "examples/codex_plane_deployment_summary.example.json",
    ]
    assert "schemas/stats-event-envelope.schema.json" in contract[
        "derived_public_districts"
    ]["additional_schema_routes"]


def test_artifact_runtime_outputs_are_materialized_not_retained_source_routes() -> None:
    topology = load_json("mechanics/topology.json")
    release_support = next(
        package
        for package in topology["active_packages"]
        if package["path"] == "release-support"
    )
    artifact_part = next(
        part
        for part in release_support["active_part_routes"]
        if part["path"] == "summary-catalog-artifact-bundle"
    )

    assert artifact_part["retained_root_routes"] == [
        "manifests/artifact_bundles",
        "scripts/validate_abyss_machine_summary_catalog_bundle.py",
    ]
    assert artifact_part["materialized_root_routes"] == [
        "dist/abyss-artifact-bundle/aoa-stats-summary-surface-catalog",
        "dist/abyss-artifact-registry/aoa-stats-summary-surface-catalog",
        "dist/abyss-artifact-subjects/aoa-stats-summary-surface-catalog",
    ]


def test_agon_former_routes_are_active_first() -> None:
    ledger = load_json("mechanics/agon/legacy/former-routes.json")
    for route in ledger["active_routes"]:
        assert (REPO_ROOT / route["current_root"]).is_dir()
        assert (REPO_ROOT / route["root_public_output"]).is_file()
        for former in route["former_paths"]:
            assert not (REPO_ROOT / former).exists(), former
    for group in ("historical_routes", "package_doc_routes"):
        for route in ledger[group]:
            assert not (REPO_ROOT / route["former_path"]).exists()
            assert (REPO_ROOT / route["current_path"]).is_file()
