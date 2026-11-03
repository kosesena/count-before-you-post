// Run with NODE_PATH pointing to the installed acorn package. Build-time extraction only. Install acorn in a temporary tools directory to regenerate.
const fs=require('fs'),path=require('path'),acorn=require('acorn');
const out=[];
function concatenation(n){
 const parts=[];
 function flatten(x){
  if(x.type==='BinaryExpression'&&x.operator==='+'){flatten(x.left);flatten(x.right)}
  else if(x.type==='Literal'&&typeof x.value==='string')parts.push(x.value);
  else parts.push(null);
 }
 flatten(n);
 if(!parts.some(x=>typeof x==='string'))return null;
 let i=0;return parts.map(x=>x===null?`{{${i++}}}`:x).join('');
}
function visit(n,file){if(!n||typeof n!=='object')return;
 if(n.type==='BinaryExpression'&&n.operator==='+'){const text=concatenation(n);if(text)out.push({file,text})}
 if(n.type==='Literal'&&typeof n.value==='string')out.push({file,text:n.value});
 if(n.type==='TemplateLiteral')out.push({file,text:n.quasis.map((q,i)=>(q.value.cooked||q.value.raw)+(i<n.expressions.length?`{{${i}}}`:'')).join('')});
 for(const [k,v]of Object.entries(n))if(k!=='loc'&&k!=='start'&&k!=='end'){if(Array.isArray(v))v.forEach(x=>visit(x,file));else if(v&&typeof v==='object')visit(v,file)}
}
function parse(s,file){try{visit(acorn.parse(s,{ecmaVersion:'latest',sourceType:'module'}),file)}catch(e){console.error(file,e.message)}}
for(const f of process.argv.slice(2)){const s=fs.readFileSync(f,'utf8');if(/\.m?js$/.test(f))parse(s,f);else for(const m of s.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi))if(!/importmap|application\/json/.test(m[1]))parse(m[2],f)}
fs.writeFileSync(process.env.CBYP_I18N_EXTRACT || '/tmp/cbyp-i18n-extract.json',JSON.stringify(out,null,2));
