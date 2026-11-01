// Ground-plane collision geometry in scene units. Small steps prevent tunnelling.
export function rectangle(x,z,hx,hz,angle=0){return {x,z,hx,hz,angle};}
function axes(r){return [[Math.cos(r.angle),-Math.sin(r.angle)],[Math.sin(r.angle),Math.cos(r.angle)]];}
export function overlaps(a,b){
 const aa=axes(a),bb=axes(b),dx=b.x-a.x,dz=b.z-a.z;
 return [...aa,...bb].every(([x,z])=>Math.abs(dx*x+dz*z)<
 a.hx*Math.abs(aa[0][0]*x+aa[0][1]*z)+a.hz*Math.abs(aa[1][0]*x+aa[1][1]*z)+
 b.hx*Math.abs(bb[0][0]*x+bb[0][1]*z)+b.hz*Math.abs(bb[1][0]*x+bb[1][1]*z)-1e-6);
}
function circleOverlap(r,c){const [u,v]=axes(r),dx=c.x-r.x,dz=c.z-r.z;return Math.hypot(Math.max(0,Math.abs(dx*u[0]+dz*u[1])-r.hx),Math.max(0,Math.abs(dx*v[0]+dz*v[1])-r.hz))<c.radius;}
function offset(x,z,angle,lx,lz){return [x+Math.cos(angle)*lx+Math.sin(angle)*lz,z-Math.sin(angle)*lx+Math.cos(angle)*lz];}
export function forkliftShapes(x,z,angle,held=false){
 const local=[[0,.05,.99,1.18],[0,-1.25,.72,.15],[-.56,-2.1,.08,.8],[.56,-2.1,.08,.8]];
 if(held)local.push([0,-2.25,.94,.84]);
 return local.map(([lx,lz,hx,hz])=>rectangle(...offset(x,z,angle,lx,lz),hx,hz,angle));
}
// Shared by the visible staircase, collision footprint and pedestrian routes.
export const stairApproach=[[-9.6,.18,9.4],[-9.6,.18,11.8]];
// Two parallel flights joined by a full-width intermediate landing.
export const stairAscent=[[-9.6,.18,11.8],[-9.6,2.24,14.4],[-9.6,2.24,14.8],[-11.2,2.24,14.8],[-11.2,2.24,14.4],[-11.2,4.3,11.8],[-11.2,4.3,10.65]];
export const solids=[
 // Receiving furniture and waste stations.
 rectangle(4,7,.08,4),rectangle(-5,-4,1.4,.6),rectangle(-7.1,-6.75,.4,.4),rectangle(-5.8,-6.75,.4,.4),
 // Receiving partition: the only vehicle passage is the controlled gate.
 rectangle(-10.775,-7.3,.625,.12),rectangle(-3.325,-7.3,5.625,.12),rectangle(11.65,-7.3,5.35,.12),
 // Dedicated storage rack uprights; the ground slot remains accessible.
 rectangle(2.5,-12.4,.09,1.3),rectangle(5.5,-12.4,.09,1.3),
 rectangle(-17, -2,.175,18),rectangle(0,-20,17,.225),
 rectangle(17,-13.325,.3,6.675),rectangle(17,8.575,.3,7.425),
 rectangle(-14.235,.3,2.75,10.9),rectangle(-10.4,13.3,1.5,2),
 rectangle(2.3,-18.7,12.85,.94),rectangle(16,-13.7,.94,5.85),
 rectangle(16,5.7,.94,4.45),
 rectangle(17.1,-6.65,.3,.22),rectangle(17.1,1.15,.3,.22),
 // Trailer sides, front wall/cab and apron guard rail.
 rectangle(21,-5.55,4,.12),rectangle(21,-2.45,4,.12),rectangle(25.8,-4,1.9,1.8),
 rectangle(17.55,.65,.6,.06),
 rectangle(6.3,-7.3,.3,.3),rectangle(1.6,-7.4,.25,.25),
 rectangle(1.6,-5.5,.1,.1),rectangle(6.4,-5.5,.1,.1),
 ...[[-4,-10.5],[13,-8]].map(([x,z])=>rectangle(x,z,1,.8)),
 ...[[6,-7.5],[6,-3.5],[-8,10]].map(([x,z])=>rectangle(x,z,.25,.25)),
];
const circles=[{x:-1,z:7,radius:4.35}];
function supported(x,z){return (x>=-16.8&&x<=17&&z>=-19.75&&z<=15.8)||(x>=16.7&&x<=19.45&&z>=-2&&z<=.7)||(x>=16.7&&x<=24&&z>=-5.45&&z<=-2.55);}
export function blockedPose(x,z,angle,{held=false,gateClosed=true,pallet=null,obstacles=[]}={}){
 const shapes=forkliftShapes(x,z,angle,held);
 // Check each wheel rather than the vehicle centre at the raised dock edge.
 for(const lx of [-.8,.8])for(const lz of [-.72,.8])if(!supported(...offset(x,z,angle,lx,lz)))return true;
 const walls=gateClosed?[...solids,...obstacles,rectangle(4.35,-7.3,1.95,.12)]:[...solids,...obstacles];
 if(shapes.some(s=>walls.some(o=>overlaps(s,o))||circles.some(c=>circleOverlap(s,c))))return true;
 // The empty forks may slide under a pallet, but the chassis cannot pass through it.
 return !!pallet&&overlaps(shapes[0],pallet);
}
export function movePose(pose,distance,rotation,options){
 let hit=false;const steps=Math.max(1,Math.ceil(Math.abs(distance)/.06),Math.ceil(Math.abs(rotation)/.025));
 let {x,z,angle}=pose;
 for(let i=0;i<steps;i++){
  const a=angle+rotation/steps;
  if(!blockedPose(x,z,a,options))angle=a;else if(rotation)hit=true;
  const nx=x-Math.sin(angle)*distance/steps,nz=z-Math.cos(angle)*distance/steps;
  if(!blockedPose(nx,nz,angle,options)){x=nx;z=nz;}else if(distance)hit=true;
 }
 return {x,z,angle,hit};
}
