'use strict';

const $ = id => document.getElementById(id);
const form = $('calculator-form');
const kind = $('kind');
const source = $('exercise-select');
const mode = $('entry-mode');
const dataSource = $('data-source');
const maxRows = 20000;
const maxBytes = 2 * 1024 * 1024;
let cases = [], lastResult = null, loadedInputs = {}, catalogLoaded = false, requestPending = false;
let workflow = 'numerical', datasetManifest = null;

const typeLabels = {
  xbar: 'Mean control chart (X̄)', range: 'Range control chart (R)', p: 'Proportion control chart (p)',
  acceptance: 'Acceptance sampling', pareto: 'Pareto analysis',
  proportion_test: 'Proportion hypothesis test', range_identity: 'Recover upper range limit'
};
const labels = {
  n: 'Subgroup / sample size (n)', N: 'Lot size (N)', mean: 'Grand mean', rbar: 'Average range (R̄)',
  se: 'Known standard error', p: 'Proportion (p)', p0: 'Null proportion (p₀)', c: 'Acceptance number (c)',
  successes: 'Observed events', alpha: 'Significance level (α)', lcl: 'Lower control limit',
  means: 'Subgroup means', ranges: 'Subgroup ranges', observations: 'Subgroup measurements',
  counts: 'Counts by subgroup', proportions: 'Proportions by subgroup', risk: 'Risk to calculate', model: 'Probability model'
};
const placeholders = {
  n: 'Enter the sample size, e.g. 10', N: 'Enter the lot size, e.g. 2500', mean: 'Enter the grand mean, e.g. 50',
  rbar: 'Enter the average range, e.g. 6.8', se: 'Enter the standard error, e.g. 0.5',
  p: 'Enter a fraction, e.g. 0.02 for 2%', p0: 'Enter the null fraction, e.g. 0.02',
  c: 'Enter the maximum accepted defects, e.g. 2', successes: 'Enter the observed count, e.g. 45',
  alpha: 'Enter the significance level, e.g. 0.05', lcl: 'Enter the lower range limit, e.g. 3',
  means: 'Enter subgroup means, e.g. 49.4, 49.9, 48.8', ranges: 'Enter subgroup ranges, e.g. 4, 7, 7',
  counts: 'Enter defect counts, e.g. 2, 1, 3', proportions: 'Enter fractions, e.g. 0.02, 0.03, 0.01'
};
const modes = {
  xbar: [['summary', 'Grand mean and average range'], ['se', 'Grand mean and known standard error'], ['subgroups', 'Subgroup means and ranges'], ['raw', 'Individual subgroup measurements']],
  range: [['summary', 'Average range'], ['subgroups', 'Subgroup means and ranges'], ['raw', 'Individual subgroup measurements']],
  p: [['summary', 'Specified proportion'], ['counts', 'Counts by subgroup'], ['proportions', 'Proportions by subgroup']]
};

function clearResult() {
  lastResult = null;
  $('result-content').hidden = true;
  $('empty-result').hidden = false;
  window.QCReportViewer.clear($('result-report'));
}

function selectWorkflow(next) {
  if (requestPending) return;
  workflow = next;
  clearResult();
  for (const item of ['numerical', 'dataset']) {
    $(item + '-tab').setAttribute('aria-selected', String(item === next));
    $(item + '-tab').tabIndex = item === next ? 0 : -1;
    $(item + '-panel').hidden = item !== next;
  }
  $('empty-result-description').textContent = next === 'dataset'
    ? 'Choose the focused or wider ForeverMart dataset, or import your own CSV, then select Analyse and simulate.'
    : 'Select an assigned book question, enter its values, then press Enter or select Calculate and compare.';
  $('empty-result-list').replaceChildren();
  const points = next === 'dataset'
    ? ['Failure rate, performance summary and exploratory statistics', 'Process charts and performance requirement checks', 'Simulation compared with the dataset’s calculated failure rate']
    : ['Answers calculated using the question’s formula', 'Comparison with available stored reference answers', 'Charts and simulation verification, where applicable'];
  points.forEach(text => { const li = document.createElement('li'); li.textContent = text; $('empty-result-list').append(li); });
}

function inferredMode(inputs) {
  if (inputs.observations) return 'raw';
  if (inputs.means) return 'subgroups';
  if (inputs.se !== undefined) return 'se';
  if (Array.isArray(inputs.counts)) return 'counts';
  if (inputs.proportions) return 'proportions';
  return 'summary';
}

function fieldKeys() {
  const k = kind.value, m = mode.value;
  if (k === 'xbar') return m === 'raw' ? ['n', 'observations'] : m === 'subgroups' ? ['n', 'means', 'ranges'] : m === 'se' ? ['n', 'mean', 'se'] : ['n', 'mean', 'rbar'];
  if (k === 'range') return m === 'raw' ? ['n', 'observations'] : m === 'subgroups' ? ['n', 'means', 'ranges'] : ['n', 'rbar'];
  if (k === 'p') return m === 'counts' ? ['n', 'p', 'counts'] : m === 'proportions' ? ['n', 'p', 'proportions'] : ['n', 'p'];
  if (k === 'acceptance') return ['N', 'n', 'c', 'p', 'risk', 'model'];
  if (k === 'pareto') return ['counts'];
  if (k === 'proportion_test') return ['n', 'successes', 'p0', 'alpha'];
  if (k === 'range_identity') return ['rbar', 'lcl'];
  return [];
}

function fieldValue(key, inputs) {
  if (inputs[key] === undefined) return '';
  if (key === 'observations') return inputs[key].map(row => row.join(', ')).join('\n');
  if (Array.isArray(inputs[key])) return inputs[key].join(', ');
  if (typeof inputs[key] === 'object') return Object.entries(inputs[key]).map(([label, count]) => `${label}: ${count}`).join('\n');
  return inputs[key];
}

function renderFields(inputs = {}) {
  const root = $('input-fields');
  root.replaceChildren();
  for (const key of fieldKeys()) {
    const wrap = document.createElement('div'), label = document.createElement('label');
    label.htmlFor = 'value-' + key;
    label.textContent = kind.value === 'pareto' && key === 'counts' ? 'Defects by category' : labels[key];
    let input;
    if (['means', 'ranges', 'observations', 'counts', 'proportions'].includes(key)) {
      wrap.className = 'field-wide';
      input = document.createElement('textarea');
      input.value = fieldValue(key, inputs);
      input.placeholder = kind.value === 'pareto' ? 'Electrical: 257\nWallboard: 303\nOther: 68'
        : key === 'observations' ? '101, 99, 102, 98, 100\n100, 103, 99, 101, 102' : placeholders[key];
    } else if (key === 'risk' || key === 'model') {
      input = document.createElement('select');
      const options = key === 'risk' ? [['producer', 'Producer’s risk'], ['consumer', 'Consumer’s risk']]
        : [['binomial', 'Binomial'], ['poisson', 'Poisson approximation']];
      options.forEach(([value, text]) => input.add(new Option(text, value)));
      input.value = inputs[key] || options[0][0];
      input.disabled = dataSource.value === 'book';
    } else {
      input = document.createElement('input');
      input.type = 'number';
      input.step = ['n', 'N', 'c', 'successes'].includes(key) ? '1' : 'any';
      input.value = fieldValue(key, inputs);
      if (['n', 'N'].includes(key)) input.min = '1';
      if (['c', 'rbar', 'se', 'lcl', 'successes'].includes(key)) input.min = '0';
      if (['p', 'p0', 'alpha'].includes(key)) { input.min = '0'; input.max = '1'; }
      input.placeholder = placeholders[key];
    }
    input.id = 'value-' + key;
    input.name = key;
    input.required = !(key === 'p' && kind.value === 'p' && mode.value !== 'summary');
    wrap.append(label, input);
    let help = '';
    if (['p', 'p0', 'alpha'].includes(key)) help = 'Use a fraction: 0.02 means 2%.';
    if (key === 'p' && kind.value === 'p' && mode.value !== 'summary') help = 'Optional target. Leave blank to estimate it from the observed data.';
    if (key === 'observations') help = 'One subgroup per line, with n comma-separated measurements.';
    if (key === 'counts' && kind.value === 'pareto') help = 'One category per line: category name: count.';
    if (dataSource.value === 'book' && ['risk', 'model'].includes(key)) help = 'Fixed by the selected book question.';
    if (help) { const hint = document.createElement('p'); hint.className = 'field-hint'; hint.textContent = help; wrap.append(hint); }
    root.append(wrap);
  }
}

function updateModes(inputs) {
  const choices = modes[kind.value] || [], bookMode = dataSource.value === 'book';
  $('mode-container').hidden = bookMode || !choices.length;
  mode.disabled = bookMode;
  mode.replaceChildren();
  choices.forEach(([value, text]) => mode.add(new Option(text, value)));
  mode.value = inferredMode(inputs);
  if (!mode.value && choices.length) mode.selectedIndex = 0;
}

function loadExercise() {
  clearResult();
  $('form-error').hidden = true;
  const bookMode = dataSource.value === 'book';
  const selected = bookMode ? cases.find(item => item.id === source.value) : null;
  loadedInputs = selected ? structuredClone(selected.inputs) : {};
  updateModes(loadedInputs);
  renderFields(selected ? { risk: loadedInputs.risk, model: loadedInputs.model } : {});
  $('input-fields').hidden = bookMode && !selected;
  source.disabled = !bookMode || !catalogLoaded;
  $('load-book-values').disabled = !selected;
  $('load-book-values').hidden = !bookMode;
  $('calculate-button').textContent = bookMode ? 'Calculate and compare' : 'Calculate my values';
  $('source-hint').textContent = !bookMode ? 'These are your independent values. The book question dropdown and reference comparison are disabled.'
    : selected ? `Enter values for ${selected.id} (textbook page ${selected.page}), or load the book values below.`
      : 'Assigned scope: 10.40–10.59. Select a question to see only its required fields.';
}

function populateSources() {
  source.replaceChildren(new Option('Select a book question', ''));
  cases.filter(item => item.kind === kind.value).forEach(item => source.add(new Option(`${item.id} — ${item.title}`, item.id)));
  loadExercise();
}

function updateTypes() {
  const previous = kind.value;
  const bookMode = dataSource.value === 'book';
  const allowed = bookMode ? new Set(cases.map(item => item.kind)) : new Set(Object.keys(typeLabels));
  kind.replaceChildren();
  Object.entries(typeLabels).forEach(([value, text]) => { if (allowed.has(value)) kind.add(new Option(text, value)); });
  if (allowed.has(previous)) kind.value = previous;
  kind.disabled = !allowed.size;
  if (!allowed.size) kind.add(new Option('No assigned questions available', ''));
  populateSources();
}

function numbers(text) {
  const tokens = text.trim().split(/[\s,;]+/).filter(Boolean);
  if (!tokens.length) throw Error('Enter at least one numerical value.');
  return tokens.map(token => { const number = Number(token); if (!Number.isFinite(number)) throw Error(`Invalid numerical value: ${token}`); return number; });
}

function collect() {
  const data = {};
  for (const key of fieldKeys()) {
    const text = $('value-' + key).value.trim();
    if (!text && key === 'p' && kind.value === 'p' && mode.value !== 'summary') continue;
    if (key === 'observations') data[key] = text.split(/\r?\n/).filter(line => line.trim()).map(numbers);
    else if (key === 'counts' && kind.value === 'pareto') {
      data[key] = Object.create(null);
      for (const line of text.split(/\r?\n/).filter(item => item.trim())) {
        const at = line.lastIndexOf(':');
        if (at < 1) throw Error('Use category name: count for each Pareto category.');
        const label = line.slice(0, at).trim(), value = line.slice(at + 1).trim();
        if (Object.hasOwn(data[key], label)) throw Error('Category names must be unique.');
        if (!value || !Number.isFinite(Number(value))) throw Error('Each category needs a valid numerical count.');
        data[key][label] = Number(value);
      }
    } else if (['means', 'ranges', 'counts', 'proportions'].includes(key)) data[key] = numbers(text);
    else if (['risk', 'model'].includes(key)) data[key] = text;
    else {
      if (!text) throw Error(`Enter ${labels[key]}.`);
      const value = Number(text);
      if (!Number.isFinite(value)) throw Error(`Enter a finite number for ${labels[key]}.`);
      data[key] = value;
    }
  }
  if (dataSource.value === 'book' && source.value) {
    for (const key of ['unit', 'attribute']) if (loadedInputs[key] !== undefined) data[key] = loadedInputs[key];
    if (loadedInputs.labels && ((data.means && data.means.length === loadedInputs.labels.length) || (data.observations && data.observations.length === loadedInputs.labels.length))) data.labels = loadedInputs.labels;
  }
  return data;
}

// Parse quoted CSV fields, escaped quotes, commas inside fields, CRLF and UTF-8 BOM.
function parseCSV(text) {
  if (new TextEncoder().encode(text).length > maxBytes) throw Error('The CSV must be no larger than 2 MB.');
  text = text.replace(/^\uFEFF/, '');
  const records = [];
  let record = [], value = '', quoted = false, afterQuote = false;
  const endField = () => { record.push(value); value = ''; afterQuote = false; };
  const endRecord = () => {
    endField();
    if (record.some(item => item.trim() !== '')) records.push(record);
    record = [];
    if (records.length > maxRows + 1) throw Error('Use at most 20,000 data batches.');
  };
  for (let index = 0; index < text.length; index++) {
    const ch = text[index];
    if (quoted) {
      if (ch === '"') {
        if (text[index + 1] === '"') { value += '"'; index++; }
        else { quoted = false; afterQuote = true; }
      } else value += ch;
      continue;
    }
    if (ch === ',') { endField(); continue; }
    if (ch === '\n' || ch === '\r') {
      if (ch === '\r' && text[index + 1] === '\n') index++;
      endRecord(); continue;
    }
    if (afterQuote) {
      if (ch !== ' ' && ch !== '\t') throw Error('Invalid CSV: a quoted field must end with a comma or a new line.');
      continue;
    }
    if (ch === '"') {
      if (value.length) throw Error('Invalid CSV: quotes must begin at the start of a field.');
      quoted = true;
    } else value += ch;
  }
  if (quoted) throw Error('Invalid CSV: a quoted field is missing its closing quote.');
  if (value.length || record.length || afterQuote) endRecord();
  if (records.length < 2) throw Error('Add the column header and at least one data batch.');
  const headers = records.shift().map(item => item.trim());
  const required = ['period', 'passed', 'failed', 'response_ms'];
  if (new Set(headers).size !== headers.length) throw Error('CSV column names must be unique.');
  if (required.some(name => !headers.includes(name))) throw Error('Required CSV columns: period,passed,failed,response_ms.');
  if (headers.some(name => !required.includes(name))) throw Error('Use only these CSV columns: period,passed,failed,response_ms.');
  return records.map((fields, index) => {
    if (fields.length !== headers.length) throw Error(`Data batch ${index + 1} has ${fields.length} fields; expected ${headers.length}.`);
    const row = {};
    headers.forEach((name, column) => { row[name] = fields[column].trim(); });
    if (!row.period) throw Error(`Data batch ${index + 1} needs a period label.`);
    for (const name of ['passed', 'failed', 'response_ms']) {
      if (!row[name] || !Number.isFinite(Number(row[name]))) throw Error(`Data batch ${index + 1}: ${name} must be a finite number.`);
      row[name] = Number(row[name]);
      if (row[name] < 0) throw Error(`Data batch ${index + 1}: ${name} cannot be negative.`);
      if (name !== 'response_ms' && !Number.isSafeInteger(row[name])) throw Error(`Data batch ${index + 1}: ${name} must be a whole-number count.`);
    }
    if (row.passed + row.failed === 0) throw Error(`Data batch ${index + 1} must contain at least one check.`);
    return row;
  });
}

function updateDatasetSource(reset = true) {
  if (reset) {
    clearResult();
    $('dataset-error').hidden = true;
  }
  const choice = $('dataset-source').value, scale = $('dataset-scale').value;
  const own = choice === 'own', macro = scale === 'macro';
  $('csv-inputs').hidden = !own;
  $('csv-text').required = own;
  if (choice === 'demo') {
    $('scale-hint').textContent = `${macro ? 'Macro demo: 10,000' : 'Micro demo: 30'} synthetic batches. These are examples, not recorded measurements.`;
  } else if (choice === 'forevermart') {
    const stats = datasetManifest?.scales?.[scale];
    const sample = stats ? `${Number(stats.rows).toLocaleString()} batches, ${Number(stats.checks).toLocaleString()} recorded HTTP checks. ` : '';
    $('scale-hint').textContent = sample + (macro ? 'Wider sample across public website routes. Larger than the micro sample; not industrial big data.' : 'Focused sample of homepage checks. Quality assurance and quality control apply at both project scales.');
  } else {
    $('scale-hint').textContent = 'Use the smaller or larger dataset relevant to your project. Both scales accept up to 20,000 batches; the analysis method is the same.';
  }
  $('dataset-source-hint').textContent = own
    ? 'Your independent dataset has no textbook answer. Simulations check the fitted failure-count model and recorded weighted timing mean.'
    : choice === 'demo' ? 'Generated example data, not measurements from your website. The same fixed seed reproduces the demo.'
      : 'Recorded HTTP checks from ForeverMart. Timing includes network, TLS and response download; it does not measure browser rendering or prove complete software quality.';
  if (choice === 'forevermart' && datasetManifest) {
    const date = datasetManifest.captured_at_utc || datasetManifest.captured_at || datasetManifest.capture_date;
    if (date) $('dataset-source-hint').textContent += ` Captured: ${date}.`;
  }
}

function showResult(result) {
  if (typeof result.report_html !== 'string') throw Error('The server returned no report. Please try the calculation again.');
  window.QCReportViewer.render($('result-report'), result.report_html);
  lastResult = result;
  $('empty-result').hidden = true;
  $('result-content').hidden = false;
  $('data-message').textContent = result.message || 'Analysis complete.';
  $('data-message').className = 'data-message' + (result.category === 'book' ? ' book-data' : '');
  if (matchMedia('(max-width:850px)').matches) $('result-content').scrollIntoView({behavior: 'smooth', block: 'start'});
}

async function sendCalculation(payload, button, error, busy) {
  if (requestPending) return;
  error.hidden = true;
  clearResult();
  const body = JSON.stringify(payload);
  if (new TextEncoder().encode(body).length > maxBytes) throw Error('The request is larger than 2 MB. Please use fewer data batches or shorter period labels.');
  requestPending = true;
  const controls = [...document.querySelectorAll('.entry-panel input,.entry-panel select,.entry-panel textarea,.entry-panel button')];
  const disabledStates = controls.map(control => control.disabled);
  controls.forEach(control => { control.disabled = true; });
  busy.hidden = false;
  $('numerical-tab').disabled = $('dataset-tab').disabled = true;
  try {
    const response = await fetch('/api/calculate', {method: 'POST', headers: {'Content-Type': 'application/json'}, body});
    let result;
    try { result = await response.json(); } catch (_) { throw Error('The server returned an unreadable response. Check that the Python server is running, then try again.'); }
    if (!response.ok) throw Error(result.error || 'The calculation could not be completed.');
    showResult(result);
  } finally {
    requestPending = false;
    controls.forEach((control, index) => { control.disabled = disabledStates[index]; });
    busy.hidden = true;
    $('numerical-tab').disabled = $('dataset-tab').disabled = false;
  }
}

function saveDownload(content, filename, type) {
  const url = URL.createObjectURL(new Blob([content], {type}));
  const a = document.createElement('a');
  a.href = url; a.download = filename;
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

['numerical', 'dataset'].forEach(item => {
  $(item + '-tab').addEventListener('click', () => selectWorkflow(item));
  $(item + '-tab').addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    const next = event.key === 'Home' ? 'numerical' : event.key === 'End' ? 'dataset' : item === 'numerical' ? 'dataset' : 'numerical';
    selectWorkflow(next); $(next + '-tab').focus();
  });
});
dataSource.addEventListener('change', updateTypes);
kind.addEventListener('change', populateSources);
source.addEventListener('change', loadExercise);
mode.addEventListener('change', () => { clearResult(); renderFields(); });
$('reset-button').addEventListener('click', loadExercise);
$('load-book-values').addEventListener('click', () => { clearResult(); renderFields(loadedInputs); });
$('dataset-source').addEventListener('change', updateDatasetSource);
$('dataset-scale').addEventListener('change', updateDatasetSource);

form.addEventListener('submit', async event => {
  event.preventDefault();
  const error = $('form-error');
  error.hidden = true;
  try {
    if (!kind.value) throw Error('Choose a calculation type.');
    if (dataSource.value === 'book' && !source.value) throw Error('Select a book question for comparison.');
    await sendCalculation({kind: kind.value, data_source: dataSource.value, exercise_id: dataSource.value === 'book' ? source.value : '', inputs: collect(), trials: Number($('trials').value)}, $('calculate-button'), error, $('loading-message'));
  } catch (e) { error.textContent = e.message; error.hidden = false; }
});

$('dataset-form').addEventListener('submit', async event => {
  event.preventDefault();
  const error = $('dataset-error');
  error.hidden = true;
  try {
    const specification = Number($('specification-ms').value);
    if (!Number.isFinite(specification) || specification <= 0) throw Error('Enter a positive response time requirement in milliseconds.');
    const payload = {project_type: 'dataset', scale: $('dataset-scale').value, dataset_source: $('dataset-source').value, specification_ms: specification, trials: Number($('dataset-trials').value)};
    if (payload.dataset_source === 'own') payload.rows = parseCSV($('csv-text').value);
    await sendCalculation(payload, $('analyse-button'), error, $('dataset-loading'));
  } catch (e) { error.textContent = e.message; error.hidden = false; }
});

$('csv-file').addEventListener('change', async event => {
  const file = event.target.files[0];
  if (!file) return;
  $('dataset-error').hidden = true;
  try {
    if (file.size > maxBytes) throw Error('Choose a CSV file no larger than 2 MB.');
    const text = await file.text();
    const rows = parseCSV(text);
    $('csv-text').value = text;
    $('csv-file-status').textContent = `Imported ${file.name}: ${rows.length.toLocaleString()} batches. You can edit the values below.`;
    clearResult();
  } catch (e) { $('dataset-error').textContent = e.message; $('dataset-error').hidden = false; }
  finally { event.target.value = ''; }
});
$('csv-text').addEventListener('input', () => { $('csv-file-status').textContent = 'The CSV editor contains your current input values.'; });
$('download-template').addEventListener('click', () => saveDownload('period,passed,failed,response_ms\r\nBatch 1,98,2,245\r\nBatch 2,96,4,310\r\nBatch 3,99,1,280\r\n', 'software-testing-dataset-template.csv', 'text/csv;charset=utf-8'));
$('download-result').addEventListener('click', () => {
  if (!lastResult) return;
  const result = {...lastResult};
  delete result.report_html;
  saveDownload(JSON.stringify(result, null, 2), workflow === 'dataset' ? 'qc-dataset-analysis.json' : 'qc-calculation.json', 'application/json');
});
fetch('chapter10_inputs.json').then(response => {
  if (!response.ok) throw Error('Unable to load stored exercises. You can still use your own numerical values or the dataset workflow.');
  return response.json();
}).then(data => {
  if (!Array.isArray(data.cases)) throw Error('The exercise catalog has an invalid format.');
  cases = data.cases.filter(item => {
    const match = /^10-(\d+)(?:[a-z].*)?$/.exec(item.id);
    return match && Number(match[1]) >= 40 && Number(match[1]) <= 59;
  });
  catalogLoaded = true;
  updateTypes();
}).catch(e => {
  dataSource.value = 'own';
  updateTypes();
  $('form-error').textContent = e.message;
  $('form-error').hidden = false;
});
fetch('dataset_manifest.json').then(response => response.ok ? response.json() : null).then(manifest => {
  datasetManifest = manifest;
  updateDatasetSource(false);
}).catch(() => { /* The server still validates recorded-data availability on submit. */ });
updateDatasetSource();
