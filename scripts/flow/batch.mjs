// Pastes every prompt of prompts.json into Google Flow (direct image mode), waits for the result tile, downloads it. Resumable.
//   PACE=45000 node scripts/flow/batch.mjs prompts.json flow/<video>
// prompts.json = [{"file": "F001", "prompt": "..."}, ...]. A file already present in the output folder is skipped.
// Env: PACE (ms pause after each image, 45000 keeps under Flow's "unusual activity" detector; 12000 got blocked after ~30 images),
//      WAIT (ms max per image, 150000), MAXFAIL (consecutive failure cards before the run stops, 3; 99 = keep retrying all evening). Output: <out>/<file>.jpg (or .png/.webp).
//      REF ("caption of a library image", e.g. "Character waving at blank wall"): attached as an INGREDIENT before every prompt, so the
//      generator sees the character instead of only reading its description. Flow consumes the ingredient at each generation, hence the
//      re-attach. The prompt must say "the same character as in the reference image, exactly the same design" (prompts.py --ref adds it).
//      Pick as reference a clean full-body image of the character on a plain background, generated once and kept in the project.
// Flow UI (flow.google.com, October 2026): prompt bar at the bottom with the textbox "Que voulez-vous créer ?", the "Agent"
// toggle OFF (direct mode), the settings trigger set to Image · 16:9 · x1. Results are `group`s in a virtual-scrolled list, NEWEST
// FIRST: a fresh tile carries the full prompt as its accessible name, then Flow replaces it with a short caption (so never rely on
// the prompt text alone). A refused generation is a `group` whose text starts with "Échec" (unusual activity, free of charge).
// Success = the newest tile shows an <img> ≥ 512 px whose URL was not on the page before the click. Failure = the number of
// failure cards grew. After MAXFAIL consecutive failures the run stops: wait 30 min or more, then run the same command again.
// If tiles were generated but not downloaded (timeouts), run harvest.mjs to recover them from the project.
import fs from 'node:fs';
import path from 'node:path';
import { attach, sleep, stamp } from './cdp.mjs';

const [src = 'prompts.json', out = 'flow/out'] = process.argv.slice(2);
const REF = process.env.REF || '';
const PACE = Number(process.env.PACE || 45_000), WAIT = Number(process.env.WAIT || 150_000), MAXFAIL = Number(process.env.MAXFAIL || 3);
const prompts = JSON.parse(fs.readFileSync(src, 'utf8'));
fs.mkdirSync(out, { recursive: true });
const done = new Set(fs.readdirSync(out).filter(f => !/\.test\./.test(f)).map(f => f.replace(/\.(jpg|jpeg|png|webp)$/i, '')));
const todo = prompts.filter(p => !done.has(p.file));
console.log(`${stamp()} ${prompts.length} prompts, ${todo.length} to generate, pace ${PACE} ms${REF ? `, reference "${REF}"` : ''}`);

const { page } = await attach(); page.setDefaultTimeout(15_000);
const box = () => page.getByRole('textbox', { name: /Que voulez-vous créer|What do you want to create/i }).first();
const genButton = () => page.getByRole('button', { name: /Lancer la génération|^Generate$|Générer|Start generation/i }).first();
const groups = () => page.locator('main [role="group"]');
async function attachRef(prompt) {   // open the ingredient picker, search the reference by its caption, click it (it becomes a chip in the prompt bar)
  const chip = page.getByRole('button', { name: /^Ingrédient$|^Ingredient$/ });
  const wanted = REF && /reference image/i.test(prompt);        // only prompts that point to it (prompts.py --ref): a reference attached to a
  if (!wanted) {                                                 // background or a no-character insert puts the character into the picture
    if (await chip.count()) { await page.getByRole('button', { name: /Effacer le prompt|Clear prompt/i }).first().click().catch(() => {}); await sleep(400); }
    return true;
  }
  if (await chip.count()) return true;   // already attached
  await page.getByRole('button', { name: /Ajouter des ingrédients|Add ingredients/i }).first().click(); await sleep(900);
  const search = page.getByRole('textbox', { name: /Rechercher des éléments|Search/i }).first();
  if (await search.count()) { await search.fill(REF); await sleep(900); }
  const opt = page.getByRole('option', { name: new RegExp(REF.slice(0, 24).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i') }).first();
  if (!(await opt.count())) { await page.keyboard.press('Escape'); console.log(`${stamp()} reference "${REF}" not found in the library`); return false; }
  await opt.click(); await sleep(700); await page.keyboard.press('Escape'); await sleep(400);
  return (await page.getByRole('button', { name: /^Ingrédient$|^Ingredient$/ }).count()) > 0;
}
const failCount = () => groups().filter({ hasText: /Échec|Failed/ }).count();  // card text starts with the icon name "warning", so no anchor
const bigImages = () => page.evaluate(() => [...document.querySelectorAll('main img')].filter(i => i.naturalWidth >= 512).map(i => i.src));
const scrollTop = () => page.evaluate(() => { const c = document.querySelector('.cdk-virtual-scrollable'); if (c) c.scrollTop = 0; });

async function ensureDirectMode() {
  const agent = page.getByRole('button', { name: /^Agent$/ }).first();
  if (await agent.isVisible().catch(() => false) && (await agent.getAttribute('aria-pressed')) === 'true') { await agent.click(); await sleep(800); console.log(`${stamp()} Agent mode switched off (direct mode)`); }
  const trig = page.getByRole('button', { name: /Déclencheur des paramètres|Settings trigger/i }).first();
  const label = (await trig.innerText().catch(() => '')).replace(/\s+/g, ' ');
  if (!/x1/.test(label)) { await trig.click(); await sleep(800); await page.getByRole('radio', { name: /^Image$/ }).first().click({ force: true }).catch(() => {}); await page.getByRole('radio', { name: /^16:9$/ }).first().click({ force: true }).catch(() => {}); await page.getByRole('radio', { name: /^x1$/ }).first().click({ force: true }).catch(() => {}); await page.keyboard.press('Escape'); await sleep(500); console.log(`${stamp()} settings set to Image · 16:9 · x1 (was "${label}")`); }
}
async function newImage(before, key) {  // URL of a fresh ≥512 px image: in the tile carrying the prompt, else in the newest tile
  const cand = [groups().filter({ hasText: key }).first(), groups().first()];
  for (const g of cand) {
    const u = await g.locator('img').first().evaluate(i => i.naturalWidth >= 512 ? i.src : '').catch(() => '');
    if (u && !before.has(u)) return u;
  }
  return '';
}
async function download(srcUrl, file) {
  const { b64, type } = await page.evaluate(async (u) => {
    const r = await fetch(u); const buf = await r.arrayBuffer(); const bytes = new Uint8Array(buf); let s = '';
    for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
    return { b64: btoa(s), type: r.headers.get('content-type') || '' };
  }, srcUrl);
  const ext = /png/.test(type) ? 'png' : /webp/.test(type) ? 'webp' : 'jpg';
  const dst = path.join(out, `${file}.${ext}`); fs.writeFileSync(dst, Buffer.from(b64, 'base64')); return dst;
}

await ensureDirectMode();
let ok = 0, skipped = 0, streak = 0;
for (const [k, p] of todo.entries()) {
  const key = p.prompt.slice(0, 60);
  try {
    await scrollTop();
    const before = new Set(await bigImages()); const fails0 = await failCount();
    if (!(await attachRef(p.prompt))) { console.log(`${stamp()} ${p.file} SKIP: reference ingredient could not be attached`); skipped++; await sleep(PACE); continue; }
    const b = box(); await b.click(); await page.keyboard.press('End'); await page.keyboard.insertText(p.prompt); await sleep(300);
    const g = genButton();
    if (await g.isDisabled().catch(() => true)) { console.log(`${stamp()} ${p.file} SKIP: generate button disabled (no credits or empty prompt)`); skipped++; await sleep(PACE); continue; }
    await g.click();
    const w0 = Date.now(); let got = false, failed = false;
    while (Date.now() - w0 < WAIT) {
      await sleep(2000); await scrollTop();
      if (await failCount() > fails0) { failed = true; break; }
      const srcUrl = await newImage(before, key);
      if (srcUrl) { await sleep(1500); const dst = await download(srcUrl, p.file); ok++; got = true; streak = 0; console.log(`${stamp()} ${p.file} ok -> ${dst} (${k + 1}/${todo.length}, ${Math.round((Date.now() - w0) / 1000)} s)`); break; }
    }
    if (failed) {
      streak++; skipped++;
      const pause = Math.min(streak * 180_000, 600_000);
      console.log(`${stamp()} ${p.file} REFUSED by Flow (failure card, ${streak}/${MAXFAIL} in a row)${streak < MAXFAIL ? `: pausing ${pause / 60_000} min` : ''}`);
      if (streak >= MAXFAIL) { console.log(`${stamp()} Flow is blocking generations ("unusual activity"). Stopping: wait 30 min or more, then run the same command again.`); break; }
      await sleep(pause); continue;
    }
    if (!got) { console.log(`${stamp()} ${p.file} TIMEOUT after ${WAIT / 1000} s (if the tile completed later, harvest.mjs recovers it)`); skipped++; }
  } catch (e) { console.log(`${stamp()} ${p.file} ERROR ${e.message.split('\n')[0]}`); skipped++; }
  await sleep(PACE);
}
console.log(`${stamp()} done: ${ok} downloaded, ${skipped} skipped or failed. Run the same command again to retry the missing ones.`);
process.exit(0);
