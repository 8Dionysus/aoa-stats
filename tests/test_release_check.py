from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "release_check.py"


def load_release_check_module():
    spec = importlib.util.spec_from_file_location("release_check", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_repo_candidate_rejects_broken_git_worktree_but_accepts_vendored_tree(
    tmp_path: Path,
) -> None:
    release_check = load_release_check_module()
    broken = tmp_path / "broken-worktree"
    broken.mkdir()
    (broken / ".git").write_text(
        "gitdir: /missing/repository/.git/worktrees/broken\n",
        encoding="utf-8",
    )
    vendored = tmp_path / "vendored-repo"
    vendored.mkdir()

    assert release_check._usable_repo_candidate(str(broken)) is False
    assert release_check._usable_repo_candidate(str(vendored)) is True
    assert release_check._usable_repo_candidate(str(REPO_ROOT)) is True


def test_release_gate_runs_artifact_roundtrip_without_writing_dist() -> None:
    release_check = load_release_check_module()
    command = next(
        command
        for label, command in release_check.COMMANDS
        if label == "validate OS Abyss summary catalog artifact bundle"
    )

    assert command[-1] == "--ephemeral"


def test_feedback_selects_one_topology_part_without_duplicate_files() -> None:
    release_check = load_release_check_module()

    selected, reason = release_check._feedback_test_selection(
        [
            "mechanics/boundary-bridge/parts/measurement-packet-crossing/schemas/active_organ_agent_local_federation_aggregate_v0.schema.json",
            "mechanics/boundary-bridge/parts/measurement-packet-crossing/README.md",
        ]
    )

    assert reason is None
    assert selected is not None
    assert len(selected) == 5
    assert len(selected) == len(set(selected))
    assert all("measurement-packet-crossing/tests/" in path for path in selected)


def test_feedback_unions_family_tests_with_topology_tests() -> None:
    release_check = load_release_check_module()

    selected, reason = release_check._feedback_test_selection(
        [
            "src/aoa_stats_builder/measurement.py",
            "mechanics/boundary-bridge/parts/measurement-packet-crossing/README.md",
        ]
    )

    assert reason is None
    assert selected is not None
    assert "tests/test_stats_protocol.py" in selected
    assert "mechanics/boundary-bridge/parts/measurement-packet-crossing/tests/test_measurement_packet_crossing.py" in selected
    assert len(selected) == len(set(selected))


def test_feedback_unions_distinct_topology_parts() -> None:
    release_check = load_release_check_module()

    selected, reason = release_check._feedback_test_selection(
        [
            "mechanics/agon/parts/epistemic-observability/config/agon_epistemic_stats_observability.seed.json",
            "mechanics/recurrence/parts/component-manifests/manifests/components/component.agon.epistemic-stats-observability.json",
        ]
    )

    assert reason is None
    assert selected is not None
    assert len(selected) == 2
    assert any("epistemic-observability/tests/" in path for path in selected)
    assert any("component-manifests/tests/" in path for path in selected)


def test_feedback_known_plus_unknown_path_falls_back_to_full_gate() -> None:
    release_check = load_release_check_module()

    selected, reason = release_check._feedback_test_selection(
        [
            "mechanics/agon/parts/epistemic-observability/README.md",
            "docs/uncovered-note.md",
        ]
    )

    assert selected is None
    assert reason == "docs/uncovered-note.md: uncovered path"


@pytest.mark.parametrize(
    ("changed_path", "reason_fragment"),
    [
        ("src/aoa_stats_builder/validation_telemetry.py", "shared family route"),
        ("docs/uncovered-note.md", "uncovered path"),
    ],
)
def test_feedback_expands_shared_or_unknown_paths_to_full_gate(
    changed_path: str, reason_fragment: str
) -> None:
    release_check = load_release_check_module()

    selected, reason = release_check._feedback_test_selection([changed_path])

    assert selected is None
    assert reason is not None and reason_fragment in reason


def test_feedback_rejects_escaping_changed_paths() -> None:
    release_check = load_release_check_module()

    with pytest.raises(SystemExit) as error:
        release_check._feedback_test_selection(["../etc/passwd"])

    assert error.value.code == 2


def test_feedback_falls_back_when_authored_manifest_is_malformed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    release_check = load_release_check_module()
    manifest = tmp_path / "source_home.manifest.json"
    manifest.write_text('{"owner_repo":"aoa-stats","families":"broken"}', encoding="utf-8")
    monkeypatch.setattr(release_check, "SOURCE_HOME_MANIFEST", manifest)

    selected, reason = release_check._feedback_test_selection(["src/aoa_stats_builder/measurement.py"])

    assert selected is None
    assert reason == "malformed or unavailable authored mapping metadata"
