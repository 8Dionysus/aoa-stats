#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder.receipt_abi import validate_receipt_abi_governance  # noqa: E402


def main() -> int:
    errors = validate_receipt_abi_governance(repo_root=REPO_ROOT, workspace_root=REPO_ROOT.parent)
    if errors:
        print("Receipt ABI governance validation failed.")
        for error in errors:
            print(f"- {error}")
        return 1
    print("[ok] validated stats receipt ABI governance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
