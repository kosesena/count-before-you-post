import {test} from 'node:test';
import assert from 'node:assert/strict';
import {analyze} from '../evaluation/analyze_time_study.mjs';
const cases=[{id:'one',expected:'block'}];
const row=mode=>({case_id:'one',mode,answer:'block',expected:'block',correct:true,active_seconds:3,wall_seconds:4,interrupted:false});
const report=()=>({version:2,trials:[row('manual'),row('assisted')]});
test('recomputes complete exports',()=>assert.equal(analyze(report(),cases).summary.eligible_pairs,1));
test('rejects missing and duplicate trials',()=>{assert.throws(()=>analyze({version:2,trials:[row('manual')]},cases));assert.throws(()=>analyze({version:2,trials:[row('manual'),row('manual')]},cases));});
test('rejects forged correctness and invalid measurements',()=>{const r=report();r.trials[0].correct=false;assert.throws(()=>analyze(r,cases));r.trials[0].correct=true;r.trials[0].active_seconds=-1;assert.throws(()=>analyze(r,cases));});
test('keeps translated UI language separate from original evidence',()=>{
 const r={...report(),version:3,ui_language:'de',evidence_language:'tr'};
 const out=analyze(r,cases);assert.equal(out.ui_language,'de');assert.equal(out.evidence_language,'tr');assert.equal(out.version,3);
 for(const change of [{ui_language:'fr'},{evidence_language:'de'},{ui_language:undefined}])assert.throws(()=>analyze({...r,...change},cases));
});
