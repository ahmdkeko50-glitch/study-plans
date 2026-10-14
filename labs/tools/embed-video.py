#!/usr/bin/env python3
"""Put a recorded video of the guided demo INSIDE a copy of the 3D lesson.

The copy is the same interactive lab, plus a video player that opens over it from
  • the toolbar button «🎬 شاهد الفيديو» (it replaces the live «شاهد المحاكاة» demo, which is heavy on weak phones),
  • a button at the top of the panel, and the guide's «شاهد الفيديو أوّلًا»,
  • automatically, on devices without WebGL.
While the video is open the 3D rendering is paused, so the phone only decodes video.
Captions and live readings are shown as large text synced to the video; the video pauses at the prediction question.

  python3 embed-video.py <lesson.html> <video.mp4> <poster.jpg> <timeline.json> <out.html>
"""
import base64, json, re, sys, html as H

SRC, MP4, POSTER, TL, OUT = sys.argv[1:6]
s = open(SRC, encoding='utf-8').read()
tl = json.load(open(TL, encoding='utf-8'))
lesson_js = s[s.index('<script>// @lesson'):]
pm = re.search(r"ctx\.predict\(\{.*?options: \[(.*?)\],\s*correct: (\d+)", lesson_js, re.S)
correct_text = ''
if pm:
    opts = re.findall(r"'((?:[^'\\]|\\.)*)'", pm.group(1)); k = int(pm.group(2)); correct_text = opts[k] if k < len(opts) else ''

def rep(a, b, count=1):
    global s
    assert s.count(a) == count, ('patch target not found', a[:80], s.count(a))
    s = s.replace(a, b)

# ---- engine patches (this copy only) ----
rep("const db = btn('🎬', 'شاهد المحاكاة', 'شاهد التجربة تعمل وحدها مع الشرح، مثل فيديو قصير', playDemo);",
    "const db = btn('🎬', 'شاهد الفيديو', 'شاهد التجربة فيديو مع الشرح (لا يُتعب الهاتف)', () => window.openLabVideo ? openLabVideo() : playDemo());")
rep("(cur.demo ? '<button type=\"button\" class=\"watch\">🎬 شاهد المحاكاة أوّلًا</button>' : '')",
    "(cur.demo ? '<button type=\"button\" class=\"watch\">🎬 شاهد الفيديو أوّلًا</button>' : '')")
i = s.index("const wb = g.querySelector('.watch');"); j = s.index('playDemo(); };', i)
s = s[:j] + "window.openLabVideo ? openLabVideo() : playDemo(); };" + s[j + len('playDemo(); };'):]
rep("function loop(now) {\n  requestAnimationFrame(loop);",
    "function loop(now) {\n  requestAnimationFrame(loop);\n  if (window.__labHold) { lastT = now; return; }   // video open: no 3D rendering at all")
rep('<div id="tabs" role="tablist" hidden></div>',
    '<button type="button" id="vopen" class="vopen">🎬 شاهد التجربة فيديو <small>أخفّ على الهاتف</small></button>\n      <div id="tabs" role="tablist" hidden></div>')

poster = 'data:image/jpeg;base64,' + base64.b64encode(open(POSTER, 'rb').read()).decode()
vid_b64 = base64.b64encode(open(MP4, 'rb').read()).decode()
MIME = 'video/webm' if MP4.lower().endswith('.webm') else 'video/mp4'
chap_btns = ''.join('<button type="button" data-t="%s"><span>%s</span><span class="tm ltr">%d:%02d</span></button>' % (c['t'], H.escape(c['title']), int(c['t']) // 60, int(c['t']) % 60) for c in tl['chapters'])

CSS = r'''<style>
.vopen{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;min-height:48px;margin:0 0 10px;border:0;border-radius:12px;background:#ffd166;color:#3a2a00;font:inherit;font-size:15px;font-weight:800;cursor:pointer;touch-action:manipulation}
.vopen small{font-weight:600;font-size:12px;opacity:.8}
#vlayer{position:fixed;inset:0;z-index:300;background:#06262c;color:#fff;overflow-y:auto;-webkit-overflow-scrolling:touch;font-family:var(--font)}
#vlayer[hidden]{display:none}
.vl-top{position:sticky;top:0;z-index:2;display:flex;align-items:center;gap:8px;padding:8px 12px;background:rgba(6,38,44,.96);border-bottom:1px solid rgba(255,255,255,.08)}
.vl-top b{flex:1;min-width:0;font-size:15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.vl-top button{min-height:40px;padding:0 14px;border-radius:10px;border:1px solid rgba(255,255,255,.25);background:rgba(255,255,255,.08);color:#fff;font:inherit;font-weight:700;cursor:pointer;touch-action:manipulation}
.vl-body{max-width:1100px;margin:0 auto;padding:10px 12px calc(24px + env(safe-area-inset-bottom))}
.vl-player{position:relative;border-radius:12px;overflow:hidden;background:#000;max-width:min(100%,calc((100dvh - 64px) * 1.7778));margin:0 auto}   /* never taller than the screen (phones held sideways) */
@media (max-height:520px){ .vl-top{padding:4px 10px} .vl-top button{min-height:34px} .vl-body{padding-top:6px} }
.vl-player video{display:block;width:100%;aspect-ratio:16/9;background:#000}
.vl-load{position:absolute;inset:0;display:grid;place-items:center;font-weight:700;background:rgba(0,0,0,.35);pointer-events:none}
.vl-load[hidden]{display:none}
#vask{position:absolute;inset:0;background:rgba(3,30,36,.9);display:flex;flex-direction:column;justify-content:center;gap:10px;padding:14px;text-align:center}
#vask[hidden]{display:none}
#vask .q{font-size:clamp(15px,2.4vw,20px);font-weight:700;line-height:1.7}
#vask .opts{display:flex;flex-wrap:wrap;gap:8px;justify-content:center}
#vask button{min-height:46px;padding:8px 14px;border-radius:12px;border:1.5px solid #ffd166;background:rgba(255,209,102,.14);color:#fff;font:inherit;font-size:15.5px;font-weight:700;cursor:pointer}
#vask .skip{border-color:rgba(255,255,255,.35);background:transparent;font-weight:600;font-size:14px}
#vend{position:absolute;inset:0;background:rgba(3,30,36,.9);display:flex;flex-direction:column;justify-content:center;align-items:center;gap:12px;padding:14px;text-align:center}
#vend[hidden]{display:none}
#vend p{margin:0;font-size:17px;font-weight:700;line-height:1.7}
#vend div{display:flex;gap:8px;flex-wrap:wrap;justify-content:center}
#vend button{min-height:48px;padding:0 18px;border-radius:12px;border:0;font:inherit;font-size:15px;font-weight:800;cursor:pointer;background:#fff;color:#04525f}
#vend button.go{background:#ffd166;color:#3a2a00}
.vl-speed{display:flex;align-items:center;gap:6px;margin-top:8px;font-size:13px;color:#bfe9ef}
.vl-speed span{margin-inline-end:auto}
.vl-speed button{min-width:54px;min-height:36px;border-radius:10px;border:1px solid rgba(255,255,255,.22);background:transparent;color:#fff;font:inherit;font-weight:700;cursor:pointer;touch-action:manipulation}
.vl-speed button[aria-pressed="true"]{background:#08798c;border-color:#08798c}
.vl-cap{margin-top:8px;background:#0f3a42;border-radius:12px;padding:10px 14px;font-size:clamp(16px,2.2vw,19px);line-height:1.85;font-weight:600;min-height:3.9em}
.vl-cap b{color:#ffd166}
.vl-cap .guess{display:block;margin-top:4px;font-size:14px;color:#bfe9ef;font-weight:600}
.vl-read{margin-top:8px;display:flex;gap:8px;overflow-x:auto;scrollbar-width:none;padding-bottom:2px}
.vl-read::-webkit-scrollbar{display:none}
.vl-read>div{flex:0 0 auto;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:6px 12px;min-width:120px}
.vl-read .hero{background:rgba(104,174,113,.18);border-color:rgba(104,174,113,.5)}
.vl-read .k{font-size:12px;color:#bfe9ef;white-space:nowrap}
.vl-read .v{direction:ltr;unicode-bidi:isolate;text-align:right;font-size:17px;font-weight:800;white-space:nowrap}
.vl-read .hero .v{font-size:22px;color:#9be0a5}
.vl-chap{margin-top:10px;display:flex;flex-wrap:wrap;gap:6px}
.vl-chap button{flex:1 1 auto;min-height:44px;padding:6px 10px;border-radius:11px;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.05);color:#fff;font:inherit;font-size:13.5px;font-weight:600;cursor:pointer;touch-action:manipulation}
.vl-chap button .tm{display:block;font-size:11px;color:#9fc7cc;font-weight:500}
.vl-chap button[aria-current="true"]{background:#08798c;border-color:#08798c}
/* wide screens: video and text side by side */
@media (min-width:1000px) and (min-aspect-ratio:4/3){ .vl-body{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:14px;max-width:1400px} .vl-side{margin-top:0} .vl-side .vl-cap{margin-top:0} }
</style>'''

LAYER = f'''<div id="vlayer" hidden role="dialog" aria-label="فيديو التجربة">
  <div class="vl-top"><b>🎬 فيديو التجربة</b><button type="button" id="vclose">✋ جرّب بنفسك ✕</button></div>
  <div class="vl-body">
    <div class="vl-main">
      <div class="vl-player">
        <video id="vid" controls playsinline webkit-playsinline preload="none" poster="{poster}"></video>
        <div class="vl-load" id="vload" hidden>جارٍ تجهيز الفيديو…</div>
        <div id="vask" hidden><div class="q"></div><div class="opts"></div><button type="button" class="skip">تخطَّ وتابع ▶</button></div>
        <div id="vend" hidden><p>🎬 انتهى الفيديو. الآن دورك!</p><div><button type="button" class="go">✋ جرّب التجربة بنفسك</button><button type="button" class="again">↻ شاهد مرّة أخرى</button></div></div>
      </div>
      <div class="vl-speed" role="group" aria-label="سرعة الفيديو"><span>السرعة</span><button type="button" data-r="1" aria-pressed="true">1×</button><button type="button" data-r="1.25">1.25×</button><button type="button" data-r="1.5">1.5×</button></div>
    </div>
    <div class="vl-side">
      <div class="vl-cap" id="vcap" aria-live="polite">▶ اضغط تشغيل لتشاهد التجربة خطوة بخطوة.</div>
      <div class="vl-read" id="vread"></div>
      <div class="vl-chap" id="vchap">{chap_btns}</div>
    </div>
  </div>
</div>
<script type="application/json" id="vtl">{json.dumps(dict(tl, correct=correct_text), ensure_ascii=False).replace('</', '<\\/')}</script>
<script type="text/plain" id="vdata">{vid_b64}</script>
'''

JS = r'''<script>
(function () {
  const $ = q => document.querySelector(q);
  const TL = JSON.parse($('#vtl').textContent), layer = $('#vlayer'), v = $('#vid'), MIME = __MIME__;
  let srcReady = null;
  function loadSrc() {
    if (srcReady) return srcReady;
    const load = $('#vload'); load.hidden = false;
    const b64 = $('#vdata').textContent.trim();
    const viaAtob = () => { const bin = atob(b64), u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return new Blob([u], { type: MIME }); };
    srcReady = (window.fetch ? fetch('data:' + MIME + ';base64,' + b64).then(r => r.blob()).catch(viaAtob) : Promise.resolve(viaAtob()))
      .then(blob => { v.src = URL.createObjectURL(blob); v.preload = 'auto'; return new Promise(r => v.addEventListener('loadeddata', r, { once: true })); })
      .then(() => { load.hidden = true; v.playbackRate = v.defaultPlaybackRate; })
      .catch(() => { load.textContent = 'تعذّر تشغيل الفيديو على هذا المتصفّح.'; });
    return srcReady;
  }
  window.openLabVideo = function () {
    window.__labHold = true;                       // the 3D lab stops rendering while the video is open
    try { if (window.Lab && Lab.stopDemo) Lab.stopDemo(); } catch (e) { }
    layer.hidden = false; $('#vend').hidden = true;
    loadSrc().then(() => { if (!layer.hidden) v.play().catch(() => { }); });
  };
  function closeVideo() { try { v.pause(); } catch (e) { } layer.hidden = true; window.__labHold = false; }
  $('#vclose').onclick = closeVideo;
  $('#vend .go').onclick = closeVideo;
  $('#vend .again').onclick = () => { $('#vend').hidden = true; v.currentTime = 0; answered.clear(); guess = null; v.play().catch(() => { }); };
  $('#vopen').onclick = () => openLabVideo();
  document.addEventListener('keydown', e => { if (!layer.hidden && e.key === 'Escape') closeVideo(); }, true);
  // no WebGL → the 3D lab cannot run: open the video straight away
  let gl = null; try { const c = document.createElement('canvas'); gl = c.getContext('webgl2') || c.getContext('webgl'); } catch (e) { }
  if (!gl) setTimeout(openLabVideo, 0);

  // fullscreen subtitles
  const plain = h => { const d = document.createElement('div'); d.innerHTML = h.replace(/<br\s*\/?>/g, '\n'); return d.textContent.replace(/[ \t]+/g, ' ').trim(); };
  const ts = t => { const h = Math.floor(t / 3600), m = Math.floor(t / 60) % 60, s = (t % 60).toFixed(3).padStart(6, '0'); return String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0') + ':' + s; };
  let vtt = 'WEBVTT\n\n';
  TL.cues.forEach((c, i) => { const e = i + 1 < TL.cues.length ? TL.cues[i + 1].t : TL.duration; if (e > c.t) vtt += ts(c.t) + ' --> ' + ts(e) + '\n' + plain(c.html) + '\n\n'; });
  const tr = document.createElement('track'); tr.kind = 'subtitles'; tr.srclang = 'ar'; tr.label = 'العربية'; tr.src = URL.createObjectURL(new Blob([vtt], { type: 'text/vtt' })); v.appendChild(tr);
  const fsSubs = on => { for (const t of v.textTracks) t.mode = on ? 'showing' : 'hidden'; };
  fsSubs(false);
  document.addEventListener('fullscreenchange', () => fsSubs(!!document.fullscreenElement));
  v.addEventListener('webkitbeginfullscreen', () => fsSubs(true)); v.addEventListener('webkitendfullscreen', () => fsSubs(false));

  // synced captions, readings, chapters, the prediction question
  const cap = $('#vcap'), rd = $('#vread'), chBtns = [...document.querySelectorAll('#vchap button')], ask = $('#vask');
  const last = (arr, t) => { let lo = 0, hi = arr.length - 1, k = -1; while (lo <= hi) { const m = (lo + hi) >> 1; if (arr[m].t <= t + 1e-3) { k = m; lo = m + 1; } else hi = m - 1; } return k; };
  const esc = x => String(x).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' })[c]);
  let guess = null; const answered = new Set(); let curCue = -2, curRead = -2, curCh = -2;
  const askCue = TL.cues.find(c => c.ask), askCh = askCue ? last(TL.chapters, askCue.t) : -1;
  let verdictCh = TL.chapters.findIndex((c, i) => i > askCh && /النتيجة/.test(c.title)); if (verdictCh < 0) verdictCh = askCh + 1;
  const verdict = () => (TL.correct && guess.slice(0, 6) === TL.correct.slice(0, 6)) ? '✓ <b>توقّعك صحيح!</b>' : '✗ توقّعت «' + esc(guess) + '» — قارنه بالنتيجة.';
  function draw() {
    const t = v.currentTime;
    const ci = last(TL.cues, t);
    if (ci !== curCue) { curCue = ci; const c = TL.cues[ci];
      let h = c ? c.html : '▶ اضغط تشغيل لتشاهد التجربة خطوة بخطوة.';
      if (c && guess != null && !c.ask) h += '<span class="guess">' + (last(TL.chapters, c.t) === verdictCh ? verdict() : 'توقّعك: «' + esc(guess) + '»') + '</span>';
      cap.innerHTML = h;
      if (c && c.ask && !TL.narrated && !answered.has(ci) && !v.paused) showAsk(ci, c); }
    // narrated video: pause only after the voice has finished asking (end of the question's segment)
    if (TL.narrated) { const c = TL.cues[ci]; if (c && c.ask && !answered.has(ci) && !v.paused) { const end = ci + 1 < TL.cues.length ? TL.cues[ci + 1].t : TL.duration; if (t >= end - 0.15) showAsk(ci, c); } }
    const ri = last(TL.reads, t);
    if (ri !== curRead) { curRead = ri; const r = TL.reads[ri];
      let h = ''; if (r) { if (r.cap) h += '<div class="hero"><div class="k">' + esc(r.cap) + '</div><div class="v">' + esc(r.val) + '</div></div>';
        Object.keys(r.r || {}).forEach(k => { if (k !== r.cap) h += '<div><div class="k">' + esc(k) + '</div><div class="v">' + esc(r.r[k]) + '</div></div>'; }); }
      rd.innerHTML = h; }
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
  chBtns.forEach(b => b.onclick = () => { ask.hidden = true; $('#vend').hidden = true; loadSrc().then(() => { v.currentTime = +b.dataset.t + 0.05; v.play().catch(() => { }); }); });
  v.addEventListener('seeking', () => { ask.hidden = true; const t = v.currentTime; TL.cues.forEach((c, i) => { if (c.ask && c.t >= t - 0.05) answered.delete(i); }); draw(); });
  let raf = 0; const tick = () => { draw(); if (!v.paused && !v.ended) raf = requestAnimationFrame(tick); };
  v.addEventListener('play', () => { $('#vend').hidden = true; cancelAnimationFrame(raf); raf = requestAnimationFrame(tick); });
  v.addEventListener('timeupdate', draw); v.addEventListener('pause', draw);
  v.addEventListener('ended', () => { $('#vend').hidden = false; });
  const sp = [...document.querySelectorAll('.vl-speed button')];
  const setRate = r => { v.playbackRate = r; v.defaultPlaybackRate = r; sp.forEach(b => b.setAttribute('aria-pressed', +b.dataset.r === r)); try { localStorage.setItem('vlab:rate', String(r)); } catch (e) { } };
  sp.forEach(b => b.onclick = () => setRate(+b.dataset.r));
  try { const r = +localStorage.getItem('vlab:rate'); if (r >= 1 && r <= 1.5) setRate(r); } catch (e) { }
  draw();
})();
</script>'''.replace('__MIME__', json.dumps(MIME))

head_end = s.index('</head>')
s = s[:head_end] + CSS + '\n' + s[head_end:]
s = s.replace('<script>Lab.start();</script>', LAYER + JS + '\n<script>Lab.start();</script>', 1)
assert 'id="vlayer"' in s
open(OUT, 'w', encoding='utf-8').write(s)
print(OUT, round(len(s) / 1048576, 2), 'MB | chapters', len(tl['chapters']), '| cues', len(tl['cues']), '| correct', correct_text)
