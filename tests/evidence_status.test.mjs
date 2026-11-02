import {test} from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
const E=vm.runInNewContext(fs.readFileSync('site/evidence-status.js','utf8')+';EvidenceStatus');
const rules=['instruction','invisible_text','receiver','readers_disagree','audit','match'];
test('optional checks not declared passed',()=>{for(const r of rules.slice(1,5))assert.equal(E.rule(r,'match',rules),'not evaluated in this run')});
test('fired and unreached rules preserved',()=>{assert.equal(E.rule('instruction','instruction',rules),'decided');assert.equal(E.rule('match','instruction',rules),'not reached')});
test('shortage separates strict visualization from gate count',()=>{const c=JSON.parse(fs.readFileSync('site/data.json')).cases.find(c=>c.id==='eksik');assert.match(E.cross(c),/accepted 11/);assert.match(E.cross(c),/doubtful SAM-only/)});
test('uncertain scene not presented as accepted count',()=>{const c=JSON.parse(fs.readFileSync('site/data.json')).cases.find(c=>c.id==='belirsiz');assert.match(E.cross(c),/No single agreed count/)});
