// Opens a real Chrome on Google Flow with a persistent profile and a CDP port, and keeps it open.
//   node scripts/flow/browser.mjs            (leave it running; Ctrl+C closes Chrome)
// Profile: ~/.flow-profile or FLOW_PROFILE. Port: 9222 or FLOW_PORT. The Google session survives between runs.
// A Chrome you already have open cannot be driven (no debugging port, and Chrome refuses CDP on the default profile),
// so this window is a separate profile: sign in once in it, then login.mjs / batch.mjs attach to it.
import { chromium, PROFILE, CDP_PORT, FLOW_URL, sleep } from './cdp.mjs';

const ctx = await chromium.launchPersistentContext(PROFILE, {
  channel: 'chrome', headless: false, viewport: null,
  args: [`--remote-debugging-port=${CDP_PORT}`, '--start-maximized', '--disable-blink-features=AutomationControlled'],
  ignoreDefaultArgs: ['--enable-automation'],
});
const page = ctx.pages()[0] || await ctx.newPage();
await page.goto(FLOW_URL, { waitUntil: 'domcontentloaded' }).catch(e => console.log('goto:', e.message));
console.log(`Chrome open on ${FLOW_URL} | profile ${PROFILE} | CDP port ${CDP_PORT}. Leave this process running.`);
process.on('SIGINT', async () => { await ctx.close().catch(() => {}); process.exit(0); });
for (;;) await sleep(60_000);
