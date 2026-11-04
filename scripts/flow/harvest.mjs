// Recovers images that Flow generated but batch.mjs did not download (timeouts, tiles renamed before detection).
//   node scripts/flow/harvest.mjs flow/<video>
// Switches the project view to "Images", scrolls the whole virtual list, downloads every image into <out>/harvest/H001.jpg…
// and writes <out>/harvest/inventory.json [{n, caption, img, file, known}] where `known` is the F-file of an identical image already
// in <out> (same bytes). Tiles are newest first and Flow replaces the prompt by a short caption, so the unknown ones are mapped by
// hand: build a contact sheet (python scripts/flow/harvest_sheet.py flow/<video>), read captions + pictures against prompts.json,
// then copy each H-file to <out>/<F-file>.jpg.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { attach, sleep, stamp } from './cdp.mjs';

const [out = 'flow/out'] = process.argv.slice(2);
const hdir = path.join(out, 'harvest'); fs.mkdirSync(hdir, { recursive: true });
const known = new Map(fs.readdirSync(out).filter(f => /^F\d+\.(jpg|png|webp)$/i.test(f)).map(f => [crypto.createHash('md5').update(fs.readFileSync(path.join(out, f))).digest('hex'), f.replace(/\.\w+$/, '')]));
const { browser, page } = await attach(); page.setDefaultTimeout(6000);
const tab = page.getByText(/^Images$/).first(); if (await tab.isVisible().catch(() => false)) { await tab.click(); await sleep(2500); }
const seen = new Map();
const collect = async () => { for (const r of await page.evaluate(() => [...document.querySelectorAll('[role="group"]')].map(g => { const img = [...g.querySelectorAll('img')].find(x => x.naturalWidth >= 512); return { caption: (g.getAttribute('aria-label') || '').slice(0, 120), img: img ? img.src : '' }; }))) if (r.img && !seen.has(r.img)) seen.set(r.img, r); };
const total = await page.evaluate(() => document.querySelector('.cdk-virtual-scrollable')?.scrollHeight || 0);
for (let y = 0; y <= total + 1000; y += 500) { await page.evaluate(yy => { const c = document.querySelector('.cdk-virtual-scrollable'); if (c) c.scrollTop = yy; }, y); await sleep(350); await collect(); }
await sleep(1500); await collect();
const list = [...seen.values()].map((r, i) => ({ n: i + 1, ...r }));
console.log(`${stamp()} ${list.length} images in the project`);
for (const r of list) {
  r.file = path.join(hdir, `H${String(r.n).padStart(3, '0')}.jpg`);
  if (!fs.existsSync(r.file)) {
    const b64 = await page.evaluate(async (u) => { const res = await fetch(u); const bytes = new Uint8Array(await res.arrayBuffer()); let s = ''; for (let k = 0; k < bytes.length; k += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(k, k + 0x8000)); return btoa(s); }, r.img);
    fs.writeFileSync(r.file, Buffer.from(b64, 'base64'));
  }
  r.known = known.get(crypto.createHash('md5').update(fs.readFileSync(r.file)).digest('hex')) || null;
}
fs.writeFileSync(path.join(hdir, 'inventory.json'), JSON.stringify(list, null, 1));
await page.evaluate(() => { const c = document.querySelector('.cdk-virtual-scrollable'); if (c) c.scrollTop = 0; });
const unknown = list.filter(r => !r.known);
console.log(`${stamp()} ${list.length - unknown.length} already in ${out}, ${unknown.length} to map by hand:`);
for (const r of unknown) console.log(`  H${String(r.n).padStart(3, '0')}  ${r.caption}`);
console.log(`inventory: ${path.join(hdir, 'inventory.json')} | sheet: python scripts/flow/harvest_sheet.py ${out}`);
await browser.close().catch(() => {}); process.exit(0);
