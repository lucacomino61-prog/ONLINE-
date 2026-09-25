---
name: logo-creation
description: Designs a new logo end to end the way the minimalist masters and top identity studios work (Rams, Vignelli, Rand, Müller-Brockmann, Aicher, MUJI, Chermayeff & Geismar & Haviv, Pentagram, Experimental Jetset, Build, Spin, OK-RM, Norm, Order) and produces a ready-to-use logo set - outlined SVG wordmark, stacked version, reverse and one-colour versions, icon, favicon.ico, app icons, social avatar, PNGs, a proof sheet and a one-page usage guide. Use this skill whenever the user asks to make, design, create, redesign, refresh or simplify a logo, wordmark, logotype, monogram, brand mark, favicon or app icon for a business, shop, bar, restaurant, studio, app or person - including casual requests like "make me a logo for my cafe", "new logo matching my website", or "minimal logo for X", even if they do not say "skill" or "identity".
---

# Logo creation

Make one excellent, minimal logo and everything needed to use it. The method comes from how the
masters and the best identity studios work (details in `references/masters-and-studios.md`):
find the one true thing, fix the constraints first, explore widely by eye, build it precisely,
test it hard at small sizes and in one colour, write the rules on one page, and present one
confident recommendation.

## What "done" means

Inside the user's project (default `brand/<slug>/`, or the current folder if there is no project):

- `logo/<slug>-logo.svg` primary, plus `-reverse`, `-ink`, `-paper` (one colour), `-black` (pure black for receipts and stamps) and `-currentcolor` (for inlining in a website)
- `logo/<slug>-logo-stacked.svg` and `-stacked-reverse` when a stacked version helps (square spaces, cups, signs)
- `logo/<slug>-icon.svg` (circle) and `-icon-square.svg` (app icon, social avatar)
- `png/` exports, `favicon.ico`, `apple-touch-icon.png`, `icon-192/512.png`, `app-icon-1024.png` (opaque, for app stores), `<slug>-avatar-1080.png`
- `proof.png` (every version, small sizes, light and dark header), `source/logo.json` (rebuildable), `source/metrics.json`
- `README.md` - one page of rules, from `assets/brand-readme-template.md`

Every SVG is outlined type: it needs no font installed and renders the same everywhere.

## Workflow

Scripts live in this skill's `scripts/` folder; run them with `python` (`py` on Windows). Look at every
PNG a script produces (open it with your image-reading tool): type is judged by eye, and the pictures
are the only way to see what you are making. Look at the sheets at the decision points below, not after
every tiny change.

### 1. Brief: find the one true thing

- Collect the exact name (spelling, case), what the business is, where, for whom, and what already exists:
  website, sign, colours, current logo, the user's constraints ("minimal", "match my site").
- If there is a website, read it: `python scripts/site_palette.py <url>`. It lists the colour variables (light and
  dark), most used colours, fonts and the current logo markup. A new logo should inherit this, not fight it
  (Bierut distils what a brand already has before inventing anything).
- Write one sentence: "<Name> is <what> for <whom>; the one thing to say is <X>." Spin asks "what's the clearest
  way of explaining my idea?"; OK-RM finds a project's key point and magnifies only that.
- Do not invent facts: no founding year, slogan, award, address or price that the user or a source did not give.
  Mockups use placeholders like `[PRICE]`.
- Ask the user only if the name itself is unclear. Otherwise decide, and state your assumptions in the final message.

### 2. Constraints: fix the rules before drawing

- **Colours:** an ink and a paper (taken from the website when there is one), plus at most one accent used for one
  small detail. Check with `python scripts/contrast.py ink=#... paper=#... accent=#...`: letters need 4.5:1; an
  accent under 3:1 on its ground may only be decorative (a dot, never letters).
- **Typeface:** one display family, from an independent foundry, under the SIL Open Font License, so the owner can
  use it anywhere. Pick candidates by voice from `references/type-shortlist.md`. Avoid system fonts (Georgia,
  Arial) and overused faces for the mark itself.
- **Form:** a wordmark first. The name, well set, is usually the whole logo. Add a symbol only if the brief truly
  needs one, and never a picture of the product (Rand: a logo identifies, it does not describe).

### 3. Explore: many options, then a few, then one

- `python scripts/contact_sheet.py "<Name>" --preset default --ink "#..." --paper "#..." --out <work>/sheet-1.png`
  (other presets: `calm-serif`, `classic-contrast`, `warm-serif`, `neutral-sans`, `condensed`, `expressive`; or
  `--font "Family:axis=value,...[:italic]"`, repeatable). Look at it.
- Shortlist 2-3. Make a second sheet of those in different weights, optical sizes, case and tracking, plus the accent
  idea (`--accent "#..." --accent-glyph N`). Judge at both sizes on the sheet: the small one is what most people see.
- Choose one, and write one line on why (fits the brief, legible small, distinct, will not date).

### 4. Build: write the config, generate outlines

- Copy `assets/logo.example.json` (the Bar Martiri logo: Newsreader, site colours, berry dot on the last i) to
  `brand/<slug>/source/logo.json` and edit it: name, slug, colours, font and axes, wordmark text, tracking, kern,
  accent, stacked lines, icon letter. `out` is the brand folder relative to the config file: keep `".."` when the
  config sits in `brand/<slug>/source/`, so the files land in `brand/<slug>/logo/` and `brand/<slug>/png/`.
- `python scripts/build_logo.py brand/<slug>/source/logo.json`. It prints the glyph indices (for `kern` and
  `accent`), the aspect ratios, minimum sizes and contrast, and writes all SVGs.
- Tune the spacing at large size, then rebuild: the word space and tracking are where craft shows (Norm and Build
  treat this as the job). Numbers and methods are in `references/craft-rules.md`.

### 5. Test: the Chermayeff & Geismar & Haviv test

- `python scripts/proof.py brand/<slug>/source/logo.json` and look at `proof.png`:
  - it reads as an icon at 16 px, and as a wordmark at its minimum width;
  - it works in one colour and reversed, and in a light and a dark website header;
  - spacing looks even and no hairline breaks up at small sizes;
  - the accent appears once, and the logo still works if the accent disappears;
  - you could describe it in one sentence and redraw it from memory.
- Fix and rebuild until every point passes. If the design fails the memory test, the idea is too weak, not the craft.

### 6. Deliver: one page of rules, one recommendation

- `python scripts/export_png.py brand/<slug>/source/logo.json` (PNGs, favicons, avatar, favicon.ico).
- Write `brand/<slug>/README.md` from `assets/brand-readme-template.md`, filling the numbers from
  `source/metrics.json`. Aicher fixed Munich 1972 in a manual before anything was printed; Order keeps rules short and
  public. One page is enough.
- Show the user `proof.png` with whatever the environment offers for showing files (a file-sending tool, an artifact,
  or the path). Present one recommendation with 3-5 lines of reasoning tied to the brief (Rand showed one solution),
  and name the runners-up in one line so the user can redirect.
- If the business has a website, include the header snippet and favicon tags from the README.
- Commit or push only if the user asked or the environment's own instructions require it.

**Revisions:** when the user asks for changes ("more minimal", "use my site colours", "bolder"), edit `logo.json` and
rebuild instead of starting over; re-run the contact sheet only if the typeface itself should change.

## Design rules (the research, distilled)

1. **One idea.** Identify, don't describe (Rand; Haviv: "a logo is not communication, it's identification").
2. **Distil what exists** before inventing (Bierut on Mastercard: "a process of distillation"; Order starts from archives).
3. **Constraints first:** one typeface, ink + paper + at most one accent, one module (Vignelli, Müller-Brockmann, Norm: "we narrow the fields of what is possible").
4. **Less, but better** (Rams): every element must do a job. If removing it changes nothing, remove it.
5. **Built for small and one colour** (Chermayeff & Geismar & Haviv): the icon must hold at 16 px, and every version must work in black.
6. **Permanence over trend:** no gradients, shadows, effects or fashionable gimmicks in the mark ("we've never done a swoosh").
7. **Let materials and products speak** (MUJI): the mark stays small and quiet on cups, signs and packaging.
8. **Rules on one page** (Aicher, Vignelli, Order): colours with roles, clear space, minimum sizes, don'ts.
9. **One confident answer** (Rand), with the alternatives visible but secondary.
10. **Craft over self-expression** (Norm, Build): spacing, weight and optical size are the design.
11. **Truth:** no invented facts, anywhere, including mockups.
12. **Accessible:** letters at least 4.5:1 on their ground; every SVG has a title and aria-label.

## Scripts

| Script | Does |
| --- | --- |
| `site_palette.py <url> [--json f]` | Colours (light and dark), fonts, manifest, current logo markup of a live site |
| `contrast.py name=#hex ...` | WCAG contrast between brand colours, with what each pair may be used for |
| `contact_sheet.py "<Name>" [--preset p] [--font spec] ...` | The name in many typefaces, large and small, as one PNG |
| `build_logo.py <logo.json>` | All SVG versions, glyph indices, metrics.json |
| `proof.py <logo.json>` | proof.png: every version, small sizes, light and dark header, colours |
| `export_png.py <logo.json>` | PNG set, favicons, app icons, avatar, favicon.ico |

`logo_lib.py` holds the shared code: Google Fonts download (subset to the name's characters, variable axes and kerning kept), HarfBuzz shaping, outlines, contrast, and headless-browser rendering.

## References

- `references/masters-and-studios.md`: how each master and studio works, with sources. Read it when choosing the direction or explaining the reasoning.
- `references/type-shortlist.md`: vetted open-licence display faces by voice, with axis settings. Read it at step 2.
- `references/craft-rules.md`: spacing, optical size, accent, stacked, icon, sizes, favicon set, SVG hygiene, website snippet and the pre-delivery checklist. Read it at steps 4-6.

## Setup

- Python 3.9+ with `pip install fonttools brotli uharfbuzz pillow`.
- A Chromium-based browser for PNGs: Chrome, Edge (always present on Windows) or Chromium. The scripts find installed Chrome, Edge, Chromium and Playwright's own Chromium by themselves; if none is found, set `LOGO_BROWSER` to its path. When each command runs in a fresh shell, put `LOGO_BROWSER=...` in front of every command rather than exporting it once.
- Fonts download from Google Fonts on first use and are cached in `~/.cache/logo-creation` (change with `LOGO_CACHE`). A licensed local font works too: `{"file": "path/to/font.otf"}` in the config, or `--font "file:path"`.
- Behind a proxy that re-signs TLS, point `SSL_CERT_FILE` at its CA bundle. Never disable certificate checks.
