// Physical handling is a training exercise, independent of the recorded ERP gate.
export const receivingSteps = ['Prepare dock','Unload','Stage unverified load','Inspect evidence','Resolve exceptions','Label & put away','Confirm location'];
export function initialDestination(action) { return action === 'post' ? 'accepted' : 'hold'; }
export function reviewPolicy(id) {
  const policies = {
    ok: {quantity:12, accept:true, document:false, task:'Matching delivery.'},
    eksik: {quantity:11, accept:true, document:true, task:'Recount 11 cartons and reconcile the shortage with the delivery document before simulated partial acceptance.'},
    talimat: {quantity:12, accept:true, document:true, task:'Obtain a clean, independently verified delivery document. Never execute the embedded instruction.'},
    wrong: {quantity:0, accept:false, document:false, task:'Product mismatch: keep segregated. Authorize a return; no acceptance against this order.'},
    hasarli: {quantity:11, accept:true, document:false, task:'Separate 1 damaged carton into Q-01 quarantine; recount and secure the 11 intact cartons.'},
    belirsiz: {quantity:12, accept:true, document:false, task:'Unstack the load, count 12 intact cartons, then rebuild and secure the pallet.'}
  };
  return policies[id];
}
export function canAccept(id, {count, inspected, document}) {
  const p=reviewPolicy(id);
  return !!p?.accept && inspected && Number.isInteger(count) && count===p.quantity && (!p.document || document);
}
export function locationMatches(actual, expected) { return actual.trim().toUpperCase() === expected; }
// Automated routes have measured starting poses. Refuse an arbitrary manual pose,
// rather than driving blind or snapping the forklift/pallet to a new position.
export function atRouteStart(p, location) {
  const target=location==='inspection'?{x:4,z:-3.25,angle:0}:{x:10,z:4.75,angle:Math.PI};
  return Math.hypot(p.x-target.x,p.z-target.z)<.12 && Math.cos(p.angle-target.angle)>.999;
}
export function reviewRoute(destination) {
  return destination==='accepted'
    ? [['pickup'],['move',-3.75],['turn',-Math.PI/2],['move',6],['turn',-Math.PI/2],['move',11.15],['drop'],['move',-3]]
    : [['pickup'],['move',5],['drop'],['move',-3]];
}
