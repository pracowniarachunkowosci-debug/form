import { runCLI } from '@wp-playground/cli';
import { Server } from 'node:net';
import { readFile, readdir, mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import assert from 'node:assert/strict';

process.chdir(dirname(fileURLToPath(import.meta.url)));
await mkdir('test-results', { recursive: true });
const steps = [
  { step: 'defineWpConfigConsts', consts: {
    WP_ENVIRONMENT_TYPE: 'local', DISABLE_WP_CRON: true,
    WP_DEBUG: false, AUTOMATIC_UPDATER_DISABLED: true,
  } },
  { step: 'mkdir', path: '/wordpress/wp-content/mu-plugins' },
  { step: 'writeFile', path: '/wordpress/wp-content/mu-plugins/pf-local-guard.php', data: await readFile('local-guard.php', 'utf8') },
  { step: 'mkdir', path: '/wordpress/wp-content/themes/pf-r04-local' },
];
for (const file of await readdir('theme')) {
  steps.push({ step: 'writeFile', path: `/wordpress/wp-content/themes/pf-r04-local/${file}`, data: await readFile(join('theme', file), 'utf8') });
}
steps.push({ step: 'installPlugin', pluginData: { resource: 'url', url: 'https://downloads.wordpress.org/plugin/woocommerce.11.2.1.zip' }, options: { activate: true } });

// Playground 3.1.62 has no public bind-host option. Restrict its HTTP listener
// and availability probe to loopback, then restore the process-local method.
const originalListen = Server.prototype.listen;
Server.prototype.listen = function (...args) {
  if (typeof args[0] === 'number') {
    if (typeof args[1] === 'string') args[1] = '127.0.0.1';
    else args.splice(1, 0, '127.0.0.1');
  } else if (typeof args[0] === 'object' && args[0]?.port !== undefined) {
    args[0] = { ...args[0], host: '127.0.0.1' };
  } else {
    throw new Error('Unexpected listener: refusing non-loopback prototype server');
  }
  return originalListen.apply(this, args);
};
let instance;
try {
  instance = await runCLI({
    command: 'server', port: 8774, wp: '7.1.4', php: '8.3', workers: 6,
    login: true, blueprint: { landingPage: '/', steps },
    'php-ini': { memory_limit: '512M', max_execution_time: '120' },
  });
} finally {
  Server.prototype.listen = originalListen;
}
assert.equal(instance.server.address().address, '127.0.0.1');
const seeded = await instance.playground.run({ code: await readFile('seed.php', 'utf8') });
assert.equal(seeded.exitCode, 0, seeded.errors);
const seed = JSON.parse(seeded.text);
await writeFile('test-results/seed.json', JSON.stringify(seed, null, 2));
console.log('Seed:', JSON.stringify(seed));
if (process.argv.includes('--test')) {
  try {
    const result = await instance.playground.run({ code: await readFile('verify.php', 'utf8') });
    assert.equal(result.exitCode, 0, result.errors);
    const checks = JSON.parse(result.text);
    assert.equal(checks.passed, true);
    // Node fetch has no cookie jar. Skip Playground's browser-only auto-login
    // for these anonymous HTTP checks; the browser manages its own cookies.
    const headers = { Cookie: 'playground_auto_login_already_happened=1' };
    const response = await fetch('http://127.0.0.1:8774/', { headers });
    assert.equal(response.status, 200);
    assert.match(response.headers.get('x-robots-tag'), /noindex/);
    const html = await response.text();
    assert.match(html, /WINTER AFTER DARK/);
    assert.match(html, /PF-TEST|obiekt techniczny/);
    const checkout = await fetch('http://127.0.0.1:8774/?rest_route=/wc/store/v1/checkout', {method:'POST', headers});
    assert.equal(checkout.status, 403);
    await writeFile('test-results/verification.json', JSON.stringify({ seed, checks, loopback: true, homepage: 200, storeCheckout: 403 }, null, 2));
    console.log('PASS: stock, variations, guards, frontend, loopback. SQLite prototype only.');
    console.log('Action Scheduler probe:', JSON.stringify(checks.queue_probe));
  } finally {
    if (!process.argv.includes('--keep')) await instance[Symbol.asyncDispose]();
  }
}
if (!process.argv.includes('--test') || process.argv.includes('--keep')) {
  console.log('Local preview: http://127.0.0.1:8774/');
  console.log(`Native product editor: http://127.0.0.1:8774/wp-admin/post.php?post=${seed.product}&action=edit`);
  console.log('Local Playground auto-login; synthetic data only. Stop with Ctrl+C.');
  process.on('SIGINT', async () => { await instance[Symbol.asyncDispose](); process.exit(0); });
}
