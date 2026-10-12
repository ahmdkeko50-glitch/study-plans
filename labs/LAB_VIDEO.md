# نسخة الفيديو للأجهزة الضعيفة — Lab video edition

Many students' phones are too weak for the interactive 3D lab. The **video edition** of a lesson is a separate HTML file
(e.g. `L1-4-video.html`) that opens on a recorded video of the lesson's guided demo («شاهد المحاكاة»).
The original lesson file is never changed.

What the student gets:
- a normal video (H.264 MP4, 960×540, 24 fps) played by the phone's hardware decoder — no 3D, no GPU load;
- **large captions under the video**, synced to it (and as Arabic subtitles in fullscreen);
- **live readings** under the video (the same values the lab shows), synced to the video;
- **chapter buttons** to jump to any part, and a **speed** choice (1× · 1.25× · 1.5×);
- **the prediction question**: the video pauses at «توقّف وفكّر», the student taps an answer, and the result chapter
  tells them whether their prediction was right;
- «ماذا تعلّمنا؟» and «تحقّق من فهمك» below the video;
- a button «🧪 جرّب التجربة التفاعليّة بنفسك» that starts the full 3D lab inside the same file. Until it is tapped,
  none of the 3D code is even parsed (all lab scripts are stored as inert `text/x-lab` blocks). Phones without WebGL get the
  button disabled with an explanation; weak phones get a note that the video is enough. Opening the file with `#3d`
  at the end of the address starts the 3D lab directly; inside the lab, «🎥 العودة إلى الفيديو» goes back.

---

## Make one (one command)

Requirements: Node + Playwright with Chromium, Python 3, ffmpeg.

```bash
cd labs/tools
bash make-video.sh ../L1-4-dielectric.html ../L1-4-video.html
```

This runs three steps (you can run them separately):

1. **Record** — `node record-demo.js <lesson.html> <frames-dir> 960 540 24 1`
   Opens a temporary copy of the lesson with a **virtual clock**, starts «شاهد المحاكاة», and saves one JPEG per video frame
   plus `timeline.json` (chapters, captions, readings). Because time only advances when a frame has been captured, every frame
   is exact even on a slow machine without a GPU. The copy sets the demo pace to 1 (the live lab uses 1.35) and switches off
   the auto-quality governor so shadows stay on. The demo's own caption box is hidden: captions are shown by the page instead.
   At the prediction question the recorder holds the picture for 3 s and records the question and its options.
   Speed here: about 3 frames per second of real time (≈ 15 min for a 2-minute demo).
2. **Encode** — `ffmpeg -framerate 24 -i frames/f%05d.jpg -c:v libx264 -profile:v main -level 3.1 -preset slow -crf 27 -pix_fmt yuv420p -movflags +faststart -an video.mp4`
3. **Build the page** — `python3 make-video-page.py <lesson.html> video.mp4 poster.jpg frames/timeline.json <out.html>`
   Add `--external L1-4-video.mp4` to reference the MP4 next to the HTML instead of embedding it (smaller HTML, but the two
   files must always travel together). Default: embedded, one self-contained file.

The script also leaves `L1-4-video.mp4` next to the page, for Telegram groups or YouTube.

## Requirements on the lesson

- The lesson must have a guided demo (`ctx.demo({...})`). Every lesson in `labs/` has one.
- The prediction verdict uses the lesson's `ctx.predict({ options, correct })` and the first chapter after the question whose
  title contains «النتيجة» (or the chapter right after the question).
- «تحقّق من فهمك» comes from `ctx.checks([...])`, «ماذا تعلّمنا؟» from `LAB_CONTENT.learned`.

## Checks before sharing

1. Open the page on a phone: the poster shows at once, the video plays, captions and readings change with it.
2. Play to the question: the video pauses, an answer resumes it, the result chapter shows ✓ or ✗.
3. Tap a chapter button and a speed button.
4. Tap «🧪 جرّب التجربة التفاعليّة»: the 3D lab starts; «🎥 العودة إلى الفيديو» returns.
