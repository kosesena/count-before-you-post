import {deliveryReply} from './chat-replies.mjs?v=bilingual-1';
import {names,participants} from './replay.mjs?v=chat-3';
const drafts=new Map();
const avatar=id=>id==='rover'?'./models/rover-avatar.png':`../img/av-${id}.jpg`;
const demoTime=index=>{const minutes=8*60+index;return `${String(Math.floor(minutes/60)%24).padStart(2,'0')}:${String(minutes%60).padStart(2,'0')}`;};
const now=()=>new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/Istanbul',hour:'2-digit',minute:'2-digit'}).format(new Date());
function el(tag,className,text){const node=document.createElement(tag);if(className)node.className=className;if(text!==undefined)node.textContent=text;return node;}
function portrait(id){const img=el('img','chat-avatar');img.src=avatar(id);img.alt=names[id]||id;return img;}
export function openConversation({root,entry,lines,onClose,onEvidence,onLocate,onWorkflow}){
 const team=participants(entry.id,lines),messages=lines.map((line,index)=>({...line,time:demoTime(index),index}));
 let selected=null,query='';
 const close=()=>{root.hidden=true;onClose();};
 function button(text,className,action,label){const b=el('button',className,text);b.type='button';if(label)b.setAttribute('aria-label',label);b.onclick=action;return b;}
 function heading(){const head=el('div','chat-heading');head.append(el('span','chat-brand','Delivery team'),button('×','chat-icon',close,'Close conversation'));return head;}
 function openAgent(id){selected=id;render();}
 function inbox(){
  root.classList.remove('chat-detail');root.replaceChildren(heading());
  const search=el('input','chat-search');search.type='search';search.placeholder='Search agents';search.setAttribute('aria-label','Search agents');search.value=query;root.append(search);
  const grid=el('div','chat-agent-grid'),list=el('div','chat-inbox');root.append(grid,el('p','chat-caption','RECORDED DELIVERY · DEMO TIMES'),list);
  function draw(){grid.replaceChildren();list.replaceChildren();
   for(const id of team.filter(id=>names[id].toLocaleLowerCase().includes(query.toLocaleLowerCase()))){
    const related=messages.filter(m=>m.speaker===id||m.to===id),latest=related.at(-1);
    const tile=button('','chat-agent',()=>openAgent(id),`Open ${names[id]} conversation`);tile.append(portrait(id),el('strong','',names[id]),el('small','',related.length?'Recorded':'No messages'));grid.append(tile);
    const row=button('','chat-inbox-row',()=>openAgent(id),`Read ${names[id]} messages`),copy=el('div','chat-row-copy'),top=el('div','chat-row-heading');top.append(el('strong','',names[id]),el('time','',latest?.time||'—'));copy.append(top,el('p','',latest?.text||'No messages in this delivery recording.'));row.append(portrait(id),copy);list.append(row);
   }
   if(!grid.children.length)list.append(el('p','chat-empty','No agents match your search.'));
  }
  search.oninput=()=>{query=search.value;draw();};draw();
  root.append(button('View full team conversation →','chat-team-link',()=>openAgent('team')));
 }
 function detail(){
  root.classList.add('chat-detail');root.replaceChildren();
  const id=selected,title=id==='team'?'Delivery team':names[id],head=el('div','chat-profile');
  head.append(button('‹','chat-icon chat-back',()=>{selected=null;render();},'Back to conversations'),button('×','chat-icon chat-close',close,'Close conversation'));
  if(id!=='team')head.append(portrait(id));else head.append(el('div','chat-team-avatar','◉'));
  head.append(el('h2','',title),el('p','chat-caption','RECORDED DELIVERY · DEMO TIMES'));
  const actions=el('div','chat-actions');actions.append(button('▤ Evidence','',onEvidence),button('☷ Workflow','',onWorkflow));if(id!=='team')actions.append(button('⌖ Locate','',()=>onLocate(id)));head.append(actions);root.append(head);
  const scroll=el('div','chat-bubbles');scroll.tabIndex=0;scroll.setAttribute('aria-label',`${title} messages`);scroll.setAttribute('role','log');scroll.setAttribute('aria-live','polite');root.append(scroll);
  const key=`${entry.id}:${id}`,local=drafts.get(key)||[];
  function bubble(message,own=false){const item=el('article',`chat-bubble ${own?'outgoing':'incoming'}`),meta=el('div','chat-bubble-meta');meta.append(el('strong','',message.speaker==='you'?'You':names[message.speaker]||message.speaker),el('time','',message.time));item.append(meta,el('p','',message.text));
   if(message.source){const details=el('details','chat-source');details.append(el('summary','','Recorded source'),el('small','',message.source));item.append(details);}scroll.append(item);
  }
  for(const message of messages.filter(m=>id==='team'||m.speaker===id||m.to===id))bubble(message,id!=='team'&&message.speaker!==id);
  if(id==='team'){
   const result=el('section','chat-comparison');result.append(el('h3','','Recorded run comparison'));
   for(const [title,data] of [['Without the gate',entry.without_gate],['With the gate',entry.agent]])result.append(el('p','',`${title}: posted ${JSON.stringify(data?.posted||[])} · supervisor notified: ${data?.supervisor?'yes':'no'}.`));
   scroll.append(result);
  }
  for(const message of local)bubble(message,message.speaker==='you');
  if(!scroll.children.length)scroll.append(el('p','chat-empty','This agent has no messages in this recording. Ask about the delivery below.'));
  const quick=el('div','chat-quick');for(const text of ['Count','Decision','Product'])quick.append(button(text,'',()=>send(text)));root.append(quick);
  const form=el('form','chat-composer'),input=el('textarea');input.rows=1;input.placeholder=`Message ${title}`;input.setAttribute('aria-label',`Message ${title}`);input.maxLength=1500;
  const submit=el('button','','↑');submit.type='submit';submit.setAttribute('aria-label','Send message');form.append(input,submit);root.append(form,el('p','chat-local-note','Replies use this delivery’s recorded evidence.'));
  function send(text){text=text.trim();if(!text)return;const stamp=now(),answer=deliveryReply(text,entry,local.at(-1)?.language||'en'),user={speaker:'you',text,time:stamp},response={speaker:id==='team'?'spark':id,...answer,time:stamp};local.push(user,response);drafts.set(key,local);bubble(user,true);bubble(response);input.value='';scroll.scrollTop=scroll.scrollHeight;input.focus();}
  form.onsubmit=e=>{e.preventDefault();send(input.value);};input.onkeydown=e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send(input.value);}};
  scroll.scrollTop=scroll.scrollHeight;
 }
 function render(){selected?detail():inbox();}
 root.hidden=false;render();
}
