/* Local, build-time catalog. Evidence files are never rewritten or sent for translation. */
(() => {
  'use strict';
  const root = new URL('./', document.currentScript.src);
  const languages = {tr:'Türkçe',en:'English',de:'Deutsch',zh:'中文'};
  const names = {tr:'Arayüz dili',en:'Interface language',de:'Sprache der Oberfläche',zh:'界面语言'};
  const notes = {
    tr:'Arayüz çevirisi · Ham kayıtlar, belgeler ve sesler özgün dilindedir. Gerçek fotoğraf testlerinin sesi İngilizcedir.',
    en:'Interface translation · Raw records, documents and audio keep their original language. Real-photo tests use English audio.',
    de:'Übersetzung der Oberfläche · Rohdaten, Dokumente und Audio bleiben in der Originalsprache. Die Tests mit echten Fotos verwenden englisches Audio.',
    zh:'界面翻译 · 原始记录、文档和音频保留原语言。真实照片测试使用英语音频。'
  };
  let locked=false;
  let locale='en';
  try {const q=new URL(location.href).searchParams.get('ui');locale=q in languages?q:(localStorage.getItem('cbyp-ui-language')||'en');}catch{}
  if(!(locale in languages))locale='en';
  try{localStorage.setItem('cbyp-ui-language',locale);}catch{}
  let exact=new Map(),patterns=[],catalogReady=false,observer,scheduled=false,bar,select;
  const originals=new WeakMap(), attributes=new WeakMap();
  const normalize=s=>s.replace(/\s+/g,' ').trim();
  const excluded='script,style,pre,code,textarea,svg,canvas,.chat-source small,[data-original-evidence],[data-ui-language-bar],[translate="no"]';
  const escape=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
  function t(value,depth=0){
    if(typeof value!=='string'||!catalogReady)return value;
    const key=normalize(value),row=exact.get(key);
    if(row)return row[locale]||value;
    if(depth>2||!key||!/[A-Za-zÀ-ž\u4e00-\u9fff]/.test(key))return value;
    for(const p of patterns){
      const m=p.regex.exec(key);if(!m)continue;
      return (p.row[locale]||p.source).replace(/\{\{(\d+)\}\}/g,(_,id)=>t(m[p.ids.indexOf(id)+1]||'',depth+1));
    }
    if(key.includes(' · ')){const parts=key.split(' · ');const mapped=parts.map(part=>t(part,depth+1));if(mapped.some((part,i)=>part!==parts[i]))return mapped.join(' · ');}
    return value;
  }
  function translateNode(node){
    if(!node.parentElement||node.parentElement.closest(excluded))return;
    const current=node.nodeValue;if(!current.trim())return;
    let record=originals.get(node);
    if(record&&current===record.last&&record.locale===locale)return;
    if(!record||current!==record.last)record={source:current,last:current};
    const next=t(record.source),prefix=record.source.match(/^\s*/)[0],suffix=record.source.match(/\s*$/)[0];
    const value=next===record.source?record.source:prefix+next+suffix;
    if(current!==value)node.nodeValue=value;
    record.last=value;record.locale=locale;originals.set(node,record);
  }
  function translateElement(el){
    if(el.closest(excluded))return;
    let records=attributes.get(el)||{};
    for(const attr of ['aria-label','title','alt','placeholder']){
      if(!el.hasAttribute(attr))continue;
      const current=el.getAttribute(attr);let r=records[attr];
      if(r&&current===r.last&&r.locale===locale)continue;
      if(!r||current!==r.last)r={source:current,last:current};
      const value=t(r.source);if(value!==current)el.setAttribute(attr,value);
      r.last=value;r.locale=locale;records[attr]=r;
    }
    attributes.set(el,records);
  }
  function apply(){
    scheduled=false;if(!catalogReady||!document.body)return;
    observer?.disconnect();
    const walk=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
    for(let n=walk.nextNode();n;n=walk.nextNode())translateNode(n);
    for(const el of document.querySelectorAll('[aria-label],[title],[alt],[placeholder]'))translateElement(el);
    document.documentElement.lang=locale==='zh'?'zh-CN':locale;
    const title=document.querySelector('title');if(title?.firstChild) {
      let r=originals.get(title.firstChild)||{source:title.textContent};title.textContent=t(r.source);originals.set(title.firstChild,r);
    }
    if(bar){bar.querySelector('label').firstChild.nodeValue=names[locale]+' ';bar.querySelector('p').textContent=notes[locale];select.value=locale;select.setAttribute('aria-label',names[locale]);}
    observer.observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['aria-label','title','alt','placeholder']});
  }
  function schedule(){if(!scheduled){scheduled=true;requestAnimationFrame(apply);}}
  async function setLocale(lang){
    if(locked||!(lang in languages))return;
    locale=lang;try{localStorage.setItem('cbyp-ui-language',lang);const url=new URL(location.href);url.searchParams.set('ui',lang);history.replaceState(null,'',url);}catch{}
    apply();document.dispatchEvent(new CustomEvent('cbyp:language',{detail:{language:lang}}));
  }
  const ready=(async()=>{
    const [sources,translations]=await Promise.all(['source.json','translations.json'].map(async name=>{const r=await fetch(new URL(name,root));if(!r.ok)throw Error('Language catalog unavailable');return r.json();}));
    for(const item of sources){const row=translations[item.id];if(!row)continue;const source=normalize(item.text);
      if(!/\{\{\d+\}\}/.test(source))exact.set(source,row);
      else {const literals=source.replace(/\{\{\d+\}\}/g,'');if(literals.length<5||!/[A-Za-zÀ-ž\u4e00-\u9fff]/.test(literals))continue;
        const ids=[];let cursor=0,expr='^';for(const m of source.matchAll(/\{\{(\d+)\}\}/g)){expr+=escape(source.slice(cursor,m.index))+'([\\s\\S]*?)';ids.push(m[1]);cursor=m.index+m[0].length;}expr+=escape(source.slice(cursor))+'$';patterns.push({source,row,ids,regex:new RegExp(expr),weight:literals.length});
      }
    }
    patterns.sort((a,b)=>b.weight-a.weight);catalogReady=true;
  })();
  window.CBYP_I18N={t,setLocale,ready,setLocked(value){locked=!!value;if(select)select.disabled=locked||!catalogReady;},get locale(){return locale;},refresh:schedule};
  async function start(){
    const style=document.createElement('link');style.rel='stylesheet';style.href=new URL('ui.css',root);document.head.append(style);
    bar=document.createElement('aside');bar.dataset.uiLanguageBar='';bar.innerHTML='<div><label>Interface language <select id="ui-language"></select></label><p></p></div>';
    select=bar.querySelector('select');for(const [value,label] of Object.entries(languages)){const option=document.createElement('option');option.value=value;option.textContent=label;select.append(option);}select.value=locale;select.disabled=true;
    document.body.prepend(bar);
    if(/\/sim(?:-lego)?\//.test(location.pathname)){document.body.dataset.uiScene='';new ResizeObserver(()=>document.documentElement.style.setProperty('--ui-bar-height',bar.offsetHeight+'px')).observe(bar);}bar.querySelector('p').textContent=notes[locale];select.addEventListener('change',()=>setLocale(select.value));
    observer=new MutationObserver(schedule);
    try{await ready;select.disabled=false;apply();}catch{bar.querySelector('p').textContent='Language catalog could not load. Reload to retry. Original interface shown.';}
    addEventListener('storage',e=>{if(!locked&&e.key==='cbyp-ui-language'&&e.newValue in languages){locale=e.newValue;apply();}});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
