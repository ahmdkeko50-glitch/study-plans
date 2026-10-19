#!/usr/bin/env python3
"""Split one recorded voice take (e.g. ElevenLabs) into the lines of a narration script, and write the json that
make-video.sh / voiceover.py use.

  python3 split-voice.py <take.mp3> <script.json> <out.json> [--whisper DIR]

- script.json: the lesson's script, e.g. ../voiceover/L2-3-0.json ("lines": one per caption).
- Finds the pauses in the take (ffmpeg silencedetect), then groups the speech pieces into exactly len(lines) groups:
  * with --whisper DIR (an unpacked sherpa-onnx whisper model, e.g. sherpa-onnx-whisper-small): each piece is transcribed
    and the grouping that best matches the script text is chosen (handles lines the voice read with a pause inside);
  * without it: the len(lines)-1 longest pauses become the line boundaries.
- Two lines read with no pause between them cannot be found from pauses alone: the tool prints a warning; split that
  segment by hand at its quietest point (see LAB_VIDEO.md / TEAM_PROMPT.md).
- Prints every line with its time range (and the transcript when whisper is used) so a person can check it.
"""
import json, os, re, subprocess, sys, difflib

args = sys.argv[1:]
wdir = None
if '--whisper' in args:
    i = args.index('--whisper'); wdir = args[i + 1]; del args[i:i + 2]
TAKE, SCRIPT, OUT = args[:3]
lines = json.load(open(SCRIPT, encoding='utf-8'))['lines']
N = len(lines)

def run(cmd): return subprocess.run(cmd, capture_output=True, text=True).stderr
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', TAKE], capture_output=True, text=True).stdout)
log = run(['ffmpeg', '-hide_banner', '-i', TAKE, '-af', 'silencedetect=noise=-40dB:d=0.25', '-f', 'null', '-'])
st = [float(v) for v in re.findall(r'silence_start: ([\d.]+)', log)]
en = [float(v) for v in re.findall(r'silence_end: ([\d.]+)', log)]
# speech pieces between silences
pieces, cur = [], 0.0
for s, e in zip(st, en):
    if s - cur > 0.15: pieces.append([cur, s])
    cur = e
if dur - cur > 0.15: pieces.append([cur, dur])
P = len(pieces)
print(f'take {dur:.1f}s, {P} speech pieces, {N} script lines')
if P < N:
    print(f'WARNING: only {P} pieces for {N} lines: some lines were read without a pause (or are missing in the take).')

texts = None
if wdir:
    import numpy as np, sherpa_onnx
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', TAKE, '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    enc = [f for f in os.listdir(wdir) if f.endswith('encoder.int8.onnx')] or [f for f in os.listdir(wdir) if f.endswith('encoder.onnx')]
    dec = [f for f in os.listdir(wdir) if f.endswith('decoder.int8.onnx')] or [f for f in os.listdir(wdir) if f.endswith('decoder.onnx')]
    tok = [f for f in os.listdir(wdir) if f.endswith('tokens.txt')]
    asr = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=os.path.join(wdir, enc[0]), decoder=os.path.join(wdir, dec[0]), tokens=os.path.join(wdir, tok[0]), language='ar', task='transcribe', num_threads=4)
    texts = []
    for a, b in pieces:
        s = asr.create_stream(); s.accept_waveform(16000, x[int(a * 16000):int(b * 16000)]); asr.decode_stream(s); texts.append(s.result.text)

norm = lambda t: ''.join(c for c in t if 'ء' <= c <= 'ي')
gaps = [pieces[i + 1][0] - pieces[i][1] for i in range(P - 1)]
if P <= N:
    groups = [[i, i] for i in range(P)]
elif texts is None:
    cut = sorted(sorted(range(P - 1), key=lambda i: -gaps[i])[:N - 1])     # the N-1 longest pauses
    groups, s0 = [], 0
    for c in cut: groups.append([s0, c]); s0 = c + 1
    groups.append([s0, P - 1])
else:
    # dynamic programming: split pieces 0..P-1 into N consecutive groups maximising text similarity with the lines
    sim = lambda i, j, k: difflib.SequenceMatcher(None, norm(' '.join(texts[i:j + 1])), norm(lines[k])).ratio()
    NEG = -1e9; best = [[NEG] * (P + 1) for _ in range(N + 1)]; back = [[0] * (P + 1) for _ in range(N + 1)]
    best[0][0] = 0
    for k in range(1, N + 1):
        for j in range(k, P - (N - k) + 1):
            for i in range(k - 1, j):
                if best[k - 1][i] == NEG: continue
                v = best[k - 1][i] + sim(i, j - 1, k - 1) + 0.02 * gaps[i - 1] if i > 0 else best[k - 1][i] + sim(i, j - 1, k - 1)
                if v > best[k][j]: best[k][j] = v; back[k][j] = i
    groups, j = [], P
    for k in range(N, 0, -1):
        i = back[k][j]; groups.append([i, j - 1]); j = i
    groups.reverse()

segs = []
for g in groups:
    a = max(0.0, pieces[g[0]][0] - 0.05); b = min(dur, pieces[g[1]][1] + 0.05); segs.append([round(a, 2), round(b, 2)])
while len(segs) < N: segs.append([0.0, 0.05]); print('WARNING: no audio for line', len(segs) - 1, '(it stays silent)')
for k, (s, g) in enumerate(zip(segs, groups + [None] * N)):
    heard = ' '.join(texts[g[0]:g[1] + 1]) if texts and g else ''
    r = difflib.SequenceMatcher(None, norm(heard), norm(lines[k])).ratio() if heard else None
    flag = '  <-- check' if r is not None and r < 0.5 else ''
    print(f'{k:2d} {s[0]:7.2f}-{s[1]:7.2f}  {lines[k][:60]}' + (f'\n            heard: {heard[:70]}  ({r:.2f}){flag}' if heard else ''))
n = json.load(open(SCRIPT, encoding='utf-8'))
out = dict(lesson=n.get('lesson'), voice='recorded', audio=os.path.basename(TAKE), lines=lines, segments=segs,
           note='segments[i] = [start, end] seconds of line i in the audio file (made by split-voice.py; check by ear).')
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('wrote', OUT, '— the audio file must be next to it, named', os.path.basename(TAKE))
