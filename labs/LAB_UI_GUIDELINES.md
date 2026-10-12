# دليل تبسيط واجهة المختبر ثلاثيّ الأبعاد — Lab UI simplification guide

Applies to every lesson built on the same `Lab` engine (the single-file HTML labs, e.g. `L1-4-dielectric.html`).
The reference implementation is `labs/L1-4-dielectric.html` (lesson 1-4, العازل الكهربائي). Diff it against the
original export to see every change below in context. Search for `v3` in the file to find each engine edit.

---

## 1. Why students got confused (assessment of the original build)

| Symptom reported | Root cause found in the code | Fix |
|---|---|---|
| "Values in the side panel do not change when I do things" | The live readouts (`#reads`) were placed **inside** step ② of the accordion (`buildStepShell` → `b2.append(..., $('#reads'), ...)`). Whenever step ① (prediction) or step ③ (checks) was open, step ② collapsed and the readouts were `display:none`. | `#reads` is now mounted directly under the title, outside the steps, so it is always visible. |
| Voltmeter needle / switch / dipoles freeze | The first toolbar button was **⏸ pause**. Pausing sets `dt = 0`, and the needle, switch blade and dipole animations are driven by `dt`. Readouts kept updating but the 3D meter did not, so the student saw a mismatch. | Lessons without time evolution declare `static: true`; the engine then removes ⏸ / ⏭ / speed buttons and ignores the space key. |
| Choosing a material "does nothing" | With the slab outside the plates (`f = 0`) the dielectric constant has no physical effect, and nothing told the student. | The lesson flashes "العازل خارج المتسعة فلا أثر لمادّته الآن — اسحبه إلى الداخل" when `k`/material changes while `f < 2 %`. |
| The main slab controls were hidden | The engine's fold heuristic ("fold every section after the first that has no primary button") folded the **"الصفيحة العازلة"** section (material, `f`, `k`) into "إعدادات إضافية", while `V₀`, `d`, `L` stayed visible. | Lessons now mark advanced sections explicitly with class `adv`; only those are folded. |
| Too many buttons | 8 material chips + "قيمة أخرى", 3 panel buttons, 13 toolbar buttons, 3 recorder buttons, 1 hint button + 3 per-mission "?" buttons, 3 nav-pad buttons. | See the budget in §2. |

---

## 2. The button and text budget (target for every lesson)

**Stage toolbar (top of the 3D view): max 3 visible**
- `🎬 شاهد المحاكاة` (only when the lesson has a demo)
- `👆 ماذا ألمس؟`
- `⋯ المزيد` (everything else: views, labels, cross-section, floor, fullscreen, panel, help, high contrast, ⟲ — no snapshot)
- Add `⏸ / ⏭` only for lessons whose physics evolves in time (waves, oscillations, RC charging…). Static lessons set `static: true`.
- The nav pad (`＋ － ⌂`) stays; ⟲ is removed from the toolbar because ⌂ does the same job.

**Panel, in this order (top → bottom)**
1. Title (`h1`) + one `📘 دليل التجربة` button.
2. **Live readings** (`#reads`) — always visible, never inside a collapsible.
3. Step ① توقّع (prediction chips).
4. Step ② جرّب — contains, in order:
   - `🧭 خطوات التجربة`: numbered list that ticks itself (no buttons inside it).
   - `⚡ التجربة`: the 2–4 controls the student really needs (toggle / slider / select). One rescue button at most, hidden until needed (e.g. `⚡ أعِد الشحن` only after breakdown).
   - `↺ ابدأ التجربة من جديد`: the **only** reset button, full width, in its own row (`.resetrow`) right after the main controls — never inside the steps box or next to other buttons.
   - `⚙️ إعدادات متقدّمة (اختياري)`: folded `<details>` — every other slider and toggle.
   - **No** missions card and **no** readings recorder (table, CSV). The student never downloads anything: the 📷 snapshot button is removed from the toolbar too.
5. Step ③ تحقّق (questions, "ماذا تعلّمت", "أين نراه").

**Text rules**
- One sentence per step, verb first, bold the action word ("**اسحب** العازل", "**المس** المفتاح").
- Readout labels ≤ 4 words + the symbol (e.g. `الشحنة Q`, `السعة C`). The symbol must match the equation sheet.
- Do not repeat the same instruction twice (intro paragraph + steps list). If the lesson has a "خطوات" section, the engine hides the "ماذا أفعل؟" paragraph automatically (it is still read by the guide dialog).
- Keep long notes two lines (the engine clamps every `p.note`; tap to expand).
- **Never put the steps list inside `ctx.note()`**: it is a `p.note`, so the engine clamps it to two lines and only step 1 shows. Replace the note's element with a plain `<div class="steps">` (see `stepsNote` in 1-4).

---

## 3. Engine edits to port (copy from `L1-4-dielectric.html`, marked `v3`)

Every lesson file embeds the same engine script (`<script>/* ====== ... المختبر ثلاثي الأبعاد` …). Apply these edits once per file, or once in the shared build template.

1. **CSS** — append the `/* ---------- v3 · simpler panel ---------- */` block at the end of the second `<style>` (`details.opt`, `select.sel`, hide `.missions .hintbtn`).
2. **`buildStepShell`** — remove `$('#reads')` from `b2.append(...)` and add `head.after($('#reads'));` after `head.after(wrap);`.
3. **`simplifyPanel`**
   - fold rule: `const adv = secs.filter(s => s.classList.contains('adv')); const fold = adv.length ? adv : <old heuristic>;` summary text `⚙️ إعدادات متقدّمة (اختياري)`.
   - after the intro is moved into `#todo`: `todo.hidden = [...$('#controls').querySelectorAll('.sec>h2')].some(h => /خطوات/.test(h.textContent));`
4. **`simplifyToolbar`** — at the top remove `#tb-play`, `#tb-step` and the speed `.tbgroup` when `cur.def.static`; `keep` only `tb-play | tb-demo | tb-step | tb-touch`; drop the branch that converted the help button into a guide button.
5. **`keys`** — space toggles pause only when `!cur.def.static`; the `L` shortcut must also look inside `#tb-menu`.
6. **`makePanel.choice`** — if `o.select || opts.length > 4`, render one `<select class="sel">` instead of chips (the block keeps the original option values, strings or numbers).
7. **`buildV2`** — do not call `buildMissions` or `buildRecorder` at all (keep only the trend-arrow ticker and `buildCards` for step ③).
8. **`buildToolbar`** — remove the `📷 لقطة` snapshot button (it downloads a PNG).

---

## 4. Lesson-script edits (the `// @lesson …` script)

```js
Lab.define({
  id: 'CH1-L4-E1',
  scene: 'bench',
  static: true,                 // ① no time evolution → no ⏸ ⏭ speed buttons
  …
  setup(ctx) {
    // ② steps list first (tint section is never folded)
    ctx.section('خطوات التجربة', '🧭', 'tint');
    …STEPS list only (a <div class="steps">, no buttons here)

    // ③ the few controls the student needs
    ctx.section('التجربة', '⚡');
    ctx.toggle(...); ctx.param(...); ctx.choice(... 5+ options → automatic <select>)
    const rescue = ctx.buttons([['⚡ أعِد الشحن', () => recharge()]])[0]; rescue.row.hidden = true;   // show only when needed

    // the single reset button, isolated in its own full-width row after the controls
    const resetRow = ctx.buttons([['↺ ابدأ التجربة من جديد', restart]], { parent: document.getElementById('controls') })[0].row;
    resetRow.className = 'btnrow ctl resetrow'; resetRow.querySelector('.btn').classList.add('primary');

    // ④ everything else, folded by the engine
    ctx.section('إعدادات متقدّمة', '⚙️', 'adv');
    ctx.param('V0', …); ctx.param('d', …); …

    // ⑤ readouts: the hero value first (wide), then ≤ 5 more
    const rV = ctx.readout('قراءة الفولتميتر ΔV', { wide: true });
    …
    update() {
      rV.set(…);                       // same value as ctx.hero.set(...)
      rescue.row.hidden = !broken;     // rescue button only when it does something
    }
  }
});
```

Checklist per lesson:
- [ ] `static: true` unless the simulation needs pause/step.
- [ ] Sections in this order: `خطوات التجربة` (tint) → main controls → `adv` section(s).
- [ ] Exactly one reset button, alone in `.resetrow` after the main controls (CSS: `.resetrow{margin:12px 0 4px;padding-top:12px;border-top:1px dashed var(--c-line)} .resetrow .btn{width:100%}`); no "example" button (the reset applies the book example and the default state **is** the book example).
- [ ] Any `ctx.choice` with 5+ options becomes a dropdown automatically; keep chips for 2–4 options only.
- [ ] Add a `wide` readout that mirrors the hero value so it also appears in the panel.
- [ ] For every control whose effect is invisible in some state, call `ctx.flash('…')` explaining what to do (throttle to one flash per ~2.5 s).
- [ ] Keep readout labels referenced by `LAB_CONTENT.missions[*].check` (e.g. `R['السعة C']`) unchanged, or update the JSON too.
- [ ] Step indices used inside `updateSteps` (e.g. `cur === 1` for the "read the meter" timer) must be re-checked after removing a step.

---

## 5. Verification (run before shipping any lesson)

Headless check used for 1-4 (Playwright + bundled Chromium, `--use-gl=swiftshader`):

1. Load the file, dismiss `#guide`.
2. Assert the panel order is `head, reads, steps` and `#reads.offsetParent !== null`.
3. Assert `#toolbar` children are `tb-demo?, tb-touch, tb-more` and no `#tb-play` / `[data-speed]` exist for static lessons.
4. Drive each main control through real DOM events (`input` on the range, `change` on the checkbox and on the `<select>`), call `Lab.step(30, 1/60)`, and assert every readout text changed where physics says it must.
5. Open step ② and ③ in turn and confirm `#reads` is still visible.
6. Screenshot at 1280×800 and 390×844.

Expected 1-4 numbers (book example, k = 6): slab in, battery off → ΔV 12 V → 2.00 V, C 10 → 60 pF, Q stays 120 pC; battery on → ΔV 12 V, Q 720 pC.
