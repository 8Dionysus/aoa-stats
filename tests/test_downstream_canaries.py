from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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
