// Open a Flow project in the running Chrome and report whether the prompt box is there.  node goto.mjs <project url>
import { attach } from './cdp.mjs';
const { page } = await attach();
await page.goto(process.argv[2], { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(8000);
const tb = page.getByRole('textbox', { name: /Que voulez-vous créer|What do you want to create/ });
console.log(page.url(), '| prompt box:', await tb.count(), '| tiles:', await page.locator('flow-grid-tile-container').count());
process.exit(0);
