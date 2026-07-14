from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_stats_source_home.py"
SPEC = importlib.util.spec_from_file_location("validate_stats_source_home", SCRIPT_PATH)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)

SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder.surface_catalog import (  # noqa: E402
    load_surface_profiles,
    public_surface_profiles,
)


def load_json(relative_path: str) -> dict[str, object]:
    payload = json.loads((REPO_ROOT / relative_path).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def copy_repo(tmp_path: Path) -> Path:
    return shutil.copytree(
        REPO_ROOT,
        tmp_path / "repo",
        ignore=shutil.ignore_patterns(
            ".git",
            ".pytest_cache",
            "__pycache__",
            "dist",
        ),
    )


def load_repo_json(repo_root: Path, relative_path: str) -> dict[str, object]:
    payload = json.loads((repo_root / relative_path).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def write_repo_json(
    repo_root: Path,
    relative_path: str,
    payload: dict[str, object],
) -> None:
    (repo_root / relative_path).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def test_live_stats_source_home_passes_before_mechanics_integration() -> None:
    assert validator.validate(REPO_ROOT, require_mechanics=False) == []


def test_source_validator_derives_profile_cardinality_from_authored_state(
    tmp_path: Path,
) -> None:
    repo_root = copy_repo(tmp_path)
    candidate = load_repo_json(
        repo_root,
        "stats/read-models/deferred/antifragility_vector.profile.json",
    )
    candidate["name"] = "inventory_growth_probe"
    candidate["activation_condition"] = (
        "Remain a validation-only growth probe until a separately reviewed "
        "owner contract exists."
    )
    write_repo_json(
        repo_root,
        "stats/read-models/deferred/inventory_growth_probe.profile.json",
        candidate,
    )
    catalog = load_repo_json(
        repo_root, "generated/summary_surface_catalog.min.json"
    )
    _, public_deferred = public_surface_profiles(
        repo_root / "stats" / "read-models"
    )
    catalog["deferred_contract_surfaces"] = public_deferred
    write_repo_json(
        repo_root,
        "generated/summary_surface_catalog.min.json",
        catalog,
    )

    assert validator.validate(repo_root, require_mechanics=False) == []


def test_source_validator_requires_a_nonempty_active_family(tmp_path: Path) -> None:
    repo_root = copy_repo(tmp_path)
    for profile_path in (repo_root / "stats/read-models/active").glob(
        "*.profile.json"
    ):
        profile_path.unlink()

    issues = validator.validate(repo_root, require_mechanics=False)

    assert (
        "stats/read-models/active: at least one authored public profile is required"
        in issues
    )


def test_source_validator_derives_operation_cardinality_from_reciprocal_state(
    tmp_path: Path,
) -> None:
    repo_root = copy_repo(tmp_path)
    operation_id = "agon.inventory-growth-probe"
    part_name = "inventory-growth-probe"
    mechanic_route = f"mechanics/agon/parts/{part_name}"
    record_ref = (
        "stats/operation-contracts/active/"
        f"{operation_id}.operation.json"
    )

    record = load_repo_json(
        repo_root,
        "stats/operation-contracts/active/"
        "agon.epistemic-observability.operation.json",
    )
    record.update(
        {
            "operation_id": operation_id,
            "mechanic_route": mechanic_route,
            "payload_class": "inventory-growth-probe-stats-operation",
            "mechanic_contract_ref": f"{mechanic_route}/CONTRACT.md",
            "validation_ref": f"{mechanic_route}/VALIDATION.md",
        }
    )
    write_repo_json(repo_root, record_ref, record)

    part_root = repo_root / mechanic_route
    part_root.mkdir()
    (part_root / "CONTRACT.md").write_text(
        "# Inventory growth probe\n\n"
        f"Authored source: `{record_ref}`.\n",
        encoding="utf-8",
    )
    (part_root / "VALIDATION.md").write_text(
        "# Inventory growth probe validation\n",
        encoding="utf-8",
    )

    manifest = load_repo_json(repo_root, "stats/source_home.manifest.json")
    operation_family = next(
        family
        for family in manifest["families"]
        if family["id"] == "operation_contracts"
    )
    operation_family["mechanic_routes"].append(
        {"package": "agon", "part": part_name, "path": mechanic_route}
    )
    write_repo_json(repo_root, "stats/source_home.manifest.json", manifest)

    topology = load_repo_json(repo_root, "mechanics/topology.json")
    agon_package = next(
        package for package in topology["active_packages"] if package["path"] == "agon"
    )
    agon_package["active_part_routes"].append(
        {
            "path": part_name,
            "stats_operation_contract_ref": record_ref,
            "owner_surface": f"{mechanic_route}/CONTRACT.md",
            "validation_surface": f"{mechanic_route}/VALIDATION.md",
            "payload_class": "inventory-growth-probe-stats-operation",
            "stats_source_family_refs": ["operation_contracts"],
        }
    )
    operation_crosswalk = next(
        entry
        for entry in topology["source_family_crosswalks"]
        if entry["stats_source_family_ref"] == "operation_contracts"
    )
    operation_crosswalk["mechanic_part_refs"].append(mechanic_route)
    write_repo_json(repo_root, "mechanics/topology.json", topology)

    assert validator.validate(repo_root) == []


def test_source_home_contains_only_declared_source_records() -> None:
    stats_root = REPO_ROOT / "stats"
    operation_contracts = sorted(
        path.relative_to(stats_root).as_posix()
        for path in (stats_root / "operation-contracts" / "active").glob(
            "*.operation.json"
        )
    )
    active_profiles = sorted(
        path.relative_to(stats_root).as_posix()
        for path in (stats_root / "read-models" / "active").glob("*.profile.json")
    )
    deferred_profiles = sorted(
        path.relative_to(stats_root).as_posix()
        for path in (stats_root / "read-models" / "deferred").glob("*.profile.json")
    )
    retired_profiles = sorted(
        path.relative_to(stats_root).as_posix()
        for path in (stats_root / "read-models" / "retired").glob("*.profile.json")
    )
    expected_json = {
        "source_home.manifest.json",
        "intake-contract/event-kind-registry.json",
        "intake-contract/examples/session_harvest_family.receipts.example.json",
        "operation-contracts/operation-contract.schema.json",
        "read-models/surface-profile.schema.json",
        "measurement-contract/measurement-contract.schema.json",
        "measurement-contract/measurement-packet.schema.json",
        "measurement-contract/packet-read-request.schema.json",
        "measurement-contract/packet-read-result.schema.json",
        "federation/local-port.schema.json",
        "federation/owner-inventory.schema.json",
        "federation/owner-inventory.json",
        *operation_contracts,
        *active_profiles,
        *deferred_profiles,
        *retired_profiles,
    }

    assert not list(stats_root.rglob("*.py"))
    assert {
        path.relative_to(stats_root).as_posix() for path in stats_root.rglob("*.json")
    } == expected_json
    assert {path.name for path in stats_root.iterdir()} == {
        "AGENTS.md",
        "README.md",
        "source_home.manifest.json",
        "measurement-contract",
        "federation",
        "intake-contract",
        "operation-contracts",
        "read-models",
        "surface-catalog",
    }


def test_source_families_name_meaning_ceiling_and_current_routes() -> None:
    manifest = load_json("stats/source_home.manifest.json")
    families = {family["id"]: family for family in manifest["families"]}

    assert set(families) == {
        "measurement_contract",
        "federation",
        "intake_contract",
        "operation_contracts",
        "read_models",
        "surface_catalog",
    }
    for family_id, family in families.items():
        assert family["meaning"]
        assert family["authority_ceiling"]
        assert family["stop_lines"]
        assert family["owner_surface"] == f"{family['path']}/AGENTS.md"
        for field in (
            "source_routes",
            "public_contract_routes",
            "implementation_routes",
            "validator_routes",
        ):
            assert family[field], (family_id, field)
            for route in family[field]:
                assert (REPO_ROOT / route).exists(), (family_id, field, route)


def test_operation_contract_records_are_complete_non_catalog_sources() -> None:
    operation_root = REPO_ROOT / "stats" / "operation-contracts" / "active"
    operation_paths = sorted(operation_root.glob("*.operation.json"))
    manifest = load_json("stats/source_home.manifest.json")
    operation_family = next(
        family
        for family in manifest["families"]
        if family["id"] == "operation_contracts"
    )
    topology = load_json("mechanics/topology.json")
    topology_refs = {
        part["stats_operation_contract_ref"]
        for package in topology["active_packages"]
        for part in package["active_part_routes"]
        if "operation_contracts" in part.get("stats_source_family_refs", [])
    }

    assert operation_paths
    assert {
        path.name.removesuffix(".operation.json") for path in operation_paths
    } == {
        load_repo_json(REPO_ROOT, path.relative_to(REPO_ROOT).as_posix())[
            "operation_id"
        ]
        for path in operation_paths
    }
    assert {
        load_repo_json(REPO_ROOT, path.relative_to(REPO_ROOT).as_posix())[
            "mechanic_route"
        ]
        for path in operation_paths
    } == {route["path"] for route in operation_family["mechanic_routes"]}
    assert topology_refs == {
        path.relative_to(REPO_ROOT).as_posix() for path in operation_paths
    }
    for path in operation_paths:
        record = load_repo_json(REPO_ROOT, path.relative_to(REPO_ROOT).as_posix())
        assert record["publication_posture"] == "non_catalog"
        assert not {"catalog_order", "schema_ref", "surface_ref"} & record.keys()
        package, part = record["mechanic_route"].removeprefix("mechanics/").split(
            "/parts/",
            1,
        )
        assert record["operation_id"] == f"{package}.{part}"
        assert {item["owner_repo"] for item in record["owner_truth_inputs"]} <= {
            item["repo"] for item in record["owner_return_routes"]
        }


def test_operation_contract_active_home_rejects_undeclared_entry(
    tmp_path: Path,
) -> None:
    repo_root = copy_repo(tmp_path)
    unexpected = repo_root / "stats/operation-contracts/active/UNDECLARED.md"
    unexpected.write_text("not an authored operation record\n", encoding="utf-8")

    issues = validator.validate(repo_root)

    assert any(
        "stats/operation-contracts/active: entries must be only authored "
        "operation records" in issue
        and "UNDECLARED.md" in issue
        for issue in issues
    )


def test_operation_contract_schema_rejects_missing_primary_question(
    tmp_path: Path,
) -> None:
    repo_root = copy_repo(tmp_path)
    record_ref = (
        "stats/operation-contracts/active/"
        "agon.epistemic-observability.operation.json"
    )
    record = load_repo_json(repo_root, record_ref)
    del record["primary_question"]
    write_repo_json(repo_root, record_ref, record)

    issues = validator.validate(repo_root)

    assert any(
        record_ref in issue
        and "'primary_question' is a required property" in issue
        for issue in issues
    )


def test_operation_contract_schema_rejects_profile_publication_field(
    tmp_path: Path,
) -> None:
    repo_root = copy_repo(tmp_path)
    record_ref = (
        "stats/operation-contracts/active/"
        "agon.epistemic-observability.operation.json"
    )
    record = load_repo_json(repo_root, record_ref)
    record["surface_ref"] = "generated/not-an-operation-contract.min.json"
    write_repo_json(repo_root, record_ref, record)

    issues = validator.validate(repo_root)

    assert any(
        record_ref in issue
        and "Additional properties are not allowed" in issue
        and "surface_ref" in issue
        for issue in issues
    )


def test_operation_contract_rejects_wrong_mechanic_route(tmp_path: Path) -> None:
    repo_root = copy_repo(tmp_path)
    record_ref = (
        "stats/operation-contracts/active/"
        "agon.epistemic-observability.operation.json"
    )
    record = load_repo_json(repo_root, record_ref)
    record["mechanic_route"] = "mechanics/agon/parts/not-the-bound-part"
    write_repo_json(repo_root, record_ref, record)

    issues = validator.validate(repo_root)

    assert any(
        record_ref in issue
        and "mechanic_contract_ref must be " in issue
        and "mechanics/agon/parts/not-the-bound-part/CONTRACT.md" in issue
        for issue in issues
    )


def test_operation_contract_id_must_derive_from_mechanic_route(
    tmp_path: Path,
) -> None:
    repo_root = copy_repo(tmp_path)
    record_ref = (
        "stats/operation-contracts/active/"
        "agon.epistemic-observability.operation.json"
    )
    record = load_repo_json(repo_root, record_ref)
    record["operation_id"] = "epistemic-observability"
    write_repo_json(repo_root, record_ref, record)

    issues = validator.validate(repo_root)

    assert any(
        record_ref in issue
        and "operation_id must match mechanic route as "
        "'agon.epistemic-observability'" in issue
        for issue in issues
    )


def test_operation_contract_posture_must_match_mechanic_class(
    tmp_path: Path,
) -> None:
    repo_root = copy_repo(tmp_path)
    record_ref = (
        "stats/operation-contracts/active/"
        "agon.epistemic-observability.operation.json"
    )
    record = load_repo_json(repo_root, record_ref)
    record["input_posture"] = "documentation_checklist"
    write_repo_json(repo_root, record_ref, record)

    issues = validator.validate(repo_root)

    assert any(
        record_ref in issue
        and "input_posture must be 'seed_registry_compiler'" in issue
        for issue in issues
    )


def test_operation_contract_requires_canonical_owner_return(tmp_path: Path) -> None:
    repo_root = copy_repo(tmp_path)
    record_ref = (
        "stats/operation-contracts/active/"
        "agon.epistemic-observability.operation.json"
    )
    record = load_repo_json(repo_root, record_ref)
    record["owner_return_routes"] = [
        {
            "repo": "aoa-stats",
            "surface": "stats/operation-contracts",
            "route_kind": "authored_meaning",
        }
    ]
    write_repo_json(repo_root, record_ref, record)

    issues = validator.validate(repo_root)

    assert any(
        record_ref in issue
        and "owner_return_routes must include canonical mechanic owner" in issue
        for issue in issues
    )


def test_operation_contract_returns_to_every_named_truth_owner(
    tmp_path: Path,
) -> None:
    repo_root = copy_repo(tmp_path)
    record_ref = (
        "stats/operation-contracts/active/titan.memory-owner-bridge.operation.json"
    )
    record = load_repo_json(repo_root, record_ref)
    record["owner_return_routes"] = [
        route
        for route in record["owner_return_routes"]
        if route["repo"] != "aoa-memo"
    ]
    write_repo_json(repo_root, record_ref, record)

    issues = validator.validate(repo_root)

    assert any(
        record_ref in issue
        and "owner_return_routes must cover every owner_truth_inputs repo" in issue
        and "aoa-memo" in issue
        for issue in issues
    )


def test_bound_current_source_requires_an_explicit_source_ref(
    tmp_path: Path,
) -> None:
    repo_root = copy_repo(tmp_path)
    record_ref = (
        "stats/operation-contracts/active/"
        "agon.epistemic-observability.operation.json"
    )
    record = load_repo_json(repo_root, record_ref)
    record["owner_truth_inputs"][0]["binding"] = "bound_current_source"
    write_repo_json(repo_root, record_ref, record)

    issues = validator.validate(repo_root)

    assert any(
        record_ref in issue and "'source_ref' is a required property" in issue
        for issue in issues
    )


def test_declared_source_cannot_be_promoted_without_registered_binding_proof(
    tmp_path: Path,
) -> None:
    repo_root = copy_repo(tmp_path)
    record_ref = (
        "stats/operation-contracts/active/"
        "agon.mechanical-trial-observability.operation.json"
    )
    record = load_repo_json(repo_root, record_ref)
    declared_input = next(
        item
        for item in record["owner_truth_inputs"]
        if item["binding"] == "declared_reference_only"
    )
    declared_input["binding"] = "bound_current_source"
    declared_input["binding_evidence_ref"] = (
        "mechanics/agon/parts/mechanical-trial-observability/VALIDATION.md"
    )
    write_repo_json(repo_root, record_ref, record)

    issues = validator.validate(repo_root)

    assert any(
        record_ref in issue
        and "bound_current_source has no registered mechanic binding proof" in issue
        for issue in issues
    )


def test_operation_contract_requires_mechanic_contract_backlink(
    tmp_path: Path,
) -> None:
    repo_root = copy_repo(tmp_path)
    record_ref = (
        "stats/operation-contracts/active/"
        "agon.epistemic-observability.operation.json"
    )
    contract_ref = "mechanics/agon/parts/epistemic-observability/CONTRACT.md"
    contract_path = repo_root / contract_ref
    contract = contract_path.read_text(encoding="utf-8")
    assert record_ref in contract
    contract_path.write_text(contract.replace(record_ref, ""), encoding="utf-8")

    issues = validator.validate(repo_root)

    assert (
        f"{contract_ref}: must link authored operation record {record_ref}"
        in issues
    )


def test_authored_profiles_are_the_public_catalog_source() -> None:
    active, deferred, retired = load_surface_profiles(
        REPO_ROOT / "stats" / "read-models"
    )
    public_active, public_deferred = public_surface_profiles(
        REPO_ROOT / "stats" / "read-models"
    )
    catalog = load_json("generated/summary_surface_catalog.min.json")

    assert [profile["catalog_order"] for profile in active] == [
        *range(1, 4),
        *range(5, 21),
        *range(23, 26),
    ]
    assert catalog["surfaces"] == public_active
    assert catalog["deferred_contract_surfaces"] == public_deferred
    retired_by_name = {profile["name"]: profile for profile in retired}
    assert {
        name: profile["former_catalog_order"]
        for name, profile in retired_by_name.items()
    } == {
        "owner_landing_summary": 4,
        "runtime_closeout_summary": 22,
        "titan_summon_summary": 21,
    }
    for profile in retired:
        assert profile["cleanup_scopes"] == [
            "committed_output",
            "summary_surface_catalog",
            "managed_live_state",
            "consumer_hints",
        ]
        assert not (REPO_ROOT / profile["retired_surface_ref"]).exists()
        assert profile["name"] not in {
            entry["name"] for entry in catalog["surfaces"]
        }
    assert not (
        REPO_ROOT / "mechanics/method-growth/parts/owner-landing"
    ).exists()
    assert not (REPO_ROOT / "mechanics/checkpoint").exists()
    assert all("mechanic_routes" not in entry for entry in catalog["surfaces"])
    assert all("catalog_order" not in entry for entry in catalog["surfaces"])


def test_retired_profile_name_cannot_reenter_active_catalog(tmp_path: Path) -> None:
    repo_root = copy_repo(tmp_path)
    active_ref = "stats/read-models/active/titan_summon_summary.profile.json"
    active = load_repo_json(
        repo_root,
        "stats/read-models/active/stress_recovery_window_summary.profile.json",
    )
    active["name"] = "titan_summon_summary"
    active["surface_ref"] = "generated/titan_summon_summary.min.json"
    active["catalog_order"] = 26
    write_repo_json(repo_root, active_ref, active)

    with pytest.raises(ValueError, match="duplicate surface profile name"):
        load_surface_profiles(repo_root / "stats/read-models")


def test_retired_output_name_cannot_alias_an_active_output(tmp_path: Path) -> None:
    repo_root = copy_repo(tmp_path)
    active_ref = "stats/read-models/active/stress_recovery_window_summary.profile.json"
    active = load_repo_json(repo_root, active_ref)
    active["surface_ref"] = "generated/titan_summon_summary.min.json"
    write_repo_json(repo_root, active_ref, active)

    with pytest.raises(ValueError, match="duplicate managed surface output name"):
        load_surface_profiles(repo_root / "stats/read-models")


def test_retired_catalog_slot_cannot_be_reused_by_an_active_profile(
    tmp_path: Path,
) -> None:
    repo_root = copy_repo(tmp_path)
    active_ref = "stats/read-models/active/stress_recovery_window_summary.profile.json"
    active = load_repo_json(repo_root, active_ref)
    active["catalog_order"] = 21
    write_repo_json(repo_root, active_ref, active)

    with pytest.raises(ValueError, match="duplicate surface catalog slot: 21"):
        load_surface_profiles(repo_root / "stats/read-models")


def test_retired_profile_requires_its_former_catalog_slot(tmp_path: Path) -> None:
    repo_root = copy_repo(tmp_path)
    retired_ref = "stats/read-models/retired/titan_summon_summary.profile.json"
    retired = load_repo_json(repo_root, retired_ref)
    del retired["former_catalog_order"]
    write_repo_json(repo_root, retired_ref, retired)

    issues = validator.validate(repo_root)

    assert any(
        retired_ref in issue and "former_catalog_order" in issue for issue in issues
    )


def test_retired_profile_requires_complete_cleanup_scope(tmp_path: Path) -> None:
    repo_root = copy_repo(tmp_path)
    retired_ref = "stats/read-models/retired/titan_summon_summary.profile.json"
    retired = load_repo_json(repo_root, retired_ref)
    retired["cleanup_scopes"].remove("consumer_hints")
    write_repo_json(repo_root, retired_ref, retired)

    issues = validator.validate(repo_root)

    assert any(
        "cleanup_scopes must name the complete retired cleanup set" in issue
        for issue in issues
    )


def test_root_contract_and_output_districts_remain_active() -> None:
    manifest = load_json("stats/source_home.manifest.json")
    posture = {
        entry["path"]: entry["status"]
        for entry in manifest["current_root_route_posture"]
    }

    assert posture["schemas/"] == "active_canonical_contract_district"
    assert posture["generated/"] == "active_committed_derived_output_district"
    assert posture["src/aoa_stats_builder/"] == "active_implementation_district"
    assert posture["scripts/"] == "active_public_and_compatibility_entrypoint_district"


def test_read_model_validator_routes_reach_each_part_local_proof_owner() -> None:
    manifest = load_json("stats/source_home.manifest.json")
    read_models = next(
        family for family in manifest["families"] if family["id"] == "read_models"
    )
    topology = load_json("mechanics/topology.json")
    validator_routes = set(read_models["validator_routes"])
    focused_part_count = 0

    for package in topology["active_packages"]:
        for part in package["active_part_routes"]:
            if (
                "read_models" not in part["stats_source_family_refs"]
                or "tests" not in part["localized_payload_roots"]
            ):
                continue
            focused_part_count += 1
            part_root = (
                REPO_ROOT
                / "mechanics"
                / package["path"]
                / "parts"
                / part["path"]
            )
            test_refs = {
                path.relative_to(REPO_ROOT).as_posix()
                for path in (part_root / "tests").glob("test_*.py")
            }
            route = part_root.relative_to(REPO_ROOT).as_posix()

            assert test_refs, route
            assert test_refs & validator_routes, route

    assert focused_part_count
