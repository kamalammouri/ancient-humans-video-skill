// Queue mode: submits prompts back to back without waiting for results (Flow runs them in parallel), then downloads every result.
//   node scripts/flow/qbatch.mjs prompts.json flow/<video>     Env: GAP (ms between submissions, 3000), WAIT (ms max after the last submission, 300000)
// Each fresh tile carries its full prompt as aria-label while loading; the node is tagged data-file at once, because Flow swaps
// the label for a short caption when the image lands. A file already present in the output folder is skipped.
// Measured 1 Nov 2026: 32 prompts at GAP 3000 all generated (about 4 min); a second lot of 36 right after got 4 to 6 "Échec" cards
// (unusual activity): keep lots to about 30 prompts and pause 30 min between lots. Tagging misses some tiles: the images ARE in
// the project, so finish with harvest.mjs (fresh output folder) and map the missing ones by caption.
import fs from 'node:fs';
import path from 'node:path';
import { attach, sleep, stamp } from './cdp.mjs';

const [src = 'prompts.json', out = 'flow/out'] = process.argv.slice(2);
const GAP = Number(process.env.GAP || 3000), WAIT = Number(process.env.WAIT || 300_000);
const prompts = JSON.parse(fs.readFileSync(src, 'utf8'));
fs.mkdirSync(out, { recursive: true });
const done = new Set(fs.readdirSync(out).map(f => f.replace(/\.(jpg|jpeg|png|webp)$/i, '')));
const uniq = (p) => { for (let i = 0; i + 80 <= p.length; i += 20) { const k = p.slice(i, i + 80); if (prompts.every(q => q.prompt === p || !q.prompt.includes(k))) return k; } return p; };  // first 80-char window no other prompt contains
const todo = prompts.filter(p => !done.has(p.file)).map(p => ({ file: p.file, prompt: p.prompt, key: uniq(p.prompt) }));
const keys = todo.map(({ file, key }) => ({ file, key }));
console.log(`${stamp()} ${prompts.length} prompts, to generate: ${todo.map(p => p.file).join(' ')}`);

const { page } = await attach(); page.setDefaultTimeout(15_000);
const root = page.url().replace(/\/collection\/.*$/, '');   // results go to the project itself, never inside a collection
if (root !== page.url()) { await page.goto(root, { waitUntil: 'domcontentloaded' }); await sleep(6000); }
const box = () => page.getByRole('textbox', { name: /Que voulez-vous créer|What do you want to create/i }).first();
const genButton = () => page.getByRole('button', { name: /^(Lancer la génération|Start generation)$/i }).first();
const failCount = () => page.locator('main [role="group"]').filter({ hasText: /Échec|Failed/ }).count();
const scrollTop = () => page.evaluate(() => { const c = document.querySelector('.cdk-virtual-scrollable'); if (c) c.scrollTop = 0; });
const tag = () => page.evaluate((pend) => {
  for (const g of document.querySelectorAll('main [role="group"]:not([data-file])')) {
    const t = (g.getAttribute('aria-label') || '') + ' ' + g.textContent;
    const hit = pend.find(p => t.includes(p.key)); if (hit) g.setAttribute('data-file', hit.file);
  }
  return document.querySelectorAll('main [data-file]').length;
}, keys);
const ready = () => page.evaluate(() => [...document.querySelectorAll('main [data-file]')].map(g => {
  const i = [...g.querySelectorAll('img')].find(x => x.naturalWidth >= 512); return i ? [g.getAttribute('data-file'), i.src] : null; }).filter(Boolean));
async function download(srcUrl, file) {
  const { b64, type } = await page.evaluate(async (u) => {
    const r = await fetch(u); const bytes = new Uint8Array(await r.arrayBuffer()); let s = '';
    for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
    return { b64: btoa(s), type: r.headers.get('content-type') || '' };
  }, srcUrl);
  const ext = /png/.test(type) ? 'png' : /webp/.test(type) ? 'webp' : 'jpg';
  const dst = path.join(out, `${file}.${ext}`); fs.writeFileSync(dst, Buffer.from(b64, 'base64')); return dst;
}
const got = new Set(), t0 = Date.now();
async function collect() { await scrollTop(); await tag(); for (const [file, u] of await ready()) if (!got.has(file)) { got.add(file); console.log(`${stamp()} ${file} ok -> ${await download(u, file)} (${Math.round((Date.now() - t0) / 1000)} s)`); } }

const trig = page.getByRole('button', { name: /Déclencheur des paramètres|Settings trigger/i }).first();
const label = (await trig.innerText().catch(() => '')).replace(/\s+/g, ' ');
if (!/x1/.test(label)) { await trig.click(); await sleep(800); for (const r of [/^Image$/, /^16:9$/, /^x1$/]) await page.getByRole('radio', { name: r }).first().click({ force: true }).catch(() => {}); await page.keyboard.press('Escape'); await sleep(500);
  console.log(`${stamp()} settings: "${label}" -> "${(await trig.innerText().catch(() => '')).replace(/\s+/g, ' ')}"`); }

const fails0 = await failCount();
for (const p of todo) {
  await box().click(); await page.keyboard.press('Control+A'); await page.keyboard.press('Delete'); await page.keyboard.insertText(p.prompt); await sleep(300);
  const g = genButton();
  if (await g.isDisabled().catch(() => true)) { console.log(`${stamp()} ${p.file} SKIP: generate button disabled`); continue; }
  await g.click(); await sleep(GAP);
  console.log(`${stamp()} ${p.file} sent (tiles tagged: ${await tag()})`);
  await collect();
}
const w0 = Date.now();
while (got.size < todo.length && Date.now() - w0 < WAIT) {
  await sleep(3000); await collect();
  const fails = await failCount() - fails0; if (fails && got.size + fails >= todo.length) break;
}
const missing = todo.filter(p => !got.has(p.file)).map(p => p.file), fails = await failCount() - fails0;
console.log(`${stamp()} done: ${got.size}/${todo.length} downloaded in ${Math.round((Date.now() - t0) / 1000)} s${fails ? `, ${fails} failure cards` : ''}${missing.length ? `, missing ${missing.join(' ')}` : ''}`);
process.exit(0);
