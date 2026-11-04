// Waits for YOU to sign in to Google Flow in the Chrome opened by browser.mjs. Never types credentials.
//   node scripts/flow/login.mjs        (polls up to 20 min, exits 0 once the Flow editor or project list is visible)
import { attach, FLOW_URL, sleep, stamp } from './cdp.mjs';

const { browser, page } = await attach();
if (!page.url().includes('labs.google')) await page.goto(FLOW_URL, { waitUntil: 'domcontentloaded' }).catch(() => {});
const start = page.getByRole('button', { name: /Créer avec Google Flow|Create with Google Flow|Get started|Commencer/i }).first();
if (await start.isVisible().catch(() => false)) { await start.click().catch(() => {}); console.log(`${stamp()} clicked the start button`); }

const deadline = Date.now() + 20 * 60_000;
while (Date.now() < deadline) {
  const url = page.url();
  const editor = await page.getByPlaceholder(/Que voulez-vous créer|What do you want to create/i).first().isVisible().catch(() => false);
  const projects = await page.getByRole('button', { name: /Nouveau projet|New project/i }).first().isVisible().catch(() => false);
  if (editor || projects) {
    console.log(`${stamp()} signed in: ${editor ? 'editor visible' : 'project list visible'} (${url})`);
    console.log(editor ? 'Ready for batch.mjs.' : 'Create or open a project, switch to image mode and set 16:9, then run batch.mjs.');
    await browser.close().catch(() => {}); process.exit(0);
  }
  console.log(`${stamp()} waiting for sign-in in the Chrome window… (${url.slice(0, 60)})`);
  await sleep(5000);
}
console.log('Timed out after 20 min without a signed-in Flow page.'); process.exit(1);
