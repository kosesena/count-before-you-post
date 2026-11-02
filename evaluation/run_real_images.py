"""Evaluate frozen SCD images using existing SAM and Spark perception, without ERP writes.
Usage: python -m evaluation.run_real_images sample.json output-directory
Public image benchmark, not field deliveries or an end-to-end document/audio evaluation.
"""
import concurrent.futures
import hashlib
import json
import statistics
import sys
import time
from pathlib import Path
from cbyp.sam import segment_image, parse
from cbyp.perception import look


def run(manifest_path, output):
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text())
    cases = manifest['cases']
    if len(cases) != 30:
        raise ValueError('Freeze all 30 selected images before running.')
    for case in cases:
        if hashlib.sha256(Path(case['file']).read_bytes()).hexdigest() != case['sha256']:
            raise ValueError('Input hash changed: ' + case['id'])
    out = Path(output)
    out.mkdir(exist_ok=False, parents=True)
    (out / 'manifest.json').write_bytes(manifest_path.read_bytes())
    def one(case):
        row = {'id': case['id'], 'sha256': case['sha256'], 'reference_count': case['annotated_visible_count'],
               'total_cost_usd': None, 'erp_written': False}
        start = time.perf_counter()
        for stage in ('sam', 'spark'):
            ts = time.perf_counter()
            try:
                if stage == 'sam':
                    raw = segment_image(case['file'], 'cardboard box')
                    (out / (case['id'] + '-sam.txt')).write_text(raw)
                    confs = [d.conf or 0 for d in parse(raw)]
                    row['sam_count'] = sum(c >= .7 for c in confs)
                    row['sam_sure_count'] = sum(c >= .88 for c in confs)
                    row['sam_confidences'] = confs
                else:
                    row['spark'] = look(case['file'])
                    row['spark_count'] = row['spark']['cartons_visible']
            except Exception as exc:
                row[stage + '_error'] = type(exc).__name__
            row[stage + '_seconds'] = round(time.perf_counter() - ts, 3)
        row['seconds'] = round(time.perf_counter() - start, 3)
        (out / (case['id'] + '.json')).write_text(json.dumps(row, indent=2))
        return row
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for row in pool.map(one, cases):
            rows.append(row)
            print(json.dumps({k: row[k] for k in ('id','reference_count','sam_count','spark_count','sam_error','spark_error') if k in row}), flush=True)
    summary = {'cases': len(rows), 'scope': 'Visible annotated carton benchmark; no physical-total or field-ROI claim',
               'total_cost_usd': None, 'median_pipeline_seconds': statistics.median(r['seconds'] for r in rows)}
    for stage in ('sam', 'spark'):
        valid = [r for r in rows if stage + '_count' in r]
        summary[stage] = {'completed': len(valid), 'failures': len(rows)-len(valid),
                         'exact_matches': sum(r[stage+'_count']==r['reference_count'] for r in valid),
                         'mean_absolute_error': statistics.mean(abs(r[stage+'_count']-r['reference_count']) for r in valid) if valid else None}
    (out / 'results.json').write_text(json.dumps({'summary': summary, 'rows': rows}, indent=2))
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    run(*sys.argv[1:])
