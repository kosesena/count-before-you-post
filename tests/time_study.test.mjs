import {test} from 'node:test';
import assert from 'node:assert/strict';
import {summarize} from '../site/time-study/metrics.mjs';
const row=(mode,time,extra={})=>({case_id:'one',mode,active_seconds:time,correct:true,interrupted:false,...extra});
test('empty results never imply savings',()=>assert.equal(summarize([]).mean_review_seconds_difference,null));
test('paired difference preserves negative result',()=>assert.equal(summarize([row('manual',10),row('assisted',15)]).mean_review_seconds_difference,-5));
test('wrong answers excluded from timing but retained in accuracy',()=>{const s=summarize([row('manual',10),row('assisted',2,{correct:false})]);assert.equal(s.eligible_pairs,0);assert.equal(s.correct_assisted,0);assert.equal(s.completed_trials,2)});
test('interrupted trial excluded',()=>assert.equal(summarize([row('manual',10),row('assisted',2,{interrupted:true})]).eligible_pairs,0));
test('unpaired case not compared',()=>assert.equal(summarize([row('manual',10)]).paired_cases,0));
