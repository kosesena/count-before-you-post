import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import vm from 'node:vm';

const root = resolve(import.meta.dirname, '..');
const js = readFileSync(resolve(root, 'site/jury/main.js'), 'utf8');
const html = readFileSync(resolve(root, 'site/jury/index.html'), 'utf8');
const css = readFileSync(resolve(root, 'site/jury/style.css'), 'utf8');

function node(id) {
  const handlers = {};
  return {
    id, textContent:'', href:'', src:'', alt:'', hidden:false, disabled:false,
    dataset:{}, value:'en', attributes:{}, handlers,
    addEventListener(type, fn){ handlers[type] = fn; },
    setAttribute(name, value){this.attributes[name] = value;},
    scrollIntoView(){this.scrolled = true;},
    click(){if(this.disabled) return; this.handlers.click?.();}
  };
}
function harness() {
  const elements = new Map();
  const el = id => {if(!elements.has(id)) elements.set(id,node(id));return elements.get(id);};
  const byCase = ['ok','eksik','belirsiz'].map(id => {
    const e=node('case-'+id);e.dataset.case=id;return e;
  });
  const byReal = ['correct','quantity-mismatch','wrong-article'].map(id => {
    const e=node('real-'+id);e.dataset.real=id;return e;
  });
  const byView = ['camera','masks','cross'].map(id => {
    const e=node('view-'+id);e.dataset.view=id;return e;
  });
  const realRow = (id, action) => ({
    id, seconds:5.5,
    evidence:{
      note:{items:[{quantity:id==='quantity-mismatch'?2:1,product_identity:{product_code:'A'}}]},
      decision:{action, reasons:['Fixture decision'], evidence:{
        order:{number:'PO-1',open:1},
        product_identity:{expected:{product_code:'A'}}
      }},
      camera:{cartons_visible:1,product_identity:{product_code:'A'}},
      result:{posted:action==='post',quantity:1},
      receiver:{quantity:1},
      second_opinions:{audit:{ok:action==='post'}}
    }
  });
  const pastCase=id=>({
    id, gate:{action:id==='belirsiz'?'human':id==='ok'?'post':'block',reason:'Recorded fixture'},
    note:{items:[{quantity:1,unit:'carton',description:'Widget'}]},
    spark:{cartons_visible:1},sam:{sure:1},
    images:{note:'note.png',camera:'camera.png',masks:'masks.png',cross:'cross.png'},
    cross:{agreed:1,sam_only:0,spark_only:0},
    agent:{steps:[],supervisor:id==='belirsiz'}
  });
  const replies = {
    '../validation.json':{counting_area_controls:{
      selected_image:'camera.png',original_image:'original.png',
      rows:[realRow('correct','post'),realRow('quantity-mismatch','block'),
            realRow('wrong-article','block')]
    }},
    '../data-en.json':{cases:['ok','eksik','belirsiz'].map(pastCase)}
  };
  const context = {
    document:{
      getElementById:el,
      querySelectorAll(selector){return ({
        '[data-case]':byCase, '[data-real]':byReal, '[data-view]':byView
      })[selector] || [];}
    },
    EvidenceStatus:{cross:()=> 'object match evidence'},
    fetch:async path=>({ok:Boolean(replies[path]),json:async()=>replies[path]}),
    console
  };
  vm.runInNewContext(js,context,{filename:'site/jury/main.js'});
  return {el,byReal,context};
}

test('jury tour has a visible start link, four navigation targets and narrow mobile tap targets',()=>{
  assert.match(html,/id="tour-start"/);
  assert.match(html,/id="guided-tour"/);
  assert.match(html,/id="tour-progress"/);
  assert.match(css,/\.tour-controls button\{min-height:44px\}/);
  assert.match(css,/@media\(max-width:420px\)/);
});

test('tour walks through the three real-photo controls and the separate historical example',async()=>{
  const {el}=harness();
  for(let n=0;n<6;n++) await Promise.resolve();
  assert.equal(el('tour-next').disabled,false);
  el('tour-start').click();
  assert.match(el('tour-progress').textContent,/Step 1 of 4/);
  assert.equal(el('real-decision').dataset.action,'post');
  el('tour-next').click();
  assert.match(el('tour-progress').textContent,/Step 2 of 4/);
  assert.equal(el('real-decision').dataset.action,'block');
  el('tour-next').click();
  assert.match(el('tour-progress').textContent,/Step 3 of 4/);
  assert.equal(el('real-decision').dataset.action,'block');
  el('tour-next').click();
  assert.match(el('tour-progress').textContent,/Step 4 of 4/);
  assert.equal(el('decision').dataset.action,'human');
  assert.match(el('tour-narration').textContent,/historical synthetic/i);
  el('tour-next').click();
  assert.match(el('tour-progress').textContent,/Step 1 of 4/);
  el('tour-prev').click();
  assert.match(el('tour-progress').textContent,/Step 1 of 4/);
});
