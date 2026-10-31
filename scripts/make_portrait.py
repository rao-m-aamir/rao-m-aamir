#!/usr/bin/env python3
"""
One-off tool: turns a photo into the pixel portrait used on the character sheet.
It cuts you out of the background, shrinks you to a tiny grid, tints the tones with the
page palette and saves ONLY the resulting pixels to scripts/portrait.json (no photo is stored).

    pip install pillow rembg onnxruntime
    python scripts/make_portrait.py me.jpg                  # moonlit green tint (default)
    python scripts/make_portrait.py me.jpg --keep-color     # keep the photo's own colours
    python scripts/make_portrait.py me.jpg --gamma 1.5      # darker / moodier (1.0 = brightest)
    python scripts/make_portrait.py me.jpg --colors 24 --shift -4    # more colours / nudge the crop left (grid cells)

Then run  python scripts/build_assets.py  to put it on the night-scene card.
"""
import argparse, json, os
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

GW, GH = 75, 115      # must match the card's picture frame (300 x 460 px at 4 px per cell)

def cutout_mask(img):
    from rembg import remove, new_session
    big = img.resize((img.width * 4, img.height * 4), Image.LANCZOS)      # the matte is cleaner on a larger image
    return remove(big, session=new_session('u2net_human_seg'), only_mask=True).resize(img.size, Image.LANCZOS)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('photo'); ap.add_argument('--keep-color', action='store_true')
    ap.add_argument('--colors', type=int, default=20); ap.add_argument('--gamma', type=float, default=1.3); ap.add_argument('--shift', type=float, default=0)
    ap.add_argument('--out', default=os.path.join(os.path.dirname(__file__), 'portrait.json'))
    a = ap.parse_args()
    im = Image.open(a.photo).convert('RGB')
    mask = cutout_mask(im)
    # crop to the frame's aspect ratio, centred on the subject
    w, h = im.size
    cw = min(w, round(h * GW / GH)); ch = round(cw * GH / GW)
    bbox = mask.point(lambda v: 255 if v > 128 else 0).getbbox() or (0, 0, w, h)
    cx = (bbox[0] + bbox[2]) / 2 + a.shift * cw / GW
    x0 = int(max(0, min(w - cw, cx - cw / 2))); y0 = max(0, min(h - ch, bbox[1] - int(ch * 0.2)))
    box = (x0, y0, x0 + cw, y0 + ch)
    im, mask = im.crop(box).resize((GW, GH), Image.LANCZOS), mask.crop(box).resize((GW, GH), Image.LANCZOS)
    alpha = mask.point(lambda v: 255 if v > 118 else 0)
    if not a.keep_color:      # moonlit duotone: deep forest -> teal -> cream
        g = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=1, mask=alpha)
        g = ImageEnhance.Contrast(g).enhance(1.12)
        g = g.point(lambda v: round(255 * (v / 255) ** a.gamma))      # darken the highlights a little so the face keeps its detail
        im = ImageOps.colorize(g, black='#07120f', mid='#3f8a6a', white='#f5f1d8', blackpoint=0, whitepoint=255, midpoint=110)
    black = Image.new('RGB', im.size, (7, 18, 15))
    q = Image.composite(im, black, alpha).quantize(colors=a.colors, method=Image.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')
    px, ap_ = q.load(), alpha.load()
    pal, rows = [], []
    for y in range(GH):
        row = ''
        for x in range(GW):
            if ap_[x, y] == 0:
                row += '.'; continue
            c = '#%02x%02x%02x' % px[x, y]
            if c not in pal: pal.append(c)
            row += chr(97 + pal.index(c))
        rows.append(row)
    json.dump({'w': GW, 'h': GH, 'palette': pal, 'rows': rows}, open(a.out, 'w'))
    print(f'wrote {a.out}: {GW}x{GH}, {len(pal)} colours, crop {box}')

if __name__ == '__main__':
    main()
