from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_readme_and_docs_map_route_current_direction_through_roadmap() -> None:
    readme = read_text("README.md")
    docs_readme = read_text("docs/README.md")
    roadmap = read_text("ROADMAP.md")

    assert "ROADMAP.md" in readme
    assert "README.md#current-v0-surface" in readme
    assert "../ROADMAP.md" in docs_readme
    assert "../README.md#current-v0-surface" in docs_readme
    assert "current repo-owned direction surface" in roadmap
    assert "README.md#current-v0-surface" in roadmap
    assert "not to widen into a dashboard empire" in roadmap


def test_decision_lane_is_visible_without_becoming_status_roster() -> None:
    readme = read_text("README.md")
    docs_readme = read_text("docs/README.md")
    decisions_readme = read_text("docs/decisions/README.md")
    agents = read_text("AGENTS.md")

    assert "docs/decisions/" in readme
    assert "decisions/README.md" in docs_readme
    assert "docs/decisions/README.md" in agents
    assert "Do not hand-maintain a \"latest decision\" roster" in decisions_readme


def test_agents_routes_design_and_cross_homes_before_roadmap() -> None:
    agents = read_text("AGENTS.md")

    design_step = "2. `DESIGN.md`"
    stats_step = "3. `stats/README.md`"
    mechanics_step = "4. `mechanics/README.md`"
    roadmap_step = "5. `ROADMAP.md`"
    boundaries_step = "6. `docs/BOUNDARIES.md`"

    ordered_steps = [design_step, stats_step, mechanics_step, roadmap_step, boundaries_step]
    for step in ordered_steps:
        assert step in agents
    assert [agents.index(step) for step in ordered_steps] == sorted(
        agents.index(step) for step in ordered_steps
    )


def test_root_routes_expose_design_source_home_and_mechanics() -> None:
    readme = read_text("README.md")
    docs_readme = read_text("docs/README.md")
    design = read_text("DESIGN.md")

    for route in ("DESIGN.md", "stats/README.md", "mechanics/README.md"):
        assert route in readme
        assert f"../{route}" in docs_readme
    assert "The `stats/` source home" in design
    assert "The `mechanics/` operation home" in design
    assert "alternating cross-slices" in design


def test_source_home_entrypoints_route_mutable_status_to_authored_owners() -> None:
    root_agents = read_text("AGENTS.md")
    root_readme = read_text("README.md")
    architecture = read_text("docs/ARCHITECTURE.md")
    docs_readme = read_text("docs/README.md")
    catalog_agents = read_text("stats/surface-catalog/AGENTS.md")
    catalog_readme = read_text("stats/surface-catalog/README.md")
    stats_agents = read_text("stats/AGENTS.md")
    stats_readme = read_text("stats/README.md")
    profiles_readme = read_text("stats/read-models/README.md")
    profiles_agents = read_text("stats/read-models/AGENTS.md")
    mechanics_agents = read_text("mechanics/AGENTS.md")

    for route in (
        "source_home.manifest.json",
        "intake-contract/README.md",
        "read-models/README.md",
        "operation-contracts/README.md",
        "surface-catalog/README.md",
    ):
        assert route in stats_readme

    for route in (
        "surface-profile.schema.json",
        "generated/summary_surface_catalog.min.json",
        "mechanics/topology.json",
        "docs/decisions/README.md",
    ):
        assert route in profiles_readme

    assert (
        "Do not turn this root card into a profile-by-profile status roster"
        in root_agents
    )
    assert "do not hand-maintain mutable" in stats_agents
    assert "Do not maintain profile counts" in profiles_readme
    assert "Do not copy those changing facts into this README" in stats_readme
    assert "Do not copy a mutable stats status roster" in mechanics_agents
    assert "Do not copy named surface state" in profiles_agents
    assert "must not duplicate changing profile counts" in root_agents
    assert "The root README does not\nreplay that changing part inventory" in root_readme
    assert "They are not maintained in this architecture document" in architecture
    assert "not replayed\nas a second part-by-part map here" in docs_readme
    assert "Keep `docs/ARCHITECTURE.md` as the stable public" in catalog_agents
    assert "does not replay the changing\nsurface inventory" in catalog_readme

    assert "## Current canonical routes" not in stats_readme
    assert "The current inventory contains" not in profiles_readme
    for mutable_roster_text in (
        "22 active authored read-model profiles",
        "The managed inventory remains",
        "Current v0 derived views",
        "Owner Landing is retired",
    ):
        assert mutable_roster_text not in root_readme
        assert mutable_roster_text not in architecture


def test_part_local_docs_do_not_keep_migration_redirects() -> None:
    docs_map = read_text("docs/README.md")
    topology = json.loads(read_text("mechanics/topology.json"))
    allowed_root_docs = set(
        topology["root_payload_contract"]["allowed_exact"]["docs"]
    )
    retained_root_routes = {
        route
        for package in topology["active_packages"]
        for part in package["active_part_routes"]
        for route in part["retained_root_routes"]
    }
    routes = {
        "docs/GROWTH_FUNNEL_SUMMARY.md": (
            "mechanics/method-growth/parts/candidate-lineage/docs/"
            "GROWTH_FUNNEL_SUMMARY.md"
        ),
        "docs/RECURRENCE_DERIVED_SUMMARIES.md": (
            "mechanics/recurrence/parts/component-manifests/docs/"
            "RECURRENCE_DERIVED_SUMMARIES.md"
        ),
        "docs/COMPONENT_REFRESH_SUMMARIES.md": (
            "mechanics/recurrence/parts/component-refresh/docs/"
            "COMPONENT_REFRESH_SUMMARIES.md"
        ),
        "docs/DERIVED_SIGNAL_HYGIENE.md": (
            "mechanics/boundary-bridge/parts/consumer-regrounding/docs/"
            "DERIVED_SIGNAL_HYGIENE.md"
        ),
    }

    for former_route, owner_route in routes.items():
        assert not (REPO_ROOT / former_route).exists()
        assert (REPO_ROOT / owner_route).is_file()
        assert owner_route not in docs_map
        assert former_route not in allowed_root_docs
        assert former_route not in retained_root_routes

    assert "../mechanics/README.md" in docs_map
    assert "../mechanics/topology.json" in docs_map
    assert "/parts/" not in docs_map
