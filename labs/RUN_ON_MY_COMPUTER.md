# صناعة فيديوهات التجارب على حاسبتك

الحاسبة اللي بيها **كرت شاشة** تسوّي الفيديوهات أسرع بهواية من السيرفر. كل الـ27 تجربة الباقية تاخذ تقريباً **ساعة أو أقل**،
وبجودة أعلى (1080p تنزل إلى 720p).

الناتج: لكل تجربة ملف `labs/L…-with-video.html`، وهو نفس المختبر ثلاثي الأبعاد وجوّاه فيديو التجربة بدون صوت.
ملف التجربة الأصلي ما يتغيّر.

خلصت 8 لحد هسّه: 1-4، 1-5، 1-6، 1-9، 2-11، 2-12، 2-14، 2-16. السكربت يتجاوزهن تلقائياً.

---

## ١. نصّب البرامج (مرّة وحدة)

### ويندوز
افتح **PowerShell** والصق هذا السطر، ويّه كل برنامج اضغط موافق:
```powershell
winget install --id Git.Git -e; winget install --id OpenJS.NodeJS.LTS -e; winget install --id Python.Python.3.12 -e; winget install --id Gyan.FFmpeg -e
```
بعدين **سكّر PowerShell وافتحه من جديد**، حتى يتعرّف على البرامج الجديدة.

### ماك
```bash
brew install git node python ffmpeg
```

## ٢. نزّل المستودع (مرّة وحدة)
بويندوز افتح **Git Bash** من قائمة ابدأ. بالماك افتح Terminal. واكتب:
```bash
git clone https://github.com/ahmdkeko50-glitch/study-plans.git
cd study-plans
git checkout claude/kind-cannon-wz5xjn
cd labs/tools
npm install
npx playwright install chromium
```

## ٣. سوّي الفيديوهات
من نفس المكان (`study-plans/labs/tools`):
```bash
bash make-all-videos.sh
```
- لكل تجربة تنفتح نافذة متصفّح وتشتغل التجربة لوحدها. **لا تسكّرها ولا تكبّسها**، تسكر لوحدها من تخلص.
- بالشاشة يطلع لك `✓ L2-3 in 2 min`، وبالأخير مجموع اللي انبنت.
- إذا انقطعت بالنص، شغّل نفس الأمر مرّة ثانية، ويكمّل من وين وكف.
- تريد تجربة وحدة بس؟ مثلاً: `bash make-all-videos.sh L2-3`

## ٤. ارفعها للمستودع
```bash
cd ..            # صرت بـ study-plans/labs
git add L*-with-video.html
git commit -m "Lesson video copies"
git push
```
أول مرّة يطلب منك تسجّل دخول GitHub. سجّل بنفس الحساب مال المستودع.

---

## إذا صارت مشكلة
| الرسالة | الحل |
|---|---|
| `node: command not found` أو `ffmpeg: command not found` | سكّر النافذة وافتحها من جديد. إذا بقت، رجّع الخطوة ١. |
| `Python 3 not found` | ويندوز: `winget install --id Python.Python.3.12 -e`، وبعدين افتح النافذة من جديد. |
| `Cannot find module 'playwright'` | تأكّد إنك بـ `labs/tools` ورجّع `npm install`. |
| `✗ L… failed` | شغّل التجربة لحالها: `bash make-all-videos.sh L…` ودزّلي آخر الأسطر اللي تطلع. |
| تريد تشوف النتيجة | افتح `labs/L…-with-video.html` بالمتصفّح واضغط «🎬 شاهد الفيديو». |

التفاصيل التقنية الكاملة: `labs/LAB_VIDEO.md`.
