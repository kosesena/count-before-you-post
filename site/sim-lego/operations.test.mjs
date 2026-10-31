import assert from 'node:assert/strict';
import {movePose,blockedPose,rectangle} from './collision.mjs';
import {collectRoute,destinationRoute,areas,contained,pickupAligned,placementClear,evidenceRows} from './operations.mjs';
import {readFileSync} from 'node:fs';
for(const destination of ['accepted','hold','returned']){
 let pose={x:18.2,z:-.6,angle:-Math.PI/2},held=false;
 for(const [op,value] of [...collectRoute,...destinationRoute(destination)]){
  if(op==='pickup'){held=true;continue;}
  if(op==='drop'){const p={x:pose.x-Math.sin(pose.angle)*2.25,z:pose.z-Math.cos(pose.angle)*2.25,angle:pose.angle};assert.ok(contained(p,areas.inspection)||contained(p,areas[destination]));assert.ok(placementClear(p));held=false;continue;}
  pose=movePose(pose,op==='move'?value:0,op==='turn'?value:0,{held,gateClosed:destination!=='accepted'});assert.equal(pose.hit,false,`${destination} ${op} ${value}`);
 }
}
for(const x of [0,9,10])assert.equal(blockedPose(x,-7.3,0,{held:true}),true,'no fence bypass');
assert.equal(blockedPose(4,-7.3,0,{held:true,gateClosed:false}),false);
assert.equal(blockedPose(4,-7.3,0,{held:true,gateClosed:true}),true);
assert.ok(pickupAligned({x:15.85,z:-4,angle:-Math.PI/2},{x:18.1,z:-4,angle:Math.PI/2}));
assert.equal(pickupAligned({x:15.85,z:-4,angle:0},{x:18.1,z:-4,angle:Math.PI/2}),false);
assert.equal(contained({x:5.7,z:-5.5,angle:0},areas.inspection),false);
assert.equal(placementClear({x:10,z:7,angle:0},[rectangle(10,7,.9,.8)]),false);
const cases=JSON.parse(readFileSync(new URL('../data.json',import.meta.url))).cases;
for(const entry of cases){assert.equal(evidenceRows(entry).length,6);assert.ok(evidenceRows(entry)[4][1].includes(entry.gate.reason));}
console.log('Routes, fence, placement, alignment and all six evidence records passed.');
// Frame-sized movement, including physical pallet collision, matches the command routes.
for(const destination of ['accepted','hold','returned']){
 let pose={x:18.2,z:-.6,angle:-Math.PI/2},held=false,pallet=rectangle(18.1,-4,.9,.8,Math.PI/2);
 for(const [op,value] of [...collectRoute,...destinationRoute(destination)]){
  if(op==='pickup'){assert.ok(pickupAligned(pose,{x:pallet.x,z:pallet.z,angle:pallet.angle}));held=true;continue;}
  if(op==='drop'){pallet=rectangle(pose.x-Math.sin(pose.angle)*2.25,pose.z-Math.cos(pose.angle)*2.25,.9,.8,pose.angle);held=false;continue;}
  let remaining=value;
  while(Math.abs(remaining)>.00001){const delta=Math.sign(remaining)*Math.min(.025,Math.abs(remaining));pose=movePose(pose,op==='move'?delta:0,op==='turn'?delta:0,{held,pallet:held?null:pallet,gateClosed:destination!=='accepted'});assert.equal(pose.hit,false,`${destination} frame ${op}`);remaining-=delta;}
 }
}
assert.equal(blockedPose(-9.6,-7.3,0,{held:false}),true,'pedestrian opening excludes forklift');
for(const target of ['accepted','returned']){
 let pose={x:10,z:1.75,angle:-3*Math.PI},held=false;
 const commands=target==='accepted'?[['move',3],['pickup'],['move',-3.75],['turn',-Math.PI/2],['move',6],['turn',-Math.PI/2],['move',11.15],['drop'],['move',-3]]:[['move',3],['pickup'],['move',5],['drop'],['move',-3]];
 for(const [op,value] of commands){if(op==='pickup'){assert.ok(pickupAligned(pose,{x:10,z:7,angle:-3*Math.PI}));held=true;continue;}if(op==='drop'){assert.ok(contained({x:pose.x-Math.sin(pose.angle)*2.25,z:pose.z-Math.cos(pose.angle)*2.25,angle:pose.angle},areas[target]));held=false;continue;}pose=movePose(pose,op==='move'?value:0,op==='turn'?value:0,{held,gateClosed:target!=='accepted',obstacles:target==='accepted'?[rectangle(13,7,.9,.8)]:[]});assert.equal(pose.hit,false,`review ${target} ${op}`);}
}
