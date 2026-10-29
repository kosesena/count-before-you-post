// Screenshot a page in headless Chrome once it says it is ready.
// Usage: node experiments/web/shot.mjs <url> <out.png> [width] [height] [readyExpr]
// readyExpr is a JS expression the page must make true (default: both models loaded); then
// waits two more seconds for animation and the frame counter. Prints window.stats.
import { spawn } from "node:child_process";
import { writeFileSync } from "node:fs";

const [url, out, w = "1600", h = "900",
  ready = "window.stats && Object.keys(window.stats.load||{}).length >= 2"] = process.argv.slice(2);
const port = 9300 + Math.floor(Math.random() * 400);
const chrome = spawn("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", [
  "--headless=new", `--remote-debugging-port=${port}`, "--use-angle=metal",
  "--enable-unsafe-swiftshader", "--hide-scrollbars", `--window-size=${w},${h}`,
  `--user-data-dir=/tmp/cbyp-shot-${port}`, "about:blank"], { stdio: "ignore" });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let target;
for (let i = 0; i < 50 && !target; i++) {
  await sleep(200);
  try { target = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find(t => t.type === "page"); } catch {}
}
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener("open", r));
let id = 0; const pending = new Map();
ws.addEventListener("message", e => { const m = JSON.parse(e.data); pending.get(m.id)?.(m); });
const send = (method, params = {}) => new Promise(r => { pending.set(++id, r); ws.send(JSON.stringify({ id, method, params })); });
const evaluate = async expr => (await send("Runtime.evaluate", { expression: expr, returnByValue: true })).result?.result?.value;
await send("Page.enable");
await send("Page.navigate", { url });
for (let i = 0; i < 120 && !(await evaluate(`!!(${ready})`)); i++) await sleep(500);
await sleep(2000);
console.log(JSON.stringify(await evaluate("window.stats")));
const shot = await send("Page.captureScreenshot", { format: "png" });
writeFileSync(out, Buffer.from(shot.result.data, "base64"));
console.log("wrote", out);
ws.close(); chrome.kill();
