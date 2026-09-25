"""Shared helpers for the logo-creation skill: fonts, outlines, SVG, colour and rendering.

Dependencies: fonttools, brotli, uharfbuzz, pillow (pip install fonttools brotli uharfbuzz pillow)
and any Chromium-based browser (Chrome, Edge, Chromium) for PNG rendering.
"""
import hashlib
import io
import json
import math
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from functools import lru_cache
from pathlib import Path

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/140.0 Safari/537.36')
CACHE = Path(os.environ.get('LOGO_CACHE', Path.home() / '.cache' / 'logo-creation'))


def http_get(url, binary=False, timeout=30):
    """GET with a browser user agent. TLS verification stays on: if a proxy re-signs
    traffic, point SSL_CERT_FILE at its CA bundle instead of disabling checks."""
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    return data if binary else data.decode('utf-8', 'replace')


# ---------------------------------------------------------------- Google Fonts

def google_metadata(max_age_days=30):
    """Family metadata for every Google Font (axes, styles, designers), cached."""
    path = CACHE / 'google-fonts-metadata.json'
    if not path.exists() or time.time() - path.stat().st_mtime > max_age_days * 86400:
        raw = http_get('https://fonts.google.com/metadata/fonts', timeout=60)
        if raw.startswith(")]}'"):
            raw = raw[4:]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(raw, encoding='utf-8')
    data = json.loads(path.read_text(encoding='utf-8'))
    return {f['family']: f for f in data['familyMetadataList']}


def family_info(family):
    meta = google_metadata()
    if family not in meta:
        close = [f for f in meta if f.lower().replace(' ', '') == family.lower().replace(' ', '')]
        if not close:
            raise SystemExit(f'Google Fonts has no family called "{family}".')
        family = close[0]
    return meta[family]


def _css2_family_param(info):
    """Build the css2 `family=` value that requests every axis range and style."""
    fam = info['family'].replace(' ', '+')
    styles = info['fonts'].keys()
    italic = any(s.endswith('i') for s in styles)
    axes = sorted(info.get('axes') or [], key=lambda a: (a['tag'].isupper(), a['tag']))
    if axes:
        tags = (['ital'] if italic else []) + [a['tag'] for a in axes]
        rng = ','.join(f"{a['min']:g}..{a['max']:g}" for a in axes)
        tuples = ([f'0,{rng}', f'1,{rng}'] if italic else [rng])
        return f"{fam}:{','.join(tags)}@{';'.join(tuples)}"
    weights = sorted({(1 if s.endswith('i') else 0, int(s.rstrip('i'))) for s in styles})
    if italic:
        return f"{fam}:ital,wght@{';'.join(f'{i},{w}' for i, w in weights)}"
    return f"{fam}:wght@{';'.join(str(w) for _, w in weights)}"


def fetch_google_font(family, text, italic=False, weight=400):
    """Download `family` subset to exactly the characters in `text` (keeps variable axes
    and kerning). Returns the path of the cached woff2 for the requested style."""
    info = family_info(family)
    chars = ''.join(sorted(set(text + ' ')))
    key = hashlib.sha1(f"{info['family']}|{italic}|{weight}|{chars}".encode()).hexdigest()[:16]
    out = CACHE / 'fonts' / f"{info['family'].replace(' ', '')}-{'it' if italic else 'rm'}-{key}.woff2"
    if out.exists():
        return out
    url = ('https://fonts.googleapis.com/css2?family=' + _css2_family_param(info)
           + '&text=' + urllib.parse.quote(chars) + '&display=swap')
    css = http_get(url)
    best = None
    for body in re.findall(r'@font-face\s*{([^}]*)}', css):
        style = re.search(r'font-style:\s*(\w+)', body).group(1)
        if (style == 'italic') != italic:
            continue
        wts = [int(w) for w in re.search(r'font-weight:\s*([\d ]+)', body).group(1).split()]
        lo, hi = wts[0], wts[-1]
        dist = 0 if lo <= weight <= hi else min(abs(weight - lo), abs(weight - hi))
        src = re.search(r'url\(([^)]+)\)', body).group(1)
        if best is None or dist < best[0]:
            best = (dist, src)
    if best is None:
        raise SystemExit(f'{family}: no {"italic" if italic else "roman"} style available.')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(http_get(best[1], binary=True))
    return out


def font_path(source, text):
    """source: {"google": "Family", "italic": bool, "weight": int} or {"file": "path"}."""
    if 'file' in source:
        return Path(source['file']).expanduser()
    return fetch_google_font(source['google'], text, bool(source.get('italic')),
                             int(source.get('weight', 400)))


def parse_font_spec(spec):
    """'Newsreader:opsz=72,wght=460:italic' or 'file:path/to/font.otf:wght=500'."""
    parts = spec.split(':')
    if parts[0] == 'file':
        # Windows paths contain a drive colon: rejoin until the part holding the extension
        path, rest = parts[1], parts[2:]
        while rest and not re.search(r'\.(ttf|otf|woff2?|ttc)$', path, re.I):
            path += ':' + rest.pop(0)
        source, parts = {'file': path}, [None] + rest
    else:
        source = {'google': parts[0]}
    axes = {}
    for p in parts[1:]:
        if p == 'italic':
            source['italic'] = True
        elif p:
            for kv in p.split(','):
                k, v = kv.split('=')
                axes[k.strip()] = float(v)
    if 'wght' in axes:
        source['weight'] = int(axes['wght'])
    return source, axes


# ---------------------------------------------------------------- outlines

@lru_cache(None)
def _instance(path, axes_items):
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont
    font = TTFont(str(path))
    if 'fvar' in font:
        loc = {}
        for a in font['fvar'].axes:
            v = dict(axes_items).get(a.axisTag, a.defaultValue)
            loc[a.axisTag] = min(max(v, a.minValue), a.maxValue)
        font = instantiateVariableFont(font, loc)
    font.flavor = None
    buf = io.BytesIO()
    font.save(buf)
    data = buf.getvalue()
    return TTFont(io.BytesIO(data)), data


def load(source, axes, text):
    """Return (TTFont, font bytes) for a font source pinned at `axes`."""
    return _instance(font_path(source, text), tuple(sorted((axes or {}).items())))


def font_metrics(tt):
    os2 = tt['OS/2']
    upm = tt['head'].unitsPerEm
    cap = getattr(os2, 'sCapHeight', 0) or int(upm * 0.7)
    xh = getattr(os2, 'sxHeight', 0) or int(upm * 0.5)
    return {'upm': upm, 'cap': cap, 'xheight': xh}


def _num(n):
    return ('%.2f' % n).rstrip('0').rstrip('.')


def outline(text, source, axes, size, x=0.0, y=0.0, kern=None, track=0, accent=None,
            features=None, font_text=None):
    """Outline `text` with its baseline at y.

    kern:   {glyph_index: font units added before that glyph}
    track:  font units added after every glyph
    accent: {"glyph": i, "part": "dot" | "glyph"}; "dot" splits off the top contour
            (the tittle of i/j), "glyph" the whole glyph, so it can take the accent colour.
    Returns dict(d, accent_d, bbox=(x0, y0, x1, y1), advance, metrics).
    """
    import uharfbuzz as hb
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.pens.recordingPen import DecomposingRecordingPen

    tt, data = load(source, axes, font_text or text)
    font = hb.Font(hb.Face(data))
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, features or {'kern': True, 'liga': True})
    order = tt.getGlyphOrder()
    glyphs = [(order[i.codepoint], p.x_advance, p.x_offset, p.y_offset)
              for i, p in zip(buf.glyph_infos, buf.glyph_positions)]
    kern = {int(k): v for k, v in (kern or {}).items()}
    s = size / tt['head'].unitsPerEm
    gs = tt.getGlyphSet()
    main, acc, bounds = SVGPathPen(gs, ntos=_num), SVGPathPen(gs, ntos=_num), BoundsPen(gs)
    cx = 0
    for i, (name, adv, xo, yo) in enumerate(glyphs):
        cx += kern.get(i, 0)
        t = (s, 0, 0, -s, x + (cx + xo) * s, y - yo * s)
        gs[name].draw(TransformPen(bounds, t))
        if accent and i == accent.get('glyph'):
            if accent.get('part', 'dot') == 'glyph':
                gs[name].draw(TransformPen(acc, t))
            else:
                rec = DecomposingRecordingPen(gs)   # flattens composite glyphs (i = dotless i + dot)
                gs[name].draw(rec)
                contours, cur = [], []
                for op, args in rec.value:
                    cur.append((op, args))
                    if op in ('closePath', 'endPath'):
                        contours.append(cur)
                        cur = []
                # the dot is the contour sitting highest; a one-contour glyph has no dot to split
                top = (max(contours, key=lambda c: min(p[1] for _, a in c for p in a))
                       if len(contours) > 1 else None)
                for c in contours:
                    pen = TransformPen(acc if c is top else main, t)
                    for op, args in c:
                        getattr(pen, op)(*args)
        else:
            gs[name].draw(TransformPen(main, t))
        cx += adv + track
    x0, y0, x1, y1 = bounds.bounds
    return {'d': main.getCommands(), 'accent_d': acc.getCommands(),
            'bbox': (x0, min(y0, y1), x1, max(y0, y1)), 'advance': cx * s,
            'metrics': font_metrics(tt), 'glyphs': [g[0] for g in glyphs]}


# ---------------------------------------------------------------- SVG + colour

def tight(b):
    x0, y0 = math.floor(b[0]), math.floor(b[1])
    return x0, y0, math.ceil(b[2]) - x0, math.ceil(b[3]) - y0


def svg_doc(view, body, label):
    x, y, w, h = view
    label = label.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{_num(x)} {_num(y)} {_num(w)} {_num(h)}" '
            f'width="{_num(w)}" height="{_num(h)}" role="img" aria-label="{label}">'
            f'<title>{label}</title>{body}</svg>\n')


def svg_size(svg_text):
    x, y, w, h = map(float, re.search(r'viewBox="([^"]+)"', svg_text).group(1).split())
    return w, h


def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_colour):
    h = hex_colour.lstrip('#')
    if len(h) == 3:
        h = ''.join(ch * 2 for ch in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# ---------------------------------------------------------------- rendering

def find_browser():
    """A Chromium-based browser for headless screenshots (Chrome, Edge or Chromium)."""
    env = os.environ.get('LOGO_BROWSER')
    if env and Path(env).exists():
        return env
    pw = os.environ.get('PLAYWRIGHT_BROWSERS_PATH')
    roots = [Path(pw)] if pw else []
    roots += [Path.home() / '.cache' / 'ms-playwright', Path.home() / 'AppData' / 'Local' / 'ms-playwright']
    for root in roots:
        for pat in ('chromium-*/chrome-linux/chrome', 'chromium-*/chrome-win/chrome.exe',
                    'chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium'):
            hits = sorted(root.glob(pat)) if root.exists() else []
            if hits:
                return str(hits[-1])
    for name in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'chrome',
                 'msedge', 'microsoft-edge'):
        hit = shutil.which(name)
        if hit:
            return hit
    candidates = []
    for base in (os.environ.get('PROGRAMFILES'), os.environ.get('PROGRAMFILES(X86)'), os.environ.get('LOCALAPPDATA')):
        if base:
            candidates += [Path(base) / 'Google/Chrome/Application/chrome.exe',
                           Path(base) / 'Microsoft/Edge/Application/msedge.exe']
    candidates += [Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'),
                   Path('/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'),
                   Path('/Applications/Chromium.app/Contents/MacOS/Chromium')]
    for c in candidates:
        if c.exists():
            return str(c)
    raise SystemExit('No Chrome, Edge or Chromium found. Install one, or set LOGO_BROWSER to its path.')


def render_html(html, out_png, width, height, transparent=False):
    """Screenshot `html` at width x height CSS px (1:1) into out_png."""
    from PIL import Image
    width, height = int(math.ceil(width)), int(math.ceil(height))
    out_png = Path(out_png).resolve()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    # Headless Chrome scales tiny windows and its viewport is shorter than the window
    # (87 px on Linux), so render in a roomy window and crop.
    win_w, win_h = max(width, 800), max(height + 200, 600)
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / 'page.html'
        page.write_text(html, encoding='utf-8')
        shot = Path(tmp) / 'shot.png'
        cmd = [find_browser(), '--headless=new', '--disable-gpu', '--hide-scrollbars',
               '--no-first-run', '--no-default-browser-check', '--force-device-scale-factor=1',
               f'--user-data-dir={Path(tmp) / "profile"}', f'--window-size={win_w},{win_h}',
               f'--screenshot={shot}']
        if transparent:
            cmd.append('--default-background-color=00000000')
        if platform.system() == 'Linux' and getattr(os, 'geteuid', lambda: 1)() == 0:
            cmd.append('--no-sandbox')
        cmd.append(page.as_uri())
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        if not shot.exists():
            raise SystemExit('The browser did not produce a screenshot: ' + ' '.join(cmd[:1]))
        Image.open(shot).crop((0, 0, width, height)).save(out_png)
    return out_png


def render_svg(svg_text, out_png, width, transparent=True, background=None):
    """Rasterise one SVG at `width` px wide, keeping its aspect ratio."""
    w, h = svg_size(svg_text)
    height = round(width * h / w)
    bg = background or ('transparent' if transparent else '#ffffff')
    svg = re.sub(r'\swidth="[^"]*"\s+height="[^"]*"', '', svg_text, count=1)
    html = (f'<!doctype html><html><body style="margin:0;background:{bg}">'
            f'<div style="width:{width}px;height:{height}px;line-height:0">{svg}</div>'
            f'<style>svg{{display:block;width:100%;height:100%}}</style></body></html>')
    return render_html(html, out_png, width, height, transparent=transparent and not background)


def load_config(path):
    path = Path(path).resolve()
    cfg = json.loads(path.read_text(encoding='utf-8'))
    cfg['_dir'] = path.parent
    out = Path(cfg.get('out', '.'))
    cfg['_out'] = (out if out.is_absolute() else path.parent / out).resolve()
    return cfg


def colour(cfg, ref):
    """Resolve a palette key ("ink", "paper", "accent") or a literal hex."""
    return cfg['colors'].get(ref, ref) if isinstance(ref, str) else ref
