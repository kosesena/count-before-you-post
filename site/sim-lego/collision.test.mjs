import assert from 'node:assert/strict';
import {blockedPose,movePose,rectangle} from './collision.mjs';
assert.equal(blockedPose(18.2,-.6,-Math.PI/2),false);
assert.equal(blockedPose(0,0,0),false);
for(const [x,z,a] of [[0,-18,0],[-12,0,0],[15,5,0],[-8,-10,0],[-1,7,0],[7.2,-3.6,0],[13,-8,0],[17,8,0]])assert.ok(blockedPose(x,z,a));
const reverse=movePose({x:18.2,z:-.6,angle:-Math.PI/2},-2.35,0,{});
assert.ok(Math.abs(reverse.x-15.85)<.01&&!reverse.hit);
const edge=movePose({x:18.2,z:-.6,angle:-Math.PI/2},20,0,{});
assert.ok(edge.hit&&edge.x<19);
const wall=movePose({x:0,z:0,angle:0},40,0,{});
assert.ok(wall.hit&&wall.z>-17);
assert.equal(blockedPose(0,-14.8,0),false);
assert.equal(blockedPose(0,-14.8,0,{held:true}),true);
assert.ok(blockedPose(0,0,0,{pallet:rectangle(0,0,.9,.8)}));
// A long turn at an edge must stop before any part crosses an obstacle.
const turn=movePose({x:18.2,z:-.6,angle:-Math.PI/2},0,Math.PI,{});
assert.ok(turn.hit&&!blockedPose(turn.x,turn.z,turn.angle));
// Sample each segment of the guided loaded route, including its turning arc.
for(let i=0;i<=100;i++){
 const p=i/100;
 for(const pose of [[15.85-5.85*p,-4,-Math.PI/2],[10,-4+5*p,-Math.PI/2],[10-6*p,1,-Math.PI/2],[4,1,-Math.PI/2*(1-p)],[4,1-4.25*p,0]])assert.equal(blockedPose(...pose,{held:true}),false,`guided route ${pose}`);
}
console.log('Collision regression checks passed.');
