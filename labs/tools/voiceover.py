#!/usr/bin/env python3
"""Add a spoken narration to a recorded demo (frames + timeline.json from record-demo.js).

  python3 voiceover.py <frames-dir> <narration.json> <voice-dir | -> <out-dir>

- A RECORDED voice (e.g. an ElevenLabs take of the lines): the narration json has "audio" (file next to the json)
  and "segments" ([start, end] seconds of each line in that file); pass "-" as voice-dir.

- Synthesizes each narration line offline with a sherpa-onnx / Piper voice (voice-dir = an unpacked
  vits-piper-* package from github.com/k2-fsa/sherpa-onnx/releases/tag/tts-models).
- Line i is spoken at the start of caption i. If a line is longer than its caption's time, that part of the
  video plays SLOWER (up to max_slow = 1.8×, frames repeated evenly) so the motion stays with the words, and only
  the rest is a hold on its last picture; every later caption, reading and chapter time shifts to match.
  A line shorter than its caption just leaves a little silence.
- Writes <out-dir>/frames/f%05d.jpg (symlinks), <out-dir>/timeline.json, <out-dir>/narration.wav.
"""
import json, os, sys
import numpy as np, soundfile as sf

FR, NAR, VOICE, OUT = sys.argv[1:5]
tl = json.load(open(os.path.join(FR, 'timeline.json'), encoding='utf-8'))
nar = json.load(open(NAR, encoding='utf-8'))
lines, fps, cues = nar['lines'], tl['fps'], tl['cues']
assert len(lines) == len(cues), f'{len(lines)} narration lines for {len(cues)} captions'
LEAD, GAP = 0.15, 0.35          # silence before a line, minimum breath after it
clips, sr = [], None
if nar.get('audio'):            # recorded take: cut line i out of the file at segments[i]
    import subprocess
    sr = 44100; raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(os.path.dirname(NAR), nar['audio']),
                                      '-f', 'f32le', '-ac', '1', '-ar', str(sr), '-'], capture_output=True, check=True).stdout
    full = np.frombuffer(raw, dtype=np.float32); full = full / max(1e-6, np.abs(full).max()) * 0.9
    assert len(nar['segments']) == len(lines), 'one [start, end] segment per line'
    fade = np.linspace(0, 1, int(0.01 * sr), dtype=np.float32)
    for a, b in nar['segments']:
        x = full[int(a * sr):int(b * sr)].copy(); x[:len(fade)] *= fade; x[-len(fade):] *= fade[::-1]; clips.append(x)
else:
    import sherpa_onnx
    onnx = [f for f in os.listdir(VOICE) if f.endswith('.onnx')][0]
    tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=f'{VOICE}/{onnx}', tokens=f'{VOICE}/tokens.txt', data_dir=f'{VOICE}/espeak-ng-data'), num_threads=4)))
    for ln in lines:
        a = tts.generate(ln, sid=0, speed=float(nar.get('speed', 1.0))); sr = a.sample_rate
        x = np.array(a.samples, dtype=np.float32); x /= max(1e-6, np.abs(x).max()); clips.append(x * 0.9)
# timing: when a line needs more time than its caption's segment, the segment is first played SLOWER (each frame shown
# a little longer, spread evenly, up to MAXS times the original length) so the motion keeps pace with the words;
# only what is still missing after that is a short hold on the segment's last frame. Shorter lines leave silence.
MAXS = float(nar.get('max_slow', 1.8))
F = tl['frames']; counts = np.ones(F, dtype=int); slowed = held = 0
for i, c in enumerate(cues):
    end = cues[i + 1]['t'] if i + 1 < len(cues) else tl['duration']
    fa = min(int(round(c['t'] * fps)), F - 1); fb = max(fa + 1, min(int(round(end * fps)), F)); n = fb - fa
    need = int(np.ceil((LEAD + len(clips[i]) / sr + GAP) * fps))
    if need <= n: continue
    st = min(need, int(n * MAXS)); extra = st - n
    if extra > 0: np.add.at(counts, fa + (np.arange(extra) * n) // extra, 1); slowed += extra
    if need > st: counts[fb - 1] += need - st; held += need - st
cum = np.concatenate([[0], np.cumsum(counts)])
def new_t(t):   # original time → time in the narrated video (same frame rounding as above)
    return cum[min(max(int(round(t * fps)), 0), F)] / fps
# frames
fo = os.path.join(OUT, 'frames'); os.makedirs(fo, exist_ok=True)
for f in os.listdir(fo): os.remove(os.path.join(fo, f))
k = 0
for f in range(F):
    src = os.path.abspath(os.path.join(FR, f'f{f:05d}.jpg'))
    for _ in range(counts[f]):
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
print(f'video {tl["duration"]:.1f}s → {dur:.1f}s | slowed +{slowed/fps:.1f}s, held +{held/fps:.1f}s | narration {sum(len(c) for c in clips)/sr:.1f}s')
