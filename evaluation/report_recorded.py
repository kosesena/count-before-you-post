"""Offline report of historical runs; never call historical dry runs real ERP writes."""
import json
import statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def report():
    groups={}
    for lang in ('tr','en','de','zh'):
        rows=json.loads((ROOT/f'experiments/results/timed/{lang}/agent_warehouse_cross.json').read_text())
        for gated in (False,True):
            selected=[r for r in rows if r['gate']==gated]
            posted=[r for r in selected if r['posted']]
            groups[f'{lang}/'+('gated' if gated else 'ungated')]={
                'cases':len(selected),'proposed_receipts':len(posted),
                'policy_violations':sum(r['expected']!='post' for r in posted),
                'real_erp_documents':sum(bool(doc) for r in selected for q,doc in r['posted']),
                'median_seconds':statistics.median(r['seconds'] for r in selected),
                'total_cost_usd':None,'physical_quantity_accuracy':None,
                'note':'Policy truth only. Do not label every violation a wrong physical count.'}
    return {'dataset':'six synthetic cases × four languages; historical core profile',
            'independent_real_deliveries':0,'field_time_saved':None,'groups':groups}
if __name__=='__main__':print(json.dumps(report(),ensure_ascii=False,indent=2))
