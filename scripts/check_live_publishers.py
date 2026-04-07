#!/usr/bin/env python3
from __future__ import annotations

import argparse
import traceback
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_views import ReceiptValidationError, load_receipts
from refresh_live_stats import DEFAULT_FEDERATION_ROOT, DEFAULT_REGISTRY, load_registry, resolve_source_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit required owner-local live receipt publishers for existence, readability, and receipt compatibility."
    )
    parser.add_argument(
        "--registry",
        default=str(DEFAULT_REGISTRY),
        help="Path to the JSON registry that lists owner-local receipt sources.",
    )
    parser.add_argument(
        "--federation-root",
        default=str(DEFAULT_FEDERATION_ROOT),
        help="Federation root used to resolve repo-relative receipt source paths.",
    )
    parser.add_argument(
        "--require-non-empty",
        action="store_true",
        help="Fail when a required source exists but currently contains zero receipts.",
    )
    return parser.parse_args(argv)


def isoformat_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat().replace(
        "+00:00", "Z"
    )


def audit_live_publishers(
    *,
    registry_path: Path,
    federation_root: Path,
    require_non_empty: bool,
) -> tuple[list[dict[str, Any]], list[str]]:
    registry = load_registry(registry_path)
    audits: list[dict[str, Any]] = []
    errors: list[str] = []

    for source in registry["sources"]:
        if not isinstance(source, dict):
            errors.append(f"{registry_path}: each source must be an object")
            continue
        label, path = resolve_source_path(
            source,
            registry_path=registry_path,
            federation_root=federation_root,
        )
        required = source.get("required", True)
        if not isinstance(required, bool):
            errors.append(f"{registry_path}: source {source.get('name')!r} required must be boolean")
            continue

        audit: dict[str, Any] = {
            "name": str(source.get("name") or "unnamed-source"),
            "label": label,
            "path": str(path),
            "required": required,
            "status": "unknown",
            "receipt_count": 0,
            "event_kinds": [],
            "modified_at": None,
        }

        if not path.exists():
            audit["status"] = "missing" if required else "optional-missing"
            audits.append(audit)
            if required:
                errors.append(f"missing required live receipt source: {path}")
            continue

        audit["modified_at"] = isoformat_mtime(path)

        try:
            receipts = load_receipts([path])
        except (OSError, ValueError, ReceiptValidationError) as exc:
            audit["status"] = "invalid"
            audits.append(audit)
            errors.append(f"{label}: {exc}")
            continue
        except Exception as exc:  # pragma: no cover - defensive fallback
            audit["status"] = "invalid"
            audits.append(audit)
            errors.append(f"{label}: unexpected audit failure: {exc}")
            errors.append(traceback.format_exc().strip())
            continue

        audit["receipt_count"] = len(receipts)
        audit["event_kinds"] = sorted(
            {receipt["event_kind"] for receipt in receipts if isinstance(receipt.get("event_kind"), str)}
        )
        if receipts:
            audit["status"] = "ok"
        else:
            audit["status"] = "empty"
            if required and require_non_empty:
                errors.append(f"{label}: required source is empty")
        audits.append(audit)

    return audits, errors


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    registry_path = Path(args.registry).expanduser().resolve()
    federation_root = Path(args.federation_root).expanduser().resolve()

    audits, errors = audit_live_publishers(
        registry_path=registry_path,
        federation_root=federation_root,
        require_non_empty=args.require_non_empty,
    )

    for audit in audits:
        prefix = {
            "ok": "[ok]",
            "empty": "[warn]",
            "optional-missing": "[skip]",
            "missing": "[error]",
            "invalid": "[error]",
        }.get(audit["status"], "[info]")
        detail = (
            f"{prefix} {audit['label']} status={audit['status']} "
            f"receipts={audit['receipt_count']}"
        )
        if audit["event_kinds"]:
            detail += f" event_kinds={','.join(audit['event_kinds'])}"
        if audit["modified_at"]:
            detail += f" modified_at={audit['modified_at']}"
        print(detail)

    if errors:
        print("[fail] live publisher audit found issues")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"[ok] audited {len(audits)} live publishers from {registry_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
