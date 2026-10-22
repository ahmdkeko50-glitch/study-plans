# Continue the labs in a new chat: handoff + ready prompts

Open Claude Code on the repo **`ahmdkeko50-glitch/study-plans`**, branch **`claude/kind-cannon-wz5xjn`**, and paste
one of the prompts in section 3. Everything else the new chat needs is in the repo.

---

## 1. Where things stand

| | lessons | file |
|---|---|---|
| ✅ **Done with Sufyan's voice (13)** | L1-4 · L1-5 · L1-6 · L1-9 · L2-3 · L2-11 · L2-12 · L2-14 · L2-16 · L3-5 · L3-8 · L3-9 · L3-11 | `labs/L*-with-video.html` |
| 🔇 **Video done, no voice yet (23)** | L4-2 · L4-3 · L4-10 · L5-2 · L5-3 · L5-5 · L5-7 · L6-3 · L6-5 · L6-9 · L6-11 · L7-6 · L7-8 · L7-10 · L8-2 · L8-3 · L8-6 · L8-7 · L8-9 · L9-2 · L9-3 · L9-4 · L9-6 | `labs/L*-with-video.html` |
| 📝 Iraqi script for every lesson | read it to ElevenLabs as is | `labs/voiceover/L*-0.txt` (and `.json`) |

All 72 files (36 labs plus 36 video copies) already have:
- the **`?theme=ta3leem|eschool`** switch (default ta3leem);
- the **white video player** with the video in a **frame**;
- one «🎬 شاهد الفيديو» button;
- the readings that wrap onto several lines;
- the voice slowing the motion instead of freezing it.

**Recordings to fix (Sufyan takes):**
- L2-14 has one English sentence, and «11 فولت» should be «ثمنطعش».
- L2-16 is missing its last line, so the summary is cut.
- L3-9 is missing «هلا بيكم! مثال خمسة», and the numbers in lines 9 and 11 are doubtful.
- L1-6 is missing «هلا بيكم».
- L2-12 and L2-16 still say «بشويش» (non-Iraqi) and should be re-recorded.

## 2. Rules the new chat must keep (also in `CLAUDE.md`)

1. **Theme:** follow `labs/THEME.md`.
   - Read `?theme=` from `location.search` only. Never use localStorage or cookies.
   - JS colours come from `window.LAB_TC`.
   - Backgrounds stay as they are. The video player is white, with the video in a frame, and only the buttons take
     the brand colour.
   - New or rebuilt files go through `labs/tools/theme.py`.
2. **Scripts in Iraqi Arabic.** No «بشويش» (use «شوية شوية» / «على كيفك»). Write the numbers as they are said.
3. Never change the original `labs/L*.html` when making the video copy.
4. Send each finished file to the user as soon as it is done. Commit and push to `claude/kind-cannon-wz5xjn`. No PRs.
5. Check before delivering:
   - zero page errors;
   - the video opens and closes;
   - it pauses at the prediction question after the voice finishes;
   - there is exactly one watch button;
   - both `?theme=` values look right.

## 3. Ready prompts (copy one)

### 3A. Add Sufyan's voice to a lesson (most common)

> Upload the mp3 in the same message. Name it after the lesson, e.g. `L4-2.mp3`.

```text
اقرأ CLAUDE.md و labs/NEXT_LESSONS.md و labs/LAB_VIDEO.md و labs/THEME.md أولاً واتّبعهم حرفياً.
هذا تسجيل سفيان (ElevenLabs) للدرس <CODE> (مثال L4-2). سوّي نسخة الفيديو بالصوت:
1) احفظ التسجيل باسم labs/voiceover/<CODE>.sufyan.mp3
2) جهّز الأدوات مرّة وحدة (القسم 4 بـ NEXT_LESSONS.md): npm في labs/tools، pip sherpa-onnx، ونموذج whisper-small.
3) python3 labs/tools/split-voice.py labs/voiceover/<CODE>.sufyan.mp3 labs/voiceover/<CODE>-0.json \
     labs/voiceover/<CODE>.sufyan.json --whisper <مجلد sherpa-onnx-whisper-small>
   راجع كل جملة ووقتها؛ صحّح أي سطر عليه «<-- check»، وبلّغني إذا جملة ناقصة أو بالإنكليزي أو رقمها غلط.
4) bash labs/tools/make-video.sh labs/<CODE>.html labs/<CODE>-with-video.html labs/tools/work/<CODE> labs/voiceover/<CODE>.sufyan.json -
5) افحص التزامن (القسم 5) وافحص الملف (القسم 2 نقطة 5) بالثيمين.
6) commit + push للفرع claude/kind-cannon-wz5xjn، ودزّلي labs/<CODE>-with-video.html.
```

### 3B. Several lessons at once

```text
اقرأ CLAUDE.md و labs/NEXT_LESSONS.md أولاً. هذي تسجيلات سفيان: <L4-2.mp3, L4-3.mp3, ...>.
سوّي لكل درس نفس خطوات 3A، درس درس بالتسلسل (مو بالتوازي)، ودزّلي كل ملف أول ما يخلص.
بالأخير سوّي zip بكل الدروس اللي بيها صوت، و zip ثاني بالدروس الباقية بدون صوت.
```

### 3C. A brand-new lesson (not in the 36)

```text
اقرأ CLAUDE.md و labs/NEXT_LESSONS.md و labs/LAB_UI_GUIDELINES.md و labs/TEAM_PROMPT.md أولاً.
هذا ملف الدرس الأصلي <file.html>. سوّي:
1) المختبر المبسّط labs/<CODE>.html بـ labs/tools/build.py + وصفة بـ labs/tools/recipes.py (build.py يضيف الثيم لوحده).
2) افحصه: node labs/tools/button-test.js labs/<CODE>.html (صفر أخطاء، كل زر يشتغل) وبالثيمين.
3) اكتب السكربت العراقي labs/voiceover/<CODE>-0.json و .txt (جملة لكل كابشن، القسم ٦ بـ TEAM_PROMPT.md).
4) سوّي نسخة الفيديو بدون صوت: bash labs/tools/make-video.sh labs/<CODE>.html labs/<CODE>-with-video.html labs/tools/work/<CODE>
5) commit + push، ودزّلي الملفين والسكربت كنص حتى أسجّله بصوت سفيان.
```

### 3D. Fix a bad recording

```text
اقرأ labs/NEXT_LESSONS.md. هذا تسجيل جديد لـ <CODE> بدل القديم (أو: هذا مقطع للجملة رقم N فقط).
بدّل labs/voiceover/<CODE>.sufyan.mp3 وأعد الخطوات 3–6 من 3A.
```

## 4. One-time setup in a fresh chat or computer

```bash
cd labs/tools && npm install                   # playwright 1.56.1 (Chromium is already on the cloud machine)
pip install sherpa-onnx soundfile scipy numpy  # for split-voice.py and the sync check
mkdir -p ~/models && cd ~/models && curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-small.tar.bz2 && tar xjf sherpa-onnx-whisper-small.tar.bz2
# ffmpeg and ffprobe must be installed
```

- A cloud machine has 4 CPUs and no GPU. Recording one lesson takes about **15 minutes**.
- Record **one lesson at a time**: running several in parallel is not faster.
- `labs/tools/work/` is not in git, so a new chat records again. If `work/<CODE>/0/frames` is still there, only the
  voice step runs, which takes about 1 minute.
- On your own computer with a GPU, add `GPU=1` for 24 fps (1–3 minutes). See `labs/RUN_ON_MY_COMPUTER.md`.

## 5. Sync check (after making a voiced video)

Transcribe each caption window of the narration and compare it with the script line. Every window should start with
its own line, and a score below 0.6 means check it by ear. The pieces are:
- `labs/tools/work/<CODE>/0/vo/timeline.json`;
- `narration.wav` next to it;
- whisper-small, with the code below.

```python
import sherpa_onnx, numpy as np, soundfile as sf, json, difflib, scipy.signal as ss
D = 'labs/tools/work/<CODE>/0/vo'; W = '<path>/sherpa-onnx-whisper-small'
tl = json.load(open(f'{D}/timeline.json', encoding='utf-8')); x, sr = sf.read(f'{D}/narration.wav', dtype='float32')
asr = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f'{W}/small-encoder.int8.onnx', decoder=f'{W}/small-decoder.int8.onnx', tokens=f'{W}/small-tokens.txt', language='ar', task='transcribe', num_threads=4)
norm = lambda s: ''.join(c for c in s if 'ء' <= c <= 'ي'); c = tl['cues']
for i, q in enumerate(c):
    e = c[i + 1]['t'] if i + 1 < len(c) else tl['duration']; seg = x[int(q['t'] * sr):int(e * sr)]
    s = asr.create_stream(); s.accept_waveform(16000, ss.resample_poly(seg, 16000, sr).astype(np.float32)); asr.decode_stream(s)
    print(i, round(difflib.SequenceMatcher(None, norm(q['say']), norm(s.result.text)).ratio(), 2), s.result.text[:70])
```

(If the folder names differ, `make-video.sh` prints where it wrote the timeline and the wav.)

## 6. ElevenLabs settings for Sufyan

- Voice: **Sufyan (pvc)**, model **v4**.
- Speed **1.18**, stability **75**, similarity **75**.
- Paste the whole `labs/voiceover/<CODE>-0.txt` as one take, with a short pause between lines (one line = one caption).
- Read the numbers exactly as written. Don't add or drop lines: `split-voice.py` matches line by line.

## 7. Deliverables

- One file per lesson: `labs/<CODE>-with-video.html`. The video, voice and player are all inside it and it works
  offline.
- Zips at the end: one with the **voiced** lessons and one with the **silent** ones.
- The site opens each file with `?theme=ta3leem` or `?theme=eschool`. With no parameter it shows ta3leem.
