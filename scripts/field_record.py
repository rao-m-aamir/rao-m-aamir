#!/usr/bin/env python3
"""
Builds assets/trail-record.svg from your PUBLIC GitHub repos (repo count, stars, top languages).
Refreshed weekly (and on demand) by .github/workflows/trail-record.yml. To run it by hand:
    GH_USER=M-Aamir-Rao python scripts/field_record.py
If GitHub can't be reached, the existing SVG is left untouched.
"""
import datetime, json, os, sys, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
from pixel import PAL as P, text, text_width, panel, svg

USER  = os.environ.get('GH_USER', 'M-Aamir-Rao')
TOKEN = os.environ.get('GITHUB_TOKEN')
OUT   = os.environ.get('OUT', os.path.join(os.path.dirname(__file__), '..', 'assets', 'trail-record.svg'))
SKIP_LANGS = {'Makefile', 'CMake', 'Dockerfile', 'Batchfile', 'Shell'}   # build files, not "languages you write"

def api(path):
    h = {'Accept': 'application/vnd.github+json', 'User-Agent': 'trail-record', 'X-GitHub-Api-Version': '2022-11-28'}
    if TOKEN: h['Authorization'] = 'Bearer ' + TOKEN
    with urllib.request.urlopen(urllib.request.Request('https://api.github.com' + path, headers=h), timeout=20) as r:
        return json.load(r)

def collect():
    repos = [r for r in api(f'/users/{USER}/repos?per_page=100&type=owner') if not r['fork']]
    langs = {}
    for r in repos:
        for k, v in api(f"/repos/{USER}/{r['name']}/languages").items():
            if k not in SKIP_LANGS: langs[k] = langs.get(k, 0) + v
    return {'repos': len(repos), 'stars': sum(r['stargazers_count'] for r in repos), 'langs': langs}

def render(d, stamp):
    total = sum(d['langs'].values()) or 1
    top = sorted(d['langs'].items(), key=lambda kv: -kv[1])[:5]
    w, h = 900, 210
    b = panel(w, h, P['bg'], P['line'], n=6, b=3)
    def stat(x, num, label):
        return text(str(num), x, 50, 6, P['cream']) + text(label, x, 104, 2, P['teal'])
    b += stat(40, d['repos'], 'PUBLIC REPOS') + stat(230, d['stars'], 'STARS') + stat(350, d.get('n_langs', len(d['langs'])), 'LANGUAGES')
    b += f'<path d="M470 28v148" stroke="{P["line"]}" stroke-width="2" stroke-dasharray="4 4" fill="none"/>'
    b += text('TOP LANGUAGES', 500, 28, 2, P['gold'])
    for i, (name, val) in enumerate(top):
        y = 56 + i * 26; pct = val * 100 / total
        b += text(name, 500, y, 2, P['cream'])
        filled = max(1, round(pct / 10))
        for j in range(10):          # ten pixel blocks per bar
            on = j < filled
            col = (P['gold'] if i == 0 else P['teal']) if on else P['panel']
            b += f'<rect x="{630 + j * 19}" y="{y}" width="15" height="12" fill="{col}"/>'
        b += text(f'{pct:.0f}%', 872, y, 2, P['mint'], 'end')
    label = stamp if stamp.startswith('AWAITING') else f'SYNCED {stamp} // PUBLIC REPOS ONLY'
    b += text(label, 40, 184, 2, P['dim'])
    return svg(w, h, b, f"GitHub trail record: {d['repos']} public repositories, {d['stars']} stars, {d.get('n_langs', len(d['langs']))} languages.")

if __name__ == '__main__':
    try:
        data = collect()
    except Exception as e:
        print('Could not reach GitHub, keeping existing card:', e); sys.exit(0)
    open(OUT, 'w', encoding='utf-8').write(render(data, datetime.date.today().isoformat()))
    print('wrote', OUT, data['repos'], 'repos,', data['stars'], 'stars,', len(data['langs']), 'languages')
