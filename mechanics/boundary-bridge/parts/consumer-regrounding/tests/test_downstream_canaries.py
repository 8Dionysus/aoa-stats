from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aoa_stats_builder.downstream_canaries import validate_downstream_canaries  # noqa: E402


def _write_sdk_canaries(root: Path) -> None:
    surface = (
        root
        / "mechanics/recurrence/parts/downstream-projection-guard/"
        "docs/stats-regrounding-policy.md"
    )
    surface.parent.mkdir(parents=True, exist_ok=True)
    surface.write_text(
        "Stats says what is derived and where its feed is thin.\n"
        "Owner repos still decide source truth.\n",
        encoding="utf-8",
    )
    contract = (
        root
        / "mechanics/boundary-bridge/parts/"
        "consumed-surface-posture-gate/docs/routing-consumer-contract.md"
    )
    contract.parent.mkdir(parents=True, exist_ok=True)
    contract.write_text(
        "aoa-stats/generated/stress_recovery_window_summary.min.json\n"
        "The consumer must not require an `aoa-routing` checkout.\n",
        encoding="utf-8",
    )


def test_downstream_canaries_pass_for_current_workspace() -> None:
    result = validate_downstream_canaries(workspace_root=ROOT.parent)
    assert result["errors"] == []
    assert len(result["checked"]) + len(result["skipped"]) >= 4


def test_downstream_canaries_report_missing_needles(tmp_path: Path) -> None:
    sdk = (
        tmp_path
        / "aoa-sdk/mechanics/recurrence/parts/downstream-projection-guard/docs"
    )
    sdk.mkdir(parents=True)
    (sdk / "stats-regrounding-policy.md").write_text(
        "aoa-stats is here but the warning text is gone\n",
        encoding="utf-8",
    )

    result = validate_downstream_canaries(workspace_root=tmp_path)

    assert any(
        "aoa-sdk/mechanics/recurrence/parts/downstream-projection-guard/"
        "docs/stats-regrounding-policy.md"
        in error
        for error in result["errors"]
    )


def test_downstream_canaries_reject_missing_contract_in_available_owner_checkout(
    tmp_path: Path,
) -> None:
    (tmp_path / "aoa-sdk").mkdir()

    result = validate_downstream_canaries(workspace_root=tmp_path)

    assert any(
        "aoa-sdk/mechanics/boundary-bridge/parts/"
        "consumed-surface-posture-gate/docs/routing-consumer-contract.md"
        in error
        and "required downstream canary is missing" in error
        for error in result["errors"]
    )


def test_downstream_canaries_use_sdk_routing_owner_without_predecessor_checkout(
    tmp_path: Path,
) -> None:
    contract = (
        tmp_path
        / "aoa-sdk"
        / "mechanics"
        / "boundary-bridge"
        / "parts"
        / "consumed-surface-posture-gate"
        / "docs"
        / "routing-consumer-contract.md"
    )
    contract.parent.mkdir(parents=True)
    contract.write_text(
        "aoa-stats/generated/stress_recovery_window_summary.min.json\n",
        encoding="utf-8",
    )

    result = validate_downstream_canaries(workspace_root=tmp_path)

    assert any(
        "aoa-sdk/mechanics/boundary-bridge/parts/"
        "consumed-surface-posture-gate/docs/routing-consumer-contract.md"
        in error
        and "must not require an `aoa-routing` checkout" in error
        for error in result["errors"]
    )


def test_downstream_canaries_prefer_explicit_dependency_root(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    explicit_sdk = tmp_path / "dependencies" / "aoa-sdk"
    _write_sdk_canaries(explicit_sdk)

    result = validate_downstream_canaries(
        workspace_root=workspace,
        repo_roots={"aoa-sdk": explicit_sdk},
    )

    assert result["errors"] == []
    assert {
        label for label in result["checked"] if label.startswith("aoa-sdk/")
    } == {
        (
            "aoa-sdk/mechanics/recurrence/parts/downstream-projection-guard/"
            "docs/stats-regrounding-policy.md"
        ),
        (
            "aoa-sdk/mechanics/boundary-bridge/parts/"
            "consumed-surface-posture-gate/docs/routing-consumer-contract.md"
        ),
    }


def test_downstream_canaries_fail_for_missing_explicit_dependency_root(
    tmp_path: Path,
) -> None:
    result = validate_downstream_canaries(
        workspace_root=tmp_path / "workspace",
        repo_roots={"aoa-sdk": tmp_path / "missing-sdk"},
    )

    assert len(
        [error for error in result["errors"] if error.startswith("aoa-sdk/")]
    ) == 2
    assert not any(label.startswith("aoa-sdk/") for label in result["skipped"])


def test_validator_script_uses_ci_sdk_dependency_root(tmp_path: Path) -> None:
    explicit_sdk = tmp_path / "aoa-sdk"
    _write_sdk_canaries(explicit_sdk)
    env = os.environ.copy()
    env["AOA_SDK_ROOT"] = str(explicit_sdk)
    env.pop("AOA_MEMO_ROOT", None)
    env.pop("AOA_EVALS_ROOT", None)

    completed = subprocess.run(
        [sys.executable, "scripts/validate_downstream_canaries.py"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "validated downstream canaries across 2 repos" in completed.stdout
