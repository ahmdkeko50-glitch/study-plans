# Lab theme: `?theme=ta3leem` / `?theme=eschool`

**This rule covers every lab file, now and in all future updates.** Anything new (a lesson, a player, a canvas, a chart,
a 3D material) has to follow it.

## What the Ta3leem site sends

- The site opens each lab with a `theme` query parameter on the lab's own URL, both in the iframe and through "open in
  new window". For example: `…/physics-12/lab-1?theme=eschool`.
- Values are `ta3leem` or `eschool`, always lowercase. Other parameters may be added later, so look `theme` up by name.
- If `theme` is missing, empty or anything else, use **`ta3leem`**. Trim and lowercase before comparing.

## The rules

1. Read the theme only from the page's own `location.search`, with `URLSearchParams`. The parent page is cross-origin,
   and `document.referrer` has no query string.
2. Apply it before the first paint. An inline script that is the first thing in `<head>` (right after
   `<meta charset>`) sets `<html data-theme="…">`, so the wrong theme never flashes.
3. **The URL is the only source of truth.** Never write the theme to localStorage or cookies, and never read a saved
   one. Every lab shares one domain, so a stored value would override what the site asked for.
4. If a lab moves between its own pages, carry `?theme=` onto the next URL. The head script provides
   `labThemeUrl(url)` for this.
5. The theme is fixed for each page load. There is no postMessage and nothing to listen for.
6. Everything coloured from JS (3D scene, canvas labels, charts, the video player) uses the same value as the CSS:
   `window.LAB_THEME` (`'ta3leem'`/`'eschool'`) and `window.LAB_TC`:

   | key | ta3leem | eschool | use |
   |---|---|---|---|
   | `p` / `ps` | `0x00c3fe` / `'#00a6e6'` | `0x08798c` / `'#08798c'` | brand primary (number for three.js, string for canvas) |
   | `pd` / `pds` | `0x200058` / `'#200058'` | `0x04525f` / `'#04525f'` | brand dark |
   | `t` | `0xe7f7ff` | `0xe4f1f3` | light tint |
   | `a` | `0x1fb6a6` | `0x68ae71` | accent / "good" |
   | `f` | `'Rubik, Alexandria'` | `'Alexandria'` | canvas font: `'800 40px ' + LAB_TC.f + ', Arial'` |

   **Never hard-code `#08798c` / `0x08798c` / `#04525f` or `Alexandria` in JS.** Use `LAB_TC`.
   In CSS, use the variables (`--c-primary`, `--c-primary-ink` for primary-coloured text, `--c-on-primary` for text
   on a primary fill, `rgba(var(--c-primary-rgb),a)`).
7. **The backgrounds do not change between themes.** The page (`--c-bg`), the cards (`--c-paper`), the 3D scene and the
   video-player overlay stay as they are. Only the brand parts change: primary/accent colours, text colour, font,
   header bar, logo and footer name.

## The two themes

| | ta3leem (default) | eschool |
|---|---|---|
| font | Rubik (Arabic + Latin, embedded woff2, weights 300–900), then Alexandria for anything Rubik lacks | Alexandria |
| primary | `#00c3fe` | `#08798c` |
| dark / ink | `#200058` | `#04525f` / `#0f3a42` |
| tint / line | `#e7f7ff` / `#d7ecfa` | `#e4f1f3` / `#cfe1e4` |
| accent | `#1fb6a6` (good), `#f6848e` (lesson-number badge) | `#68ae71`, amber badge |
| muted text | `#6f6a93` | `#4a6a70` |
| text on primary buttons | `#200058` (white on `#00c3fe` is too faint) | `#fff` |
| header | navy gradient `#200058 → #0a5fa6`, white Ta3leem logo | teal gradient, white «المدرسة الإلكترونية» logo |
| footer | «تعليم · المنهج الرقميّ التفاعليّ» | «المدرسة الإلكترونية · المنهج الرقميّ التفاعليّ» |
| page background | `#f4f8f8` (unchanged) | `#f4f8f8` |

High contrast (`html.hc`) beats both themes.

## How it is built

- `tools/theme.py <files>` adds all of this to lab html files and skips files that already have it. It does the
  following:
  - adds the head script;
  - adds a `<style id="lab-theme">` block with the Rubik font, the ta3leem variables, the header, and the logo/footer
    swap;
  - switches the CSS to `--c-on-primary` / `--c-primary-ink`;
  - replaces the brand literals in JS with `LAB_TC`;
  - makes the hand-built model materials `paint_08798c` / `paint_04525f` follow the theme;
  - adds the second logo and the footer spans;
  - switches the video-player teal to the variables.
- `tools/build.py` runs `theme.patch()` on every lesson it builds. `tools/embed-video.py` writes a player that already
  uses the variables.
- The assets are in `tools/theme-assets/`: the Rubik woff2 files (`@fontsource-variable/rubik`, OFL), the Ta3leem logo
  (white, for the dark header, 188×120 webp) and the favicon.

## Done when (test every file)

- `?theme=ta3leem` and `?theme=eschool` each show their own theme everywhere, including what JS draws.
- No parameter, `?theme=` and `?theme=anything-else` look exactly like ta3leem.
- `?foo=1&theme=eschool` shows eschool, and so does ` ESchool ` (it is trimmed and lowercased).
- A hard reload of `?theme=eschool` never shows ta3leem, even briefly: `data-theme` is set before `<body>` exists.
- Nothing named `theme` in localStorage or cookies.

**Limit:** the recorded video inside the `-with-video` files is a picture of the lab. The player around it follows the
theme, but the frames keep the colours the lab had when it was recorded (eschool teal). For a ta3leem-coloured video,
record again with `?theme=ta3leem` (make-video.sh / record-demo.js).
