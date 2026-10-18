// Clicks every control of every lesson and reports page errors and controls that change nothing.
//   OUT=buttons.json node button-test.js ../L*.html
// For each experiment (tab): every visible or folded button, slider (min → max), toggle, chip, select option,
// tappable ✋ label, prediction option, quiz answer, toolbar and ⋯ menu item, nav-pad button, then the reset button
// (state must return to the start). "no effect" = state, readings, hero and panel text identical before and after.
const { chromium } = require('playwright');
const fs = require('fs');
const SNAP = () => {
  const t = e => (e && e.textContent || '').replace(/\s+/g, ' ').trim();
  const S = (window.__activity && window.__activity.state) || {};
  const st = {}; Object.keys(S).forEach(k => { const v = S[k]; if (typeof v !== 'function' && typeof v !== 'object') st[k] = v; });
  const cam = window.__activity && window.__activity.api && window.__activity.api.camera;
  return JSON.stringify({ st, reads: [...document.querySelectorAll('#reads .read .v')].map(t), hero: t(document.querySelector('#hero')),
    steps: [...document.querySelectorAll('#controls .steps li')].map(l => l.className), ui: t(document.querySelector('#panel')).length,
    cls: document.body.className + '|' + document.documentElement.className + '|' + JSON.stringify(document.documentElement.dataset) + JSON.stringify(document.body.dataset),
    app: (document.querySelector('#app') || document.body).className + (document.querySelector('#panel') || {}).offsetWidth,
    vis: (() => { let n = 0; const sc = window.__activity && window.__activity.api && window.__activity.api.scene; const walk = o => { if (!o.visible) return; n++; (o.children || []).forEach(walk); }; try { (window.__labScene || sc) && walk(window.__labScene || sc); } catch (e) { } return n; })(),
    lab3: [...document.querySelectorAll('.lab3')].filter(e => e.offsetParent && getComputedStyle(e).visibility !== 'hidden' && getComputedStyle(e).opacity !== '0').length,
    modal: [...document.querySelectorAll('.modal, #help, dialog, #tb-menu')].map(e => !e.hidden).join(''), hidden: [...document.querySelectorAll('#panel [hidden], #stage [hidden], #flash, #demo, #tb-menu, .lab3')].map(e => e.hidden + (e.style.display || '')).join(''),
    cam: cam ? [cam.position.x, cam.position.y, cam.position.z].map(v => v.toFixed(2)).join() : '' });
};
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader'] });
  const files = process.argv.slice(2), report = {};
  for (const f of files) {
    const name = f.replace(/.*\//, '');
    const pg = await b.newPage({ viewport: { width: 900, height: 600 } });
    const errs = []; pg.on('pageerror', e => errs.push(e.message.slice(0, 200)));
    pg.on('console', m => { if (m.type() === 'error' && !/GL Driver|WebGL|GPU stall/.test(m.text())) errs.push('console: ' + m.text().slice(0, 200)); });
    pg.on('dialog', d => d.dismiss());
    const res = { exps: [], errs };
    try {
      await pg.goto('file://' + require('path').resolve(f), { timeout: 60000 }); await pg.waitForTimeout(2000);
      await pg.evaluate(() => { const g = document.querySelector('#guide'); if (g) { const go = g.querySelector('.go'); go ? go.click() : g.remove(); } });
      const n = await pg.evaluate(() => document.querySelectorAll('#tabs button').length || 1);
      const settle = async () => { await pg.evaluate(() => { try { Lab.step(8, 1 / 15); } catch (e) { } }); await pg.waitForTimeout(120); };
      for (let i = 0; i < n; i++) {
        if (i > 0) { await pg.evaluate(k => document.querySelectorAll('#tabs button')[k].click(), i); await pg.waitForTimeout(1200); }
        const exp = { tab: i, tested: 0, noEffect: [], failed: [], reset: '' };
        await pg.evaluate(() => document.querySelectorAll('#controls details').forEach(d => d.open = true));
        await settle();
        const start = await pg.evaluate(SNAP);
        // enumerate targets
        const targets = await pg.evaluate(() => {
          const t = e => (e && e.textContent || '').replace(/\s+/g, ' ').trim(), out = [];
          const vis = e => !e.closest('[hidden]') && !e.hidden && getComputedStyle(e).display !== 'none';
          document.querySelectorAll('#controls .ctl').forEach((c, ci) => {
            if (!vis(c)) return; const lbl = t(c.querySelector('.lbl')) || t(c).slice(0, 30);
            c.querySelectorAll('input[type=range]').forEach(() => out.push({ k: 'range', ci, lbl }));
            c.querySelectorAll('input[type=checkbox]').forEach(() => out.push({ k: 'check', ci, lbl }));
            c.querySelectorAll('select').forEach(s => [...s.options].forEach((o, oi) => out.push({ k: 'select', ci, oi, lbl: lbl + ' → ' + t(o) })));
            c.querySelectorAll('.chip').forEach((h, hi) => out.push({ k: 'chip', ci, hi, lbl: lbl + ' → ' + t(h) }));
          });
          document.querySelectorAll('#controls .btn').forEach((e, bi) => { if (vis(e) && !e.closest('.resetrow')) out.push({ k: 'btn', bi, lbl: t(e) }); });
          document.querySelectorAll('#predict button, .predict button, #panel .pred button').forEach((e, pi) => { if (vis(e)) out.push({ k: 'pred', pi, lbl: 'توقّع: ' + t(e) }); });
          return out;
        });
        for (const tg of targets) {
          const before = await pg.evaluate(SNAP);
          let ok = true;
          try {
            await pg.evaluate(tg => {
              const c = document.querySelectorAll('#controls .ctl')[tg.ci];
              if (tg.k === 'range') { const r = c.querySelector('input[type=range]'); const set = v => { r.value = v; r.dispatchEvent(new Event('input', { bubbles: true })); r.dispatchEvent(new Event('change', { bubbles: true })); };
                set(+r.value >= (+r.max + +r.min) / 2 ? r.min : r.max); }
              else if (tg.k === 'check') c.querySelector('input[type=checkbox]').click();
              else if (tg.k === 'select') { const s = c.querySelector('select'); if (s.selectedIndex === tg.oi) return; s.selectedIndex = tg.oi; s.dispatchEvent(new Event('change', { bubbles: true })); }
              else if (tg.k === 'chip') c.querySelectorAll('.chip')[tg.hi].click();
              else if (tg.k === 'btn') document.querySelectorAll('#controls .btn')[tg.bi].click();
              else if (tg.k === 'pred') document.querySelectorAll('#predict button, .predict button, #panel .pred button')[tg.pi].click();
            }, tg);
          } catch (e) { ok = false; exp.failed.push(tg.lbl + ' : ' + String(e).slice(0, 120)); }
          if (tg.k === 'pred') exp.predDone = (exp.predDone || 0) + 1;
          await settle(); await pg.waitForTimeout(tg.k === 'btn' ? 1400 : 150); await settle();
          const after = await pg.evaluate(SNAP); exp.tested++;
          if (ok && after === before && !(tg.k === 'chip' && /aria-pressed/.test(''))) {
            // a chip / select option that is already selected legitimately changes nothing
            const already = await pg.evaluate(tg => { const c = document.querySelectorAll('#controls .ctl')[tg.ci]; if (tg.k === 'chip') { const h = c.querySelectorAll('.chip')[tg.hi]; return h.getAttribute('aria-pressed') === 'true' || h.classList.contains('on'); } if (tg.k === 'select') return true; return false; }, tg);
            if (!already && !(tg.k === 'pred' && exp.predDone > 1)) exp.noEffect.push(tg.k + ' «' + tg.lbl + '»');
          }
        }
        // tappable 3D labels
        const taps = await pg.evaluate(() => [...document.querySelectorAll('.lab3.grab.tap')].map(e => (e.textContent || '').trim()));
        for (let k = 0; k < taps.length; k++) {
          const before = await pg.evaluate(SNAP);
          await pg.evaluate(k => { const e = document.querySelectorAll('.lab3.grab.tap')[k]; e && e.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true })); e && e.dispatchEvent(new PointerEvent('pointerup', { bubbles: true })); e && e.click(); }, k);
          await settle(); await pg.waitForTimeout(900); await settle(); exp.tested++;
          if (await pg.evaluate(SNAP) === before) exp.noEffect.push('✋ «' + taps[k] + '»');
        }
        // quiz (③ تحقّق): click the first option of every question
        const quiz = await pg.evaluate(() => { let n = 0; document.querySelectorAll('#checks .q, .checks .q, #panel .quiz .q').forEach(q => { const o = q.querySelector('button'); if (o) { o.click(); n++; } }); return n; });
        exp.tested += quiz; exp.quiz = quiz;
        // reset → back to the start state
        const rb = await pg.evaluate(() => { const r = [...document.querySelectorAll('#controls .resetrow .btn')]; r.forEach(x => x.click()); return r.length; });
        await settle(); await pg.waitForTimeout(600); await settle();
        const st0 = JSON.parse(start).st, st1 = JSON.parse(await pg.evaluate(SNAP)).st;
        const diff = Object.keys(st0).filter(k => typeof st0[k] !== 'number' ? st0[k] !== st1[k] : Math.abs(st0[k] - st1[k]) > 1e-6 * Math.max(1, Math.abs(st0[k])));
        exp.reset = rb ? (diff.length ? 'differs: ' + diff.slice(0, 6).join(',') : 'ok') : 'NO RESET BUTTON';
        exp.resetDiff = diff.map(k => k + ' ' + st0[k] + '→' + st1[k]).slice(0, 6);
        res.exps.push(exp);
      }
      // toolbar, ⋯ menu, nav pad (once per lesson)
      const tb = { noEffect: [] };
      const tbt = await pg.evaluate(() => [...document.querySelectorAll('#toolbar button, #navpad button')].filter(e => !e.hidden && getComputedStyle(e).display !== 'none').map(e => e.id || (e.title || e.textContent).trim()));
      for (const id of tbt) {
        const before = await pg.evaluate(SNAP);
        await pg.evaluate(id => { const e = document.getElementById(id) || [...document.querySelectorAll('#toolbar button, #navpad button')].find(x => (x.title || x.textContent).trim() === id); e && e.click(); }, id);
        await pg.waitForTimeout(700); await settle();
        if (await pg.evaluate(SNAP) === before) tb.noEffect.push(id);
        await pg.evaluate(() => { try { Lab.stopDemo && Lab.stopDemo(); } catch (e) { } const m = document.querySelector('#tb-menu'); if (m) m.hidden = true; document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' })); });
        await pg.waitForTimeout(200);
      }
      const menu = await pg.evaluate(() => [...document.querySelectorAll('#tb-menu button')].map(e => (e.textContent || '').trim()));
      for (let k = 0; k < menu.length; k++) {
        await pg.evaluate(() => { const m = document.querySelector('#tb-more, #tb-menu-btn, [aria-controls="tb-menu"]'); m && m.click(); });
        await pg.waitForTimeout(150); const before = await pg.evaluate(SNAP);
        await pg.evaluate(k => document.querySelectorAll('#tb-menu button')[k].click(), k);
        await pg.waitForTimeout(700); await settle();
        if (await pg.evaluate(SNAP) === before) tb.noEffect.push('⋯ ' + menu[k]);
        await pg.evaluate(() => { try { Lab.stopDemo && Lab.stopDemo(); } catch (e) { } document.querySelectorAll('.modal, #help').forEach(m => m.hidden = true); document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' })); });
      }
      tb.toolbar = tbt; tb.menu = menu; res.toolbar = tb;
      // video copy: open, play, close
      if (await pg.evaluate(() => !!window.openLabVideo)) {
        res.video = await pg.evaluate(async () => { openLabVideo(); await new Promise(r => setTimeout(r, 1500)); const open = !document.querySelector('#vlayer').hidden && window.__labHold === true;
          document.querySelector('#vclose').click(); return open && !window.__labHold && document.querySelector('#vlayer').hidden ? 'ok' : 'FAIL'; });
      }
    } catch (e) { res.fatal = String(e).slice(0, 300); }
    report[name] = res; await pg.close();
    const p = res.exps.map(e => `tab${e.tab}: ${e.tested} tested, noEffect ${e.noEffect.length}, reset ${e.reset}`).join(' | ');
    console.log(name, res.fatal ? 'FATAL ' + res.fatal : p, errs.length ? 'ERRS ' + errs.length : '', res.toolbar && res.toolbar.noEffect.length ? 'toolbar-noEffect ' + res.toolbar.noEffect.join(',') : '', res.video ? 'video ' + res.video : '');
  }
  fs.writeFileSync(process.env.OUT || 'buttons.json', JSON.stringify(report, null, 1));
  await b.close();
})();
