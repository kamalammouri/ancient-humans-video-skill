// Shared helpers: resolve playwright (from PLAYWRIGHT_DIR or next to this script), the persistent profile, the CDP endpoint, and attach().
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import os from 'node:os';

const here = path.dirname(fileURLToPath(import.meta.url));
const pwDir = process.env.PLAYWRIGHT_DIR || here;
let playwright;
try { playwright = createRequire(path.join(pwDir, 'package.json'))('playwright'); }
catch { try { playwright = createRequire(path.join(here, 'package.json'))('playwright'); }
  catch { console.error(`playwright not found. Run "npm i playwright" in a folder and set PLAYWRIGHT_DIR to it (tried ${pwDir}).`); process.exit(2); } }

export const { chromium } = playwright;
export const PROFILE = process.env.FLOW_PROFILE || path.join(os.homedir(), '.flow-profile');
export const CDP_PORT = Number(process.env.FLOW_PORT || 9222);
export const CDP = process.env.FLOW_CDP || `http://127.0.0.1:${CDP_PORT}`;   // Chrome sometimes listens on [::1] only: FLOW_CDP=http://[::1]:9222
export const FLOW_URL = 'https://labs.google/fx/tools/flow';
export const sleep = (ms) => new Promise(r => setTimeout(r, ms));
export const stamp = () => new Date().toTimeString().slice(0, 8);

/** Attach to the Chrome started by browser.mjs and return its Flow page; FLOW_PROJECT=<project url> is opened in a new tab when none is found. */
export async function attach() {
  let browser;
  try { browser = await chromium.connectOverCDP(CDP, { timeout: 5000 }); }
  catch (e) { console.error(`No Chrome on ${CDP}. Start it first: node scripts/flow/browser.mjs (keep it running).`); process.exit(2); }
  const ctx = browser.contexts()[0] || await browser.newContext();
  const pages = ctx.pages();
  // FLOW_TAB=last drives the newest Flow tab, so the user can keep working in the first one (5 Nov 2026: a user edit in the shared tab broke a batch)
  let page = pages[process.env.FLOW_TAB === 'last' ? 'findLast' : 'find'](p => /flow\.google\.com|labs\.google/.test(p.url()));
  if (!page) {                      // the user browsed elsewhere in that tab or closed it: open Flow in a NEW tab, never touch their tabs
    const url = process.env.FLOW_PROJECT || FLOW_URL;
    console.log(`${stamp()} no Flow tab found: opening ${url} in a new tab`);
    page = await ctx.newPage(); await page.goto(url, { waitUntil: 'domcontentloaded' }); await sleep(6000);
  }
  return { browser, ctx, page };
}
