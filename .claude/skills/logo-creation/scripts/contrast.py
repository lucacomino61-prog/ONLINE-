#!/usr/bin/env python3
"""WCAG contrast between brand colours.

    python contrast.py ink=#151515 paper=#F4F0E8 accent=#E55C87

Text needs 4.5:1 (3:1 at 24 px and up, or bold 19 px); graphics and icons need 3:1.
A colour that fails 3:1 on its ground may only be decorative (a dot, never letters).
"""
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import logo_lib as L  # noqa: E402


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        raise SystemExit(__doc__)
    named = [(a.split('=')[0], a.split('=')[-1]) if '=' in a else (a, a) for a in args]
    for (n1, c1), (n2, c2) in itertools.combinations(named, 2):
        r = L.contrast(c1, c2)
        verdict = ('text OK (AA)' if r >= 4.5 else 'large text / graphics only' if r >= 3
                   else 'decorative only')
        print(f'{n1} {c1} vs {n2} {c2}: {r:5.2f}:1  {verdict}')


if __name__ == '__main__':
    main()
