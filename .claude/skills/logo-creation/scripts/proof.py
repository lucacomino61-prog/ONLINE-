#!/usr/bin/env python3
"""Render one proof sheet of the whole logo set, for looking at before delivering.

    python proof.py path/to/logo.json [--out proof.png]

Shows every version on its ground, the icon from 140 px down to 16 px, the wordmark down to its
minimum width, a light and a dark website header, and the colours with their contrast.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import logo_lib as L  # noqa: E402


def inline(path):
    if not path.exists():
        return ''
    svg = path.read_text(encoding='utf-8')
    return re.sub(r'\swidth="[^"]*"\s+height="[^"]*"', '', svg, count=1)


def box(svg, max_w, max_h=None, extra=''):
    """The SVG as large as fits in max_w x max_h, keeping its proportions."""
    if not svg:
        return ''
    w, h = L.svg_size(svg)
    width = min(max_w, (max_h or 10 ** 6) * w / h)
    return f'<div style="width:{width:.1f}px;line-height:0;{extra}">{svg}</div>'


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('config')
    ap.add_argument('--out')
    a = ap.parse_args()
    cfg = L.load_config(a.config)
    slug, src = cfg['slug'], cfg['_out'] / 'logo'
    ink, paper = cfg['colors']['ink'], cfg['colors']['paper']
    accent = cfg['colors'].get('accent')
    metrics_path = cfg['_dir'] / 'metrics.json'
    metrics = json.loads(metrics_path.read_text()) if metrics_path.exists() else {}
    min_px = metrics.get('wordmark', {}).get('min_width_px', 96)
    mid = min(160, round(min_px * 1.5))
    s = {k: inline(src / f'{slug}-{k}.svg') for k in (
        'logo', 'logo-reverse', 'logo-ink', 'logo-currentcolor', 'logo-stacked',
        'logo-stacked-reverse', 'icon', 'icon-square')}
    label = 'font:600 11px/1 system-ui,-apple-system,sans-serif;letter-spacing:.06em;text-transform:uppercase;opacity:.55'
    row = 'position:relative;display:flex;align-items:center;box-sizing:border-box;padding:0 48px'

    def tag(text, colour):
        return f'<span style="position:absolute;left:16px;top:12px;{label};color:{colour}">{text}</span>'

    chips = ''
    for name, hex_ in (('ink', ink), ('paper', paper), ('accent', accent)):
        if hex_:
            chips += (f'<div style="display:flex;align-items:center;gap:10px"><span style="width:36px;height:36px;'
                      f'border-radius:50%;background:{hex_};border:1px solid rgba(0,0,0,.15)"></span>'
                      f'<span style="font:13px/1.3 system-ui,sans-serif;color:{ink}">{name}<br>{hex_}</span></div>')
    c = f'ink on paper {L.contrast(ink, paper):.1f}:1'
    if accent:
        c += f' · accent on paper {L.contrast(accent, paper):.1f}:1 · accent on ink {L.contrast(accent, ink):.1f}:1'
    html = f'''<!doctype html><html><body style="margin:0;width:1200px">
<section style="{row};height:280px;background:{paper};justify-content:space-around">{tag('Primary · stacked', ink)}
  {box(s['logo'], 640, 180)}{box(s['logo-stacked'], 260, 180)}</section>
<section style="{row};height:220px;background:{ink};justify-content:space-around">{tag('Reverse', paper)}
  {box(s['logo-reverse'], 480, 140)}{box(s['logo-stacked-reverse'], 200, 140)}</section>
<section style="{row};height:200px;background:{paper};gap:28px">{tag(f'Icon 140 / 64 / 32 / 16 · wordmark 200 / {mid} / {min_px} (minimum) px', ink)}
  {box(s['icon'], 140)}{box(s['icon-square'], 140, None, 'border-radius:31px;overflow:hidden')}
  {box(s['icon'], 64)}{box(s['icon'], 32)}{box(s['icon'], 16)}
  <span style="width:24px"></span>{box(s['logo-ink'], 200, 64)}{box(s['logo'], mid, 36)}{box(s['logo'], min_px)}</section>
<section style="{row};height:64px;background:{paper};border-top:1px solid rgba(0,0,0,.12);border-bottom:1px solid rgba(0,0,0,.12);justify-content:space-between;color:{ink}">
  {box(s['logo-currentcolor'], 150, 26)}<span style="{label};color:{ink}">Website header · light</span></section>
<section style="{row};height:64px;background:#141414;justify-content:space-between;color:{paper}">
  {box(s['logo-currentcolor'], 150, 26)}<span style="{label};color:{paper}">Website header · dark</span></section>
<section style="{row};height:96px;background:{paper};gap:32px">{chips}
  <span style="font:13px/1.4 system-ui,sans-serif;color:{ink};margin-left:auto">{c}</span></section>
</body></html>'''
    out = Path(a.out) if a.out else cfg['_out'] / 'proof.png'
    L.render_html(html, out, 1200, 924)
    print(out)


if __name__ == '__main__':
    main()
