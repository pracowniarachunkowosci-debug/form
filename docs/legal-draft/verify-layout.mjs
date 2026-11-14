// Run with node --experimental-websocket. Uses a separate headless Chrome profile,
// no user browser/session and no CUA. Outputs only to this packet's qa directory.
import { spawn } from 'node:child_process';
import { mkdtemp, mkdir, readdir, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));
const out = join(root, 'qa');
await mkdir(out, { recursive: true });
const profile = await mkdtemp(join(tmpdir(), 'pf-legal-headless-'));
const chrome = spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  '--disable-background-networking', '--remote-debugging-port=0', `--user-data-dir=${profile}`, 'about:blank'
], { windowsHide: true, stdio: ['ignore', 'ignore', 'pipe'] });
let socket;
try {
  const endpoint = await new Promise((resolve, reject) => {
    let log = '';
    const timer = setTimeout(() => reject(new Error('Headless startup timeout')), 20000);
    chrome.on('error', error => { clearTimeout(timer); reject(error); });
    chrome.stderr.on('data', chunk => {
      log += chunk.toString();
      const match = log.match(/DevTools listening on (ws:\/\/[^\s]+)/);
      if (match) { clearTimeout(timer); resolve(match[1]); }
    });
  });
  socket = new WebSocket(endpoint);
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  let sequence = 0;
  const waiting = new Map();
  socket.onmessage = event => {
    const message = JSON.parse(event.data);
    const request = waiting.get(message.id);
    if (!request) return;
    waiting.delete(message.id);
    clearTimeout(request.timer);
    if (message.error) request.reject(new Error(JSON.stringify(message.error)));
    else request.resolve(message.result);
  };
  const call = (method, params = {}, sessionId) => new Promise((resolve, reject) => {
    const id = ++sequence;
    const timer = setTimeout(() => { waiting.delete(id); reject(new Error(`Timeout: ${method}`)); }, 20000);
    waiting.set(id, { resolve, reject, timer });
    socket.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
  });
  const { targetId } = await call('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await call('Target.attachToTarget', { targetId, flatten: true });
  const cmd = (method, params) => call(method, params, sessionId);
  await cmd('Page.enable');
  await cmd('Runtime.enable');
  const results = [];
  const files = (await readdir(root)).filter(name => name.endsWith('.html')).sort();
  for (const file of files) {
    await cmd('Page.navigate', { url: pathToFileURL(join(root, file)).href });
    for (let attempt = 0; attempt < 60; attempt++) {
      const loaded = await cmd('Runtime.evaluate', { expression: 'document.readyState', returnByValue: true });
      if (loaded.result.value === 'complete') break;
      await new Promise(resolve => setTimeout(resolve, 50));
    }
    for (const width of [320, 360, 390, 430, 1100]) {
      await cmd('Emulation.setEmulatedMedia', { media: 'screen' });
      await cmd('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: 1, mobile: false });
      const { result } = await cmd('Runtime.evaluate', { returnByValue: true, expression: `JSON.stringify({
        width: document.documentElement.clientWidth, scrollWidth: document.documentElement.scrollWidth,
        heading: document.querySelector('h1')?.textContent,
        notices: [...document.querySelectorAll('.status')].every(e => e.getBoundingClientRect().height > 0),
        resources: performance.getEntriesByType('resource').map(e => e.name)
      })` });
      const measurements = JSON.parse(result.value);
      if (measurements.scrollWidth > measurements.width || !measurements.notices) throw new Error(`${file}: layout failed ${width}`);
      if (measurements.resources.some(url => !url.startsWith('file:'))) throw new Error(`${file}: remote resource`);
      results.push({ file, media: 'screen', viewport: width, ...measurements });
      if (file === 'index.html' && width === 390) {
        const shot = await cmd('Page.captureScreenshot', { format: 'png' });
        await writeFile(join(out, 'index-mobile.png'), Buffer.from(shot.data, 'base64'));
      }
    }
    await cmd('Emulation.setEmulatedMedia', { media: 'print' });
    await cmd('Emulation.setDeviceMetricsOverride', { width: 680, height: 960, deviceScaleFactor: 1, mobile: false });
    const { result } = await cmd('Runtime.evaluate', { returnByValue: true, expression: `JSON.stringify({
      width: document.documentElement.clientWidth, scrollWidth: document.documentElement.scrollWidth,
      navHidden: getComputedStyle(document.querySelector('nav') || document.createElement('nav')).display === 'none',
      draftVisible: document.querySelector('.status').getBoundingClientRect().height > 0,
      textHeight: document.documentElement.scrollHeight
    })` });
    const printed = JSON.parse(result.value);
    // Index has no navigation; all document pages have print-hidden navigation.
    if (printed.scrollWidth > printed.width || !printed.draftVisible || (file !== 'index.html' && !printed.navHidden)) throw new Error(`${file}: print style failed`);
    const pdf = await cmd('Page.printToPDF', { preferCSSPageSize: true, printBackground: true, displayHeaderFooter: false });
    const bytes = Buffer.from(pdf.data, 'base64');
    if (bytes.subarray(0, 5).toString() !== '%PDF-') throw new Error(`${file}: invalid print output`);
    const pages = (bytes.toString('latin1').match(/\/Type\s*\/Page\b/g) || []).length;
    if (!pages) throw new Error(`${file}: no printed pages`);
    results.push({ file, media: 'print', ...printed, pdfBytes: bytes.length, pages });
    if (file === 'formularz-odstapienia.html') {
      const shot = await cmd('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true,
        clip: { x: 0, y: 0, width: 680, height: printed.textHeight, scale: 1 } });
      await writeFile(join(out, 'formularz-print.png'), Buffer.from(shot.data, 'base64'));
    }
  }
  await writeFile(join(out, 'layout.json'), JSON.stringify({ status: 'PASS', browser: 'isolated headless Chrome',
    htmlFiles: files.length, screenChecks: files.length * 5, printChecks: files.length,
    printNote: 'CSS print emulation plus A4 PDF generation; PDFs not retained. Screenshots are not paginated PDF renders.', results }, null, 2) + '\n');
  console.log(JSON.stringify({ status: 'PASS', htmlFiles: files.length, screenChecks: files.length * 5,
    printChecks: files.length, printPages: results.filter(row => row.media === 'print').map(({ file, pages }) => ({ file, pages })) }));
  await call('Browser.close').catch(() => {});
} finally {
  socket?.close();
  chrome.kill();
  // Dedicated profile stays in the OS temporary directory; no recursive deletion.
}
