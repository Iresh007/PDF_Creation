// Usage: node render_pdf.js <input.html> <output.pdf> "<footer title>"
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const [input, output, title = ''] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(input), { waitUntil: 'networkidle' });
  await page.pdf({
    path: output,
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: `<div style="font-size:7px;width:100%;padding:0 12mm;color:#888;display:flex;justify-content:space-between;">
      <span>${title}</span><span>Page <span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`,
    margin: { top: '12mm', bottom: '14mm', left: '12mm', right: '12mm' },
  });
  await browser.close();
})();
