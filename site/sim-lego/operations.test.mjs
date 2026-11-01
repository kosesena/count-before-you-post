import assert from 'node:assert/strict';
import {movePose,blockedPose,rectangle} from './collision.mjs';
import {collectRoute,warehouseAisleRoute,warehouseReturnRoute,destinationRoute,refuseRoute,areas,contained,pickupAligned,placementClear,evidenceRows} from './operations.mjs';
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
const order=JSON.parse(readFileSync(new URL('../data.json',import.meta.url))).order;
for(const entry of cases){assert.equal(evidenceRows(entry,order).length,7);assert.ok(evidenceRows(entry,order)[4][1].includes(entry.gate.reason));assert.ok(evidenceRows(entry,order)[6][1].includes(order.number));}
// Refused at the dock: in, then the same way back onto the trailer, frame by frame, without a collision.
{let pose={x:18.2,z:-.6,angle:-Math.PI/2},held=false,pallet=rectangle(18.1,-4,.9,.8,Math.PI/2),drops=[];
 for(const [op,value] of [...collectRoute,...refuseRoute]){
  if(op==='pickup'){assert.ok(pickupAligned(pose,{x:pallet.x,z:pallet.z,angle:pallet.angle}),'pickup '+drops.length);held=true;continue;}
  if(op==='drop'){const p={x:pose.x-Math.sin(pose.angle)*2.25,z:pose.z-Math.cos(pose.angle)*2.25,angle:pose.angle};drops.push(p);pallet=rectangle(p.x,p.z,.9,.8,p.angle);held=false;continue;}
  let remaining=value;
  while(Math.abs(remaining)>.00001){const delta=Math.sign(remaining)*Math.min(.025,Math.abs(remaining));pose=movePose(pose,op==='move'?delta:0,op==='turn'?delta:0,{held,pallet:held?null:pallet,gateClosed:true});assert.equal(pose.hit,false,`refuse ${op} ${value}`);remaining-=delta;}
 }
 assert.ok(contained(drops[0],areas.inspection),'inspected first');assert.ok(contained(drops[1],areas.refused),'back on the trailer');
 assert.ok(Math.hypot(pose.x-18.2,pose.z+.6)<.05,'forklift back at its start');}
console.log('Refused at the dock: back onto the trailer, no collision.');
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

// Parking retraces the empty aisle, leaving the accepted pallet at its address.
{
 let pose={x:4,z:-7.15,angle:-2*Math.PI};
 const pallet=rectangle(4,-12.4,.9,.8,0);
 const route=[['move',-3.9],...collectRoute.filter(c=>['move','turn'].includes(c[0])).slice().reverse().map(([op,n])=>[op,-n])];
 for(const [op,value] of route){let remaining=value;while(Math.abs(remaining)>.00001){const delta=Math.sign(remaining)*Math.min(.025,Math.abs(remaining));pose=movePose(pose,op==='move'?delta:0,op==='turn'?delta:0,{held:false,pallet,gateClosed:false});assert.equal(pose.hit,false,'parking route clears the rack and stored load');remaining-=delta;}}
 assert.ok(Math.hypot(pose.x-18.2,pose.z+.6)<.05,'returns to parking by driving');
}
// Temporary A-01 to the real C-06 warehouse bay, then back to parking.
{
 let pose={x:4,z:-7.15,angle:0},held=false,pallet=rectangle(4,-12.4,.9,.8,0);
 const route=[['move',3],['pickup'],['move',-3],...warehouseAisleRoute,['move',2.3],['drop'],['move',-2.3],...warehouseReturnRoute,['move',-3.9],...collectRoute.filter(c=>['move','turn'].includes(c[0])).slice().reverse().map(([op,n])=>[op,-n])];
 for(const [op,value] of route){
  if(op==='pickup'){assert.ok(pickupAligned(pose,{x:4,z:-12.4,angle:0}));held=true;continue;}
  if(op==='drop'){const p={x:pose.x-Math.sin(pose.angle)*2.25,z:pose.z-Math.cos(pose.angle)*2.25,angle:pose.angle};assert.ok(contained(p,areas.storage));assert.ok(placementClear(p));pallet=rectangle(p.x,p.z,.9,.8,p.angle);held=false;continue;}
  let remaining=value;while(Math.abs(remaining)>.00001){const delta=Math.sign(remaining)*Math.min(.025,Math.abs(remaining));pose=movePose(pose,op==='move'?delta:0,op==='turn'?delta:0,{held,pallet:held?null:pallet,gateClosed:false});assert.equal(pose.hit,false,'warehouse transfer '+op+' '+value+' '+JSON.stringify(pose));remaining-=delta;}
 }
 assert.ok(Math.hypot(pose.x-18.2,pose.z+.6)<.05);
}

assert.equal(blockedPose(4,-12.4,0,{gateClosed:false}),true,'staging deck blocks forklift body');
