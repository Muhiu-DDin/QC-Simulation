'use strict';

// Render server-generated reports in the page. Shadow DOM keeps the report's
// styles separate from the input form without a second iframe navigation.
(() => {
  const allowedTags = new Set(('MAIN HEADER FOOTER SECTION ARTICLE ASIDE NAV DIV SPAN P ' +
    'H1 H2 H3 H4 H5 H6 TABLE THEAD TBODY TFOOT TR TH TD COLGROUP COL UL OL LI DL DT DD ' +
    'STRONG EM B I SMALL CODE PRE BR HR IMG A DETAILS SUMMARY').split(' '));
  const allowedAttributes = new Set(('class id title role hidden open colspan rowspan scope ' +
    'alt width height loading href src download target rel').split(' '));

  function safeURL(value, image = false) {
    const url = value.trim();
    if (/^data:image\/png;base64,[A-Za-z0-9+/=\s]+$/i.test(url)) return true;
    if (image) return false;
    return url.startsWith('#') || /^https:\/\//i.test(url);
  }

  function render(host, html) {
    if (typeof html !== 'string' || !html.trim()) throw Error('The server returned an empty report. Please try again.');
    const parsed = new DOMParser().parseFromString(html, 'text/html');
    if (!parsed.body.querySelector('main') || !parsed.body.textContent.trim()) {
      throw Error('The server returned an incomplete report. Please try again.');
    }

    // Navigation belongs to the workspace. Report content needs no scripts,
    // event-handler attributes, external images, or nested embedded documents.
    parsed.body.querySelectorAll('.topbar,.report-heading,.overview,footer,.subtle-link').forEach(node => node.remove());
    for (const node of parsed.body.querySelectorAll('*')) {
      if (!allowedTags.has(node.tagName)) { node.remove(); continue; }
      for (const attribute of [...node.attributes]) {
        const name = attribute.name.toLowerCase();
        if (!allowedAttributes.has(name) && !name.startsWith('aria-')) node.removeAttribute(attribute.name);
      }
      if (node.hasAttribute('href') && !safeURL(node.getAttribute('href'))) node.removeAttribute('href');
      if (node.hasAttribute('src') && !safeURL(node.getAttribute('src'), true)) node.removeAttribute('src');
      if (node.tagName === 'A' && node.getAttribute('target') === '_blank') node.setAttribute('rel', 'noopener noreferrer');
    }

    const style = document.createElement('style');
    style.textContent = [...parsed.head.querySelectorAll('style')].map(node => node.textContent
      .replace(/:root\b/g, ':host')
      // Match the body selector without changing selectors such as "tbody".
      .replace(/(^|[\s,}])body(?=[\s.{:#\[])/g, '$1.report-document')).join('\n') +
      '\n:host{display:block;min-width:0;--ink:#292c34;--red:#bd3039;--line:#dce0e5}' +
      '.report-document{min-height:0!important;margin:0!important}' +
      'main{padding:16px!important;max-width:none!important}' +
      '.exercise{padding:20px!important;margin:0 0 16px!important}' +
      '.workspace{display:block!important}.panel-heading{align-items:flex-start}' +
      '.panel-heading p{max-width:240px}img{max-width:100%;height:auto}' +
      'table{overflow-wrap:anywhere}@media(max-width:600px){main{padding:10px!important}}';
    const content = document.createElement('div');
    content.className = 'report-document';
    content.append(...[...parsed.body.childNodes].map(node => document.importNode(node, true)));
    const root = host.shadowRoot || host.attachShadow({mode: 'open'});
    root.replaceChildren(style, content);
  }

  function clear(host) {
    host.shadowRoot?.replaceChildren();
  }

  window.QCReportViewer = {render, clear};
})();
