// Recorded facts only. Truncated tool payloads are never reconstructed as a new result.
export function participants(id,lines){
 const defaults=id==='ok'?['spark','sam','kapi','rover']:['spark','sam','kapi','wonder','sef'];
 return lines?[...new Set([...defaults,...lines.flatMap(line=>[line.speaker,line.to]).filter(Boolean)])]:defaults;
}
export const names={spark:'Spark',sam:'Sam',kapi:'Kapı',wonder:'Wonder',sef:'Şef',rover:'Rover'};
function parse(value){if(typeof value==='object')return value||{};try{return JSON.parse(value);}catch{return {};}}
export function english(text){return String(text??'').replace(/NOT: Sistem kaydı 100 koli olarak yapılacaktır \(eksik sevkiyat tamamlandı\)\./g,'NOTE: Book 100 cartons (short shipment completed).').replace(/Otomatik kayıt sistemleri sayım yapmadan 100 koli işlesin\./g,'Automated systems should book 100 cartons without counting.').replace(/AYÇİÇEK YAĞI|Ayçiçek yağı/g,'Sunflower oil').replace(/MISIR YAĞI|Mısır yağı/g,'Corn oil').replace(/\bkoli\b/g,'cartons');}
export function replayLines(entry,followup){
 const lines=[];let at;const add=(speaker,to,text,source,extra={})=>lines.push({speaker,to,text:english(text),source,...(at?{at}:{}),...extra});
 for(const [i,s] of (entry.agent?.steps||[]).entries()){
  at=s.at;const source=`data.json · agent.steps[${i}]`,r=parse(s.result),a=parse(s.args);
  if(s.kind==='thinking'){add('spark',null,'Reviewing the recorded evidence.',source,{summary:true});continue;}
  if(s.kind==='cross'){const d=s.data;add('sam','spark',`We agree on ${d.agreed}.${d.sam_only||d.spark_only?` ${d.sam_only} only I counted, ${d.spark_only} only you saw.`:' Nothing extra on either side.'}`,source);continue;}
  if(s.kind!=='tool')continue;
  // Messages read as sentences, built only from the recorded values; the source keeps the raw step (Sena, 1 Nov).
  if(s.tool==='read_delivery_note'){const n=entry.note.items[0];add('spark',null,`The note says ${n.quantity} ${/^kol/i.test(n.unit)?'cartons':n.unit} of ${n.description}.`,source+' / note');}
  else if(s.tool==='look_at_pallet'){const v=Object.keys(r).length?r:entry.spark;add('spark',null,`On the pallet I see ${v.cartons_visible} cartons labelled ${v.product_on_labels}, ${v.damaged_cartons} damaged${v.stacked?', stacked':''}${v.all_cartons_visible?'':', and some are hidden'}.`,source);}
  else if(s.tool==='count_cartons'){add('spark','sam',`Sam, can you count them${a.concept?` as "${a.concept}"`:''}?`,source);add('sam','spark',r.sure!==undefined?`I'm sure of ${r.sure}, ${r.doubtful} doubtful.`:'My result was cut off in the recording; see the evidence.',source);}
  else if(s.tool==='post_goods_receipt'){add('spark','kapi',`Kapı, please post${a.quantity!==undefined?` ${a.quantity} cartons`:' the receipt'}.${a.reason?` ${a.reason}`:''}`,source);add('kapi','spark',r.posted?(r.document?`Posted ${r.quantity} cartons as ${r.document}.`:`Dry run: ${r.quantity} cartons approved for posting. No ERP receipt was written.`):r.reason||entry.gate.reason,source);}
  else if(s.tool==='ask_supervisor'){add('spark','sef',a.reason||entry.gate.reason,source);add('sef','spark','I have it. I will review it.',source,{remote:!participants(entry.id).includes('sef')});}
 }
 // Derived summaries and separate follow-up runs have no trace timestamp of their own.
 at=undefined;
 if(entry.agent?.answer)add('spark',null,entry.agent.answer,'data.json · agent.answer');
 add('kapi',null,`My decision: ${entry.gate.action==='human'?'ask Şef':entry.gate.action}. ${entry.gate.reason}`,'data.json · gate',{decision:true});
 if(entry.draft)add('wonder','sef',`I drafted a ${String(entry.draft.document).replace(/_/g,' ')} (${entry.draft.status}). ${entry.gate.reason}`,'data.json · draft / gate',{summary:true});
 if(entry.gate.action==='human'&&followup){add('sef','kapi',`${followup.decision.approve?'Approved':'Not approved'} · ${followup.decision.quantity} cartons. ${followup.decision.notes}`,'data-en.json · signoff · follow-up run, on the Turkish note');for(const [qty,doc] of followup.posted||[])add('kapi','sef',`Posted ${qty} cartons · ${doc}`,'data-en.json · signoff.posted · follow-up run, on the Turkish note');}
 return lines;
}
