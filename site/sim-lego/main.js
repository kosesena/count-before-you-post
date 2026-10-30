import * as T from 'three';
import { blockedPose, movePose, rectangle } from './collision.mjs';
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
async function stage(text) { loadingText.textContent=text;stageAt=performance.now();await pauseFrame(); }
const C = {floor:0xc5c9cc,wall:0xd9dbd8,blue:0x0055bd,yellow:0xffcc00,orange:0xf47b13,navy:0x163360,teal:0x009e95,black:0x202326,red:0xc91a09,tan:0xd9b576,white:0xf4f3e9,pink:0xdc2485,purple:0x8553bf,green:0x438b40};
const scene = new T.Scene(); scene.background = new T.Color(0xe7e9df);
const renderer = new T.WebGLRenderer({antialias:true,alpha:false});
renderer.setPixelRatio(Math.min(devicePixelRatio,1.7)); renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = T.PCFSoftShadowMap;
renderer.toneMapping = T.ACESFilmicToneMapping; renderer.toneMappingExposure = .95;
$('world').appendChild(renderer.domElement);
const camera = new T.PerspectiveCamera(46,innerWidth/innerHeight,.15,180);
const controls = new OrbitControls(camera,renderer.domElement);
controls.enableDamping = true; controls.dampingFactor = .07; controls.maxPolarAngle = Math.PI*.485;
controls.minDistance = 3; controls.maxDistance = 64; controls.target.set(-1,3.5,-4);
camera.position.set(-1,6.5,21);
const pmrem = new T.PMREMGenerator(renderer);
const env = new RoomEnvironment(); const envTarget = pmrem.fromScene(env,.04);
scene.environment = envTarget.texture; scene.environmentIntensity = .48; env.dispose(); pmrem.dispose();
scene.add(new T.HemisphereLight(0xeaf5ff,0xa3906e,.8));
const sun = new T.DirectionalLight(0xffedcf,2.5); sun.position.set(18,22,8); sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048); Object.assign(sun.shadow.camera,{left:-27,right:27,top:24,bottom:-24,near:1,far:65});
sun.shadow.normalBias=.035; sun.shadow.bias=-.0001; scene.add(sun);
const fill = new T.DirectionalLight(0xd8e7ff,.6);fill.position.set(-14,12,12);scene.add(fill);
const matCache = new Map(), geoCache = new Map(), batches = new Map();
function mat(color,rough=.25){const k=color+':'+rough;if(!matCache.has(k))matCache.set(k,new T.MeshPhysicalMaterial({color,roughness:rough,metalness:0,clearcoat:.24,clearcoatRoughness:.16}));return matCache.get(k);}
const glass = new T.MeshPhysicalMaterial({color:0xd9f4fa,transparent:true,opacity:.12,roughness:.08,depthWrite:false,side:T.DoubleSide});
const glow = new T.MeshStandardMaterial({color:0xffe8a0,emissive:0xffce67,emissiveIntensity:2});
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
const world=group();
await stage('Building the warehouse…');
// Baseplate and tiled safety lanes.
box(world,0,-.22,-2,35,.4,37,0x9da6aa);
for(let x=-17;x<17;x+=2)for(let z=-20;z<16;z+=2)box(world,x+1,0,z+1,1.985,.12,1.985,C.floor);
for(let x=-16.8;x<17;x+=.4)for(let z=-19.8;z<16;z+=.4){if(Math.hypot(x+1,z-7)<4.4)continue;cyl(world,x,.11,z,.115,.08,C.floor,12);}
function stripe(x,z,w,d,col=C.yellow){box(world,x,.145,z,w,.065,d,col);}
stripe(-9,-2,.13,35);stripe(5,-2,.13,35);stripe(-2,-13,14,.13);stripe(10,7,9,.13);stripe(14,-1,.13,16);
// Studded brick walls; open front and open roof allow inspection from above.
for(let layer=0;layer<19;layer++){const yy=.32+layer*.48;for(let x=-17;x<17;x+=1.6){const xx=x+.8+(layer%2)*.8;if(xx>17)continue;box(world,xx,yy,-20,1.585,.465,.45,layer%7===0?0xc7cccb:C.wall,layer===18);}}
for(let layer=0;layer<16;layer++)for(let z=-20;z<16;z+=1.6){
 const lo=z+(layer%2)*.8,hi=Math.min(lo+1.6,16);
 const spans=layer<12?[[lo,Math.min(hi,-6.65)],[Math.max(lo,1.15),hi]]:[[lo,hi]];
 for(const [a,b] of spans)if(b-a>.025)box(world,17,.32+layer*.48,(a+b)/2,.45,.465,b-a-.015,C.wall,layer===15);
}
// Upper facade: alternating ribbed panels with brick joints, like the dock reference.
for(let z=-19.2;z<16;z+=1.6)box(world,17,9.25,z,.45,3.15,1.585,C.wall,true);
for(let x=-16;x<=16;x+=8){box(world,x,5.2,-19.65,.35,10.4,.6,0xb8bfbe);box(world,x,10.6,-2,.26,.35,36,0xb0b7b7,true);}
for(let z=-19;z<=15;z+=6)box(world,0,10.55,z,34,.35,.26,0xaeb6b8,true);
for(let x=-7;x<=11;x+=9)for(let z=-16;z<=14;z+=6){cyl(world,x,9.95,z,.035,1.05,C.black,8);const shade=new T.Mesh(new T.CylinderGeometry(.22,.65,.45,24),mat(C.black));shade.position.set(x,9.2,z);world.add(shade);cyl(world,x,8.98,z,.57,.045,glow,24);cyl(world,x,9.5,z,.15,.15,C.black,16);}
flush(world);
await stage('Placing the bricks…');
// Shelving sits flush to the perimeter; no islands in the central aisle.
const ceiling=group();
for(let z=-18;z<=14;z+=4)box(ceiling,0,10.9,z,34,.12,3.97,0xc7cbc4);for(let x=-15.8;x<17;x+=.8)for(let z=-19.2;z<16;z+=.8){
 piece(ceiling,geom('torus',.13,.028,12),mat(0x939b97),x,10.82,z,Math.PI/2);
}
flush(ceiling);ceiling.traverse(o=>{o.castShadow=false;});
const racks=group();
function rack(parent,x,z,ry,bays){const g=group(parent,x,0,z,ry);const step=2.8;for(let b=0;b<=bays;b++){const xx=(b-bays/2)*step;for(const zz of [-.7,.7]){for(let k=0;k<16;k++)box(g,xx,.25+k*.48,zz,.18,.465,.22,C.blue,k===15);box(g,xx,.16,zz,.45,.16,.45,C.blue);for(let k=0;k<14;k++)cyl(g,xx,.55+k*.48,zz+.115,.035,.012,0x063d79,8,Math.PI/2);}}
 for(let b=0;b<bays;b++){const xx=(b+.5-bays/2)*step;for(let lev=0;lev<4;lev++){const y=.5+lev*1.95;box(g,xx,y,.73,2.8,.18,.18,C.yellow,true);box(g,xx,y,-.73,2.8,.18,.18,C.yellow,true);box(g,xx,y,0,2.66,.12,1.38,0xb7bdc0);for(let c=0;c<3;c++){const h=.6+((b+lev+c)%3)*.12;crate(g,xx+(c-1)*.78,y+.12,0,.68,h,.84);if((b+lev+c)%3===0)crate(g,xx+(c-1)*.78,y+.12+h+.08,0,.55,.48,.65);}box(g,xx+.75,y,.84,.4,.09,.02,C.white);}}
 flush(g);return g;}
rack(racks,2.3,-18.7,0,9);rack(racks,16,-13.7,-Math.PI/2,4);rack(racks,16,5.7,-Math.PI/2,3);rack(racks,-16,-15.9,Math.PI/2,2);
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
const castSlots=[], castMixers=[];
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
const roomDefs=[['Spark',C.orange,0xd95c16],['Şef',C.blue,0x26231d],['Sam',0x369ce5,0x42352b],['Voice',0x2b62ca,0x252521],['Kapı',0x26589c,0x43302a],['Iris',C.pink,0xa91c81],['Ada',C.teal,0x171b20],['Glimmer',C.purple,0xc4a3df],['Wonder',0xe7b82a,0x784322],['Rover',0x287a6d,0x994422]];
await stage('Preparing the crew…');
for(let floor=0;floor<2;floor++)for(let n=0;n<5;n++){
 const [name,color,hair]=roomDefs[floor*5+n], room=group(offices,-14.1,.16+floor*3.85,9-n*4.35,Math.PI/2);
 box(room,0,.02,0,4.35,.22,5.4,0xc4c9c8,true);box(room,0,1.85,-2.5,4.35,3.6,.26,color);
 if(n===0||n===4)box(room,n===0?-2.175:2.175,1.85,0,.12,3.6,5.3,color,true);
 for(const xx of [-2.12,2.12]){box(room,xx,1.85,.04,.14,3.6,5.18,color,true);box(room,xx,1.85,2.58,.12,3.7,.15,C.black);}
 box(room,0,3.62,2.58,4.3,.22,.18,C.black);box(room,0,.14,2.58,4.3,.1,.18,C.black);box(room,0,1.85,2.58,.09,3.5,.12,C.black);
 const roomLight=new T.PointLight(0xffddb0,9,6,2);roomLight.position.set(0,3.1,.5);room.add(roomLight);
 const pane=new T.Mesh(new T.PlaneGeometry(4.05,3.35),glass);pane.position.set(0,1.85,2.6);room.add(pane);
 box(room,.77,1.4,2.67,.055,.36,.08,0xd7dadd);
 litName(room,name,color);
 // Light tiled floors, desk, monitor, keyboard, paperwork, bookcase.
 for(let xx=-1.8;xx<2;xx+=.6)for(let zz=-2;zz<2.4;zz+=.6)box(room,xx,.155,zz,.585,.04,.585,floor?0xdacdb3:0xe7e5dc,true);
 box(room,.1,1.2,.7,2.8,.14,1.25,0xc6ac83);for(const xx of [-1.1,1.3])for(const zz of [.22,1.15])box(room,xx,.68,zz,.1,1.05,.1,0x58636c);
 box(room,.65,1.66,.6,.85,.6,.09,C.black);box(room,.65,1.68,.545,.75,.47,.015,name==='Ada'?0x123e3d:0x3b5668);box(room,.65,1.34,.6,.08,.24,.1,C.black);box(room,.65,1.28,.7,.4,.045,.3,C.black);
 for(let k=0;k<4;k++)box(room,.65,1.8-k*.08,.53,.52-k*.08,.015,.012,name==='Ada'?0x67dba9:0xa7c5cb);
 box(room,.55,1.3,.25,.65,.04,.23,0xe1e4e0);sheet(room,-.65,1.3,1.0,.5,.55);cyl(room,-1,1.4,.45,.09,.24,C.white,16);
 box(room,1.65,1.45,-1.5,.5,2.7,1.55,0xc6ad7e);for(let lev=0;lev<3;lev++){box(room,1.32,.6+lev*.8,-1.5,.22,.08,1.5,0xf0d4a1);for(let b=0;b<5;b++)box(room,1.3,.87+lev*.8,-2.05+b*.25,.25,.48,.15,[C.blue,C.yellow,C.red,C.teal,C.white][(b+lev)%5]);}
 box(room,-.65,.5,-.85,.85,.13,.85,C.black);box(room,-.65,.32,-.85,.12,.35,.12,C.black);box(room,-.65,.93,-1.25,.85,.8,.12,C.black);
 plant(room,-1.65,.22,1.9);label(room,name==='Iris'?'✦':'01',-.8,2.45,-2.39,1.4,.85,'#faf4df','#617c87');
 if(name==='Iris'){for(let i=0;i<3;i++)label(room,['ART','COLOR','FORM'][i],-.9+i*.85,2.5,-2.38,.7,.9,['#ffc839','#fa9cb4','#6bb5c0'][i],'#ffffff');}
 if(floor===1){box(room,0,.2,3.1,4.35,.18,.9,0xa8b2b6,true);for(const xx of (n===4?[-2,-1,0,1]:[-2,-1,0,1,2]))box(room,xx,.85,3.5,.06,1.2,.06,C.black);box(room,n===4?-.55:0,1.45,3.5,n===4?3.2:4.3,.09,.1,C.black);box(room,n===4?-.55:0,.73,3.5,n===4?3.2:4.3,.055,.06,C.black);}
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
  const gltf=await castLoader.loadAsync(`../sim/models/${slot.id}.glb`);
  const root=gltf.scene, bounds=new T.Box3().setFromObject(root), size=bounds.getSize(new T.Vector3());
  const actor=group(slot.room,-.65,.21,-.85);
  root.position.set(-(bounds.min.x+bounds.max.x)/2,-bounds.min.y,-(bounds.min.z+bounds.max.z)/2);
  const scaled=new T.Group();scaled.scale.setScalar(2.24/size.y);scaled.add(root);actor.add(scaled);
  root.traverse(o=>{if(o.isMesh){o.castShadow=false;o.receiveShadow=true;}});
  slot.room.remove(slot.placeholder);slot.actor=actor;slot.loaded=true;
  slot.mixer=new T.AnimationMixer(root);castMixers.push(slot.mixer);
  // Keep the existing face design; full-resolution textures preserve its printed detail.
  root.traverse(o=>{if(o.isMesh)for(const material of (Array.isArray(o.material)?o.material:[o.material])){if(material.map)material.map.anisotropy=renderer.capabilities.getMaxAnisotropy();}});
  slot.legs=[root.getObjectByName('LegL'),root.getObjectByName('LegR')].filter(Boolean);
  if(slot.legs.length){
   actor.updateWorldMatrix(true,true);const hip=actor.worldToLocal(slot.legs[0].getWorldPosition(new T.Vector3()));
   actor.position.y=.66-hip.y;
   // Rest legs point down; negative local X turns them towards the desk (+Z).
   slot.legs.forEach(leg=>leg.rotation.x=-Math.PI/2);
  }
  const idle=gltf.animations.find(c=>c.name==='Idle');if(idle)slot.mixer.clipAction(idle).play();
  // Imported wave deforms the shoulders; keep the seated idle pose until the rig is repaired.
  slot.wave=null;
  castLoaded++;$('loading').querySelector('small').textContent=`CREW · ${castLoaded} / 10`;
 }catch(error){console.error(`Karakter yüklenemedi: ${slot.name}`,error);}
}));
draco.dispose();document.body.dataset.castLoaded=String(castLoaded);
// Stairs meet the far-end balcony at its opening, outside the working aisle.
const stairs=group(scene,OFFICE_WALL_SHIFT);
for(let i=0;i<14;i++){const x=-5.75-i*.37,top=.16+(i+1)*(4.14/14);box(stairs,x,top-.075,-10.05,.39,.15,1.25,0x7c878e,true);box(stairs,x,top-.26,-10.05,.08,.38,1.15,0x505c66);for(const z of [-10.65,-9.45]){box(stairs,x,top+.5,z,.055,1,.055,C.yellow);}}
// Continuous sloping handrails, cut from the same yellow LEGO beam family.
for(const z of [-10.65,-9.45]){const beam=new T.Mesh(geom('box',6.2,.09,.09),mat(C.yellow));beam.position.set(-8.15,3.38,z);beam.rotation.z=-Math.atan2(4.14,5.18);stairs.add(beam);}
box(stairs,-10.8,4.22,-10.05,.65,.16,1.25,0x7c878e,true);flush(stairs);
// Meeting island: navy disk, yellow segmented ring, orange tiled round tabletop.
const meeting=group(scene,-1,.15,7);
cyl(meeting,0,.08,0,4.35,.16,C.navy,96);cyl(meeting,0,.18,0,4.13,.08,C.yellow,96);cyl(meeting,0,.23,0,3.91,.08,C.navy,96);
for(let x=-3.8;x<=3.8;x+=.65)for(let z=-3.8;z<=3.8;z+=.65)if(Math.hypot(x,z)<3.55)box(meeting,x,.276,z,.636,.015,.636,C.navy);
for(let i=0;i<72;i++){const a=i*Math.PI*2/72;const p=group(meeting,Math.cos(a)*4.22,.22,Math.sin(a)*4.22,-a);box(p,0,0,0,.24,.065,.33,C.yellow);flush(p);}
cyl(meeting,0,.4,0,1,.27,C.black,48);for(let i=0;i<7;i++)cyl(meeting,0,.57+i*.19,0,.65,.18,C.black,32);cyl(meeting,0,1.94,0,2.55,.22,0xc9782e,96);cyl(meeting,0,2.055,0,2.5,.035,0xd68739,96);
// Fine tile seams on smooth round top; rows stop exactly at the circular edge.
for(let x=-2.4;x<=2.4;x+=.6){const len=Math.sqrt(2.48**2-x*x)*2;box(meeting,x,2.077,0,.012,.003,len,0xb96c2b);box(meeting,0,2.078,x,len,.003,.012,0xb96c2b);}
const stools=[[-2.85,-1.5,C.yellow],[2.85,-1.5,C.blue],[-1.95,2.5,C.teal],[1.95,2.5,C.orange]];
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
person(truck,.65,2.05,3.5,C.blue,0x31251d,false,.7);
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
 cyl(truck,side*1.13,2.04,5.1,.2,.12,glow,24,Math.PI/2);cyl(truck,side*1.38,1.92,5.02,.11,.1,C.orange,16,Math.PI/2);
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
for(const z of [-6,-4,-2]){cyl(yard,17.65,5.92,z,.13,.16,glow,16);}
for(let z=-19;z<16;z+=1.6){box(yard,17.5,10.65,z,1.1,.2,1.585,0x57636a,true);if(Math.round((z+19)/1.6)%3===0){cyl(yard,17.7,10.4,z,.15,.15,glow,16);}}
label(yard,'RECEIVING 01',17.48,5.65,-2.75,3.5,.35,'#20282b','#ffe393',Math.PI/2);
const dockSignal=group(yard,17.5,2,1.4,Math.PI/2);box(dockSignal,0,0,0,.45,1.2,.25,C.black);for(let i=0;i<3;i++)cyl(dockSignal,0,.35-i*.35,.15,.13,.07,[C.red,C.yellow,0x35bd43][i],16,Math.PI/2);flush(dockSignal);
person(yard,28,-1.05,-.25,C.orange,0x242521,false,1,1.1);person(yard,17.9,-1.05,2.4,0x72933d,0x242521,true,.9,1.1);flush(yard);
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
flush(fork);flush(lift);
// Delivery pallet and gate, beyond the meeting area.
const delivery=group(scene,18.1,.18,-4,Math.PI/2);pallet(delivery,0,0,0,1.8,1.6);flush(delivery);
let cartons=group(delivery);let currentCase='ok';
function buildLoad(){delivery.remove(cartons);cartons.traverse(o=>{if(o.isInstancedMesh)o.dispose();});batches.delete(cartons);cartons=group(delivery);const count=currentCase==='eksik'?11:12;for(let i=0;i<count;i++){const row=Math.floor(i/6),j=i%6;const x=(j%3-1)*.55,z=(Math.floor(j/3)-.5)*.72;crate(cartons,x,.36+row*.56,z,.51,.48,.64);if(currentCase==='wrong')box(cartons,x,.6+row*.56,z+.335,.25,.2,.02,C.yellow);if(currentCase==='hasarli'&&i===11){box(cartons,x,.91,z+.34,.32,.06,.02,C.red);box(cartons,x,.98,z+.34,.055,.25,.02,C.red);}}
 if(currentCase==='belirsiz'){cartons.children.length=0;batches.delete(cartons);for(let i=0;i<12;i++)crate(cartons,(i%2-.5)*.6,.36+Math.floor(i/4)*.56,(Math.floor(i/2)%2-.5)*.72,.54,.49,.64);}flush(cartons);}
buildLoad();
const zone={x:4,z:-5.5};const gate=group(scene,zone.x,.18,zone.z);
for(const z of [-1.6,1.6])box(gate,0,.03,z,4,.06,.12,C.yellow);for(const x of [-2,2])box(gate,x,.03,0,.12,.06,3.2,C.yellow);
box(gate,2.3,.75,-1.8,.5,1.5,.55,C.black,true);box(gate,2.3,1.6,-1.8,.45,.3,.5,C.yellow);
const barrier=group(gate,2.3,1.75,-1.8);box(barrier,-1.95,0,0,3.9,.2,.18,C.white);for(let k=0;k<6;k++)box(barrier,-.25-k*.65,0,.105,.3,.205,.02,C.red);flush(barrier);
box(gate,-2.4,1.4,-1.9,.14,2.8,.14,C.black);box(gate,-2.4,2.85,-1.9,.48,1.2,.35,C.black);
const signals=[];for(let i=0;i<3;i++){const material=new T.MeshStandardMaterial({color:[0xd62e1e,0xf9b722,0x40a34d][i],emissive:[0xd62e1e,0xf9b722,0x40a34d][i],emissiveIntensity:.06,roughness:.2});const light=new T.Mesh(new T.CylinderGeometry(.14,.14,.06,24),material);light.rotation.x=Math.PI/2;light.position.set(-2.4,3.2-i*.35,-1.69);gate.add(light);signals.push(light);}
box(gate,0,4.1,0,4.8,.18,.18,C.white,true);for(const x of [-2.4,2.4])box(gate,x,2.1,0,.14,4.2,.14,C.white);box(gate,0,3.9,0,.55,.35,.45,C.white);cyl(gate,0,3.68,.02,.12,.12,C.black,16);label(gate,'RECEIVING',0,4.4,.12,2.5,.4,'#ffcc00','#243238');flush(gate);
// A compact terminal and colored minifigure by the gate.
const terminal=group(scene,7,.2,-5.9);box(terminal,0,.85,0,.13,1.7,.13,C.black);box(terminal,0,1.85,0,1.1,.75,.15,C.black);label(terminal,'CHECK',0,1.86,.085,.95,.55,'#174c3b','#ddf7d9');flush(terminal);
person(scene,7.2,.2,-3.6,C.blue,0x2b2826,true,1,-.6);
// Small pallet jack, spare cartons and safety cones stay at the edges.
const props=group();for(const [x,z] of [[-4,-10.5],[14,9],[13,-8]]){pallet(props,x,.16,z);for(let i=0;i<3;i++)crate(props,x+(i-1)*.55,.52,z,.5,.6,.65);}
for(const [x,z] of [[6,-7.5],[6,-3.5],[-10,10]]){box(props,x,.2,z,.5,.12,.5,C.orange);const cone=new T.Mesh(new T.CylinderGeometry(.07,.2,.55,16),mat(C.orange));cone.position.set(x,.5,z);props.add(cone);cyl(props,x,.55,z,.12,.1,C.white,16);}flush(props);
await stage('Finishing the details…');
let caseData;
try{const res=await fetch('../data.json');if(!res.ok)throw Error('data');caseData=await res.json();}catch{caseData=null;}
const state={paused:false,speed:.5,mode:'orbit',held:false,running:false,phase:0,t:0,result:null};
const keys=new Set();let cameraTween=null;let barrierTarget=0;
const views={hero:{eye:[-1,6.5,21],target:[-1,3.5,-4]},table:{eye:[8,7,18],target:[-1,1.5,7]},rooms:{eye:[4,8,15],target:[-13,3.9,1]},dock:{eye:[10,8,8],target:[12,1,-4]},plan:{eye:[31,39,35],target:[6,0,0]},outside:{eye:[33,5.8,10],target:[22,2.7,-4]}};
// A live cinematic tour of this exact warehouse, with no external video.
let introActive=false,introStarted=0;
const introShots=[
 {view:'outside',title:'Every delivery starts here.',detail:'THE LOADING DOCK',offset:[-2,.4,1]},
 {view:'dock',title:'Count. Check. Verify.',detail:'THE RECEIVING FLOOR',offset:[-2,-.5,-1]},
 {view:'rooms',title:'Ten agents. One shared mission.',detail:'MEET THE CREW',offset:[-2,-.5,-1]},
 {view:'table',title:'Count Before You Post',detail:'META GLOBAL AI HACKATHON · PROJECT DEMO',offset:[-2,-.4,-1]}
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
function reset(){document.querySelector('.playback').hidden=true;state.paused=false;$('pause-demo').textContent='Pause';state.running=false;state.held=false;state.phase=0;state.result=null;state.mode='orbit';state.t=0;delivery.parent?.remove(delivery);scene.add(delivery);delivery.position.set(18.1,.18,-4);delivery.rotation.set(0,Math.PI/2,0);fork.position.set(18.2,.18,-.6);fork.rotation.y=-Math.PI/2;lift.position.y=0;barrierTarget=0;signals.forEach(s=>s.material.emissiveIntensity=.06);$('demo').disabled=false;$('case').disabled=false;status('Ready to explore.');setView('hero');}
function pickup(){if(state.held){const pos=new T.Vector3();delivery.getWorldPosition(pos);const heading=fork.rotation.y;scene.attach(delivery);delivery.position.y=.18;delivery.rotation.y=heading;lift.position.y=0;state.held=false;if(Math.hypot(pos.x-zone.x,pos.z-zone.z)<1.6){state.running=true;state.phase=3;state.t=0;$('demo').disabled=true;$('case').disabled=true;status('Sam is counting the cartons…');}else status('Pallet placed. Take it to the yellow inspection zone.');return true;}
 const front=new T.Vector3(0,0,-2.3).applyAxisAngle(new T.Vector3(0,1,0),fork.rotation.y).add(fork.position);if(front.distanceTo(delivery.position)>1.7){status('Move closer and align the forks under the pallet.','#d19a31');return false;}if(blockedPose(fork.position.x,fork.position.z,fork.rotation.y,{...collisionOptions(),held:true,pallet:null})){status('Not enough clearance for the load. Align the forklift.','#d19a31');return false;}fork.attach(delivery);delivery.position.set(0,.42,-2.25);delivery.rotation.set(0,0,0);lift.position.y=.3;state.held=true;status('Load secured. Take it to the yellow zone; press E to set down.');return true;}
const resultCopy={ok:'12 cartons verified. The receiving gate is open.',eksik:'11 cartons found; the note says 12. Delivery blocked.',wrong:'The product label does not match the note. Delivery blocked.',hasarli:'A carton is damaged. Supervisor review required.',talimat:'Injected instructions found in the note. Delivery blocked.',belirsiz:'Stacked cartons cannot be counted. Supervisor review required.'};
function finish(){const entry=caseData?.cases.find(c=>c.id===currentCase);if(!entry){status('Recorded verification data could not load. Result unavailable.','#bd4931');state.running=false;$('demo').disabled=false;$('case').disabled=false;return;}const action=entry.gate.action;state.result=action;signals.forEach((s,i)=>s.material.emissiveIntensity=i===({block:0,human:1,post:2}[action])?2.5:.06);barrierTarget=action==='post'?-Math.PI*.48:0;status(resultCopy[currentCase],{post:'#4e8e56',block:'#ca4d38',human:'#d19728'}[action]);state.running=false;$('demo').disabled=false;$('case').disabled=false;}
function runDemo(){reset();document.querySelector('.playback').hidden=false;setView('dock');state.running=true;state.phase=-2;state.t=0;$('demo').disabled=true;$('case').disabled=true;status('The forklift is moving from the dock to the loading point…');}
$('toggle-panel').onclick=()=>{const collapsed=$('panel').classList.toggle('collapsed');$('panel-controls').hidden=collapsed;$('toggle-panel').textContent=collapsed?'+':'−';$('toggle-panel').setAttribute('aria-expanded',String(!collapsed));$('toggle-panel').setAttribute('aria-label',collapsed?'Expand controls':'Minimize controls');};
$('pause-demo').onclick=()=>{state.paused=!state.paused;$('pause-demo').textContent=state.paused?'Resume':'Pause';};$('play-speed').onchange=()=>{state.speed=Number($('play-speed').value);};
$('demo').onclick=runDemo;$('case').onchange=()=>{currentCase=$('case').value;reset();buildLoad();};
$('drive').onclick=()=>{if(state.running)return;if(state.mode==='drive'){setView('hero');return;}cameraTween=null;state.mode='drive';controls.enabled=false;$('touch').hidden=false;$('drive').innerHTML='Exit driving <span>ESC</span>';status('Use WASD / arrow keys to drive. E picks up or sets down the load.');document.querySelectorAll('[data-view]').forEach(b=>b.classList.remove('active'));};
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
$('help').onclick=()=>$('instructions').showModal();$('close-help').onclick=()=>$('instructions').close();$('clean').onclick=()=>document.body.classList.toggle('clean');
window.addEventListener('keydown',e=>{if(['SELECT','INPUT','TEXTAREA'].includes(e.target.tagName)||$('instructions').open)return;const k=e.key.toLowerCase();if(['arrowup','arrowdown','arrowleft','arrowright',' '].includes(k))e.preventDefault();keys.add(k);if(e.repeat)return;if(k==='h')document.body.classList.toggle('clean');if(k==='r')reset();if(k==='escape')setView('hero');if(k==='e'&&state.mode==='drive'&&!state.running)pickup();});
window.addEventListener('keyup',e=>keys.delete(e.key.toLowerCase()));window.addEventListener('blur',()=>keys.clear());
document.querySelectorAll('[data-key]').forEach(b=>{b.onpointerdown=e=>{b.setPointerCapture(e.pointerId);keys.add(b.dataset.key);};b.onpointerup=b.onpointercancel=()=>keys.delete(b.dataset.key);});$('touch-load').onclick=()=>{if(state.mode==='drive'&&!state.running)pickup();};
// Shared geometry handles the body, forks, carried load, rotation and dock edges.
function collisionOptions(){return {held:state.held,gateClosed:barrier.rotation.z>-.35,pallet:state.held?null:rectangle(delivery.position.x,delivery.position.z,.9,.8,delivery.rotation.y)};}
function blocked(x,z,angle=fork.rotation.y){return blockedPose(x,z,angle,collisionOptions());}
let collisionNotice=false;
const clock=new T.Clock();
function animate(){requestAnimationFrame(animate);const dt=Math.min(clock.getDelta(),.05);state.t+=state.running?(state.paused?0:dt*state.speed):dt;for(const mixer of castMixers)mixer.update(dt);for(const slot of castSlots)slot.legs?.forEach(leg=>leg.rotation.x=-Math.PI/2);
 if(cameraTween){const a=cameraTween;a.t+=dt;const p=Math.min(1,a.t/1.3),q=p*p*(3-2*p);camera.position.lerpVectors(a.from,a.to,q);controls.target.lerpVectors(a.targetFrom,a.targetTo,q);if(p===1)cameraTween=null;}
 if(state.mode==='drive'&&!state.running){const turn=(keys.has('a')||keys.has('arrowleft')?1:0)-(keys.has('d')||keys.has('arrowright')?1:0);const speed=(keys.has('w')||keys.has('arrowup')?1:0)-(keys.has('s')||keys.has('arrowdown')?1:0);const next=movePose({x:fork.position.x,z:fork.position.z,angle:fork.rotation.y},speed*dt*3.2,turn*dt*1.5,collisionOptions());fork.position.x=next.x;fork.position.z=next.z;fork.rotation.y=next.angle;
 if(next.hit){status('Obstacle ahead. Reverse or change direction.','#d19a31');collisionNotice=true;}else if(collisionNotice&&(speed||turn)){status(state.held?'Load secured. Take it to the yellow zone; press E to set down.':'Use WASD / arrow keys to drive. E picks up or sets down the load.');collisionNotice=false;}
 const follow=new T.Vector3(0,5.5,8).applyAxisAngle(new T.Vector3(0,1,0),fork.rotation.y).add(fork.position);camera.position.lerp(follow,1-Math.exp(-dt*4));controls.target.copy(fork.position).add(new T.Vector3(0,1,0));camera.lookAt(controls.target);}
 if(state.running&&!state.paused){if(state.phase===-2){const p=Math.min(state.t/1.4,1);fork.position.set(T.MathUtils.lerp(18.2,15.85,p),.18,-.6);if(p===1){state.phase=-1;state.t=0;}}else if(state.phase===-1){const p=Math.min(state.t/1.8,1);fork.rotation.y=0;fork.position.z=T.MathUtils.lerp(-.6,-4,p);if(p===1){fork.rotation.y=-Math.PI/2;state.phase=0;state.t=0;status('The forklift is collecting the delivery…');}}else if(state.phase===0&&state.t>.8){pickup();state.phase=1;state.t=0;status('Moving the delivery to the inspection zone…');}else if(state.phase===1){const p=Math.min(state.t/3,1);fork.position.set(T.MathUtils.lerp(15.85,10,p),.18,-4);fork.rotation.y=-Math.PI/2;if(p===1){state.phase=2;state.t=0;}}else if(state.phase===2){
 // Pass around the operator and cones, then align before entering the inspection bay.
 const t=state.t;
 if(t<2){fork.position.set(10,.18,T.MathUtils.lerp(-4,1,t/2));}
 else if(t<4){fork.position.set(T.MathUtils.lerp(10,4,(t-2)/2),.18,1);}
 else if(t<5.5){fork.rotation.y=T.MathUtils.lerp(-Math.PI/2,0,(t-4)/1.5);}
 else {const p=Math.min((t-5.5)/2,1);fork.position.set(4,.18,T.MathUtils.lerp(1,-3.25,p));fork.rotation.y=0;if(p===1){pickup();state.phase=3;state.t=0;}}
 }else if(state.phase===3){if(state.t>3)status('Spark checks the note. Wonder verifies the evidence…');if(state.t>7)finish();}}
 barrier.rotation.z=T.MathUtils.damp(barrier.rotation.z,barrierTarget,4,dt);
 if(introActive)updateIntro();else if(state.mode!=='drive')controls.update();ceiling.visible=camera.position.y<10.8;renderer.render(scene,camera);
 document.body.dataset.ready='true';document.body.dataset.cameraMoving=String(!!cameraTween);document.body.dataset.result=state.result||'';document.body.dataset.phase=String(state.phase);document.body.dataset.fork=JSON.stringify([fork.position.x,fork.position.z]);
}
window.addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
window.__lego={scene,camera,controls,renderer,state,fork,delivery,zone,reset,pickup,runDemo,setView,blocked,get currentCase(){return currentCase;}};
if(camera.aspect<1.25)setView('hero');
animate();await pauseFrame();$('loading').remove();if(!matchMedia('(prefers-reduced-motion: reduce)').matches)startIntro();
