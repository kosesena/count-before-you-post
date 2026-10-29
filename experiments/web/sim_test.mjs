// Play every case of the simulator to its result card in headless Chrome, and check the gate
// shows the recorded decision. Usage: node experiments/web/sim_test.mjs [base_url] [out_dir]
// Uses the ?test hook: places the forklift in front of the pallet, picks it up, places it so
// the pallet lands in the middle of the yellow zone, sets it down. Driving itself is checked
// separately: holding the up arrow for a second must move the forklift.
import { spawn } from "node:child_process";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";

const base = process.argv[2] || "http://localhost:8766/sim/";
const outDir = process.argv[3] || "/tmp";
mkdirSync(outDir, { recursive: true });
const data = JSON.parse(readFileSync(new URL("../../site/data-en.json", import.meta.url)));
const port = 9700 + Math.floor(Math.random() * 200);
const chrome = spawn("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", [
  "--headless=new", `--remote-debugging-port=${port}`, "--use-angle=metal",
  "--enable-unsafe-swiftshader", "--hide-scrollbars", "--window-size=1600,900",
  `--user-data-dir=/tmp/cbyp-simtest-${port}`, "about:blank"], { stdio: "ignore" });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let target;
for (let i = 0; i < 50 && !target; i++) {
  await sleep(200);
  try { target = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find(t => t.type === "page"); } catch {}
}
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener("open", r));
let id = 0; const pending = new Map(); const errors = [];
ws.addEventListener("message", e => {
  const m = JSON.parse(e.data);
  if (m.method === "Runtime.exceptionThrown") errors.push(m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text);
  if (m.method === "Runtime.consoleAPICalled" && m.params.type === "error") errors.push(m.params.args.map(a => a.value ?? a.description).join(" "));
  pending.get(m.id)?.(m);
});
const send = (method, params = {}) => new Promise(r => { pending.set(++id, r); ws.send(JSON.stringify({ id, method, params })); });
const ev = async expr => {
  const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true });
  if (r.result?.exceptionDetails) throw new Error(r.result.exceptionDetails.exception?.description);
  return r.result?.result?.value;
};
const until = async (expr, ms = 30000) => { for (let t = 0; t < ms; t += 250) { if (await ev(`!!(${expr})`)) return true; await sleep(250); } return false; };
const key = async (code, type) => send("Input.dispatchKeyEvent", { type, code, key: code === "ArrowUp" ? "ArrowUp" : code, windowsVirtualKeyCode: code === "ArrowUp" ? 38 : 0 });

await send("Page.enable"); await send("Runtime.enable");
const rows = [];
for (const c of data.cases) {
  errors.length = 0;
  await send("Page.navigate", { url: base + "?test" });
  await until("window.__sim && window.stats && window.stats.loadMs");
  const clicked = await ev(`(() => { const b = [...document.querySelectorAll("button")].find(b => b.textContent.trim() === ${JSON.stringify(c.title)}); if (!b) return false; b.click(); return true; })()`);
  await ev(`document.getElementById("startBtn").click()`);
  await until(`window.__sim.G.pallet && window.__sim.G.pallet.y > 9`, 20000);
  // Driving: one second of the up arrow must move the forklift (after the first frames: the
  // forklift accelerates with inertia, and the first case also pays for the cold load).
  await sleep(1200);
  const y0 = await ev("window.__sim.G.fork.y");
  await key("ArrowUp", "keyDown"); await sleep(1000); await key("ArrowUp", "keyUp");
  const moved = Math.abs((await ev("window.__sim.G.fork.y")) - y0) > 0.2;
  // In front of the pallet, heading into the trailer (+y), at the hook's pick distance.
  await ev(`(() => { const S = window.__sim, F = S.G.fork, P = S.G.pallet, K = S.FORK || { pick: 1.8 }; F.x = P.x; F.y = P.y - K.pick; F.h = P.yaw || 0; F.v = 0; })()`);
  await sleep(300);
  const picked = await ev("window.__sim.pickup()");
  // Carry it so the pallet lands on the middle of the zone (set down FORK.set ahead).
  await ev(`(() => { const S = window.__sim, F = S.G.fork, K = S.FORK || { set: 1.19 }; F.x = 0; F.y = 5.5 - K.set; F.h = 0; F.v = 0; })()`);
  await sleep(500);
  await ev("window.__sim.drop()");
  const done = await until(`document.body.classList.contains("done")`, 30000);
  await sleep(1200);
  const text = await ev(`(document.getElementById("result") || document.querySelector(".result, [class*=result]") || document.body).innerText.slice(0, 600)`);
  const shot = await send("Page.captureScreenshot", { format: "png" });
  writeFileSync(`${outDir}/sim-${c.id}.png`, Buffer.from(shot.result.data, "base64"));
  const want = { post: /written to the ERP/i, block: /nothing written/i, human: /sent to Ş?ef|Şef/i }[c.gate.action];
  rows.push({ case: c.id, gate: c.gate.action, clicked, moved, picked, done, right: done && want.test(text), errors: [...errors] });
  console.log(JSON.stringify(rows.at(-1)));
}
console.log(rows.every(r => r.right && r.moved && r.picked && !r.errors.length) ? "ALL OK" : "PROBLEMS");
ws.close(); chrome.kill();
