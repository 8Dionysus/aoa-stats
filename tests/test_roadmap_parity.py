from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def load_json(relative_path: str) -> dict:
    payload = json.loads((REPO_ROOT / relative_path).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_roadmap_owns_direction_without_replaying_mutable_inventory() -> None:
    roadmap = read_text("ROADMAP.md")
    readme = read_text("README.md")
    changelog = read_text("CHANGELOG.md")
    catalog = load_json("generated/summary_surface_catalog.min.json")

    assert "> Current release: `v0.1.3`" in readme
    assert "## [0.1.3] - 2026-04-23" in changelog
    assert "`v0.1.3`" in roadmap
    assert "derived-observability hardening" in roadmap
    assert "Priority sequence" in roadmap
    assert "alternating cross-slices" in roadmap
    assert "remain weaker than source-owned rollout history" in roadmap
    assert catalog["schema_version"] == "aoa_stats_summary_surface_catalog_v2"
    assert catalog["authority_ref"] == "docs/ARCHITECTURE.md"

    for marker in (
        "## Active summary families",
        "## Maintained contracts",
        "live-admitted read models",
        "managed names",
        "stress_recovery_window_summary.chaos-wave1.example.json",
        "Current v0 derived views",
    ):
        assert marker not in roadmap

    assert "/parts/" not in roadmap
    for surface in catalog["surfaces"]:
        assert surface["name"] not in roadmap


def test_roadmap_routes_exact_state_to_authoritative_surfaces() -> None:
    roadmap = read_text("ROADMAP.md")
    catalog = load_json("generated/summary_surface_catalog.min.json")
    profile_names = {
        load_json(path.relative_to(REPO_ROOT).as_posix())["name"]
        for path in (REPO_ROOT / "stats/read-models/active").glob("*.profile.json")
    }
    assert profile_names == {entry["name"] for entry in catalog["surfaces"]}

    current_routes = (
        "AGENTS.md",
        "DESIGN.md",
        "CHANGELOG.md",
        "stats/README.md",
        "stats/source_home.manifest.json",
        "stats/read-models/",
        "stats/operation-contracts/",
        "stats/intake-contract/",
        "mechanics/README.md",
        "mechanics/topology.json",
        "generated/summary_surface_catalog.min.json",
        "docs/BOUNDARIES.md",
        "docs/ARCHITECTURE.md",
        "docs/SURFACE_STRENGTH_MODEL.md",
        "docs/decisions/README.md",
    )
    for route in current_routes:
        assert (REPO_ROOT / route).exists(), route
        assert route in roadmap

    assert "exact current state" in roadmap
    assert "python scripts/release_check.py" in roadmap
