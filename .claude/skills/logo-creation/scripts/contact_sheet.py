#!/usr/bin/env python3
"""Set a name in many typefaces side by side, large and small, to choose the logo's type.

    python contact_sheet.py "Bar Martiri" --preset default --out sheet.png
    python contact_sheet.py "Bar Martiri" --font "Newsreader:opsz=72,wght=460" \
        --font "Bodoni Moda:opsz=6,wght=900:italic" --font "file:C:/fonts/Brand.otf:wght=500"

Font spec: Google Fonts family, then optional axis values, then optional ":italic". Add track=N to the
values to set tracking for that candidate only ("Archivo:wdth=62,wght=800,track=40").
Colours default to ink #151515 on paper #F4F0E8; --accent/--accent-glyph preview an accent.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import logo_lib as L  # noqa: E402

PRESETS = {
    'calm-serif': ['Newsreader:opsz=72,wght=450', 'Literata:opsz=72,wght=450', 'Source Serif 4:opsz=60,wght=450',
                   'Castoro', 'Gelasio:wght=450', 'Spectral:wght=400'],
    'classic-contrast': ['Bodoni Moda:opsz=11,wght=700', 'Bodoni Moda:opsz=6,wght=900:italic',
                         'Libre Bodoni:wght=500', 'Libre Caslon Display', 'Imbue:opsz=100,wght=400',
                         'Cormorant:wght=600'],
    'warm-serif': ['Fraunces:opsz=72,wght=600,SOFT=50', 'Young Serif', 'DM Serif Display', 'Gloock',
                   'Instrument Serif', 'EB Garamond:wght=500'],
    'neutral-sans': ['Inter:opsz=32,wght=600', 'Instrument Sans:wght=600', 'Geist:wght=500',
                     'Archivo:wdth=100,wght=600', 'Hanken Grotesk:wght=600', 'Schibsted Grotesk:wght=600'],
    'condensed': ['League Gothic:wdth=100', 'Sofia Sans Extra Condensed:wght=800', 'Archivo:wdth=62,wght=800',
                  'Anybody:wdth=60,wght=800', 'Bricolage Grotesque:opsz=96,wdth=75,wght=700',
                  'Instrument Sans:wdth=75,wght=700'],
    'expressive': ['Syne:wght=700', 'Bricolage Grotesque:opsz=96,wght=700', 'Unbounded:wght=500',
                   'Fraunces:opsz=144,wght=900,WONK=1', 'Anybody:wdth=120,wght=700', 'Funnel Display:wght=600'],
}
PRESETS['default'] = ['Newsreader:opsz=72,wght=450', 'Literata:opsz=72,wght=450', 'Castoro',
                      'Bodoni Moda:opsz=6,wght=800', 'Fraunces:opsz=72,wght=500', 'Instrument Serif',
                      'Young Serif', 'Inter:opsz=32,wght=600', 'Instrument Sans:wght=600',
                      'Archivo:wdth=62,wght=800', 'Syne:wght=700', 'Space Grotesk:wght=500']

CELL_W, CELL_H, BIG, SMALL = 680, 170, 84, 20


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('text')
    ap.add_argument('--font', action='append', default=[])
    ap.add_argument('--preset', action='append', default=[], choices=sorted(PRESETS))
    ap.add_argument('--ink', default='#151515')
    ap.add_argument('--paper', default='#F4F0E8')
    ap.add_argument('--accent')
    ap.add_argument('--accent-glyph', type=int)
    ap.add_argument('--accent-part', default='dot', choices=['dot', 'glyph'])
    ap.add_argument('--tracking', type=float, default=0)
    ap.add_argument('--out', default='contact-sheet.png')
    a = ap.parse_args()
    specs = a.font + [s for p in a.preset for s in PRESETS[p]]
    if not specs:
        specs = PRESETS['default']
    accent = {'glyph': a.accent_glyph, 'part': a.accent_part} if a.accent and a.accent_glyph is not None else None
    cells = []
    for i, spec in enumerate(specs):
        x0, y0 = 20 + (i % 2) * (CELL_W + 20), 20 + (i // 2) * (CELL_H + 12)
        try:
            source, axes = L.parse_font_spec(spec)
            track = axes.pop('track', a.tracking)
            probe = L.outline(a.text, source, axes, BIG, track=track)
            w = probe['bbox'][2] - probe['bbox'][0]
            size = min(BIG, BIG * (CELL_W - 40) / max(w, 1))
            big = L.outline(a.text, source, axes, size, x=x0 + 20 - probe['bbox'][0] * size / BIG,
                            y=y0 + 118, track=track, accent=accent)
            small = L.outline(a.text, source, axes, SMALL, x=x0 + 20, y=y0 + 156, track=track, accent=accent)
            who = ', '.join(L.family_info(source['google'])['designers'][:2]) if 'google' in source else source['file']
            label = f'{i + 1}. {spec}  ·  {who}'
            body = ''
            for o in (big, small):
                body += f'<path fill="{a.ink}" d="{o["d"]}"/>'
                if o['accent_d']:
                    body += f'<path fill="{a.accent}" d="{o["accent_d"]}"/>'
        except SystemExit as e:
            label, body = f'{i + 1}. {spec}  ·  not available: {e}', ''
        label = label.replace('&', '&amp;').replace('<', '&lt;')
        cells.append(f'<rect x="{x0}" y="{y0}" width="{CELL_W}" height="{CELL_H}" fill="{a.paper}"/>'
                     f'<text x="{x0 + 20}" y="{y0 + 22}" font-family="monospace" font-size="12" '
                     f'fill="{a.ink}" fill-opacity=".6">{label}</text>{body}')
    rows = (len(specs) + 1) // 2
    W, H = 2 * CELL_W + 60, rows * (CELL_H + 12) + 28
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<rect width="{W}" height="{H}" fill="#d9d4ca"/>{"".join(cells)}</svg>')
    out = L.render_html(f'<!doctype html><html><body style="margin:0">{svg}</body></html>', a.out, W, H)
    print(out)


if __name__ == '__main__':
    main()
