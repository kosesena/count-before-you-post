import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {initialDestination,reviewPolicy,canAccept,locationMatches,atRouteStart,reviewRoute} from './receiving.mjs';
import {areas,collectRoute,destinationRoute,contained,pickupAligned,placementClear} from './operations.mjs';
import {movePose,rectangle,blockedPose} from './collision.mjs';
const cases=JSON.parse(readFileSync(new URL('../data.json',import.meta.url))).cases;
for(const c of cases){
 assert.equal(initialDestination(c.gate.action),c.id==='ok'?'accepted':'hold');
 const p=reviewPolicy(c.id);
 assert.equal(canAccept(c.id,{count:p.quantity,inspected:true,document:true}),p.accept);
 assert.equal(canAccept(c.id,{count:p.quantity,inspected:false,document:true}),false);
 assert.equal(canAccept(c.id,{count:p.quantity+.5,inspected:true,document:true}),false);
 if(p.document)assert.equal(canAccept(c.id,{count:p.quantity,inspected:true,document:false}),false);
}
assert.equal(locationMatches(' a-01-l0 ','A-01-L0'),true);
assert.equal(locationMatches('A-01-L1','A-01-L0'),false);
assert.equal(atRouteStart({x:10,z:4.75,angle:-3*Math.PI},'hold'),true);
assert.equal(atRouteStart({x:10,z:1.75,angle:Math.PI},'hold'),false);
assert.equal(atRouteStart({x:4,z:-3.25,angle:Math.PI},'inspection'),false);
const stagedRoute=collectRoute.map(c=>[...c]);stagedRoute.splice(7,0,['drop'],['pickup']);
for(const outcome of ['accepted','returned','hold']){
 let pose={x:18.2,z:-.6,angle:-Math.PI/2},held=false,load=rectangle(18.1,-4,.9,.8,Math.PI/2),drops=0;
 const first=destinationRoute(outcome==='accepted'?'accepted':'hold');if(outcome!=='accepted')first.pop();
 const route=[...stagedRoute,...first,...(outcome==='returned'?reviewRoute('returned'):[])];
 for(const [op,value] of route){
  if(op==='pickup'){assert.ok(pickupAligned(pose,load));held=true;continue;}
  if(op==='drop'){
   load=rectangle(pose.x-Math.sin(pose.angle)*2.25,pose.z-Math.cos(pose.angle)*2.25,.9,.8,pose.angle);held=false;
   const expected=drops===0?'arrival':drops===1?'inspection':drops===2?(outcome==='accepted'?'accepted':'hold'):'returned';
   assert.ok(contained(load,areas[expected]),`${outcome} drop ${expected}`);assert.ok(placementClear(load));drops++;continue;
  }
  let remaining=value;
  while(Math.abs(remaining)>1e-5){const delta=Math.sign(remaining)*Math.min(Math.abs(remaining),.025);pose=movePose(pose,op==='move'?delta:0,op==='turn'?delta:0,{held,pallet:held?null:load,gateClosed:outcome!=='accepted'});assert.equal(pose.hit,false,`${outcome}: ${op} ${value}`);remaining-=delta;}
 }
}
// Review begins at the actual aligned drop pose, with no blind three-metre approach.
let pose={x:10,z:4.75,angle:Math.PI},held=false,load=rectangle(10,7,.9,.8,Math.PI);
for(const [op,value] of reviewRoute('accepted')){
 if(op==='pickup'){assert.ok(pickupAligned(pose,load));held=true;continue;}
 if(op==='drop'){load=rectangle(pose.x-Math.sin(pose.angle)*2.25,pose.z-Math.cos(pose.angle)*2.25,.9,.8,pose.angle);assert.ok(contained(load,areas.accepted));held=false;continue;}
 pose=movePose(pose,op==='move'?value:0,op==='turn'?value:0,{held,pallet:held?null:load,gateClosed:false,obstacles:[rectangle(13,7,.9,.8)]});assert.equal(pose.hit,false);
}
for(const [x,z] of [[-5,-4],[-5,-.8]])assert.ok(blockedPose(x,z,0),'new equipment is solid');
console.log('Six handling policies, document/recount guards, B-01 staging, review routes and destination scans passed.');

// Include workers at their final stations: the review return turn sweeps the
// opposite side of the inspection approach from the outbound hold transfer.
const crew=[[-2,-4.5],[-.5,-1.6],[0,-5.5],[12,4.5],[12.2,5]].map(([x,z])=>rectangle(x,z,.32,.32));
let reviewPose={x:10,z:4.75,angle:Math.PI},carried=false,reviewLoad=rectangle(10,7,.9,.8,Math.PI);
for(const [op,value] of reviewRoute('accepted')){
 if(op==='pickup'){carried=true;continue;}
 if(op==='drop'){reviewLoad=rectangle(reviewPose.x-Math.sin(reviewPose.angle)*2.25,reviewPose.z-Math.cos(reviewPose.angle)*2.25,.9,.8,reviewPose.angle);carried=false;continue;}
 let remaining=value;
 while(Math.abs(remaining)>1e-5){const delta=Math.sign(remaining)*Math.min(Math.abs(remaining),.025);reviewPose=movePose(reviewPose,op==='move'?delta:0,op==='turn'?delta:0,{held:carried,pallet:carried?null:reviewLoad,gateClosed:false,obstacles:[...crew,rectangle(13,7,.9,.8)]});assert.equal(reviewPose.hit,false,'review route clears the actual workstations and quarantine');remaining-=delta;}
}
