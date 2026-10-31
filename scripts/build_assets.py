#!/usr/bin/env python3
"""
Rebuilds every pixel-art SVG in assets/ (banner, character sheet, section headers,
milestone cards, footer).  Pure Python, no dependencies.

    python scripts/build_assets.py                    # rebuild everything
    python scripts/build_assets.py --style wanderer   # swap your portrait for the hooded-traveller sprite

Your portrait comes from scripts/portrait.json (made once by scripts/make_portrait.py from a photo).
Change the words: edit the CONFIG block below and run it again, then commit.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pixel import PAL, text, text_width, panel, notched, svg, cells_d
from scene import Scene, C

# =============================== CONFIG ===============================
NAME      = 'MUHAMMAD AAMIR SAIFI'
CARD_ROWS = [  # (label, value). A blank label continues the group above. None -> STATUS, '???' -> MAIN QUEST
    ('NAME',       NAME),
    ('CLASS',      'COMPUTER SCIENCE STUDENT'),
    ('',           'INSTITUTE OF SPACE TECHNOLOGY'),
    ('STATUS',     None),
    ('MAIN QUEST', '???'),
    ('GUILD',      'HEAD OF VENTURES & PRODUCT'),
    ('',           'LAUNCH @ AFRIUM'),
    ('',           'SOCIAL MEDIA LEAD @ DEVCORE'),
    ('STACK',      'C++  KOTLIN  PHP  JS  SQL'),
    ('PATHS',      'SOFTWARE · AI · PRODUCT'),
    ('',           'CREATIVE WORK · COMMUNITY'),
    ('TROPHY',     'NATIONAL FINALIST, BANOQABIL'),
    ('',           'X ALIBABA AI HACKATHON'),
    ('',           'RUNNER-UP, MASTERCODE IST'),
    ('DRAWN TO',   'AI-LED DEVELOPMENT'),
    ('',           'VISUAL DIRECTION · CIVIC TECH'),
    ('',           'SOCIAL MEDIA · MARKETING'),
]
PROMPT      = 'rao@wandering-log'
SECTIONS = [  # (number, title, right-hand tag)
    ('01', 'THE QUEST BOARD',     'OPEN TRAIL'),
    ('02', 'ACTIVE QUESTS',       'STATUS: ONGOING'),
    ('03', 'TRAINING GROUNDS',    'INVENTORY'),
    ('04', 'MILESTONES',          'UNLOCKED'),
    ('05', 'TRAIL RECORD',        'FROM GITHUB'),
    ('06', 'THE CAMPFIRE',        'SAY HELLO'),
]
SLUGS = ['quest-board', 'active-quests', 'training-grounds', 'milestones', 'trail-record', 'campfire']
# ======================================================================

OUT = os.path.join(os.path.dirname(__file__), '..', 'assets')
P = PAL
def write(name, s):
    path = os.path.join(OUT, name)
    open(path, 'w', encoding='utf-8').write(s)
    print(f'wrote assets/{name:<22} {len(s)/1024:5.1f} KB')

def frame(w, h, n, b, color):
    inner = (f'M{b+n} {b}H{w-b-n}V{b+n}H{w-b}V{h-b-n}H{w-b-n}V{h-b}H{b+n}V{h-b-n}H{b}V{b+n}H{b+n}Z')
    return f'<path fill-rule="evenodd" d="{notched(w, h, n)}{inner}" fill="{color}"/>'

def dashes(x0, x1, y, color, on=4, off=6, h=2):
    d = ''.join(f'M{x} {y}h{on}v{h}h-{on}z' for x in range(x0, x1, on + off))
    return f'<path d="{d}" fill="{color}"/>'

# ------------------------------- sprite --------------------------------
SPR = dict(o='#08120f', L='#6dc29b', h='#3f8a6a', H='#2a6150', c='#f5f1d8', b='#8a6540', B='#5f4430',
           g='#dfc47e', r='#4a3426', R='#33241a', s='#7a5a3a', w='#f6dc7a', W='#c9a24a')
HALF = [  # 9 columns = outer edge ... centre; mirrored automatically (light side left, shaded right)
    "......ooo",
    ".....oLLL",
    "....oLLLh",
    "...oLLhhh",
    "...oLhhhh",
    "...ohhhhh",
    "....ohhhh",
    "....occcc",
    "..oLLLhbb",
    "..oLLhbBb",
    "..oLLhbbb",
    "..oLLhbgg",
    "..oLLhbbb",
    "..oLhhBBB",
    "..oLhhhhh",
    ".oLLhhhhh",
    ".oLhhhhhh",
    "oLLhhhhhh",
    "oLhhhhhhh",
    "ooLLhhhhh",
    ".oooooooo",
    "...orrrr.",
    "...oRRRR.",
]
def sprite():
    """Hooded traveller seen from behind, bedroll pack, walking staff with a lantern."""
    mirror = {'L': 'h', 'h': 'H'}
    cells = {}
    for y, half in enumerate(HALF):
        full = half + ''.join(mirror.get(ch, ch) for ch in reversed(half))
        for x, ch in enumerate(full):
            if ch != '.':
                cells[(x, y)] = SPR[ch]
    # staff + lantern on the right
    for y in range(6, 22):
        cells[(19, y)] = SPR['s']
    for y in range(8, 11):
        for x in (18, 20):
            cells[(x, y)] = SPR['o']
    for x in (18, 19, 20):
        cells[(x, 7)] = SPR['o']; cells[(x, 11)] = SPR['o']
    cells[(19, 8)] = cells[(19, 9)] = cells[(19, 10)] = SPR['w']
    cells[(18, 9)] = cells[(20, 9)] = SPR['W']
    glow = {(x, y) for x in range(15, 25) for y in range(4, 15) if (x - 19) ** 2 + (y - 9) ** 2 <= 22 and (x + y) % 2 == 0}
    return cells, glow, 21, len(HALF)

def draw_sprite(x0, y0, u):
    cells, glow, w, h = sprite()
    from collections import defaultdict
    by = defaultdict(set)
    for p, c in cells.items():
        by[c].add(p)
    s = f'<g transform="translate({x0} {y0}) scale({u})">'
    s += f'<path class="glow" d="{cells_d(glow)}" fill="#f6dc7a"/>'
    s += ''.join(f'<path d="{cells_d(v)}" fill="{c}"/>' for c, v in by.items()) + '</g>'
    return s, w * u, h * u

# ------------------------------- banner --------------------------------
def banner():
    W, H, U = 225, 70, 4
    sc = Scene(W, H, horizon=43, seed=11, k=1.0, moon=(0.86, 0.3, 7))
    trees = [('pine', 9, 67, 36), ('pine', 27, 61, 24), ('round', 46, 63, 5),
             ('pine', 216, 67, 38), ('pine', 198, 62, 25), ('round', 180, 64, 6)]
    body = '<defs><clipPath id="cp"><path d="%s"/></clipPath></defs>' % notched(W * U, H * U, 8)
    body += '<g clip-path="url(#cp)">' + sc.svg_group(U, tree_spec=trees)
    body += f'<rect width="{W*U}" height="{H*U}" fill="#06100f" opacity=".18"/></g>'
    body += frame(W * U, H * U, 8, 3, P['line'])
    # HUD
    body += text("RAO'S WANDERING LOG", 24, 20, 2, P['teal'], shadow=P['shadow'])
    body += text('CHAPTER 01 // SPAWN POINT', 876, 20, 2, P['teal'], 'end', shadow=P['shadow'])
    # title
    u = 10; word = 'RAO'; tw = text_width('RAO.', u); x0 = (900 - tw) // 2
    body += text(word, x0, 52, u, P['cream'], shadow=P['shadow'])
    body += text('.', x0 + text_width(word, u) + u, 52, u, P['gold'], shadow=P['shadow'])
    body += text('TAKING THE SCENIC ROUTE.', 450, 134, 4, P['cream'], 'middle', shadow=P['shadow'])
    body += text('STUDENT  ·  CURIOUS BUILDER  ·  HABITUAL SIDE-QUEST TAKER', 450, 176, 2, P['mint'], 'middle', shadow=P['shadow'])
    return svg(W * U, H * U, body, "Rao's Wandering Log: taking the scenic route. Student, curious builder, habitual side-quest taker.")

# ---------------------------- character sheet ---------------------------
def load_portrait():
    import json
    d = json.load(open(os.path.join(os.path.dirname(__file__), 'portrait.json')))
    cells = {}
    for y, row in enumerate(d['rows']):
        for x, ch in enumerate(row):
            if ch != '.':
                cells[(x, y)] = d['palette'][ord(ch) - 97]
    return cells, d['w'], d['h']

def character_sheet(style='portrait'):
    W, rx, vx, step, gap, y0 = 900, 364, 500, 22, 4, 84
    ys, y = [], y0
    for i, (lab, val) in enumerate(CARD_ROWS):
        if lab and i:
            y += gap
        ys.append(y); y += step
    y_end = ys[-1] + 14
    H = y_end + 70
    fx, fy, fw = 28, 28, 300
    fh = H - 84
    gw, gh = fw // 4, fh // 4
    for lab, val in CARD_ROWS:                      # keep every value inside the card
        if val and val != '???':
            assert vx + text_width(val, 2) <= 876, f'too wide: {val}'
    body = panel(W, H, P['bg'], P['line'], n=8, b=3)
    body += f'<defs><clipPath id="fc"><rect x="{fx}" y="{fy}" width="{fw}" height="{fh}"/></clipPath></defs>'
    body += '<g clip-path="url(#fc)">'
    if style == 'portrait':
        from collections import defaultdict
        sc = Scene(gw, gh, horizon=int(gh * 0.64), seed=9, k=0.5, moon=(0.82, 0.10, 5))
        sc.fireflies = [[], [], []]
        for yy in range(gh):                                  # soft dithered halo behind the head
            for xx in range(gw):
                d = ((xx - 38) ** 2 + ((yy - 44) * 0.9) ** 2) ** 0.5
                if 26 <= d <= 33 and (xx + yy) % 2 == 0 and sc.base.get((xx, yy)) in C['sky']:
                    i = C['sky'].index(sc.base[(xx, yy)])
                    sc.base[(xx, yy)] = C['sky'][min(i + 1, len(C['sky']) - 1)]
        cells, pw, ph = load_portrait()
        ox, oy = (gw - pw) // 2, gh - ph
        subj = {(x + ox, y + oy): c for (x, y), c in cells.items() if 0 <= x + ox < gw and 0 <= y + oy < gh}
        edge = {}
        for (x, y) in subj:                                    # thin dark outline so the cut-out sits in the scene
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, y + dy)
                if q not in subj and 0 <= q[0] < gw and 0 <= q[1] < gh:
                    edge[q] = '#06100f'
        by = defaultdict(set)
        for pt, c in {**edge, **subj}.items():
            by[c].add(pt)
        extra = ''.join(f'<path d="{cells_d(s_)}" fill="{c}"/>' for c, s_ in by.items())
        body += f'<g transform="translate({fx} {fy})">' + sc.svg_group(4, extra_layers=extra) + '</g>'
    else:
        sc = Scene(gw, gh, horizon=int(gh * 0.5), seed=5, k=0.62, moon=(0.76, 0.13, 5))
        b0 = gh - 8
        trees = [('pine', 7, b0, 38), ('pine', 20, b0 - 5, 22), ('pine', 68, b0 + 3, 40), ('pine', 56, b0 - 4, 24)]
        rc, rw, pc, pw, t = sc.path_center(gh - 10)
        sprite_svg, _, _ = draw_sprite(0, 0, 1)
        extra = f'<g transform="translate({int(pc - 10)} {gh - 32})">{sprite_svg}</g>'
        body += f'<g transform="translate({fx} {fy})">' + sc.svg_group(4, extra_layers=extra, tree_spec=trees) + '</g>'
    body += '<rect x="%d" y="%d" width="%d" height="%d" fill="#06100f" opacity=".10"/>' % (fx, fy, fw, fh)
    body += '</g>'
    body += f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" fill="none" stroke="{P["line"]}" stroke-width="2"/>'
    s_ = 14
    for (cx_, cy_, dx, dy) in [(fx + 8, fy + 8, 1, 1), (fx + fw - 8, fy + 8, -1, 1), (fx + 8, fy + fh - 8, 1, -1), (fx + fw - 8, fy + fh - 8, -1, -1)]:
        body += f'<path d="M{cx_} {cy_ + dy*s_}V{cy_}H{cx_ + dx*s_}" fill="none" stroke="{P["mint"]}" stroke-width="3" opacity=".85"/>'
    body += f'<rect x="{fx+14}" y="{fy+14}" width="148" height="22" fill="{P["bg"]}" opacity=".78"/>'
    body += text('SPAWN POINT', fx + 22, fy + 18, 2, P['mint'])
    body += f'<rect x="{fx+fw-86}" y="{fy+14}" width="72" height="22" fill="{P["bg"]}" opacity=".78"/>'
    body += f'<rect class="blink" x="{fx+fw-80}" y="{fy+21}" width="8" height="8" fill="{P["orange"]}"/>'
    body += text('LIVE', fx + fw - 64, fy + 18, 2, P['orange'])
    body += f'<rect x="{fx+14}" y="{fy+fh-36}" width="184" height="22" fill="{P["bg"]}" opacity=".78"/>'
    body += text('CHAPTER 01 // NIGHT', fx + 22, fy + fh - 32, 2, P['teal'])
    body += text('FIG. 1 // THE TRAVELLER', fx, fy + fh + 14, 2, P['dim'])
    # right-hand sheet
    body += text(PROMPT, rx, 36, 2, P['teal']) + text(':~$ ', rx + text_width(PROMPT, 2) + 2, 36, 2, P['dim'])
    body += text('WHOAMI', rx + text_width(PROMPT + ':~$ ', 2) + 4, 36, 2, P['cream'])
    body += dashes(rx, 872, 66, P['dim'], 3, 5)
    for (lab, val), y in zip(CARD_ROWS, ys):
        if lab:
            body += text(lab, rx, y, 2, P['teal'])
        if val is None:
            body += f'<rect class="blink" x="{vx}" y="{y+2}" width="10" height="10" fill="{P["gold"]}"/>'
            body += text('EXPLORING // ON THE TRAIL', vx + 20, y, 2, P['gold'])
        elif val == '???':
            body += text('???', vx, y, 2, P['orange'], cls='blink')
            body += text('STILL SEARCHING', vx + 54, y, 2, P['dim'])
        else:
            body += text(val, vx, y, 2, P['cream'])
    ly = y_end + 14
    body += dashes(rx, 872, ly, P['dim'], 3, 5)
    body += text(PROMPT, rx, ly + 14, 2, P['teal']) + text(':~$ ', rx + text_width(PROMPT, 2) + 2, ly + 14, 2, P['dim'])
    body += f'<rect class="blink" x="{rx + text_width(PROMPT + ":~$ ", 2) + 6}" y="{ly+14}" width="10" height="14" fill="{P["cream"]}"/>'
    return svg(W, H, body, 'Character sheet. Muhammad Aamir Saifi (Rao), Computer Science student at the Institute of Space Technology. Head of Ventures and Product Launch at AFRIUM, Social Media Lead at DevCore. National Finalist, BanoQabil x Alibaba AI Hackathon. Runner-up at MasterCode IST. Drawn to AI-led development, visual direction, civic tech, social media and marketing.')

# ------------------------------- headers --------------------------------
def header(num, title, tag):
    w, h = 900, 48
    body = panel(w, h, P['bg'], P['line'], n=4, b=2)
    body += f'<rect x="10" y="9" width="6" height="30" fill="{P["gold"]}"/>'
    body += text(f'[ {num} ]', 34, 14, 3, P['gold'])
    body += text(title, 126, 14, 3, P['cream'])
    body += text(tag, 856, 17, 2, P['teal'], 'end')
    body += f'<rect class="blink" x="868" y="20" width="8" height="8" fill="{P["gold"]}"/>'
    return svg(w, h, body, f'{num} {title.title()}')

# ------------------------------ milestone -------------------------------
TROPHY = [
    ".gggggggggg.",
    "gGggggggggGg",
    "gGggggggggGg",
    "gGggggggggGg",
    ".gGgggggggG.",
    "..gGgggggG..",
    "...gGgggG...",
    ".....gG.....",
    ".....gG.....",
    "....gggg....",
    "...ddddd....",
    "..dddddddd..",
]
TCOLS = dict(g='#dfc47e', G='#a8873f', d='#5f4430')
STAR = [
    ".....g.....",
    ".....g.....",
    "....ggg....",
    "....ggg....",
    "ggggggggggg",
    ".ggggwgggg.",
    "..gggwggg..",
    "...ggggg...",
    "..ggggggg..",
    "..ggg.ggg..",
    ".ggg...ggg.",
    ".gg.....gg.",
]
SCOLS = dict(g='#dfc47e', G='#a8873f', w='#f8e9b0')

def _icon(rows, cols, shade_lower_right=False):
    from collections import defaultdict
    by = defaultdict(set)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == '.':
                continue
            if shade_lower_right and ch == 'g' and x > 5 and y > 5:
                ch = 'G'
            by[cols[ch]].add((x, y))
    return ''.join(f'<path d="{cells_d(s_)}" fill="{c}"/>' for c, s_ in by.items())

def _sparkles(y_off, seed=0):
    out = ''
    for i, (sx, sy) in enumerate([(30, 22), (136, 38), (122, 100), (28, 96)]):
        out += f'<g class="tw{(i + seed) % 3 + 1}"><path d="{cells_d({(0,1),(1,0),(1,1),(1,2),(2,1)}, 4, sx, sy + y_off)}" fill="{P["gold"]}"/></g>'
    return out

def milestone():
    w, ph, gap = 900, 124, 14
    h = ph * 2 + gap
    body = ''
    # 1 - National finalist (Ustad-e-Karigar)
    body += panel(w, ph, P['bg'], P['line'], n=6, b=3)
    body += '<g transform="translate(50 30) scale(6)">' + _icon(STAR, SCOLS, True) + '</g>' + _sparkles(0)
    body += text('NATIONAL FINALIST', 190, 22, 5, P['cream'], shadow=P['shadow'])
    body += text('BANOQABIL X ALIBABA AI HACKATHON', 190, 66, 3, P['gold'])
    body += text('THE QUEST: USTAD-E-KARIGAR · KOTLIN + GEMINI + ROOM', 190, 98, 2, P['teal'])
    # 2 - Runner-up (MasterCode)
    oy = ph + gap
    body += f'<g transform="translate(0 {oy})">' + panel(w, ph, P['bg'], P['line'], n=6, b=3)
    body += '<g transform="translate(48 30) scale(6)">' + _icon(TROPHY, TCOLS) + '</g>' + _sparkles(0, 1)
    body += text('RUNNER-UP', 190, 22, 5, P['cream'], shadow=P['shadow'])
    body += text('MASTERCODE · IST', 190, 66, 3, P['gold'])
    body += text('COMPETITIVE PROGRAMMING · C++', 190, 98, 2, P['teal'])
    body += text('SOME QUESTS COME', 868, 74, 2, P['dim'], 'end') + text('WITH A SMALL TROPHY.', 868, 94, 2, P['dim'], 'end') + '</g>'
    return svg(w, h, body, 'Milestones. National Finalist in the BanoQabil x Alibaba AI Hackathon with Ustad-e-Karigar. Runner-up at MasterCode, IST, in competitive programming with C++.')

# -------------------------------- footer --------------------------------
FIRE = [  # three flicker frames, 9 wide
    ["....o....", "...oro...", "..orRro..", "..orgro..", ".orgggro.", ".orgwgro.", "..orgro.."],
    ["...o.....", "...oro...", "..orRro..", ".orrgro..", ".orgggro.", ".orgwgro.", "..orgro.."],
    [".....o...", "...oro...", "..orRro..", "..orgrro.", ".orgggro.", ".orgwgro.", "..orgro.."],
]
FC = dict(o='#9a4a1c', r='#d4691f', R='#e08a3c', g='#f2b340', w='#f8e08a')
def footer():
    w, h = 900, 168
    body = panel(w, h, P['bg'], P['line'], n=6, b=3)
    body += dashes(24, 876, 20, P['dim'], 3, 5)
    body += text('THE END OF THE KNOWN TRAIL', 450, 36, 4, P['cream'], 'middle', shadow=P['shadow'])
    from collections import defaultdict
    fu = 5; fx, fy = 450 - 9 * fu // 2 - 1, 92
    for i, fr in enumerate(FIRE):
        by = defaultdict(set)
        for y, row in enumerate(fr):
            for x, ch in enumerate(row):
                if ch != '.':
                    by[FC[ch]].add((x, y))
        body += f'<g class="fr{i+1}" transform="translate({fx} {fy}) scale({fu})">' + ''.join(f'<path d="{cells_d(s)}" fill="{c}"/>' for c, s in by.items()) + '</g>'
    logs = {(x, y) for y in (7, 8) for x in range(0, 9)}
    body += f'<g transform="translate({fx} {fy}) scale({fu})"><path d="{cells_d(logs)}" fill="#5f4430"/><path d="{cells_d({(x,7) for x in range(0,9)})}" fill="#7d6444"/></g>'
    for i, (sx, sy) in enumerate([(442, 94), (462, 90), (451, 96)]):
        body += f'<g class="sp{i+1}"><rect x="{sx}" y="{sy}" width="4" height="4" fill="{P["gold"]}"/></g>'
    body += text('MAIN QUEST STILL NOT FOUND.', 40, 116, 2, P['teal'])
    body += text('STAY CURIOUS. TAKE THE SIDE QUEST.', 860, 116, 2, P['gold'], 'end')
    body += text('CONNECTION TERMINATED', 450, 144, 2, P['dim'], 'middle')
    return svg(w, h, body, 'End of the known trail. Stay curious. Take the side quest.')

# --------------------------------- main ---------------------------------
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--style', choices=['portrait', 'wanderer'], default='portrait')
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    write('banner.svg', banner())
    write('character-sheet.svg', character_sheet(a.style))
    for slug, (n, t, tag) in zip(SLUGS, SECTIONS):
        write(f'sec-{slug}.svg', header(n, t, tag))
    write('milestone.svg', milestone())
    write('footer.svg', footer())
