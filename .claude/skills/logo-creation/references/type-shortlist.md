# Type shortlist for logos

Open-licence (SIL OFL) display families on Google Fonts, mostly from independent foundries and designers,
checked for logo use. The OFL lets the owner use, modify and embed the font commercially, so the logo and
everything around it stays legal. Designers are as listed by Google Fonts (September 2026).

Spec strings work directly with `contact_sheet.py --font`. Axis values are good starting points for a
wordmark; tune weight and optical size on a second sheet.

## Choosing by voice

Match the brief's one sentence, not personal taste:

| Voice | Suits | Group |
| --- | --- | --- |
| Calm, editorial, quietly premium | hospitality, cafés, hotels, galleries, consultants | calm serif |
| Classic, Italian, fashion, high contrast | restaurants, fashion, beauty, wine | classic contrast |
| Warm, friendly, food, craft | bakeries, ice cream, delis, kids | warm serif |
| Modern, neutral, precise | tech, apps, studios, clinics | neutral sans |
| Loud, sign-like, sport, street | bars, gyms, events, streetwear | condensed |
| Playful, art, culture | festivals, music, art spaces | expressive |

## Calm serif (`--preset calm-serif`)

| Spec | Designer | Notes |
| --- | --- | --- |
| `Newsreader:opsz=72,wght=460` | Production Type | Axes opsz 6-72, wght 200-800. Used for Bar Martiri: editorial and calm, sturdy at 20 px at weight 450-480. |
| `Literata:opsz=72,wght=450` | TypeTogether | opsz 7-72, wght 200-900. Warmer, bookish. |
| `Source Serif 4:opsz=60,wght=450` | Frank Grießhammer | opsz 8-60. Crisp, slightly corporate. |
| `Castoro` | Tiro Typeworks | Static Regular and Italic. Sturdy Dutch-style serif, good small. |
| `Gelasio:wght=450` | Eben Sorkin | Metric-compatible with Georgia: use when a site's headlines are Georgia and the logo must feel native. |
| `Spectral:wght=400` | Production Type | Static weights. Light and elegant; check small sizes. |

## Classic contrast (`--preset classic-contrast`)

| Spec | Designer | Notes |
| --- | --- | --- |
| `Bodoni Moda:opsz=6,wght=900:italic` | Owen Earl | opsz 6-96, wght 400-900. Bodoni is Italian (Parma). For logos keep opsz 6-11: from opsz 24 up the hairlines vanish at small sizes. |
| `Libre Bodoni:wght=500` | Pablo Impallari, Rodrigo Fuenzalida | wght 400-700. Sturdier Bodoni. |
| `Libre Caslon Display` | Impallari Type | Beautiful large, fragile hairlines small: pair with a sturdier icon. |
| `Imbue:opsz=100,wght=400` | Tyler Finck (ETC) | Condensed didone, opsz 10-100, wght 100-900. |
| `Cormorant:wght=600` | Christian Thalmann | wght 300-700. Garamond-like display; use 600+ for small sizes. |
| `Playfair Display:wght=500` | Claus Eggers Sørensen | Very common on the web: avoid for the mark unless asked. |

## Warm serif (`--preset warm-serif`)

| Spec | Designer | Notes |
| --- | --- | --- |
| `Fraunces:opsz=72,wght=600,SOFT=50` | Undercase Type (Phaedra Charles, Flavia Zimbardi) | Axes SOFT 0-100, WONK 0-1, opsz 9-144, wght 100-900. Popular with food brands. |
| `Young Serif` | Bastien Sozeau | Static, heavy and friendly. |
| `DM Serif Display` | Colophon Foundry | Static Regular and Italic. |
| `Gloock` | Duarte Pinto | Static, high contrast with character. |
| `Instrument Serif` | Rodrigo Fuenzalida, Jordan Egstad | Condensed, lovely italic; very common on award-winning sites since 2023, so it can look trendy. |
| `EB Garamond:wght=500` | Georg Duffner, Octavio Pardo | wght 400-800. Classic book face. |

## Neutral sans (`--preset neutral-sans`)

| Spec | Designer | Notes |
| --- | --- | --- |
| `Inter:opsz=32,wght=600` | Rasmus Andersson | opsz 14-32 (32 = Inter Display), wght 100-900. Everywhere in UI: fine to match a site, weak as a distinctive mark. |
| `Instrument Sans:wght=600` | Rodrigo Fuenzalida, Jordan Egstad | wdth 75-100, wght 400-700. |
| `Geist:wght=500` | Vercel (Andrés Briganti, Mateo Zaragoza, Guillermo Rauch, Evil Rabbi) | wght 100-900. Tech voice. |
| `Archivo:wdth=100,wght=600` | Omnibus-Type | wdth 62-125, wght 100-900: one family from condensed to wide. |
| `Hanken Grotesk:wght=600` | Alfredo Marco Pradil, Hanken Design Co. | wght 100-900. |
| `Schibsted Grotesk:wght=600` | Bakken & Bæck, Henrik Kongsvoll | wght 400-900. |

## Condensed (`--preset condensed`)

| Spec | Designer | Notes |
| --- | --- | --- |
| `League Gothic:wdth=100` | Tyler Finck, Caroline Hadilaksono, Micah Rich | wdth 75-100. Classic sign gothic. |
| `Sofia Sans Extra Condensed:wght=800` | Lettersoup, Botio Nikoltchev, Ani Petrova | wght 1-1000. |
| `Archivo:wdth=62,wght=800` | Omnibus-Type | Strong, legible condensed. |
| `Anybody:wdth=60,wght=800` | Tyler Finck | wdth 50-150; below 60 the counters close. |
| `Bricolage Grotesque:opsz=96,wdth=75,wght=700` | Mathieu Triay | opsz 12-96, wdth 75-100, wght 200-800. |
| `Instrument Sans:wdth=75,wght=700` | Rodrigo Fuenzalida, Jordan Egstad | Quiet condensed. |

## Expressive (`--preset expressive`)

| Spec | Designer | Notes |
| --- | --- | --- |
| `Syne:wght=700` | Bonjour Monde, Lucas Descroix, George Triantafyllakos | wght 400-800; widens as it gets bolder. |
| `Bricolage Grotesque:opsz=96,wght=700` | Mathieu Triay | Ink traps at large sizes. |
| `Unbounded:wght=500` | NaN | wght 200-900, wide and round. |
| `Fraunces:opsz=144,wght=900,WONK=1` | Undercase Type | Wonky, 70s. |
| `Anybody:wdth=120,wght=700` | Tyler Finck | Wide end of Anybody. |
| `Funnel Display:wght=600` | NORD ID, Kristian Möller | wght 300-800. |

## Any other Google font

`--font "Family Name"` works for every Google Fonts family: `logo_lib.py` reads Google's metadata, requests all
axes and styles, and subsets the font to the characters of the name. A licensed local font works with
`--font "file:path/to/font.otf:wght=500"` (check its licence allows logo use).

## Rules of thumb

- The mark should be a notch more crafted than the site's body text. If the site uses Georgia or Inter, the logo
  can harmonise with them (Gelasio, Newsreader; Inter Display) without being the same system font.
- Prefer faces with an optical-size axis: display sizes look refined, and a lower optical size gives sturdier
  hairlines for small print (Bodoni Moda at opsz 6 has hairlines about twice as thick as at opsz 11).
- Weight: a touch above the family's Regular (450-500 for a serif wordmark) so it holds at 20 px.
- Avoid for the mark itself: system fonts (Georgia, Arial, Helvetica, Times), and faces so common they read as
  default (Montserrat, Poppins, Bebas Neue, Playfair Display) unless the user asks for them.
