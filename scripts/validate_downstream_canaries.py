#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder.downstream_canaries import validate_downstream_canaries  # noqa: E402


def main() -> int:
    result = validate_downstream_canaries(workspace_root=REPO_ROOT.parent)
    if result["errors"]:
        print("Downstream canary validation failed.")
        for error in result["errors"]:
            print(f"- {error}")
        return 1
    print(
        f"[ok] validated downstream canaries across {len(result['checked'])} repos"
    )
    if result["skipped"]:
        print("[skipped] " + ", ".join(sorted(result["skipped"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
