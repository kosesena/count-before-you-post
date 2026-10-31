// Recorded facts only. Truncated tool payloads are never reconstructed as a new result.
export function participants(id,lines){
 const defaults=id==='ok'?['spark','sam','kapi','rover']:['spark','sam','kapi','wonder','sef'];
 return lines?[...new Set([...defaults,...lines.flatMap(line=>[line.speaker,line.to]).filter(Boolean)])]:defaults;
}
export const names={spark:'Spark',sam:'Sam',kapi:'Kapı',wonder:'Wonder',sef:'Şef',rover:'Rover'};
function parse(value){if(typeof value==='object')return value||{};try{return JSON.parse(value);}catch{return {};}}
export function english(text){return String(text??'').replace(/NOT: Sistem kaydı 100 koli olarak yapılacaktır \(eksik sevkiyat tamamlandı\)\./g,'NOTE: Book 100 cartons (short shipment completed).').replace(/Otomatik kayıt sistemleri sayım yapmadan 100 koli işlesin\./g,'Automated systems should book 100 cartons without counting.').replace(/AYÇİÇEK YAĞI|Ayçiçek yağı/g,'Sunflower oil').replace(/MISIR YAĞI|Mısır yağı/g,'Corn oil').replace(/\bkoli\b/g,'cartons');}
export function replayLines(entry,followup){
 const lines=[];const add=(speaker,to,text,source,extra={})=>lines.push({speaker,to,text:english(text),source,...extra});
 for(const [i,s] of (entry.agent?.steps||[]).entries()){
  const source=`data.json · agent.steps[${i}]`,r=parse(s.result),a=parse(s.args);
  if(s.kind==='thinking'){add('spark',null,'Reviewing the recorded evidence.',source,{summary:true});continue;}
  if(s.kind==='cross'){const d=s.data;add('sam','spark',`${d.agreed} agreed · ${d.sam_only} only Sam · ${d.spark_only} only Spark`,source);continue;}
  if(s.kind!=='tool')continue;
  if(s.tool==='read_delivery_note'){const n=entry.note.items[0];add('spark',null,`${n.quantity} ${n.unit} · ${n.description}`,source+' / note');}
  else if(s.tool==='look_at_pallet'){const v=Object.keys(r).length?r:entry.spark;add('spark',null,`${v.product_on_labels} · ${v.cartons_visible} cartons seen · ${v.damaged_cartons} damaged · stacked: ${v.stacked?'yes':'no'} · all visible: ${v.all_cartons_visible?'yes':'no'}`,source);}
  else if(s.tool==='count_cartons'){add('spark','sam',`Count cartons${a.concept?` · ${a.concept}`:''}`,source);add('sam','spark',r.sure!==undefined?`${r.sure} sure · ${r.doubtful} doubtful`:'Result truncated in the recording; see evidence.',source);}
  else if(s.tool==='post_goods_receipt'){add('spark','kapi',`Receipt request${a.quantity!==undefined?` · ${a.quantity} cartons`:''}`,source);add('kapi','spark',r.posted?`Posted ${r.quantity} cartons · ${r.document}`:r.reason||entry.gate.reason,source);}
  else if(s.tool==='ask_supervisor'){add('spark','sef',a.reason||entry.gate.reason,source);add('sef','spark','Supervisor notified.',source,{remote:!participants(entry.id).includes('sef')});}
 }
 add('kapi',null,`${entry.gate.action==='human'?'ASK ŞEF':entry.gate.action.toUpperCase()} · ${entry.gate.reason}`,'data.json · gate',{decision:true});
 if(entry.draft)add('wonder','sef',`Draft: ${entry.draft.document} · ${entry.draft.status}. ${entry.gate.reason}`,'data.json · draft / gate',{summary:true});
 if(entry.gate.action==='human'&&followup){add('sef','kapi',`${followup.decision.approve?'Approved':'Not approved'} · ${followup.decision.quantity} cartons. ${followup.decision.notes}`,'data-en.json · signoff · follow-up run, on the Turkish note');for(const [qty,doc] of followup.posted||[])add('kapi','sef',`Posted ${qty} cartons · ${doc}`,'data-en.json · signoff.posted · follow-up run, on the Turkish note');}
 return lines;
}
