// DOM regression tests. Setup (from repository root):
// npm install --prefix tmp/report-viewer-tests --no-save --no-package-lock jsdom@26.1.0
// node --test tests/test_report_viewer.cjs
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {join} = require('node:path');
const {test} = require('node:test');
const {JSDOM} = require(require.resolve('jsdom', {paths: [join(__dirname, '../tmp/report-viewer-tests')]}));
const root = join(__dirname, '..');
const html = readFileSync(join(root, 'web/calculator.html'), 'utf8');
const viewer = readFileSync(join(root, 'web/report-viewer.js'), 'utf8');
const calculator = readFileSync(join(root, 'web/calculator.js'), 'utf8');
const fixture = '<!doctype html><html><head><style>:root{--ink:#292c34}body{color:var(--ink)}tbody th{font-weight:bold}</style></head>' +
  '<body><main><header><h1>Micro dataset quality analysis</h1></header><section><h2>Simulation verification</h2>' +
  '<table><tbody><tr><th>Weighted mean</th><td>188.5776 ms</td></tr></tbody></table>' +
  '<img src="data:image/png;base64,iVBORw0KGgo=" alt="Failure rate chart">' +
  '<details><summary>Inputs</summary><p>Recorded website checks</p></details></section></main></body></html>';

function setup(response = {category:'independent', message:'Recorded website data', report_html:fixture}) {
  const dom = new JSDOM(html, {url:'https://qc-simulation.vercel.app/', runScripts:'outside-only'});
  dom.window.matchMedia = () => ({matches:false});
  dom.window.structuredClone = structuredClone;
  dom.window.TextEncoder = TextEncoder;
  dom.window.fetch = async (url, options) => ({ok:true, json:async () => options ? response : url.includes('chapter10') ? {cases:[]} : {}});
  dom.window.eval(viewer);
  return dom;
}

test('dataset report renders its tables, charts and expandable details directly in the page', () => {
  const dom = setup();
  const host = dom.window.document.getElementById('result-report');
  dom.window.QCReportViewer.render(host, fixture);
  const content = host.shadowRoot;
  assert.match(content.textContent, /Simulation verification/);
  assert.equal(content.querySelector('td').textContent, '188.5776 ms');
  assert.equal(content.querySelectorAll('img').length, 1);
  content.querySelector('details').open = true;
  assert.equal(content.querySelector('details').open, true);
  assert.equal(dom.window.document.querySelectorAll('iframe').length, 0);
  assert.match(content.querySelector('style').textContent, /:host\{/);
  assert.match(content.querySelector('style').textContent, /\.report-document\{color/);
  assert.match(content.querySelector('style').textContent, /tbody th/);
  dom.window.close();
});

test('numerical report retains results and comparison while removing standalone report navigation', () => {
  const dom = setup();
  const report = '<html><head><style>body{margin:0}</style></head><body><header class="topbar">Navigation</header>' +
    '<main><header class="report-heading">Overview</header><div class="overview">Counters</div>' +
    '<section class="exercise"><h2>10-44: Control limits</h2><div class="comparison">Independent validation: Verified</div>' +
    '<details><summary>Simulation verification</summary><p>Calculated probability</p></details></section><footer>Downloads</footer></main></body></html>';
  dom.window.QCReportViewer.render(dom.window.document.getElementById('result-report'), report);
  const content = dom.window.document.getElementById('result-report').shadowRoot;
  assert.match(content.textContent, /Independent validation: Verified/);
  assert.equal(content.querySelector('.topbar,.report-heading,.overview,footer'), null);
  assert.equal(content.querySelectorAll('details').length, 1);
  dom.window.close();
});

test('report content cannot run scripts, inject event handlers or embed external pages', () => {
  const dom = setup();
  const unsafe = fixture.replace('</main>', '<script>window.compromised=true</script><iframe src="https://example.com"></iframe>' +
    '<img src="https://example.com/tracker" onerror="window.compromised=true"><a href="javascript:alert(1)" onclick="alert(1)">Link</a>' +
    '<a href="https://www.itl.nist.gov/" target="_blank">Reference</a></main>');
  dom.window.QCReportViewer.render(dom.window.document.getElementById('result-report'), unsafe);
  const content = dom.window.document.getElementById('result-report').shadowRoot;
  assert.equal(content.querySelector('script,iframe,[onerror],[onclick],[href^="javascript:"]'), null);
  assert.equal(content.querySelectorAll('img[src]').length, 1);
  assert.equal(content.querySelector('a[target="_blank"]').rel, 'noopener noreferrer');
  assert.equal(dom.window.compromised, undefined);
  dom.window.close();
});

test('a second report replaces the first and clearing removes previous content', () => {
  const dom = setup();
  const host = dom.window.document.getElementById('result-report');
  dom.window.QCReportViewer.render(host, fixture);
  dom.window.QCReportViewer.render(host, fixture.replace('Micro dataset', 'Macro dataset'));
  assert.match(host.shadowRoot.textContent, /Macro dataset/);
  assert.doesNotMatch(host.shadowRoot.textContent, /Micro dataset/);
  assert.equal(host.shadowRoot.querySelectorAll('main').length, 1);
  dom.window.QCReportViewer.clear(host);
  assert.equal(host.shadowRoot.childNodes.length, 0);
  dom.window.close();
});

test('empty or incomplete reports fail visibly instead of being labelled complete', () => {
  const dom = setup();
  const host = dom.window.document.getElementById('result-report');
  for (const value of ['', null, '<p>Not a report</p>']) {
    assert.throws(() => dom.window.QCReportViewer.render(host, value), /report/);
  }
  dom.window.close();
});

test('Analyse and simulate displays the returned report and restores the form controls', async () => {
  const dom = setup();
  dom.window.eval(calculator);
  dom.window.document.getElementById('dataset-tab').click();
  dom.window.document.getElementById('dataset-form').dispatchEvent(new dom.window.Event('submit', {bubbles:true, cancelable:true}));
  await new Promise(resolve => setImmediate(resolve));
  const document = dom.window.document;
  assert.equal(document.getElementById('result-content').hidden, false);
  assert.equal(document.getElementById('empty-result').hidden, true);
  assert.match(document.getElementById('result-report').shadowRoot.textContent, /188\.5776 ms/);
  assert.equal(document.getElementById('analyse-button').disabled, false);
  assert.equal(document.getElementById('dataset-error').hidden, true);
  dom.window.close();
});

test('an invalid successful API response shows an error without an empty completed report', async () => {
  const dom = setup({report_html:''});
  dom.window.eval(calculator);
  dom.window.document.getElementById('dataset-tab').click();
  dom.window.document.getElementById('dataset-form').dispatchEvent(new dom.window.Event('submit', {bubbles:true, cancelable:true}));
  await new Promise(resolve => setImmediate(resolve));
  const document = dom.window.document;
  assert.equal(document.getElementById('result-content').hidden, true);
  assert.equal(document.getElementById('dataset-error').hidden, false);
  assert.match(document.getElementById('dataset-error').textContent, /empty report/);
  assert.equal(document.getElementById('analyse-button').disabled, false);
  dom.window.close();
});
