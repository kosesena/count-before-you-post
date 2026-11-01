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
  // Receiving desk, handheld scanner, printer and paperwork tray.
  for(const [x,z,w] of [[-5,-4,2.8]]){
    box(equipment,x,1.35,z,w,.18,1.2,C.tan);for(const dx of [-1.2,1.2])for(const dz of [-.45,.45])box(equipment,x+dx,.75,z+dz,.1,1.2,.1,C.black);
  }
  hangingSign(['RECEIVING','DOCUMENTS'],-5,-4.5,3.2,'#174c3b');
  sheet(equipment,-5.8,1.48,-4,.5,.65);
  box(equipment,-4.4,1.7,-4,.8,.55,.6,C.white);box(equipment,-4.4,1.77,-3.68,.55,.07,.03,C.black);
  const printed=label(root,'PALLET / P-001',-4.4,1.56,-3.61,.65,.21,'#ffffff','#202326');
  const scanner=group(root,-5.3,1.55,-3.65);box(scanner,0,0,0,.15,.3,.15,C.black);box(scanner,0,.2,0,.32,.18,.3,C.teal);flush(scanner);
  // Recount and repack happen in H-01, so the sign hangs there (Sena, 1 Nov).
  hangingSign(['RECOUNT · REPACK','H-01'],10,7,3.4,'#174c3b',5.2);
  // Waste stations by the receiving desk, in bricks (written by hand, Claude Code): a wheelie bin
  // for stretch film and a roll cage for flattened cardboard. Each stays inside its old 0.8 m footprint.
  // Backed against the receiving partition behind the desk, out of the open floor (Sena, 1 Nov).
  const filmMat=new T.MeshStandardMaterial({color:0xf4f8ff,transparent:true,opacity:.55,roughness:.1,side:T.DoubleSide,depthWrite:false});
  const WASTE_Z=-6.75, DARK_BLUE=0x0b3f8a, TAPE=0xb07a3c, KRAFT=0xc9a46a;
  const wrapBin=group(equipment,-7.1,.18,WASTE_Z);
  box(wrapBin,0,.46,.02,.66,.74,.58,C.blue);                       // body
  box(wrapBin,0,.85,.02,.74,.06,.66,DARK_BLUE);                    // rim
  for(const x of [-.34,.34])box(wrapBin,x,.47,.02,.03,.62,.44,DARK_BLUE);   // side ribs
  box(wrapBin,0,.12,.02,.62,.08,.54,DARK_BLUE);                    // base
  box(wrapBin,0,.48,.32,.5,.05,.03,DARK_BLUE);                     // front lip
  box(wrapBin,0,.84,-.36,.6,.05,.05,C.black);                      // handle bar
  for(const x of [-.28,.28])box(wrapBin,x,.8,-.33,.05,.1,.06,C.black);
  cyl(wrapBin,0,.11,-.3,.025,.72,C.black,10,0,0,Math.PI/2);         // axle
  for(const x of [-.33,.33]){cyl(wrapBin,x,.11,-.3,.11,.07,C.black,18,0,0,Math.PI/2);cyl(wrapBin,x,.11,-.3,.05,.075,0x9aa3a8,12,0,0,Math.PI/2);}
  const lid=group(wrapBin,0,.88,-.32);box(lid,0,0,.34,.76,.05,.7,DARK_BLUE,true);lid.rotation.x=-1.9;flush(lid);
  // a liner bag over the rim and film crumpled above it
  const liner=new T.Mesh(new T.CylinderGeometry(.36,.33,.12,20,1,true),filmMat);liner.scale.set(1,1,.9);liner.position.set(0,.86,.02);wrapBin.add(liner);
  for(const [x,y,z,r,sy] of [[-.12,.93,.04,.2,.5],[.13,.95,-.04,.18,.6],[.02,1.02,.08,.16,.55],[-.05,.98,-.12,.14,.5]]){
    const puff=new T.Mesh(new T.IcosahedronGeometry(r,1),filmMat);puff.scale.set(1.2,sy,1);puff.position.set(x,y,z);puff.rotation.set(x*3,z*5,y);wrapBin.add(puff);}
  cyl(wrapBin,.2,1.04,.12,.05,.34,KRAFT,14,0,0,1.3);              // an empty film core on top
  flush(wrapBin);
  label(equipment,'STRETCH FILM',-7.1,.55,WASTE_Z+.33,.5,.12,'#ffffff','#0b3f8a');
  const cardCage=group(equipment,-5.8,.18,WASTE_Z);
  box(cardCage,0,.12,0,.74,.06,.7,0x2f8a3a);                       // deck
  for(const x of [-.34,.34])for(const z of [-.32,.32]){box(cardCage,x,.58,z,.05,.92,.05,C.green);
    cyl(cardCage,x*.9,.04,z*.9,.045,.04,C.black,12);box(cardCage,x*.9,.08,z*.9,.06,.04,.06,0x9aa3a8);}
  for(const y of [.32,.56,.8,1.02])for(const z of [-.32,.32])box(cardCage,0,y,z,.66,.025,.025,C.green);
  for(const y of [.32,.56,.8,1.02])box(cardCage,-.34,y,0,.025,.025,.6,C.green);
  for(let k=1;k<6;k++)box(cardCage,-.34+k*.113,.58,-.32,.018,.9,.018,C.green);       // back mesh
  for(let k=1;k<6;k++)box(cardCage,-.34,.58,-.32+k*.107,.018,.9,.018,C.green);       // side mesh
  for(let k=1;k<6;k++)box(cardCage,-.34+k*.113,.36,.32,.018,.46,.018,C.green);       // half front gate
  box(cardCage,0,.6,.32,.66,.03,.03,C.green);
  for(let k=1;k<6;k++)box(cardCage,.34,.58,-.32+k*.107,.018,.9,.018,C.green);        // open side mesh
  flush(cardCage);
  for(const [x,h,tilt,col] of [[-.22,.95,-.06,C.tan],[-.1,1.05,.05,KRAFT],[.03,.88,-.03,C.tan],[.15,1.0,.07,KRAFT],[.25,.82,-.05,C.tan]]){
    const sheet=group(cardCage,x,.15,0);box(sheet,0,h/2,0,.035,h,.56,col);box(sheet,.02,h*.62,0,.006,.05,.56,TAPE);flush(sheet);sheet.rotation.z=tilt;}
  const leaning=group(equipment,-6.32,.18,WASTE_Z);box(leaning,0,.33,0,.035,.66,.42,KRAFT);box(leaning,.02,.4,0,.006,.04,.42,TAPE);flush(leaning);leaning.rotation.z=.22;
  label(equipment,'CARDBOARD',-5.8,.8,WASTE_Z+.345,.6,.14,'#ffffff','#167443');
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
  const signal=new T.Mesh(new T.SphereGeometry(.18,12,8),new T.MeshStandardMaterial({color:C.red,emissive:C.red,emissiveIntensity:1.5}));signal.position.set(17.8,2.8,-1.1);signal.visible=false;root.add(signal);
  hangingSign(['DRIVER','WAIT FOR RELEASE'],18.4,-.9,3.1,'#243238',4.3,6.05,Math.PI/2);
  // Marked driver refuge on the ground-level yard, separated from the apron; the sign over the
  // door says it, so the floor frame carries no second sign (Sena, 1 Nov).
  for(const z of [3,5.4])box(equipment,20.8,-1.04,z,3,.06,.08,C.green);
  for(const x of [19.3,22.3])box(equipment,x,-1.04,4.2,.08,.06,2.4,C.green);
  box(equipment,20.8,-.55,5,.9,.6,.45,C.blue);
  const workLight=new T.Mesh(new T.CircleGeometry(.55,24),new T.MeshBasicMaterial({color:0x80eddd,transparent:true,opacity:.38,depthWrite:false}));workLight.rotation.x=-Math.PI/2;workLight.position.set(4,.2,-5.5);root.add(workLight);workLight.visible=false;
  // Briefing is a protected visitor area, not a required receiving operation.
  for(const z of [3,5,7,9,11])box(equipment,4,.85,z,.1,1.4,.1,C.teal);
  box(equipment,4,1.5,7,.1,.1,8,C.teal);box(equipment,4,.7,7,.1,.08,8,C.teal);
  hangingSign(['BRIEFING','PEDESTRIANS ONLY'],-1,7,3.2,'#167c70',7.1);   // over the meeting table's centre, high and narrow so it does not hide the offices (Sena, 1 Nov)
  flush(equipment);
  function worker(name,x,y,z,color){
    const g=group(root,x,y,z);box(g,0,1.15,0,.66,.65,.4,color);box(g,0,1.14,.22,.68,.09,.025,C.white);
    for(const dx of [-.23,.23])box(g,dx,1.15,.22,.07,.6,.025,C.white);
    cyl(g,0,1.75,0,.25,.4,0xffce44,20);cyl(g,0,2,0,.29,.15,C.yellow,20);
    // A minifigure face: two round eyes and a smile on the side the figure walks towards (Sena, 1 Nov).
    for(const ex of [-.085,.085])cyl(g,ex,1.8,.245,.035,.02,C.black,12,Math.PI/2);
    box(g,0,1.67,.247,.13,.022,.012,C.black);for(const ex of [-.075,.075])box(g,ex,1.685,.246,.03,.03,.012,C.black);
    const legs=[-.18,.18].map(x=>{const l=group(g,x,.8,0);box(l,0,-.32,0,.25,.64,.3,C.navy);flush(l);return l;});
    const arms=[-.43,.43].map(x=>{const a=group(g,x,1.4,0);box(a,0,-.25,0,.2,.55,.25,color);flush(a);return a;});
    if(name)twoSidedLabel(g,name,0,2.45,0,2.2,.3,'#243238','#ffffff');flush(g);return {g,legs,arms,home:new T.Vector3(x,y,z),route:[],task:'idle'};
  }
  const receiver=worker('RECEIVER',-5, .18,-2.7,C.orange);
  const driver=worker(null,20.8,-1.05,4.1,C.orange);
  const workers=[receiver,driver];let elapsed=0;
  return {
    receiver,driver,scanner,printed,
    prepare(){chocks.visible=true;bridge.visible=true;signal.material.color.setHex(C.red);signal.material.emissive.setHex(C.red);receiver.task='documents';},
    inspect(){receiver.route=[new T.Vector3(-2,.18,-2.7),new T.Vector3(1,.18,-4.5)];receiver.task='scan';workLight.visible=true;},
    repack(){receiver.route=[new T.Vector3(1,.18,-2),new T.Vector3(12,.18,-2),new T.Vector3(12,.18,4.5)];receiver.task='repack';},
    release(){signal.material.color.setHex(C.green);signal.material.emissive.setHex(C.green);bridge.visible=false;chocks.visible=false;
      // On the green signal the driver leaves the refuge and climbs into the cab (Sena, 1 Nov).
      driver.route=[new T.Vector3(23.6,-1.05,3.2),new T.Vector3(26.15,-1.05,-1.6),new T.Vector3(26.15,-.4,-2.2),new T.Vector3(26.15,.3,-2.6),new T.Vector3(26.15,1.43,-3.35),new T.Vector3(26.15,1.43,-4.65)];driver.task='board';},
    reset(){for(const w of workers){w.g.position.copy(w.home);w.route=[];w.task='idle';w.g.visible=true;}scanner.position.set(-5.3,1.55,-3.65);workLight.visible=false;bridge.visible=false;chocks.visible=false;signal.material.color.setHex(C.red);signal.material.emissive.setHex(C.red);},
    tick(dt){elapsed+=dt;for(const w of workers){if(w.task==='seated')continue;const next=w.route[0];if(!next&&w.task==='board'){w.task='seated';w.legs.forEach(l=>l.rotation.x=-Math.PI/2);continue;}if(next){const d=w.g.position.distanceTo(next),step=dt*(w.task==='board'?.9:2);w.g.lookAt(next.x,w.g.position.y,next.z);if(d<=step){w.g.position.copy(next);w.route.shift();}else w.g.position.addScaledVector(next.clone().sub(w.g.position).normalize(),step);w.legs.forEach((l,i)=>l.rotation.x=Math.sin(elapsed*7+i*Math.PI)*.35);}else{w.legs.forEach(l=>l.rotation.x=0);w.arms.forEach((a,i)=>a.rotation.x=w.task==='idle'?0:-.5+Math.sin(elapsed*3+i)*.1);}}
      if(receiver.task==='scan'||receiver.task==='repack'){scanner.position.copy(receiver.g.position).add(new T.Vector3(.45,1.3,.1));receiver.g.lookAt(receiver.task==='scan'?4:10,.18,receiver.task==='scan'?-5.5:7);}workLight.material.opacity=.25+.13*Math.sin(elapsed*3);
    }
  };
}
