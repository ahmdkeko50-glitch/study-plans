#!/usr/bin/env python3
"""Add a spoken narration to a recorded demo (frames + timeline.json from record-demo.js).

  python3 voiceover.py <frames-dir> <narration.json> <voice-dir> <out-dir>

- Synthesizes each narration line offline with a sherpa-onnx / Piper voice (voice-dir = an unpacked
  vits-piper-* package from github.com/k2-fsa/sherpa-onnx/releases/tag/tts-models).
- Line i is spoken at the start of caption i. If a line is longer than its caption's time, the video
  HOLDS on the last picture of that caption until the line ends (frames are duplicated), and every later
  caption, reading and chapter time shifts by the same amount.
- Writes <out-dir>/frames/f%05d.jpg (symlinks), <out-dir>/timeline.json, <out-dir>/narration.wav.
"""
import json, os, sys
import numpy as np, soundfile as sf, sherpa_onnx

FR, NAR, VOICE, OUT = sys.argv[1:5]
tl = json.load(open(os.path.join(FR, 'timeline.json'), encoding='utf-8'))
nar = json.load(open(NAR, encoding='utf-8'))
lines, fps, cues = nar['lines'], tl['fps'], tl['cues']
assert len(lines) == len(cues), f'{len(lines)} narration lines for {len(cues)} captions'
onnx = [f for f in os.listdir(VOICE) if f.endswith('.onnx')][0]
tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
    vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=f'{VOICE}/{onnx}', tokens=f'{VOICE}/tokens.txt', data_dir=f'{VOICE}/espeak-ng-data'), num_threads=4)))
LEAD, GAP = 0.15, 0.35          # silence before a line, minimum breath after it
clips, sr = [], None
for ln in lines:
    a = tts.generate(ln, sid=0, speed=float(nar.get('speed', 1.0))); sr = a.sample_rate
    x = np.array(a.samples, dtype=np.float32); x /= max(1e-6, np.abs(x).max()); clips.append(x * 0.9)
# holds: frame index → extra frames inserted before it
holds = {}
for i, c in enumerate(cues):
    end = cues[i + 1]['t'] if i + 1 < len(cues) else tl['duration']
    need = LEAD + len(clips[i]) / sr + GAP
    if need > end - c['t']:
        f_end = min(int(round(end * fps)), tl['frames'] - 1)
        holds[f_end] = holds.get(f_end, 0) + int(np.ceil((need - (end - c['t'])) * fps))
def new_t(t):   # same frame rounding as the holds, so a caption that starts where a hold was inserted moves with it
    f = int(round(t * fps)); return (f + sum(n for k, n in holds.items() if k <= f)) / fps
# frames
fo = os.path.join(OUT, 'frames'); os.makedirs(fo, exist_ok=True)
for f in os.listdir(fo): os.remove(os.path.join(fo, f))
k = 0
for f in range(tl['frames']):
    src = os.path.abspath(os.path.join(FR, f'f{f:05d}.jpg'))
    for _ in range(1 + holds.get(f, 0)):
        os.symlink(src, os.path.join(fo, f'f{k:05d}.jpg')); k += 1
dur = k / fps
# audio
mix = np.zeros(int(dur * sr) + sr, dtype=np.float32)
for i, c in enumerate(cues):
    s = int((new_t(c['t']) + LEAD) * sr); mix[s:s + len(clips[i])] += clips[i][:max(0, len(mix) - s)]
sf.write(os.path.join(OUT, 'narration.wav'), np.clip(mix[:int(dur * sr)], -1, 1), sr)
# timeline
t2 = dict(tl, frames=k, duration=round(dur, 2), narrated=True,
          chapters=[dict(c, t=round(new_t(c['t']), 2)) for c in tl['chapters']],
          cues=[dict(c, t=round(new_t(c['t']), 2), say=lines[i]) for i, c in enumerate(cues)],
          reads=[dict(r, t=round(new_t(r['t']), 2)) for r in tl['reads']])
json.dump(t2, open(os.path.join(OUT, 'timeline.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(f'video {tl["duration"]:.1f}s → {dur:.1f}s | holds at {len(holds)} captions (+{sum(holds.values())/fps:.1f}s) | narration {sum(len(c) for c in clips)/sr:.1f}s')
