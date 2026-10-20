import re, sys, os, glob, json, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recipes, theme
import argparse
ap = argparse.ArgumentParser(description='Splice the reference engine + CSS into exported lesson files and inject their LAB_SIMPLE recipe')
ap.add_argument('src', help='folder with the original exported lesson .html files (names start with <hash>-<code>_)')
ap.add_argument('out', help='output folder, e.g. labs/')
ap.add_argument('--ref', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'L1-4-dielectric.html'), help='reference file whose engine/CSS are copied')
ap.add_argument('codes', nargs='*', help='only these lesson codes (default: all)')
A = ap.parse_args()
REF = A.ref
ref = open(REF, encoding='utf-8').read()
def engine_of(s): return [x for x in re.finditer(r'<script>(.*?)</script>', s, re.S) if 'window.Lab = {' in x.group(1)][0]
def css_of(s): return list(re.finditer(r'<style>(/\* ===.*?)</style>', s, re.S))[0]
E = engine_of(ref).group(0); CSS = css_of(ref).group(0)
U = A.src; out = A.out; only = A.codes
for f in sorted(glob.glob(U + '/*.html')):
    m = re.match(r'[0-9a-f]{8}-(\d+-\d+)_', os.path.basename(f)); code = m.group(1) if m else None
    if not code or code == '1-4' or (only and code not in only): continue
    s = open(f, encoding='utf-8').read()
    cm = css_of(s); s = s[:cm.start()] + CSS + s[cm.end():]
    em = engine_of(s); s = s[:em.start()] + E + s[em.end():]
    rec = recipes.R.get(code)
    if rec:
        for old, new in rec.get('patch', []):   # small source fixes inside the lesson script
            assert s.count(old) == 1, (code, old[:60]); s = s.replace(old, new)
        rec = {k: v for k, v in rec.items() if k != 'patch'}
        block = '<script>window.LAB_SIMPLE = ' + json.dumps(rec, ensure_ascii=False) + ';</script>\n'
        i = s.index('<script>// @lesson'); s = s[:i] + block + s[i:]
    s = theme.patch(s) or s   # ?theme=ta3leem|eschool (see THEME.md)
    open(f'{out}/L{code}.html', 'w', encoding='utf-8').write(s)
    print(code, 'recipe' if rec else 'NO RECIPE')
