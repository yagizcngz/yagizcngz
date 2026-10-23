"""Generates header-light.svg and header-dark.svg (pixel art campfire scene). Run: py -3 make_header.py <out_dir>"""
import math, os, sys

PX = 4
GROUND = 46
COLORS = {
    'k': '#10142a', 'H': '#dce3ea', 'M': '#9aa6b2', 'D': '#5f6b78', 'V': '#0b0f1a',
    'N': '#1e3a8a', 'n': '#14286b', 'Y': '#e3b341',
    'C': '#8a939c', 'c': '#626b74', 'B': '#7a4a22', 'b': '#3d2a1c',
    'O': '#f08a24', 'o': '#c25e12', 'q': '#8a3d0c', 'E': '#ffd98a', 'e': '#e0b45c',
    'w': '#f6b26b', 'F': '#f3ead8', 'W': '#ffffff',
    'P': '#9b6bff', 'p': '#6c45cc', 's': '#d6c4ff',
    'R': '#e3341a', 'A': '#ff8c1a', 'G': '#ffd23f', 'z': '#9aa6b2',
}
SHADE = {'O': 'o', 'o': 'q', 'E': 'e', 'w': 'o', 'P': 'p', 'F': 'M'}

KNIGHT_SIT = [
    ".....kkkkkk.....",
    "....kHHHHHMk....",
    "...kHHHHHHMMk...",
    "...kHHHHHHMDk...",
    "...kVVVVVVVVk...",
    "...kHHHHHHMDk...",
    "...kHDHDHHMDk...",
    "...kHHHHHHMDk...",
    "....kMMMMMDk....",
    "..kkkCCCCCCkkk..",
    ".kMMkYNNNNNkMMk.",
    ".kHMkNYNNNNkMHk.",
    ".kMDkNNYNNNkDMk.",
    ".kCCkNNNYNNkCCk.",
    ".kCckNNNNYNkCck.",
    ".kMMkNNNNNYkMMk.",
    ".kDDkBBYYBBkDDk.",
    "..kNNNNnnNNNNk..",
    ".kMMMMkkkkMMMMk.",
    ".kMDMMk..kMMDMk.",
    ".kkMMk....kMMkk.",
    "..kbbbk..kbbbk..",
    "..kkkkk..kkkkk..",
]
LOG = [
    "kkkkkkkkkkkkkkkkkk",
    "kBBBBBBBBBBBBBBBek",
    "kbBbbBBbbBBbBBbBek",
    "kkkkkkkkkkkkkkkkkk",
]
FIRE_BASE = [
    "..kRAAAAARk...",
    "kbBBBBBBBBBbk.",
    ".kBbbBBbbBbk..",
    "..kkkkkkkkk...",
]
FLAMES = [
    ["......R.......",
     ".....RR...R...",
     "....RAR..RR...",
     "...RAAR.RAR...",
     "...RAAARRAAR..",
     "..RAAGAAAAAR..",
     "..RAGGGAGAAR..",
     ".RAAGGGGGAAAR.",
     ".RAGGWGGGGAR..",
     "..RAGGGGGAR..."],
    ["..........R...",
     "...R.....RR...",
     "...RR...RAR...",
     "..RAR..RAAR...",
     "..RAARRAAAR...",
     "..RAAAGAAAR...",
     ".RAAGGGAGAR...",
     ".RAGGGGGGAAR..",
     "..RAGGWGGGAR..",
     "..RAGGGGGAR..."],
    [".......R......",
     "......RR..R...",
     "..R..RAR..R...",
     "..RR.RAAR.RR..",
     "..RARRAAARAR..",
     "..RAAAGAAAAR..",
     "..RAGGGGAAR...",
     ".RAAGGWGGAAR..",
     ".RAGGGGGGAR...",
     "..RAGGGGGAR..."],
]
ZZZ = ["zzz.....", "..z.....", ".z..zz..", "zzz..z..", "....z...", "....zz.."]
STAR = [".Y.", "YGY", ".Y."]


def ascii_grid(rows):
    return {(x, y): ch for y, r in enumerate(rows) for x, ch in enumerate(r) if ch != '.'}


def inside(poly, x, y):
    c = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


class Shape:
    """Union of ellipses and polygons, rasterized then auto-outlined and shaded."""

    def __init__(self):
        self.ops = []

    def ell(self, cx, cy, rx, ry, c):
        self.ops.append(('e', (cx, cy, rx, ry), c))
        return self

    def poly(self, pts, c):
        self.ops.append(('p', pts, c))
        return self

    def px(self, pts, c):
        self.ops.append(('x', pts, c))
        return self

    def grid(self):
        g = {}
        for kind, a, c in self.ops:
            if kind == 'x':
                g.update({p: c for p in a})
                continue
            if kind == 'e':
                cx, cy, rx, ry = a
                box = (cx - rx, cy - ry, cx + rx, cy + ry)
            else:
                box = (min(p[0] for p in a), min(p[1] for p in a), max(p[0] for p in a), max(p[1] for p in a))
            for y in range(math.floor(box[1]), math.ceil(box[3]) + 1):
                for x in range(math.floor(box[0]), math.ceil(box[2]) + 1):
                    px, py = x + .5, y + .5
                    if kind == 'e':
                        hit = ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 <= 1
                    else:
                        hit = inside(a, px, py)
                    if hit:
                        g[(x, y)] = c
        filled = set(g)
        details = {p for op in self.ops if op[0] == 'x' for p in op[1]}
        for (x, y), c in list(g.items()):
            if (x, y) not in details and c in SHADE and ((x + 1, y) not in filled or (x, y + 1) not in filled):
                g[(x, y)] = SHADE[c]
        for x, y in filled:
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if n not in filled:
                    g[n] = 'k'
        return g


def dragon_sleep(breath):
    # faces left, lying down with its head on the ground; breath lifts the back by a pixel
    b = 1 if breath else 0
    return (Shape()
            .poly([(17, 11 - b), (22, 4 - b), (26, 7 - b), (31, 4 - b), (36, 11 - b), (20, 12)], 'w')
            .px([(22, 5 - b), (22, 6 - b), (23, 7 - b), (31, 5 - b), (30, 6 - b), (29, 7 - b)], 'o')
            .ell(25, 15 - b / 2, 13, 6.5 + b / 2, 'O')
            .ell(24, 19.5, 10, 2, 'E')
            .poly([(36, 16), (40, 19), (38, 22.5), (15, 23.5), (20, 20.5), (34, 20)], 'O')
            .poly([(11, 15), (18, 11), (19, 20), (11, 21)], 'O')
            .ell(8, 18, 5.5, 3.6, 'O')
            .ell(2.5, 19.2, 3.4, 2.4, 'O')
            .poly([(8, 15.5), (15, 12), (15.5, 13.5), (10, 16.5)], 'F')
            .poly([(5, 15.5), (9, 12), (10, 13), (7, 16)], 'F')
            .ell(15, 22.6, 2.4, 1.3, 'O')
            .px([(4, 17), (5, 17), (6, 17)], 'k').px([(0, 19)], 'q')
            .px([(x, 21) for x in range(18, 32, 3)], 'e')
            .grid())


def slime():
    return (Shape()
            .poly([(0, 7), (1, 3), (4, 0), (7, 0), (10, 3), (11, 7)], 'P')
            .px([(3, 4), (7, 4)], 'k').px([(2, 2), (3, 1)], 's')
            .grid())


def at(g, x, y, bottom=False):
    if bottom:
        y -= max(py for _, py in g) + 1
    return {(px + x, py + y): c for (px, py), c in g.items()}


def rects(g):
    parts, rows = [], {}
    for (x, y), c in g.items():
        rows.setdefault(y, {})[x] = c
    for y, row in sorted(rows.items()):
        xs = sorted(row)
        i = 0
        while i < len(xs):
            j = i
            while j + 1 < len(xs) and xs[j + 1] == xs[j] + 1 and row[xs[j + 1]] == row[xs[i]]:
                j += 1
            parts.append(f'<rect x="{xs[i]*PX}" y="{y*PX}" width="{(j-i+1)*PX}" height="{PX}" fill="{COLORS[row[xs[i]]]}"/>')
            i = j + 1
    return ''.join(parts)


def group(cls, *grids):
    merged = {}
    for g in grids:
        merged.update(g)
    assert all(-1 < x < 110 and -1 < y < 47 for x, y in merged), f'{cls} out of bounds'
    return f'<g class="{cls}">{rects(merged)}</g>'


FX = 38
flame_frames = [at(ascii_grid(f + FIRE_BASE), FX, GROUND, True) for f in FLAMES]
body = (
    group('star s1', at(ascii_grid(STAR), 6, 4)) + group('star s2', at(ascii_grid(STAR), 40, 9))
    + group('star s3', at(ascii_grid(STAR), 92, 3)) + group('star s4', at(ascii_grid(STAR), 74, 14))
    + group('d0', at(dragon_sleep(False), 54, GROUND, True)) + group('d1', at(dragon_sleep(True), 54, GROUND, True))
    + group('zz', at(ascii_grid(ZZZ), 55, 22))
    + group('', at(ascii_grid(LOG), 16, GROUND, True), at(ascii_grid(KNIGHT_SIT), 17, GROUND - 2, True))
    + ''.join(group(f'f{i}', g) for i, g in enumerate(flame_frames))
    + group('slime', at(slime(), 97, GROUND, True))
)

THEMES = {'light': ('#1f2328', '#59636e', '#d1d9e0'), 'dark': ('#f0f6fc', '#9198a1', '#3d444d')}


def svg(name_fill, sub_fill, rule):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 190" width="880" height="190" role="img" aria-label="Yağız Cengiz. A pixel art knight resting by a campfire next to a sleeping dragon and a slime.">
  <style>
    .name {{ font: 600 48px -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; fill: {name_fill}; letter-spacing: -0.5px; }}
    .sub {{ font: 400 16px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: {sub_fill}; }}
    .rule {{ stroke: {rule}; stroke-width: 1; }}
    .glow {{ animation: glow .9s step-end infinite; }}
    .f0 {{ animation: f0 .9s step-end infinite; }}
    .f1 {{ animation: f1 .9s step-end infinite; }}
    .f2 {{ animation: f2 .9s step-end infinite; }}
    .d0 {{ animation: d0 3.2s step-end infinite; }}
    .d1 {{ animation: d1 3.2s step-end infinite; }}
    .zz {{ animation: zz 3.2s steps(4) infinite; }}
    .slime {{ animation: hop 2.6s step-end infinite; }}
    .star {{ animation: tw 2.4s step-end infinite; }}
    .s2 {{ animation-delay: -.6s; }} .s3 {{ animation-delay: -1.2s; }} .s4 {{ animation-delay: -1.8s; }}
    @keyframes f0 {{ 0% {{ opacity: 1; }} 33.33% {{ opacity: 0; }} }}
    @keyframes f1 {{ 0% {{ opacity: 0; }} 33.33% {{ opacity: 1; }} 66.66% {{ opacity: 0; }} }}
    @keyframes f2 {{ 0% {{ opacity: 0; }} 66.66% {{ opacity: 1; }} }}
    @keyframes glow {{ 0% {{ opacity: .8; }} 33.33% {{ opacity: 1; }} 66.66% {{ opacity: .65; }} }}
    @keyframes d0 {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
    @keyframes d1 {{ 0% {{ opacity: 0; }} 50% {{ opacity: 1; }} }}
    @keyframes zz {{ 0% {{ transform: translate(0, 0); opacity: 1; }} 100% {{ transform: translate(8px, -16px); opacity: 0; }} }}
    @keyframes hop {{ 0% {{ transform: translateY(0); }} 84% {{ transform: translateY(-4px); }} 92% {{ transform: translateY(0); }} }}
    @keyframes tw {{ 0% {{ opacity: 1; }} 50% {{ opacity: .25; }} }}
    @media (prefers-reduced-motion: reduce) {{
      .glow, .f0, .d0, .zz, .slime, .star {{ animation: none; }}
      .f1, .f2, .d1 {{ display: none; }}
    }}
  </style>
  <text class="name" x="0" y="90">Yağız Cengiz</text>
  <text class="sub" x="2" y="128">computer engineering student · software developer</text>
  <g transform="translate(440 0)" shape-rendering="crispEdges">
    <defs><radialGradient id="glow"><stop offset="0" stop-color="#ff8c1a" stop-opacity=".45" /><stop offset="1" stop-color="#ff8c1a" stop-opacity="0" /></radialGradient></defs>
    <ellipse class="glow" cx="{(FX + 6) * PX}" cy="176" rx="80" ry="16" fill="url(#glow)" />
    {body}
  </g>
  <line class="rule" x1="0" y1="188" x2="880" y2="188" />
</svg>
'''
for theme, colors in THEMES.items():
    with open(os.path.join(sys.argv[1], f'header-{theme}.svg'), 'w', encoding='utf-8') as f:
        f.write(svg(*colors))

# footer: the slime carrying a letter next to the email address
ENVELOPE = [
    "kkkkkkkkkk",
    "kWkHHHHkWk",
    "kWHkHHkHWk",
    "kWHHkRRHWk",
    "kWWWWWWWWk",
    "kkkkkkkkkk",
]
EMAIL = 'yagizcengiz888@gmail.com'
mail = group('slime', at(ascii_grid(ENVELOPE), 2, 0), at(slime(), 1, 7))


def footer(text_fill, rule):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 90" width="880" height="90" role="img" aria-label="Email: {EMAIL}">
  <style>
    .mail {{ font: 400 18px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: {text_fill}; }}
    .rule {{ stroke: {rule}; stroke-width: 1; }}
    .slime {{ animation: hop 2.6s step-end infinite; }}
    @keyframes hop {{ 0% {{ transform: translateY(0); }} 84% {{ transform: translateY(-4px); }} 92% {{ transform: translateY(0); }} }}
    @media (prefers-reduced-motion: reduce) {{ .slime {{ animation: none; }} }}
  </style>
  <line class="rule" x1="0" y1="1" x2="880" y2="1" />
  <g transform="translate(276 16)" shape-rendering="crispEdges">{mail}</g>
  <text class="mail" x="344" y="66">{EMAIL}</text>
</svg>
'''


for theme, (name_fill, _, rule) in THEMES.items():
    with open(os.path.join(sys.argv[1], f'footer-{theme}.svg'), 'w', encoding='utf-8') as f:
        f.write(footer(name_fill, rule))
