from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aoa_stats_builder.downstream_canaries import validate_downstream_canaries  # noqa: E402


def test_downstream_canaries_pass_for_current_workspace() -> None:
    result = validate_downstream_canaries(workspace_root=ROOT.parent)
    assert result["errors"] == []
    assert len(result["checked"]) + len(result["skipped"]) >= 4


def test_downstream_canaries_report_missing_needles(tmp_path: Path) -> None:
    sdk = tmp_path / "aoa-sdk" / "docs"
    sdk.mkdir(parents=True)
    (sdk / "aoa-surface-detection-second-wave.md").write_text(
        "aoa-stats is here but the warning text is gone\n",
        encoding="utf-8",
    )

    result = validate_downstream_canaries(workspace_root=tmp_path)

    assert any("aoa-sdk/docs/aoa-surface-detection-second-wave.md" in error for error in result["errors"])


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
