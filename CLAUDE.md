# Rules for this repository

## Physics 3D labs (`labs/`): read before any change

- **Theme rule (always):** every lab follows `labs/THEME.md`.
  - `?theme=ta3leem|eschool` is read from `location.search` only, by an inline script at the top of `<head>`; the default is `ta3leem`.
  - Never use localStorage or cookies for the theme.
  - JS-drawn colours and fonts come from `window.LAB_TC`; never hard-code `#08798c` / `0x08798c` / `Alexandria` in JS.
  - The page, 3D scene and video-player backgrounds are the same in both themes.
  - Carry `?theme=` onto any internal link.
  - New or rebuilt lab files go through `labs/tools/theme.py`. `build.py` already runs it.
  - Test the "Done when" list in THEME.md.
- Design, build and video work: `labs/LAB_UI_GUIDELINES.md`, `labs/LAB_VIDEO.md`, `labs/TEAM_PROMPT.md` (Arabic team guide).
- Narration scripts are in Iraqi Arabic. Never use non-Iraqi words such as «بشويش» (use «شوية شوية» / «على كيفك»).
