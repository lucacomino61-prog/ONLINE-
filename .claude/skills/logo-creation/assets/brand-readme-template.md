# {{Name}} — logo

{{One or two sentences: what the logo is and the one idea behind it, e.g. "A calm wordmark in the site's ink and
paper; the only colour is the berry dot on the last i, the site's sunset colour."}}

![Proof](proof.png)

## Files

| File | Use |
| --- | --- |
| `logo/{{slug}}-logo.svg` | Primary{{, ink + accent}}, on {{paper}} or any light ground |
| `logo/{{slug}}-logo-reverse.svg` | On {{ink}} or dark photos |
| `logo/{{slug}}-logo-ink.svg` | One colour, ink only: receipts, stamps, engraving, anything printed in one colour |
| `logo/{{slug}}-logo-paper.svg` | One colour, paper only, on dark |
| `logo/{{slug}}-logo-currentcolor.svg` | For inlining in a website: letters take the text colour (light and dark mode) |
| `logo/{{slug}}-logo-stacked.svg`, `-stacked-reverse.svg` | Square or narrow spaces |
| `logo/{{slug}}-icon.svg` | Icon on a circle: favicon, small spaces |
| `logo/{{slug}}-icon-square.svg` | Full square: app icon, social avatar |
| `png/` | The same as PNG, plus `favicon.ico`, `favicon-32/48/96.png`, `apple-touch-icon.png`, `icon-192.png`, `icon-512.png`, `{{slug}}-avatar-1080.png` |

## Colours

| Name | Hex | RGB | Role |
| --- | --- | --- | --- |
| {{Ink name}} | `{{#hex}}` | {{r g b}} | The letters |
| {{Paper name}} | `{{#hex}}` | {{r g b}} | The ground |
| {{Accent name}} | `{{#hex}}` | {{r g b}} | {{The one detail, nothing else}} |

{{Ink}} on {{paper}} is {{contrast}}:1 contrast. {{Accent sentence, e.g. "Berry on paper is only 3:1, so it never colours letters."}}
For print, have the printer match the colours to a physical proof.

## Typeface

{{Family}} by {{designer}}, {{axes, e.g. display optical size (72), weight 460}}, {{licence, e.g. SIL Open Font
License}}. The logo files are outlines, so no font needs to be installed to use them.

## Rules

- **Clear space:** the height of the lowercase *{{letter}}* on every side.
- **Minimum size:** wordmark {{px}} px / {{mm}} mm wide, stacked {{px}} px / {{mm}} mm, icon 16 px / 5 mm.
  Smaller than that, use the next mark down.
- **Don't** stretch, rotate, recolour the letters, add shadows or effects, place it on busy colour or photos
  without enough contrast, or retype it in another font.

## On the website

{{Only if there is a website: the header snippet (inline currentColor SVG with aria-hidden, CSS height) and the
favicon link tags, using the site's existing icon file names where possible. Otherwise delete this section.}}

## Rebuilding

The logo is generated from `source/logo.json` with the logo-creation skill's scripts:

```bash
python <skill>/scripts/build_logo.py source/logo.json
python <skill>/scripts/export_png.py source/logo.json
python <skill>/scripts/proof.py source/logo.json
```
