from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


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


def test_live_stats_source_home_passes_before_mechanics_integration() -> None:
    assert validator.validate(REPO_ROOT, require_mechanics=False) == []


def test_source_home_contains_only_declared_source_records() -> None:
    stats_root = REPO_ROOT / "stats"
    active_profiles = sorted(
        path.relative_to(stats_root).as_posix()
        for path in (stats_root / "read-models" / "active").glob("*.profile.json")
    )
    deferred_profiles = sorted(
        path.relative_to(stats_root).as_posix()
        for path in (stats_root / "read-models" / "deferred").glob("*.profile.json")
    )
    expected_json = {
        "source_home.manifest.json",
        "intake-contract/event-kind-registry.json",
        "intake-contract/examples/session_harvest_family.receipts.example.json",
        "read-models/surface-profile.schema.json",
        *active_profiles,
        *deferred_profiles,
    }

    assert not list(stats_root.rglob("*.py"))
    assert {
        path.relative_to(stats_root).as_posix() for path in stats_root.rglob("*.json")
    } == expected_json
    assert {path.name for path in stats_root.iterdir()} == {
        "AGENTS.md",
        "README.md",
        "source_home.manifest.json",
        "intake-contract",
        "operation-contracts",
        "read-models",
        "surface-catalog",
    }


def test_source_families_name_meaning_ceiling_and_current_routes() -> None:
    manifest = load_json("stats/source_home.manifest.json")
    families = {family["id"]: family for family in manifest["families"]}

    assert set(families) == {
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


def test_authored_profiles_are_the_public_catalog_source() -> None:
    active, deferred = load_surface_profiles(REPO_ROOT / "stats" / "read-models")
    public_active, public_deferred = public_surface_profiles(
        REPO_ROOT / "stats" / "read-models"
    )
    catalog = load_json("generated/summary_surface_catalog.min.json")

    assert len(active) == 25
    assert len(deferred) == 1
    assert [profile["catalog_order"] for profile in active] == list(range(1, 26))
    assert catalog["surfaces"] == public_active
    assert catalog["deferred_contract_surfaces"] == public_deferred
    assert all("mechanic_routes" not in entry for entry in catalog["surfaces"])
    assert all("catalog_order" not in entry for entry in catalog["surfaces"])


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
