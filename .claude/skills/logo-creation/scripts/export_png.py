#!/usr/bin/env python3
"""Export PNG sizes and favicon.ico from the SVGs that build_logo.py wrote.

    python export_png.py path/to/logo.json

Writes <out>/png/: wordmark and stacked at print/screen size (transparent), the social avatar,
favicons (32/48/96), manifest icons (192/512), apple-touch-icon (180) and favicon.ico (16/32/48).
"""
import argparse
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import logo_lib as L  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('config')
    cfg = L.load_config(ap.parse_args().config)
    slug = cfg['slug']
    src, dst = cfg['_out'] / 'logo', cfg['_out'] / 'png'
    dst.mkdir(parents=True, exist_ok=True)
    jobs = [(f'{slug}-logo{s}.svg', f'{slug}-logo{s}.png', 2400) for s in ('', '-reverse', '-ink', '-paper')]
    jobs += [(f'{slug}-logo-stacked{s}.svg', f'{slug}-logo-stacked{s}.png', 1600) for s in ('', '-reverse')]
    jobs += [(f'{slug}-icon-square.svg', f'{slug}-avatar-1080.png', 1080),
             (f'{slug}-icon.svg', 'favicon-32.png', 32),
             (f'{slug}-icon.svg', 'favicon-48.png', 48),
             (f'{slug}-icon.svg', 'favicon-96.png', 96),
             (f'{slug}-icon.svg', 'icon-192.png', 192),
             (f'{slug}-icon-square.svg', 'apple-touch-icon.png', 180),
             (f'{slug}-icon-square.svg', 'icon-512.png', 512),
             (f'{slug}-icon-square.svg', 'app-icon-1024.png', 1024)]
    opaque = {'apple-touch-icon.png', 'app-icon-1024.png'}   # iOS and the App Store reject transparency
    from PIL import Image
    for svg_name, png_name, width in jobs:
        svg = src / svg_name
        if svg.exists():
            out = L.render_svg(svg.read_text(encoding='utf-8'), dst / png_name, width)
            if png_name in opaque:
                Image.open(out).convert('RGB').save(out)
            print(png_name)
    icon = src / f'{slug}-icon.svg'
    if icon.exists():
        with tempfile.TemporaryDirectory() as tmp:
            big = L.render_svg(icon.read_text(encoding='utf-8'), Path(tmp) / 'icon-256.png', 256)
            Image.open(big).save(dst / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
        print('favicon.ico')


if __name__ == '__main__':
    main()
