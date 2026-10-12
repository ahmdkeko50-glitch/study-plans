# فيديو التجربة داخل المختبر — Embedded experiment video

Many students' phones are too weak for the interactive 3D lab. The fix is a **copy** of the lesson (e.g.
`L1-4-with-video.html`) that is the same 3D experiment with a recorded video of its guided demo **inside it**.
The original lesson file is never changed.

What the student gets:
- The toolbar button **🎬 شاهد الفيديو** (it replaces the live «شاهد المحاكاة» demo, which is heavy on weak phones),
  a yellow **«🎬 شاهد التجربة فيديو — أخفّ على الهاتف»** button at the top of the panel, and «شاهد الفيديو أوّلًا» in the guide.
- The video opens over the experiment. **While it is open the 3D rendering stops completely**, so the phone only plays a
  normal H.264 video with its hardware decoder.
- Large captions and live readings (ΔV, Q, C…) under the video, synced to it; Arabic subtitles in fullscreen.
- Chapter buttons, a speed choice (1× · 1.25× · 1.5×).
- The prediction question: the video pauses at «توقّف وفكّر», the student taps an answer, and the «النتيجة» chapter says
  whether it was right.
- At the end, or with «✋ جرّب بنفسك ✕» at any time, the video closes and the 3D experiment continues where it was.
- On a device without WebGL (no 3D at all) the video opens automatically.
- Phone held sideways: the player never gets taller than the screen. Wide screens: video and captions side by side.

Video quality: frames are rendered at 1920×1080 and downscaled to 1280×720 (supersampled, sharp labels), H.264 CRF 21,
24 fps. About 1 MB per 10 seconds of video.

---

## Make one (one command)

Requirements: Node + Playwright with Chromium, Python 3, ffmpeg.

```bash
cd labs/tools
bash make-video.sh ../L1-4-dielectric.html ../L1-4-with-video.html
```

Steps inside the script (they can be run one by one):

1. **Record** — `node record-demo.js <lesson.html> <frames-dir> 1024 576 24 1 1.875`
   Opens a temporary copy of the lesson with a **virtual clock** and starts «شاهد المحاكاة». Time only advances after a frame
   has been captured, so every frame is exact even on a machine without a GPU. The copy uses demo pace 1 (the live lab uses
   1.35) and switches off the auto-quality governor so shadows stay on. The demo's caption box is hidden; captions, the
   question and the readings are written to `timeline.json` instead. Speed on a CPU-only machine: about 1 frame per second
   at 1080p (≈ 30 min for a 90-second demo). Use `960 540 24 1 1` for a quick draft (≈ 3 frames per second).
2. **Encode** — `ffmpeg -framerate 24 -i frames/f%05d.jpg -vf scale=1280:720:flags=lanczos -c:v libx264 -profile:v main -level 3.1 -preset slow -crf 21 -pix_fmt yuv420p -movflags +faststart -an video.mp4`
3. **Embed** — `python3 embed-video.py <lesson.html> video.mp4 poster.jpg frames/timeline.json <out.html>`

## Requirements on the lesson

- A guided demo (`ctx.demo({...})`) — every lesson in `labs/` has one.
- The verdict uses `ctx.predict({ options, correct })` and the first chapter after the question whose title contains «النتيجة».
- `embed-video.py` patches three engine lines in the copy (demo button, guide button, render loop). If the engine changes and a
  patch target is missing, the script stops with «patch target not found» instead of producing a broken file.

## Checks before sharing

1. Open the file on a phone: tap «🎬 شاهد الفيديو». The video plays; captions and readings change with it.
2. Play to the question: it pauses; an answer resumes it; «النتيجة» shows ✓ or ✗.
3. Tap a chapter and a speed button; turn the phone sideways.
4. Tap «✋ جرّب بنفسك ✕»: the 3D experiment is back and responds.
