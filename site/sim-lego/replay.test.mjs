import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {participants,replayLines,english} from './replay.mjs';
const original=JSON.parse(readFileSync(new URL('../data.json',import.meta.url))).cases;
const followup=JSON.parse(readFileSync(new URL('../data-en.json',import.meta.url))).cases;
for(const c of original){
 const lines=replayLines(c,followup.find(x=>x.id===c.id).signoff);
 assert.ok(lines.length>c.agent.steps.length);
 assert.equal(lines.filter(x=>x.decision).length,1);
 const results=c.agent.steps.filter(s=>s.tool==='count_cartons').map(s=>JSON.parse(s.result));
 const replies=lines.filter(x=>x.speaker==='sam'&&x.text.includes("I'm sure of"));
 assert.deepEqual(replies.map(x=>x.text),results.map(r=>`I'm sure of ${r.sure}, ${r.doubtful} doubtful.`));
 assert.ok(lines.every(x=>!x.text.includes('undefined')));
 if(c.agent?.answer)assert.ok(lines.find(x=>x.source==='data.json · agent.answer').text.startsWith('Recorded model summary — not proof of an ERP write:'));
 for(const s of c.agent.steps.filter(s=>s.kind==='thinking'))assert.ok(!lines.some(x=>x.text===s.text));
 assert.ok(participants(c.id).length<=5);
 const team=participants(c.id,lines);
 for(const line of lines)for(const id of [line.speaker,line.to].filter(Boolean))assert.ok(team.includes(id),`${c.id}: missing participant ${id}`);
 if(c.gate.action==='human')assert.ok(lines.some(x=>x.source.includes('follow-up run, on the Turkish note')));
}
console.log('Six recorded replays retain per-step counts, gate decisions and labelled signoffs.');

// Each language must replay its own timestamps and source paths, without borrowing TR signoff.
for(const lang of ['tr','en','de','zh']){
 const file=lang==='tr'?'data.json':`data-${lang}.json`;
 const data=JSON.parse(readFileSync(new URL('../'+file,import.meta.url)));
 assert.equal(data.lang,lang);
 assert.equal(data.cases.length,6);
 for(const entry of data.cases){
  const lines=replayLines(entry,entry.signoff,{language:lang,dataFile:file});
  assert.ok(lines.every(line=>line.source.startsWith(file+' · ')));
  const times=new Set(entry.agent.steps.map(step=>step.at).filter(Boolean));
  for(const line of lines.filter(line=>line.at))assert.ok(times.has(line.at));
  if(lang!=='tr')assert.ok(lines.every(line=>!line.source.includes('signoff')));
  assert.ok(lines.some(line=>line.decision&&line.text.includes(english(entry.gate.reason))));
  for(const key of ['note','camera'])assert.ok(readFileSync(new URL('../'+entry.images[key],import.meta.url)).length>0);
 }
}
console.log('All 24 language/scenario recordings retain their own sources, times and evidence assets.');
