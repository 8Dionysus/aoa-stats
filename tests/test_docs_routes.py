from __future__ import annotations

import importlib.util
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REFRESH_LIVE_STATS_PATH = REPO_ROOT / "scripts" / "refresh_live_stats.py"


def load_refresh_live_stats_module():
    spec = importlib.util.spec_from_file_location("refresh_live_stats", REFRESH_LIVE_STATS_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


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


def test_live_session_docs_match_profile_derived_refresh_inventories() -> None:
    refresh_live_stats = load_refresh_live_stats_module()
    docs = read_text(
        "mechanics/recurrence/parts/live-receipt-refresh/docs/LIVE_SESSION_USE.md"
    )

    live_section = docs.split("## Default live command", 1)[1].split("## What the builder accepts", 1)[0]
    committed_section = docs.split("## Canonical repo surfaces", 1)[1].split(
        "## Live local surfaces", 1
    )[0]
    documented_live = tuple(
        re.findall(r"^- `state/generated/([^`]+\.min\.json)`$", live_section, re.MULTILINE)
    )
    documented_committed = tuple(
        re.findall(r"^- `generated/([^`]+\.min\.json)`$", committed_section, re.MULTILINE)
    )

    assert documented_live == refresh_live_stats.SUMMARY_OUTPUT_NAMES
    assert documented_committed == refresh_live_stats.MANAGED_SUMMARY_OUTPUT_NAMES
