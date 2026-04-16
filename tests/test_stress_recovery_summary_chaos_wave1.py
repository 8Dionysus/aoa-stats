from __future__ import annotations

import json
import os
from pathlib import Path

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> object:
    return json.loads((REPO_ROOT / relative_path).read_text(encoding="utf-8"))


def neighbor_root(env_name: str, repo_name: str) -> Path | None:
    for candidate in (
        os.environ.get(env_name),
        str((REPO_ROOT / repo_name).resolve()),
        str((REPO_ROOT / ".deps" / repo_name).resolve()),
        str((REPO_ROOT.parent / repo_name).resolve()),
    ):
        if candidate and Path(candidate).exists():
            return Path(candidate).resolve()
    return None


def assert_repo_ref_matches_neighbor(repo_ref: str, env_name: str, repo_name: str) -> None:
    prefix = f"repo:{repo_name}/"
    assert repo_ref.startswith(prefix)
    repo_root = neighbor_root(env_name, repo_name)
    if repo_root is None:
        return
    assert (repo_root / repo_ref.removeprefix(prefix)).is_file(), repo_ref


def test_stress_recovery_chaos_wave1_docs_are_discoverable_and_bounded() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    docs_readme = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    guide = (REPO_ROOT / "docs" / "STRESS_RECOVERY_WINDOW_SUMMARIES.md").read_text(
        encoding="utf-8"
    )
    chaos = (
        REPO_ROOT / "docs" / "STRESS_RECOVERY_SUMMARIES_CHAOS_WAVE1.md"
    ).read_text(encoding="utf-8")
    roadmap = (REPO_ROOT / "ROADMAP.md").read_text(encoding="utf-8")

    assert "docs/STRESS_RECOVERY_SUMMARIES_CHAOS_WAVE1.md" in readme
    assert "STRESS_RECOVERY_SUMMARIES_CHAOS_WAVE1.md" in docs_readme
    assert "stress_recovery_window_summary.chaos-wave1.example.json" in readme
    assert "stress_recovery_window_summary.chaos-wave1.example.json" in roadmap
    assert "bounded chaos-wave example" in guide

    for token in (
        "One compact summary example is enough for wave 1.",
        "synthetic health truth",
        'global "system got smarter" claims',
    ):
        assert token in chaos


def test_stress_recovery_chaos_wave1_example_and_schema_validate() -> None:
    schema = load_json("schemas/stress_recovery_window_summary_v1.json")
    example = load_json("examples/stress_recovery_window_summary.chaos-wave1.example.json")

    assert isinstance(schema, dict)
    assert isinstance(example, dict)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(example)


def test_stress_recovery_chaos_wave1_example_refs_existing_neighbor_surfaces() -> None:
    payload = load_json("examples/stress_recovery_window_summary.chaos-wave1.example.json")
    assert isinstance(payload, dict)
    assert_repo_ref_matches_neighbor(
        "repo:aoa-kag/examples/projection_health_receipt.retrieval-outage-honesty.example.json",
        "AOA_KAG_ROOT",
        "aoa-kag",
    )
    assert_repo_ref_matches_neighbor(
        "repo:aoa-evals/bundles/aoa-stress-recovery-window/reports/example-report.json",
        "AOA_EVALS_ROOT",
        "aoa-evals",
    )
    assert_repo_ref_matches_neighbor(
        "repo:aoa-evals/examples/runtime_evidence_selection.return-anchor-integrity.example.json",
        "AOA_EVALS_ROOT",
        "aoa-evals",
    )
    assert_repo_ref_matches_neighbor(
        "repo:aoa-routing/examples/stress_navigation_hint.timeout-chaos.example.json",
        "AOA_ROUTING_ROOT",
        "aoa-routing",
    )
    assert_repo_ref_matches_neighbor(
        "repo:aoa-routing/examples/composite_stress_route_hint.retrieval-outage-honesty.example.json",
        "AOA_ROUTING_ROOT",
        "aoa-routing",
    )
    assert_repo_ref_matches_neighbor(
        "repo:aoa-memo/examples/pattern.antifragility-stress-recovery-window.example.json",
        "AOA_MEMO_ROOT",
        "aoa-memo",
    )

    inputs = payload["inputs"]
    assert isinstance(inputs, dict)
    assert "repo:aoa-kag/examples/projection_health_receipt.retrieval-outage-honesty.example.json" in inputs["receipt_refs"]
    assert "repo:aoa-evals/bundles/aoa-stress-recovery-window/reports/example-report.json" in inputs["eval_report_refs"]
    assert "repo:aoa-evals/examples/runtime_evidence_selection.return-anchor-integrity.example.json" in inputs["eval_report_refs"]
    assert "repo:aoa-routing/examples/stress_navigation_hint.timeout-chaos.example.json" in inputs["route_hint_refs"]
    assert "repo:aoa-routing/examples/composite_stress_route_hint.retrieval-outage-honesty.example.json" in inputs["route_hint_refs"]
    assert "repo:aoa-memo/examples/pattern.antifragility-stress-recovery-window.example.json" in inputs["memo_context_refs"]

    assert payload["scope"]["owner_surface"] == "runtime-chaos-recovery"
    assert payload["summary"]["trust_calibration"] == 0.9
    assert "retrieval-outage-held-source-first" in payload["trend_flags"]
