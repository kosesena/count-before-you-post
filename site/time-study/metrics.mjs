export function summarize(rows){
 const ids=[...new Set(rows.map(r=>r.case_id))];
 const pairs=ids.map(id=>{const a=rows.find(r=>r.case_id===id&&r.mode==='manual'),b=rows.find(r=>r.case_id===id&&r.mode==='assisted');return a&&b?{case_id:id,manual_seconds:a.active_seconds,assisted_seconds:b.active_seconds,both_correct:a.correct&&b.correct,interrupted:a.interrupted||b.interrupted}:null}).filter(Boolean);
 const eligible=pairs.filter(p=>p.both_correct&&!p.interrupted);
 const mean=x=>x.length?x.reduce((a,b)=>a+b,0)/x.length:null;
 return {completed_trials:rows.length,paired_cases:pairs.length,correct_manual:rows.filter(r=>r.mode==='manual'&&r.correct).length,correct_assisted:rows.filter(r=>r.mode==='assisted'&&r.correct).length,eligible_pairs:eligible.length,mean_manual_seconds:mean(eligible.map(p=>p.manual_seconds)),mean_assisted_review_seconds:mean(eligible.map(p=>p.assisted_seconds)),mean_review_seconds_difference:mean(eligible.map(p=>p.manual_seconds-p.assisted_seconds)),pairs,scope:'Human screen-review time only, prerecorded assistance, synthetic scenes. Excludes upload, model latency and physical warehouse work. Paired repeats have learning bias. Not field savings.'};
}
