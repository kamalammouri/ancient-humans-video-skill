// Accessibility tree of the Flow page (or of a region), to find controls.  node aria.mjs [regex of a role/name to filter lines]
import { attach } from './cdp.mjs';
const { page } = await attach();
const snap = await page.locator('body').ariaSnapshot();
const re = process.argv[2] ? new RegExp(process.argv[2], 'i') : null;
console.log(re ? snap.split('\n').filter(l => re.test(l)).join('\n') : snap);
process.exit(0);
