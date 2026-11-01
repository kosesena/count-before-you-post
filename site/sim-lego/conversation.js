import {deliveryReply} from './chat-replies.mjs?v=bilingual-1';
import {names,participants} from './replay.mjs?v=sentences-1';
const drafts=new Map();
const avatar=id=>`../img/av-${id}.jpg`;   // the site's own 160 px avatars
// Real times only (Sena, 1 Nov): a recorded message shows the time it was recorded when the run
// kept one (`at`), otherwise its place in the run; typed messages show the viewer's clock, 12-hour.
const clock=date=>new Intl.DateTimeFormat('en-US',{hour:'numeric',minute:'2-digit'}).format(date);
const stampOf=(line,index,total)=>line.at?clock(new Date(line.at)):`${index+1}/${total}`;
const now=()=>clock(new Date());
function el(tag,className,text){const node=document.createElement(tag);if(className)node.className=className;if(text!==undefined)node.textContent=text;return node;}
export function openConversation({root,entry,lines,cast,onClose,onEvidence,onLocate,onWorkflow,initialView=null,live=false}){
 const team=participants(entry.id,lines),messages=lines.map((line,index)=>({...line,time:stampOf(line,index,lines.length),index}));
 const crew=(cast&&cast.length?cast:Object.keys(names).map(id=>({id,name:names[id],job:''})));
 const nameOf=id=>crew.find(c=>c.id===id)?.name||names[id]||id;
 const jobOf=id=>crew.find(c=>c.id===id)?.job||'';
 const portrait=id=>{const img=el('img','chat-avatar');img.src=avatar(id);img.alt=nameOf(id);return img;};
 let selected=initialView==='team'?'team':(typeof initialView==='string'&&crew.some(c=>c.id===initialView)?initialView:null),query='';
 let teamShown=live?0:messages.length,teamTyping=null,teamActive=null;
 const visible=()=>messages.slice(0,teamShown);
 const close=()=>{root.hidden=true;if(root._esc){document.removeEventListener('keydown',root._esc);root._esc=null;}onClose?.();};
 const esc=e=>{if(e.key==='Escape'&&!root.hidden){e.preventDefault();close();}};
 if(root._esc)document.removeEventListener('keydown',root._esc);
 root._esc=esc;document.addEventListener('keydown',esc);root._close=close;
 function button(text,className,action,label){const b=el('button',className,text);b.type='button';if(label)b.setAttribute('aria-label',label);b.onclick=action;return b;}
 function heading(){const head=el('div','chat-heading');head.append(el('span','chat-brand','Delivery team'),button('×','chat-icon',close,'Close conversation'));return head;}
 function openAgent(id){selected=id;render();try{onLocate?.(id);}catch{}}
 function openTeam(){selected='team';render();}
 function inbox(){
  root.classList.remove('chat-detail');root.replaceChildren(heading());
  const search=el('input','chat-search');search.type='search';search.placeholder='Search agents';search.setAttribute('aria-label','Search agents');search.value=query;root.append(search);
  const grid=el('div','chat-agent-grid'),list=el('div','chat-inbox');root.append(grid,el('p','chat-caption','RECENT CONVERSATIONS'),list);
  function draw(){grid.replaceChildren();list.replaceChildren();
   const q=query.toLocaleLowerCase(),shown=visible();
   for(const agent of crew.filter(c=>c.name.toLocaleLowerCase().includes(q))){
    const tile=button('','chat-agent'+(agent.id===teamActive?' speaking':''),()=>openAgent(agent.id),`Open ${agent.name} conversation`);
    tile.dataset.agent=agent.id;
    const wrap=el('span','chat-avatar-wrap');wrap.append(portrait(agent.id));
    if(team.includes(agent.id)){const dot=el('span','chat-dot');dot.setAttribute('aria-hidden','true');dot.title='In this delivery';wrap.append(dot);}
    tile.append(wrap,el('strong','',agent.name),el('small','',jobOf(agent.id)));grid.append(tile);
   }
   if(!q||'team chat'.includes(q)||team.some(id=>nameOf(id).toLocaleLowerCase().includes(q))){
    const latest=shown.at(-1),row=button('','chat-inbox-row',openTeam,'Read the team conversation'),copy=el('div','chat-row-copy'),top=el('div','chat-row-heading'),stack=el('span','chat-stack');
    for(const id of team.slice(0,2))stack.append(portrait(id));
    top.append(el('strong','','Team chat'),el('time','',latest?.time||'—'));
    copy.append(top,el('p','',latest?String(latest.text||'').split('\n')[0]:'Live during Play delivery'));row.append(stack,copy);list.append(row);
   }
   const lastBySpeaker=new Map();
   for(const m of shown)if(m.speaker)lastBySpeaker.set(m.speaker,m);
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
 function teamView(){
  root.classList.add('chat-detail');root.replaceChildren();
  const head=el('div','chat-profile');
  head.append(button('‹','chat-icon chat-back',()=>{selected=null;render();},'Back to conversations'),button('×','chat-icon chat-close',close,'Close conversation'));
  head.append(el('h2','','Team chat'),el('p','chat-caption',(entry.title?entry.title.toLocaleUpperCase():'RECORDED DELIVERY')+' · RECORDED RUN'));
  root.append(head);
  const strip=el('div','chat-team-strip');strip.setAttribute('role','list');strip.setAttribute('aria-label','Delivery team');
  for(const id of team){
   const member=button('','chat-team-member'+(id===teamActive?' speaking':''),()=>openAgent(id),`Open ${nameOf(id)} conversation`);
   member.dataset.agent=id;member.append(portrait(id),el('span','',nameOf(id)));strip.append(member);
  }
  root.append(strip);
  const scroll=el('div','chat-bubbles');scroll.tabIndex=0;scroll.setAttribute('aria-label','Team messages');scroll.setAttribute('role','log');scroll.setAttribute('aria-live','polite');root.append(scroll);
  const show=visible();
  if(!show.length&&!teamTyping)scroll.append(el('p','chat-empty','The recorded run appears here when the inspection begins.'));
  for(const message of show){
   const row=el('div','chat-team-row'),pic=button('','chat-avatar-btn',()=>openAgent(message.speaker),`Open ${nameOf(message.speaker)} conversation`);
   pic.append(portrait(message.speaker));
   const item=el('article','chat-bubble incoming'),meta=el('div','chat-bubble-meta');
   meta.append(el('strong','',nameOf(message.speaker)||message.speaker),el('time','',message.time));
   item.append(meta,el('p','',message.text));
   if(message.source){const details=el('details','chat-source');details.append(el('summary','','Recorded source'),el('small','',message.source));item.append(details);}
   row.append(pic,item);scroll.append(row);
  }
  if(teamTyping){
   const row=el('div','chat-team-row'),pic=button('','chat-avatar-btn',()=>openAgent(teamTyping),`Open ${nameOf(teamTyping)} conversation`);
   pic.append(portrait(teamTyping));
   const item=el('div','chat-bubble incoming chat-typing');
   item.append(el('strong','',nameOf(teamTyping)||teamTyping),el('span','chat-typing-dots','typing…'));
   row.append(pic,item);scroll.append(row);
  }
  scroll.scrollTop=scroll.scrollHeight;
 }
 function detail(){
  root.classList.add('chat-detail');root.replaceChildren();
  const id=selected,title=nameOf(id),head=el('div','chat-profile');
  head.append(button('‹','chat-icon chat-back',()=>{selected=null;render();},'Back to conversations'),button('×','chat-icon chat-close',close,'Close conversation'));
  head.append(portrait(id));
  head.append(el('h2','',title),el('p','chat-caption','RECORDED DELIVERY · RECORDED RUN'));
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
 function render(){if(selected==='team')teamView();else if(selected)detail();else inbox();}
 root._teamTotal=messages.length;root._openTeam=openTeam;
 root._getTeamLive=()=>({shown:teamShown,typing:teamTyping,total:messages.length,active:teamActive});
 root._setTeamLive=(shown,typingId)=>{
  teamShown=Math.max(0,Math.min(messages.length,shown));teamTyping=typingId||null;
  teamActive=teamTyping||(teamShown>0?messages[teamShown-1]?.speaker:null)||null;
  if(selected==='team')render();
  else if(!selected){const hadFocus=root.querySelector('.chat-search')===document.activeElement;render();if(hadFocus){const s=root.querySelector('.chat-search');if(s){s.focus();s.setSelectionRange(s.value.length,s.value.length);}}}
 };
 root._askAgent=(id,text)=>{if(!crew.some(c=>c.id===id)||!String(text||'').trim())return;selected=id;render();const form=root.querySelector('.chat-composer'),input=root.querySelector('.chat-composer textarea');if(form&&input){input.value=text;form.requestSubmit();}};
 root.hidden=false;render();
}
