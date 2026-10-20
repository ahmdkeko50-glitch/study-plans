# فيديو التجربة داخل المختبر — Embedded experiment video (complete guide)

This guide explains how the `labs/L*-with-video.html` files were designed and built: each is the 3D lesson with a narrated
video of its own guided demo embedded **inside the same file**. All 36 lessons have one (1-4 with the recorded «Sufyan» voice,
the other 35 with the offline voice and their own Iraqi script in `voiceover/`). Follow it to get the same result for any lesson.
It covers why it was made this way, the full build pipeline with every setting, how the player is designed, the spoken
narration (recorded voice or offline TTS), the checks, and the pitfalls that were already fixed.

Contents
1. [What the student gets](#1-what-the-student-gets)
2. [Design decisions (and why)](#2-design-decisions-and-why)
3. [Files](#3-files)
4. [Quick start: one command](#4-quick-start-one-command)
5. [The pipeline step by step](#5-the-pipeline-step-by-step)
6. [timeline.json format](#6-timelinejson-format)
7. [Inside the output HTML](#7-inside-the-output-html)
8. [Player design: layout, behaviour, responsive rules](#8-player-design)
9. [Spoken narration](#9-spoken-narration)
10. [Requirements on the lesson](#10-requirements-on-the-lesson)
11. [Checks before sharing](#11-checks-before-sharing)
12. [Pitfalls already solved](#12-pitfalls-already-solved)
13. [Exactly how lesson 1-4 was built](#13-exactly-how-lesson-1-4-was-built)

---


> **Theme:** the player follows `?theme=` through the CSS variables (see `THEME.md`). The recorded frames keep the colours the lab had while recording; to make a ta3leem-coloured video, open the lab with `?theme=ta3leem` when recording.

## 1. What the student gets

The lesson opens as the normal interactive 3D experiment. On top of it:

| Entry point | Where | Text |
|---|---|---|
| Toolbar button | replaces the live «شاهد المحاكاة» demo | **🎬 شاهد الفيديو** |
| Guide card | first-visit guide | **🎬 شاهد الفيديو أوّلًا** |
| Automatic | devices with no WebGL (the 3D cannot run) | the video opens by itself |

When the video opens:
- It covers the screen. **The 3D rendering stops completely** while the video is open, so a weak phone only plays an
  ordinary H.264 video with its hardware decoder.
- The video has a spoken narration in Iraqi Arabic. The captions under the video stay in formal Arabic (the textbook
  wording), together with the live readings (ΔV, Q, C…). Both stay synced to the video.
- In fullscreen, the captions become Arabic subtitles (WebVTT).
- **Prediction question.** The video pauses after the voice finishes asking «توقّف وفكّر». The student taps an answer or
  «تخطَّ وتابع ▶». The «النتيجة» chapter then shows «✓ توقّعك صحيح!» or «✗ توقّعت «…» — قارنه بالنتيجة».
- Chapter buttons let the student jump to a part (المتسعة المشحونة · إدخال العازل · داخل العازل · النتيجة · البطارية موصولة ·
  الخلاصة). Speed is 1× · 1.25× · 1.5×, and the browser remembers the choice.
- At the end, «🎬 انتهى الفيديو. الآن دورك!» offers «✋ جرّب التجربة بنفسك» and «↻ شاهد مرّة أخرى».
- **«✋ جرّب بنفسك ✕»** (top bar) or **Esc** closes the video at any time, and the 3D experiment continues where it was.

The original lesson file (`L1-4-dielectric.html`) is never changed; the video version is a separate copy.

## 2. Design decisions (and why)

| Decision | Reason |
|---|---|
| Video **inside the 3D lesson copy**, not a separate video page | The teacher asked for it: one file, the student watches and then tries the same experiment. A separate page was built first and rejected. |
| Record the lesson's **own guided demo** (`ctx.demo`) | The video always matches the experiment exactly, and there is nothing to animate by hand. |
| **Virtual clock** recording | The recording machine has no GPU, so the real-time demo would stutter. With a virtual clock, time advances only after each frame is captured, so every frame is perfect. |
| Render **1920×1080**, encode **1280×720** (lanczos) | Supersampling gives sharp labels and edges. 720p keeps the file small. The first 960×540 version was rejected as "quality is so bad". |
| H.264 **main@3.1**, `-tune animation`, CRF 26, `+faststart` | Plays with hardware decoding on every phone, including old Android and iOS. Clean flat colours. About 1 MB per 10 s. |
| Captions are **not burned into the picture** | They stay large and readable as page text on any screen size, can be RTL-styled, and also become fullscreen subtitles. |
| Video stored as **base64 in the HTML**, turned into a Blob URL on first open | Single file, works offline from WhatsApp or Telegram. Nothing is decoded until the student taps. |
| `preload="none"` + poster image | Opening the lesson costs nothing extra until the video is requested. |
| `window.__labHold` stops the render loop | Frees the phone's CPU and GPU completely while watching. |
| Narration **holds the picture** when a line is longer than its segment | The voice never talks over the next step; the picture waits for it. |
| Pause at the question **after** the voice finishes it | A pause on the first word cut the spoken question in half. |

## 3. Files

```
labs/
  L1-4-dielectric.html        original 3D lesson (never modified by this pipeline)
  L1-4-with-video.html        RESULT: 3D lesson + embedded narrated video (≈16.6 MB)
  L1-5-with-video.html …      the same for the other 35 lessons (≈10–16 MB each)
  voiceover/
    L1-4.ar-iq.json           narration script: 18 Iraqi lines, one per caption (for offline TTS)
    L<code>-0.json            script of every other lesson (experiment 0), one line per caption
    L<code>-0.txt             the same lines as plain paragraphs, ready to paste into ElevenLabs
    L1-4.sufyan.mp3           recorded take of those 18 lines (ElevenLabs voice "Sufyan")
    L1-4.sufyan.json          same lines + "audio" + "segments" (where each line is in the take)
  tools/
    make-video.sh             one command: record → narrate → encode → poster → embed → copy mp4
    record-demo.js            Playwright recorder with virtual clock → frames + timeline.json (DRY=1: captions only, seconds)
    button-test.js            clicks every control / toolbar / menu item of every lab, reports errors and dead buttons
    voiceover.py              places narration lines on captions, inserts holds, mixes narration.wav
    embed-video.py            patches a COPY of the lesson and inserts player + video + timeline
```

Requirements: Node 18+ with `playwright` (Chromium), Python 3 with `numpy` and `soundfile`, and `ffmpeg` with libx264
and AAC. For offline TTS you also need `sherpa-onnx` and a Piper voice (§9).

## 4. Quick start: one command

**All lessons at once, on a computer with a graphics card (recommended):** step-by-step setup in `RUN_ON_MY_COMPUTER.md`.
```bash
cd labs/tools && npm install && npx playwright install chromium
bash make-all-videos.sh            # every lesson without a -with-video.html yet; GPU=1, 1080p frames, 24 fps, silent
```
With a graphics card a lesson takes 1–3 minutes instead of ≈17 on a CPU-only server. The videos are **silent** by default
(captions and readings are shown by the player); narration is optional (§9).


```bash
cd labs/tools
# silent video
bash make-video.sh ../L1-4-dielectric.html ../L1-4-with-video.html work
# with the recorded voice (what L1-4 uses now)
bash make-video.sh ../L1-4-dielectric.html ../L1-4-with-video.html work ../voiceover/L1-4.sufyan.json -
# with an offline TTS voice
bash make-video.sh ../L1-4-dielectric.html ../L1-4-with-video.html work ../voiceover/L1-4.ar-iq.json ./vits-piper-ar_JO-kareem-medium
# any other lesson: the script voiceover/<CODE>-<tab>.json is found automatically
bash make-video.sh ../L2-3.html ../L2-3-with-video.html work23 ./vits-piper-ar_JO-kareem-medium
```
A lesson file with several experiments (tabs) gets one video per experiment: `make-video.sh` records each tab into
`work/<tab>/frames`, and the player shows a switcher «1 · … / 2 · …». (The lessons in `labs/` are one-experiment builds,
`LAB_META.only`, so each has one video.)
- `work/` keeps the frames. If `work/frames/timeline.json` already exists, recording is skipped.
- Recording takes about 30 minutes on a CPU-only machine. With frames reused, changing the voice or words takes about 30 seconds.

## 5. The pipeline step by step

### 5.1 Record — `record-demo.js`
```bash
NOAA=1 node record-demo.js <lesson.html> <frames-dir> 1024 576 20 1 1.5 [tab]
#                                                    W    H   fps pace dpr  → 1536×864 JPEG frames
```
Speed on a 4-core machine without GPU (software rendering): about 2 frames per second, so a 80-second demo takes ≈15 minutes;
all 35 lessons ≈ 8 hours. Run lessons **one after another**: software rendering already uses every core, two at a time is
slower in total. `NOAA=1` turns MSAA off in the copy (≈25 % faster; the 1.5× supersampling + downscale keeps edges smooth).
1-4 was recorded at `24 fps, dpr 1.875` (≈1 fps to record); the others at `20 fps, dpr 1.5`.
`DRY=1` skips drawing and screenshots and only writes `timeline.json` (≈10 s per lesson): use it to read the captions and
write the script before the long recording.
What it does:
1. Writes a temporary copy `_lesson.html` next to the frames. The lesson itself is never touched. The copy has two changes:
   - `DEMO_PACE = 1.35` → `DEMO_PACE = 1`. The live lab is slow on purpose; the video is a little brisker.
   - `govMs > 25` → `govMs > 1e9`. Otherwise the auto-quality governor reads the fixed frame step as a slow device and
     turns off shadows.
2. Injects a **virtual clock** before any page script runs. It replaces `performance.now`, `Date.now`,
   `requestAnimationFrame`, `setTimeout`/`setInterval`, and CSS/Web Animations. `window.__adv(ms)` advances time by one frame.
3. Hides the UI so only the 3D stage is filmed:
   `#panel,#split,#navpad,#toolbar,#tb-menu,#flash,#democta,#demo{display:none!important}`.
   The demo caption box is hidden as well; its text goes into the timeline instead.
4. Removes the first-visit guide, runs 90 frames so the opening camera move settles, then clicks `#tb-demo`.
5. Every frame it advances the clock by 1/24 s and takes a JPEG screenshot (quality 93). It also reads:
   - the demo chapter `#demo .ch` → `chapters`;
   - the caption `#demo .dsay` (HTML) and the question buttons `#demo .dask` → `cues`;
   - every `#reads .read` tile plus `#hero` → `reads` (every 3 frames, only when something changed).
6. At the question it waits 3 s, then clicks «التالي» (`#demo .nx`). In the real player, the student answers instead.
7. Stops 4 s after the chapter says «انتهت». Writes `timeline.json` and `chapters.json`.

Chromium flags: `--use-gl=swiftshader --enable-unsafe-swiftshader --disable-background-timer-throttling`.
Quick draft: `960 540 24 1 1` (about 3 frames/s instead of 1).

### 5.2 Narrate (optional) — `voiceover.py`
```bash
python3 voiceover.py <frames-dir> <narration.json> <voice-dir | -> <out-dir>
```
See §9. Output: `<out-dir>/frames/` (symlinks, with held frames repeated), `timeline.json` (times shifted, `narrated: true`,
a `say` field on each cue), and `narration.wav`.

### 5.3 Encode — ffmpeg
```bash
ffmpeg -framerate 24 -i frames/f%05d.jpg [-i narration.wav] \
  -vf scale=1280:720:flags=lanczos \
  [-c:a aac -b:a 64k -ac 1 -ar 44100 -shortest] \
  -c:v libx264 -profile:v main -level 3.1 -preset slow -tune animation -crf 26 -pix_fmt yuv420p \
  -movflags +faststart video.mp4          # silent: add -an
```
| Setting | Why |
|---|---|
| `scale=1280:720:flags=lanczos` | 1080p → 720p supersampling: sharp text, small file |
| `profile main, level 3.1, yuv420p` | Hardware playback on old phones (High profile and 4:4:4 fail on some) |
| `-tune animation -crf 26 -preset slow` | Flat 3D colours compress well; CRF 24 is bigger with no visible gain, 28 shows blocks |
| `+faststart` | The index sits at the front, so playback starts at once |
| AAC 64 kb/s mono 44.1 kHz | Speech only; enough for a clear voice |

Poster: `ffmpeg -ss 2 -i video.mp4 -frames:v 1 -q:v 3 poster.jpg`.

### 5.4 Embed — `embed-video.py`
```bash
python3 embed-video.py <lesson.html> <out.html> <timeline.json>:<video.mp4|.webm>:<poster.jpg> [one triple per experiment …]
```
1. Finds the correct prediction answer in the lesson: `ctx.predict({ … options: [...], correct: N })`.
2. Patches **five places** (4 engine lines + the prediction hook) in the copy (§7.1). If any patch target is missing, it stops with
   `patch target not found` instead of writing a broken file.
3. Adds the player CSS before `</head>`. Adds the player HTML, the timeline, the base64 video and the player JS just before
   `<script>Lab.start();</script>`.
4. Prints the size, the number of chapters and cues, and the correct answer, e.g.
   `15.77 MB | chapters 6 | cues 18 | correct تنخفض`.

`make-video.sh` runs 5.1 → 5.4 for every experiment (`MP4=1` also leaves the mp4 files next to the output).

## 6. `timeline.json` format

```jsonc
{
  "fps": 24, "frames": 2660, "duration": 110.83,
  "narrated": true,                                  // only after voiceover.py
  "chapters": [ { "t": 0.0, "title": "المتسعة المشحونة" }, { "t": 57.08, "title": "النتيجة" }, … ],
  "cues": [                                          // one per demo caption, in order
    { "t": 20.92, "html": "🤔 توقّف وفكّر: ماذا سيحدث لقراءة الفولتميتر حين يدخل العازل؟",
      "ask": true, "opts": ["تزداد", "تنخفض", "لا تتغيّر"],
      "say": "دقيقة، فكّر وياي: شراح يصير لقراءة الفولتميتر من يدخل العازل؟ اختار جوابك." }, …
  ],
  "reads": [                                         // panel readings over time
    { "t": 36.38, "cap": "قراءة الفولتميتر ΔV", "val": "2.03 V", "sub": "Q = 120 pC ثابتة",
      "r": { "الشحنة Q": "120 pC · ثابتة", "السعة C": "59.1 pF = 5.91 C₀", … } }, …
  ]
}
```
A cue lasts until the next cue's `t` (the last one lasts until `duration`). The player shows the last entry whose `t ≤ currentTime`,
found by binary search. `embed-video.py` adds `"correct": "<text of the right option>"`.

## 7. Inside the output HTML

```
<head> … lesson CSS … [player CSS] </head>
<body>
  … lesson (engine v3 + LAB_SIMPLE recipe + lesson script) …
  [#vlayer player overlay]
  <script type="application/json" id="vtl"> timeline + correct </script>
  <script type="text/plain" id="vdata0"> base64 mp4 of experiment 1 </script>   ← ~96 % of the file size (vdata1, vdata2 … for more experiments)
  <script> player JS </script>
  <script>Lab.start();</script>
</body>
```

### 7.1 Engine patches (this copy only)
| # | Original | Becomes |
|---|---|---|
| 1 | toolbar `btn('🎬', 'شاهد المحاكاة', …, playDemo)` | `btn('🎬', 'شاهد الفيديو', 'شاهد التجربة فيديو مع الشرح (لا يُتعب الهاتف)', () => window.openLabVideo ? openLabVideo() : playDemo())` |
| 2 | guide button text `🎬 شاهد المحاكاة أوّلًا` | `🎬 شاهد الفيديو أوّلًا` |
| 3 | guide `.watch` handler `playDemo(); };` | `window.openLabVideo ? openLabVideo() : playDemo(); };` |
| 4 | `function loop(now) {\n  requestAnimationFrame(loop);` | adds `if (window.__labHold) { lastT = now; return; }` (`lastT` is reset so physics does not jump after closing) |
| 5 | engine `predict(o) {` | adds `window.__labPred = o;` so the player can read the correct prediction when the lesson builds its question in a helper |

### 7.2 Loading the video
- `<video id="vid" controls playsinline webkit-playsinline preload="none" poster="data:image/jpeg;base64,…">`. iOS needs
  `playsinline` so the video does not jump straight to fullscreen.
- On first open: `fetch('data:video/mp4;base64,…')` → Blob → `URL.createObjectURL`. Fallback: `atob` → `Uint8Array` → Blob.
  «جارٍ تجهيز الفيديو…» shows until `loadeddata`. It is done only once (`srcReady` promise).
- If decoding fails, the message becomes «تعذّر تشغيل الفيديو على هذا المتصفّح.».
- `.webm` input gets MIME `video/webm` (used for headless testing, because Chromium in Playwright has no H.264/AAC).

### 7.3 Player logic
- `openLabVideo()`: sets `__labHold = true`, stops a running live demo (`Lab.stopDemo`), shows the layer, loads, then plays.
- `closeVideo()`: pauses, hides the layer, sets `__labHold = false`. Wired to «✋ جرّب بنفسك ✕», «✋ جرّب التجربة بنفسك» and Esc.
- No WebGL (`webgl2` and `webgl` both fail) → `setTimeout(openLabVideo, 0)`.
- **Subtitles.** A WebVTT file is generated in the page from `cues` (HTML → plain text) and added as a `<track>`. It is shown
  only in fullscreen (`fullscreenchange`, plus iOS `webkitbeginfullscreen`/`webkitendfullscreen`).
- **draw()** runs on every animation frame while playing, and on `timeupdate`, `pause` and `seeking`:
  - **Caption.** The current cue's HTML. After the student answers, a line is added: «توقّعك: «…»», or the verdict in the
    first chapter titled «النتيجة» after the question. The verdict compares the first 6 characters with `correct`.
  - **Question.** Without narration it pauses when the question cue starts. With narration (`TL.narrated`) it pauses
    0.15 s before the question cue *ends*, after the voice has asked it. Each question is asked once; seeking back
    before it re-arms it.
  - **Readings.** The hero tile (green, bigger) plus the other tiles from `r`.
  - **Chapters.** The current chapter button gets `aria-current="true"`.
- A chapter tap seeks to `t + 0.05` and plays. A speed tap sets `playbackRate` and `defaultPlaybackRate` and saves `vlab:rate`
  in `localStorage` (inside try/catch).
- `ended` shows the end card. «↻ شاهد مرّة أخرى» resets the answers and replays.

## 8. Player design

Colours: background `#06262c`, caption box `#0f3a42`, accent yellow `#ffd166` (question borders, the bold
words in captions), active teal `#08798c`, hero reading green `#9be0a5`. Font: the lesson's `var(--font)`.

```
┌ vl-top (sticky) ─────────────────────────────── 🎬 فيديو التجربة ── [✋ جرّب بنفسك ✕] ┐
│ ┌ vl-player (16:9, rounded 12px) ───────────────────────────┐                      │
│ │  <video controls>     #vask  (question overlay)           │                      │
│ │                        #vend  (end card overlay)          │                      │
│ └───────────────────────────────────────────────────────────┘                      │
│  السرعة                                        [1×] [1.25×] [1.5×]                  │
│ ┌ vl-cap: big caption (16–19px, line-height 1.85, min 3.9em) ┐                      │
│ └────────────────────────────────────────────────────────────┘                      │
│ [hero ΔV 2.03 V] [Q 120 pC] [C 59.1 pF] …   ← vl-read: one horizontal swipe strip   │
│ [المتسعة المشحونة 0:00] [إدخال العازل 0:16] [داخل العازل 0:37] …  ← vl-chap         │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

Responsive rules:
| Situation | Rule |
|---|---|
| Phone portrait | Everything stacked. Video full width. Readings are one horizontal strip (no wrapping, hidden scrollbar). |
| **Phone sideways / short screens** | `.vl-player{max-width:min(100%, calc((100dvh - 64px) * 1.7778))}`: the video is never taller than the screen. Under 520 px height the top bar gets smaller. |
| Wide screen (≥1000 px and ≥4:3) | Two columns: video on one side, a 340 px column with the caption, readings and chapters on the other. Max 1400 px. |
| iPhone notch / home bar | Bottom padding uses `env(safe-area-inset-bottom)`. |
| Touch | Every button is at least 36–48 px high and uses `touch-action:manipulation` (no double-tap zoom). |
| Numbers with units | `.v{direction:ltr; unicode-bidi:isolate}`, so «10 pF» never shows as «pF 10» in RTL. |

Text on the player (all fixed Arabic):
«▶ اضغط تشغيل لتشاهد التجربة خطوة بخطوة.» · «تخطَّ وتابع ▶» · «🎬 انتهى الفيديو. الآن دورك!» · «✋ جرّب التجربة بنفسك» ·
«↻ شاهد مرّة أخرى» · «السرعة» · «جارٍ تجهيز الفيديو…».

## 9. Spoken narration

### 9.1 Writing the script
`voiceover/<lesson>.ar-iq.json`:
```json
{ "lesson": "1-4", "voice": "ar_JO-kareem-medium", "speed": 1.25,
  "lines": [ "هلا بيكم! هاي متسعة بيها صفيحتين متوازيتين، مشحونة على اثنعش فولت.", … ] }
```
- **One line per cue, in the same order.** Count the cues in `work/frames/timeline.json`; `voiceover.py` checks the count.
- Iraqi dialect, short, and talking to the students: «هسّه», «شوفوا», «ركّزوا», «دتنزل», «شراح يصير», «يلّا نشوف».
- The line for the question cue must end with the question itself («… اختار جوابك.»), because the video pauses when it ends.
- Spell numbers and symbols the way they should be heard: «اثنعش فولت», «مية وعشرين بيكو كولوم», «إي على كي».
  Avoid «گ»; write «ك» or «ق».
- Say what is happening on screen *now* and what to watch («ركّزوا على إبرة الفولتميتر»). Do not repeat the caption word for word.

### 9.2 How lines are placed (`voiceover.py`)
- Line *i* starts `LEAD = 0.15 s` after cue *i* starts.
- It needs `LEAD + length + GAP (0.35 s)`. If that is longer than the cue's segment, the segment is **played slower**:
  its frames are repeated evenly (up to `max_slow` = 1.8× the segment length) so the motion keeps pace with the words.
  Only what is still missing after that becomes a short hold on the segment's **last** frame (never the next step's first).
  A shorter line just leaves some silence.
- Every later chapter, cue and reading time is mapped through the same frame counts (`new_t(t)`), so captions, readings and
  the voice stay together.
- Lesson 1-4: 89 s of picture + 22 s of holds = 111 s.

### 9.3 Option A: recorded voice (used now) — ElevenLabs «Sufyan»
1. In ElevenLabs, paste the lines in order, with a clear pause between lines (a new paragraph per line). Download the MP3.
2. Put it in `voiceover/` and find the pauses:
   ```bash
   ffmpeg -i voiceover/L1-4.sufyan.mp3 -af silencedetect=noise=-40dB:d=0.3 -f null - 2>&1 | grep silence_
   ```
3. Write `voiceover/<lesson>.sufyan.json`. It has the same `lines` plus the audio file name and one `[start, end]` per line
   (seconds in the take). Each start goes just inside the pause before the line, and each end just inside the pause after it:
   ```json
   { "lesson": "1-4", "voice": "Sufyan (ElevenLabs, recorded)", "audio": "L1-4.sufyan.mp3",
     "lines": [ … 18 lines … ],
     "segments": [[0.0,5.45],[5.70,11.40],[11.70,15.75], … ,[97.83,103.71]] }
   ```
   If two lines are read with no pause, split them at the quietest point between them. In 1-4, lines 15/16 were split at 79.55 s.
4. Build with `-` as the voice folder:
   `bash make-video.sh ../L1-4-dielectric.html ../L1-4-with-video.html work ../voiceover/L1-4.sufyan.json -`
5. The whole take is normalised to a peak of 0.9. Each clip gets a 10 ms fade in and out (no clicks).

### 9.4 Option B: free offline voice (no internet at playback or build)
```bash
pip install sherpa-onnx soundfile scipy
curl -L -O https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-ar_JO-kareem-medium.tar.bz2
tar xjf vits-piper-ar_JO-kareem-medium.tar.bz2
bash make-video.sh ../L1-4-dielectric.html ../L1-4-with-video.html work ../voiceover/L1-4.ar-iq.json ./vits-piper-ar_JO-kareem-medium
```
`ar_JO-kareem-medium` at speed 1.25 was the clearest offline Arabic voice. Checked with Whisper: 85 % of words recognised,
against 67–73 % for `ar_JO-SA_miro_V2` and `ar_JO-SA_dii`. Its accent is neutral Levantine, not Iraqi.
Real Iraqi neural voices: Microsoft `ar-IQ-BasselNeural` / `ar-IQ-RanaNeural` via `pip install edge-tts`
(`edge-tts --voice ar-IQ-BasselNeural --text "…" --write-media lineN.mp3`). Join the clips into one take and use Option A.

### 9.5 Checking the sync
Transcribe each cue's window of `work/vo/narration.wav` with Whisper (e.g. sherpa-onnx `whisper-small`, language `ar`) and
compare the result with that cue's `say` text. Every window should contain its own line and nothing from the next one.
Lesson 1-4 (Sufyan): 17 of 18 windows match 0.70–0.96. The question line scores low only because Whisper repeats a letter;
checked alone, it is complete.

## 9.6 How the 35 scripts were written
1. `DRY=1 node record-demo.js ../L2-3.html dry/L2-3-0 480 270 24 1 1 0` → captions with times.
2. A sheet per lesson: index, start, duration, caption, the question and its options.
3. One Iraqi line per caption following §9.1 (about 11–13 characters per second of the caption; numbers in words; the
   question line ends «اختار جوابك.»; first line «هلا بيكم!», last line «هسّه دورك! …»).
4. Checked automatically: one line per caption, no digits / Latin letters / «گ» / «چ», question line ending.
5. After the build, every caption window of the narration was transcribed with Whisper and compared with its line (§9.5).

## 10. Requirements on the lesson

- The lesson uses the v3 engine (see `LAB_UI_GUIDELINES.md`) and has a guided demo `ctx.demo({...})`. All 36 lessons in `labs/` do.
- For the verdict: `ctx.predict({ options: [...], correct: N })`, and a demo chapter whose title contains «النتيجة» after the
  question. Without one, the chapter right after the question is used.
- The five patch targets in §7.1 must exist exactly once. If the engine changes, update the strings in `embed-video.py`.

To make the video for another lesson, e.g. 2-3:
```bash
cd labs/tools
node record-demo.js ../L2-3.html work23/frames 1024 576 24 1 1.875     # ≈30 min
python3 -c "import json;print(len(json.load(open('work23/frames/timeline.json'))['cues']))"   # → number of lines to write
# write ../voiceover/L2-3.ar-iq.json (and record it in ElevenLabs → L2-3.sufyan.mp3 + L2-3.sufyan.json)
bash make-video.sh ../L2-3.html ../L2-3-with-video.html work23 ../voiceover/L2-3.sufyan.json -
```
The cue texts are in `timeline.json` under `cues[i].html`; write narration line *i* for cue *i*.

## 11. Checks before sharing

0. `OUT=buttons.json node tools/button-test.js labs/L*.html` — every button, slider, toggle, chip, choice, ✋ label,
   prediction, toolbar and ⋯ menu item is clicked; page errors, controls that change nothing, and a reset that does not
   return to the start are listed (in the video copies it also opens and closes the video). All 36 lessons and their
   video copies: no page errors. Items it lists that are fine: speed buttons and «⟲ إعادة الزاوية» when already at that
   value/view, «ملء الشاشة» (no fullscreen in a headless browser), a «سجّل»/«أعِد الشحن» button when there is nothing to
   record or the capacitor is already charged, a prediction option after the prediction was revealed.

1. `git diff --quiet labs/<original>.html`: the original is unchanged.
2. `ffprobe <out>.mp4`: one h264 and one aac stream, the same duration.
3. On a phone:
   - Tap «🎬 شاهد الفيديو». The video starts after «جارٍ تجهيز الفيديو…», and the sound plays.
   - Captions and readings change with the picture.
   - At the question, the voice finishes, then the video pauses. Tap an answer. In «النتيجة» you see ✓ or ✗.
   - Tap a chapter and a speed button. Turn the phone sideways: the whole video is visible.
   - Go fullscreen: Arabic subtitles appear.
   - Tap «✋ جرّب بنفسك ✕»: the 3D experiment is back and responds to touch.
4. Desktop wide window: video and text side by side.
5. Size: about 1 MB per 10 s of video plus about 0.6 MB for the lesson.

## 12. Pitfalls already solved

| Problem | Fix |
|---|---|
| Choppy recording on a CPU-only machine | Virtual clock, so frames don't depend on render speed |
| Shadows disappeared in the recording | Governor threshold changed in the temporary copy only |
| Low quality (blurry labels) | Render at 1.875× DPR (1080p), lanczos down to 720p, `-tune animation` |
| Video taller than the screen on a sideways phone | `max-width: calc((100dvh - 64px) * 16/9)` |
| Units reversed in RTL tiles («pF 10») | `direction:ltr; unicode-bidi:isolate` on values |
| Verdict shown in the wrong caption | Verdict tied to the «النتيجة» chapter after the question |
| Video paused before the voice finished the question | For narrated timelines, pause at the end of the question's segment |
| A narration line spilled into the next caption | `new_t()` uses the same frame rounding as the holds |
| Playwright Chromium cannot play H.264/AAC | Test with a `.webm` (VP9/Opus) build; the real file stays mp4 |
| A separate video page | Rejected: the video lives inside the 3D lesson copy |

## 13. Exactly how lesson 1-4 was built

```bash
cd labs/tools
node record-demo.js ../L1-4-dielectric.html work/frames 1024 576 24 1 1.875
#   → 2129 frames, 88.7 s, 6 chapters, 18 cues
bash make-video.sh ../L1-4-dielectric.html ../L1-4-with-video.html work ../voiceover/L1-4.sufyan.json -
#   voiceover: video 88.7s → 110.8s | holds at 13 captions (+22.1s) | narration 98.3s
#   embed:     15.77 MB | chapters 6 | cues 18 | correct تنخفض
```
Result: `L1-4-with-video.html` (3D lesson + 111 s narrated 720p video) and `L1-4-with-video.mp4` (10.5 MB, H.264 + AAC).
