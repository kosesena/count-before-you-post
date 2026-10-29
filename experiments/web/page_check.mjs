// Check the demo page in headless Chrome: required ids, the four languages, console errors,
// sideways scroll at a width, and a screenshot of an element.
// Usage: node experiments/web/page_check.mjs <url> <width> <out.jpg> [selector-to-shoot]
import { spawn } from "node:child_process"; import { writeFileSync } from "node:fs";
const [url, w = "1440", out = "/tmp/page.jpg", sel = "#h-cast"] = process.argv.slice(2);
const port = 9600 + Math.floor(Math.random() * 300);
const chrome = spawn("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", ["--headless=new", `--remote-debugging-port=${port}`, "--hide-scrollbars", `--window-size=${w},900`, `--user-data-dir=/tmp/cbyp-pc-${port}`, "about:blank"], { stdio: "ignore" });
const sleep = ms => new Promise(r => setTimeout(r, ms)); let t;
for (let i = 0; i < 50 && !t; i++) { await sleep(200); try { t = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find(x => x.type === "page"); } catch {} }
const ws = new WebSocket(t.webSocketDebuggerUrl); await new Promise(r => ws.addEventListener("open", r));
let id = 0; const p = new Map(); const errors = [];
ws.addEventListener("message", e => { const m = JSON.parse(e.data);
  if (m.method === "Runtime.exceptionThrown") errors.push(m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text);
  if (m.method === "Runtime.consoleAPICalled" && m.params.type === "error") errors.push(m.params.args.map(a => a.value ?? a.description).join(" "));
  if (m.method === "Log.entryAdded" && m.params.entry.level === "error") errors.push(m.params.entry.text + " " + (m.params.entry.url || ""));
  p.get(m.id)?.(m); });
const send = (method, params = {}) => new Promise(r => { p.set(++id, r); ws.send(JSON.stringify({ id, method, params })); });
const ev = async x => (await send("Runtime.evaluate", { expression: x, returnByValue: true, awaitPromise: true })).result?.result?.value;
await send("Page.enable"); await send("Runtime.enable"); await send("Log.enable");
await send("Page.navigate", { url }); await sleep(4000);
const res = await ev(`(async () => {
  const ids = ['h-dock','h-cast','langSel','tabs','case','voice','dialogue','outside','secondTable','stats'];
  const r = { missing: ids.filter(i => !document.getElementById(i)), video: !!document.querySelector('video'),
              profileLinks: document.querySelectorAll('a[href*="character.html"]').length };
  const s = document.getElementById('langSel');
  for (const l of ['de','zh','tr','en']) { s.value = l; s.dispatchEvent(new Event('change', {bubbles:true})); await new Promise(z => setTimeout(z, 1200)); r[l] = document.querySelectorAll('#tabs .tab').length; }
  r.scroll = document.documentElement.scrollWidth + '/' + innerWidth;
  document.querySelectorAll('img').forEach(i => i.loading = 'eager');
  return r; })()`);
await sleep(2500);
const box = await ev(`(() => { const e = document.querySelector(${JSON.stringify(sel)}); if (!e) return null; const b = e.getBoundingClientRect(); return { x: 0, y: b.top + scrollY - 20, width: innerWidth, height: Math.min(3200, document.documentElement.scrollHeight - (b.top + scrollY - 20)) }; })()`);
if (box) { const s = await send("Page.captureScreenshot", { format: "jpeg", quality: 80, captureBeyondViewport: true, clip: { ...box, scale: w > 800 ? 0.5 : 1 } }); writeFileSync(out, Buffer.from(s.result.data, "base64")); }
console.log(JSON.stringify({ ...res, errors }));
ws.close(); chrome.kill();
