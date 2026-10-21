"""Compose reference-style preview cards and element sheets (plain Python + Pillow, run after Blender).

    python compose_sheets.py            -> uses <root>/romantic
"""
import os, sys, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'romantic')
FONT_B = r'C:\Windows\Fonts\segoeuib.ttf'
FONT = r'C:\Windows\Fonts\segoeui.ttf'

# title, key, (sky top, horizon), showcase side element, extra obstacle
MAPS = {
    1: ('Enchanted Jungle Temple', 'enchanted_jungle_temple', ('#6fb8ff', '#ffe3f0'), 'en_heart_lantern'),
    2: ('Romantic City Subway', 'romantic_city_subway', ('#7cc0ff', '#ffe0ea'), 'rc_victorian_lamp'),
    3: ('Sunset Desert Kingdom', 'sunset_desert_kingdom', ('#8a6fd8', '#ffb38a'), 'sd_lion_statue'),
    4: ('Snowy Fairytale Railway', 'snowy_fairytale_railway', ('#2a2470', '#8a6ac8'), 'sf_christmas_tree'),
    5: ('Romantic Neon City', 'romantic_neon_city', ('#1a0838', '#8a2a8a'), 'rn_heart_sign'),
    6: ('Tropical Flower Island', 'tropical_flower_island', ('#4fb4ff', '#e6fbff'), 'tf_tiki_hut'),
    7: ('Red Canyon Railway', 'red_canyon_railway', ('#5a3a8a', '#ff9a5a'), 'rr_balloon_a'),
    8: ('Cherry Blossom Kingdom', 'cherry_blossom_kingdom', ('#9ac8ff', '#ffd6ec'), 'cb_paper_lantern'),
    9: ('Magical Underwater Railway', 'magical_underwater_railway', ('#0a3a8a', '#3ab8f0'), 'mu_jellyfish_pink'),
    10: ('Heavenly Sky Temple', 'heavenly_sky_temple', ('#7ab4ff', '#ffe6f4'), 'hs_angel_statue'),
}
TITLE_BG = (122, 20, 70, 235)
GOLD = (255, 205, 110)


def hexrgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def gradient(w, h, top, bottom):
    a, b = hexrgb(top), hexrgb(bottom)
    img = Image.new('RGB', (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)))
    return img


def rounded_mask(w, h, r):
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255)
    return m


def fit(img, box):
    img = img.copy()
    bb = img.getbbox()
    if bb:
        img = img.crop(bb)
    img.thumbnail(box, Image.LANCZOS)
    return img


def glow_paste(dst, img, xy):
    """Paste RGBA with a soft dark shadow so light assets read on light tiles."""
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sh.putalpha(img.split()[3].point(lambda a: int(a * 0.45)))
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    dst.alpha_composite(Image.merge('RGBA', (Image.new('L', img.size, 20),) * 3 + (sh.split()[3],)), (xy[0] + 4, xy[1] + 6))
    dst.alpha_composite(img, xy)


def tile(size, colors, imgs):
    w, h = size
    bg = gradient(w, h, colors[1], colors[0]).convert('RGBA')
    inner = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    n = len(imgs)
    for k, im in enumerate(imgs):
        box = (int((w - 12) / n), h - 16)
        f = fit(im, box)
        x = 6 + k * box[0] + (box[0] - f.width) // 2
        glow_paste(inner, f, (x, (h - f.height) // 2))
    bg.alpha_composite(inner)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out.paste(bg, (0, 0), rounded_mask(w, h, 14))
    ImageDraw.Draw(out).rounded_rectangle([0, 0, w - 1, h - 1], 14, outline=(255, 255, 255, 90), width=2)
    return out


def load_el(idx, name):
    p = os.path.join(ROOT, 'map%d' % idx, 'elements', name + '.png')
    return Image.open(p).convert('RGBA') if os.path.exists(p) else None


def card(idx):
    title, key, colors, side = MAPS[idx]
    man = json.load(open(os.path.join(ROOT, 'map%d' % idx, 'manifest.json'), encoding='utf-8'))
    kinds = {}
    for a in man['assets']:
        kinds.setdefault(a['kind'], []).append(a['name'])
    W, H, MAIN = 600, 1000, 790
    c = Image.new('RGBA', (W, H), (24, 14, 30, 255))
    prev = Image.open(os.path.join(ROOT, 'map%d' % idx, 'preview.png')).convert('RGBA')
    prev = prev.resize((W, int(prev.height * W / prev.width)), Image.LANCZOS)
    top = int((prev.height - MAIN) * 0.35)
    c.paste(prev.crop((0, top, W, top + MAIN)), (0, 0))
    d = ImageDraw.Draw(c)
    fb = ImageFont.truetype(FONT_B, 30)
    text = '%d. %s' % (idx, title)
    tw = d.textlength(text, font=fb)
    x0, y0 = (W - tw) / 2 - 26, 18
    d.rounded_rectangle([x0, y0, x0 + tw + 52, y0 + 54], 27, fill=TITLE_BG, outline=GOLD, width=3)
    d.text((W / 2, y0 + 27), text, font=fb, fill=(255, 255, 255), anchor='mm')
    seg = load_el(idx, man['segment'])
    obst = (kinds.get('obstacle_low', []) + kinds.get('obstacle_high', []))[:1]
    pups = [n for n in kinds.get('powerup', []) if not n.endswith('_heart')][:1]
    tiles = [
        ('Track\nTexture', [seg] if seg else []),
        ('Obstacles', [load_el(idx, n) for n in obst]),
        ('Coins /\nPower-ups', [load_el(idx, man['coin'])] + [load_el(idx, n) for n in pups]),
        ('Side\nElements', [load_el(idx, side)]),
    ]
    fs = ImageFont.truetype(FONT_B, 17)
    tw_, th_ = 132, 126
    gap = (W - 4 * tw_) / 5
    for k, (label, imgs) in enumerate(tiles):
        x = int(gap + k * (tw_ + gap))
        t = tile((tw_, th_), colors, [i for i in imgs if i is not None])
        c.alpha_composite(t, (x, MAIN + 12))
        d.multiline_text((x + tw_ / 2, MAIN + 12 + th_ + 30), label, font=fs, fill=(240, 236, 245), anchor='mm', align='center', spacing=2)
    c.save(os.path.join(ROOT, 'map%d' % idx, 'card.png'))
    return c


def coin_card(idx):
    title, key, colors, side = MAPS[idx]
    man = json.load(open(os.path.join(ROOT, 'map%d' % idx, 'manifest.json'), encoding='utf-8'))
    coin = man['coin']
    W, H, MAIN = 600, 1000, 660
    c = Image.new('RGBA', (W, H), (16, 12, 22, 255))
    prev = Image.open(os.path.join(ROOT, 'map%d' % idx, 'preview.png')).convert('RGBA')
    prev = prev.resize((W, int(prev.height * W / prev.width)), Image.LANCZOS)
    top = int((prev.height - MAIN) * 0.3)
    c.paste(prev.crop((0, top, W, top + MAIN)), (0, 0))
    big = load_el(idx, coin + '_3d') or load_el(idx, coin)
    if big:
        big = fit(big, (340, 340))
        glow = Image.new('RGBA', big.size, (0, 0, 0, 0))
        glow.putalpha(big.split()[3].point(lambda a: int(a * 0.85)))
        col = hexrgb(colors[1])
        halo = Image.merge('RGBA', [Image.new('L', big.size, v) for v in (255, min(255, col[1] + 40), min(255, col[2] + 40))] + [glow.split()[3]])
        pad = Image.new('RGBA', (big.width + 120, big.height + 120), (0, 0, 0, 0))
        pad.alpha_composite(halo, (60, 60))
        pad = pad.filter(ImageFilter.GaussianBlur(28))
        x, y = (W - big.width) // 2, MAIN - big.height - 40
        c.alpha_composite(pad, (x - 60, y - 60))
        c.alpha_composite(big, (x, y))
    d = ImageDraw.Draw(c)
    fb = ImageFont.truetype(FONT_B, 30)
    text = '%d. %s' % (idx, title)
    tw = d.textlength(text, font=fb)
    x0, y0 = (W - tw) / 2 - 26, 18
    d.rounded_rectangle([x0, y0, x0 + tw + 52, y0 + 54], 27, fill=TITLE_BG, outline=GOLD, width=3)
    d.text((W / 2, y0 + 27), text, font=fb, fill=(255, 255, 255), anchor='mm')
    d.rounded_rectangle([10, MAIN + 10, W - 10, H - 10], 18, fill=(22, 18, 28), outline=(70, 60, 80), width=2)
    d.text((W / 2, MAIN + 42), 'Coin Shape (Front / Side / 3D View)', font=ImageFont.truetype(FONT_B, 22), fill=(240, 236, 245), anchor='mm')
    fs = ImageFont.truetype(FONT_B, 20)
    for k, (suffix, label) in enumerate((('_front', 'Front'), ('_side', 'Side'), ('_3d', '3D View'))):
        el = load_el(idx, coin + suffix)
        cx = W * (k + 0.5) / 3
        if el:
            f = fit(el, (150, 190) if suffix != '_side' else (70, 190))
            glow_paste(c, f, (int(cx - f.width / 2), MAIN + 75 + (190 - f.height) // 2))
        d.text((cx, H - 40), label, font=fs, fill=(240, 236, 245), anchor='mm')
    c.save(os.path.join(ROOT, 'map%d' % idx, 'coin_card.png'))
    return c


def element_sheet(idx):
    title, key, colors, side = MAPS[idx]
    man = json.load(open(os.path.join(ROOT, 'map%d' % idx, 'manifest.json'), encoding='utf-8'))
    order = ['segment', 'coin', 'powerup', 'obstacle_low', 'obstacle_high', 'obstacle_train', 'ramp', 'landmark', 'prop', 'backdrop']
    assets = sorted(man['assets'], key=lambda a: (order.index(a['kind']) if a['kind'] in order else 99, a['name']))
    cols, tw, th = 6, 230, 270
    rows = (len(assets) + cols - 1) // cols
    W, H = cols * tw + 40, rows * th + 130
    img = gradient(W, H, colors[0], colors[1]).convert('RGBA')
    d = ImageDraw.Draw(img)
    d.text((W / 2, 55), '%d. %s — all elements' % (idx, title), font=ImageFont.truetype(FONT_B, 40), fill=(255, 255, 255),
           anchor='mm', stroke_width=3, stroke_fill=(90, 20, 60))
    fl, fk = ImageFont.truetype(FONT_B, 16), ImageFont.truetype(FONT, 14)
    prefix = assets[0]['name'].split('_')[0] + '_'
    for i, a in enumerate(assets):
        x, y = 20 + (i % cols) * tw, 110 + (i // cols) * th
        panel = Image.new('RGBA', (tw - 14, th - 14), (255, 255, 255, 70))
        img.alpha_composite(panel, (x + 7, y + 7))
        el = load_el(idx, a['name'])
        if el:
            f = fit(el, (tw - 34, th - 80))
            glow_paste(img, f, (x + (tw - f.width) // 2, y + 16 + (th - 80 - f.height) // 2))
        name = a['name'].replace(prefix, '', 1).replace('_', ' ').title()
        d.text((x + tw / 2, y + th - 46), name, font=fl, fill=(255, 255, 255), anchor='mm', stroke_width=2, stroke_fill=(60, 20, 50))
        d.text((x + tw / 2, y + th - 26), a['kind'].replace('_', ' '), font=fk, fill=(255, 235, 245), anchor='mm', stroke_width=2,
               stroke_fill=(60, 20, 50))
    img.convert('RGB').save(os.path.join(ROOT, 'map%d' % idx, 'elements_sheet.png'))


def main():
    cards, coins = [], []
    for idx in MAPS:
        cards.append(card(idx))
        coins.append(coin_card(idx))
        element_sheet(idx)
        print('map', idx, 'done')
    g = 8
    W, H = cards[0].size
    for items, fname in ((cards, 'all_maps_reference_style.png'), (coins, 'all_coins_reference_style.png')):
        sheet = Image.new('RGB', (5 * W + 6 * g, 2 * H + 3 * g), (14, 10, 18))
        for i, c in enumerate(items):
            sheet.paste(c.convert('RGB'), (g + (i % 5) * (W + g), g + (i // 5) * (H + g)))
        sheet.save(os.path.join(ROOT, fname))
        print('saved', os.path.join(ROOT, fname))


if __name__ == '__main__':
    main()
