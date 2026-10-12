const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader'] });
  const files = process.argv.slice(2);
  const report = {};
  for (const f of files) {
    const pg = await b.newPage({ viewport: { width: 1280, height: 800 } });
    const errs = []; pg.on('pageerror', e => errs.push(e.message.slice(0, 160))); pg.on('console', m => { if (m.type() === 'error' && !/GL Driver|WebGL/.test(m.text())) errs.push('console: ' + m.text().slice(0, 160)); });
    try {
      await pg.goto('file://' + f, { timeout: 60000 }); await pg.waitForTimeout(2500);
      const n = await pg.evaluate(() => document.querySelectorAll('#tabs button').length || 1);
      const exps = [];
      for (let i = 0; i < n; i++) {
        if (i > 0) { await pg.evaluate(k => Lab.mount(k), i); await pg.waitForTimeout(1200); }
        const inv = await pg.evaluate(() => {
          const t = e => (e && e.textContent || '').replace(/\s+/g, ' ').trim();
          const g = document.querySelector('#guide'); if (g) g.querySelector('.go').click();
          Lab.step(10, 1 / 60);
          const secs = [...document.querySelectorAll('#controls .sec')].map(s => ({ h: t(s.querySelector('h2')), cls: s.className.replace('sec', '').trim(), folded: !!s.closest('details'),
            ctls: [...s.querySelectorAll('.ctl')].map(c => { const rg = c.querySelector('input[type=range]'); const cb = c.querySelector('input[type=checkbox]'); const se = c.querySelector('select'); const chips = c.querySelectorAll('.chip'); const btns = [...c.querySelectorAll('.btn')].map(t);
              return rg ? 'slider:' + t(c.querySelector('.lbl')) : cb ? 'toggle:' + t(c.querySelector('span')) : se ? 'select(' + se.options.length + '):' + t(c.querySelector('.lbl')) : chips.length ? 'chips(' + chips.length + '):' + t(c.querySelector('.lbl')) : btns.length ? 'buttons:' + btns.join(' | ') : 'other'; }) }));
          const reads = [...document.querySelectorAll('#reads .read .k')].map(t);
          const hero = t(document.querySelector('#hero .cap'));
          const drags = window.__activity && window.__activity.api ? null : null;
          const labels = [...document.querySelectorAll('.lab3.grab')].map(t);
          const stateKeys = Object.keys(window.__activity.state); const S = window.__activity.state; const st = {}; stateKeys.forEach(k => st[k] = S[k]); const handles = (window.__activity.api && window.__activity.api.pointerHandles ? window.__activity.api.pointerHandles() : []).map(h => h.kind + ':' + (h.obj && h.obj.name) + (h.opts && h.opts.hint ? ' «' + h.opts.hint + '»' : '') + (h.opts && h.opts.axis ? ' axis' : h.opts && h.opts.plane ? ' plane:' + h.opts.plane : ''));
          const stepsN = document.querySelectorAll('#controls .steps li').length, resetN = document.querySelectorAll('#controls .resetrow .btn').length, visBtns = [...document.querySelectorAll('#controls .btn')].filter(b => !b.hidden && !b.closest('[hidden]') && !b.closest('details:not([open])')).map(t); return { stepsN, resetN, visBtns, title: t(document.querySelector('#head h1')), secs, reads, hero, grabLabels: labels, stateKeys: st, handles, charts: document.querySelectorAll('#charts canvas').length, hasDemo: !!document.querySelector('#tb-demo'), toolbar: [...document.querySelectorAll('#toolbar>*')].map(e => e.id || t(e)) };
        });
        exps.push(inv);
      }
      report[f.replace(/.*\//, '')] = { n, errs, exps };
    } catch (e) { report[f.replace(/.*\//, '')] = { fatal: String(e).slice(0, 200), errs }; }
    await pg.close();
  }
  fs.writeFileSync(process.env.OUT || 'inventory.json', JSON.stringify(report, null, 1));
  for (const k in report) { const r = report[k]; console.log(k, r.fatal ? 'FATAL ' + r.fatal : ('exps=' + r.n + (r.errs.length ? ' ERRS=' + JSON.stringify(r.errs.slice(0, 2)) : ' ok'))); }
  await b.close();
})();
