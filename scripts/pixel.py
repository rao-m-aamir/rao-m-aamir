"""Shared pixel toolkit: palette, 5x7 bitmap font, rectangle merging, SVG helpers.
Every piece of text in the README art is drawn from pixels (no <text>, no web fonts),
so it looks identical on every device and inside GitHub's <img> sandbox."""
from collections import defaultdict

# ---- palette (lifted from the portfolio: forest greens, cream paper, gold dot) ----
PAL = dict(
    bg='#0f1c1a', panel='#152b27', line='#2d554a', cream='#f5f1d8', mint='#d9dda8',
    teal='#7fb5a5', dim='#5f7a70', gold='#dfc47e', orange='#e08a3c', shadow='#06100f',
)

FONT = {
 'A': [".###.","#...#","#...#","#####","#...#","#...#","#...#"],
 'B': ["####.","#...#","#...#","####.","#...#","#...#","####."],
 'C': [".####","#....","#....","#....","#....","#....",".####"],
 'D': ["####.","#...#","#...#","#...#","#...#","#...#","####."],
 'E': ["#####","#....","#....","####.","#....","#....","#####"],
 'F': ["#####","#....","#....","####.","#....","#....","#...."],
 'G': [".###.","#...#","#....","#.###","#...#","#...#",".###."],
 'H': ["#...#","#...#","#...#","#####","#...#","#...#","#...#"],
 'I': ["#####","..#..","..#..","..#..","..#..","..#..","#####"],
 'J': ["..###","...#.","...#.","...#.","...#.","#..#.",".##.."],
 'K': ["#...#","#..#.","#.#..","##...","#.#..","#..#.","#...#"],
 'L': ["#....","#....","#....","#....","#....","#....","#####"],
 'M': ["#...#","##.##","#.#.#","#.#.#","#...#","#...#","#...#"],
 'N': ["#...#","##..#","#.#.#","#..##","#...#","#...#","#...#"],
 'O': [".###.","#...#","#...#","#...#","#...#","#...#",".###."],
 'P': ["####.","#...#","#...#","####.","#....","#....","#...."],
 'Q': [".###.","#...#","#...#","#...#","#.#.#","#..#.",".##.#"],
 'R': ["####.","#...#","#...#","####.","#.#..","#..#.","#...#"],
 'S': [".####","#....","#....",".###.","....#","....#","####."],
 'T': ["#####","..#..","..#..","..#..","..#..","..#..","..#.."],
 'U': ["#...#","#...#","#...#","#...#","#...#","#...#",".###."],
 'V': ["#...#","#...#","#...#","#...#","#...#",".#.#.","..#.."],
 'W': ["#...#","#...#","#...#","#.#.#","#.#.#","##.##","#...#"],
 'X': ["#...#","#...#",".#.#.","..#..",".#.#.","#...#","#...#"],
 'Y': ["#...#","#...#",".#.#.","..#..","..#..","..#..","..#.."],
 'Z': ["#####","....#","...#.","..#..",".#...","#....","#####"],
 '0': [".###.","#...#","#..##","#.#.#","##..#","#...#",".###."],
 '1': ["..#..",".##..","..#..","..#..","..#..","..#..",".###."],
 '2': [".###.","#...#","....#","...#.","..#..",".#...","#####"],
 '3': ["####.","....#","....#",".###.","....#","....#","####."],
 '4': ["...#.","..##.",".#.#.","#..#.","#####","...#.","...#."],
 '5': ["#####","#....","####.","....#","....#","#...#",".###."],
 '6': [".###.","#....","#....","####.","#...#","#...#",".###."],
 '7': ["#####","....#","...#.","..#..",".#...",".#...",".#..."],
 '8': [".###.","#...#","#...#",".###.","#...#","#...#",".###."],
 '9': [".###.","#...#","#...#",".####","....#","....#",".###."],
 ' ': ["---","---","---","---","---","---","---"],
 '.': [".",".",".",".",".",".","#"],
 ',': ["..","..","..","..","..",".#","#."],
 ':': [".",".","#",".",".","#","."],
 '!': ["#","#","#","#","#",".","#"],
 '?': [".###.","#...#","....#","...#.","..#..",".....","..#.."],
 "'": ["#","#",".",".",".",".","."],
 '-': [".....",".....",".....","#####",".....",".....","....."],
 '_': [".....",".....",".....",".....",".....",".....","#####"],
 '/': ["....#","...#.","...#.","..#..",".#...",".#...","#...."],
 '(': [".#","#.","#.","#.","#.","#.",".#"],
 ')': ["#.",".#",".#",".#",".#",".#","#."],
 '[': ["##","#.","#.","#.","#.","#.","##"],
 ']': ["##",".#",".#",".#",".#",".#","##"],
 '+': [".....","..#..","..#..","#####","..#..","..#..","....."],
 '=': [".....",".....","#####",".....","#####",".....","....."],
 '>': ["#....",".#...","..#..","...#.","..#..",".#...","#...."],
 '<': ["....#","...#.","..#..",".#...","..#..","...#.","....#"],
 '@': [".###.","#...#","#.###","#.#.#","#.###","#....",".####"],
 '&': [".##..","#..#.","#.#..",".#...","#.#.#","#..#.",".##.#"],
 '%': ["##..#","##..#","...#.","..#..",".#...","#..##","#..##"],
 '*': [".....","#.#.#",".###.","#####",".###.","#.#.#","....."],
 '·': [".",".",".","#",".",".","."],
 '|': ["#","#","#","#","#","#","#"],
 '█': ["#####"]*7,
 '▶': ["#....","##...","###..","####.","###..","##...","#...."],
 '◆': ["..#..",".###.","#####",".###.","..#..",".....","....."],
}
FONT['~'] = [".....",".....",".#...","#.#.#","...#.",".....","....."]
FONT['$'] = ["..#..",".####","#.#..",".###.","..#.#","####.","..#.."]
FONT['"'] = ["#.#","#.#",'...','...','...','...','...']


def glyph(ch):
    g = FONT[ch]
    w = len(g[0])
    return [r.replace('-', '.') for r in g], w


def text_cells(s, spacing=1):
    cells, x = set(), 0
    for ch in s.upper():
        g, w = glyph(ch)
        for r, row in enumerate(g):
            for c, v in enumerate(row):
                if v == '#':
                    cells.add((x + c, r))
        x += w + spacing
    return cells, max(0, x - spacing)


def text_width(s, u, spacing=1):
    return text_cells(s, spacing)[1] * u


def cells_to_rects(cells):
    """Merge a set of (x, y) cells into as few rectangles as possible."""
    rows = defaultdict(list)
    for x, y in cells:
        rows[y].append(x)
    runs = {}
    for y, xs in rows.items():
        xs.sort()
        out, start, prev = [], xs[0], xs[0]
        for x in xs[1:]:
            if x == prev + 1:
                prev = x
            else:
                out.append((start, prev - start + 1)); start = prev = x
        out.append((start, prev - start + 1))
        runs[y] = out
    rects, active, prev_y = [], {}, None
    for y in sorted(runs):
        cur = set(runs[y])
        if prev_y is not None and y != prev_y + 1:
            for (x, w), y0 in active.items():
                rects.append((x, y0, w, prev_y - y0 + 1))
            active = {}
        else:
            for k in list(active):
                if k not in cur:
                    rects.append((k[0], active[k], k[1], y - active[k]))
                    del active[k]
        for k in cur:
            active.setdefault(k, y)
        prev_y = y
    for (x, w), y0 in active.items():
        rects.append((x, y0, w, prev_y - y0 + 1))
    return rects


def rects_to_d(rects, u=1, ox=0, oy=0):
    f = lambda v: f'{v:g}'
    return ''.join(f'M{f(ox + x * u)} {f(oy + y * u)}h{f(w * u)}v{f(h * u)}h-{f(w * u)}z' for x, y, w, h in rects)


def cells_d(cells, u=1, ox=0, oy=0):
    return rects_to_d(cells_to_rects(cells), u, ox, oy) if cells else ''


def text_d(s, x, y, u, anchor='start', spacing=1):
    cells, w = text_cells(s, spacing)
    ox = x - (w * u // 2 if anchor == 'middle' else w * u if anchor == 'end' else 0)
    return cells_d(cells, u, ox, y)


def text(s, x, y, u, fill, anchor='start', shadow=None, spacing=1, cls=''):
    so = u if u <= 4 else 4
    """Pixel text as <path>. `shadow` adds a 1-unit drop shadow in that colour."""
    out = ''
    if shadow:
        out += f'<path d="{text_d(s, x + so, y + so, u, anchor, spacing)}" fill="{shadow}"/>'
    c = f' class="{cls}"' if cls else ''
    return out + f'<path{c} d="{text_d(s, x, y, u, anchor, spacing)}" fill="{fill}"/>'


def notched(w, h, n):
    return f'M{n} 0H{w-n}V{n}H{w}V{h-n}H{w-n}V{h}H{n}V{h-n}H0V{n}H{n}Z'


def panel(w, h, fill, border, n=4, b=3):
    """8-bit window: border colour outer, fill colour inner, stepped corners."""
    inner = (f'M{b+n} {b}H{w-b-n}V{b+n}H{w-b}V{h-b-n}H{w-b-n}V{h-b}H{b+n}V{h-b-n}H{b}V{b+n}H{b+n}Z')
    return f'<path d="{notched(w, h, n)}" fill="{border}"/><path d="{inner}" fill="{fill}"/>'


STYLE = """
.blink{animation:blink 1.1s steps(1) infinite}
@keyframes blink{0%,60%{opacity:1}61%,100%{opacity:0}}
.tw1{animation:tw 3.2s steps(1) infinite}.tw2{animation:tw 4.1s steps(1) -1.3s infinite}.tw3{animation:tw 5.3s steps(1) -2.7s infinite}
@keyframes tw{0%,70%{opacity:1}71%,85%{opacity:.2}86%,100%{opacity:1}}
.ff1{animation:ff 4s steps(1) infinite}.ff2{animation:ff 5s steps(1) -1.7s infinite}.ff3{animation:ff 6s steps(1) -3.1s infinite}
@keyframes ff{0%,35%{opacity:0}36%,70%{opacity:1}71%,100%{opacity:0}}
.sh1{animation:sh 1.8s steps(1) infinite}.sh2{animation:sh 1.8s steps(1) -.9s infinite}
@keyframes sh{0%,49%{opacity:1}50%,100%{opacity:0}}
@keyframes drift{from{transform:translateX(-60px)}to{transform:translateX(290px)}}
.glow{animation:glow 2.4s steps(1) infinite}
@keyframes glow{0%,50%{opacity:.5}51%,100%{opacity:.25}}
.fr1{animation:fr1 .72s steps(1) infinite}.fr2{animation:fr2 .72s steps(1) infinite}.fr3{animation:fr3 .72s steps(1) infinite}
@keyframes fr1{0%,33%{opacity:1}34%,100%{opacity:0}}
@keyframes fr2{0%,33%{opacity:0}34%,66%{opacity:1}67%,100%{opacity:0}}
@keyframes fr3{0%,66%{opacity:0}67%,100%{opacity:1}}
.sp1{animation:sp 2.6s steps(6) infinite}.sp2{animation:sp 3.3s steps(6) -1.1s infinite}.sp3{animation:sp 2.9s steps(6) -2s infinite}
@keyframes sp{0%{transform:translateY(0);opacity:1}80%{opacity:1}100%{transform:translateY(-26px);opacity:0}}
.eyes{animation:eyes 5.5s steps(1) infinite}
@keyframes eyes{0%,94%{opacity:0}95%,98%{opacity:1}99%,100%{opacity:0}}
.twinkle{animation:star 2.2s steps(1) infinite}
@keyframes star{0%,60%{opacity:1}61%,100%{opacity:.35}}
@media (prefers-reduced-motion: reduce){*{animation:none!important}}
"""


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{label}" shape-rendering="crispEdges">'
            f'<style>{STYLE}</style>{body}</svg>')
