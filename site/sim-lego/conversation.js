import {deliveryReply} from './chat-replies.mjs?v=bilingual-1';
import {names,participants} from './replay.mjs?v=chat-3';
const drafts=new Map();
const avatar=id=>`../img/av-${id}.jpg`;   // the site's own 160 px avatars
const demoTime=index=>{const minutes=8*60+index;return `${String(Math.floor(minutes/60)%24).padStart(2,'0')}:${String(minutes%60).padStart(2,'0')}`;};
const now=()=>new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/Istanbul',hour:'2-digit',minute:'2-digit'}).format(new Date());
function el(tag,className,text){const node=document.createElement(tag);if(className)node.className=className;if(text!==undefined)node.textContent=text;return node;}
export function openConversation({root,entry,lines,cast,onClose,onEvidence,onLocate,onWorkflow}){
 const team=participants(entry.id,lines),messages=lines.map((line,index)=>({...line,time:demoTime(index),index}));
 const crew=(cast&&cast.length?cast:Object.keys(names).map(id=>({id,name:names[id],job:''})));
 const nameOf=id=>crew.find(c=>c.id===id)?.name||names[id]||id;
 const jobOf=id=>crew.find(c=>c.id===id)?.job||'';
 const portrait=id=>{const img=el('img','chat-avatar');img.src=avatar(id);img.alt=nameOf(id);return img;};
 let selected=null,query='';
 const close=()=>{root.hidden=true;if(root._esc){document.removeEventListener('keydown',root._esc);root._esc=null;}onClose?.();};
 const esc=e=>{if(e.key==='Escape'&&!root.hidden){e.preventDefault();close();}};
 if(root._esc)document.removeEventListener('keydown',root._esc);
 root._esc=esc;document.addEventListener('keydown',esc);root._close=close;
 function button(text,className,action,label){const b=el('button',className,text);b.type='button';if(label)b.setAttribute('aria-label',label);b.onclick=action;return b;}
 function heading(){const head=el('div','chat-heading');head.append(el('span','chat-brand','Delivery team'),button('×','chat-icon',close,'Close conversation'));return head;}
 function openAgent(id){selected=id;render();try{onLocate?.(id);}catch{}}
 function inbox(){
  root.classList.remove('chat-detail');root.replaceChildren(heading());
  const search=el('input','chat-search');search.type='search';search.placeholder='Search agents';search.setAttribute('aria-label','Search agents');search.value=query;root.append(search);
  const grid=el('div','chat-agent-grid'),list=el('div','chat-inbox');root.append(grid,el('p','chat-caption','RECENT CONVERSATIONS'),list);
  function draw(){grid.replaceChildren();list.replaceChildren();
   const q=query.toLocaleLowerCase();
   for(const agent of crew.filter(c=>c.name.toLocaleLowerCase().includes(q))){
    const tile=button('','chat-agent',()=>openAgent(agent.id),`Open ${agent.name} conversation`);
    const wrap=el('span','chat-avatar-wrap');wrap.append(portrait(agent.id));
    if(team.includes(agent.id)){const dot=el('span','chat-dot');dot.setAttribute('aria-hidden','true');dot.title='In this delivery';wrap.append(dot);}
    tile.append(wrap,el('strong','',agent.name),el('small','',jobOf(agent.id)));grid.append(tile);
   }
   const lastBySpeaker=new Map();
   for(const m of messages)if(m.speaker)lastBySpeaker.set(m.speaker,m);
   const recents=[...lastBySpeaker.entries()].sort((a,b)=>b[1].index-a[1].index).filter(([id])=>nameOf(id).toLocaleLowerCase().includes(q));
   for(const [id,latest] of recents){
    const row=button('','chat-inbox-row',()=>openAgent(id),`Read ${nameOf(id)} messages`),copy=el('div','chat-row-copy'),top=el('div','chat-row-heading');
    top.append(el('strong','',nameOf(id)),el('time','',latest.time||'—'));
    copy.append(top,el('p','',String(latest.text||'').split('\n')[0]));row.append(portrait(id),copy);list.append(row);
   }
   if(!grid.children.length)list.append(el('p','chat-empty','No agents match your search.'));
   else if(!list.children.length)list.append(el('p','chat-empty','No recorded conversations for this search.'));
  }
  search.oninput=()=>{query=search.value;draw();};draw();
 }
 function detail(){
  root.classList.add('chat-detail');root.replaceChildren();
  const id=selected,title=nameOf(id),head=el('div','chat-profile');
  head.append(button('‹','chat-icon chat-back',()=>{selected=null;render();},'Back to conversations'),button('×','chat-icon chat-close',close,'Close conversation'));
  head.append(portrait(id));
  head.append(el('h2','',title),el('p','chat-caption','RECORDED DELIVERY · DEMO TIMES'));
  const actions=el('div','chat-actions');actions.append(button('▤ Evidence','',onEvidence),button('☷ Workflow','',onWorkflow),button('⌖ Locate','',()=>onLocate?.(id)));head.append(actions);root.append(head);
  const scroll=el('div','chat-bubbles');scroll.tabIndex=0;scroll.setAttribute('aria-label',`${title} messages`);scroll.setAttribute('role','log');scroll.setAttribute('aria-live','polite');root.append(scroll);
  const key=`${entry.id}:${id}`,local=drafts.get(key)||[];
  function bubble(message,own=false){const item=el('article',`chat-bubble ${own?'outgoing':'incoming'}`),meta=el('div','chat-bubble-meta');meta.append(el('strong','',message.speaker==='you'?'You':nameOf(message.speaker)||message.speaker),el('time','',message.time));item.append(meta,el('p','',message.text));
   if(message.source){const details=el('details','chat-source');details.append(el('summary','','Recorded source'),el('small','',message.source));item.append(details);}scroll.append(item);
  }
  for(const message of messages.filter(m=>m.speaker===id||m.to===id))bubble(message,message.speaker!==id);
  for(const message of local)bubble(message,message.speaker==='you');
  if(!scroll.children.length)scroll.append(el('p','chat-empty','This agent has no messages in this recording. Ask about the delivery below.'));
  const form=el('form','chat-composer'),input=el('textarea');input.rows=1;input.placeholder=`Message ${title}`;input.setAttribute('aria-label',`Message ${title}`);input.maxLength=1500;
  const submit=el('button','','↑');submit.type='submit';submit.setAttribute('aria-label','Send message');form.append(input,submit);root.append(form,el('p','chat-local-note','Replies use this delivery’s recorded evidence.'));
  function send(text){text=text.trim();if(!text)return;const stamp=now(),answer=deliveryReply(text,entry,local.at(-1)?.language||'en'),user={speaker:'you',text,time:stamp},response={speaker:id,...answer,time:stamp};local.push(user,response);drafts.set(key,local);bubble(user,true);bubble(response);input.value='';scroll.scrollTop=scroll.scrollHeight;input.focus();}
  form.onsubmit=e=>{e.preventDefault();send(input.value);};input.onkeydown=e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send(input.value);}};
  scroll.scrollTop=scroll.scrollHeight;
 }
 function render(){selected?detail():inbox();}
 root.hidden=false;render();
}
