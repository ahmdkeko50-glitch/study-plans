#!/usr/bin/env python3
"""Build a phone-friendly «video» edition of a lesson: one HTML file that opens on a recorded video of the guided demo,
with large synced captions, live readings and chapter buttons, and keeps every 3D script inert (never parsed or run)
until the student taps «جرّب التجربة التفاعليّة». The original lesson file is not modified.

  python3 make-video-page.py <lesson.html> <video.mp4> <poster.jpg> <timeline.json> <out.html> [--external NAME.mp4]

--external: reference the mp4 next to the html instead of embedding it (smaller html; both files must be shipped together).
"""
import base64, json, re, sys, html as H

args = [a for a in sys.argv[1:] if not a.startswith('--')]
ext = None
if '--external' in sys.argv: ext = sys.argv[sys.argv.index('--external') + 1]; args.remove(ext)
SRC, MP4, POSTER, TL, OUT = args[:5]
s = open(SRC, encoding='utf-8').read()
tl = json.load(open(TL, encoding='utf-8'))

meta = json.loads(re.search(r'window\.LAB_META = (\{.*?\});</script>', s).group(1))
content = {}
m = re.search(r'window\.LAB_CONTENT = (\{.*?\});</script>', s)
if m: content = json.loads(m.group(1))
lesson_js = s[s.index('<script>// @lesson'):]
title = re.search(r"\n  title: '((?:[^'\\]|\\.)*)',", lesson_js).group(1)
checks = re.findall(r"\{ q: '((?:[^'\\]|\\.)*)', a: '((?:[^'\\]|\\.)*)' \}", lesson_js)
pm = re.search(r"ctx\.predict\(\{.*?options: \[(.*?)\],\s*correct: (\d+)", lesson_js, re.S)
correct_text = ''
if pm:
    opts = re.findall(r"'((?:[^'\\]|\\.)*)'", pm.group(1)); correct_text = opts[int(pm.group(2))] if int(pm.group(2)) < len(opts) else ''
brand = re.search(r'<header class="brandbar">.*?</header>', s, re.S).group(0)

# 1) every script in <body> becomes inert until the student asks for the 3D lab
body_at = s.index('<body>')
head, body = s[:body_at], s[body_at:]
body = body.replace('<script>', '<script type="text/x-lab">')

poster = 'data:image/jpeg;base64,' + base64.b64encode(open(POSTER, 'rb').read()).decode()
vid_b64 = '' if ext else base64.b64encode(open(MP4, 'rb').read()).decode()
MIME = 'video/webm' if MP4.lower().endswith('.webm') else 'video/mp4'

learned = content.get('learned') or {}
learned_html = ''
if learned.get('points'):
    learned_html = '<details class="vcard"><summary>🧠 ماذا تعلّمنا؟</summary><ul>' + ''.join('<li>' + H.escape(p) + '</li>' for p in learned['points']) + '</ul>' + \
        ('<div class="vlaw ltr">' + H.escape(learned.get('law', '')) + '</div>' if learned.get('law') else '') + '</details>'
checks_html = ''
if checks:
    checks_html = '<section class="vcard vchecks"><h2>✅ تحقّق من فهمك</h2>' + ''.join(
        '<details class="q"><summary>' + q.replace("\\'", "'") + '</summary><div class="ans">' + a.replace("\\'", "'") + '</div></details>' for q, a in checks) + '</section>'

CSS = r'''<style>
#vpage{position:fixed;inset:0;z-index:200;overflow-y:auto;-webkit-overflow-scrolling:touch;background:var(--c-bg);font-family:var(--font);color:var(--c-ink)}
#vpage[hidden]{display:none}
#vpage .brandbar{position:sticky;top:0;z-index:3}
.vwrap{max-width:960px;margin:0 auto;padding:12px 12px calc(28px + env(safe-area-inset-bottom))}
.vtitle{font-size:18px;line-height:1.5;margin:4px 0 10px;color:var(--c-primary-dark);font-weight:800}
.vplayer{position:relative;background:#0d2a30;border-radius:14px;overflow:hidden;box-shadow:0 6px 22px rgba(4,40,46,.18)}
.vplayer video{display:block;width:100%;aspect-ratio:16/9;background:#0d2a30}
.vload{position:absolute;inset:0;display:grid;place-items:center;color:#fff;font-weight:700;background:rgba(13,42,48,.55);pointer-events:none}
.vload[hidden]{display:none}
#vask{position:absolute;inset:0;background:rgba(3,30,36,.88);color:#fff;display:flex;flex-direction:column;justify-content:center;gap:10px;padding:14px;text-align:center}
#vask[hidden]{display:none}
#vask .q{font-size:17px;font-weight:700;line-height:1.7}
#vask .opts{display:flex;flex-wrap:wrap;gap:8px;justify-content:center}
#vask button{min-height:46px;padding:8px 14px;border-radius:12px;border:1.5px solid #ffd166;background:rgba(255,209,102,.14);color:#fff;font:inherit;font-size:15.5px;font-weight:700;cursor:pointer}
#vask .skip{border-color:rgba(255,255,255,.35);background:transparent;font-weight:600;font-size:14px}
.vspeed{display:flex;align-items:center;gap:6px;margin-top:8px;font-size:13px;color:var(--c-ink-soft)}
.vspeed span{margin-inline-end:auto}
.vspeed button{min-width:54px;min-height:36px;border-radius:10px;border:1px solid var(--c-line);background:var(--c-paper);color:var(--c-ink);font:inherit;font-weight:700;cursor:pointer;touch-action:manipulation}
.vspeed button[aria-pressed="true"]{background:var(--c-primary);border-color:var(--c-primary);color:#fff}
.vcap{margin-top:8px;background:#0f3a42;color:#fff;border-radius:12px;padding:10px 14px;font-size:17px;line-height:1.85;font-weight:600;min-height:3.9em}
.vcap b{color:#ffd166}
.vcap .guess{display:block;margin-top:4px;font-size:14px;color:#bfe9ef;font-weight:600}
.vread{margin-top:10px;display:flex;gap:8px;overflow-x:auto;scrollbar-width:none;padding-bottom:2px}
.vread::-webkit-scrollbar{display:none}
.vread .hero,.vread .tile{flex:0 0 auto;background:var(--c-paper);border:1px solid var(--c-line);border-radius:12px;padding:6px 12px;min-width:120px}
.vread .hero{background:var(--c-tint-2);border-color:#bcd9b8}
.vread .k{font-size:12px;color:var(--c-ink-soft);white-space:nowrap}
.vread .v{direction:ltr;unicode-bidi:isolate;text-align:right;font-size:17px;font-weight:800;color:var(--c-primary-dark);white-space:nowrap}
.vread .hero .v{font-size:22px;color:#2f7a3c}
.vchap{margin-top:12px;display:flex;flex-wrap:wrap;gap:6px}
.vchap button{flex:1 1 auto;min-height:44px;padding:6px 10px;border-radius:11px;border:1px solid var(--c-line);background:var(--c-paper);color:var(--c-ink);font:inherit;font-size:13.5px;font-weight:600;cursor:pointer;touch-action:manipulation}
.vchap button .tm{display:block;font-size:11px;color:var(--c-ink-soft);font-weight:500}
.vchap button[aria-current="true"]{background:var(--c-primary);border-color:var(--c-primary);color:#fff}
.vchap button[aria-current="true"] .tm{color:#d6f0f3}
.vcard{margin-top:12px;background:var(--c-paper);border:1px solid var(--c-line);border-radius:14px;padding:10px 12px}
details.vcard>summary{cursor:pointer;font-weight:800;color:#2f6b47;min-height:36px;display:flex;align-items:center}
.vcard ul{margin:6px 0;padding-inline-start:20px;line-height:1.85;font-size:14.5px}
.vlaw{margin-top:6px;background:#f1faf3;border:1px dashed #9fcf9a;border-radius:10px;padding:8px;text-align:center;font-weight:700}
.vchecks h2{font-size:15px;margin:0 0 8px;color:var(--c-primary)}
.v3d{margin-top:16px;width:100%;min-height:52px;border-radius:14px;border:1.5px solid var(--c-primary);background:var(--c-tint);color:var(--c-primary-dark);font:inherit;font-size:16px;font-weight:800;cursor:pointer}
.v3d[disabled]{opacity:.5;cursor:default}
.vnote{font-size:12.5px;color:var(--c-ink-soft);text-align:center;margin:6px 0 0;line-height:1.7}
#vback{display:flex;align-items:center;justify-content:center;gap:6px;width:100%;min-height:42px;margin:0 0 10px;border-radius:11px;border:1px solid var(--c-line);background:var(--c-bg);color:var(--c-primary-dark);font:inherit;font-weight:700;cursor:pointer}
@media (min-width:900px){.vcap{font-size:18px}.vtitle{font-size:20px}}
</style>'''

chap_btns = ''.join('<button type="button" data-t="%s"><span>%s</span><span class="tm ltr">%d:%02d</span></button>' % (c['t'], H.escape(c['title']), int(c['t']) // 60, int(c['t']) % 60) for c in tl['chapters'])
PAGE = f'''<div id="vpage">
{brand}
<main class="vwrap">
  <h1 class="vtitle">{H.escape(title)}</h1>
  <div class="vplayer">
    <video id="vid" controls playsinline webkit-playsinline preload="auto" poster="{poster}"></video>
    <div class="vload" id="vload">جارٍ تجهيز الفيديو…</div>
    <div id="vask" hidden><div class="q"></div><div class="opts"></div><button type="button" class="skip">تخطَّ وتابع ▶</button></div>
  </div>
  <div class="vspeed" id="vspeed" role="group" aria-label="سرعة الفيديو"><span>السرعة</span><button type="button" data-r="1" aria-pressed="true">1×</button><button type="button" data-r="1.25">1.25×</button><button type="button" data-r="1.5">1.5×</button></div>
  <div class="vcap" id="vcap" aria-live="polite">▶ اضغط تشغيل لتشاهد التجربة خطوة بخطوة.</div>
  <div class="vread" id="vread"></div>
  <div class="vchap" id="vchap">{chap_btns}</div>
  {learned_html}
  {checks_html}
  <button type="button" class="v3d" id="v3d">🧪 جرّب التجربة التفاعليّة بنفسك (ثلاثيّة الأبعاد)</button>
  <p class="vnote" id="v3dnote">تعمل التجربة التفاعليّة جيّدًا على الحاسوب والأجهزة الحديثة. الفيديو يكفي لفهم الدرس على أيّ هاتف.</p>
</main>
</div>
<script type="application/json" id="vtl">{json.dumps(dict(tl, correct=correct_text), ensure_ascii=False).replace('</', '<\\/')}</script>
<script type="text/plain" id="vdata">{vid_b64}</script>
'''

JS = r'''<script>
(function () {
  const $ = s => document.querySelector(s);
  const TL = JSON.parse($('#vtl').textContent), page = $('#vpage'), v = $('#vid');
  const EXT = __EXT__, MIME = __MIME__;
  // ---------------- the 3D lab: inert until asked for ----------------
  let labOn = false;
  function startLab() {
    if (labOn) return; labOn = true; try { v.pause(); } catch (e) { }
    page.hidden = true;
    const back = document.createElement('button'); back.type = 'button'; back.id = 'vback'; back.textContent = '🎥 العودة إلى الفيديو';
    back.onclick = () => { location.hash = ''; location.reload(); };
    const pb = $('#panel-body'); if (pb) pb.prepend(back);
    document.querySelectorAll('script[type="text/x-lab"]').forEach(old => { const n = document.createElement('script'); n.textContent = old.textContent; old.replaceWith(n); });
  }
  $('#v3d').onclick = () => { location.hash = '3d'; startLab(); };
  // weak or unsupported devices: say so next to the button
  (function () {
    let gl = null; try { const c = document.createElement('canvas'); gl = c.getContext('webgl2') || c.getContext('webgl'); } catch (e) { }
    const note = $('#v3dnote'), btn = $('#v3d');
    if (!gl) { btn.disabled = true; note.textContent = 'جهازك لا يدعم العرض ثلاثيّ الأبعاد — الفيديو أعلاه يعرض التجربة كاملة.'; return; }
    const weak = (navigator.hardwareConcurrency || 8) <= 4 || (navigator.deviceMemory || 8) <= 3;
    if (weak) note.textContent = 'قد تكون التجربة التفاعليّة بطيئة على جهازك. الفيديو أعلاه يعرض التجربة كاملة ولا يُتعب الهاتف.';
  })();
  if (location.hash === '#3d') { startLab(); return; }

  // ---------------- video source (embedded → Blob URL so seeking works everywhere) ----------------
  const load = $('#vload');
  function setSrc(url) { v.src = url; v.addEventListener('loadeddata', () => { load.hidden = true; }, { once: true }); }
  if (EXT) setSrc(EXT);
  else {
    const b64 = $('#vdata').textContent.trim();
    const viaAtob = () => { const bin = atob(b64), u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return new Blob([u], { type: MIME }); };
    setTimeout(() => {
      (window.fetch ? fetch('data:' + MIME + ';base64,' + b64).then(r => r.blob()).catch(viaAtob) : Promise.resolve(viaAtob()))
        .then(blob => setSrc(URL.createObjectURL(blob))).catch(() => { load.textContent = 'تعذّر تشغيل الفيديو على هذا المتصفّح.'; });
    }, 30);
  }
  // fullscreen subtitles (WebVTT) built from the same captions
  const plain = h => { const d = document.createElement('div'); d.innerHTML = h.replace(/<br\s*\/?>/g, '\n'); return d.textContent.replace(/[ \t]+/g, ' ').trim(); };
  const ts = t => { const h = Math.floor(t / 3600), m = Math.floor(t / 60) % 60, s = (t % 60).toFixed(3).padStart(6, '0'); return String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0') + ':' + s; };
  let vtt = 'WEBVTT\n\n';
  TL.cues.forEach((c, i) => { const e = i + 1 < TL.cues.length ? TL.cues[i + 1].t : TL.duration; if (e > c.t) vtt += ts(c.t) + ' --> ' + ts(e) + '\n' + plain(c.html) + '\n\n'; });
  const tr = document.createElement('track'); tr.kind = 'subtitles'; tr.srclang = 'ar'; tr.label = 'العربية';
  tr.src = URL.createObjectURL(new Blob([vtt], { type: 'text/vtt' })); v.appendChild(tr);
  const fsSubs = on => { for (const t of v.textTracks) t.mode = on ? 'showing' : 'hidden'; };
  fsSubs(false);
  document.addEventListener('fullscreenchange', () => fsSubs(!!document.fullscreenElement));
  v.addEventListener('webkitbeginfullscreen', () => fsSubs(true)); v.addEventListener('webkitendfullscreen', () => fsSubs(false));

  // ---------------- synced captions, readings, chapters, questions ----------------
  const cap = $('#vcap'), rd = $('#vread'), chBtns = [...document.querySelectorAll('#vchap button')], ask = $('#vask');
  const last = (arr, t) => { let lo = 0, hi = arr.length - 1, k = -1; while (lo <= hi) { const m = (lo + hi) >> 1; if (arr[m].t <= t + 1e-3) { k = m; lo = m + 1; } else hi = m - 1; } return k; };
  let guess = null, answered = new Set(), curCue = -2, curRead = -2, curCh = -2;
  const esc = s => String(s).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' })[c]);
  // the verdict is shown in the «النتيجة» chapter after the question (or the chapter right after it)
  const askCue = TL.cues.find(c => c.ask), askCh = askCue ? last(TL.chapters, askCue.t) : -1;
  let verdictCh = TL.chapters.findIndex((c, i) => i > askCh && /النتيجة/.test(c.title)); if (verdictCh < 0) verdictCh = askCh + 1;
  function verdictFor() {
    if (guess == null || !TL.correct) return '';
    const ok = TL.correct.slice(0, 6) && guess.slice(0, 6) === TL.correct.slice(0, 6);
    return ok ? '✓ <b>توقّعك صحيح!</b>' : '✗ توقّعت «' + esc(guess) + '» — قارنه بالنتيجة.';
  }
  function draw() {
    const t = v.currentTime;
    const ci = last(TL.cues, t);
    if (ci !== curCue) { curCue = ci; const c = TL.cues[ci];
      let h = c ? c.html.replace(/^🤔\s*/, '🤔 ') : '▶ اضغط تشغيل لتشاهد التجربة خطوة بخطوة.';
      if (c && guess != null && !c.ask) h += '<span class="guess">' + (last(TL.chapters, c.t) === verdictCh ? verdictFor() : 'توقّعك: «' + esc(guess) + '»') + '</span>';
      cap.innerHTML = h;
      if (c && c.ask && !answered.has(ci) && !v.paused) showAsk(ci, c);
    }
    const ri = last(TL.reads, t);
    if (ri !== curRead) { curRead = ri; const r = TL.reads[ri];
      if (!r) rd.innerHTML = '';
      else { let h = r.cap ? '<div class="hero"><div class="k">' + esc(r.cap) + '</div><div class="v ltr">' + esc(r.val) + '</div></div>' : '';
        Object.keys(r.r || {}).forEach(k => { if (k === r.cap) return; h += '<div class="tile"><div class="k">' + esc(k) + '</div><div class="v">' + esc(r.r[k]) + '</div></div>'; });
        rd.innerHTML = h; } }
    const hi = last(TL.chapters, t);
    if (hi !== curCh) { curCh = hi; chBtns.forEach((b, i) => b.setAttribute('aria-current', i === hi)); }
  }
  function showAsk(i, c) {
    v.pause(); answered.add(i);
    ask.querySelector('.q').innerHTML = c.html;
    const o = ask.querySelector('.opts'); o.innerHTML = '';
    (c.opts || []).forEach(t => { const b = document.createElement('button'); b.type = 'button'; b.textContent = t; b.onclick = () => { guess = t; closeAsk(); }; o.appendChild(b); });
    ask.hidden = false;
  }
  function closeAsk() { ask.hidden = true; curCue = -2; draw(); v.play().catch(() => { }); }
  ask.querySelector('.skip').onclick = closeAsk;
  chBtns.forEach(b => b.onclick = () => { ask.hidden = true; v.currentTime = +b.dataset.t + 0.05; v.play().catch(() => { }); });
  v.addEventListener('seeking', () => { ask.hidden = true; const t = v.currentTime; TL.cues.forEach((c, i) => { if (c.ask && c.t >= t - 0.05) answered.delete(i); }); draw(); });
  // a cheap rAF loop only while playing (precise pause at a question); timeupdate as fallback
  let raf = 0; const tick = () => { draw(); if (!v.paused && !v.ended) raf = requestAnimationFrame(tick); };
  v.addEventListener('play', () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(tick); });
  v.addEventListener('timeupdate', draw); v.addEventListener('pause', draw);
  v.addEventListener('ended', () => { cap.innerHTML = '🎬 انتهى الفيديو. أجب عن «تحقّق من فهمك» أدناه، أو جرّب التجربة التفاعليّة بنفسك.'; });
  // playback speed (remembered)
  const sp = [...document.querySelectorAll('#vspeed button')];
  const setRate = r => { v.playbackRate = r; v.defaultPlaybackRate = r; sp.forEach(b => b.setAttribute('aria-pressed', +b.dataset.r === r)); try { localStorage.setItem('vlab:rate', String(r)); } catch (e) { } };
  sp.forEach(b => b.onclick = () => setRate(+b.dataset.r));
  try { const r = +localStorage.getItem('vlab:rate'); if (r >= 1 && r <= 1.5) setRate(r); } catch (e) { }
  v.addEventListener('loadeddata', () => { v.playbackRate = v.defaultPlaybackRate; });
  draw();
})();
</script>'''.replace('__EXT__', json.dumps(ext)).replace('__MIME__', json.dumps(MIME))

body = body.replace('<body>', '<body>\n' + CSS + '\n' + PAGE, 1)
body = body.replace('</body>', JS + '\n</body>', 1)
s2 = head + body
s2 = s2.replace('<title>', '<title>🎥 ', 1)
open(OUT, 'w', encoding='utf-8').write(s2)
print(OUT, round(len(s2) / 1048576, 2), 'MB', '| chapters', len(tl['chapters']), '| cues', len(tl['cues']), '| checks', len(checks), '| correct', correct_text)
