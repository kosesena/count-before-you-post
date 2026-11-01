import {openConversation} from './conversation.js?v=bilingual-1';
import {buildReceivingScene} from './receiving-scene.js?v=waste-1';
import {receivingSteps,initialDestination,reviewPolicy,canAccept,locationMatches,atRouteStart,reviewRoute} from './receiving.mjs?v=order-1';
import {participants,names,replayLines,english} from './replay.mjs?v=chat-3';
import * as T from 'three';
import { blockedPose, movePose, rectangle, stairAscent, stairApproach } from './collision.mjs?v=waste-1';
import {areas,contained,pickupAligned,placementClear,collectRoute,destinationRoute,refuseRoute,evidenceRows} from './operations.mjs?v=waste-1';
import { GLTFLoader } from './vendor/GLTFLoader.js';
import { DRACOLoader } from './vendor/DRACOLoader.js';
import { OrbitControls } from './vendor/OrbitControls.js';
import { RoomEnvironment } from './vendor/RoomEnvironment.js';
import { RoundedBoxGeometry } from './vendor/RoundedBoxGeometry.js';

// This independent scene is measured in LEGO modules. No existing dock assets are changed.
const $ = id => document.getElementById(id);
const loadingText = $('loading').querySelector('strong');
const pauseFrame = () => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
let stageAt=performance.now();
// Six loading stages and the crew of ten fill the bar (written by hand, Claude Code).
let stageN=0;const progress=f=>{$('loading-bar').firstChild.style.width=`${Math.round(Math.max(.04,Math.min(1,f))*100)}%`;};
async function stage(text) { loadingText.textContent=text;stageAt=performance.now();progress(++stageN/7);await pauseFrame(); }
const C = {floor:0xc5c9cc,wall:0xd9dbd8,blue:0x0055bd,yellow:0xffcc00,orange:0xf47b13,navy:0x163360,teal:0x009e95,black:0x202326,red:0xc91a09,tan:0xd9b576,white:0xf4f3e9,pink:0xdc2485,purple:0x8553bf,green:0x438b40};
const scene = new T.Scene(); scene.background = new T.Color(0xe7e9df);
const renderer = new T.WebGLRenderer({antialias:true,alpha:false});
renderer.setPixelRatio(Math.min(devicePixelRatio,1.7)); renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = T.PCFSoftShadowMap;
renderer.toneMapping = T.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.;
$('world').appendChild(renderer.domElement);
const camera = new T.PerspectiveCamera(46,innerWidth/innerHeight,.15,180);
const controls = new OrbitControls(camera,renderer.domElement);
controls.enableDamping = true; controls.dampingFactor = .07; controls.maxPolarAngle = Math.PI*.485;
controls.minDistance = 3; controls.maxDistance = 64; controls.target.set(-1,3.5,-4);
camera.position.set(-1,6.5,21);
const pmrem = new T.PMREMGenerator(renderer);
const env = new RoomEnvironment(); const envTarget = pmrem.fromScene(env,.04);
scene.environment = envTarget.texture; scene.environmentIntensity = .33; env.dispose(); pmrem.dispose();
scene.add(new T.HemisphereLight(0xeaf5ff,0xa3906e,.42));
const sun = new T.DirectionalLight(0xffdfb2,2.05); sun.position.set(18,22,8); sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048); Object.assign(sun.shadow.camera,{left:-27,right:27,top:24,bottom:-24,near:1,far:65});
sun.shadow.normalBias=.035; sun.shadow.bias=-.0001; scene.add(sun);
const fill = new T.DirectionalLight(0xd8e7ff,.32);fill.position.set(-14,12,12);scene.add(fill);
// Round 2: no per-pendant lights; lamp pools are fake additive floor decals below.
const matCache = new Map(), geoCache = new Map(), batches = new Map();
function mat(color,rough=.25){const k=color+':'+rough;if(!matCache.has(k))matCache.set(k,new T.MeshPhysicalMaterial({color,roughness:rough,metalness:0,clearcoat:.24,clearcoatRoughness:.16}));return matCache.get(k);}
const glass = new T.MeshPhysicalMaterial({color:0xd9f4fa,transparent:true,opacity:.12,roughness:.08,depthWrite:false,side:T.DoubleSide});
const glow = new T.MeshStandardMaterial({color:0xfff1c8,emissive:0xffd27a,emissiveIntensity:5});
const pendantGlow = new T.MeshStandardMaterial({color:0xfff1c8,emissive:0xffc27a,emissiveIntensity:3.2,roughness:.4});pendantGlow.toneMapped=false;
// A soft additive halo around the small lamps, so they read as lit from a distance (written by hand, Claude Code).
const haloMat=(()=>{const c=document.createElement('canvas');c.width=c.height=64;const g=c.getContext('2d'),r=g.createRadialGradient(32,32,0,32,32,32);r.addColorStop(0,'rgba(255,240,200,1)');r.addColorStop(.22,'rgba(255,214,140,.6)');r.addColorStop(1,'rgba(255,200,120,0)');g.fillStyle=r;g.fillRect(0,0,64,64);return new T.SpriteMaterial({map:new T.CanvasTexture(c),blending:T.AdditiveBlending,depthWrite:false,transparent:true});})();
function halo(root,x,y,z,s=1){const h=new T.Sprite(haloMat);h.position.set(x,y,z);h.scale.set(s,s,1);root.add(h);}
// Fake lamp pools: one shared warm radial decal, additive, no light cost.
const poolTex=(()=>{const c=document.createElement('canvas');c.width=c.height=256;const g=c.getContext('2d'),r=g.createRadialGradient(128,128,0,128,128,128);r.addColorStop(0,'rgba(255,214,148,.5)');r.addColorStop(.4,'rgba(255,204,132,.22)');r.addColorStop(.75,'rgba(255,196,120,.06)');r.addColorStop(1,'rgba(255,190,115,0)');g.fillStyle=r;g.fillRect(0,0,256,256);const t=new T.CanvasTexture(c);t.colorSpace=T.SRGBColorSpace;return t;})();
const poolMat=new T.MeshBasicMaterial({map:poolTex,transparent:true,opacity:.45,blending:T.AdditiveBlending,depthWrite:false,toneMapped:false});
const poolGeo=new T.PlaneGeometry(6.5,6.5);
function geom(type,w=1,h=1,d=1){const key=[type,w,h,d].join(':');if(!geoCache.has(key)){let g;if(type==='box')g=new RoundedBoxGeometry(w,h,d,1,Math.min(.035,w*.1,h*.1,d*.1));else if(type==='cyl')g=new T.CylinderGeometry(w,w,h,d);else if(type==='sphere')g=new T.SphereGeometry(w,12,8);else if(type==='torus')g=new T.TorusGeometry(w,h,8,d);geoCache.set(key,g);}return geoCache.get(key);}
// Static meshes are instanced by geometry and material: thousands of physical studs, few draw calls.
const temp = new T.Object3D();
function piece(root,g,m,x,y,z,rx=0,ry=0,rz=0){let groups=batches.get(root);if(!groups){groups=new Map();batches.set(root,groups);}const key=g.uuid+m.uuid;let b=groups.get(key);if(!b){b={g,m,transforms:[]};groups.set(key,b);}temp.position.set(x,y,z);temp.rotation.set(rx,ry,rz);temp.scale.set(1,1,1);temp.updateMatrix();b.transforms.push(temp.matrix.clone());}
// Large surfaces are assemblies of separate bricks/tiles, never a monolithic slab.
function box(root,x,y,z,w,h,d,color,studs=false){
 const nx=w>3.2?Math.ceil(w/1.6):1,ny=h>1.1?Math.ceil(h/.48):1,nz=d>3.2?Math.ceil(d/1.6):1;
 for(let a=0;a<nx;a++)for(let b=0;b<ny;b++)for(let c=0;c<nz;c++){
  const ww=w/nx-(nx>1?.012:0),hh=h/ny-(ny>1?.012:0),dd=d/nz-(nz>1?.012:0);
  piece(root,geom('box',ww,hh,dd),mat(color),x+(a-(nx-1)/2)*w/nx,y+(b-(ny-1)/2)*h/ny,z+(c-(nz-1)/2)*d/nz);
 }
 if(studs){const sx=Math.max(1,Math.round(w/.4)),sz=Math.max(1,Math.round(d/.4));for(let i=0;i<sx;i++)for(let j=0;j<sz;j++)cyl(root,x+(i-(sx-1)/2)*.4,y+h/2+.045,z+(j-(sz-1)/2)*.4,.12,.09,color,12);}
}
function cyl(root,x,y,z,r,h,color,n=32,rx=0,ry=0,rz=0){piece(root,geom('cyl',r,h,n),typeof color==='number'?mat(color):color,x,y,z,rx,ry,rz);}
function ring(root,x,y,z,r,t,color){piece(root,geom('torus',r,t,48),mat(color),x,y,z,Math.PI/2);}
function flush(root){const groups=batches.get(root);if(!groups)return;for(const b of groups.values()){const m=new T.InstancedMesh(b.g,b.m,b.transforms.length);b.transforms.forEach((v,i)=>m.setMatrixAt(i,v));m.castShadow=true;m.receiveShadow=true;m.computeBoundingSphere();root.add(m);}batches.delete(root);}
function group(parent=scene,x=0,y=0,z=0,ry=0){const g=new T.Group();g.position.set(x,y,z);g.rotation.y=ry;parent.add(g);return g;}
function label(root,text,x,y,z,w,h,bg='#ffffff',fg='#253b40',ry=0){const cv=document.createElement('canvas');cv.width=512;cv.height=Math.round(512*h/w);const ct=cv.getContext('2d');ct.fillStyle=bg;ct.fillRect(0,0,cv.width,cv.height);ct.fillStyle=fg;ct.font=`bold ${Math.min(cv.height*.58,85)}px Arial`;ct.textAlign='center';ct.textBaseline='middle';ct.fillText(text,256,cv.height/2,490);const tx=new T.CanvasTexture(cv);tx.colorSpace=T.SRGBColorSpace;tx.anisotropy=4;const p=new T.Mesh(new T.PlaneGeometry(w,h),new T.MeshBasicMaterial({map:tx,side:T.DoubleSide}));p.position.set(x,y,z);p.rotation.y=ry;root.add(p);return p;}
// A second outward-facing plane reads normally from behind; both share live text updates.
function twoSidedLabel(root,text,x,y,z,w,h,bg='#ffffff',fg='#253b40',ry=0,depth=.025){
 const front=label(root,text,x,y,z,w,h,bg,fg,ry);front.material.side=T.FrontSide;
 const back=new T.Mesh(front.geometry,front.material);back.rotation.y=Math.PI;back.position.z=-depth;front.add(back);
 return front;
}
function litName(root,text,color){
 box(root,0,3.42,2.73,3.9,.64,.24,color);
 box(root,0,3.42,2.87,3.62,.49,.07,0x20343d);
 for(const x of [-1.82,1.82])cyl(root,x,3.42,2.91,.09,.06,color,20,Math.PI/2);
 const cv=document.createElement('canvas');cv.width=1024;cv.height=180;
 const ctx=cv.getContext('2d');ctx.textAlign='center';ctx.textBaseline='middle';
 ctx.font='900 128px "Arial Rounded MT Bold", "Trebuchet MS", sans-serif';
 ctx.shadowColor='#ffc35d';ctx.shadowBlur=16;ctx.fillStyle='#ffe5a2';ctx.fillText(text,512,92,950);
 ctx.shadowBlur=0;ctx.fillStyle='#fff8df';ctx.fillText(text,512,92,950);
 const texture=new T.CanvasTexture(cv);texture.colorSpace=T.SRGBColorSpace;texture.anisotropy=renderer.capabilities.getMaxAnisotropy();
 const face=new T.Mesh(new T.PlaneGeometry(3.18,.46),new T.MeshBasicMaterial({map:texture,transparent:true,toneMapped:false,depthWrite:false}));face.position.set(0,3.42,2.92);root.add(face);
 box(root,0,3.42,2.58,3.62,.49,.07,0x20343d);
 const reverseFace=new T.Mesh(face.geometry,face.material);reverseFace.position.set(0,3.42,2.53);reverseFace.rotation.y=Math.PI;root.add(reverseFace);
 const spill=new T.PointLight(0xffd99b,.7,2,2);spill.position.set(0,3.35,3.02);root.add(spill);
}
function sheet(root,x,y,z,w=.55,d=.7){box(root,x,y,z,w,.035,d,C.white);for(let k=0;k<4;k++)box(root,x,y+.02,z-d*.3+k*d*.15,w*.68,.006,.018,0x65727d);}
function crate(root,x,y,z,w=.75,h=.7,d=.7){box(root,x,y+h/2,z,w,h,d,C.tan,true);box(root,x,y+h/2+.006,z+d/2+.008,w*.32,h*.42,.018,C.white);box(root,x,y+h+.005,z,.09,.012,d,0xc5a06d);}
function pallet(root,x,y,z,w=1.8,d=1.5){for(let i=-1;i<=1;i++)box(root,x+i*w*.33,y+.12,z,w*.15,.24,d,0xa97b45);for(let i=0;i<5;i++)box(root,x,y+.29,z+(i-2)*d/5,w,.13,d/5-.035,0xbd965f,true);}
function plant(root,x,y,z){
 // Round flowerpot, stacked stem pins and molded LEGO leaf plates.
 cyl(root,x,y+.23,z,.22,.45,C.white,16);ring(root,x,y+.45,z,.19,.035,C.white);
 for(let k=0;k<4;k++)cyl(root,x,y+.5+k*.12,z,.045,.115,0x28703b,8);
 for(let k=0;k<6;k++){const a=k*Math.PI/3,g=group(root,x,y+.57+(k%2)*.13,z,a);box(g,0,.04,.18,.14,.08,.42,k%2?0x226a36:0x408b3e);cyl(g,0,.105,.3,.06,.05,0x408b3e,8);flush(g);}
}
const world=group(),overhead=group();
await stage('Building the warehouse…');
// Baseplate and tiled safety lanes.
box(world,0,-.22,-2,35,.4,37,0x9da6aa);
for(let x=-17;x<17;x+=2)for(let z=-20;z<16;z+=2)box(world,x+1,0,z+1,1.985,.12,1.985,C.floor);
for(let x=-16.8;x<17;x+=.4)for(let z=-19.8;z<16;z+=.4){if(Math.hypot(x+1,z-7)<4.4)continue;cyl(world,x,.11,z,.115,.08,C.floor,12);}
function stripe(x,z,w,d,col=C.yellow){box(world,x,.145,z,w,.065,d,col);}
stripe(-9,-2,.13,35);stripe(5,-2,.13,35);stripe(-2,-13,14,.13);stripe(10,9.6,9,.13);stripe(14,-1,.13,16);
// Studded brick walls; open front and open roof allow inspection from above.
for(let layer=0;layer<19;layer++){const yy=.32+layer*.48;for(let x=-17;x<17;x+=1.6){const xx=x+.8+(layer%2)*.8;if(xx>17)continue;box(world,xx,yy,-20,1.585,.465,.45,layer%7===0?0xc7cccb:C.wall,layer===18);}}
for(let layer=0;layer<16;layer++)for(let z=-20;z<16;z+=1.6){
 const lo=z+(layer%2)*.8,hi=Math.min(lo+1.6,16);
 const spans=layer<12?[[lo,Math.min(hi,-6.65)],[Math.max(lo,1.15),hi]]:[[lo,hi]];
 for(const [a,b] of spans)if(b-a>.025)box(world,17,.32+layer*.48,(a+b)/2,.45,.465,b-a-.015,C.wall,layer===15);
}
// Upper facade: alternating ribbed panels with brick joints, like the dock reference.
for(let z=-19.2;z<16;z+=1.6)box(world,17,9.25,z,.45,3.15,1.585,C.wall,true);
for(let x=-16;x<=16;x+=8){box(world,x,5.2,-19.65,.35,10.4,.6,0xb8bfbe);box(overhead,x,10.6,-2,.26,.35,36,0xb0b7b7,true);}
for(let z=-19;z<=15;z+=6)box(overhead,0,10.55,z,34,.35,.26,0xaeb6b8,true);
// Pendant centres never sit inside racks (x≈16 / z≈-18.7) or offices (x<-9.8); only the meeting disk covers one.
for(let x=-7;x<=11;x+=9)for(let z=-16;z<=14;z+=6){cyl(overhead,x,9.95,z,.035,1.05,C.black,8);const shade=new T.Mesh(new T.CylinderGeometry(.22,.65,.45,24),mat(C.black));shade.position.set(x,9.2,z);overhead.add(shade);cyl(overhead,x,8.98,z,.57,.045,pendantGlow,24);cyl(overhead,x,9.5,z,.15,.15,C.black,16);halo(overhead,x,8.8,z,2.2);if(Math.hypot(x+1,z-7)>4.4){const pool=new T.Mesh(poolGeo,poolMat);pool.rotation.x=-Math.PI/2;pool.position.set(x,.21,z);world.add(pool);}}
flush(world);flush(overhead);
await stage('Placing the bricks…');
// Shelving sits flush to the perimeter; no islands in the central aisle.
const ceiling=group();
for(let z=-18;z<=14;z+=4)box(ceiling,0,10.9,z,34,.12,3.97,0xc7cbc4);for(let x=-15.8;x<17;x+=.8)for(let z=-19.2;z<16;z+=.8){
 piece(ceiling,geom('torus',.13,.028,12),mat(0x939b97),x,10.82,z,Math.PI/2);
}
flush(ceiling);ceiling.traverse(o=>{o.castShadow=false;});
const racks=group();let rackIndex=0;
function rack(parent,x,z,ry,bays){const g=group(parent,x,0,z,ry);const rackCode=String.fromCharCode(67+rackIndex++);/* C, D, E: B-01 is the arrival bay */const step=2.8;for(let b=0;b<=bays;b++){const xx=(b-bays/2)*step;for(const zz of [-.7,.7]){for(let k=0;k<16;k++)box(g,xx,.25+k*.48,zz,.18,.465,.22,C.blue,k===15);box(g,xx,.16,zz,.45,.16,.45,C.blue);for(let k=0;k<14;k++)cyl(g,xx,.55+k*.48,zz+.115,.035,.012,0x063d79,8,Math.PI/2);}}
 for(let b=0;b<bays;b++){const xx=(b+.5-bays/2)*step;for(let lev=0;lev<4;lev++){const y=.5+lev*1.95;box(g,xx,y,.73,2.8,.18,.18,C.yellow,true);box(g,xx,y,-.73,2.8,.18,.18,C.yellow,true);box(g,xx,y,0,2.66,.12,1.38,0xb7bdc0);for(let c=0;c<3;c++){const h=.6+((b+lev+c)%3)*.12;crate(g,xx+(c-1)*.78,y+.12,0,.68,h,.84);if((b+lev+c)%3===0)crate(g,xx+(c-1)*.78,y+.12+h+.08,0,.55,.48,.65);}for(const side of [1,-1])label(g,`${rackCode}-${String(b+1).padStart(2,'0')}-L${lev}`,xx,y+.22,side*.86,1.2,.18,'#f4f3e9','#263d35',side===1?0:Math.PI).material.side=T.FrontSide;}}
 flush(g);return g;}
rack(racks,2.3,-18.7,0,9);rack(racks,16,-13.7,-Math.PI/2,4);rack(racks,16,5.7,-Math.PI/2,3);
// Continuous left shell: the office backs sit flush against its inner face.
for(let layer=0;layer<21;layer++)for(let z=-20;z<16;z+=1.6){
  const start=z+(layer%2)*.8,end=Math.min(start+1.6,16);
  if(start>=16)continue;
  box(world,-17,.32+layer*.48,(start+end)/2,.35,.465,end-start-.015,C.wall,layer===20);
}
// Close the half-brick at the rear of each staggered course.
for(let layer=1;layer<21;layer+=2)box(world,-17,.32+layer*.48,-19.6,.35,.465,.785,C.wall);
flush(world);
// Character construction: separate rigid limbs, printed face, C-shaped hands.
const actors=[];
const castSlots=[], castMixers=[], officeDoors=[];
const castIds=['spark','sef','sam','voice','kapi','iris','ada','glimmer','wonder','rover'];
const castJobs=['Reads the delivery note','Makes the final call','Counts the cartons','Listens to the receiver','Guards the receiving gate','Designs the visuals','Builds the system','Read every note in the second-reader trial','Cross-checks the evidence','Reads the note again'];
function person(parent,x,y,z,color,hair=0x39271e,hat=false,scale=1,ry=0){const g=group(parent,x,y,z,ry);g.scale.setScalar(scale);for(const s of [-1,1]){box(g,s*.2,.34,0,.34,.64,.4,0x243452);box(g,s*.2,.1,.12,.35,.2,.58,0x243452);}box(g,0,.76,0,.78,.2,.4,C.black);const torso=new T.Mesh(new T.CylinderGeometry(.33,.46,.65,4,1),mat(color));torso.rotation.y=Math.PI/4;torso.scale.z=.65;torso.position.y=1.16;g.add(torso);box(g,0,1.18,.26,.08,.5,.015,color===C.blue?C.yellow:C.white);for(const s of [-1,1]){const arm=group(g,s*.49,1.4,0,0);const a=new T.Mesh(geom('cyl',.14,.55,12),mat(color));a.position.set(0,-.2,.01);a.rotation.z=s*.14;arm.add(a);const hand=new T.Mesh(new T.TorusGeometry(.115,.055,8,14,Math.PI*1.65),mat(0xffce44));hand.position.set(0,-.55,.06);hand.rotation.z=-.3;arm.add(hand);}
 cyl(g,0,1.58,0,.13,.16,0xffce44);cyl(g,0,1.87,0,.29,.46,0xffce44,24);cyl(g,0,2.135,0,.12,.09,0xffce44,16);
 for(const s of [-1,1]){cyl(g,s*.105,1.9,.274,.03,.014,C.black,12,Math.PI/2);cyl(g,s*.098,1.91,.285,.008,.014,C.white,8,Math.PI/2);}
 const smile=new T.Mesh(new T.TorusGeometry(.085,.014,6,16,Math.PI),mat(C.black));smile.position.set(0,1.79,.285);smile.rotation.z=Math.PI;g.add(smile);
 if(hat){cyl(g,0,2.14,0,.33,.18,color,24);box(g,0,2.07,.19,.68,.06,.4,color);cyl(g,0,2.24,0,.12,.06,color,12);}else{cyl(g,0,2.11,-.025,.31,.15,hair,16);for(let i=0;i<8;i++){const a=i*Math.PI/4;piece(g,geom('sphere',.13),mat(hair),Math.sin(a)*.25,2.12+Math.sin(i)*.04,Math.cos(a)*.22-.04);}}
 flush(g);actors.push(g);return g;}
// Two-storey office wing: fronts face the central warehouse, as in the reference.
const OFFICE_WALL_SHIFT = -.20; // Back face -16.825 matches the wall inner face.
const offices=group(scene,OFFICE_WALL_SHIFT);
const BALCONY_DEPTH=1.8;
const roomDefs=[['Spark',C.orange,0xd95c16],['Şef',C.blue,0x26231d],['Sam',0x369ce5,0x42352b],['Voice',0x2b62ca,0x252521],['Kapı',0x26589c,0x43302a],['Iris',C.pink,0xa91c81],['Ada',C.teal,0x171b20],['Glimmer',C.purple,0xc4a3df],['Wonder',0xe7b82a,0x784322],['Rover',0x287a6d,0x994422]];
await stage('Preparing the crew…');
for(let floor=0;floor<2;floor++)for(let n=0;n<5;n++){
 const [name,color,hair]=roomDefs[floor*5+n], room=group(offices,-14.1,.16+floor*3.85,9-n*4.35,Math.PI/2);
 box(room,0,.02,0,4.35,.22,5.4,0xc4c9c8,true);box(room,0,1.85,-2.5,4.35,3.6,.26,color);
 if(n===0||n===4)box(room,n===0?-2.175:2.175,1.85,0,.12,3.6,5.3,color,true);
 for(const xx of [-2.12,2.12]){box(room,xx,1.85,.04,.14,3.6,5.18,color,true);box(room,xx,1.85,2.58,.12,3.7,.15,C.black);}
 box(room,0,3.62,2.58,4.3,.22,.18,C.black);box(room,0,.14,2.58,4.3,.1,.18,C.black);box(room,0,1.85,2.58,.09,3.5,.12,C.black);
 const roomLight=new T.PointLight(0xffddb0,9,6,2);roomLight.position.set(0,3.1,.5);room.add(roomLight);
 const pane=new T.Mesh(new T.PlaneGeometry(2,3.35),glass);pane.position.set(-1.05,1.85,2.6);room.add(pane);
 const door=group(room,2.08,0,2.61);const doorGlass=new T.Mesh(new T.PlaneGeometry(1.98,3.3),glass);doorGlass.position.set(-1,1.83,0);door.add(doorGlass);box(door,-1.98,1.84,0,.07,3.35,.1,C.black);box(door,-1.7,1.4,.07,.055,.36,.08,0xd7dadd);flush(door);officeDoors.push(door);
 litName(room,name,color);
 // Light tiled floors, desk, monitor, keyboard, paperwork, bookcase.
 for(let xx=-1.8;xx<2;xx+=.6)for(let zz=-2;zz<2.4;zz+=.6)box(room,xx,.155,zz,.585,.04,.585,floor?0xdacdb3:0xe7e5dc,true);
 box(room,.1,1.2,.7,2.8,.14,1.25,0xc6ac83);for(const xx of [-1.1,1.3])for(const zz of [.22,1.15])box(room,xx,.68,zz,.1,1.05,.1,0x58636c);
 box(room,.65,1.66,.6,.85,.6,.09,C.black);box(room,.65,1.68,.545,.75,.47,.015,name==='Ada'?0x123e3d:0x3b5668);box(room,.65,1.34,.6,.08,.24,.1,C.black);box(room,.65,1.28,.7,.4,.045,.3,C.black);
 for(let k=0;k<4;k++)box(room,.65,1.8-k*.08,.53,.52-k*.08,.015,.012,name==='Ada'?0x67dba9:0xa7c5cb);
 box(room,.55,1.3,.25,.65,.04,.23,0xe1e4e0);sheet(room,-.65,1.3,1.0,.5,.55);cyl(room,-1,1.4,.45,.09,.24,C.white,16);
 box(room,1.65,1.45,-1.5,.5,2.7,1.55,0xc6ad7e);for(let lev=0;lev<3;lev++){box(room,1.32,.6+lev*.8,-1.5,.22,.08,1.5,0xf0d4a1);for(let b=0;b<5;b++)box(room,1.3,.87+lev*.8,-2.05+b*.25,.25,.48,.15,[C.blue,C.yellow,C.red,C.teal,C.white][(b+lev)%5]);}
 box(room,-.65,.5,-.85,.85,.13,.85,C.black);box(room,-.65,.32,-.85,.12,.35,.12,C.black);box(room,-.65,.93,-1.25,.85,.8,.12,C.black);
 plant(room,-1.65,.22,1.9);label(room,name==='Iris'?'✦':String(floor*5+n+1).padStart(2,'0'),-.8,2.45,-2.39,1.4,.85,'#faf4df','#617c87');
 if(name==='Iris'){for(let i=0;i<3;i++)label(room,['ART','COLOR','FORM'][i],-.9+i*.85,2.5,-2.38,.7,.9,['#ffc839','#fa9cb4','#6bb5c0'][i],'#ffffff');}
 // Balcony: deep enough to walk past an open door; the stair landing opens onto its full depth.
 if(floor===1){const edge=2.65+BALCONY_DEPTH-.1;box(room,0,.2,2.65+BALCONY_DEPTH/2,4.35,.18,BALCONY_DEPTH,0xa8b2b6,true);for(const xx of [-2,-1,0,1,2])box(room,xx,.85,edge,.06,1.2,.06,C.black);for(const y of [1.45,.73])box(room,0,y,edge,4.3,y>1?.09:.055,y>1?.1:.06,C.black);
  const ends=n===4?[[2.15,2.65]]:[];for(const [xx,from] of ends){const mid=(from+edge)/2,len=edge-from;box(room,xx,.85,mid,.06,1.2,.06,C.black);for(const y of [1.45,.73])box(room,xx,y,mid,.1,y>1?.09:.055,len,C.black);}}
 const placeholder=person(room,-.65,.18,.05,color,hair,name==='Sam'||name==='Şef',.9);
 castSlots.push({id:castIds[floor*5+n],name,room,placeholder,index:floor*5+n});
 flush(room);
}
// Load the project's original animated cast; normalize feet and height in each office.
await stage('Welcoming all ten agents…');
const draco=new DRACOLoader().setDecoderPath('./vendor/draco/').setWorkerLimit(2);
const castLoader=new GLTFLoader().setDRACOLoader(draco);
let castLoaded=0;
await Promise.all(castSlots.map(async slot=>{
 try{
  const gltf=await castLoader.loadAsync(slot.id==='rover'?'./models/rover-clean.glb':slot.id==='sef'?'./models/sef-refined.glb':`../sim/models/${slot.id}.glb`);
  const root=gltf.scene, bounds=new T.Box3().setFromObject(root), size=bounds.getSize(new T.Vector3());
  const actor=group(slot.room,-.65,.21,-.85);
  root.position.set(-(bounds.min.x+bounds.max.x)/2,-bounds.min.y,-(bounds.min.z+bounds.max.z)/2);
  const scaled=new T.Group();scaled.scale.setScalar(2.24/size.y);scaled.add(root);actor.add(scaled);
  root.traverse(o=>{if(o.isMesh){o.castShadow=false;o.receiveShadow=true;}});
  slot.room.remove(slot.placeholder);slot.actor=actor;slot.loaded=true;
  slot.mixer=new T.AnimationMixer(root);castMixers.push(slot.mixer);
  // Keep the existing face design; full-resolution textures preserve its printed detail.
  root.traverse(o=>{if(o.isMesh)for(const material of (Array.isArray(o.material)?o.material:[o.material])){if(material.map)material.map.anisotropy=renderer.capabilities.getMaxAnisotropy();}});
  slot.arms=[root.getObjectByName('ArmL'),root.getObjectByName('ArmR')].filter(Boolean);
  slot.legs=[root.getObjectByName('LegL'),root.getObjectByName('LegR')].filter(Boolean);
  if(slot.legs.length){
   actor.updateWorldMatrix(true,true);const hip=actor.worldToLocal(slot.legs[0].getWorldPosition(new T.Vector3()));
   slot.hipHeight=hip.y;actor.position.y=.66-hip.y;
   // Rest legs point down; negative local X turns them towards the desk (+Z).
   slot.legs.forEach(leg=>leg.rotation.x=-Math.PI/2);
  }
  const idle=gltf.animations.find(c=>c.name==='Idle'),walk=gltf.animations.find(c=>c.name==='Walk');slot.idle=idle?slot.mixer.clipAction(idle):null;slot.walk=walk?slot.mixer.clipAction(walk):null;slot.idle?.play();
  // Imported wave deforms the shoulders; keep the seated idle pose until the rig is repaired.
  slot.wave=null;
  castLoaded++;$('loading').querySelector('small').textContent=`CREW · ${castLoaded} / 10`;progress((4+castLoaded/10)/7);
 }catch(error){console.error(`Karakter yüklenemedi: ${slot.name}`,error);}
}));
draco.dispose();document.body.dataset.castLoaded=String(castLoaded);
// Compact steel switchback stair: open treads, stringers, columns and a turning landing.
const stairs=group(scene),steel=0x687781,rail=0xc3ccd0;
function stairBeam(a,b,width=.07,color=rail){
 const start=new T.Vector3(...a),end=new T.Vector3(...b),delta=end.clone().sub(start);
 const mesh=new T.Mesh(geom('box',width,delta.length(),width),mat(color));
 mesh.position.copy(start.add(end).multiplyScalar(.5));mesh.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),delta.normalize());stairs.add(mesh);
}
function stairFlight(a,b){
 const count=8,dx=b[0]-a[0],dz=b[2]-a[2],rise=b[1]-a[1];
 for(let i=0;i<count;i++){
  const t=(i+.5)/count,x=a[0]+dx*t,z=a[2]+dz*t,y=a[1]+rise*(i+1)/count;
  box(stairs,x,y-.055,z,1.25,.11,.34,steel);
  for(const d of [-.1,0,.1])box(stairs,x,y+.004,z+d,1.18,.012,.026,rail);
  for(const side of [-1,1])stairBeam([x+side*.62,y,z],[x+side*.62,y+1,z],.045);
 }
 for(const side of [-1,1]){
  stairBeam([a[0]+side*.62,a[1]-.08,a[2]],[b[0]+side*.62,b[1]-.08,b[2]],.14,steel);
  for(const height of [.5,1])stairBeam([a[0]+side*.62,a[1]+height,a[2]],[b[0]+side*.62,b[1]+height,b[2]],.065);
 }
}
stairFlight(stairAscent[0],stairAscent[1]);stairFlight(stairAscent[4],stairAscent[5]);
box(stairs,-10.4,2.16,14.8,2.85,.16,1.05,steel);
box(stairs,-10.86,4.22,11.49,1.93,.16,.62,steel); // Top landing spans the full balcony depth and starts where the balcony ends, so the two floors never overlap.
for(let x=-11.75;x<=-9.05;x+=.15)box(stairs,x,2.248,14.8,.035,.015,.95,rail);
for(const x of [-11.82,-8.98]){
 for(const z of [14.35,15.25]){stairBeam([x,.18,z],[x,3.24,z],.12,steel);box(stairs,x,.2,z,.32,.08,.32,steel);}
 for(const y of [2.74,3.24])stairBeam([x,y,14.35],[x,y,15.25]);
}
for(const y of [2.74,3.24])stairBeam([-11.82,y,15.25],[-8.98,y,15.25]);
for(const x of [-11.82,-9.9]){
 stairBeam([x,.18,11.6],[x,5.3,11.6],.12,steel);
 for(const y of [4.8,5.3])stairBeam([x,y,x>-11?11.18:10.65],[x,y,11.8]);
}
for(const y of [4.8,5.3])stairBeam([-10.58,y,11.8],[-9.9,y,11.8]);
stairBeam([-11.82,.3,14.35],[-11.82,2.12,15.25],.08,steel);
flush(stairs);
// Meeting island: navy disk, yellow segmented ring, orange tiled round tabletop.
const meeting=group(scene,-1,.15,7);
cyl(meeting,0,.08,0,4.35,.16,C.navy,96);cyl(meeting,0,.18,0,4.13,.08,C.yellow,96);cyl(meeting,0,.23,0,3.91,.08,C.navy,96);
for(let x=-3.8;x<=3.8;x+=.65)for(let z=-3.8;z<=3.8;z+=.65)if(Math.hypot(x,z)<3.55)box(meeting,x,.276,z,.636,.015,.636,C.navy);
for(let i=0;i<72;i++){const a=i*Math.PI*2/72;const p=group(meeting,Math.cos(a)*4.22,.22,Math.sin(a)*4.22,-a);box(p,0,0,0,.24,.065,.33,C.yellow);flush(p);}
cyl(meeting,0,.4,0,1,.27,C.black,48);for(let i=0;i<7;i++)cyl(meeting,0,.57+i*.19,0,.65,.18,C.black,32);cyl(meeting,0,1.94,0,2.55,.22,0xc9782e,96);cyl(meeting,0,2.055,0,2.5,.035,0xd68739,96);
// Fine tile seams on smooth round top; rows stop exactly at the circular edge.
for(let x=-2.4;x<=2.4;x+=.6){const len=Math.sqrt(2.48**2-x*x)*2;box(meeting,x,2.077,0,.012,.003,len,0xb96c2b);box(meeting,0,2.078,x,len,.003,.012,0xb96c2b);}
const stools=Array.from({length:5},(_,i)=>{const a=Math.PI+i*Math.PI*2/5;return [Math.cos(a)*3.15,Math.sin(a)*3.15,[C.yellow,C.blue,C.teal,C.orange,0x9853bf][i]];});
for(const [x,z,c] of stools){cyl(meeting,x,.36,z,.5,.15,c,40);for(let i=0;i<5;i++)cyl(meeting,x,.5+i*.19,z,.105,.18,C.black,20);ring(meeting,x,.58,z,.34,.055,C.black);cyl(meeting,x,1.45,z,.51,.21,c,48);cyl(meeting,x,1.565,z,.46,.035,c,48);for(let i=0;i<4;i++){const a=i*Math.PI/2;cyl(meeting,x+Math.cos(a)*.32,1.6,z+Math.sin(a)*.32,.065,.045,c,12);}}
sheet(meeting,.6,2.1,.7,.65,.8);sheet(meeting,.25,2.1,-.65,.65,.8);box(meeting,-.85,2.12,-.1,.6,.09,.75,C.black);box(meeting,-.85,2.17,-.1,.48,.012,.6,0xd3e8e6);box(meeting,.95,2.14,-.35,.25,.12,.25,C.black);cyl(meeting,.95,2.34,-.35,.06,.3,0x81888b,16);flush(meeting);
await stage('Parking the vehicles…');
function wheel(parent,x,y,z,r=.55){
 cyl(parent,x,y,z,r,.38,0x202226,32,0,0,Math.PI/2);
 for(let k=0;k<24;k++){const a=k*Math.PI/12;piece(parent,geom('box',.4,.09,r*.17),mat(0x292c2e),x,y+Math.cos(a)*r,z+Math.sin(a)*r,a,0,0);}
 const side=Math.sign(x)||1,face=x+side*.21;
 cyl(parent,face,y,z,r*.64,.055,0xa7adb2,24,0,0,Math.PI/2);cyl(parent,face+side*.035,y,z,r*.46,.035,0x454d51,24,0,0,Math.PI/2);
 cyl(parent,face+side*.07,y,z,r*.27,.08,0x9da5a9,16,0,0,Math.PI/2);
 for(let k=0;k<6;k++){const a=k*Math.PI/3;cyl(parent,face+side*.07,y+Math.cos(a)*r*.44,z+Math.sin(a)*r*.44,r*.065,.04,0xc5cbcd,8,0,0,Math.PI/2);}
}
// A clear molded LEGO window in a thick black frame.
function vehicleWindow(root,x,y,z,w,h,ry=0){
 const g=group(root,x,y,z,ry);
 for(const side of [-1,1]){box(g,side*(w/2+.035),0,0,.075,h+.15,.12,C.black);box(g,0,side*(h/2+.035),0,w+.15,.075,.12,C.black);}
 const pane=new T.Mesh(new T.BoxGeometry(w,h,.045),new T.MeshPhysicalMaterial({color:0x20323c,transparent:true,opacity:.65,roughness:.07,metalness:0,clearcoat:1,depthWrite:false}));pane.position.z=.04;g.add(pane);flush(g);
}
// Brick-built red cab, open light-grey trailer, white bumper and twin stacks.
const truck=group(scene,22.6,-1.12,-4,Math.PI/2);
// Headlamps (written by hand, Claude Code): off while parked, on while the truck is running.
const truckLampMat=new T.MeshStandardMaterial({color:0xd9d6cc,emissive:0xfff0c8,emissiveIntensity:0,roughness:.2});
box(truck,0,.65,0,2.8,.35,10.8,C.black,true);
for(const z of [-3.8,-2.4,2.65,4.15])for(const x of [-1.45,1.45])wheel(truck,x,.67,z,.65);
// Individual red courses, with narrower side sections around the wheel arches.
for(let row=0;row<7;row++){
 const y=1.42+row*.48;
 if(row<4)for(let xx=0;xx<4;xx++)box(truck,(xx-1.5)*.69,y,4.7,.675,.465,.26,C.red,row===6);
 for(const side of [-1,1])for(let zz=0;zz<(row>=4?1:3);zz++)box(truck,side*1.31,y,2.35+zz*.72,.18,.465,.705,C.red,row===6);
}
// Brick A-pillars, window headers and rear wall close the cab around its clear panes.
box(truck,0,3.2,2.18,2.7,2.9,.18,C.red);
box(truck,0,4.5,4.7,2.8,.3,.26,C.red);
for(const side of [-1,1]){
 box(truck,side*1.3,3.72,4.7,.22,1.55,.26,C.red);
 box(truck,side*1.31,3.72,4.49,.18,1.55,.26,C.red);
 box(truck,side*1.31,3.72,2.96,.18,1.55,.46,C.red);
 box(truck,side*1.31,4.5,3.45,.18,.3,2.4,C.red);
}
box(truck,0,4.74,3.45,2.8,.18,2.85,C.red,true);
for(let xx=0;xx<4;xx++)for(let zz=0;zz<4;zz++)box(truck,(xx-1.5)*.69,4.85,2.35+zz*.72,.675,.055,.705,C.red);
box(truck,0,1.6,3.5,2.5,.2,2.4,C.black,true);box(truck,0,3.02,4.35,2.45,.16,.35,C.black);
box(truck,.65,2.55,3.55,.7,.14,.7,C.black);box(truck,.65,2.85,3.2,.7,.65,.12,C.black);

const truckSteering=new T.Mesh(new T.TorusGeometry(.2,.03,8,20),mat(C.black));truckSteering.position.set(.65,3.05,4.15);truckSteering.rotation.x=.8;truck.add(truckSteering);
vehicleWindow(truck,0,3.72,4.87,2.35,1.2);
vehicleWindow(truck,1.45,3.72,3.75,1.1,1.2,Math.PI/2);
vehicleWindow(truck,-1.45,3.72,3.75,1.1,1.2,-Math.PI/2);
for(const side of [-1,1]){box(truck,side*1.48,2.8,3.6,.06,.085,.32,0xc9cdd0);box(truck,side*1.67,3.7,4.55,.23,.5,.18,C.black);box(truck,side*1.52,3.7,4.55,.35,.05,.06,C.black);box(truck,side*1.45,1.2,3.5,.25,.15,.65,0x9aa4aa,true);}
// Reference's white belt across the cab, SNOT-facing round studs and round headlamps.
box(truck,0,2.6,4.94,2.8,.3,.17,C.white);
for(let x=-1.2;x<=1.2;x+=.4)cyl(truck,x,2.6,5.05,.12,.07,C.white,16,Math.PI/2);
box(truck,0,1.98,4.97,2.25,.82,.18,C.white);
box(truck,0,1.12,5.03,3,.3,.3,0x69757b,true);box(truck,0,.94,5.18,1.8,.13,.09,C.black);
for(const side of [-1,1]){
 cyl(truck,side*1.13,2.04,5.1,.2,.12,truckLampMat,24,Math.PI/2);cyl(truck,side*1.38,1.92,5.02,.11,.1,C.orange,16,Math.PI/2);
 for(let j=0;j<4;j++)cyl(truck,side*1.4,1.02,1.15+j*.2,.3,.19,0xaab3b7,24,Math.PI/2);
 for(let j=0;j<8;j++)cyl(truck,side*1.13,4.05+j*.28,2.18,.105,.265,0xbcc2c4,16);
 cyl(truck,side*1.13,6.22,2.18,.15,.13,0x92999c,16);
}
box(truck,0,1.24,-1.9,3,.22,7.2,0xb4bec4,true);
// Rear part of both side curtains is open, revealing pallets and inner lamp.
for(let layer=0;layer<8;layer++)for(let k=0;k<9;k++)for(const side of [-1,1]){
 if(k<3)continue;
 box(truck,side*1.46,1.6+layer*.4,-5.15+k*.8,.12,.39,.785,0xc9d0d4,layer===7);
}
box(truck,0,3.02,1.65,3,3.6,.14,0xc9d0d4);
for(let k=0;k<9;k++)box(truck,0,4.86,-5.15+k*.8,3.05,.15,.785,0xd7dcdf,k===8);
// Door leaves are hinged open beside the cargo aperture, rather than sealing its rear.
for(const side of [-1,1]){
 const door=group(truck,side*1.48,3.02,-5.55,side*Math.PI*.55);
 for(let row=0;row<8;row++)box(door,-side*.72,-1.4+row*.4,0,1.42,.39,.09,C.white);
 box(door,-side*1.2,0,.08,.045,2.65,.07,0x87949d);flush(door);
 box(truck,side*1.47,3.02,-3.15,.13,3.6,.13,0x929da5,true);
 for(let k=0;k<4;k++)cyl(truck,side*1.48,1.6+k*.8,-5.55,.09,.3,0x87949d,12);
}
for(const x of [-1.54,1.54])for(let k=0;k<12;k++)box(truck,x,1.44,-5.15+k*.6,.03,.08,.3,k%2?C.white:C.red);
for(let row=0;row<3;row++)for(let side of [-.7,.7]){pallet(truck,side,1.35,-2.3+row*1.05,.95,.95);crate(truck,side,1.7,-2.3+row*1.05,.83,.7,.83);}
cyl(truck,0,4.55,-4.5,.16,.12,glow,16);const cargoLamp=new T.PointLight(0xffd096,12,5,2);cargoLamp.position.set(0,3.9,-4.8);truck.add(cargoLamp);flush(truck);
// Outdoor yard is lower than the warehouse; the trailer deck meets the dock floor.
const yard=group();box(yard,26,-1.33,-2,18,.4,37,0x535f65);
for(let x=17.4;x<35;x+=.4)for(let z=-19.8;z<16;z+=.4)cyl(yard,x,-1.09,z,.115,.08,0x707b81,12);
for(const z of [-6.7,-1.3])for(let x=18;x<35;x+=1.4)box(yard,x,-1.05,z,1.1,.07,.14,C.yellow);
for(let z=-19;z<=15;z+=1)if(z<-7||z>1.6)box(yard,17.8,-1.02,z,1.4,.18,.98,0xbdc4c5);
// Loading portal, rubber bumpers, awning and ribbed exterior cladding.
for(const z of [-6.65,1.15]){box(yard,17.1,2.85,z,.55,5.7,.38,C.black,true);box(yard,17.35,.6,z,.25,1.15,.45,C.black);box(yard,17.55,-.4,z,.2,1.4,.2,C.yellow);}
box(yard,17.1,5.65,-2.75,.65,.5,8.4,C.black,true);box(yard,17.6,6.1,-2.75,1.8,.18,8.6,0x4d5960,true);
for(let z=-19.5;z<15.5;z+=.32)if(z<-7||z>1.6)box(yard,17.26,5.1,z,.075,10.2,.06,0xa9b0b1);
// Raised side apron leaves the trailer deck clear; the parked forklift is visible outside.
box(yard,17.1,.12,-2.75,.5,.18,7.3,0x8b969e,true);
box(yard,18.15,.12,-.65,2.6,.18,2.7,0x8b969e,true);
for(const z of [-1.8,.5])for(const x of [17.1,19.2]){box(yard,x,-.42,z,.22,1.15,.22,C.black,true);}
for(let i=0;i<4;i++)box(yard,18.6,-.02-i*.28,.9+i*.34,1.05,.18,.35,0xa3adb2,true);
for(let x=17.1;x<18.2;x+=.4)box(yard,x,.65,.65,.075,1.1,.075,C.black);
box(yard,17.55,1.22,.65,1.1,.09,.09,C.black);
for(const z of [-6,-4,-2]){cyl(yard,17.65,5.92,z,.13,.16,glow,16);halo(yard,17.75,5.8,z,1.1);}
for(let z=-19;z<16;z+=1.6){box(yard,17.5,10.65,z,1.1,.2,1.585,0x57636a,true);if(Math.round((z+19)/1.6)%3===0){cyl(yard,17.7,10.4,z,.19,.15,glow,16);halo(yard,17.85,10.3,z,1.4);}}
twoSidedLabel(yard,'RECEIVING 01',17.48,5.65,-2.75,3.5,.35,'#20282b','#ffe393',Math.PI/2);
const dockSignal=group(yard,17.5,2,1.4,Math.PI/2);box(dockSignal,0,0,0,.45,1.2,.25,C.black);
// The yard signal's lamps really light (written by hand, Claude Code): red while the driver waits, green on release.
const dockLamps=[C.red,C.yellow,0x35bd43].map((c,i)=>{const m=new T.MeshStandardMaterial({color:c,emissive:c,emissiveIntensity:.05,roughness:.25});cyl(dockSignal,0,.35-i*.35,.15,.13,.07,m,16,Math.PI/2);return m;});
flush(dockSignal);
const dockGlow=new T.PointLight(0xff3b2a,14,5,2);dockGlow.position.set(0,.35,.6);dockSignal.add(dockGlow);
const lampOn=[0xff2a1a,0xffc21a,0x2dff4a],lampOff=[0x3a1210,0x3a2c0c,0x0f2a14];
function setDockSignal(go){dockLamps.forEach((m,i)=>{const on=i===(go?2:0);m.color.setHex(on?lampOn[i]:lampOff[i]);m.emissive.setHex(on?lampOn[i]:0x000000);m.emissiveIntensity=on?4:0;});dockGlow.color.setHex(go?0x45ff5c:0xff3b2a);dockGlow.position.y=go?-.35:.35;}
setDockSignal(false);
person(yard,17.9,-1.05,2.4,0x72933d,0x242521,true,.9,1.1);flush(yard);
// Driveable forklift. Front is local -Z; mast and lifting carriage are separate.
const fork=group(scene,18.2,.18,-.6,-Math.PI/2);const lift=group(fork,0,0,-1.45);
box(fork,0,.7,.1,1.5,.6,2.2,C.yellow,true);box(fork,0,1.06,.65,1.5,.25,.85,C.yellow,true);box(fork,0,1.25,-.2,.66,.16,.7,C.black);box(fork,0,1.57,.15,.66,.55,.16,C.black);
for(const x of [-.8,.8])for(const z of [-.72,.8])wheel(fork,x,.46,z,.43);
for(const x of [-.65,.65])for(const z of [-.85,.85])box(fork,x,1.9,z,.11,2,.11,C.black);
box(fork,0,2.92,0,1.6,.14,2.05,C.black,true);for(let k=0;k<5;k++)box(fork,-.6+k*.3,2.9,0,.08,.08,1.9,C.black);
cyl(fork,0,3.08,.5,.13,.2,C.orange,16);cyl(fork,0,2.99,.5,.19,.06,C.black,16);
for(const x of [-.56,.56]){box(fork,x,1.65,-1.25,.16,3,.2,C.black);box(lift,x,.25,-.65,.14,.1,1.6,0x777f83);}box(lift,0,.6,0,1.3,.9,.12,C.black);box(fork,0,3.1,-1.25,1.35,.18,.22,C.black,true);
const steering=new T.Mesh(new T.TorusGeometry(.2,.035,8,20),mat(C.black));steering.position.set(0,1.6,-.7);steering.rotation.x=.6;fork.add(steering);
person(fork,0,.65,-.05,C.blue,0x29271e,true,.65,Math.PI);
const forkLampMat=new T.MeshStandardMaterial({color:0xd9d6cc,emissive:0xfff0c8,emissiveIntensity:0,roughness:.2});
for(const x of [-.5,.5])cyl(fork,x,2.72,-1.12,.11,.08,forkLampMat,16,Math.PI/2);
flush(fork);flush(lift);
// Forklift and truck headlights (written by hand, Claude Code): on while the vehicle moves or runs.
function beam(root,x,y,z,tz){const l=new T.SpotLight(0xfff0d0,0,14,.5,.6,1.5);l.position.set(x,y,z);l.target.position.set(x,0,tz);root.add(l,l.target);return l;}
const forkBeam=beam(fork,0,2.6,-1.25,-7),truckBeam=beam(truck,0,2.1,5.3,13);
const lastFork=new T.Vector3();let forkLitUntil=0;
function updateHeadlights(now){
 if(fork.position.distanceToSquared(lastFork)>1e-6)forkLitUntil=now+.8;lastFork.copy(fork.position);
 const forkOn=now<forkLitUntil,truckOn=!!state.running;
 forkLampMat.emissiveIntensity=forkOn?4:0;forkBeam.intensity=forkOn?40:0;
 truckLampMat.emissiveIntensity=truckOn?4:0;truckBeam.intensity=truckOn?50:0;
}
// Delivery pallet and gate, beyond the meeting area.
const delivery=group(scene,18.1,.18,-4,Math.PI/2);pallet(delivery,0,0,0,1.8,1.6);flush(delivery);
let cartons=group(delivery);let currentCase='ok';
function disposeLoadGraphics(root){root.traverse(o=>{if(o.isInstancedMesh)o.dispose();else if(o.isMesh&&o.material.map?.isCanvasTexture){o.geometry.dispose();o.material.map.dispose();o.material.dispose();}});}
function buildLoad(overrideCount=null,spread=false){
 delivery.remove(cartons);disposeLoadGraphics(cartons);batches.delete(cartons);cartons=group(delivery);
 // A floor recount uses the same carton dimensions; the pallet is temporarily removed.
 for(const child of delivery.children)if(child.isInstancedMesh)child.visible=!spread;
 const count=overrideCount??(currentCase==='eksik'?11:12),stacked=currentCase==='belirsiz'&&overrideCount===null;
 for(let i=0;i<count;i++){
  const row=spread?0:stacked?Math.floor(i/4):Math.floor(i/6),j=spread?i:stacked?i%4:i%6;
  const x=spread?(j%4-1.5)*.55:stacked?(j%2-.5)*.6:(j%3-1)*.55;
  const z=spread?(Math.floor(j/4)-1)*.72:stacked?(Math.floor(j/2)-.5)*.72:(Math.floor(j/3)-.5)*.72;
  const y=(spread?0:.36)+row*.56;
  if(currentCase==='hasarli'&&i===11){const broken=group(cartons,x,y,z);broken.rotation.z=.15;box(broken,0,.13,0,.51,.26,.64,C.tan);box(broken,.08,.27,0,.36,.035,.64,C.tan);flush(broken);}
  else crate(cartons,x,y,z,.51,.48,.64);
  label(cartons,currentCase==='wrong'?'CORN OIL':'SUNFLOWER OIL',x,y+.22,z+.335,.46,.13,'#fff8df','#253b40');
  if(currentCase==='hasarli'&&i===11){box(cartons,x,y+.55,z+.34,.32,.06,.02,C.red);box(cartons,x,y+.62,z+.34,.055,.25,.02,C.red);}
 }
 flush(cartons);
}
buildLoad();
const palletTag=twoSidedLabel(delivery,'UNVERIFIED',0,1.7,.87,1.7,.3,'#243238','#ffffff');
function updatePalletTag(destination,quantity=null){const text=`P-${String(deliveryNumber).padStart(3,'0')} / ${destination}${quantity===null?'':' / '+quantity}`;for(const tag of [palletTag,receivingScene.printed]){const cv=tag.material.map.image,ctx=cv.getContext('2d');const refused=destination.startsWith('REFUSED');ctx.fillStyle=refused?'#c0392b':'#ffffff';ctx.fillRect(0,0,cv.width,cv.height);ctx.fillStyle=refused?'#ffffff':'#153d30';ctx.font=`bold ${Math.round(cv.height*.44)}px Arial`;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(text,cv.width/2,cv.height/2,cv.width-12);tag.material.map.needsUpdate=true;}}
const zone={x:4,z:-5.5};const gate=group(scene,zone.x,.18,zone.z);
for(const z of [-1.6,1.6])box(gate,0,.03,z,4,.06,.12,C.yellow);for(const x of [-2,2])box(gate,x,.03,0,.12,.06,3.2,C.yellow);
box(gate,2.3,.75,-1.8,.5,1.5,.55,C.black,true);box(gate,2.3,1.6,-1.8,.45,.3,.5,C.yellow);
const barrier=group(gate,2.3,1.75,-1.8);box(barrier,-1.95,0,0,3.9,.2,.18,C.white);for(let k=0;k<6;k++)box(barrier,-.25-k*.65,0,.105,.3,.205,.02,C.red);flush(barrier);
box(gate,-2.4,1.4,-1.9,.14,2.8,.14,C.black);box(gate,-2.4,2.85,-1.9,.48,1.2,.35,C.black);
const signals=[];for(let i=0;i<3;i++){const material=new T.MeshStandardMaterial({color:[0xd62e1e,0xf9b722,0x40a34d][i],emissive:[0xd62e1e,0xf9b722,0x40a34d][i],emissiveIntensity:.06,roughness:.2});const light=new T.Mesh(new T.CylinderGeometry(.14,.14,.06,24),material);light.rotation.x=Math.PI/2;light.position.set(-2.4,3.2-i*.35,-1.69);gate.add(light);signals.push(light);}
box(gate,0,4.1,0,4.8,.18,.18,C.white,true);for(const x of [-2.4,2.4])box(gate,x,2.1,0,.14,4.2,.14,C.white);box(gate,0,3.9,0,.55,.35,.45,C.white);cyl(gate,0,3.68,.02,.12,.12,C.black,16);twoSidedLabel(gate,'RECEIVING',0,4.4,.12,2.5,.4,'#ffcc00','#243238');flush(gate);

// Spare cartons and safety cones stay at the edges.
const props=group();for(const [x,z] of [[-4,-10.5],[13,-8]]){pallet(props,x,.16,z);for(let i=0;i<3;i++)crate(props,x+(i-1)*.55,.52,z,.5,.6,.65);}
for(const [x,z] of [[6,-7.5],[6,-3.5],[-8,10]]){box(props,x,.2,z,.5,.12,.5,C.orange);const cone=new T.Mesh(new T.CylinderGeometry(.07,.2,.55,16),mat(C.orange));cone.position.set(x,.5,z);props.add(cone);cyl(props,x,.55,z,.12,.1,C.white,16);}flush(props);
// Marked circulation and receiving partition, matching collision solids.
const circulation=group();
for(const [x,w] of [[-10.775,1.25],[-3.325,11.25],[11.65,10.7]]){for(let xx=x-w/2;xx<=x+w/2;xx+=1)box(circulation,xx,.8,-7.3,.1,1.4,.1,C.yellow);box(circulation,x,1.45,-7.3,w,.1,.12,C.yellow);box(circulation,x,.6,-7.3,w,.08,.1,C.black);}
for(let z=-6;z<=11.2;z+=.8)box(circulation,-9.6,.17,z,1.1,.03,.6,0x439b89);
const walkSign=label(circulation,'PEDESTRIANS',-9.6,.2,4,3,.65,'#287a6d','#ffffff');walkSign.rotation.x=-Math.PI/2;
const vehicleSign=label(circulation,'FORKLIFT ROUTE',8,.2,1,3,.65,'#ffcc00','#243238');vehicleSign.rotation.x=-Math.PI/2;
twoSidedLabel(circulation,'CONTROLLED STORAGE',0,1.9,-7.3,3,.4,'#243238','#fff3b2');
for(const [id,a] of Object.entries(areas)){if(id==='inspection'||id==='refused')continue;const col=id==='accepted'?0x369469:id==='hold'?C.orange:C.red;for(const dz of [-a.hz,a.hz])box(circulation,a.x,.19,a.z+dz,a.hx*2,.04,.09,col);for(const dx of [-a.hx,a.hx])box(circulation,a.x+dx,.19,a.z,.09,.04,a.hz*2,col);const tag=label(circulation,`${id==='returned'?'RETURN':id==='hold'?'HOLD / NO STOCK':id==='arrival'?'UNVERIFIED':'ACCEPTED'} / ${a.address}`,a.x,.22,a.z+a.hz+.5,3.2,.55,'#f4f3e9','#243238');tag.rotation.x=-Math.PI/2;}
// A dedicated put-away rack, with one empty pallet slot on each level.
for(const x of [2.5,5.5])for(const z of [-13.65,-11.15])box(circulation,x,2.3,z,.14,4.3,.14,C.blue,true);
box(circulation,4,2.45,-12.4,3,.16,2.6,C.yellow);box(circulation,4,4.4,-12.4,3,.12,2.6,C.yellow);
twoSidedLabel(circulation,'A-01 · L0 / L1',4,4.65,-11.08,2.8,.35,'#0055bd','#ffffff');
// Q-01 markings are provided by the receiving equipment module.
flush(circulation);
const receivingScene=buildReceivingScene({T,scene,group,box,cyl,label,twoSidedLabel,flush,sheet,C});
const walkingGuide=person(scene,-9.6,.18,3,0x72933d,0x242521,false,.8);let walkStarted=0;
await stage('Finishing the details…');
let caseData;
try{const res=await fetch('../data.json');if(!res.ok)throw Error('data');caseData=await res.json();}catch{caseData=null;}
const state={paused:false,speed:.5,mode:'orbit',held:false,running:false,phase:0,t:0,result:null};
const completedLoads=[];let automation=null,transferTarget=null,verified=false,reviewResolved=false,deliveryNumber=1;let forkHeight=0;
let dockReady=false,arrivalDone=false,inspectionRun=null,physicalLocation='trailer',locationConfirmed=false,handlingDecision=null,reviewTask=null,receivedQty=null;
const flowList=$('receiving-steps');receivingSteps.forEach(text=>{const li=document.createElement('li');li.textContent=text;flowList.append(li);});
function flowStep(index,text){[...flowList.children].forEach((li,i)=>{li.dataset.state=i<index?'done':i===index?'active':'pending';if(i===index)li.setAttribute('aria-current','step');else li.removeAttribute('aria-current');});if(text)status(text);}
function entryNow(){return caseData?.cases.find(c=>c.id===currentCase);}

const keys=new Set();let cameraTween=null;let barrierTarget=0;
const views={hero:{eye:[-1,6.5,21],target:[-1,3.5,-4]},gatecheck:{eye:[10.5,6.2,3.2],target:[2.6,1.8,-6.4]},table:{eye:[8,7,18],target:[-1,1.5,7]},rooms:{eye:[4,8,15],target:[-13,3.9,1]},dock:{eye:[18,16,16],target:[8,0,-4]},inspection:{eye:[10,13,17],target:[-2,1,-3]},review:{eye:[10,16,24],target:[10,1,7]},plan:{eye:[31,39,35],target:[6,0,0]},outside:{eye:[33,5.8,10],target:[22,2.7,-4]}};
// A live cinematic tour of this exact warehouse, with no external video.
let introActive=false,introStarted=0;
const introShots=[
 {view:'outside',title:'The note says 12 cartons.',detail:'THE LOADING DOCK · A SHORT DELIVERY',offset:[-2,.4,1]},
 {view:'dock',title:'The camera counts 11. The gate refuses the write.',detail:'THE RECEIVING FLOOR · CAMERA, VOICE, GATE',offset:[-2,-.5,-1]},
 {view:'rooms',title:'Ten agents. One rule: count before you post.',detail:'MEET THE CREW',offset:[-2,-.5,-1]},
 {view:'table',title:'24 of 24 gate decisions right. 0 wrong receipts.',detail:'SIX DELIVERIES · FOUR LANGUAGES · META GLOBAL AI HACKATHON',offset:[-2,-.4,-1]}
];
function startIntro(){
 if(state.running)reset();
 cameraTween=null;keys.clear();state.mode='orbit';introStarted=performance.now();introActive=true;
 closeNavigation();$('cast-card').hidden=true;$('touch').hidden=true;
 document.body.classList.remove('cast-focus','clean');document.body.classList.add('intro-playing');
 $('warehouse-intro').hidden=false;controls.enabled=false;$('skip-intro').focus();
}
function endIntro(restore=true){
 introActive=false;document.body.classList.remove('intro-playing');$('warehouse-intro').hidden=true;
 controls.enabled=true;if(restore)setView('hero');
}
function updateIntro(){
 const elapsed=(performance.now()-introStarted)/1000,index=Math.floor(elapsed/5);
 if(index>=introShots.length){endIntro();return;}
 const shot=introShots[index],v=views[shot.view],p=(elapsed%5)/5,q=p*p*(3-2*p);
 const target=new T.Vector3(...v.target),eye=new T.Vector3(...v.eye).addScaledVector(new T.Vector3(...shot.offset),q);
 if(camera.aspect<1.25)eye.sub(target).multiplyScalar(Math.min(1.6,1.25/camera.aspect)).add(target);
 camera.position.copy(eye);controls.target.copy(target);camera.lookAt(target);
 $('intro-title').textContent=shot.title;$('intro-detail').textContent=shot.detail;
 $('intro-progress').style.transform=`scaleX(${elapsed/20})`;
 $('warehouse-intro').style.setProperty('--cut',String(Math.max(0,1-Math.min(elapsed%5,5-elapsed%5)/.3)));
 document.body.dataset.introShot=shot.view;
}
$('skip-intro').onclick=()=>endIntro();$('replay-intro').onclick=startIntro;
document.addEventListener('keydown',e=>{if(introActive&&e.key==='Escape'){e.preventDefault();e.stopImmediatePropagation();endIntro();}},true);
function status(text,color='#799c70'){$('status').querySelector('span').textContent=text;$('status').querySelector('i').style.background=color;}
function setView(name){if(introActive)endIntro(false);$('scene-nav').hidden=true;$('open-nav').setAttribute('aria-expanded','false');document.body.classList.remove('cast-focus');state.mode='orbit';$('touch').hidden=true;$('drive').innerHTML='Drive forklift <span>W A S D</span>';const v=views[name];const aim=new T.Vector3(...v.target);const eye=new T.Vector3(...v.eye);if(camera.aspect<1.25)eye.sub(aim).multiplyScalar(Math.min(1.75,1.25/camera.aspect)).add(aim);cameraTween={from:camera.position.clone(),targetFrom:controls.target.clone(),to:eye,targetTo:aim,t:0};document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===name));controls.enabled=true;}
let meetingRun=null;
const castHomes=new Map(castSlots.filter(s=>s.actor).map(s=>[s.id,{position:s.actor.position.clone(),rotation:s.actor.rotation.clone()}]));
let followupData=null;try{const r=await fetch('../data-en.json');if(r.ok)followupData=await r.json();}catch{}
function resetMeeting(){
 meetingRun=null;document.body.classList.remove('conversation-open');$('meeting-chat').hidden=true;$('speech').hidden=true;
 for(const slot of castSlots){const home=castHomes.get(slot.id);if(!home)continue;slot.room.add(slot.actor);slot.actor.position.copy(home.position);slot.actor.rotation.copy(home.rotation);slot.onFloor=false;slot.route=null;slot.seated=false;slot.walk?.stop();slot.idle?.play();}
}
function resetReceiving(){
 dockReady=false;arrivalDone=false;inspectionRun=null;reviewTask=null;physicalLocation='trailer';locationConfirmed=false;handlingDecision=null;
 receivingScene.reset();setDockSignal(false);updatePalletTag('UNVERIFIED');$('prepare-dock').disabled=false;$('prepare-dock').textContent='Prepare dock & receive documents';
 $('dock-checks').textContent='Vehicle restraint · bridge plate · driver refuge · delivery note';
 $('review-inspected').checked=false;$('review-document').checked=false;$('review-count').value='0';$('location-code').value='';$('location-confirm').hidden=true;
 for(const slot of castSlots){slot.workRoute=null;slot.working=false;}
 areas.accepted.y=.18;areas.accepted.address='A-01-L0';$('storage-level').value='0';flowStep(0);
}
$('prepare-dock').onclick=()=>{
 if(state.running||dockReady)return;
 if(!entryNow()){status('Recorded delivery data is unavailable. Refresh before starting.','#bd4931');return;}
 if(introActive)endIntro(false);setView('outside');state.running=true;state.phase=8;state.t=0;state.paused=false;
 $('prepare-dock').disabled=true;$('case').disabled=true;document.querySelector('.playback').hidden=false;
 flowStep(0,'Driver waits in the marked refuge. Receiver checks the note, vehicle restraint and dock bridge.');
};
function updateDock(){
 const t=state.t;
 $('dock-checks').textContent=t<2?`1 / 3 · Driver in refuge; delivery note matched to ${order()?.number||'the purchase order'}.`:t<4?'2 / 3 · Trailer secured; deck and pallet condition checked.':'3 / 3 · Bridge plate in position; unloading route clear.';
 if(t>=6){receivingScene.prepare();dockReady=true;state.running=false;state.phase=0;$('prepare-dock').textContent='Dock prepared';$('demo').disabled=false;flowStep(1,'Dock ready. Play delivery or drive the forklift to B-01.');}
}
function deployWorker(id,x,z){
 const slot=castSlots.find(s=>s.id===id);if(!slot?.actor)return;
 if(slot.onFloor)return;
 const home=castHomes.get(id),points=[home.position.clone(),new T.Vector3(1.9,home.position.y,-.3),new T.Vector3(1.9,home.position.y,3.1)].map(v=>slot.room.localToWorld(v));
 const y=slot.index>=5?4.3:.18;points.forEach(p=>p.y=y);
 if(slot.index>=5)points.push(...stairAscent.slice().reverse().map(p=>new T.Vector3(...p)),...stairApproach.slice(0,-1).reverse().map(p=>new T.Vector3(...p)));
 points.push(new T.Vector3(-9.6,.18,points.at(-1).z),new T.Vector3(-9.6,.18,-2.7));
 points.push(new T.Vector3(x,.18,-2.7));
 points.push(new T.Vector3(x,.18,z));
 scene.attach(slot.actor);slot.actor.position.copy(points[0]);slot.actor.rotation.set(0,0,0);slot.onFloor=true;slot.seated=false;slot.workRoute=points.slice(1);slot.working=true;slot.room.children.filter(o=>officeDoors.includes(o)).forEach(d=>d.userData.open=true);slot.walk?.reset().play();slot.idle?.stop();
}
function updateWorkActors(dt){
 for(const slot of castSlots){if(!slot.workRoute)continue;const next=slot.workRoute[0];
  if(next){const d=slot.actor.position.distanceTo(next),step=dt*2.8;slot.actor.lookAt(next.x,slot.actor.position.y,next.z);if(d<=step){slot.actor.position.copy(next);slot.workRoute.shift();}else slot.actor.position.addScaledVector(next.clone().sub(slot.actor.position).normalize(),step);}
  else {slot.walk?.stop();slot.idle?.play();slot.actor.lookAt(slot.id==='sef'?10:4,.18,slot.id==='sef'?7:-5.5);if(slot.working)slot.arms?.forEach((a,i)=>a.rotation.x=-.35-Math.sin(state.t*2+i)*.1);}
 }
}
function stageSupervisor(){deployWorker('sef',13.2,5);setView('review');}
function beginInspection(){
 state.mode='orbit';controls.enabled=true;$('touch').hidden=true;setView('inspection');
 inspectionRun={elapsed:0,index:-1};state.phase=6;receivingScene.inspect();
 deployWorker('spark',-2,-4.5);deployWorker('sam',-.5,-1.6);deployWorker('kapi',0,-5.5);
 flowStep(3,'Receiver scans the pallet; Spark reads the note, Sam reviews the camera count, Kapı compares the evidence.');
}
function updateInspection(dt){
 const run=inspectionRun;if(!run)return;
 if(receivingScene.receiver.route.length||castSlots.some(s=>s.workRoute?.length))return;
 run.elapsed+=dt;const index=Math.floor(run.elapsed/3);
 const entry=entryNow();if(!entry){inspectionRun=null;finish();return;}
 const rows=evidenceRows(entry,order());
 const steps=[['Delivery note',rows[0][1]],['Camera count · recorded',rows[1][1]],['Visual inspection · recorded',rows[2][1]],['Receiver / Voice','Physical work is illustrative. No independent voice result was recorded in this scenario.'],['Purchase order',rows[6][1]],['Gate · recorded',rows[4][1]]];
 if(index>=steps.length){inspectionRun=null;finish();return;}
 if(index!==run.index){run.index=index;flowStep(3,steps[index].join(' — '));}
}
function updateReview(dt){
 if(!reviewTask)return;
 if(receivingScene.receiver.route.length||castSlots.some(s=>s.id==='sef'&&s.workRoute?.length))return;
 reviewTask.elapsed+=dt;
 if(reviewTask.elapsed<4)return;
 // Show the physical recount, rather than silently reusing the stacked arrangement.
 if(currentCase==='belirsiz')buildLoad(12,true);
 $('review-inspected').checked=true;reviewTask=null;state.running=false;state.phase=0;
 status('Physical check complete (illustrative). Confirm the intact count; a corrected document is still required where indicated.');showOutcomeActions('hold');
}
function showRecordedConversation(){
 const entry=entryNow();if(!entry)return;
 meetingRun=null;
 openConversation({root:$('meeting-chat'),entry,lines:replayLines(entry,followupData?.cases.find(c=>c.id===currentCase)?.signoff),
  onClose:()=>document.body.classList.remove('conversation-open'),onEvidence:()=>{$('meeting-chat').hidden=true;document.body.classList.remove('conversation-open');renderEvidence();},onLocate:focusCast,
  onWorkflow:()=>{$('meeting-chat').hidden=true;document.body.classList.remove('conversation-open');document.body.classList.remove('cast-focus');}});
 document.body.classList.add('conversation-open');
}
$('show-meeting').onclick=showRecordedConversation;
function reset(){$('match').hidden=true;receivedQty=null;resetReceiving();resetMeeting();buildLoad();for(const load of completedLoads){scene.remove(load.object);disposeLoadGraphics(load.object);}completedLoads.length=0;automation=null;transferTarget=null;verified=false;reviewResolved=false;forkHeight=0;$('evidence').hidden=true;$('outcome-actions').hidden=true;$('next-delivery').hidden=true;document.querySelector('.playback').hidden=true;state.paused=false;$('pause-demo').textContent='Pause';state.running=false;state.held=false;state.phase=0;state.result=null;state.mode='orbit';state.t=0;delivery.parent?.remove(delivery);scene.add(delivery);delivery.position.set(18.1,.18,-4);delivery.rotation.set(0,Math.PI/2,0);fork.position.set(18.2,.18,-.6);fork.rotation.y=-Math.PI/2;lift.position.y=0;barrierTarget=0;signals.forEach(s=>s.material.emissiveIntensity=.06);$('demo').disabled=false;$('case').disabled=false;status('Ready to explore.');setView('hero');}
function pickup(){
 const pose={x:fork.position.x,z:fork.position.z,angle:fork.rotation.y};
 if(physicalLocation==='hold'&&!handlingDecision&&!state.held){status('Resolve the hold before collecting this load.');return false;}
 if(!dockReady){status('Prepare the dock before handling the load.','#c48223');return false;}
 if(state.held){
  const pos=delivery.getWorldPosition(new T.Vector3()),p={x:pos.x,z:pos.z,angle:pose.angle};
  const id=transferTarget||(arrivalDone?'inspection':'arrival'),area=areas[id];
  if(!contained(p,area)){status(`Place the whole pallet inside ${area.address||'the inspection bay'}.`,'#c48223');return false;}
  if(Math.abs(forkHeight-(area.y-.18))>.12){status('Lower / raise the forks to the selected shelf level.','#c48223');return false;}
  if(id!=='refused'&&!placementClear(p,completedLoads.map(o=>rectangle(o.x,o.z,.9,.8,o.angle)))){status('The placement area is occupied or obstructed.','#c48223');return false;}
  scene.attach(delivery);delivery.position.y=area.y;delivery.rotation.y=pose.angle;state.held=false;physicalLocation=id;locationConfirmed=false;forkHeight=0;lift.position.y=0;
  if(id==='arrival'){arrivalDone=true;updatePalletTag('UNVERIFIED B-01');flowStep(2,'B-01: received physically, not yet verified. Move to the yellow inspection bay.');}
  else if(id==='inspection'){updatePalletTag('INSPECTION');if(!verified){state.running=true;state.phase=3;state.t=0;}document.querySelector('.playback').hidden=false;status('Forklift stopped. Receiver and digital checks inspect the load.');}
  else if(id==='refused'){updatePalletTag('REFUSED · RETURN TO SUPPLIER');locationConfirmed=true;handlingDecision='refused';$('outcome-actions').hidden=false;showOutcomeActions(id);if(!automation)$('next-delivery').hidden=false;flowStep(6,`Refused at the dock: the pallet is back on the trailer. Nothing is received against ${order()?.number||'the order'}; the driver takes it back.`);}
  else {flowStep(id==='hold'?4:6,`Delivery ${deliveryNumber} placed in ${area.address}. ${id==='hold'?'Awaiting a separate handling decision.':'Confirm the location to finish.'}`);$('next-delivery').hidden=true;$('outcome-actions').hidden=false;showOutcomeActions(id);}
  return true;
 }
 const pos=delivery.getWorldPosition(new T.Vector3());
 if(!pickupAligned(pose,{x:pos.x,z:pos.z,angle:delivery.rotation.y})||Math.abs(forkHeight-(pos.y-.18))>.12){status('Align squarely with the pallet openings and match the fork height.','#c48223');return false;}
 if(blockedPose(pose.x,pose.z,pose.angle,{...collisionOptions(),held:true,pallet:null})){status('Not enough clearance to lift the pallet.','#c48223');return false;}
 fork.attach(delivery);delivery.position.set(0,.42+forkHeight,-2.25);delivery.rotation.set(0,0,0);state.held=true;physicalLocation='forklift';lift.position.y=forkHeight+.3;
 status('Load secured. Keep it low while travelling.');return true;
}
const resultCopy={ok:'12 cartons verified. The receiving gate is open.',eksik:'11 cartons found; the note says 12. ERP write blocked; handling decision pending.',wrong:'The labels say corn oil; the note and the order say sunflower oil. ERP write blocked: refuse it at the dock.',hasarli:'A carton is damaged. Supervisor review required.',talimat:'Injected instructions found in the note. ERP write blocked; handling decision pending.',belirsiz:'Stacked cartons cannot be counted. Supervisor review required.'};
function renderEvidence(){
 const entry=caseData?.cases.find(c=>c.id===currentCase);const list=$('evidence-rows');list.replaceChildren();
 for(const [name,value] of evidenceRows(entry,order())){const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=name;dd.textContent=value;list.append(dt,dd);}
 $('evidence-note').src='../'+(entry?.images.note||'');$('evidence-camera').src='../'+(entry?.images.camera||'');
 $('evidence-warning').textContent=entry?.note.embedded_instructions?.length?'Untrusted document text — instructions below were NOT executed. '+entry.note.embedded_instructions.join(' | '):entry?.what||'';
 $('evidence').hidden=false;
}
function finish(){
 const entry=caseData?.cases.find(c=>c.id===currentCase);state.running=false;automation=null;
 if(!entry){status('Recorded evidence unavailable. Delivery remains on hold.','#bd4931');$('demo').disabled=false;$('case').disabled=false;return;}
 state.result=entry.gate.action;verified=true;physicalLocation='inspection';barrierTarget=state.result==='post'?-Math.PI*.48:0;
 signals.forEach((s,i)=>s.material.emissiveIntensity=i===({block:0,human:1,post:2}[state.result])?2.5:.06);
 status(resultCopy[currentCase]+(currentCase==='hasarli'?' Recorded proposal: accept 11 intact cartons; isolate 1 damaged carton.':''));showMatch(entry);setView('gatecheck');
 flowStep(state.result==='post'?5:4);$('outcome-actions').hidden=false;showOutcomeActions();
}
// Three-way match (written by hand, Claude Code): what was ordered, what the note says, what is on the pallet.
function showMatch(entry){const o=order(),n=entry.note?.items?.[0],v=entry.spark,c=entry.cross;if(!o||!n||!v){$('match').hidden=true;return;}
 const counted=c?c.agreed:v.cartons_visible,label=english(v.product_on_labels),same=(a,b)=>english(a).toLowerCase().replace(/\s+/g,'')===english(b).toLowerCase().replace(/\s+/g,'');
 const hidden=v.stacked||!v.all_cartons_visible,damaged=v.damaged_cartons||0,told=(entry.note?.embedded_instructions||[]).length>0;
 const palletNote=hidden?' · stacked, some hidden':damaged?` · ${damaged} damaged`:'';
 const rows=[['Ordered',o.number,`${o.ordered} × ${o.product}`,true],['Note','delivery note',`${n.quantity} × ${english(n.description)}${told?' · hidden instruction':''}`,!told&&n.quantity<=o.ordered&&same(n.description,o.product)],['Pallet','camera',`${hidden?counted+' visible':counted} × ${label}${palletNote}`,!hidden&&!damaged&&counted===n.quantity&&same(label,n.description)]];
 $('match-rows').replaceChildren(...rows.map(([k,src,val,ok])=>{const li=document.createElement('li');li.className=ok?'ok':'bad';li.innerHTML=`<b></b><span></span><i></i>`;li.children[0].textContent=k;li.children[1].textContent=val;li.children[2].textContent=ok?'✓':'✗';li.title=src;return li;}));
 $('match-badge').textContent={post:'POST',block:'BLOCK',human:'ASK ŞEF'}[state.result]||'';$('match-badge').className=state.result||'';$('match-say').textContent=resultCopy[currentCase]||'';
 $('match').hidden=false;}
$('match-close').onclick=()=>{$('match').hidden=true;};
function showOutcomeActions(location='inspection'){
 const policy=reviewPolicy(currentCase), accepted=state.result==='post'||handlingDecision==='accepted';
 $('manual-transfer').hidden=location!=='inspection';$('storage-level').disabled=location!=='inspection'||!accepted;
 $('transfer-load').hidden=location!=='inspection';$('transfer-load').textContent=accepted?`Label & put away · A-01-L${$('storage-level').value}`:initialDestination(state.result,currentCase)==='refused'?'Refuse at the dock · reload to trailer':'Move to exception hold · H-01';
 $('review-controls').hidden=location!=='hold';$('review-proposal').textContent=policy.task;
 $('review-approve').hidden=!policy.accept;$('review-count').disabled=!policy.accept;
 $('review-document-row').hidden=!policy.document;
 $('review-inspect').disabled=!!reviewTask;$('review-inspect').textContent=reviewTask?'Receiver is checking…':'Perform recount / document check';
 $('location-confirm').hidden=!['accepted','returned'].includes(location);if(location==='refused'){$('transfer-load').hidden=true;$('manual-transfer').hidden=true;}
 $('location-prompt').textContent=`P-${String(deliveryNumber).padStart(3,'0')} → ${areas[location]?.address||''}. Enter the destination address to confirm this simulated scan.`;
 if(location==='hold')stageSupervisor();
}
function startCommands(commands,onComplete){automation={commands:commands.map(x=>[...x]),index:0,remaining:null,onComplete};state.running=true;state.paused=false;state.phase=4;$('pause-demo').textContent='Pause';document.querySelector('.playback').hidden=false;}
function stepCommands(dt){
 const a=automation;if(!a)return;const cmd=a.commands[a.index];if(!cmd){automation=null;state.running=false;a.onComplete?.();return;}
 const [op,value]=cmd;
 if(op==='wait'){a.remaining=(a.remaining??value)-dt;if(a.remaining<=0){a.index++;a.remaining=null;}return;}
 if(op==='pickup'||op==='drop'){
  if(!pickup()){state.paused=true;$('pause-demo').textContent='Resume';return;}
  a.index++;a.remaining=null;return;
 }
 if(op==='lift'){forkHeight=T.MathUtils.damp(forkHeight,value,5,dt);lift.position.y=forkHeight+.3;if(state.held)delivery.position.y=.42+forkHeight;if(Math.abs(forkHeight-value)<.02){forkHeight=value;a.index++;}return;}
 if(a.remaining===null)a.remaining=value;
 const delta=Math.sign(a.remaining)*Math.min(Math.abs(a.remaining),dt*(op==='turn'?.8:2.4));
 const next=movePose({x:fork.position.x,z:fork.position.z,angle:fork.rotation.y},op==='move'?delta:0,op==='turn'?delta:0,collisionOptions());
 fork.position.set(next.x,.18,next.z);fork.rotation.y=next.angle;
 if(next.hit){state.paused=true;$('pause-demo').textContent='Resume';status('Route obstructed. Movement stopped; reset or clear the route.','#bd4931');return;}
 a.remaining-=delta;if(Math.abs(a.remaining)<.0001){a.index++;a.remaining=null;}
}
function runDemo(){if(state.running)return;if(physicalLocation!=='trailer'||Math.hypot(fork.position.x-18.2,fork.position.z+.6)>.1||Math.cos(fork.rotation.y+Math.PI/2)<.999){status('Continue manual handling, or press R and prepare the next exercise before guided playback.');return;}if(!dockReady){status('Complete dock preparation first.');return;}setView('dock');$('demo').disabled=true;$('case').disabled=true;flowStep(1,'Unload to B-01; the pallet is not accepted stock yet.');const commands=collectRoute.map(c=>[...c]);commands.splice(7,0,['drop'],['wait',3],['pickup']);startCommands(commands,()=>{state.running=true;state.phase=3;state.t=0;});}
// The purchase order the delivery is received against (data.json, the Turkish run), in English.
function order(){const o=caseData?.order;return o&&{...o,product:english(o.product)};}
// What this delivery leaves on the order line once it is received.
function onOrder(){const o=order();if(!o||physicalLocation!=='accepted')return '';const q=receivedQty??12,left=o.ordered-q;return ` Received ${q} of ${o.ordered} on ${o.number}${left>0?`; ${left} still open: claim the shortfall from the supplier or close the line`:'; order line complete'}.`;}
function chooseDestination(){transferTarget=initialDestination(state.result,currentCase);const upper=$('storage-level').value==='1';areas.accepted.y=upper?2.53:.18;areas.accepted.address=upper?'A-01-L1':'A-01-L0';updatePalletTag(areas[transferTarget].address,state.result==='post'?12:null);}
function withShelfLift(commands){if(transferTarget!=='accepted'||areas.accepted.y<1)return commands;const copy=commands.map(c=>[...c]),i=copy.findIndex(c=>c[0]==='drop');copy.splice(i,0,['lift',2.35]);return copy;}
function forkPose(){return {x:fork.position.x,z:fork.position.z,angle:fork.rotation.y};}
function manualForTarget(){state.running=false;automation=null;state.mode='orbit';$('drive').click();status(`Manual handling: place the load in ${areas[transferTarget].address}. The selected decision remains separate from the recorded ERP result.`);}
$('transfer-load').onclick=()=>{
 if(!verified||state.running||physicalLocation!=='inspection')return;chooseDestination();$('match').hidden=true;
 $('storage-level').disabled=true;$('transfer-load').hidden=true;$('manual-transfer').hidden=true;$('evidence').hidden=true;
 if(!atRouteStart(forkPose(),'inspection')){manualForTarget();return;}
 setView(transferTarget==='refused'?'dock':'plan');const route=transferTarget==='refused'?refuseRoute.map(c=>[...c]):destinationRoute(transferTarget);if(transferTarget==='hold')route.pop();
 flowStep(transferTarget==='hold'?4:5,transferTarget==='refused'?'Not what was ordered. Reloading the pallet onto the trailer.':transferTarget==='hold'?'ERP result retained. Moving to H-01 for a handling decision.':'Receiver prints the pallet label. Moving to the selected storage location.');
 startCommands(withShelfLift(route),()=>{showOutcomeActions(transferTarget);if(transferTarget==='refused'){$('next-delivery').hidden=false;setView('outside');}});
};
$('storage-level').onchange=()=>{$('transfer-load').textContent=`Label & put away · A-01-L${$('storage-level').value}`;};
$('manual-transfer').onclick=()=>{if(!verified||state.running||physicalLocation!=='inspection')return;chooseDestination();$('match').hidden=true;manualForTarget();};
$('review-inspect').onclick=()=>{
 if(state.running||physicalLocation!=='hold'||reviewTask)return;
 $('review-inspected').checked=false;receivingScene.repack();stageSupervisor();
 reviewTask={elapsed:0};state.running=true;state.phase=7;state.paused=false;document.querySelector('.playback').hidden=false;
 status(reviewPolicy(currentCase).task+' Illustrative handling, not a new AI measurement.');showOutcomeActions('hold');
};
$('review-approve').onclick=()=>{
 if(state.running||physicalLocation!=='hold'||state.held)return;
 const count=Number($('review-count').value);
 if(!canAccept(currentCase,{count,inspected:$('review-inspected').checked,document:$('review-document').checked})){status('Complete the physical check, reconcile the document when required, and confirm the intact count.','#c48223');return;}
 receivedQty=count;reviewResolved=true;handlingDecision='accepted';barrierTarget=-Math.PI*.48;transferTarget='accepted';areas.accepted.y=.18;areas.accepted.address='A-01-L0';
 buildLoad(count);updatePalletTag('A-01-L0',count);
 if(currentCase==='hasarli'){const isolated=group(scene,13,.18,7);pallet(isolated,0,0,0);crate(isolated,0,.36,0,.51,.26,.64);twoSidedLabel(isolated,'Q-01 · 1 DAMAGED',0,1,0,1.5,.3,'#c48223','#ffffff');flush(isolated);completedLoads.push({object:isolated,x:13,z:7,angle:0});}
 $('review-controls').hidden=true;flowStep(5,reviewPolicy(currentCase).document?`Corrected note verified on its own: it now says ${count}, as counted. Not an override of the blocked receipt: a new check, where note, order and count agree. Label and secure the load.`:`Supervisor signs off ${count} (the gate sent this delivery to a person). Label and secure the load.`);
 if(!atRouteStart(forkPose(),'hold')){manualForTarget();return;}
 setView('plan');startCommands(reviewRoute('accepted'),()=>showOutcomeActions('accepted'));
};
$('review-return').onclick=()=>{
 if(state.running||physicalLocation!=='hold'||state.held)return;
 transferTarget='returned';updatePalletTag('R-01');handlingDecision='returned';reviewResolved=true;$('review-controls').hidden=true;
 status('Supervisor authorized a return. Move to R-01 for collection; this is not a completed outbound shipment.');
 if(!atRouteStart(forkPose(),'hold')){manualForTarget();return;}
 setView('plan');startCommands(reviewRoute('returned'),()=>showOutcomeActions('returned'));
};
$('confirm-location').onclick=()=>{
 if(state.running||state.held||!['accepted','returned'].includes(physicalLocation))return;
 const expected=areas[physicalLocation].address;
 if(!locationMatches($('location-code').value,expected)){status(`Location does not match. Read ${expected} at the destination and try again.`,'#c48223');return;}
 locationConfirmed=true;$('next-delivery').hidden=false;$('location-confirm').hidden=true;
 flowStep(7,`${expected} confirmed for P-${String(deliveryNumber).padStart(3,'0')}. ${physicalLocation==='returned'?'Awaiting carrier collection.':'Put-away complete.'}${onOrder()} No live inventory update.`);
};
$('close-evidence').onclick=()=>$('evidence').hidden=true;$('show-evidence').onclick=renderEvidence;
$('next-delivery').onclick=()=>{
 if(state.running||state.held||!locationConfirmed)return;
 const li=document.createElement('li');li.textContent=`Delivery ${deliveryNumber} · ${currentCase} · ${transferTarget==='refused'?'refused · back on the trailer':areas[transferTarget].address} · ERP ${state.result} (recorded) · handling ${handlingDecision||transferTarget} (simulated)${currentCase==='hasarli'&&handlingDecision==='accepted'?' · 1 carton remains Q-01 quarantined':''}`;$('delivery-history').prepend(li);
 // End this exercise. This clears its scene, not persistent inventory or an outbound shipment.
 receivingScene.release();setDockSignal(true);setView('outside');state.running=true;state.phase=9;state.t=0;$('next-delivery').hidden=true;status('Exercise saved. Receiver releases the dock; driver receives the green signal.');
};
$('toggle-panel').onclick=()=>{const collapsed=$('panel').classList.toggle('collapsed');$('panel-controls').hidden=collapsed;$('toggle-panel').textContent=collapsed?'+':'−';$('toggle-panel').setAttribute('aria-expanded',String(!collapsed));$('toggle-panel').setAttribute('aria-label',collapsed?'Expand controls':'Minimize controls');};
$('pause-demo').onclick=()=>{state.paused=!state.paused;$('pause-demo').textContent=state.paused?'Resume':'Pause';};$('play-speed').onchange=()=>{state.speed=Number($('play-speed').value);};
$('demo').onclick=runDemo;$('case').onchange=()=>{currentCase=$('case').value;reset();buildLoad();};
$('drive').onclick=()=>{if(state.running)return;if(!dockReady){status('Prepare the dock before driving.');return;}if(state.mode==='drive'){setView('hero');return;}cameraTween=null;state.mode='drive';controls.enabled=false;$('touch').hidden=false;$('drive').innerHTML='Exit driving <span>ESC</span>';status('Use WASD / arrow keys to drive. E picks up or sets down the load.');document.querySelectorAll('[data-view]').forEach(b=>b.classList.remove('active'));};
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>setView(b.dataset.view));
const castSelect=$('cast-select');
castSlots.forEach(slot=>{const option=document.createElement('option');option.value=slot.id;option.textContent=slot.name+(slot.loaded?'':' — unavailable');castSelect.appendChild(option);});
function focusCast(id){
 const slot=castSlots.find(s=>s.id===id);if(!slot)return;
 setView('rooms');document.body.classList.add('cast-focus');scene.updateMatrixWorld(true);
 const pos=(slot.actor||slot.placeholder).getWorldPosition(new T.Vector3());
 const target=pos.clone().add(new T.Vector3(0,1.35,0));
 cameraTween={from:camera.position.clone(),targetFrom:controls.target.clone(),to:target.clone().add(new T.Vector3(5.3,.75,1.4)),targetTo:target,t:0};
 $('cast-caption').textContent=castJobs[slot.index];
 if(slot.wave){const action=slot.mixer.clipAction(slot.wave);action.reset().setLoop(T.LoopOnce,1);action.clampWhenFinished=false;action.play();}
 status(`${slot.name} · ${castJobs[slot.index]}`);
}
$('crew').onclick=()=>{const card=$('cast-card');card.hidden=!card.hidden;if(!card.hidden)focusCast(castSelect.value);else document.body.classList.remove('cast-focus');};
castSelect.onchange=()=>focusCast(castSelect.value);
function closeNavigation(){ $('scene-nav').hidden=true; $('open-nav').setAttribute('aria-expanded','false'); }
$('open-nav').onclick=()=>{if(!$('scene-nav').hidden){closeNavigation();return;}$('scene-nav').hidden=false;$('open-nav').setAttribute('aria-expanded','true');$('close-nav').focus();};
$('close-nav').onclick=()=>{closeNavigation();$('open-nav').focus();};
document.addEventListener('pointerdown',e=>{if(!$('scene-nav').hidden&&!$('scene-nav').contains(e.target)&&!$('open-nav').contains(e.target))closeNavigation();});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!$('scene-nav').hidden){e.preventDefault();e.stopImmediatePropagation();closeNavigation();$('open-nav').focus();}},true);
$('office-doors').onclick=()=>{const open=$('office-doors').getAttribute('aria-pressed')!=='true';$('office-doors').setAttribute('aria-pressed',String(open));officeDoors.forEach(d=>d.userData.open=open);};
$('walk-route').onclick=()=>{walkStarted=performance.now();setView('rooms');status('Pedestrian route: public walkway → near-side stairs → balcony. No entry into controlled storage.');};
function adjustLift(delta){if(state.running||state.mode!=='drive')return;forkHeight=T.MathUtils.clamp(forkHeight+delta,0,2.35);lift.position.y=forkHeight+(state.held?.3:0);if(state.held)delivery.position.y=.42+forkHeight;status(`Fork height: ${forkHeight.toFixed(2)} · Lower before driving.`);}
$('lift-up').onclick=()=>adjustLift(.1);$('lift-down').onclick=()=>adjustLift(-.1);
$('help').onclick=()=>$('instructions').showModal();$('close-help').onclick=()=>$('instructions').close();$('clean').onclick=()=>document.body.classList.toggle('clean');
window.addEventListener('keydown',e=>{if(['SELECT','INPUT','TEXTAREA'].includes(e.target.tagName)||$('instructions').open)return;const k=e.key.toLowerCase();if(['arrowup','arrowdown','arrowleft','arrowright',' '].includes(k))e.preventDefault();keys.add(k);if(e.repeat)return;if(k==='h')document.body.classList.toggle('clean');if(k==='r')reset();if(k==='q')adjustLift(.1);if(k==='z')adjustLift(-.1);if(k==='escape')setView('hero');if(k==='e'&&state.mode==='drive'&&!state.running)pickup();});
window.addEventListener('keyup',e=>keys.delete(e.key.toLowerCase()));window.addEventListener('blur',()=>keys.clear());
document.querySelectorAll('[data-key]').forEach(b=>{b.onpointerdown=e=>{b.setPointerCapture(e.pointerId);keys.add(b.dataset.key);};b.onpointerup=b.onpointercancel=()=>keys.delete(b.dataset.key);});$('touch-load').onclick=()=>{if(state.mode==='drive'&&!state.running)pickup();};
// Shared geometry handles the body, forks, carried load, rotation and dock edges.
function collisionOptions(){return {held:state.held,gateClosed:barrier.rotation.z>-.35,pallet:state.held?null:rectangle(delivery.position.x,delivery.position.z,.9,.8,delivery.rotation.y),obstacles:[...completedLoads.map(o=>rectangle(o.x,o.z,.9,.8,o.angle)),...castSlots.filter(s=>s.onFloor).map(s=>rectangle(s.actor.position.x,s.actor.position.z,.32,.32)),rectangle(receivingScene.receiver.g.position.x,receivingScene.receiver.g.position.z,.32,.32)]};}
function blocked(x,z,angle=fork.rotation.y){return blockedPose(x,z,angle,collisionOptions());}
let collisionNotice=false;
const clock=new T.Clock();
function animate(){requestAnimationFrame(animate);updateHeadlights(performance.now()/1000);const dt=Math.min(clock.getDelta(),.05);receivingScene.tick(state.paused?0:dt*state.speed);updateWorkActors(state.paused?0:dt*state.speed);state.t+=state.running?(state.paused?0:dt*state.speed):dt;for(const slot of castSlots)slot.mixer?.update(state.paused&&slot.onFloor?0:dt);for(const slot of castSlots)if(!slot.onFloor||slot.seated)slot.legs?.forEach(leg=>leg.rotation.x=-Math.PI/2);
 for(const slot of castSlots){if(slot.seated&&slot.id===meetingRun?.speaker&&!state.paused){const t=clock.elapsedTime;slot.arms?.forEach((arm,i)=>{arm.rotation.x=-.18-.12*Math.sin(t*2.8+i);arm.rotation.z=(i?1:-1)*(.04+.035*Math.sin(t*2));});}}
 for(const door of officeDoors)door.rotation.y=T.MathUtils.damp(door.rotation.y,door.userData.open?-Math.PI*.47:0,4,dt);
 if(walkStarted){const t=(performance.now()-walkStarted)/1000;const points=[[-9.6,.18,3],...stairApproach,...stairAscent.slice(1),[-11.2,4.3,9.4],[-11.2,4.3,3]];let duration=0;for(let i=0;i<points.length-1;i++){const a=new T.Vector3(...points[i]),b=new T.Vector3(...points[i+1]),d=a.distanceTo(b)/1.4;if(t>=duration&&t<duration+d){walkingGuide.position.lerpVectors(a,b,(t-duration)/d);walkingGuide.rotation.y=Math.atan2(b.x-a.x,b.z-a.z);break;}duration+=d;}if(t>duration){walkStarted=0;status('Pedestrian route complete: upper office balcony.');}}
 if(cameraTween){const a=cameraTween;a.t+=dt;const p=Math.min(1,a.t/1.3),q=p*p*(3-2*p);camera.position.lerpVectors(a.from,a.to,q);controls.target.lerpVectors(a.targetFrom,a.targetTo,q);if(p===1)cameraTween=null;}
 if(state.mode==='drive'&&!state.running){const turn=(keys.has('a')||keys.has('arrowleft')?1:0)-(keys.has('d')||keys.has('arrowright')?1:0);const speed=(keys.has('w')||keys.has('arrowup')?1:0)-(keys.has('s')||keys.has('arrowdown')?1:0);const next=movePose({x:fork.position.x,z:fork.position.z,angle:fork.rotation.y},(forkHeight>.4?0:speed)*dt*3.2,(forkHeight>.4?0:turn)*dt*1.5,collisionOptions());fork.position.x=next.x;fork.position.z=next.z;fork.rotation.y=next.angle;
 if(next.hit){status('Obstacle ahead. Reverse or change direction.','#d19a31');collisionNotice=true;}else if(collisionNotice&&(speed||turn)){status(state.held?'Load secured. Take it to the yellow zone; press E to set down.':'Use WASD / arrow keys to drive. E picks up or sets down the load.');collisionNotice=false;}
 const follow=new T.Vector3(0,5.5,8).applyAxisAngle(new T.Vector3(0,1,0),fork.rotation.y).add(fork.position);camera.position.lerp(follow,1-Math.exp(-dt*4));controls.target.copy(fork.position).add(new T.Vector3(0,1,0));camera.lookAt(controls.target);}
 if(state.running&&!state.paused){if(automation)stepCommands(dt*state.speed);else if(state.phase===3){beginInspection();}else if(state.phase===6){updateInspection(dt*state.speed);}else if(state.phase===7){updateReview(dt*state.speed);}else if(state.phase===8){updateDock();}else if(state.phase===9&&state.t>=5){deliveryNumber++;reset();status('Exercise saved in session history. Prepare the dock for the next delivery.');}}
 if(meetingRun?.speaker&&!$('speech').hidden){const slot=castSlots.find(s=>s.id===meetingRun.speaker);if(slot?.actor){const v=slot.actor.getWorldPosition(new T.Vector3()).add(new T.Vector3(0,3,0)).project(camera);$('speech').style.left=`${Math.max(document.body.classList.contains('conversation-open')&&innerWidth>550?(innerWidth<=900?420:460):140,Math.min(innerWidth-140,(v.x+1)*innerWidth/2))}px`;$('speech').style.top=`${Math.max(130,Math.min(innerHeight-160,(1-v.y)*innerHeight/2))}px`;}}
 barrier.rotation.z=T.MathUtils.damp(barrier.rotation.z,barrierTarget,4,dt);
 if(introActive)updateIntro();else if(state.mode!=='drive')controls.update();ceiling.visible=camera.position.y<10.8&&!(state.running||state.mode==='drive');overhead.visible=camera.position.y<10.8;renderer.render(scene,camera);
 document.body.classList.toggle('handling-active',state.running);document.body.dataset.ready='true';document.body.dataset.cameraMoving=String(!!cameraTween);document.body.dataset.result=state.result||'';document.body.dataset.phase=String(state.phase);document.body.dataset.fork=JSON.stringify([fork.position.x,fork.position.z]);
}
window.addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
window.__lego={scene,camera,controls,renderer,state,fork,delivery,zone,reset,pickup,runDemo,setView,blocked,get currentCase(){return currentCase;}};
if(camera.aspect<1.25)setView('hero');
resetReceiving();animate();progress(1);await pauseFrame();$('loading').remove();if(!matchMedia('(prefers-reduced-motion: reduce)').matches)startIntro();
