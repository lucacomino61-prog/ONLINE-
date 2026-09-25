"""Build the Bar Martiri logo files as outlined SVG (no font needed to display them).

    pip install fonttools brotli uharfbuzz
    python3 build_logo.py            # writes ../logo/*.svg
    NODE_PATH="$(npm root -g)" node export_png.js   # optional: ../png/*.png (Playwright + Chromium)

Colours are the live site's CSS variables (barmartiri.com, styles.css): --ink, --paper, --berry.
Typeface: Newsreader by Production Type, SIL Open Font License 1.1. It is downloaded from
Google Fonts on the first run and cached in ./.fonts/ (git-ignored).
"""
import io, math, os, re, urllib.request
from functools import lru_cache

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'logo')
CACHE = os.path.join(HERE, '.fonts')

# ---- Brand constants (from barmartiri.com) --------------------------------
INK = '#151515'     # --ink
PAPER = '#F4F0E8'   # --paper
BERRY = '#E55C87'   # --berry, the site's sunset colour: the dot on the last i, nowhere else

AXES = {'opsz': 72, 'wght': 460}    # display optical size, a touch above Regular
WORD_SPACE = -50                     # font units (UPM 2000) taken out of the word space
TRACK = -10                          # font units per glyph
TEXT = 'Bar Martiri'
DOT = 10                             # glyph index of the last "i"


def fetch_font():
    """Download the latin subset of Newsreader (variable, roman) once."""
    path = os.path.join(CACHE, 'Newsreader-VF.woff2')
    if os.path.exists(path):
        return path
    os.makedirs(CACHE, exist_ok=True)
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36'
    url = 'https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,200..800'
    css = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': ua})).read().decode()
    for subset, body in re.findall(r'/\*\s*([\w-]+)\s*\*/\s*@font-face\s*{([^}]*)}', css):
        if subset == 'latin':
            urllib.request.urlretrieve(re.search(r'url\(([^)]+)\)', body).group(1), path)
    return path


FONT = fetch_font()


@lru_cache(None)
def _instance(axes):
    font = instantiateVariableFont(TTFont(FONT), dict(axes))
    font.flavor = None
    buf = io.BytesIO()
    font.save(buf)
    data = buf.getvalue()
    return TTFont(io.BytesIO(data)), data


def _num(n):
    return ('%.2f' % n).rstrip('0').rstrip('.')


def text_path(text, size, x=0.0, y=0.0, kern=None, track=0, dot=None):
    """Outline `text` with its baseline at y.
    Returns (path_d, dot_d, (xmin, ymin, xmax, ymax)); dot_d is the top contour (the tittle)
    of glyph index `dot`, split out so it can take the accent colour."""
    tt, data = _instance(tuple(sorted(AXES.items())))
    font = hb.Font(hb.Face(data))
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {'kern': True, 'liga': True})
    order = tt.getGlyphOrder()
    glyphs = [(order[i.codepoint], p.x_advance) for i, p in zip(buf.glyph_infos, buf.glyph_positions)]
    s = size / tt['head'].unitsPerEm
    gs = tt.getGlyphSet()
    main, accent, bounds = SVGPathPen(gs, ntos=_num), SVGPathPen(gs, ntos=_num), BoundsPen(gs)
    cx = 0
    for i, (name, adv) in enumerate(glyphs):
        cx += (kern or {}).get(i, 0)
        t = (s, 0, 0, -s, x + cx * s, y)
        gs[name].draw(TransformPen(bounds, t))
        if i == dot:
            rec = RecordingPen()
            gs[name].draw(rec)
            contours, cur = [], []
            for op, args in rec.value:
                cur.append((op, args))
                if op in ('closePath', 'endPath'):
                    contours.append(cur)
                    cur = []
            top = max(contours, key=lambda c: min(p[1] for _, a in c for p in a))
            for c in contours:
                pen = TransformPen(accent if c is top else main, t)
                for op, args in c:
                    getattr(pen, op)(*args)
        else:
            gs[name].draw(TransformPen(main, t))
        cx += adv + track
    x0, y0, x1, y1 = bounds.bounds
    return main.getCommands(), accent.getCommands(), (x0, min(y0, y1), x1, max(y0, y1))


def svg(view, body, label='Bar Martiri'):
    x, y, w, h = view
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{_num(x)} {_num(y)} {_num(w)} {_num(h)}" '
            f'width="{_num(w)}" height="{_num(h)}" role="img" aria-label="{label}">'
            f'<title>{label}</title>{body}</svg>\n')


def tight(b):
    x0, y0, x1, y1 = math.floor(b[0]), math.floor(b[1]), math.ceil(b[2]), math.ceil(b[3])
    return x0, y0, x1 - x0, y1 - y0


def wordmark(size=300):
    return text_path(TEXT, size, kern={4: WORD_SPACE}, track=TRACK, dot=DOT)


def stacked(size=300):
    _, _, b1 = text_path('Bar', size, track=TRACK)
    _, _, b2 = text_path('Martiri', size, track=TRACK)
    gap = size * 0.67 * 0.22                            # 22% of the cap height
    y2 = b1[3] + gap - b2[1]
    c1, c2 = (b1[0] + b1[2]) / 2, (b2[0] + b2[2]) / 2
    d1, _, b1 = text_path('Bar', size, x=c2 - c1, track=TRACK)
    d2, dot, b2 = text_path('Martiri', size, y=y2, track=TRACK, dot=6)
    return d1 + d2, dot, (min(b1[0], b2[0]), b1[1], max(b1[2], b2[2]), b2[3])


def centred_m(size, cx, cy):
    _, _, b = text_path('M', size)
    return text_path('M', size, x=cx - (b[0] + b[2]) / 2, y=cy - (b[1] + b[3]) / 2)[0]


def icon(square=False):
    bg = (f'<rect width="512" height="512" fill="{INK}"/>' if square
          else f'<circle cx="256" cy="256" r="256" fill="{INK}"/>')
    return svg((0, 0, 512, 512), bg + f'<path fill="{PAPER}" d="{centred_m(330, 256, 256)}"/>',
               label='Bar Martiri icon')


def main():
    os.makedirs(OUT, exist_ok=True)
    files = {}
    d, dot, b = wordmark()
    v = tight(b)
    files['bar-martiri-logo.svg'] = svg(v, f'<path fill="{INK}" d="{d}"/><path fill="{BERRY}" d="{dot}"/>')
    files['bar-martiri-logo-reverse.svg'] = svg(v, f'<path fill="{PAPER}" d="{d}"/><path fill="{BERRY}" d="{dot}"/>')
    files['bar-martiri-logo-ink.svg'] = svg(v, f'<path fill="{INK}" d="{d}{dot}"/>')
    files['bar-martiri-logo-paper.svg'] = svg(v, f'<path fill="{PAPER}" d="{d}{dot}"/>')
    # for inlining in the website: letters take the surrounding text colour (light and dark mode)
    files['bar-martiri-logo-currentcolor.svg'] = svg(v, f'<path fill="currentColor" d="{d}"/><path fill="{BERRY}" d="{dot}"/>')
    d, dot, b = stacked()
    v = tight(b)
    files['bar-martiri-logo-stacked.svg'] = svg(v, f'<path fill="{INK}" d="{d}"/><path fill="{BERRY}" d="{dot}"/>')
    files['bar-martiri-logo-stacked-reverse.svg'] = svg(v, f'<path fill="{PAPER}" d="{d}"/><path fill="{BERRY}" d="{dot}"/>')
    files['bar-martiri-icon.svg'] = icon()
    files['bar-martiri-icon-square.svg'] = icon(square=True)
    for name, text in files.items():
        with open(os.path.join(OUT, name), 'w') as fh:
            fh.write(text)
        print(f'{name:40s} {len(text):>7,} bytes')


if __name__ == '__main__':
    main()
