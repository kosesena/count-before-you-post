'use strict';
const $ = id => document.getElementById(id);
const ids = ['ok', 'eksik', 'belirsiz'];
const titles = ['Matching delivery', 'One carton missing', 'The camera cannot settle it'];
let data, selected = 'ok', view = 'camera', request = 0;
const parse = value => typeof value === 'string' ? JSON.parse(value) : value;
function image(id, path) {
  $(id).src = '../' + path;
  $(id + '-link').href = '../' + path;
}
function render() {
  const c = data.cases.find(c => c.id === selected);
  if (!c) throw Error('Missing recorded delivery');
  const index = ids.indexOf(selected), gate = c.gate;
  $('step').textContent = `DECISION ${index + 1} OF 3`;
  $('case-title').textContent = titles[index];
  $('next').textContent = index === 2 ? 'Back to acceptance ↺' : 'Next decision →';
  document.querySelectorAll('[data-case]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.case === selected)));
  document.querySelectorAll('[data-view]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.view === view)));
  $('claim').textContent = c.note.items.map(i => `${i.quantity} ${i.unit}`).join(' · ');
  $('product').textContent = c.note.items.map(i => i.description).join(' · ');
  $('count').textContent = `${c.spark.cartons_visible} seen by Spark · ${c.sam.sure} sure for SAM`;
  image('note', c.images.note);
  image('camera', c.images[view]);
  $('camera').alt = `${titles[index]} — recorded ${view === 'cross' ? 'SAM and Spark object matching' : view}`;
  const cross = c.cross;
  $('cross').textContent = cross ? `${cross.agreed} matched objects · ${cross.sam_only} SAM only · ${cross.spark_only} Spark only` : 'No object-match result recorded.';
  $('cross-detail').textContent = EvidenceStatus.cross(c);
  $('decision').dataset.action = gate.action;
  $('verdict').textContent = {post:'APPROVE · dry run',block:'BLOCK · no receipt',human:'ASK A PERSON · no automatic receipt'}[gate.action];
  $('reason').textContent = gate.reason;
  const attempts = c.agent.steps.filter(s => s.tool === 'post_goods_receipt');
  const latest = attempts.at(-1);
  if (latest) {
    const result = parse(latest.result), args = parse(latest.args);
    $('transaction').textContent = result.posted
      ? result.document ? `ERP receipt ${result.document} · ${result.quantity} cartons.` : `Approved ${result.quantity} cartons. document: null — no ERP write.`
      : `The agent requested ${args.quantity} cartons. The write was refused.`;
  } else {
    $('transaction').textContent = c.agent.supervisor ? 'The agent asked the supervisor without a write attempt.' : 'No write attempt appears in this recording.';
  }
  $('recorded-at').textContent = `${latest?.at ? 'Recorded ' + latest.at + '. ' : ''}Historical core profile; not a new verification.`;
  $('trace').textContent = JSON.stringify(c.agent.steps, null, 2);
  $('case').hidden = false;
}
async function load() {
  const token = ++request;
  $('case').hidden = true;
  $('status').textContent = 'Loading recorded evidence…';
  document.querySelectorAll('[data-case]').forEach(b => b.disabled = true);
  try {
    const lang = $('language').value;
    const response = await fetch(lang === 'tr' ? '../data.json' : `../data-${lang}.json`);
    if (!response.ok) throw Error('Unavailable recording');
    const next = await response.json();
    if (token !== request) return;
    data = next;
    render();
    $('status').textContent = '';
    document.querySelectorAll('[data-case]').forEach(b => b.disabled = false);
  } catch (error) {
    if (token !== request) return;
    $('case').hidden = true;
    $('status').textContent = 'This recording could not be loaded. Choose another language or reload the page.';
  }
}
document.querySelectorAll('[data-case]').forEach(b => b.addEventListener('click', () => {selected = b.dataset.case; render();}));
document.querySelectorAll('[data-view]').forEach(b => b.addEventListener('click', () => {view = b.dataset.view; render();}));
$('next').addEventListener('click', () => {selected = ids[(ids.indexOf(selected) + 1) % ids.length]; render();});
$('language').addEventListener('change', load);
load();

// Keep the real-photo controls independent of the historical language selector.
let realControls, realSelected = 'correct';
function renderReal() {
  const row = realControls.rows.find(row => row.id === realSelected);
  const e = row.evidence, item = e.note.items[0];
  document.querySelectorAll('[data-real]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.real === realSelected)));
  $('real-claim').textContent = `${item.quantity} ${item.quantity === 1 ? 'carton' : 'cartons'} · ${item.product_identity.product_code}`;
  image('real-note', `img/validation/area-${row.id}-note.png`);
  image('real-camera', realControls.selected_image);
  $('real-original').href = '../' + realControls.original_image;
  const order = e.decision.evidence.order;
  $('real-order').textContent = `${order.number}: ${order.open} open · expected article ${e.decision.evidence.product_identity.expected.product_code}`;
  $('real-count').textContent = `${e.camera.cartons_visible} carton · camera reads ${e.camera.product_identity.product_code}`;
  $('real-decision').dataset.action = e.decision.action;
  $('real-verdict').textContent = {post: 'APPROVE · dry run', block: 'BLOCK · no receipt', human: 'ASK A PERSON'}[e.decision.action];
  $('real-reason').textContent = e.decision.reasons.join(' ');
  $('real-result').textContent = `${e.result.posted ? `Approved ${e.result.quantity} carton; document: null.` : 'Receipt refused.'} No ERP write. ${row.seconds.toFixed(1)} s recorded elapsed time.`;
  $('real-checks').textContent = e.second_opinions?.audit?.ok
    ? 'Second note reader and pre-write audit completed. Synthetic receiver count: ' + e.receiver.quantity + '.'
    : 'Stopped before second-reader and audit checks; those checks are not credited to this result.';
  $('real-trace').textContent = JSON.stringify(row, null, 2);
  $('real-case').hidden = false;
}
async function loadReal() {
  try {
    const response = await fetch('../validation.json');
    if (!response.ok) throw Error('Unavailable controls');
    realControls = (await response.json()).counting_area_controls;
    renderReal();
    $('real-status').textContent = '';
    document.querySelectorAll('[data-real]').forEach(b => b.disabled = false);
  } catch (error) {
    $('real-case').hidden = true;
    $('real-status').textContent = 'Real-photo evidence could not be loaded. Reload or open the full development evidence below.';
  }
}
document.querySelectorAll('[data-real]').forEach(b => b.addEventListener('click', () => {realSelected = b.dataset.real; renderReal();}));
loadReal();
