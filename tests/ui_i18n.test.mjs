import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const code=fs.readFileSync(new URL('../site/i18n/ui.js',import.meta.url),'utf8');
async function runtime(lang){
 const store=new Map();const document={currentScript:{src:'https://demo.test/i18n/ui.js'},readyState:'loading',addEventListener(){},dispatchEvent(){}};
 const context=vm.createContext({URL,Map,WeakMap,RegExp,CustomEvent:class{},document,window:{},location:{href:'https://demo.test/jury/?ui='+lang},history:{replaceState(){}},localStorage:{getItem:k=>store.get(k),setItem:(k,v)=>store.set(k,v)},fetch:async url=>({ok:true,json:async()=>JSON.parse(fs.readFileSync(new URL('../site/i18n/'+url.pathname.split('/').at(-1),import.meta.url),'utf8'))})});
 vm.runInContext(code,context);await context.window.CBYP_I18N.ready;return {ui:context.window.CBYP_I18N,store};
}
test('all published source strings have all four translations and identical placeholders',()=>{
 const source=JSON.parse(fs.readFileSync(new URL('../site/i18n/source.json',import.meta.url))),translations=JSON.parse(fs.readFileSync(new URL('../site/i18n/translations.json',import.meta.url)));
 for(const row of source)for(const lang of ['tr','en','de','zh']){assert.ok(translations[row.id]?.[lang],row.text+' '+lang);assert.deepEqual((row.text.match(/\{\{\d+\}\}/g)||[]).sort(),(translations[row.id][lang].match(/\{\{\d+\}\}/g)||[]).sort());}
});
test('language persists independently of evidence and can be locked for timing study',async()=>{
 const {ui,store}=await runtime('tr');assert.equal(ui.locale,'tr');assert.equal(store.get('cbyp-ui-language'),'tr');assert.equal(ui.t('All evidence'),'Tüm kanıtlar');await ui.setLocale('de');assert.equal(ui.locale,'de');assert.equal(store.get('cbyp-ui-language'),'de');ui.setLocked(true);await ui.setLocale('zh');assert.equal(ui.locale,'de');ui.setLocked(false);await ui.setLocale('zh');assert.equal(ui.locale,'zh');assert.equal(ui.t('PO-area-correct'),'PO-area-correct');
});
test('dynamic quantities survive translation without changing their value',async()=>{
 const {ui}=await runtime('de');const text=ui.t('12 seen by Spark · 11 sure for SAM');assert.match(text,/12/);assert.match(text,/11/);assert.doesNotMatch(text,/seen by|sure for/);assert.equal(ui.t('12 cartons'),'12 Kartons');assert.equal(ui.t('2 cartons · No.770'),'2 Kartons · No.770');
});
