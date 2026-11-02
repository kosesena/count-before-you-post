"""Evaluation utilities: policy compliance is not the same metric as physical accuracy."""
import hashlib
import json
import math
import statistics
from pathlib import Path


def summarize(rows):
    """Truth must be written by the human before model runs. Unknown is never counted correct."""
    totals = {k: 0 for k in ('cases','eligible','correct_accept','unsafe_accept','unnecessary_review','correct_hold','quantity_errors','quantity_assessed','technical_failures','physical_count_assessed','physical_count_errors')}
    times=[];costs=[]
    for row in rows:
        truth=row['truth'];result=row['result'];totals['cases']+=1
        expected=truth['action']=='post'
        if type(truth.get('physical_count')) is int and type(row.get('observed_count')) is int:
            totals['physical_count_assessed']+=1
            totals['physical_count_errors']+=row['observed_count']!=truth['physical_count']
        # Failed calls can still incur charges; include them in complete billing.
        cost = row.get('total_cost_usd')
        if type(cost) in (int, float) and math.isfinite(cost) and cost >= 0:
            costs.append(cost)
        if result.get('action')=='error':
            totals['technical_failures']+=1
            totals['eligible']+=expected
            continue
        accept=result.get('action')=='post'
        totals['eligible']+=expected
        totals['correct_accept']+=accept and expected and result.get('quantity')==truth.get('quantity')
        totals['unsafe_accept']+=accept and (not expected or result.get('quantity')!=truth.get('quantity'))
        totals['unnecessary_review']+=not accept and expected
        totals['correct_hold']+=not accept and not expected
        if accept and truth.get('quantity') is not None:
            totals['quantity_assessed']+=1
            totals['quantity_errors']+=result.get('quantity')!=truth['quantity']
        if isinstance(row.get('seconds'),(int,float)):times.append(row['seconds'])
    return totals | {'median_seconds':statistics.median(times) if times else None,
                     'measured_cost_cases':len(costs),'total_cost_usd':sum(costs) if len(costs)==len(rows) and rows else None,
                     'automatic_correct_accept_rate':totals['correct_accept']/totals['eligible'] if totals['eligible'] else None}


def freeze(manifest, target):
    """Seal the new test set and truth before calling models. Never silently replace a seal."""
    manifest=Path(manifest);data=json.loads(manifest.read_text());entries=[]
    for case in data['cases']:
        if case.get('split') != 'held_out' or not case.get('truth'):
            raise ValueError('Each case needs held_out split and independent human truth.')
        files={}
        for key in ('note','camera','audio'):
            path=(manifest.parent / case[key]).resolve()
            files[key]={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        entries.append(case | {'files':files})
    if not entries:raise ValueError('Cannot seal an empty test set.')
    payload=json.dumps({'cases':entries},ensure_ascii=False,sort_keys=True,indent=2)
    with Path(target).open('x') as f:f.write(payload)
    return hashlib.sha256(payload.encode()).hexdigest()
