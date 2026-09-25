# Craft rules

The numbers behind steps 4-6. Font units assume a 2000 UPM font (Newsreader, Bodoni Moda); for a 1000 UPM
font halve them. `build_logo.py` prints the glyph indices you need for `kern` and `accent`.

## Spacing

- **Tracking** (`wordmark.tracking`): display sizes want slightly tighter spacing than text. Start at -10 and
  go down to -20 for serif wordmarks; all-caps wordmarks usually want positive tracking (+40 to +120).
- **Word space** (`wordmark.kern`: `{"<index of the second word's first glyph>": -50}`): a default word space
  reads as two words set in a font; tightening it by 40-70 units makes one name. Bar Martiri uses -50.
- **Pairs:** check `Ma`, `ar`, `rt`, `Te`, `Av`, `To`, `ry`, `LT` and round-straight joins at large size.
  Adjust single pairs with `kern` entries of 10-40 units. Even rhythm matters more than any single pair.
- Judge spacing at large size, then confirm at 20 px: small sizes forgive less than you expect.

## Weight and optical size

- Choose weight for the smallest real use (favicon, receipt, sachet), then check the large version still
  looks refined. Serif wordmarks: 450-500 on a 400 Regular. Sans wordmarks: 500-650.
- On families with an `opsz` axis, use the display end (48-72) for elegance, unless hairlines break up in the
  proof; then drop to 6-24 for sturdier hairlines. Bar Martiri: Newsreader opsz 72, wght 460.
- Italic wordmarks lean right: centre a stacked italic line 0.05-0.1 em left of the true centre
  (`stacked.shift_em`), and nudge an italic icon letter left by 1-3 % (`icon.shift`).

## Case

- Sentence case ("Bar Martiri") reads calm and friendly; all caps reads formal and sign-like and needs
  positive tracking; lowercase reads casual and tech. Match the brief's voice.

## Accent

- At most one accent colour, on one detail: the dot of an i or j (`"part": "dot"`), one glyph
  (`"part": "glyph"`), or nothing. Bar Martiri: the berry dot on the last i, the site's sunset colour.
- The logo must still work if the accent disappears: the `-ink` and `-paper` versions drop it, and so does
  every one-colour use.
- An accent under 3:1 on its ground is decorative only; never use it for letters.

## Stacked version

- For square or narrow spaces. Lines centred on the widest line; gap 0.18-0.25 × cap height
  (`stacked.gap`, default 0.22).
- Break at the natural word boundary, or at the seam of a compound name ("Tide / pool"); don't split a short
  single word.

## Icon

- The first letter of the name (or two, for a strong monogram) in the same face, paper on an ink circle for
  favicons and an ink square for app icons and avatars (platforms round the corners themselves).
- Letter size: `icon.font_size` 300-340 in the 512 box (the letter fills about 40-45 % of the circle).
  Centred by its bounding box, then nudged optically if needed.
- Keep important shapes inside the central 80 % circle: Android and PWAs crop "maskable" icons to it.
- A single letter in a circle is common. If the brief needs a more ownable icon, make the accent the rule
  (Experimental Jetset): the dot, the crop, or one line repeated everywhere.
- The icon can carry the accent: `"icon": {"text": "i", "font_size": 360, "accent": {"glyph": 0, "part": "dot"}}`
  gives an i whose dot takes the accent colour (`accent_color` picks another palette key). A lone i can read as an
  "info" sign, so use it when the dot is already the brand's known signature, and check it at 16 px.
- **Sister brands** (a second business that must look like the same family): keep the typeface, colours and
  accent, but take the icon letter from the word that tells them apart ("Martiri Gelato" uses G, because Bar
  Martiri already owns M). Two-letter monograms rarely survive 16 px: test them at true size before choosing one.

## Clear space and minimum sizes

- Clear space: the x-height of the wordmark on every side (metrics.json gives it as a ratio of logo height).
- Minimum sizes come from legibility: the x-height stays at least 8 px on screen and 2 mm in print.
  `build_logo.py` computes them. Bar Martiri: wordmark 96 px / 24 mm, stacked 64 px / 16 mm, icon 16 px.

## Colour

- Ink and paper from the brand (read the website first). Record hex and RGB and each colour's role.
- For print, tell the owner to match colours to a physical swatch with their printer; don't publish Pantone or
  CMYK values you have not measured.
- Contrast: letters 4.5:1 minimum on their ground (3:1 at 24 px and up); icon shapes 3:1.

## Files

- SVG: outlined paths, tight viewBox, `<title>` plus `role="img"` and `aria-label`, no fonts, styles or scripts.
- `-currentcolor.svg`: letters use `currentColor`, the accent keeps its hex, so the logo follows light and dark
  mode when inlined in a page.
- PNG: wordmark 2400 px wide, stacked 1600, avatar 1080 square; favicons 32/48/96; manifest icons 192 and 512;
  `apple-touch-icon.png` 180 and `app-icon-1024.png` (App Store, Xcode) opaque and square; `favicon.ico` with 16, 32
  and 48.

## Website snippet (goes in the README)

```html
<a class="wordmark" href="/" aria-label="Brand name, home">
  <!-- paste logo/<slug>-logo-currentcolor.svg here and add aria-hidden="true" to the <svg> -->
</a>
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon-96.png" type="image/png" sizes="96x96">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
```

```css
.wordmark svg { display: block; height: 22px; width: auto; }
```

If the site already has icons, give the new files the same names and sizes so they drop in.

## Mockups and presentation

- Show the logo where it will live (the site header, a cup, a sign, a receipt) using only real facts. Anything
  unknown is a placeholder: `[ADDRESS]`, `[PRICE]`, `[TAX NUMBER]`.
- Present one recommendation. Name the runners-up in one line so the user can redirect.

## Pre-delivery checklist

- [ ] The one-sentence brief is written and the logo expresses one idea
- [ ] Colours come from the brand (or the brief); contrast checked
- [ ] One typeface, open-licensed or licensed by the owner, credited in the README
- [ ] Spacing checked at large size, legible at 20 px
- [ ] Accent used once; the one-colour versions work without it
- [ ] Icon reads at 16 px
- [ ] proof.png looked at; reverse and dark header checked
- [ ] PNGs, favicon.ico, app icons exported
- [ ] README written from the template with real numbers from metrics.json
- [ ] No invented facts anywhere
