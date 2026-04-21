from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
GENERATED = ROOT / 'generated/agon_sophian_stats_observability_registry.min.json'
SCRIPT = ROOT / 'scripts/build_agon_sophian_stats_observability_registry.py'
VALIDATOR = ROOT / 'scripts/validate_agon_sophian_stats_observability_registry.py'
EXPECTED_COUNT = 6
ITEM_KEY = 'sophian_stats_summaries'

def test_generated_registry_shape():
    reg = json.loads(GENERATED.read_text(encoding='utf-8'))
    assert reg['wave'] == 'XVIII'
    assert reg['count'] == EXPECTED_COUNT
    assert len(reg[ITEM_KEY]) == EXPECTED_COUNT
    assert all(item.get('live_protocol') is False for item in reg[ITEM_KEY])
    assert all(item.get('review_status') == 'candidate_only' for item in reg[ITEM_KEY])

def test_builder_check():
    result = subprocess.run([sys.executable, str(SCRIPT), '--check'], cwd=str(ROOT), text=True, capture_output=True)
    assert result.returncode == 0, result.stderr


def test_validator():
    result = subprocess.run([sys.executable, str(VALIDATOR)], cwd=str(ROOT), text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
