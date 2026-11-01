"""Play every Brick Dock scenario end to end like a user; log what the page says at each step.

Usage (site served on :8766, e.g. python3 -m http.server 8766 --directory site; needs Python
Playwright with Chromium):
  python experiments/web/brick_dock_walk.py <screenshot_dir> ok,wrong,eksik,talimat,hasarli,belirsiz
Each case: prepare the dock, play the delivery, read the decision card, move the load, recount
in H-01 when asked, confirm the location, release the dock. Expect every case to reach a
history line and no page errors.
"""
import sys, asyncio, json
from playwright.async_api import async_playwright

OUT = sys.argv[1]
CASES = sys.argv[2].split(',')
QTY = {"eksik": 11, "talimat": 12, "hasarli": 11, "belirsiz": 12}

STATE = """()=>{const v=id=>{const e=document.getElementById(id);return !!(e&&!e.hidden&&e.offsetParent!==null)};
 return {status:document.querySelector('#status span')?.textContent,
  match:v('match')?[...document.querySelectorAll('#match-rows li')].map(l=>l.innerText.replace(/\\n/g,' ')):null,
  transfer:v('transfer-load')?document.getElementById('transfer-load').textContent:null,
  review:v('review-controls')?document.getElementById('review-proposal').textContent:null,
  approveShown:v('review-approve'), docRow:v('review-document-row'),
  locate:v('location-confirm')?document.getElementById('location-prompt').textContent:null,
  next:v('next-delivery'), result:document.body.dataset.result}}"""
VISIBLE = "(id=>{const e=document.getElementById(id);return !!(e&&!e.hidden&&e.offsetParent!==null)})"


async def wait_for(pg, js, timeout=90, step=.3):
    t = 0
    while t < timeout:
        if await pg.evaluate(js):
            return True
        await asyncio.sleep(step)
        t += step
    return False


async def run(case):
    log = []
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-angle=metal", "--enable-gpu", "--ignore-gpu-blocklist"])
        pg = await b.new_page(viewport={"width": 1440, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(f"http://localhost:8766/sim-lego/?walk={case}", wait_until="load")
        await pg.wait_for_selector("#loading", state="detached", timeout=60000)
        await pg.keyboard.press("Escape"); await asyncio.sleep(.6)
        await pg.select_option("#case", case); await asyncio.sleep(.5)
        await pg.evaluate("()=>{const s=document.getElementById('play-speed');s.value='4';s.dispatchEvent(new Event('change'))}")
        await pg.click("#prepare-dock")
        await wait_for(pg, "!document.getElementById('demo').disabled && document.getElementById('prepare-dock').textContent.includes('prepared')", 40)
        log.append(("dock", await pg.evaluate("document.getElementById('dock-checks').textContent")))
        await pg.click("#demo")
        ok = await wait_for(pg, "document.body.dataset.result!==''", 180)
        await asyncio.sleep(1.2)
        log.append(("decision", await pg.evaluate(STATE)))
        await pg.screenshot(path=f"{OUT}/{case}-1-decision.jpg", quality=70)
        if not ok:
            log.append(("FAIL", "no decision"))
        await pg.click("#transfer-load")
        await wait_for(pg, f"{VISIBLE}('review-controls')||{VISIBLE}('location-confirm')||{VISIBLE}('next-delivery')", 150)
        await asyncio.sleep(1)
        st = await pg.evaluate(STATE)
        log.append(("after transfer", st))
        await pg.screenshot(path=f"{OUT}/{case}-2-placed.jpg", quality=70)
        if st["review"]:
            await pg.click("#review-inspect")
            await wait_for(pg, "document.getElementById('review-inspected').checked", 90)
            await asyncio.sleep(.5)
            log.append(("after recount", await pg.evaluate(STATE)))
            if st["approveShown"]:
                await pg.fill("#review-count", str(QTY.get(case, 12)))
                if st["docRow"]:
                    await pg.check("#review-document")
                await pg.click("#review-approve")
            else:
                await pg.click("#review-return")
            await wait_for(pg, f"{VISIBLE}('location-confirm')", 150)
            await asyncio.sleep(1)
            st = await pg.evaluate(STATE)
            log.append(("after review", st))
            await pg.screenshot(path=f"{OUT}/{case}-3-reviewed.jpg", quality=70)
        st = await pg.evaluate(STATE)
        if st["locate"]:
            addr = st["locate"].split('→')[1].split('.')[0].strip()
            await pg.fill("#location-code", addr)
            await pg.click("#confirm-location"); await asyncio.sleep(.8)
            log.append(("confirmed", await pg.evaluate(STATE)))
        st = await pg.evaluate(STATE)
        if st["next"]:
            await pg.click("#next-delivery"); await asyncio.sleep(2.5)
            log.append(("released", await pg.evaluate(STATE)))
            await pg.screenshot(path=f"{OUT}/{case}-4-released.jpg", quality=70)
            log.append(("history", await pg.evaluate("document.querySelector('#delivery-history li')?.textContent")))
        else:
            log.append(("FAIL", "next delivery never offered"))
        log.append(("page errors", errs))
        await b.close()
    return log


async def main():
    for c in CASES:
        for k, v in await run(c):
            print(c, "|", k, "|", json.dumps(v, ensure_ascii=False)[:700])
        print()

asyncio.run(main())
