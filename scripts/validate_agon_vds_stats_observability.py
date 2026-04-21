from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/'generated'/'agon_vds_stats_observability_registry.min.json'
def validate():
    d=json.loads(REGISTRY.read_text(encoding='utf-8'))
    assert d['registry_id']=='agon.vds_stats_observability.registry.v1'
    assert d['wave']=='XI' and d['live_protocol'] is False and d['runtime_effect']=='none'
    assert d['summary_count']>=5
    ids=[]
    for item in d['summaries']:
        assert item.get('must_not_emit')
        assert item.get('may_emit') is not None

    assert 'no_stats_authority' in d['stop_lines']
    assert 'no_value_system' in d['stop_lines']
    return d
if __name__=='__main__':
    d=validate(); print('validated {count} VDS stats summaries'.format(count=d['summary_count']))
