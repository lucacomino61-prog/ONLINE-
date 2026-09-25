#!/usr/bin/env python3
"""Read a live website's colours, fonts and current logo so a new logo can inherit them.

    python site_palette.py https://www.example.com [--json site.json]

Reports theme-color, the web-app manifest, CSS custom properties that hold colours (the first
value is normally the default, later ones dark mode or overrides), the most used colours, the
font families, and the markup of the current logo or wordmark. TLS verification stays on.
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter, OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import logo_lib as L  # noqa: E402

HEX = r'#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b'
COLOUR = rf'(?:{HEX}|rgba?\([^)]*\)|hsla?\([^)]*\)|oklch\([^)]*\)|oklab\([^)]*\))'


def fetch(url, limit=4_000_000):
    req = urllib.request.Request(url, headers={'User-Agent': L.UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read(limit).decode('utf-8', 'replace'), r.geturl()


def attrs(tag):
    return {k.lower(): v for k, _, v in re.findall(r'([\w:-]+)\s*=\s*(["\'])(.*?)\2', tag)}


def norm_hex(h):
    h = h.lstrip('#').upper()
    if len(h) in (3, 4):
        h = ''.join(c * 2 for c in h)
    return '#' + h


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('url')
    ap.add_argument('--json')
    a = ap.parse_args()
    url = a.url if '://' in a.url else 'https://' + a.url
    html, base = fetch(url)
    info = OrderedDict(url=base)
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.S | re.I)
    info['title'] = re.sub(r'\s+', ' ', m.group(1)).strip() if m else ''
    m = re.search(r'<html[^>]*\blang=["\']([^"\']+)', html, re.I)
    info['lang'] = m.group(1) if m else ''
    metas = [attrs(t) for t in re.findall(r'<meta\b[^>]*>', html, re.I)]
    info['theme_color'] = [(x.get('content'), x.get('media', '')) for x in metas if x.get('name') == 'theme-color']
    for key in ('description', 'og:site_name', 'og:description', 'og:image'):
        hit = [x.get('content') for x in metas if key in (x.get('name'), x.get('property'))]
        if hit:
            info[key] = hit[0]
    links = [attrs(t) for t in re.findall(r'<link\b[^>]*>', html, re.I)]
    css_urls = [urllib.parse.urljoin(base, x['href']) for x in links
                if 'stylesheet' in x.get('rel', '').lower() and x.get('href')]
    info['font_services'] = [u for u in css_urls if re.search(r'fonts\.googleapis|typekit|use\.fontawesome|fonts\.bunny', u)]
    info['icons'] = [urllib.parse.urljoin(base, x['href']) for x in links
                     if 'icon' in x.get('rel', '').lower() and x.get('href')]
    css = '\n'.join(re.findall(r'<style[^>]*>(.*?)</style>', html, re.S | re.I))
    fetched = []
    for u in [u for u in css_urls if u not in info['font_services']][:8]:
        try:
            text, _ = fetch(u)
            for imp in re.findall(r'@import\s+(?:url\()?["\']?([^"\')\s;]+)', text)[:4]:
                try:
                    css += '\n' + fetch(urllib.parse.urljoin(u, imp))[0]
                except Exception:
                    pass
            css += '\n' + text
            fetched.append(u)
        except Exception as e:
            fetched.append(f'{u} (failed: {e})')
    info['stylesheets'] = fetched
    man = [x for x in links if 'manifest' in x.get('rel', '').lower() and x.get('href')]
    if man:
        try:
            mj = json.loads(fetch(urllib.parse.urljoin(base, man[0]['href']))[0])
            info['manifest'] = {k: mj.get(k) for k in ('name', 'short_name', 'background_color', 'theme_color')}
        except Exception as e:
            info['manifest'] = f'failed: {e}'
    variables = OrderedDict()
    for name, value in re.findall(r'(--[\w-]+)\s*:\s*([^;{}]+)', css):
        value = value.strip()
        if re.search(COLOUR, value) and 'var(' not in value:
            variables.setdefault(name, [])
            if value not in variables[name]:
                variables[name].append(value)
    info['colour_variables'] = variables
    info['font_variables'] = OrderedDict((n, v.strip()) for n, v in re.findall(r'(--[\w-]*font[\w-]*)\s*:\s*([^;{}]+)', css))
    info['top_colours'] = Counter(norm_hex(h) for h in re.findall(HEX, css)).most_common(14)
    info['font_families'] = Counter(v.strip().replace('!important', '').strip()
                                    for v in re.findall(r'font-family\s*:\s*([^;}]+)', css)).most_common(8)
    info['font_face'] = sorted({f.strip().strip('"\'') for f in re.findall(r'@font-face\s*{[^}]*?font-family\s*:\s*([^;}]+)', css)})
    brand = []
    for mt in re.finditer(r'<(a|div|span|header|img|svg|p)\b[^>]*(?:class|id|aria-label|alt)=["\'][^"\']*(?:logo|brand|wordmark)[^"\']*["\'][^>]*>', html, re.I):
        snippet = html[mt.start():mt.start() + 500]
        brand.append(re.sub(r'\s+', ' ', snippet)[:300])
        if len(brand) == 3:
            break
    info['brand_markup'] = brand

    print(f"{info['title']}  ({info['url']}, lang {info['lang'] or '?'})")
    print('theme-color:', info['theme_color'] or 'none')
    if 'manifest' in info:
        print('manifest:', info['manifest'])
    print(f'\nColour variables ({len(variables)}; first value = default, later = dark mode/overrides):')
    for n, vals in list(variables.items())[:48]:
        print(f'  {n}: {vals[0]}' + (f'   (also {", ".join(vals[1:3])})' if len(vals) > 1 else ''))
    print('\nMost used colours:', ', '.join(f'{h} x{c}' for h, c in info['top_colours']))
    print('\nFont variables:', dict(info['font_variables']) or 'none')
    print('Font families:', '; '.join(f'{f} x{c}' for f, c in info['font_families']))
    print('@font-face:', info['font_face'] or 'none', '| font services:', info['font_services'] or 'none')
    print('\nCurrent logo / wordmark markup:')
    for b in brand or ['none found']:
        print('  ' + b)
    print('\nIcons:', info['icons'] or 'none')
    if a.json:
        Path(a.json).write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    main()
