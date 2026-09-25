// Export PNGs from ../logo/*.svg with Playwright's Chromium (transparent where the SVG is).
//   NODE_PATH="$(npm root -g)" node export_png.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const LOGO = path.join(__dirname, '..', 'logo');
const OUT = path.join(__dirname, '..', 'png');

// [svg, png, width in px]
const JOBS = [
  ['bar-martiri-logo.svg', 'bar-martiri-logo.png', 2400],
  ['bar-martiri-logo-reverse.svg', 'bar-martiri-logo-reverse.png', 2400],
  ['bar-martiri-logo-ink.svg', 'bar-martiri-logo-ink.png', 2400],
  ['bar-martiri-logo-paper.svg', 'bar-martiri-logo-paper.png', 2400],
  ['bar-martiri-logo-stacked.svg', 'bar-martiri-logo-stacked.png', 1600],
  ['bar-martiri-logo-stacked-reverse.svg', 'bar-martiri-logo-stacked-reverse.png', 1600],
  ['bar-martiri-icon-square.svg', 'bar-martiri-avatar-1080.png', 1080],
  ['bar-martiri-icon.svg', 'favicon-32.png', 32],
  ['bar-martiri-icon.svg', 'favicon-48.png', 48],
  ['bar-martiri-icon.svg', 'favicon-96.png', 96],
  ['bar-martiri-icon.svg', 'icon-192.png', 192],
  ['bar-martiri-icon-square.svg', 'apple-touch-icon.png', 180],
  ['bar-martiri-icon-square.svg', 'icon-512.png', 512],
];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const [svg, png, width] of JOBS) {
    // Inline the SVG: an about:blank page may not load file:// images.
    const markup = fs.readFileSync(path.join(LOGO, svg), 'utf8');
    await page.setContent(`<body style="margin:0;background:transparent"><div id="i" style="width:${width}px;line-height:0">${markup}</div>
      <style>#i svg{display:block;width:100%;height:auto}</style></body>`);
    await page.locator('#i').screenshot({ path: path.join(OUT, png), omitBackground: true });
    console.log(png);
  }
  await browser.close();
})();
