#!/usr/bin/env python3
"""Build a complete logo set as outlined SVG from a JSON config.

    python build_logo.py path/to/logo.json

Writes <out>/logo/<slug>-*.svg and <config dir>/metrics.json. See assets/logo.example.json
for every field. Letters are converted to outlines, so no font is needed to use the files.
"""
import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import logo_lib as L  # noqa: E402

SIZE = 300          # font size of wordmark and stacked, in SVG units
ICON_BOX = 512      # icons are drawn in a 512 x 512 box


def part_font(cfg, part):
    return cfg.get(part, {}).get('font') or cfg['font'], cfg.get(part, {}).get('axes') or cfg.get('axes', {})


def all_text(cfg):
    txt = cfg['wordmark']['text']
    txt += ''.join(cfg.get('stacked', {}).get('lines', []))
    txt += cfg.get('icon', {}).get('text', '')
    return txt


def paths(body_d, accent_d, fill, accent_fill):
    if accent_d and accent_fill:
        return f'<path fill="{fill}" d="{body_d}"/><path fill="{accent_fill}" d="{accent_d}"/>'
    return f'<path fill="{fill}" d="{body_d}{accent_d}"/>'


def wordmark(cfg):
    w = cfg['wordmark']
    source, axes = part_font(cfg, 'wordmark')
    return L.outline(w['text'], source, axes, SIZE, kern=w.get('kern'), track=w.get('tracking', 0),
                     accent=w.get('accent'), features=w.get('features'), font_text=all_text(cfg))


def stacked(cfg):
    st = cfg['stacked']
    source, axes = part_font(cfg, 'wordmark')
    track = st.get('tracking', cfg['wordmark'].get('tracking', 0))
    lines = st['lines']
    acc = st.get('accent') or {}
    shifts = st.get('shift_em') or [0] * len(lines)
    ft = all_text(cfg)
    first = [L.outline(t, source, axes, SIZE, track=track, font_text=ft) for t in lines]
    m = first[0]['metrics']
    gap = SIZE * m['cap'] / m['upm'] * st.get('gap', 0.22)
    ref = max(first, key=lambda o: o['bbox'][2] - o['bbox'][0])['bbox']
    align = st.get('align', 'center')
    out, y = [], 0.0
    for i, (text, o) in enumerate(zip(lines, first)):
        b = o['bbox']
        if i:
            y = out[-1]['bbox'][3] + gap - b[1]
        if align == 'left':
            x = ref[0] - b[0]
        elif align == 'right':
            x = ref[2] - b[2]
        else:
            x = (ref[0] + ref[2]) / 2 - (b[0] + b[2]) / 2
        x += shifts[i] * SIZE
        a = {'glyph': acc['glyph'], 'part': acc.get('part', 'dot')} if acc and acc.get('line') == i else None
        out.append(L.outline(text, source, axes, SIZE, x=x, y=y, track=track, accent=a, font_text=ft))
    bbox = (min(o['bbox'][0] for o in out), out[0]['bbox'][1],
            max(o['bbox'][2] for o in out), out[-1]['bbox'][3])
    return {'d': ''.join(o['d'] for o in out), 'accent_d': ''.join(o['accent_d'] for o in out),
            'bbox': bbox, 'metrics': m}


def icon(cfg, square):
    ic = cfg['icon']
    source, axes = part_font(cfg, 'icon')
    size = ic.get('font_size', 330)
    c = ICON_BOX / 2
    probe = L.outline(ic['text'], source, axes, size, font_text=all_text(cfg))['bbox']
    dx, dy = ic.get('shift', [0, 0])
    x = c - (probe[0] + probe[2]) / 2 + dx * ICON_BOX
    y = c - (probe[1] + probe[3]) / 2 + dy * ICON_BOX
    # an icon may carry the accent too, e.g. a lowercase i whose dot takes the accent colour
    o = L.outline(ic['text'], source, axes, size, x=x, y=y, accent=ic.get('accent'), font_text=all_text(cfg))
    bg, fg = L.colour(cfg, ic.get('bg', 'ink')), L.colour(cfg, ic.get('fg', 'paper'))
    acc = L.colour(cfg, ic.get('accent_color', 'accent')) if ic.get('accent') else None
    shape = (f'<rect width="{ICON_BOX}" height="{ICON_BOX}" fill="{bg}"/>' if square
             else f'<circle cx="{c:g}" cy="{c:g}" r="{c:g}" fill="{bg}"/>')
    return L.svg_doc((0, 0, ICON_BOX, ICON_BOX), shape + paths(o['d'], o['accent_d'], fg, acc),
                     f"{cfg['name']} icon")


def min_width(aspect, xh_ratio, xh_min):
    """Smallest width at which the x-height is still xh_min tall."""
    return aspect / xh_ratio * xh_min


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('config')
    cfg = L.load_config(ap.parse_args().config)
    slug, name = cfg['slug'], cfg['name']
    ink, paper = cfg['colors']['ink'], cfg['colors']['paper']
    accent = cfg['colors'].get('accent') if cfg['wordmark'].get('accent') else None
    out = cfg['_out'] / 'logo'
    out.mkdir(parents=True, exist_ok=True)
    files, metrics = {}, {}

    wm = wordmark(cfg)
    print('wordmark glyphs (index: name) for "kern" and "accent":',
          ', '.join(f'{i}: {g}' for i, g in enumerate(wm['glyphs'])))
    v = L.tight(wm['bbox'])
    files[f'{slug}-logo.svg'] = L.svg_doc(v, paths(wm['d'], wm['accent_d'], ink, accent), name)
    files[f'{slug}-logo-reverse.svg'] = L.svg_doc(v, paths(wm['d'], wm['accent_d'], paper, accent), name)
    files[f'{slug}-logo-ink.svg'] = L.svg_doc(v, paths(wm['d'], wm['accent_d'], ink, None), name)
    files[f'{slug}-logo-paper.svg'] = L.svg_doc(v, paths(wm['d'], wm['accent_d'], paper, None), name)
    files[f'{slug}-logo-currentcolor.svg'] = L.svg_doc(v, paths(wm['d'], wm['accent_d'], 'currentColor', accent), name)
    m = wm['metrics']
    xh = SIZE * m['xheight'] / m['upm']
    metrics['wordmark'] = {'aspect': round(v[2] / v[3], 3), 'xheight_ratio': round(xh / v[3], 3),
                           'min_width_px': math.ceil(min_width(v[2] / v[3], xh / v[3], 8) / 4) * 4,
                           'min_width_mm': math.ceil(min_width(v[2] / v[3], xh / v[3], 2))}

    if cfg.get('stacked'):
        st = stacked(cfg)
        v = L.tight(st['bbox'])
        files[f'{slug}-logo-stacked.svg'] = L.svg_doc(v, paths(st['d'], st['accent_d'], ink, accent), name)
        files[f'{slug}-logo-stacked-reverse.svg'] = L.svg_doc(v, paths(st['d'], st['accent_d'], paper, accent), name)
        metrics['stacked'] = {'aspect': round(v[2] / v[3], 3), 'xheight_ratio': round(xh / v[3], 3),
                              'min_width_px': math.ceil(min_width(v[2] / v[3], xh / v[3], 8) / 4) * 4,
                              'min_width_mm': math.ceil(min_width(v[2] / v[3], xh / v[3], 2))}

    if cfg.get('icon'):
        files[f'{slug}-icon.svg'] = icon(cfg, square=False)
        files[f'{slug}-icon-square.svg'] = icon(cfg, square=True)
        metrics['icon'] = {'min_width_px': 16, 'min_width_mm': 5}

    metrics['contrast'] = {'ink_on_paper': round(L.contrast(ink, paper), 2)}
    if cfg['colors'].get('accent'):
        metrics['contrast'].update(accent_on_paper=round(L.contrast(cfg['colors']['accent'], paper), 2),
                                   accent_on_ink=round(L.contrast(cfg['colors']['accent'], ink), 2))
    for fname, text in files.items():
        (out / fname).write_text(text, encoding='utf-8')
        print(f'{fname:44s} {len(text):>7,} bytes')
    (cfg['_dir'] / 'metrics.json').write_text(json.dumps(metrics, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(metrics, indent=2))


if __name__ == '__main__':
    main()
