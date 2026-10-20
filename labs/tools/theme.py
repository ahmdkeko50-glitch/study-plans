#!/usr/bin/env python3
"""Add the ?theme= switch (ta3leem | eschool) to lab html files. Safe to run again: files already done are skipped.

  python3 theme.py ../L*.html

Rules (from the Ta3leem site, see THEME.md):
- The site opens every lab as  <lab url>?theme=ta3leem  or  ?theme=eschool  (iframe and "open in new window").
- Missing / empty / unknown value -> ta3leem. Trim + lowercase. Look the parameter up by name (other params may exist).
- Read only location.search. Never localStorage / cookies. Applied by an inline script at the top of <head>
  (data-theme on <html>) so the wrong theme never flashes.
- Everything drawn from JS (3D scene, canvas labels, charts) reads window.LAB_TC, set by the same script.
- The page background, the 3D scene background and the video-player background stay as they are in both themes.

What it changes in each file:
  1. inline theme script right after <head>
  2. a <style id="lab-theme"> after the main CSS: Rubik font (Arabic + Latin, embedded), the ta3leem colours, header,
     logo and footer swap
  3. main CSS: text-on-primary and primary-coloured text go through new variables (--c-on-primary, --c-primary-ink)
  4. JS: brand teal literals (0x08798c, '#08798c', 0x04525f, ...) and the canvas font name -> window.LAB_TC
  5. header: second logo (Ta3leem), footer brand name per theme
  6. video player (in *-with-video.html): its teal buttons follow the theme
"""
import base64, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, 'theme-assets')
MARK = '/* lab-theme */'

def b64(name): return base64.b64encode(open(os.path.join(ASSETS, name), 'rb').read()).decode()

AR_RANGE = ('U+0600-06FF,U+0750-077F,U+0870-088E,U+0890-0891,U+0897-08E1,U+08E3-08FF,U+200C-200E,U+2010-2011,U+204F,'
            'U+2E41,U+FB50-FDFF,U+FE70-FE74,U+FE76-FEFC')
LA_RANGE = ('U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,'
            'U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD')

HEAD = '''<script>''' + MARK + ''' /* ?theme=ta3leem|eschool. The URL is the only source of truth: no localStorage, no cookies. */
(function () {
  var theme = (new URLSearchParams(location.search).get('theme') || '').trim().toLowerCase();
  if (theme !== 'ta3leem' && theme !== 'eschool') theme = 'ta3leem';
  document.documentElement.setAttribute('data-theme', theme);
  window.LAB_THEME = theme;
  /* colours + font for everything drawn from JS (3D scene, canvas, charts) */
  window.LAB_TC = theme === 'eschool'
    ? { p: 0x08798c, pd: 0x04525f, t: 0xe4f1f3, a: 0x68ae71, ps: '#08798c', pds: '#04525f', f: 'Alexandria' }
    : { p: 0x00c3fe, pd: 0x200058, t: 0xe7f7ff, a: 0x1fb6a6, ps: '#00a6e6', pds: '#200058', f: 'Rubik, Alexandria' };
  /* if the lab ever links to its own pages, keep ?theme= on the next url */
  window.labThemeUrl = function (u) { var x = new URL(u, location.href); x.searchParams.set('theme', theme); return x.href; };
  if (theme === 'ta3leem') document.addEventListener('DOMContentLoaded', function () {
    var m = document.querySelector('meta[name="theme-color"]'); if (m) m.content = '#200058';
    var i = document.querySelector('link[rel="icon"]'); if (i) i.href = 'data:image/png;base64,@@FAV@@';
  });
})();
</script>
'''

THEME_CSS = '''<style id="lab-theme">''' + MARK + '''
@font-face{font-family:'Rubik';font-style:normal;font-weight:300 900;font-display:swap;src:url(data:font/woff2;base64,@@RAR@@) format('woff2');unicode-range:''' + AR_RANGE + '''}
@font-face{font-family:'Rubik';font-style:normal;font-weight:300 900;font-display:swap;src:url(data:font/woff2;base64,@@RLA@@) format('woff2');unicode-range:''' + LA_RANGE + '''}
:root{--c-on-primary:#fff;--c-primary-ink:#08798c;--c-primary-rgb:8,121,140;--c-primary-soft:#9fd2da}
/* Ta3leem — the backgrounds (--c-bg, --c-paper, 3D scene, video player) stay as they are */
html[data-theme="ta3leem"]:not(.hc){
  --c-primary:#00c3fe; --c-primary-dark:#200058; --c-tint:#e7f7ff; --c-accent:#1fb6a6;
  --c-line:#d7ecfa; --c-ink:#200058; --c-ink-soft:#6f6a93;
  --c-on-primary:#200058; --c-primary-ink:#0086c4; --c-primary-rgb:0,195,254; --c-primary-soft:#a6e9ff;
  --lab-ink:#200058; --lab-line:#d7ecfa;
  --font:'Rubik','Alexandria',system-ui,-apple-system,'Segoe UI',Tahoma,sans-serif;
}
html[data-theme="ta3leem"] body{font-weight:400}
html[data-theme="ta3leem"]:not(.hc) .brandbar{background:linear-gradient(135deg,#200058 0%,#2b0a73 55%,#0a5fa6 100%)}
html[data-theme="ta3leem"]:not(.hc) .brandbar .code{background:#f6848e;color:#200058}
html[data-theme="ta3leem"]:not(.hc) .banner.info{border-color:#b9e6fb}
html[data-theme="ta3leem"]:not(.hc) .btn.primary:hover{color:#fff}
html[data-theme="ta3leem"] .brandbar img.logo-e,html:not([data-theme="ta3leem"]) .brandbar img.logo-t{display:none}
html[data-theme="ta3leem"] .vl-chap button[aria-current="true"] .tm{color:inherit;opacity:.75}
html[data-theme="ta3leem"] .br-e,html:not([data-theme="ta3leem"]) .br-t{display:none}
</style>
'''

LOGO_T = '<img class="logo-t" src="data:image/webp;base64,@@LOGO@@" alt="تعليم">'
FOOT_OLD = 'المدرسة الإلكترونية · المنهج الرقميّ التفاعليّ'
FOOT_NEW = '<span class="br-e">المدرسة الإلكترونية</span><span class="br-t">تعليم</span> · المنهج الرقميّ التفاعليّ'

# brand literals inside JS -> theme values
JS_SUBS = [
    (r"'#08798c'", 'LAB_TC.ps'), (r'"#08798c"', 'LAB_TC.ps'),
    (r"'#04525f'", 'LAB_TC.pds'), (r'"#04525f"', 'LAB_TC.pds'),
    (r'\b0x08798c\b', 'LAB_TC.p'), (r'\b0x04525f\b', 'LAB_TC.pd'), (r'\b0xe4f1f3\b', 'LAB_TC.t'), (r'\b0x68ae71\b', 'LAB_TC.a'),
    # canvas font: '800 78px Alexandria, Arial'  ->  '800 78px ' + LAB_TC.f + ', Arial'
    (r"Alexandria(?=, [^'\n]*')", "' + LAB_TC.f + '"),
    # hand-built models: material paint_<hex>; the two brand teals (555404 = 0x08798c, 283231 = 0x04525f) follow the theme
    (r"color: parseInt\(k\.slice\(6\), 16\)", "color: ({ 555404: LAB_TC.p, 283231: LAB_TC.pd })[parseInt(k.slice(6), 16)] || parseInt(k.slice(6), 16)"),
]

def patch_css(css):
    css = re.sub(r'(?<![-\w])color:var\(--c-primary\)', 'color:var(--c-primary-ink)', css)
    css = css.replace('rgba(8,121,140,', 'rgba(var(--c-primary-rgb),').replace('#9fd2da', 'var(--c-primary-soft)')
    def rule(m):
        r = m.group(0)
        return r.replace('color:#fff', 'color:var(--c-on-primary)') if 'background:var(--c-primary)' in r else r
    return re.sub(r'[^{}]+\{[^{}]*\}', rule, css)

def patch_player(css):   # the video player's own <style> (made by embed-video.py)
    css = re.sub(r'background:#08798c;border-color:#08798c', 'background:var(--c-primary);border-color:var(--c-primary);color:var(--c-on-primary)', css)
    return css.replace('#08798c', 'var(--c-primary)').replace('#04525f', 'var(--c-primary-dark)')

def patch(s):
    if MARK in s: return None
    assets = {'@@FAV@@': b64('fav_ta3leem.png'), '@@RAR@@': b64('rubik-arabic-wght-normal.woff2'),
              '@@RLA@@': b64('rubik-latin-wght-normal.woff2'), '@@LOGO@@': b64('logo_ta3leem.webp')}
    head, tcss, logo = HEAD, THEME_CSS, LOGO_T
    for k, v in assets.items(): head = head.replace(k, v); tcss = tcss.replace(k, v); logo = logo.replace(k, v)
    # 1. head script: first thing in <head> (after the charset meta, which must stay in the first 1024 bytes)
    i = s.index('<meta charset="utf-8">') + len('<meta charset="utf-8">') + 1
    s = s[:i] + head + s[i:]
    # 2+3. main css
    m = re.search(r'<style>(/\* ===.*?)</style>\n?', s, re.S)
    s = s[:m.start()] + '<style>' + patch_css(m.group(1)) + '</style>\n' + tcss + s[m.end():]
    # 6. player css
    s = re.sub(r'<style>\n#vlayer\{.*?</style>', lambda m: patch_player(m.group(0)), s, flags=re.S)
    # 4. JS literals, only inside <script> blocks
    def js(m):
        t = m.group(0)
        if MARK in t: return t
        for a, b in JS_SUBS: t = re.sub(a, b, t)
        return t
    s = re.sub(r'<script>.*?</script>', js, s, flags=re.S)
    # 5. logo + footer
    s, n = re.subn(r'(<header class="brandbar">.*?<img )(src="data:image/png)', r'\1class="logo-e" \2', s, count=1, flags=re.S)
    assert n == 1, 'brandbar logo not found'
    j = s.index('>', s.index('class="logo-e"')) + 1
    s = s[:j] + logo + s[j:]
    assert s.count(FOOT_OLD) == 1, 'footer text'
    s = s.replace(FOOT_OLD, FOOT_NEW)
    return s

if __name__ == '__main__':
    for f in sys.argv[1:]:
        r = patch(open(f, encoding='utf-8').read())
        if r is None: print('skip (already themed)', f); continue
        open(f, 'w', encoding='utf-8').write(r)
        print('themed', f)
