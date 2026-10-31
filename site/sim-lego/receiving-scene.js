// Brick equipment stays outside the forklift routes; solids are shared with collision.mjs.
export function buildReceivingScene({T,scene,group,box,cyl,label,twoSidedLabel,flush,sheet,C}) {
  const root=group(scene), equipment=group(root);
  // Separate outward-facing surfaces keep the reverse face readable, never mirrored.
  function hangingSign(lines,x,z,w=3.5,color='#167c70',y=4.5,roof=10.55,rotation=0){
    const sign=group(root,x,y,z,rotation),h=1.05,depth=.22;
    sign.name='Hanging sign: '+lines.join(' / ');
    box(sign,0,0,0,w,h,depth,C.black);
    for(const face of [1,-1]){
      const panel=group(sign,0,0,face*(depth/2+.008),face===1?0:Math.PI);
      const background=label(panel,'',0,0,0,w-.12,h-.12,color,'#ffffff');background.material.side=T.FrontSide;
      lines.forEach((text,i)=>{
        const textFace=label(panel,text,0,lines.length===1?0:.21-i*.42,.006,w-.32,lines.length===1?.6:.38,color,'#ffffff');
        textFace.material.side=T.FrontSide;textFace.material.toneMapped=false;
      });
    }
    const top=h/2,length=roof-y-top;
    for(const x of [-w*.36,w*.36]){
      cyl(sign,x,top+length/2,0,.026,length,0x58656b,8);
      box(sign,x,roof-y,0,.24,.1,.42,C.black);
      cyl(sign,x,top+.035,0,.065,.09,0xadb9bc,12);
    }
    box(sign,0,roof-y+.07,0,w+.35,.12,.18,0x8e999c);
    flush(sign);return sign;
  }
  const floorTag=(text,x,z,w=3,color='#167c70')=>{const p=label(equipment,text,x,.24,z,w,.48,color,'#ffffff');p.rotation.x=-Math.PI/2;};
  // Receiving desk, handheld scanner, printer, paperwork tray and recount bench.
  for(const [x,z,w] of [[-5,-4,2.8],[-5,-.8,2.8]]){
    box(equipment,x,1.35,z,w,.18,1.2,C.tan);for(const dx of [-1.2,1.2])for(const dz of [-.45,.45])box(equipment,x+dx,.75,z+dz,.1,1.2,.1,C.black);
  }
  hangingSign(['RECEIVING','DOCUMENTS'],-5,-4.5,3.2,'#174c3b');
  sheet(equipment,-5.8,1.48,-4,.5,.65);
  box(equipment,-4.4,1.7,-4,.8,.55,.6,C.white);box(equipment,-4.4,1.77,-3.68,.55,.07,.03,C.black);
  const printed=label(root,'PALLET / P-001',-4.4,1.56,-3.61,.65,.21,'#ffffff','#202326');
  const scanner=group(root,-5.3,1.55,-3.65);box(scanner,0,0,0,.15,.3,.15,C.black);box(scanner,0,.2,0,.32,.18,.3,C.teal);flush(scanner);
  hangingSign(['RECOUNT','REPACK'],-5,-1.3,3.2,'#174c3b');
  for(const x of [-5.8,-5.3])cyl(equipment,x,1.65,-.8,.15,.5,C.white,16);
  // Hand pallet truck, parked with forks down in its own marked pocket.
  const jack=group(equipment,-7.3,.2,-5.1);
  for(const x of [-.34,.34]){box(jack,x,.18,.3,.22,.16,1.8,C.yellow);cyl(jack,x,.12,.95,.12,.16,C.black,16,0,0,Math.PI/2);}
  box(jack,0,.3,-.55,.9,.32,.5,C.yellow);box(jack,0,.9,-.65,.08,1.2,.08,C.black);
  box(jack,0,1.52,-.65,.55,.08,.08,C.black);flush(jack);floorTag('PALLET TRUCK',-7.2,-3.7,2);
  for(const [x,name,color] of [[-7.1,'WRAP',C.blue],[-5.8,'CARDBOARD',C.green]]){box(equipment,x,.6,1.1,.8,.85,.8,color);label(equipment,name,x,1.15,1.52,.8,.22,'#243238','#ffffff');}
  // Quarantine is physically distinct from authorized returns.
  for(const z of [5.6,8.4])box(equipment,13,.23,z,2.8,.06,.08,C.orange);
  for(const x of [11.6,14.4])box(equipment,x,.23,7,.08,.06,2.8,C.orange);
  hangingSign(['Q-01','QUARANTINE'],13,8.4,3.2,'#a96020');
  floorTag('Q-01 · DO NOT USE',13,8.8,2.7,'#a96020');
  // First aid, extinguisher and an exit door beside the protected pedestrian route.
  box(equipment,-16.7,1.7,12,.12,.9,.8,C.green);label(equipment,'FIRST AID +',-16.58,2.4,12,1.7,.3,'#167443','#ffffff',Math.PI/2);
  cyl(equipment,-16.3,.8,13.3,.19,1.1,C.red,20);box(equipment,-16.3,1.45,13.3,.25,.12,.15,C.black);
  label(equipment,'FIRE',-16.3,2.1,13.3,1,.3,'#bc301d','#ffffff',Math.PI/2);
  box(equipment,-16.75,1.6,14.6,.12,3,1.5,C.green);box(equipment,-16.64,1.5,14.6,.08,.08,1.1,C.white);
  label(equipment,'EXIT →',-16.55,3.4,14.6,1.8,.4,'#167443','#ffffff',Math.PI/2);
  // A bridging plate spans the dock/trailer interface. The red external signal
  // remains red while the receiving team works; green is only shown after release.
  const bridge=group(root,17.5,.22,-4);box(bridge,0,0,0,1.25,.1,2.6,0x6b7c81);for(const z of [-1.2,1.2])box(bridge,0,.07,z,1.25,.025,.08,C.yellow);flush(bridge);bridge.visible=false;
  const chocks=group(root);for(const x of [19.8,20.4])box(chocks,x,-.8,-5.68,.35,.35,.42,C.yellow);flush(chocks);chocks.visible=false;
  const signal=new T.Mesh(new T.SphereGeometry(.18,12,8),new T.MeshStandardMaterial({color:C.red,emissive:C.red,emissiveIntensity:1.5}));signal.position.set(17.8,2.8,-1.1);root.add(signal);
  hangingSign(['DRIVER','WAIT FOR RELEASE'],18.4,-.9,3.1,'#243238',4.3,6.05,Math.PI/2);
  // Marked driver refuge on the ground-level yard, separated from the apron.
  for(const z of [3,5.4])box(equipment,20.8,-1.04,z,3,.06,.08,C.green);
  for(const x of [19.3,22.3])box(equipment,x,-1.04,4.2,.08,.06,2.4,C.green);
  twoSidedLabel(equipment,'DRIVER WAITING',20.8,1.7,5.35,3,.35,'#167443','#ffffff');
  box(equipment,20.8,-.55,5,.9,.6,.45,C.blue);
  const workLight=new T.Mesh(new T.CircleGeometry(.55,24),new T.MeshBasicMaterial({color:0x80eddd,transparent:true,opacity:.38,depthWrite:false}));workLight.rotation.x=-Math.PI/2;workLight.position.set(4,.2,-5.5);root.add(workLight);workLight.visible=false;
  // Briefing is a protected visitor area, not a required receiving operation.
  for(const z of [3,5,7,9,11])box(equipment,4,.85,z,.1,1.4,.1,C.teal);
  box(equipment,4,1.5,7,.1,.1,8,C.teal);box(equipment,4,.7,7,.1,.08,8,C.teal);
  hangingSign(['BRIEFING','PEDESTRIANS ONLY'],0,11.4,4.2,'#167c70');
  flush(equipment);
  function worker(name,x,y,z,color){
    const g=group(root,x,y,z);box(g,0,1.15,0,.66,.65,.4,color);box(g,0,1.14,.22,.68,.09,.025,C.white);
    for(const dx of [-.23,.23])box(g,dx,1.15,.22,.07,.6,.025,C.white);
    cyl(g,0,1.75,0,.25,.4,0xffce44,20);cyl(g,0,2,0,.29,.15,C.yellow,20);
    const legs=[-.18,.18].map(x=>{const l=group(g,x,.8,0);box(l,0,-.32,0,.25,.64,.3,C.navy);flush(l);return l;});
    const arms=[-.43,.43].map(x=>{const a=group(g,x,1.4,0);box(a,0,-.25,0,.2,.55,.25,color);flush(a);return a;});
    twoSidedLabel(g,name,0,2.45,0,2.2,.3,'#243238','#ffffff');flush(g);return {g,legs,arms,home:new T.Vector3(x,y,z),route:[],task:'idle'};
  }
  const receiver=worker('RECEIVER',-5, .18,-2.7,C.orange);
  const driver=worker('DRIVER',20.8,-1.05,4.1,C.orange);
  const workers=[receiver,driver];let elapsed=0;
  return {
    receiver,driver,scanner,printed,
    prepare(){chocks.visible=true;bridge.visible=true;signal.material.color.setHex(C.red);signal.material.emissive.setHex(C.red);receiver.task='documents';},
    inspect(){receiver.route=[new T.Vector3(-2,.18,-2.7),new T.Vector3(1,.18,-4.5)];receiver.task='scan';workLight.visible=true;},
    repack(){receiver.route=[new T.Vector3(1,.18,-2),new T.Vector3(12,.18,-2),new T.Vector3(12,.18,4.5)];receiver.task='repack';},
    release(){signal.material.color.setHex(C.green);signal.material.emissive.setHex(C.green);bridge.visible=false;chocks.visible=false;},
    reset(){for(const w of workers){w.g.position.copy(w.home);w.route=[];w.task='idle';}scanner.position.set(-5.3,1.55,-3.65);workLight.visible=false;bridge.visible=false;chocks.visible=false;signal.material.color.setHex(C.red);signal.material.emissive.setHex(C.red);},
    tick(dt){elapsed+=dt;for(const w of workers){const next=w.route[0];if(next){const d=w.g.position.distanceTo(next),step=dt*2;w.g.lookAt(next.x,w.g.position.y,next.z);if(d<=step){w.g.position.copy(next);w.route.shift();}else w.g.position.addScaledVector(next.clone().sub(w.g.position).normalize(),step);w.legs.forEach((l,i)=>l.rotation.x=Math.sin(elapsed*7+i*Math.PI)*.35);}else{w.legs.forEach(l=>l.rotation.x=0);w.arms.forEach((a,i)=>a.rotation.x=w.task==='idle'?0:-.5+Math.sin(elapsed*3+i)*.1);}}
      if(receiver.task==='scan'||receiver.task==='repack'){scanner.position.copy(receiver.g.position).add(new T.Vector3(.45,1.3,.1));receiver.g.lookAt(receiver.task==='scan'?4:10,.18,receiver.task==='scan'?-5.5:7);}workLight.material.opacity=.25+.13*Math.sin(elapsed*3);
    }
  };
}
