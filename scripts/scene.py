"""Procedural pixel-art night landscape (sky, moon, hills, pines, river + dirt path),
modelled on the portfolio's 'Wandering Log' world. Everything lives on a small grid;
the SVG scales it up with crisp edges."""
import math, random
from pixel import cells_d

C = dict(
    sky=['#0a1620', '#0e1f29', '#122934', '#173340', '#1d3f48', '#264e50', '#305c58'],
    moon='#e8e2b4', moon_sh='#c9c593', star='#f5f1d8', star_dim='#8fa89c',
    cloud='#2a4850', cloud_hi='#3a5c62', cloud_lo='#203a41', streak='#8c7650',
    far='#1c3844', far_hi='#27505a', near='#162f37', near_hi='#1f4249',
    tree_line='#0f2a22', tree_line2='#143428',
    grass=['#173627', '#1c4030', '#234b36'], speck='#2d6140', flower='#b9a15c', flower2='#c9714a',
    river='#2a5f68', river_dk='#1f4a52', river_hi='#4a8d94', bank='#163a36',
    path='#7d6444', path_hi='#9a7d57', path_dk='#5f4a33',
    trunk='#2a1f19', pine_dk='#0f2c1c', pine_mid='#17432a', pine_lt='#255c37',
    leaf_dk='#17432a', leaf_mid='#255c37', leaf_lt='#3a7d48', firefly='#f2d675',
)


class Scene:
    def __init__(self, W, H, horizon, seed=3, k=1.0, cx=None, moon=(0.88, 0.2, 7)):
        self.W, self.H, self.hz, self.k = W, H, horizon, k
        self.cx = cx if cx is not None else W / 2
        self.r = random.Random(seed)
        self.base = {}                       # (x,y) -> colour   (static layer)
        self.stars = [[], [], []]            # three twinkle groups of (x,y,colour)
        self.crosses = []                    # bright 5-pixel stars
        self.clouds = []                     # list of dict cells
        self.fireflies = [[], [], []]
        self.shimmer = [set(), set()]
        self.moon = moon
        self.build()

    # ---------------- helpers ----------------
    def put(self, x, y, c, layer=None):
        x, y = int(x), int(y)
        if 0 <= x < self.W and 0 <= y < self.H:
            (self.base if layer is None else layer)[(x, y)] = c

    def sky_color(self, x, y):
        v = y / self.hz * (len(C['sky']) - 1)
        b = int(v); f = v - b
        if b >= len(C['sky']) - 1:
            return C['sky'][-1]
        if f > 0.78 and (x + y) % 2 == 0:
            return C['sky'][b + 1]
        if f > 0.9:
            return C['sky'][b + 1]
        return C['sky'][b]

    def path_center(self, y):
        t = max(0.0, (y - self.hz) / (self.H - self.hz))
        k = self.k
        wig = 6 * k * math.sin(t * 4.5) * t
        rc = self.cx - (1 + 8 * k * t ** 1.2) + wig
        pc = self.cx + (1 + 16 * k * t ** 1.2) + 0.8 * wig
        return rc, 0.5 + 12 * k * t, pc, 0.4 + 4.6 * k * t, t

    # ---------------- layers ----------------
    def build(self):
        W, H, hz, r = self.W, self.H, self.hz, self.r
        for y in range(hz + 1):
            for x in range(W):
                self.put(x, y, self.sky_color(x, y))
        self.make_moon()
        self.make_stars()
        self.make_hills()
        self.make_ground()
        self.make_river_path()
        self.make_clouds()
        self.make_fireflies()

    def make_moon(self):
        fx, fy, rad = self.moon
        mx, my = int(self.W * fx), int(self.H * fy)
        for y in range(my - rad - 4, my + rad + 5):
            for x in range(mx - rad - 4, mx + rad + 5):
                d = math.hypot(x - mx, y - my)
                if rad < d <= rad + 4 and (x + y) % 2 == 0 and 0 <= y <= self.hz:
                    base = self.sky_color(x, y)
                    i = C['sky'].index(base)
                    self.put(x, y, C['sky'][min(i + 1, len(C['sky']) - 1)])
        for y in range(my - rad, my + rad + 1):
            for x in range(mx - rad, mx + rad + 1):
                d = math.hypot(x - mx, y - my)
                if d <= rad + 0.2:
                    cut = math.hypot(x - (mx + rad * 0.45), y - (my - rad * 0.3))
                    if cut <= rad * 0.88:
                        continue
                    self.put(x, y, C['moon_sh'] if d > rad - 1.2 and x < mx - 1 else C['moon'])

    def make_stars(self):
        r = self.r
        mx, my, rad = int(self.W * self.moon[0]), int(self.H * self.moon[1]), self.moon[2]
        n = max(14, int(self.W * self.hz / 95))
        for i in range(n):
            x, y = r.randrange(self.W), r.randrange(1, int(self.hz * 0.62))
            if math.hypot(x - mx, y - my) < rad + 6:
                continue
            col = C['star'] if r.random() < 0.35 else C['star_dim']
            self.stars[i % 3].append((x, y, col))
        for _ in range(max(2, n // 9)):
            x, y = r.randrange(4, self.W - 4), r.randrange(3, int(self.hz * 0.5))
            if math.hypot(x - mx, y - my) < rad + 8:
                continue
            self.crosses.append((x, y))

    def make_hills(self):
        W, hz, r = self.W, self.hz, self.r
        s = W / 225
        ph = [r.uniform(0, 6) for _ in range(6)]
        for x in range(W):
            h1 = 10 + 4.5 * math.sin(x / (22 * s) + ph[0]) + 2.6 * math.sin(x / (9 * s) + ph[1]) + 1.2 * math.sin(x / (4 * s) + ph[2])
            top = int(hz - h1 * min(1, 0.55 + s))
            for y in range(top, hz + 1):
                self.put(x, y, C['far_hi'] if y == top else C['far'])
        for x in range(W):
            h2 = 5 + 2.6 * math.sin(x / (16 * s) + ph[3]) + 1.4 * math.sin(x / (6 * s) + ph[4])
            top = int(hz - h2 * min(1, 0.55 + s))
            for y in range(top, hz + 1):
                self.put(x, y, C['near_hi'] if y == top else C['near'])
        # distant pine silhouettes on the tree line
        x = 1
        while x < W - 1:
            h = r.choice([2, 3, 3, 4, 5]) if s >= 0.5 else r.choice([2, 3, 4])
            base = hz
            for j in range(h):
                hw = j // 2
                for xx in range(x - hw, x + hw + 1):
                    self.put(xx, base - h + j, C['tree_line2'] if (xx + j) % 3 else C['tree_line'])
            x += r.choice([2, 3, 3, 4])

    def make_ground(self):
        W, H, hz, r = self.W, self.H, self.hz, self.r
        for y in range(hz + 1, H):
            t = (y - hz) / (H - hz)
            for x in range(W):
                i = 0 if (t < .22 or (t < .4 and (x + y) % 2 == 0)) else 1
                if t > .7 and (x * 3 + y) % 5 == 0:
                    i = 2
                self.put(x, y, C['grass'][i])
        for _ in range(int(W * (H - hz) * 0.07)):
            x, y = r.randrange(W), r.randrange(hz + 2, H)
            self.put(x, y, C['speck'])
        for _ in range(int(W * (H - hz) * 0.012)):
            x, y = r.randrange(W), r.randrange(hz + 4, H)
            self.put(x, y, C['flower'] if r.random() < .75 else C['flower2'])

    def make_river_path(self):
        r = self.r
        for y in range(self.hz + 1, self.H):
            rc, rw, pc, pw, t = self.path_center(y)
            for x in range(self.W):
                if abs(x + 0.5 - pc) <= pw:
                    edge = abs(x + 0.5 - pc) > pw - 1.2
                    c = C['path_dk'] if edge else (C['path_hi'] if r.random() < .12 else C['path'])
                    self.put(x, y, c)
            for x in range(self.W):
                d = abs(x + 0.5 - rc)
                if d <= rw + 1:
                    if d > rw:
                        self.put(x, y, C['bank'])
                    else:
                        self.put(x, y, C['river_dk'] if d > rw - 1.4 else C['river'])
                        if d < rw - 1.4 and r.random() < .16:
                            self.shimmer[r.randrange(2)].add((x, y))

    def pine(self, cx, by, h, light=True):
        top = by - h
        for y in range(top, by - 2):
            rr = y - top
            hw = rr // 2 + (1 if rr % 4 == 3 else 0)
            hw = min(hw, h // 3 + 1)
            for x in range(cx - hw, cx + hw + 1):
                if x < cx - hw // 2 and light:
                    c = C['pine_lt'] if (x + y) % 3 == 0 else C['pine_mid']
                elif x > cx + hw // 3:
                    c = C['pine_dk']
                else:
                    c = C['pine_mid']
                self.put(x, y, c)
        for y in range(by - 2, by):
            self.put(cx, y, C['trunk']); self.put(cx - 1, y, C['trunk'])
        for x in range(cx - 3, cx + 4):
            self.put(x, by, C['grass'][0])

    def round_tree(self, cx, by, rad):
        cy = by - rad * 2 - 2
        for dy in range(-rad, rad + 1):
            for dx in range(-rad - 1, rad + 2):
                d = math.hypot(dx / 1.15, dy)
                if d <= rad:
                    lit = dx + dy < -rad * 0.5
                    c = C['leaf_lt'] if lit and (dx + dy) % 2 == 0 else (C['leaf_dk'] if dx + dy > rad * .5 else C['leaf_mid'])
                    self.put(cx + dx, cy + dy, c)
        for y in range(cy + rad - 1, by):
            self.put(cx, y, C['trunk']); self.put(cx - 1, y, C['trunk'])

    def make_clouds(self):
        r = self.r
        for i in range(4):
            w, h = r.randrange(16, 34), r.randrange(4, 7)
            bumps = [(r.uniform(h, w - h), r.uniform(h * .6, h * 1.05)) for _ in range(3)]
            cells = {}
            for x in range(w):
                ht = max((math.sqrt(max(0, rad * rad - (x - bx) ** 2)) for bx, rad in bumps), default=0)
                ht = min(h, int(ht))
                for j in range(ht):
                    y = h - 1 - j
                    cells[(x, y)] = C['cloud_hi'] if j == ht - 1 else (C['cloud_lo'] if j == 0 else C['cloud'])
            y0 = max(int(self.hz * (0.12 + 0.55 * (i / 4)) + r.randrange(-1, 3)), 9 if self.W > 150 else 0)
            self.clouds.append(dict(cells=cells, y=y0, dur=r.choice([110, 150, 210, 260]), delay=-r.randrange(10, 200)))
        for i in range(2):
            w = r.randrange(12, 20)
            cells = {(x, 0): C['streak'] for x in range(w)}
            cells.update({(x, 1): C['streak'] for x in range(2, w - 3)})
            self.clouds.append(dict(cells=cells, y=int(self.hz * (0.28 + 0.2 * i)), dur=r.choice([180, 240]), delay=-r.randrange(10, 220)))

    def make_fireflies(self):
        r = self.r
        for i in range(max(8, int(self.W * (self.H - self.hz) / 260))):
            x, y = r.randrange(2, self.W - 2), r.randrange(self.hz + 3, self.H - 2)
            self.fireflies[i % 3].append((x, y))

    # ---------------- svg ----------------
    def svg_group(self, scale, extra_layers='', trees=True, tree_spec=None):
        """Return SVG body (scaled group). `tree_spec` = list of ('pine'|'round', x, base_y, size)."""
        from collections import defaultdict
        if tree_spec:
            for kind, x, by, size in tree_spec:
                (self.pine if kind == 'pine' else self.round_tree)(x, by, size)
        by_col = defaultdict(set)
        for (x, y), c in self.base.items():
            by_col[c].add((x, y))
        out = f'<g transform="scale({scale})">'
        for c, cells in by_col.items():
            out += f'<path d="{cells_d(cells)}" fill="{c}"/>'
        # shimmer
        for i, cells in enumerate(self.shimmer):
            out += f'<path class="sh{i + 1}" d="{cells_d(cells)}" fill="{C["river_hi"]}"/>'
        # stars
        for i, grp in enumerate(self.stars):
            d = defaultdict(set)
            for x, y, c in grp:
                d[c].add((x, y))
            out += f'<g class="tw{i + 1}">' + ''.join(f'<path d="{cells_d(s)}" fill="{c}"/>' for c, s in d.items()) + '</g>'
        cs = set()
        for x, y in self.crosses:
            cs |= {(x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)}
        if cs:
            out += f'<g class="twinkle"><path d="{cells_d(cs)}" fill="{C["star"]}" opacity=".85"/></g>'
        # clouds
        for cl in self.clouds:
            by = defaultdict(set)
            for p, c in cl['cells'].items():
                by[c].add(p)
            inner = ''.join(f'<path d="{cells_d(s)}" fill="{c}"/>' for c, s in by.items())
            out += (f'<g transform="translate(0 {cl["y"]})" opacity=".92"><g style="animation:drift {cl["dur"]}s steps(350) {cl["delay"]}s infinite">'
                    f'{inner}</g></g>')
        out += extra_layers
        # fireflies
        for i, pts in enumerate(self.fireflies):
            glow = set()
            for x, y in pts:
                glow |= {(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)}
            out += (f'<g class="ff{i + 1}"><path d="{cells_d(glow)}" fill="{C["firefly"]}" opacity=".28"/>'
                    f'<path d="{cells_d(set(pts))}" fill="{C["firefly"]}"/></g>')
        return out + '</g>'
