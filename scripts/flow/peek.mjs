// Screenshot + accessibility snapshot of the Flow page, to diagnose a stuck batch without touching the window.
//   node scripts/flow/peek.mjs out.png [--full]
import fs from 'node:fs';
import { attach } from './cdp.mjs';

const [out = 'peek.png'] = process.argv.slice(2).filter(a => !a.startsWith('--'));
const { browser, page } = await attach();
console.log('url:', page.url(), '| title:', await page.title());
await page.screenshot({ path: out, fullPage: process.argv.includes('--full') });
const snap = await page.locator('body').ariaSnapshot().catch(() => '(no snapshot)');
fs.writeFileSync(out.replace(/\.png$/i, '') + '.aria.txt', snap);
console.log(snap.split('\n').slice(0, 80).join('\n'));
console.log(`\nscreenshot: ${out} | full aria snapshot: ${out.replace(/\.png$/i, '')}.aria.txt`);
await browser.close().catch(() => {}); process.exit(0);
