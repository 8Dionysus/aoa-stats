from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from typing import Any


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def parse_iso_datetime(value: Any) -> datetime | None:
    if not is_nonempty_string(value):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if is_nonempty_string(item)]


def parse_iso_datetime_or_min(value: Any) -> datetime:
    parsed = parse_iso_datetime(value)
    if parsed is None:
        return datetime.min.replace(tzinfo=UTC)
    return parsed


def collect_datetime_candidates(value: Any) -> list[datetime]:
    parsed = parse_iso_datetime(value)
    if parsed is not None:
        return [parsed]
    if isinstance(value, dict):
        candidates: list[datetime] = []
        for item in value.values():
            candidates.extend(collect_datetime_candidates(item))
        return candidates
    if isinstance(value, list):
        candidates = []
        for item in value:
            candidates.extend(collect_datetime_candidates(item))
        return candidates
    return []


def summary_window_ref(receipts: list[dict[str, Any]]) -> str:
    months = sorted(
        {
            parsed.strftime("%Y-%m")
            for receipt in receipts
            if (parsed := parse_iso_datetime(receipt.get("observed_at"))) is not None
        }
    )
    if not months:
        return "window:unknown"
    if len(months) == 1:
        return f"window:{months[0]}"
    return f"window:{months[0]}..{months[-1]}"


def string_count_map(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted(counter.items()))


def duration_days_between(start_value: Any, end_value: Any) -> float | None:
    start = parse_iso_datetime(start_value)
    end = parse_iso_datetime(end_value)
    if start is None or end is None or end < start:
        return None
    return (end - start).total_seconds() / 86400
