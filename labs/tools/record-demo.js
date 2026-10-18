// Records a lesson's guided demo («شاهد المحاكاة») into JPEG frames with a virtual clock, so every frame is exact
// even on a slow software GPU. Usage:
//   node record-demo.js <lesson.html> <out-frames-dir> [width height fps pace dpr tab]
// tab: which experiment (0-based) of a lesson with several «التجربة» tabs
// width/height are the CSS layout size; dpr multiplies the rendered pixels (1024×576 at dpr 1.875 = 1920×1080 frames)
// pace: the demo's own pacing factor (the lab uses 1.35 = slow for live viewing; 1 = brisker video)
// Writes frames f00000.jpg … and timeline.json: chapters [{t,title}], cues [{t,html,ask?,opts?}], reads [{t,cap,val,sub,r:{label:value}}].
// DRY=1: no screenshots (only timeline.json, in seconds; used to read the captions before the real recording).
// Captions are NOT burned into the frames: the video page shows them as large text (and as WebVTT subtitles in fullscreen). Encode with ffmpeg afterwards (see LAB_VIDEO.md).
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [, , SRC, OUT, W = '1024', H = '576', FPS = '24', PACE = '1', DPR = '1.875', TAB = '0'] = process.argv;
const w = +W, h = +H, fps = +FPS, dt = 1000 / fps;
fs.mkdirSync(OUT, { recursive: true });
// a temporary copy with the requested demo pace (the lesson file itself is never changed)
const TMP = path.join(OUT, '_lesson.html');
fs.writeFileSync(TMP, fs.readFileSync(SRC, 'utf8').replace(/DEMO_PACE = [0-9.]+/, 'DEMO_PACE = ' + (+PACE)).replace('govMs > 25', 'govMs > 1e9').replace('antialias: true', process.env.NOAA ? 'antialias: false' : 'antialias: true'));   // and keep full quality (the auto-quality governor would read the fixed frame step as a slow device)
const CLOCK = `(() => {
  let vt = 0; const T0 = Date.now(); let rafQ = [], rafId = 0, timers = [], tId = 0;
  performance.now = () => vt; Date.now = () => T0 + vt;
  window.requestAnimationFrame = cb => { rafQ.push({ id: ++rafId, cb }); return rafId; };
  window.cancelAnimationFrame = id => { rafQ = rafQ.filter(r => r.id !== id); };
  const add = (cb, ms, args, rep) => { timers.push({ id: ++tId, at: vt + Math.max(0, +ms || 0), cb, args, rep: rep ? Math.max(1, +ms || 0) : 0 }); return tId; };
  window.setTimeout = (cb, ms, ...a) => add(cb, ms, a, false); window.setInterval = (cb, ms, ...a) => add(cb, ms, a, true);
  window.clearTimeout = window.clearInterval = id => { timers = timers.filter(t => t.id !== id); };
  const anims = new WeakMap();
  window.__adv = ms => {
    const end = vt + ms;
    for (;;) { timers.sort((a, b) => a.at - b.at); const t = timers[0]; if (!t || t.at > end) break; vt = Math.max(vt, t.at);
      if (t.rep) t.at += t.rep; else timers.shift(); try { typeof t.cb === 'function' ? t.cb(...t.args) : eval(t.cb); } catch (e) { console.error(e); } }
    vt = end; const q = rafQ; rafQ = []; q.forEach(r => { try { r.cb(vt); } catch (e) { console.error(e); } });
    // CSS / Web Animations follow the virtual clock too
    document.getAnimations().forEach(a => { let s = anims.get(a); if (!s) { s = { t: +a.currentTime || 0 }; anims.set(a, s); try { a.pause(); } catch (e) { } } s.t += ms; try { a.currentTime = s.t; } catch (e) { } });
    return vt;
  };
  try { localStorage.setItem('phys3d:guide:' + ((window.LAB_META || {}).code || ''), '1'); } catch (e) { }
})();`;
const STYLE = `#panel,#split,#navpad,#toolbar,#tb-menu,#flash,#democta,#demo{display:none!important}
#app{padding:0!important} #demo{inset-inline:22px;bottom:18px} #demo .dbox{width:min(900px,100%)} #demo .dsay{font-size:21px;line-height:1.7}
#demo .dask button{pointer-events:none} .vthink{display:block;margin-top:6px;font-size:15px;color:#ffd166;font-weight:700}`;
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--disable-background-timer-throttling'] });
  const ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: +DPR });
  await ctx.addInitScript(CLOCK);
  const pg = await ctx.newPage(); pg.on('pageerror', e => console.error('pageerror', e.message));
  await pg.goto('file://' + path.resolve(TMP));
  await pg.addStyleTag({ content: STYLE });
  await pg.evaluate(() => { try { localStorage.setItem('phys3d:guide:' + (window.LAB_META.code || ''), '1'); } catch (e) { } const g = document.querySelector('#guide'); if (g) g.remove(); });
  if (process.env.DRY) await pg.evaluate(() => { const r = window.__activity.api.renderer; r.render = () => { }; });   // captions only: skip drawing
  if (+TAB > 0) { await pg.evaluate(k => { const g = document.querySelector('#guide'); if (g) g.remove(); Lab.mount(k); }, +TAB); }
  await pg.evaluate(ms => { for (let i = 0; i < 90; i++) window.__adv(ms); }, dt);   // opening camera move, settle
  await pg.evaluate(() => { const g = document.querySelector('#guide'); if (g) g.remove(); document.querySelector('#tb-demo').click(); });
  const chapters = [], cues = [], reads = []; let f = 0, lastCh = '', lastSay = '', askAt = -1, endAt = -1, lastRead = '';
  const MAX = fps * 600;
  while (f < MAX) {
    const s = await pg.evaluate(ms => { window.__adv(ms); const q = e => document.querySelector(e), t = e => (e && e.textContent || '').replace(/\s+/g, ' ').trim();
      const ch = q('#demo .ch'), ask = q('#demo .dask'), say = q('#demo .dsay');
      const r = {}; document.querySelectorAll('#reads .read').forEach(x => { const k = t(x.querySelector('.k')), v = t(x.querySelector('.v')); if (k && v) r[k] = v; });
      const h = q('#hero');
      return { ch: t(ch), ask: ask ? [...ask.querySelectorAll('button')].map(t) : null, say: say ? say.innerHTML : '', end: !!(ch && /انتهت/.test(ch.textContent)),
        hero: h && !h.hidden ? { cap: t(h.querySelector('.cap')), val: t(h.querySelector('.val')), sub: t(h.querySelector('.sub')) } : null, r }; }, dt);
    const T = +(f / fps).toFixed(2);
    if (s.ch && s.ch !== lastCh && !s.end) { lastCh = s.ch; chapters.push({ t: T, title: s.ch.replace(/^.*·\s*/, '') }); }
    const sayKey = s.say + (s.ask ? '|ask' : '');
    if (s.say && sayKey !== lastSay) { lastSay = sayKey; cues.push(Object.assign({ t: T, html: s.say }, s.ask ? { ask: true, opts: s.ask } : {}, s.end ? { end: true } : {})); }
    const rk = JSON.stringify([s.hero, s.r]);
    if (f % 3 === 0 && rk !== lastRead) { lastRead = rk; reads.push(Object.assign({ t: T, r: s.r }, s.hero || {})); }
    if (s.ask && askAt < 0) askAt = f;
    if (s.ask && f - askAt > fps * 3) { await pg.evaluate(() => document.querySelector('#demo .nx').click()); askAt = -1; }   // the page pauses here and asks the student
    if (!s.ask) askAt = -1;
    if (s.end && endAt < 0) endAt = f;
    if (!process.env.DRY) await pg.screenshot({ path: path.join(OUT, 'f' + String(f).padStart(5, '0') + '.jpg'), type: 'jpeg', quality: 93 });
    f++;
    if (endAt >= 0 && f - endAt > fps * 4) break;
    if (f % (fps * 10) === 0) console.log('t =', f / fps, 's', lastCh);
  }
  fs.unlinkSync(TMP);
  const tabTitle = await pg.evaluate(() => { const b = document.querySelectorAll('#tabs button'), h = document.querySelector('#head h1'); const a = [...b].find(x => x.getAttribute('aria-selected') === 'true'); return ((a || {}).textContent || (h || {}).textContent || '').replace(/\s+/g, ' ').trim(); });
  fs.writeFileSync(path.join(OUT, 'timeline.json'), JSON.stringify({ fps, frames: f, tab: +TAB, title: tabTitle, duration: +(f / fps).toFixed(2), chapters, cues, reads }));
  fs.writeFileSync(path.join(OUT, 'chapters.json'), JSON.stringify(chapters, null, 1));
  console.log('frames', f, 'duration', (f / fps).toFixed(1), 's', 'chapters', chapters.length, 'cues', cues.length, 'reads', reads.length);
  await b.close();
})();
