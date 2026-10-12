# دليل تبسيط واجهة المختبر ثلاثيّ الأبعاد — Lab UI simplification guide (v3)

This document tells you how to turn any exported 3D-lab lesson (the single-file HTML labs built on the shared `Lab`
engine) into the simplified form used in `labs/L1-4-dielectric.html` and the 35 lessons in `labs/`.
Follow it and you get the same result every time:

- live readings always visible under the title, trend arrows on every value;
- a numbered **steps list** that ticks itself, with a 3D pointer above the next object to touch;
- the 2–4 controls that matter, the rest folded under **إعدادات متقدّمة (اختياري)**;
- one **↺ ابدأ التجربة من جديد** button, alone in its own row;
- a toolbar of three buttons (شاهد المحاكاة · ماذا ألمس؟ · المزيد); no ⏸ for lessons without time evolution;
- nothing to download: no missions card, no readings recorder, no snapshot button;
- easier 3D control: one-tap buttons for drags, tappable ✋ labels, larger grab tolerance, gentler camera;
- a dropdown instead of a wall of chips when a choice has 5+ options.

---

## 0. The two ways to apply it

| | What you edit | When |
|---|---|---|
| **A. Recipe (recommended)** | Nothing inside the lesson script. You add a small JSON block `window.LAB_SIMPLE = {…}` and let the engine do the rest. | Every exported lesson. All 35 lessons in `labs/` use this. |
| **B. In-code** | The lesson script itself calls `ctx.steps(...)`, `ctx.resetButton(...)`, marks sections `adv`, sets `static: true`. | A new lesson you write from scratch, or when a recipe cannot express something. `L1-4-dielectric.html` is the reference. |

Both need the **v3 engine**. The engine and the CSS are identical in every export, so they are replaced wholesale.

---

## 1. Build procedure (recipe way) — 5 commands

```
labs/tools/build.py      # splices the v3 engine + CSS into each export and injects its recipe
labs/tools/recipes.py    # one recipe per lesson code ('1-5', '2-3', …) — edit this
labs/tools/inventory.js  # lists every control, readout, state key and 3D handle of a lesson (needed to write a recipe)
```

1. Put the exported lesson files in one folder. Their names must start with `<hash>-<code>_`, e.g. `2dcd864e-1-5_….html`.
2. Build once without a recipe to inspect the lesson:
   ```bash
   python3 labs/tools/build.py <export-folder> labs 2-3
   OUT=inv.json node labs/tools/inventory.js labs/L2-3.html
   ```
   `inv.json` gives you, per lesson: section titles, control labels, readout labels (the keys of `R[...]`),
   the state keys and current values (`S.*`), the 3D handles (`drag:<object name> «hint»`, `pick:<name>`, `rotate:<name>`),
   the hero caption and whether the lesson has a demo.
3. Write the recipe in `labs/tools/recipes.py` (schema below), using the labels and names from step 2.
4. Build again: `python3 labs/tools/build.py <export-folder> labs 2-3`.
5. Verify (§5). Zero page errors, steps list present, one reset button, advanced section folded.

`build.py` needs Python 3 only. `inventory.js` needs Node + Playwright with Chromium (`--use-gl=swiftshader` is set inside).

---

## 2. Recipe schema (`window.LAB_SIMPLE`)

```js
R['2-3'] = dict(
  static=False,                 # True → no ⏸/⏭/speed buttons, space key ignored (lessons with no time evolution)
  heroRead=True,                # add a wide readout at the top of the panel mirroring the hero value on the stage
  scale=1,                      # size of the 3D step pointer (3 for big scenes such as 2-11, 2 for 4-10)
  adv=['الملف والمغناطيس'],     # regexes on section titles (h2) → whole section folded under «إعدادات متقدّمة»
  advCtl=['حركة آليّة'],        # regexes on a control's text → that single control moved into the folded section
  mainCtl=['التصوير الحراريّ'], # regexes → a control pulled OUT of a folded section into the main one
  hide=['مثال \\(2\\)'],         # regexes on button text → button hidden (a row whose buttons are all hidden disappears)
  taps=[dict(label='⬇ قرّب الصفيحتين', key='d', to=1.5),            # one-tap buttons: glide a slider to a value
        dict(label='⬆ أبعِدهما', key='d', to=8)],                   # (placed right under the control `key`; `after` overrides)
  tapLabel=dict(handle='upper-plate', key='d', a=8, b=1.5,           # the ✋ label of that drag becomes a button that
                textA='قرّب الصفيحتين', textB='أبعِد الصفيحتين'),   # toggles the slider between a and b, text follows state
  patch=[['old source text', 'new source text']],   # exact one-off replacements inside the lesson script (build.py
                                                   # asserts each old text occurs exactly once); not sent to the page
  doneText='…',                 # optional text under the list when every step is done
  steps=[                       # the guided checklist
    dict(t='<b>قرّب المغناطيس</b> إلى الملف …',   # one sentence, verb first, the action word in <b>
         done="Math.abs(R['موقع المغناطيس بالنسبة للملف']) < 8",   # JS expression → true when the step is done
         target='magnet-carrier',                 # 3D object name (from the inventory) for the pointer; optional
         up=1.2),                                 # pointer height above the object; optional
  ])
```

Inside `done` you can use:
- `S` — the state object (`S.bat`, `S.ins`, …; keys and current values are in the inventory);
- `R['readout label']` — the first number of that readout, SI prefixes resolved (`'60.0 pF'` → `6e-11`, `'12 cm'` → `12`);
- `H` — the hero value as a number, `HT` — the hero caption;
- `t` — seconds spent on this step (use `t > 2.5` for "read and observe" steps).
Only the current step and earlier ones are evaluated; a step that throws counts as not done.

Writing rules for `steps`:
- 3–5 steps. Each one is a single action the student can do with the visible controls or the 3D objects.
- Use the exact button labels in «…» and make the physics outcome part of the sentence ("…: ΔV يقلّ و C تزداد").
- Do not make the first step already true in the default state (it would tick on load).
- Keep `R[...]` labels exactly as the inventory prints them; renaming a readout breaks the step.

A lesson that already ships its own "خطوات" section (e.g. 3-9 worked example) gets no `steps` key.

**Gated drags.** Search the lesson script for `enabledFn:` on `ctx.drag(...)`. A drag that is enabled only in one mode
(2-3: the coil only in «تحريك الملف»), or only after the prediction (6-3: the lamp), feels broken to the student. Use `patch`
to remove the gate and switch the mode in `onStart` instead (see `R['2-3']`), or keep the mode switch visible in the main
section when the gate is physically meaningful (8-6: absorbers exist only in radiography mode).

---

## 3. In-code way (for new lessons) — what the engine offers

```js
Lab.define({
  …, static: true,                                  // no time evolution → no pause/step/speed buttons
  setup(ctx) {
    const steps = ctx.steps([                       // checklist + 3D pointer; returns {reset(), isDone(i), all}
      { t: 'html', done: tOn => bool, target: () => obj, up: 1.2 }, …
    ], { scale: 1, doneText: '…' });
    ctx.section('التجربة', '⚡');                   // the few controls the student needs
    ctx.toggle(…); ctx.param(…); ctx.choice(… 5+ options render as a <select> automatically);
    ctx.buttons([[ '⚡ أعِد الشحن', fn ]])[0].row.hidden = true;   // rescue buttons only when they do something
    ctx.resetButton(() => { example(); steps.reset(); });          // THE reset button, isolated in its own row
    ctx.section('إعدادات متقدّمة', '⚙️', 'adv');  // class 'adv' → folded by the engine
    …
    ctx.drag(obj, { hint: 'أدخِل العازل', onTap: () => slideTo(S.ins > 50 ? 0 : 100) }); // ✋ label becomes a button
    ctx.ctl('ins')                                  // any control's api by state key: set / get / el
  }
});
```
Other engine behaviours you get for free: readouts above the steps, auto reset button (`restartCurrent`) when the lesson
adds none, hidden "ماذا أفعل؟" paragraph when a «خطوات» section exists, no missions/recorder/snapshot, select for 5+ options,
camera `rotateSpeed 0.55 / zoomSpeed 0.75 / damping 0.12`, grab halo `44 px` touch / `20 px` mouse.

Rules: never build the steps list inside `ctx.note()` (notes are clamped to two lines); never put the reset button next to
other buttons; keep readout labels referenced by recipes or by `LAB_CONTENT` unchanged.

---

## 4. Engine edits (already in `L1-4-dielectric.html`; `build.py` copies them). Search `v3` in the file.

1. CSS block `/* v3 · simpler panel */` + `.resetrow`, `.lab3.grab.tap`, `.chips.go`, `select.sel`.
2. `buildStepShell`: `#reads` mounted after `#head` (always visible), not inside step ②.
3. `simplifyPanel`: fold = sections with class `adv` (with a recipe present, nothing else is folded); hide `#todo` when a
   «خطوات» section exists; add the auto reset button when none exists.
4. `simplifyToolbar`: keep `tb-demo`, `tb-touch` (+ play/step when not static); everything else under ⋯; no ⟲ (the nav pad has ⌂).
5. `buildToolbar`: no `📷 لقطة`. `keys`: space ignored when static; `L` also looks in `#tb-menu`.
6. `makePanel`: `choice()` → `<select>` for 5+ options; `steps()`, `resetButton()`, `ctl()` helpers.
7. `buildV2`: no `buildMissions`, no `buildRecorder` (keep `buildCards` and the trend ticker).
8. `initRenderer`: camera speeds/damping. `makePointer`: grab halo, `onTap` labels kept after the first drag, `handles` getter.
9. `applySimple(rt)` — the recipe interpreter, called in `mount()` between `applyHero` and `simplifyPanel`;
   `ctx.pointerHandles()` for the inventory.

---

## 5. Verification (do it for every lesson before shipping)

```bash
OUT=inv.json node labs/tools/inventory.js labs/L*.html     # prints "exps=1 ok" per file; any page or console error is listed
```
Then open the file and check:
1. Panel order: title → readings → ① توقّع → ② جرّب (steps, controls, reset, folded advanced) → ③ تحقّق.
2. Toolbar: `شاهد المحاكاة · ماذا ألمس؟ · المزيد` (+ ⏸ only for time-based lessons).
3. Do step 1 by hand: it ticks, the pointer moves to the next object, the readings change.
4. Nothing in the page downloads a file.
5. Devices (the engine handles these; just confirm): phone portrait (390×844) → stage on top (52 dvh), a grey drag bar
   between stage and panel (drag to resize, double-tap to toggle), one-line brand header, readings as one horizontal
   strip; phone landscape (844×390) → panel 340 px on the side; tablet portrait (768×1024) → stage 56 dvh, three readout
   tiles per row; tablet landscape and desktop → side panel 372 px. No horizontal page scroll at any width.
   `labs/tools/inventory.js` runs at 1280×800; for the device shots use the same Playwright setup with `isMobile`/`hasTouch`.

The 36 lessons in `labs/` pass this check with zero errors (Chromium, software GL).
