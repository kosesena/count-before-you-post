// Recompute human-study summaries from raw trials; never pool different UI versions.
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import {summarize} from '../site/time-study/metrics.mjs';
export function analyze(report,cases){
 if(![1,2,3].includes(report.version)||!Array.isArray(report.trials))throw Error('Unsupported study export.');
 if(report.version===3&&(!['tr','en','de','zh'].includes(report.ui_language)||report.evidence_language!=='tr'))throw Error('Invalid language metadata.');
 const truth=new Map(cases.map(c=>[c.id,c.expected]));
 const seen=new Set();
 const rows=report.trials.map(r=>{
  const key=r.case_id+':'+r.mode;
  if(!truth.has(r.case_id)||!['manual','assisted'].includes(r.mode)||seen.has(key))throw Error('Unknown or duplicate trial.');
  seen.add(key);
  if(!['post','block','human'].includes(r.answer)||![r.active_seconds,r.wall_seconds].every(n=>Number.isFinite(n)&&n>=0)||typeof r.interrupted!=='boolean')throw Error('Invalid trial measurement.');
  if(r.expected!==truth.get(r.case_id)||r.correct!==(r.answer===truth.get(r.case_id)))throw Error('Export disagrees with the configured case policy.');
  return r;
 });
 if(rows.length!==2*truth.size)throw Error('Incomplete study; all paired trials are required.');
 return {version:report.version,ui_language:report.ui_language||'tr',evidence_language:report.evidence_language||'tr',completed_at:report.completed_at,prior_familiarity_self_reported:report.prior_familiarity,
  summary:summarize(rows),unsafe_accepts:{manual:rows.filter(r=>r.mode==='manual'&&r.answer==='post'&&r.expected!=='post').length,assisted:rows.filter(r=>r.mode==='assisted'&&r.answer==='post'&&r.expected!=='post').length},
  limitations:['Single-participant screen review, not warehouse time savings.','Repeated cases and previous exposure can change results.','Different UI versions are reported separately; no pooled improvement claim.','Assistance excludes model waiting time.']};
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const files=process.argv.slice(2);if(!files.length)throw Error('Provide one or more exported study JSON files.');
 const cases=JSON.parse(fs.readFileSync(new URL('../site/data.json',import.meta.url))).cases;
 console.log(JSON.stringify({studies:files.map(f=>analyze(JSON.parse(fs.readFileSync(f)),cases)),pooled:false},null,2));
}
