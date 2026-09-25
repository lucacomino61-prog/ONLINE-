# Bar Martiri — logo

A minimal wordmark for Bar Martiri, Spille. It uses the colours of the live site,
[barmartiri.com](https://www.barmartiri.com/): ink letters on paper, and the site's
berry pink for one detail only, the dot on the last *i*.

Presentation (private canvas): https://claude.ai/artifact/11jyyNycZqLzooSwPaK6Dm

## Files

| File | Use |
| --- | --- |
| `logo/bar-martiri-logo.svg` | Primary: ink + berry dot, on paper or any light ground |
| `logo/bar-martiri-logo-reverse.svg` | Paper + berry dot, on ink or dark photos |
| `logo/bar-martiri-logo-ink.svg` | One colour, ink only: receipts, stamps, engraving |
| `logo/bar-martiri-logo-paper.svg` | One colour, paper only, on dark |
| `logo/bar-martiri-logo-currentcolor.svg` | For inlining in the website: letters take the text colour, so it follows light and dark mode |
| `logo/bar-martiri-logo-stacked.svg`, `-stacked-reverse.svg` | Square or narrow spaces: cups, bags, menu covers |
| `logo/bar-martiri-icon.svg` | Paper M on an ink circle: favicon, small spaces |
| `logo/bar-martiri-icon-square.svg` | Full square: app icon, social avatar |
| `png/` | The same at print/screen sizes, plus `favicon.ico`, `favicon-96.png`, `apple-touch-icon.png` (180), `icon-192.png`, `icon-512.png`, `bar-martiri-avatar-1080.png` |

`favicon-96.png` and `apple-touch-icon.png` have the same names and sizes as the icons
the site references today (`assets/optimized/`), so they can replace them directly.

## Colours (the site's CSS variables)

| Name | Hex | RGB | Role |
| --- | --- | --- | --- |
| Ink (`--ink`) | `#151515` | 21 21 21 | The letters |
| Paper (`--paper`) | `#F4F0E8` | 244 240 232 | The ground |
| Berry (`--berry`) | `#E55C87` | 229 92 135 | The dot on the last *i*, nothing else |

Ink on Paper is 16:1 contrast. Berry on Paper is only 3:1, too light for text, so it never
colours letters. For print, have the printer match colours to a physical proof.

## Typeface

Newsreader by Production Type, display optical size (72), weight 460, SIL Open Font
License. The logo files are outlines, so no font needs to be installed to use them.
The website keeps its own type (Georgia headlines, Inter labels).

## Rules

- **Clear space:** the height of the lowercase *a* on every side.
- **Minimum size:** wordmark 96 px / 24 mm wide, stacked 64 px / 16 mm, icon 16 px / 5 mm.
  Smaller than that, use the next mark down.
- **Don't** stretch, rotate, recolour the letters, add shadows or effects, set it on busy
  colour or photos without enough contrast, or retype it in another font.

## On the website

Header: replace the text inside `<a class="wordmark">` with the contents of
`logo/bar-martiri-logo-currentcolor.svg` (add `aria-hidden="true"` to the `<svg>`; the link
already has an `aria-label`), then size it in CSS:

```css
.wordmark svg { display: block; height: 22px; width: auto; }
```

Icons:

```html
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="assets/optimized/favicon-96.png" type="image/png" sizes="96x96">
<link rel="apple-touch-icon" href="assets/optimized/apple-touch-icon.png">
```

## Rebuilding

```bash
cd source
pip install fonttools brotli uharfbuzz
python3 build_logo.py                           # logo/*.svg (fetches Newsreader into .fonts/ once)
NODE_PATH="$(npm root -g)" node export_png.js   # png/*.png (needs Playwright + Chromium)
python3 -c "from PIL import Image; Image.open('../png/icon-192.png').save('../png/favicon.ico', sizes=[(16,16),(32,32),(48,48)])"
```

Spacing, weight and colours are constants at the top of `source/build_logo.py`.
