"""Asset lists + scene layouts for the 10 runner maps.

Conventions (shared by every map, so a game can swap maps freely):
  * runner moves along +Y, lanes at x = -2.6 / 0 / +2.6 (lib.LANE)
  * ground segments are 10 m long (lib.SEG), origin at the segment start
  * obstacles / coins are centred on x=0 -> place them at a lane's x
  * coins face -Y (towards the player), centre at their origin
  * side buildings face +X (rotate 180 deg for the right-hand side)
"""
import math, random
from lib import *


# =========================================================================== shared obstacle shapes
def stone_block(name, m, m2, moss=None, size=(2.3, 1.2, 1.1), seed=0, kind='obstacle_low'):
    p = Part(name, kind)
    r = random.Random(seed)
    w, d, h = size
    p.box(size, (0, 0, h / 2), m, bevel=0.12, jitter=0.02, seed=seed)
    for i in range(3):
        p.box((w * 0.22, 0.08, h * 0.45), (-w / 3 + i * w / 3, -d / 2 - 0.02, h * 0.5), m2, bevel=0.02)
    p.box((w * 0.9, 0.06, 0.08), (0, -d / 2 - 0.03, h * 0.85), m2)
    if moss:
        p.box((w * 0.7, d * 0.6, 0.1), (r.uniform(-0.2, 0.2), 0, h + 0.03), moss, bevel=0.03)
        p.box((0.25, 0.06, h * 0.5), (w * 0.3, -d / 2 - 0.03, h * 0.7), moss)
    return p


def beam_gate(name, pillar, beam, deco=None, moss=None, clearance=1.55, round_top=False):
    p = Part(name, 'obstacle_high')
    top = 2.9
    for x in (-1.15, 1.15):
        p.box((0.45, 0.6, top), (x, 0, top / 2), pillar, bevel=0.06)
        p.box((0.65, 0.8, 0.2), (x, 0, 0.1), pillar, bevel=0.04)
    bh = top + 0.2 - clearance
    p.box((3.0, 0.75, bh), (0, 0, clearance + bh / 2), beam, bevel=0.08)
    if round_top:
        p.ring(1.1, 1.6, 0.7, (0, 0, top + 0.2), beam, a0=0, a1=180, seg=12)
    if deco:
        for i in range(4):
            p.box((0.4, 0.08, 0.4), (-0.9 + i * 0.6, -0.4, clearance + bh / 2), deco, bevel=0.02)
    if moss:
        p.box((2.4, 0.6, 0.08), (0.2, 0, top + 0.22), moss, bevel=0.02)
        for x in (-0.6, 0.4, 0.9):
            p.box((0.1, 0.05, 0.5), (x, -0.4, clearance + 0.05), moss)
    return p


def log(name, bark, ring_m, moss=None, length=2.4, rad=0.45, kind='obstacle_low'):
    p = Part(name, kind)
    p.cyl(rad, length, (0, 0, rad), bark, rot=(0, 90, 0), seg=12, jitter=0.02)
    for sg in (-1, 1):
        p.cyl(rad * 0.85, 0.04, (sg * length / 2, 0, rad), ring_m, rot=(0, 90, 0), seg=12)
    p.rod((0.3, 0, rad * 1.6), (0.5, -0.2, rad * 2.4), 0.08, bark, seg=6, r2=0.03)
    if moss:
        p.box((length * 0.5, rad * 1.2, 0.08), (-0.2, 0, rad * 2), moss, bevel=0.03)
    return p


def rubble(name, mats, seed=0, kind='obstacle_low'):
    p = Part(name, kind)
    r = random.Random(seed)
    for i in range(7):
        s = r.uniform(0.45, 0.8)
        p.box((s * 1.2, s, s * 0.8), (r.uniform(-0.8, 0.8), r.uniform(-0.3, 0.3), s * 0.4 + (0.5 if i > 4 else 0)),
              r.choice(mats), rot=(0, 0, r.uniform(-30, 30)), bevel=0.08, jitter=0.03, seed=seed + i)
    return p


# =========================================================================== MAP 1 - Jungle Temple
def temple_gate(name, st, st2, dark, moss, vine, seed=3):
    p = Part(name, 'landmark')
    r = random.Random(seed)
    W, D, H, dw, dh = 20.0, 6.0, 8.5, 7.0, 6.5
    side = (W - dw) / 2
    for sg in (-1, 1):
        p.box((side, D, H), (sg * (dw / 2 + side / 2), 0, H / 2), st, bevel=0.12)
    p.box((dw, D, H - dh), (0, 0, dh + (H - dh) / 2), st)
    for sg in (-1, 1):
        p.box((0.8, D + 0.3, dh + 0.4), (sg * (dw / 2 + 0.2), 0, (dh + 0.4) / 2), st2, bevel=0.06)
    p.box((dw + 1.8, D + 0.3, 0.9), (0, 0, dh + 0.45), st2, bevel=0.06)
    p.box((dw, D * 0.9, dh), (0, 0.5, dh / 2), dark)
    z = H
    tiers = ((W - 1.5, D - 0.5, 0.5), (W - 4, D - 1.2, 3.0), (W - 5, D - 1.4, 0.5),
             (W - 9, D - 2.2, 2.6), (W - 10, D - 2.4, 0.45), (W - 13.5, D - 3.0, 2.4), (W - 14.5, D - 3.2, 0.4))
    fronts = []
    for i, (w, d, h) in enumerate(tiers):
        p.box((w, d, h), (0, 0, z + h / 2), st2 if i % 2 == 0 else st, bevel=0.08)
        fronts.append((w, d, z, h))
        z += h
    for k in range(70):
        x = r.uniform(-W / 2 + 0.7, W / 2 - 0.7)
        zz = r.uniform(0.5, H - 0.4)
        if abs(x) < dw / 2 + 1.2 and zz < dh + 1.2:
            continue
        p.box((r.uniform(0.8, 1.7), 0.12, r.uniform(0.4, 0.75)), (x, -D / 2 - 0.04, zz), r.choice([st, st2]), bevel=0.03)
    w, d, z0, h = fronts[1]
    for i in range(7):
        p.box((0.9, 0.18, 0.9), (-4.5 + i * 1.5, -d / 2 - 0.08, z0 + h / 2), st2, bevel=0.05)
        p.box((0.45, 0.2, 0.45), (-4.5 + i * 1.5, -d / 2 - 0.12, z0 + h / 2), dark)
    w, d, z0, h = fronts[5]
    p.box((2.2, 0.3, 1.8), (0, -d / 2 - 0.1, z0 + h / 2), st2, bevel=0.06)
    p.box((1.2, 0.35, 0.9), (0, -d / 2 - 0.12, z0 + h / 2), dark)
    for (w, d, z0, h) in fronts:
        for k in range(3):
            p.box((r.uniform(1.0, 3.0), r.uniform(0.6, 1.5), 0.1),
                  (r.uniform(-w / 2.5, w / 2.5), -d / 2 + 0.5, z0 + h + 0.03), r.choice([moss, vine]), bevel=0.03)
    for k in range(14):
        x = r.choice((-1, 1)) * r.uniform(dw / 2 + 1.0, W / 2 - 0.5) if k < 10 else r.uniform(-dw / 2, dw / 2)
        ztop = H if k < 10 else H
        n = r.randint(4, 9)
        for j in range(n):
            p.box((0.14, 0.08, 0.5), (x + r.uniform(-0.08, 0.08), -D / 2 - 0.1, ztop - 0.25 - j * 0.48), vine)
            if j % 2 == 0:
                p.box((0.3, 0.06, 0.18), (x + 0.12, -D / 2 - 0.12, ztop - 0.3 - j * 0.48), moss, rot=(0, 30, 0))
    return p


def map1():
    S1, S2, S3 = mat('stone_a', '#9b9a84', .85), mat('stone_b', '#878670', .85), mat('stone_c', '#aaa792', .85)
    G, WL = mat('grout', '#5f5b4a', .9), mat('wall_stone', '#7f7c69', .85)
    MO, MO2 = mat('moss', '#5f9a2c', .8), mat('moss_light', '#7cb83a', .8)
    LF, LF2, LF3 = mat('leaf', '#3f8f2a', .7), mat('leaf_light', '#5aad34', .7), mat('leaf_dark', '#2e6e22', .7)
    TR, TR2 = mat('bark', '#6b4a2b', .9), mat('bark_dark', '#563a20', .9)
    DK = mat('doorway_dark', '#0b0b0b', 1)
    FI, FI2 = mat('fire', '#ff7a12', .5, emit=8), mat('fire_core', '#ffd84a', .5, emit=12)
    GO, GO2 = mat('coin_gold', '#f7c948', .3, metal=.9), mat('coin_gold_dark', '#c98f22', .35, metal=.9)
    WA, FO = mat('water', '#8fdcff', .1, emit=.8), mat('foam', '#ffffff', .4, emit=.6)
    BR = mat('bronze', '#6d5a3a', .5, metal=.6)
    WOOD = mat('log_ring', '#c99a5e', .8)
    parts = [
        stone_path('jt_path_segment', [S1, S2, S3], G, WL, moss=MO, wall_h=1.0, seed=11, under=WL),
        temple_gate('jt_temple_gate', WL, S2, DK, MO, MO2),
        torch('jt_torch', S2, BR, FI, FI2, h=0.9),
        palm('jt_palm_tree_a', TR, TR2, LF, LF2, h=7, seed=1),
        palm('jt_palm_tree_b', TR, TR2, LF2, LF3, h=5.5, seed=5),
        round_tree('jt_jungle_tree', TR, [LF, LF2, LF3], h=6, rad=2.8, seed=3),
        bush('jt_fern', [LF, LF2, LF3], seed=2, size=1.2),
        blob_bush('jt_bush', [LF, LF3], seed=4, size=1.3),
        waterfall('jt_waterfall', [WL, S2], WA, FO, h=16, top=[LF, LF2, LF3]),
        cliff('jt_cliff', [WL, S2, S1], w=9, d=7, h=14, seed=7, top=[LF, LF2, LF3]),
        rock('jt_rock_mossy', [S1, S2], size=1.0, seed=3, moss=MO),
        stone_block('jt_obstacle_stone_block', S2, G, moss=MO),
        beam_gate('jt_obstacle_stone_beam', WL, S2, deco=G, moss=MO),
        log('jt_obstacle_fallen_log', TR, WOOD, moss=MO),
        coin('jt_coin', GO, GO2, GO2, 'glyph'),
    ]
    cfg = dict(
        segment='jt_path_segment', seg_range=(-2, 7),
        world=dict(top='#3d8fe0', hor='#cdeeff', strength=1.0, sun=(4.0, '#fff1d6', (50, 0, 35))),
        ground=dict(hex='#3f7d2a', z=-1.5),
        repeat=[('jt_torch', 1, [(-4.65, 5.0, 2.05, 0), (4.65, 5.0, 2.05, 0)])],
        fixed=[('jt_temple_gate', (0, 72, 0), 0, 1.0), ('jt_waterfall', (-22, 55, -1.5), 25, 1.0),
               ('jt_waterfall', (24, 80, -1.5), -20, 1.2), ('jt_cliff', (-26, 85, -1.5), 0, 1.3),
               ('jt_cliff', (26, 45, -1.5), 0, 1.0), ('jt_palm_tree_a', (-8, 64, -1.5), 0, 1.2),
               ('jt_palm_tree_a', (8.5, 66, -1.5), 90, 1.1)],
        scatter=[dict(names=['jt_palm_tree_a', 'jt_palm_tree_b', 'jt_jungle_tree'], n=14, x=(7.5, 16), y=(-10, 62), s=(0.9, 1.3), z=-1.5),
                 dict(names=['jt_fern', 'jt_bush', 'jt_rock_mossy'], n=22, x=(6, 14), y=(-10, 66), s=(0.8, 1.4), z=-1.5),
                 dict(names=['jt_cliff'], n=4, x=(20, 30), y=(0, 70), s=(0.8, 1.2), z=-1.5)],
        obstacles=[('jt_obstacle_stone_block', -1, 14), ('jt_obstacle_stone_beam', 0, 22), ('jt_obstacle_fallen_log', 1, 30),
                   ('jt_obstacle_stone_block', 0, 40), ('jt_obstacle_stone_beam', -1, 48), ('jt_obstacle_fallen_log', 1, 55)],
        coins=[(0, 3, 6), (1, 12, 8), (-1, 28, 6), (1, 40, 6), (0, 50, 6)],
        coin_arcs=[(-1, 14, 7), (0, 40, 7)],
        coin='jt_coin', surface=0.44,
    )
    return parts, cfg


# =========================================================================== MAP 2 - City Subway
def city_building(name, w, d, floors, wall, trim, glass, frame, roof, seed=0, awning=None, door=None, balcony=None):
    p = Part(name, 'backdrop')
    r = random.Random(seed)
    fh = 3.0
    H = floors * fh + 0.6
    p.box((d, w, H), (0, 0, H / 2), wall)
    for f in range(1, floors + 1):
        p.box((d + 0.16, w + 0.16, 0.2), (0, 0, f * fh), trim)
    p.box((d + 0.45, w + 0.45, 0.4), (0, 0, H), trim, bevel=0.05)
    nwin = max(2, int(w / 2.2))
    for f in range(floors):
        zc = f * fh + 1.65
        for i in range(nwin):
            yc = -w / 2 + (i + 0.5) * w / nwin
            if f == 0 and i == nwin // 2:
                p.box((0.15, 1.3, 2.3), (d / 2 + 0.02, yc, 1.15), door or frame)
                continue
            p.box((0.12, 1.35, 1.75), (d / 2 + 0.03, yc, zc), frame)
            p.box((0.16, 1.05, 1.45), (d / 2 + 0.05, yc, zc), glass)
            if f > 0 and balcony and r.random() < 0.35:
                p.box((0.8, 1.6, 0.12), (d / 2 + 0.45, yc, zc - 0.9), trim)
                p.box((0.06, 1.6, 0.6), (d / 2 + 0.83, yc, zc - 0.55), balcony)
        nside = max(1, int(d / 2.4))
        for i in range(nside):
            xc = -d / 2 + (i + 0.5) * d / nside
            for sg in (-1, 1):
                p.box((1.3, 0.12, 1.7), (xc, sg * (w / 2 + 0.03), zc), frame)
                p.box((1.0, 0.16, 1.4), (xc, sg * (w / 2 + 0.05), zc), glass)
    if awning:
        n = max(3, int(w / 0.9))
        for i in range(n):
            p.box((1.4, w / n, 0.08), (d / 2 + 0.6, -w / 2 + (i + 0.5) * w / n, 2.9), awning[i % 2], rot=(0, 22, 0))
    p.box((1.4, 1.2, 0.9), (r.uniform(-d / 4, 0), r.uniform(-w / 4, w / 4), H + 0.6), roof, bevel=0.05)
    if r.random() < 0.6:
        tx, ty = r.uniform(-d / 4, 0), r.uniform(-w / 3, w / 3)
        for lx in (-0.4, 0.4):
            for ly in (-0.4, 0.4):
                p.box((0.08, 0.08, 1.0), (tx + lx, ty + ly, H + 0.7), roof)
        p.cyl(0.65, 1.3, (tx, ty, H + 1.85), roof, seg=12)
        p.cyl(0.7, 0.4, (tx, ty, H + 2.65), roof, seg=12, r2=0.05)
    return p


def skyscraper(name, w, h, body, band, top, seed=0, light=None):
    p = Part(name, 'backdrop')
    r = random.Random(seed)
    p.box((w, w, h), (0, 0, h / 2), body)
    for i in range(1, int(h / 3.2)):
        p.box((w + 0.1, w + 0.1, 0.5), (0, 0, i * 3.2), band)
    p.box((w * 0.7, w * 0.7, 3), (0, 0, h + 1.5), body)
    p.cyl(0.15, 5, (0, 0, h + 5.5), top, seg=6)
    if light:
        p.sphere(0.35, (0, 0, h + 8.1), light)
    return p


def catenary(name, pole, wire, insul, h=6.2, light=None):
    p = Part(name)
    xs = 3 * LANE / 2 + 1.3
    for sg in (-1, 1):
        p.box((0.3, 0.3, h), (sg * xs, 0, h / 2), pole)
        p.box((0.6, 0.6, 0.3), (sg * xs, 0, 0.15), pole)
    p.box((2 * xs + 0.6, 0.25, 0.35), (0, 0, h - 0.2), pole)
    for li in (-1, 0, 1):
        x = li * LANE
        p.rod((x, 0, h - 0.4), (x, 0, h - 1.1), 0.04, pole)
        p.cyl(0.08, 0.25, (x, 0, h - 0.55), insul, seg=8)
        p.rod((x, 0, h - 1.1), (x, 2 * SEG, h - 1.1), 0.025, wire, seg=5)
        p.rod((x, 0, h - 0.45), (x, 2 * SEG, h - 0.45), 0.02, wire, seg=5)
    if light:
        for sg in (-1, 1):
            p.sphere(0.15, (sg * xs, -0.2, h - 0.6), light)
    return p


def bunting(name, rope, flags, pole, span=15.0, h=7.0, seed=0):
    p = Part(name)
    r = random.Random(seed)
    for sg in (-1, 1):
        p.cyl(0.08, h, (sg * span / 2, 0, h / 2), pole, seg=6)
    pts = []
    n = 16
    for i in range(n + 1):
        t = i / n
        pts.append((-span / 2 + t * span, 0, h - 0.2 - 1.2 * math.sin(math.pi * t)))
    for i in range(n):
        p.rod(pts[i], pts[i + 1], 0.02, rope, seg=4)
        if 0 < i:
            x, _, z = pts[i]
            p.prism([(-0.25, 0), (0.25, 0), (0, -0.6)], 0.02, (x, 0, z), flags[i % len(flags)])
    return p


def map2():
    BED, SL, RA = mat('ballast', '#8a5a3c', .95), mat('sleeper', '#5a3a24', .9), mat('rail', '#a7b0ba', .3, metal=.9)
    SW, CU = mat('sidewalk', '#d8c3a0', .85), mat('curb_red', '#e0503a', .7)
    walls = [mat('wall_orange', '#f2a33a', .8), mat('wall_pink', '#e85d75', .8), mat('wall_blue', '#4fb3d9', .8),
             mat('wall_green', '#7ccf6b', .8), mat('wall_yellow', '#f6d04d', .8), mat('wall_purple', '#a77be0', .8)]
    TRIM, GL, FR = mat('trim_cream', '#fff3e0', .7), mat('window_glass', '#2d4a6b', .15, metal=.3), mat('window_frame', '#ffffff', .6)
    ROOF, DOOR = mat('roof_grey', '#6b6560', .8), mat('door_brown', '#6b3e26', .7)
    AW1, AW2 = mat('awning_red', '#e8413a', .7), mat('awning_white', '#fafafa', .7)
    LF, LF2 = mat('leaf', '#3fa83a', .7), mat('leaf_dark', '#2f8a2c', .7)
    TR, TR2 = mat('palm_bark', '#8a6a44', .9), mat('palm_bark_dark', '#6e5236', .9)
    TB, TS, TRF = mat('train_yellow', '#f2b51c', .45), mat('train_blue', '#2c62c9', .45), mat('train_roof', '#c9d1da', .5, metal=.4)
    TW, TL, TU = mat('train_window', '#1d2b3a', .1), mat('train_light', '#fff6c0', .3, emit=6), mat('train_under', '#30343a', .7)
    POLE, WIRE, INS = mat('pole_dark', '#3a3f45', .6, metal=.5), mat('wire', '#1a1a1a', .6), mat('insulator', '#c8a26a', .5)
    BW, BRD = mat('barrier_white', '#f4f4f4', .6), mat('barrier_red', '#d93a2b', .6)
    SKY1, SKY2 = mat('sky_glass', '#7fb2d9', .2, metal=.4), mat('sky_band', '#e8eef5', .6)
    GO, GO2 = mat('coin_gold', '#f7c948', .3, metal=.9), mat('coin_gold_dark', '#c98f22', .35, metal=.9)
    FL = [mat('flag_' + c, h, .7) for c, h in (('red', '#ff4d4d'), ('yellow', '#ffd23f'), ('blue', '#3fa9ff'), ('green', '#5ad16a'))]
    parts = [track_segment('city_track_segment', BED, SL, RA, SW, curb=CU)]
    for i, (w, fl) in enumerate(((8, 3), (8, 4), (8, 3), (8, 5), (8, 4), (8, 3))):
        parts.append(city_building('city_building_%s' % 'abcdef'[i], w, 6, fl, walls[i], TRIM, GL, FR, ROOF, seed=i,
                                   awning=(AW1, AW2) if i % 2 == 0 else None, door=DOOR, balcony=FR))
    parts += [
        palm('city_palm_tree', TR, TR2, LF, LF2, h=7.5, seed=8),
        catenary('city_catenary_frame', POLE, WIRE, INS),
        bunting('city_bunting', WIRE, FL, POLE, span=16.5),
        skyscraper('city_skyscraper', 10, 40, SKY1, SKY2, POLE, seed=1),
        train('city_train', TB, TS, TRF, TW, TL, TU),
        ramp('city_ramp', TU, BRD, BW),
        barrier_low('city_barrier_low', BRD, BW, POLE, light=TL),
        barrier_high('city_barrier_high', POLE, BRD, BW, sign=TS),
        coin('city_coin', GO, GO2, GO2, 'star'),
    ]
    blds = ['city_building_%s' % c for c in 'abcdef']
    cfg = dict(
        segment='city_track_segment', seg_range=(-2, 22), repeat_min_y=8,
        world=dict(top='#3d8fe8', hor='#c6ecff', strength=1.0, sun=(4.5, '#fff4e0', (55, 0, -30))),
        ground=dict(hex='#b9a78a', z=-0.02),
        repeat=[('city_catenary_frame', 2, [(0, 0, 0, 0)]), ('city_bunting', 3, [(0, 5, 0, 0)])],
        rows=[dict(names=blds, x=10.4, y=(-15, 210), step=8.2)],
        scatter=[dict(names=['city_palm_tree'], n=12, x=(6.2, 6.8), y=(-5, 150), s=(0.9, 1.1), z=0.5)],
        fixed=[('city_skyscraper', (-30, 230, 0), 0, 1.0), ('city_skyscraper', (22, 260, 0), 20, 1.4),
               ('city_skyscraper', (-8, 300, 0), 0, 1.8), ('city_skyscraper', (35, 210, 0), 0, 0.9)],
        obstacles=[('city_train', 1, 34), ('city_ramp', 1, 25), ('city_train', 1, 46.5), ('city_barrier_low', 0, 18),
                   ('city_barrier_high', -1, 26), ('city_train', -1, 70), ('city_barrier_low', 0, 52)],
        coins=[(0, 3, 8), (-1, 14, 6), (1, 22, 4), (0, 30, 8)],
        coin_arcs=[(0, 18, 7), (0, 52, 7)],
        coins_raised=[(1, 29.5, 10, 4.1)],
        coin='city_coin', surface=0.56,
    )
    return parts, cfg


# =========================================================================== MAP 3 - Desert Temple
def face_gate(name, st, st2, dark, cloth, gold, seed=5):
    p = Part(name, 'landmark')
    W, H, D = 24.0, 10.0, 6.0
    arched_wall(p, W, H, D, 4.5, 3.8, st, st2, dark)
    tw, th = 9.0, 7.0
    p.box((tw, D - 0.6, th), (0, 0.3, H + th / 2), st, bevel=0.15)
    p.box((tw + 1, D, 0.6), (0, 0, H + 0.3), st2, bevel=0.06)
    fy = -D / 2 + 0.2
    zf = H + 0.6
    p.box((6.0, 1.0, 5.6), (0, fy, zf + 2.9), st2, bevel=0.3)
    p.box((5.0, 0.4, 0.6), (0, fy - 0.6, zf + 4.3), st, bevel=0.1)
    for sg in (-1, 1):
        p.box((1.3, 0.3, 0.6), (sg * 1.3, fy - 0.55, zf + 3.6), dark, bevel=0.08)
        p.box((0.8, 0.8, 2.6), (sg * 3.3, fy, zf + 2.6), st2, bevel=0.1)
    p.prism([(-0.6, 0), (0.6, 0), (0, 1.7)], 0.7, (0, fy - 0.7, zf + 1.6), st)
    p.box((2.6, 0.4, 0.45), (0, fy - 0.6, zf + 1.05), dark, bevel=0.08)
    p.box((3.6, 0.5, 0.4), (0, fy - 0.55, zf + 0.5), st)
    for i, w in enumerate((7.0, 5.8, 4.4)):
        p.box((w, 1.6, 0.6), (0, fy + 0.3, zf + 5.9 + i * 0.6), st if i % 2 else st2, bevel=0.08)
    p.cyl(0.5, 0.3, (0, fy - 0.6, zf + 6.4), gold, rot=(90, 0, 0), seg=12)
    for sg in (-1, 1):
        x = sg * (W / 2 + 1.5)
        p.box((4, D + 1, H + 5), (x, 0, (H + 5) / 2), st, bevel=0.12)
        for i in range(3):
            p.box((0.9, D + 1, 0.9), (x - 1.4 + i * 1.4, 0, H + 5.45), st2, bevel=0.06)
        p.box((1.2, 0.1, 4.0), (x, -D / 2 - 0.55, H - 1.5), cloth)
        p.box((1.3, 0.12, 0.2), (x, -D / 2 - 0.56, H + 0.5), gold)
    for i in range(6):
        p.box((1.3, 0.15, 1.3), (-8.5 + i * 3.4 if i < 3 else 8.5 - (i - 3) * 3.4, -D / 2 - 0.07, 7.6), st2, bevel=0.06)
    return p


def banner_pole(name, wood, cloth, gold):
    p = Part(name)
    p.cyl(0.08, 4.2, (0, 0, 2.1), wood, seg=8)
    p.box((1.1, 0.08, 0.08), (0.45, 0, 4.0), wood)
    p.box((0.85, 0.04, 1.8), (0.5, 0, 3.05), cloth)
    p.prism([(-0.425, 0), (0.425, 0), (0, -0.35)], 0.04, (0.5, 0, 2.15), cloth)
    p.box((0.9, 0.06, 0.12), (0.5, 0, 3.95), gold)
    p.sphere(0.13, (0, 0, 4.3), gold)
    return p


def map3():
    S1, S2, S3 = mat('sand_tile_a', '#e3b470', .85), mat('sand_tile_b', '#d4a060', .85), mat('sand_tile_c', '#ebc68e', .85)
    G, WL, WL2 = mat('sand_grout', '#b07a42', .9), mat('sandstone', '#c98d4e', .85), mat('sandstone_light', '#dca566', .85)
    DK = mat('doorway_dark', '#2a170b', 1)
    CL, GO, GO2 = mat('cloth_red', '#c0392b', .8), mat('coin_gold', '#f7c948', .3, metal=.9), mat('coin_gold_dark', '#b9831e', .35, metal=.9)
    FI, FI2 = mat('fire', '#ff7a12', .5, emit=8), mat('fire_core', '#ffd84a', .5, emit=12)
    BR = mat('bronze', '#8a5a2a', .4, metal=.7)
    LF, LF2 = mat('leaf', '#5c9e2e', .7), mat('leaf_dry', '#8aa83a', .7)
    TR, TR2 = mat('palm_bark', '#8a6a44', .9), mat('palm_bark_dark', '#6e5236', .9)
    WOOD, HOLE = mat('wood', '#6b4426', .8), mat('coin_hole', '#5a3a10', .5)
    R1, R2, R3 = mat('cliff_orange', '#c8743a', .9), mat('cliff_tan', '#dc9a55', .9), mat('cliff_red', '#a9572e', .9)
    parts = [
        stone_path('dt_path_segment', [S1, S2, S3], G, WL, wall_h=1.1, seed=21, cap=WL2),
        face_gate('dt_face_gate', WL, WL2, DK, CL, GO),
        brazier('dt_brazier', WL2, BR, FI, FI2),
        banner_pole('dt_banner_pole', WOOD, CL, GO),
        palm('dt_palm_tree_a', TR, TR2, LF, LF2, h=7, seed=3),
        palm('dt_palm_tree_b', TR, TR2, LF2, LF, h=5.5, seed=9),
        rubble('dt_sandstone_pile', [WL, WL2, S2], seed=4, kind='prop'),
        cliff('dt_cliff', [R1, R2, R3], w=10, d=8, h=18, seed=2),
        rock('dt_rock', [R1, R2], size=1.1, seed=6),
        bush('dt_desert_shrub', [LF2, LF], seed=5, size=0.8),
        stone_block('dt_obstacle_sandstone_block', WL2, G),
        beam_gate('dt_obstacle_lintel', WL, WL2, deco=CL),
        rubble('dt_obstacle_rubble', [WL, WL2], seed=8),
        coin('dt_coin', GO, GO2, GO2, 'square', dark=HOLE),
    ]
    cfg = dict(
        segment='dt_path_segment', seg_range=(-2, 7),
        world=dict(top='#4f9de0', hor='#ffe4b0', strength=1.1, sun=(5.0, '#fff0d0', (45, 0, -40))),
        ground=dict(hex='#e3b46e', z=0.0),
        repeat=[('dt_brazier', 2, [(-4.65, 5.0, 0.98, 0)]), ('dt_brazier', 2, [(4.65, 15.0, 0.98, 0)]),
                ('dt_banner_pole', 3, [(-6.2, 2.0, 0, 0), (6.2, 17, 0, 180)])],
        fixed=[('dt_face_gate', (0, 72, 0), 0, 1.0), ('dt_cliff', (-24, 60, 0), 0, 1.2), ('dt_cliff', (25, 75, 0), 40, 1.4),
               ('dt_cliff', (-30, 95, 0), 10, 1.6), ('dt_cliff', (32, 40, 0), 0, 1.0)],
        scatter=[dict(names=['dt_palm_tree_a', 'dt_palm_tree_b'], n=10, x=(7, 14), y=(-10, 64), s=(0.9, 1.2)),
                 dict(names=['dt_sandstone_pile', 'dt_rock', 'dt_desert_shrub'], n=20, x=(6, 16), y=(-10, 66), s=(0.8, 1.4))],
        obstacles=[('dt_obstacle_sandstone_block', 0, 14), ('dt_obstacle_lintel', 1, 22), ('dt_obstacle_rubble', -1, 30),
                   ('dt_obstacle_sandstone_block', 1, 42), ('dt_obstacle_lintel', 0, 50), ('dt_obstacle_rubble', -1, 56)],
        coins=[(0, 2, 7), (-1, 12, 8), (1, 30, 7), (-1, 44, 6)],
        coin_arcs=[(0, 14, 7), (1, 42, 7)],
        coin='dt_coin', surface=0.44,
    )
    return parts, cfg


# =========================================================================== MAP 4 - Snow Village (night)
def snow_house(name, wall, wood, roof, snow, win, door, chimney, w=7.0, d=6.0, floors=2, seed=0):
    p = Part(name, 'backdrop')
    H = floors * 3.0
    p.box((d, w, H), (0, 0, H / 2), wall)
    for sg in (-1, 1):
        for sy in (-1, 1):
            p.box((0.3, 0.3, H), (sg * d / 2, sy * w / 2, H / 2), wood)
    p.box((d + 0.2, w + 0.2, 0.25), (0, 0, 3.0), wood)
    rh = 3.2
    p.prism([(-d / 2 - 0.6, 0), (d / 2 + 0.6, 0), (0, rh)], w + 0.8, (0, 0, H), roof, rot=(0, 0, 0))
    p.prism([(-d / 2 - 0.7, 0.25), (d / 2 + 0.7, 0.25), (0, rh + 0.35)], w + 0.9, (0, 0, H), snow)
    p.box((0.9, 0.9, 2.5), (-d / 4, w / 4, H + 2.2), chimney)
    p.box((1.1, 1.1, 0.3), (-d / 4, w / 4, H + 3.5), snow)
    for f in range(floors):
        zc = f * 3.0 + 1.7
        for yc in (-w / 3, 0, w / 3):
            if f == 0 and yc == 0:
                p.box((0.15, 1.3, 2.3), (d / 2 + 0.03, 0, 1.15), door)
                p.box((0.4, 1.8, 0.15), (d / 2 + 0.2, 0, 2.5), snow)
                continue
            p.box((0.14, 1.3, 1.5), (d / 2 + 0.03, yc, zc), wood)
            p.box((0.18, 1.0, 1.2), (d / 2 + 0.05, yc, zc), win)
            p.box((0.5, 1.5, 0.15), (d / 2 + 0.2, yc, zc - 0.82), snow)
        for sg in (-1, 1):
            p.box((1.0, 0.18, 1.2), (0, sg * (w / 2 + 0.05), zc), win)
    p.ico(1.0, (d / 2 + 0.6, -w / 2 + 0.5, 0.2), snow, scale=(1.2, 1.6, 0.6), sub=2, smooth=True)
    return p


def street_lamp(name, metal, glass, snow=None, h=4.2):
    p = Part(name)
    p.cyl(0.25, 0.4, (0, 0, 0.2), metal, seg=10, r2=0.15)
    p.cyl(0.08, h, (0, 0, h / 2), metal, seg=8)
    p.box((0.5, 0.5, 0.1), (0, 0, h), metal)
    p.box((0.4, 0.4, 0.6), (0, 0, h + 0.35), glass)
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box((0.05, 0.05, 0.62), (sx * 0.21, sy * 0.21, h + 0.35), metal)
    p.cyl(0.42, 0.35, (0, 0, h + 0.82), metal, seg=4, r2=0.05, rot=(0, 0, 45))
    p.sphere(0.07, (0, 0, h + 1.05), metal)
    if snow:
        p.cyl(0.38, 0.12, (0, 0, h + 0.85), snow, seg=8, r2=0.15)
    return p


def snowman(name, snow, coal, carrot, scarf, hat):
    p = Part(name, 'obstacle_low')
    p.sphere(0.65, (0, 0, 0.6), snow, seg=16, rings=10)
    p.sphere(0.45, (0, 0, 1.45), snow, seg=16, rings=10)
    p.sphere(0.32, (0, 0, 2.05), snow, seg=16, rings=10)
    for x in (-0.11, 0.11):
        p.sphere(0.045, (x, -0.29, 2.12), coal, seg=8, rings=6)
    p.cyl(0.07, 0.35, (0, -0.45, 2.02), carrot, rot=(90, 0, 0), seg=8, r2=0.0)
    p.torus(0.3, 0.08, (0, 0, 1.8), scarf, seg=16, sides=6)
    p.box((0.18, 0.06, 0.5), (0.2, -0.3, 1.55), scarf, rot=(0, 15, 0))
    for z in (1.35, 1.55):
        p.sphere(0.045, (0, -0.44, z), coal, seg=8, rings=6)
    p.cyl(0.3, 0.06, (0, 0, 2.32), hat, seg=12)
    p.cyl(0.2, 0.35, (0, 0, 2.5), hat, seg=12)
    p.rod((0.4, 0, 1.5), (0.9, 0, 1.9), 0.03, coal, seg=5)
    p.rod((-0.4, 0, 1.5), (-0.9, 0, 1.8), 0.03, coal, seg=5)
    return p


def snow_fence(name, wood, snow, red):
    p = Part(name, 'obstacle_low')
    for x in (-1.05, 0, 1.05):
        p.box((0.16, 0.16, 1.15), (x, 0, 0.58), wood)
        p.cyl(0.12, 0.1, (x, 0, 1.2), snow, seg=8, r2=0.05)
    for z in (0.45, 0.85):
        for i in range(4):
            p.box((2.4 / 4, 0.1, 0.2), (-1.2 + (i + 0.5) * 0.6, -0.1, z), red if i % 2 == 0 else wood)
    p.box((2.3, 0.3, 0.1), (0, -0.05, 0.98), snow, bevel=0.04)
    p.ico(1.0, (0, 0.1, 0.0), snow, scale=(1.4, 0.6, 0.4), sub=2, smooth=True)
    return p


def tunnel_gate(name, st, st2, dark, snow):
    p = Part(name, 'landmark')
    W, H, D = 26.0, 10.5, 4.0
    arched_wall(p, W, H, D, 3.0, 5.0, st, st2, dark, depth_dark=12)
    p.box((W + 1, D + 1, 0.7), (0, 0, H + 0.35), st2, bevel=0.1)
    p.box((W + 1.4, D + 1.4, 0.6), (0, 0, H + 0.95), snow, bevel=0.25)
    p.ring(5.5, 5.7, D + 0.6, (0, 0, 3.0), snow, a0=0, a1=180, seg=16)
    r = random.Random(3)
    for k in range(30):
        x = r.uniform(-W / 2 + 0.6, W / 2 - 0.6)
        z = r.uniform(0.5, H - 0.5)
        if abs(x) < 6 and z < 8.6:
            continue
        p.box((r.uniform(0.9, 1.6), 0.12, r.uniform(0.45, 0.7)), (x, -D / 2 - 0.04, z), st2, bevel=0.03)
    for sg in (-1, 1):
        p.ico(1.0, (sg * (W / 2 - 2.5), -D / 2 - 0.8, 0.2), snow, scale=(3.0, 1.6, 1.1), sub=2, smooth=True)
    return p


def map4():
    BED, SL, RA = mat('ballast_snowy', '#7d7f95', .9), mat('sleeper', '#7a4f32', .85), mat('rail', '#b7c0cc', .3, metal=.9)
    SN, SN2 = mat('snow', '#f2f6ff', .55), mat('snow_shadow', '#d9e3f7', .6)
    WA = [mat('house_wall_a', '#a0583a', .8), mat('house_wall_b', '#5b6f8a', .8), mat('house_wall_c', '#c9a46a', .8)]
    WD, RF = mat('wood_dark', '#4a2e1c', .85), mat('roof', '#3c3232', .8)
    WIN = mat('window_warm', '#ffc05a', .4, emit=6)
    DR, CH = mat('door', '#5a321e', .8), mat('chimney_brick', '#8a4a3a', .9)
    PN, BK = mat('pine', '#1f5a3e', .8), mat('pine_bark', '#4a3020', .9)
    LM, LG = mat('lamp_metal', '#1e2026', .5, metal=.6), mat('lamp_glow', '#ffcf73', .3, emit=12)
    ST, ST2, DK = mat('tunnel_stone', '#6c6f7d', .85), mat('tunnel_stone_dark', '#555866', .85), mat('tunnel_dark', '#07070b', 1)
    TB, TS, TRF = mat('train_white', '#e8eef6', .4), mat('train_blue', '#2f6fd6', .4), mat('train_roof_snow', '#f4f8ff', .5)
    TW, TL, TU = mat('train_window', '#ffd27a', .2, emit=3), mat('train_light', '#fff6d0', .3, emit=10), mat('train_under', '#2a2d33', .7)
    RED, COAL, CAR, SCF = mat('fence_red', '#c8352b', .7), mat('coal', '#111111', .6), mat('carrot', '#ff7a1a', .6), mat('scarf', '#d8323c', .8)
    CF, CR, CE = mat('coin_ice_face', '#cfe9ff', .2, metal=.9), mat('coin_ice_rim', '#8fc6ff', .25, metal=.9), mat('coin_flake', '#ffffff', .2, emit=1.5)
    parts = [
        track_segment('snow_track_segment', BED, SL, RA, SN, side_h=0.65),
        pine('snow_pine_tree_a', BK, PN, SN, h=8, seed=1),
        pine('snow_pine_tree_b', BK, PN, SN, h=6, seed=2, tiers=3),
    ]
    for i, c in enumerate('abc'):
        parts.append(snow_house('snow_house_' + c, WA[i], WD, RF, SN, WIN, DR, CH, floors=2 if i != 1 else 3, seed=i))
    parts += [
        street_lamp('snow_street_lamp', LM, LG, snow=SN),
        tunnel_gate('snow_tunnel_gate', ST, ST2, DK, SN),
        rock('snow_pile', [SN, SN2], size=1.2, seed=4),
        train('snow_train', TB, TS, TRF, TW, TL, TU, stripe2=TS),
        ramp('snow_ramp', TU, TS, SN),
        snow_fence('snow_obstacle_fence', WD, SN, RED),
        barrier_high('snow_obstacle_high', WD, RED, SN, sign=TS),
        snowman('snow_obstacle_snowman', SN, COAL, CAR, SCF, COAL),
        coin('snow_coin', CF, CR, CE, 'snowflake'),
    ]
    cfg = dict(
        segment='snow_track_segment', seg_range=(-2, 8),
        world=dict(top='#0b1238', hor='#33478a', strength=0.6, sun=(0.9, '#9fb6ff', (60, 0, 30))),
        ground=dict(hex='#e6eeff', z=0.0),
        rows=[dict(names=['snow_house_a', 'snow_house_b', 'snow_house_c'], x=11.5, y=(-12, 72), step=9.0)],
        repeat=[('snow_street_lamp', 2, [(-6.0, 3, 0.65, 0), (6.0, 13, 0.65, 0)])],
        lamp_lights=('snow_street_lamp', (0, 0, 4.6), 250, '#ffc46b'),
        scatter=[dict(names=['snow_pine_tree_a', 'snow_pine_tree_b'], n=18, x=(17, 30), y=(-10, 80), s=(0.9, 1.4)),
                 dict(names=['snow_pile'], n=12, x=(6.5, 9), y=(-10, 75), s=(0.7, 1.2), z=0.4)],
        fixed=[('snow_tunnel_gate', (0, 82, 0), 0, 1.0), ('snow_pine_tree_a', (-10, 78, 0), 0, 1.5), ('snow_pine_tree_a', (11, 76, 0), 0, 1.6)],
        obstacles=[('snow_obstacle_fence', 0, 15), ('snow_train', 1, 30), ('snow_obstacle_snowman', -1, 24),
                   ('snow_obstacle_high', 0, 40), ('snow_train', -1, 55), ('snow_ramp', -1, 46)],
        coins=[(0, 3, 8), (-1, 10, 7), (1, 16, 6), (0, 46, 6)],
        coin_arcs=[(0, 15, 7)],
        snowfall=True,
        coin='snow_coin', surface=0.56,
    )
    return parts, cfg


# =========================================================================== MAP 5 - Neon City (night)
def neon_building(name, w, d, floors, wall, glows, dark_win, strip, sign_m, seed=0):
    p = Part(name, 'backdrop')
    r = random.Random(seed)
    H = floors * 3.0 + 0.5
    p.box((d, w, H), (0, 0, H / 2), wall)
    nwin = max(2, int(w / 1.8))
    for f in range(floors):
        zc = f * 3.0 + 1.7
        for i in range(nwin):
            yc = -w / 2 + (i + 0.5) * w / nwin
            m = r.choice(glows) if r.random() < 0.7 else dark_win
            p.box((0.14, 1.1, 1.4), (d / 2 + 0.04, yc, zc), m)
        for sg in (-1, 1):
            for xc in (-d / 4, d / 4):
                m = r.choice(glows) if r.random() < 0.6 else dark_win
                p.box((1.1, 0.14, 1.4), (xc, sg * (w / 2 + 0.04), zc), m)
    for sy in (-1, 1):
        p.box((0.12, 0.12, H), (d / 2 + 0.06, sy * (w / 2 - 0.06), H / 2), strip)
    p.box((0.12, w, 0.12), (d / 2 + 0.06, 0, H - 0.1), strip)
    sh = min(H - 4, 9)
    p.box((0.9, 1.4, sh), (d / 2 + 0.7, -w / 2 + 1.2, 3.5 + sh / 2), wall)
    p.box((0.95, 1.1, sh - 0.6), (d / 2 + 0.72, -w / 2 + 1.2, 3.5 + sh / 2), sign_m)
    for k in range(int(sh / 1.4)):
        p.box((1.0, 0.7, 0.5), (d / 2 + 0.75, -w / 2 + 1.2, 4.1 + k * 1.4), wall)
    p.box((0.3, w * 0.5, 1.2), (d / 2 + 0.3, w / 6, 3.2), r.choice(glows))
    p.cyl(0.08, 4, (0, 0, H + 2), wall, seg=6)
    p.sphere(0.2, (0, 0, H + 4), strip)
    return p


def map5():
    BED, SL, RA = mat('wet_ballast', '#251c38', .12), mat('sleeper', '#3a2a4a', .3), mat('rail_chrome', '#d8dcff', .15, metal=1)
    SD = mat('wet_sidewalk', '#2c2444', .1)
    EDGE = mat('neon_edge_cyan', '#25e6ff', .3, emit=10)
    WALLS = [mat('wall_dark_a', '#2a1d45', .6), mat('wall_dark_b', '#1d2340', .6), mat('wall_dark_c', '#3a1d3f', .6)]
    G1, G2, G3 = mat('win_warm', '#ffb35a', .3, emit=5), mat('win_cyan', '#46e8ff', .3, emit=5), mat('win_pink', '#ff4fd8', .3, emit=5)
    DW = mat('win_off', '#151020', .2)
    NP, NC, NY = mat('neon_pink', '#ff2fd0', .3, emit=14), mat('neon_cyan', '#21e3ff', .3, emit=14), mat('neon_yellow', '#ffe53b', .3, emit=12)
    TB, TS, TRF = mat('train_navy', '#1c2a5a', .35, metal=.3), mat('train_neon_stripe', '#21e3ff', .3, emit=8), mat('train_roof', '#2f3550', .5, metal=.4)
    TW, TL, TU = mat('train_window_glow', '#ffcf7a', .2, emit=5), mat('train_light', '#fff6d0', .3, emit=14), mat('train_under', '#111218', .6)
    POLE, WIRE, INS = mat('pole', '#1a1a24', .4, metal=.6), mat('wire', '#0a0a0a', .5), mat('insulator_glow', '#ff2fd0', .3, emit=6)
    LF, LF2 = mat('palm_leaf_night', '#0f3a2e', .6), mat('palm_leaf_night2', '#173f4a', .6)
    TR, TR2 = mat('palm_bark_night', '#2a2030', .8), mat('palm_bark_night2', '#3a2a40', .8)
    SKB = mat('tower_glass', '#141a3a', .15, metal=.5)
    CF, CR = mat('coin_gold', '#f7c948', .25, metal=.9), mat('coin_neon_rim', '#21e3ff', .3, emit=6)
    CE = mat('coin_bolt', '#ff2fd0', .3, emit=6)
    parts = [track_segment('neon_track_segment', BED, SL, RA, SD, edge=EDGE)]
    for i, c in enumerate('abc'):
        parts.append(neon_building('neon_building_' + c, 8, 6, 5 + i * 2, WALLS[i], [G1, G2, G3], DW, [NP, NC, NY][i],
                                   [NC, NP, NY][i], seed=i))
    parts += [
        skyscraper('neon_skyscraper', 12, 70, SKB, NC, POLE, light=NP),
        skyscraper('neon_skyscraper_pink', 9, 55, SKB, NP, POLE, light=NC),
        catenary('neon_catenary_frame', POLE, WIRE, INS, light=NP),
        palm('neon_palm_tree', TR, TR2, LF, LF2, h=7, seed=4),
        train('neon_train', TB, TS, TRF, TW, TL, TU, door=NP),
        ramp('neon_ramp', TU, NC, NP),
        barrier_low('neon_barrier_low', NP, mat('barrier_black', '#121218', .4), POLE, light=NC),
        barrier_high('neon_barrier_high', POLE, NC, mat('barrier_black2', '#121218', .4), sign=NP, light=NY),
        coin('neon_coin', CF, CR, CE, 'bolt'),
    ]
    cfg = dict(
        segment='neon_track_segment', seg_range=(-2, 22), repeat_min_y=8,
        world=dict(top='#12072e', hor='#5a1d7a', strength=0.7, haze=0.006, sun=(0.6, '#b49cff', (60, 0, 20))),
        ground=dict(hex='#1a1430', z=-0.02, rough=0.15),
        rows=[dict(names=['neon_building_a', 'neon_building_b', 'neon_building_c'], x=10.4, y=(-15, 220), step=8.2)],
        repeat=[('neon_catenary_frame', 2, [(0, 0, 0, 0)])],
        scatter=[dict(names=['neon_palm_tree'], n=10, x=(6.2, 6.8), y=(-5, 150), s=(0.9, 1.1), z=0.5)],
        fixed=[('neon_skyscraper', (-28, 240, 0), 0, 1.0), ('neon_skyscraper_pink', (20, 260, 0), 0, 1.3),
               ('neon_skyscraper', (2, 320, 0), 0, 1.6), ('neon_skyscraper_pink', (-45, 300, 0), 0, 1.5)],
        lights=[('POINT', (-5, 10, 4), 600, '#ff3fd5'), ('POINT', (5, 25, 4), 600, '#2fe0ff'), ('POINT', (-5, 45, 4), 600, '#2fe0ff'),
                ('POINT', (5, 60, 4), 600, '#ff3fd5'), ('POINT', (0, -4, 6), 400, '#ffd9a0')],
        obstacles=[('neon_train', 1, 40), ('neon_train', -1, 28), ('neon_barrier_low', 0, 16), ('neon_barrier_high', 1, 22),
                   ('neon_ramp', -1, 18.5), ('neon_barrier_low', 0, 50)],
        coins=[(0, 3, 8), (1, 12, 6), (0, 30, 10)],
        coin_arcs=[(0, 16, 7), (0, 50, 7)],
        coins_raised=[(-1, 23, 10, 4.1)],
        coin='neon_coin', surface=0.56,
    )
    return parts, cfg


# =========================================================================== MAP 6 - Jungle River
def plank_bridge(name, planks, beam, post, rope, seed=6):
    p = Part(name, 'segment')
    r = random.Random(seed)
    W = 8.4
    for x in (-3.0, 0, 3.0):
        p.box((0.35, SEG, 0.4), (x, SEG / 2, -0.05), beam)
    n = 17
    for i in range(n):
        y = (i + 0.5) * SEG / n
        p.box((W + r.uniform(-0.2, 0.3), SEG / n - 0.08, 0.14), (r.uniform(-0.1, 0.1), y, 0.25 + r.uniform(-0.02, 0.02)),
              r.choice(planks), rot=(0, r.uniform(-1, 1), r.uniform(-1.2, 1.2)), bevel=0.02)
    for sg in (-1, 1):
        x = sg * (W / 2 + 0.2)
        for py in (0.3, SEG / 2 + 0.3):
            p.cyl(0.22, 2.6, (x, py, 0.9), post, seg=8)
            p.cyl(0.25, 0.12, (x, py, 2.2), beam, seg=8)
            p.torus(0.24, 0.05, (x, py, 1.6), rope, seg=10, sides=5)
            p.torus(0.24, 0.05, (x, py, 1.0), rope, seg=10, sides=5)
        for z in (1.0, 1.6):
            for (a, b) in ((0.3, SEG / 2 + 0.3), (SEG / 2 + 0.3, SEG + 0.3)):
                k = 4
                pts = [(x, a + (b - a) * t / k, z - 0.25 * math.sin(math.pi * t / k)) for t in range(k + 1)]
                for i in range(k):
                    p.rod(pts[i], pts[i + 1], 0.05, rope, seg=5)
        for i in range(10):
            yy = (i + 0.5) * SEG / 10
            p.rod((x, yy, 0.3), (x, yy, 1.0 - 0.25 * math.sin(math.pi * ((yy - 0.3) % (SEG / 2)) / (SEG / 2))), 0.025, rope, seg=4)
    return p


def bank(name, earth, grass, seed=0, L=24, w=9):
    p = Part(name, 'backdrop')
    r = random.Random(seed)
    p.box((w, L, 2.4), (0, 0, -0.9), earth, bevel=0.3, jitter=0.1, seed=seed)
    p.box((w + 0.2, L + 0.2, 0.3), (0, 0, 0.35), grass, bevel=0.1, jitter=0.05, seed=seed + 1)
    for i in range(6):
        p.ico(r.uniform(0.6, 1.0), (-w / 2 + r.uniform(0, 0.5), r.uniform(-L / 2, L / 2), -0.8), earth, sub=1, jitter=0.2, seed=seed + i)
    return p


def ruin_gate(name, st, st2, moss, dark):
    p = Part(name, 'backdrop')
    for x in (-2.2, 2.2):
        p.box((1.2, 1.4, 5), (x, 0, 2.5), st, bevel=0.1)
    p.box((6, 1.6, 1.2), (0, 0, 5.6), st2, bevel=0.1)
    p.box((3.2, 1.0, 4.4), (0, 0.4, 2.2), dark)
    p.box((5.0, 1.3, 0.8), (0, 0, 6.6), st, bevel=0.1)
    p.box((4.0, 1.2, 0.15), (0.3, 0, 7.05), moss)
    p.box((0.2, 0.1, 2.5), (-1.8, -0.75, 4.5), moss)
    return p


def crates(name, wood, wood2, metal):
    p = Part(name, 'obstacle_low')
    for (x, z, s, rz) in ((-0.55, 0.5, 1.0, 5), (0.6, 0.45, 0.9, -8), (0.0, 1.35, 0.8, 15)):
        p.box((s, s, s), (x, 0, z), wood, rot=(0, 0, rz), bevel=0.04)
        pre = M((x, 0, z), (0, 0, rz))
        p.box((s + 0.02, 0.12, s * 0.15), (0, -s / 2, 0), wood2, pre=pre)
        p.box((s * 0.12, s + 0.02, s + 0.02), (-s / 2 + 0.08, 0, 0), wood2, pre=pre)
        p.box((s * 0.12, s + 0.02, s + 0.02), (s / 2 - 0.08, 0, 0), wood2, pre=pre)
    return p


def hanging_log(name, wood, bark, rope, vine):
    p = Part(name, 'obstacle_high')
    for x in (-1.25, 1.25):
        p.cyl(0.2, 3.2, (x, 0, 1.6), wood, seg=8)
    p.rod((-1.5, 0, 3.0), (1.5, 0, 3.0), 0.16, wood, seg=8)
    p.cyl(0.38, 2.6, (0, 0, 1.95), bark, rot=(0, 90, 0), seg=10, jitter=0.02)
    for x in (-0.8, 0.8):
        p.rod((x, 0, 2.3), (x, 0, 2.95), 0.04, rope, seg=5)
    for x in (-0.5, 0.2, 0.7):
        p.box((0.12, 0.06, 0.5), (x, -0.35, 1.45), vine)
    return p


def map6():
    PL = [mat('plank_a', '#a8794a', .85), mat('plank_b', '#946638', .85), mat('plank_c', '#b8885a', .85)]
    BM, PO, RP = mat('beam_dark', '#5a3b20', .9), mat('post_wood', '#7a5530', .85), mat('rope', '#c9a86a', .9)
    WAT = mat('river_water', '#2fd3d0', .05, metal=.1)
    EA, GR = mat('earth', '#6b4a2e', .95), mat('grass', '#4fa832', .8)
    LF, LF2, LF3 = mat('leaf', '#3f8f2a', .7), mat('leaf_light', '#5aad34', .7), mat('leaf_dark', '#2e6e22', .7)
    TR, TR2 = mat('bark', '#6b4a2b', .9), mat('bark_dark', '#563a20', .9)
    S1, S2, MO = mat('stone', '#8f8d7a', .85), mat('stone_dark', '#74725f', .85), mat('moss', '#5f9a2c', .8)
    DK = mat('ruin_dark', '#14140f', 1)
    WF, FO = mat('waterfall', '#9fe9ff', .1, emit=.8), mat('foam', '#ffffff', .4, emit=.6)
    MET, RING = mat('metal', '#55524a', .5, metal=.7), mat('log_ring', '#c99a5e', .8)
    GO, GO2, GL = mat('coin_gold', '#f7c948', .3, metal=.9), mat('coin_gold_dark', '#c98f22', .35, metal=.9), mat('coin_leaf', '#46c23a', .4, metal=.3)
    parts = [
        plank_bridge('jr_bridge_segment', PL, BM, PO, RP),
        bank('jr_river_bank', EA, GR),
        round_tree('jr_jungle_tree_a', TR, [LF, LF2, LF3], h=7, rad=3.0, seed=1),
        round_tree('jr_jungle_tree_b', TR2, [LF3, LF], h=9, rad=2.4, seed=2, blobs=5),
        palm('jr_palm_tree', TR, TR2, LF2, LF, h=7, seed=7),
        waterfall('jr_waterfall', [S1, S2], WF, FO, h=20, w=5, top=[LF, LF2, LF3], seed=8),
        cliff('jr_cliff', [S2, S1, EA], w=10, d=8, h=16, seed=3, top=[LF, LF2, LF3]),
        ruin_gate('jr_ruin_gate', S1, S2, MO, DK),
        rock('jr_rock_mossy', [S1, S2], size=1.2, seed=9, moss=MO),
        bush('jr_fern', [LF, LF2, LF3], seed=3, size=1.3),
        log('jr_obstacle_log', TR, RING, moss=MO),
        crates('jr_obstacle_crates', PL[1], BM, MET),
        hanging_log('jr_obstacle_hanging_log', PO, TR, RP, LF),
        coin('jr_coin', GO, GO2, GL, 'leaf'),
    ]
    cfg = dict(
        segment='jr_bridge_segment', seg_range=(-2, 16),
        world=dict(top='#3d8fe0', hor='#d2f0ff', strength=1.0, sun=(4.0, '#fff1d6', (50, 0, -35))),
        ground=dict(hex='#22c3c4', z=-1.4, rough=0.05, name='river_water'),
        rows=[dict(names=['jr_river_bank'], x=14, y=(-20, 160), step=24, fixed_rz=True)],
        scatter=[dict(names=['jr_jungle_tree_a', 'jr_jungle_tree_b', 'jr_palm_tree'], n=16, x=(11, 18), y=(-10, 140), s=(0.9, 1.3), z=0.5),
                 dict(names=['jr_fern', 'jr_rock_mossy'], n=18, x=(10, 18), y=(-10, 140), s=(0.8, 1.3), z=0.5),
                 dict(names=['jr_rock_mossy'], n=8, x=(5.5, 9), y=(0, 120), s=(0.6, 1.0), z=-1.6)],
        fixed=[('jr_waterfall', (14, 95, -1.4), -15, 1.2), ('jr_waterfall', (-30, 140, -1.4), 10, 1.5), ('jr_cliff', (-24, 80, -1.4), 0, 1.4),
               ('jr_cliff', (26, 140, -1.4), 0, 1.6), ('jr_ruin_gate', (-14, 60, 0.5), 80, 1.3), ('jr_cliff', (-10, 170, -1.4), 0, 2.0)],
        obstacles=[('jr_obstacle_log', 0, 14), ('jr_obstacle_crates', 1, 22), ('jr_obstacle_hanging_log', -1, 30),
                   ('jr_obstacle_log', 1, 40), ('jr_obstacle_crates', -1, 48), ('jr_obstacle_hanging_log', 0, 58)],
        coins=[(0, 2, 7), (-1, 12, 8), (1, 28, 8), (0, 40, 8)],
        coin_arcs=[(0, 14, 7), (1, 40, 7)],
        coin='jr_coin', surface=0.32,
    )
    return parts, cfg


# =========================================================================== MAP 7 - Canyon Sunset
def mesa(name, mats, w=10, h=24, seed=0, kind='backdrop'):
    p = Part(name, kind)
    r = random.Random(seed)
    n = int(h / 2.2)
    z = 0
    for i in range(n):
        lh = h / n
        f = 1 - 0.25 * i / n
        p.cyl(w / 2 * f * r.uniform(0.92, 1.05), lh * 1.02, (r.uniform(-0.3, 0.3), r.uniform(-0.3, 0.3), z + lh / 2),
              mats[i % len(mats)], seg=7, jitter=w * 0.025, seed=seed + i)
        z += lh
    p.cyl(w / 2 * 0.78, 0.6, (0, 0, h + 0.3), mats[0], seg=7, r2=w / 2 * 0.7, jitter=0.15, seed=seed + 99)
    return p


def trestle(name, wood, wood2, rail, L=30, H=14):
    p = Part(name, 'backdrop')
    p.box((3.2, L, 0.5), (0, 0, H), wood, bevel=0.05)
    for i in range(int(L / 0.8)):
        p.box((3.4, 0.25, 0.15), (0, -L / 2 + i * 0.8 + 0.4, H + 0.32), wood2)
    for x in (-0.6, 0.6):
        p.box((0.12, L, 0.15), (x, 0, H + 0.45), rail)
    for y in range(int(-L / 2) + 2, int(L / 2), 5):
        for x in (-1.4, 1.4):
            p.box((0.35, 0.35, H), (x, y, H / 2), wood)
        p.rod((-1.4, y, 0.5), (1.4, y, H - 0.5), 0.12, wood2, seg=6)
        p.rod((1.4, y, 0.5), (-1.4, y, H - 0.5), 0.12, wood2, seg=6)
        p.box((3.2, 0.3, 0.3), (0, y, H / 2), wood)
    return p


def cactus(name, green, green2, flower=None):
    p = Part(name)
    p.cyl(0.35, 3.2, (0, 0, 1.6), green, seg=10, smooth=True)
    p.sphere(0.35, (0, 0, 3.2), green, seg=10, rings=6)
    for sg, z, hh in ((-1, 1.4, 1.2), (1, 1.9, 0.9)):
        p.rod((0, 0, z), (sg * 0.9, 0, z), 0.22, green2, seg=8, smooth=True)
        p.cyl(0.22, hh, (sg * 0.9, 0, z + hh / 2), green2, seg=8, smooth=True)
        p.sphere(0.22, (sg * 0.9, 0, z + hh), green2, seg=8, rings=6)
    if flower:
        p.sphere(0.14, (0, -0.1, 3.5), flower, seg=8, rings=6)
    return p


def mine_cart(name, metal, wood, ore, under):
    p = Part(name, 'obstacle_low')
    p.cyl(1.25, 1.0, (0, 0, 0.95), metal, seg=4, r2=1.0, rot=(0, 0, 45), scale=(1.15, 0.75, 1))
    p.box((2.0, 1.25, 0.08), (0, 0, 1.47), wood)
    for x in (-0.7, 0.7):
        for y in (-0.55, 0.55):
            p.cyl(0.25, 0.12, (x, y * 1.05, 0.28), under, rot=(90, 0, 0), seg=12)
    r = random.Random(2)
    for i in range(9):
        p.ico(0.22, (r.uniform(-0.6, 0.6), r.uniform(-0.3, 0.3), 1.55), ore, sub=1, jitter=0.2, seed=i)
    return p


def map7():
    BED, SL, RA = mat('red_dirt', '#8a452a', .95), mat('sleeper', '#4e3220', .9), mat('rail', '#a9a9b0', .3, metal=.9)
    SIDE = mat('canyon_ground', '#a95a36', .95)
    R1, R2, R3, R4 = mat('rock_red', '#a5482a', .9), mat('rock_orange', '#c8673a', .9), mat('rock_dark', '#7c3420', .9), mat('rock_sand', '#dd8a52', .9)
    W1, W2 = mat('timber', '#6b4426', .85), mat('timber_dark', '#4a2e18', .85)
    SUN = mat('sun_disc', '#ffd27a', .5, emit=8)
    TB, TS, TRF = mat('train_red', '#b8322a', .45), mat('train_cream', '#f2e2c0', .5), mat('train_roof', '#5a5a60', .5, metal=.4)
    TW, TL, TU = mat('train_window', '#2a1e2a', .1), mat('train_light', '#fff2c0', .3, emit=8), mat('train_under', '#2a2a2e', .7)
    CG, CG2, CFL = mat('cactus', '#4f8a3a', .7), mat('cactus_dark', '#3f7430', .7), mat('cactus_flower', '#ff5a8a', .6)
    MT, ORE = mat('cart_metal', '#5a5a62', .45, metal=.7), mat('gold_ore', '#ffcf3a', .3, metal=.9)
    BW, BRD = mat('barrier_white', '#f0e6d8', .6), mat('barrier_red', '#c8352b', .6)
    GO, GO2 = mat('coin_gold', '#f7c948', .3, metal=.9), mat('coin_gold_dark', '#d0731e', .35, metal=.9)
    parts = [
        track_segment('cn_track_segment', BED, SL, RA, SIDE),
        mesa('cn_mesa_a', [R1, R2, R3, R4], w=14, h=28, seed=1),
        mesa('cn_mesa_b', [R2, R4, R1], w=9, h=18, seed=2),
        mesa('cn_rock_pillar', [R1, R3, R2], w=4, h=16, seed=3),
        cliff('cn_cliff_wall', [R1, R2, R3, R4], w=12, d=10, h=22, seed=4, shrink=0.15, layer=2.2),
        trestle('cn_trestle_bridge', W1, W2, RA),
        cactus('cn_cactus', CG, CG2, CFL),
        rock('cn_rock', [R1, R2, R3], size=1.3, seed=5),
        Part('cn_sun_disc', 'backdrop'),
        train('cn_train', TB, TS, TRF, TW, TL, TU, stripe2=TS),
        ramp('cn_ramp', W2, BRD, BW),
        mine_cart('cn_obstacle_mine_cart', MT, W1, ORE, TU),
        barrier_high('cn_obstacle_wood_high', W2, W1, BRD, sign=BW),
        rubble('cn_obstacle_rocks', [R1, R2, R3], seed=7),
        coin('cn_coin', GO, GO2, GO2, 'sun'),
    ]
    sun = next(p for p in parts if p.name == 'cn_sun_disc')
    sun.cyl(12, 0.5, (0, 0, 0), SUN, rot=(90, 0, 0), seg=32)
    cfg = dict(
        segment='cn_track_segment', seg_range=(-2, 22),
        world=dict(top='#40306e', hor='#ff8a4a', strength=1.0, haze=0.004, clouds=True, sun=(3.5, '#ffb070', (78, 0, 180))),
        ground=dict(hex='#b05d36', z=-0.02),
        scatter=[dict(names=['cn_cactus', 'cn_rock'], n=18, x=(6, 14), y=(-10, 150), s=(0.8, 1.3)),
                 dict(names=['cn_rock_pillar', 'cn_mesa_b'], n=8, x=(20, 45), y=(20, 200), s=(0.8, 1.4))],
        rows=[dict(names=['cn_cliff_wall'], x=14, y=(-15, 220), step=11, sides=(1,))],
        fixed=[('cn_mesa_a', (-40, 160, 0), 0, 1.4), ('cn_mesa_a', (-20, 260, 0), 30, 2.0), ('cn_mesa_b', (-60, 220, 0), 0, 1.6),
               ('cn_trestle_bridge', (-18, 110, -12), 90, 1.0), ('cn_sun_disc', (-30, 400, 25), 0, 1.0),
               ('cn_mesa_a', (40, 300, 0), 0, 2.2)],
        obstacles=[('cn_train', 1, 30), ('cn_ramp', 1, 21), ('cn_obstacle_mine_cart', 0, 15), ('cn_obstacle_wood_high', -1, 25),
                   ('cn_obstacle_rocks', 0, 40), ('cn_train', -1, 55)],
        coins=[(0, 3, 6), (-1, 10, 6), (0, 25, 8)],
        coin_arcs=[(0, 15, 7), (0, 40, 7)],
        coins_raised=[(1, 25.5, 10, 4.1)],
        coin='cn_coin', surface=0.56,
    )
    return parts, cfg


# =========================================================================== MAP 8 - Cherry Blossom
def cherry_tree(name, bark, pinks, seed=0, h=5.5):
    p = Part(name)
    r = random.Random(seed)
    p.cyl(0.4, h * 0.55, (0, 0, h * 0.27), bark, seg=8, r2=0.28, jitter=0.03, seed=seed)
    ends = []
    for k in range(4):
        a = math.radians(k * 90 + r.uniform(-25, 25))
        e = (2.0 * math.cos(a), 2.0 * math.sin(a), h * r.uniform(0.75, 0.95))
        p.rod((0, 0, h * 0.5), e, 0.2, bark, seg=6, r2=0.08)
        ends.append(e)
    for k, e in enumerate(ends):
        p.canopy((e[0], e[1], e[2] + 0.5), 1.7, pinks, seed=seed + 13 * k, blobs=3, flat=0.8, cards=30, card_size=0.35)
    p.canopy((0, 0, h + 0.6), 2.0, pinks, seed=seed + 77, blobs=3, flat=0.75, cards=30, card_size=0.35)
    return p


def stone_lantern(name, st, st2, glow):
    p = Part(name)
    p.box((1.0, 1.0, 0.3), (0, 0, 0.15), st2, bevel=0.05)
    p.cyl(0.4, 0.25, (0, 0, 0.42), st, seg=8, r2=0.3)
    p.cyl(0.18, 1.2, (0, 0, 1.15), st, seg=8)
    p.box((0.9, 0.9, 0.18), (0, 0, 1.8), st2, bevel=0.04)
    p.box((0.62, 0.62, 0.62), (0, 0, 2.2), st, bevel=0.03)
    p.box((0.66, 0.4, 0.36), (0, 0, 2.2), glow)
    p.box((0.4, 0.66, 0.36), (0, 0, 2.2), glow)
    p.cyl(0.85, 0.5, (0, 0, 2.75), st2, seg=4, r2=0.12, rot=(0, 0, 45))
    p.sphere(0.14, (0, 0, 3.1), st)
    return p


def pagoda(name, wall, roof, trim, gold, base_m):
    p = Part(name, 'landmark')
    p.box((10, 10, 1.2), (0, 0, 0.6), base_m, bevel=0.1)
    z = 1.2
    w = 7.0
    for i in range(4):
        h = 3.2 - i * 0.4
        p.box((w, w, h), (0, 0, z + h / 2), wall)
        for sx in (-1, 1):
            for sy in (-1, 1):
                p.cyl(0.18, h, (sx * w / 2, sy * w / 2, z + h / 2), trim, seg=8)
        p.box((w * 0.35, 0.1, h * 0.6), (0, -w / 2 - 0.05, z + h * 0.45), mat('pagoda_door', '#3a1c14', .8))
        z += h
        rw = w * 0.85 + 2.4
        p.cyl(rw, 1.1, (0, 0, z + 0.4), roof, seg=4, r2=w * 0.42, rot=(0, 0, 45))
        p.box((w * 1.15, w * 1.15, 0.2), (0, 0, z - 0.05), trim)
        for a in range(4):
            ang = math.radians(45 + 90 * a)
            cx, cy = rw * 0.98 * math.cos(ang), rw * 0.98 * math.sin(ang)
            p.cyl(0.12, 0.6, (cx, cy, z + 0.2), gold, seg=6, r2=0.02)
        z += 0.95
        w *= 0.78
    for i in range(5):
        p.torus(0.35, 0.08, (0, 0, z + 0.4 + i * 0.4), gold, seg=12, sides=6)
    p.cyl(0.08, 3, (0, 0, z + 1.5), gold, seg=6)
    p.sphere(0.25, (0, 0, z + 3.1), gold)
    return p


def torii(name, red, black, w=2.6, h=3.2, kind='obstacle_high', nuki=1.55):
    p = Part(name, kind)
    for x in (-w / 2, w / 2):
        p.cyl(0.14 * w / 2.6 + 0.04, h, (x, 0, h / 2), red, seg=12)
        p.cyl(0.24 * w / 2.6, 0.25, (x, 0, 0.12), black, seg=12)
    p.box((w + 0.4, 0.3, 0.28), (0, 0, nuki + 0.14), red)
    p.box((w + 1.2, 0.42, 0.3), (0, 0, h + 0.05), red, bevel=0.03)
    p.box((w + 1.5, 0.5, 0.18), (0, 0, h + 0.28), black, bevel=0.03)
    p.box((0.25, 0.25, h - nuki - 0.3), (0, 0, (h + nuki + 0.28) / 2), red)
    return p


def low_wall(name, st, st2, petals=None):
    p = Part(name, 'obstacle_low')
    p.box((2.4, 0.8, 0.85), (0, 0, 0.425), st, bevel=0.06)
    p.box((2.6, 1.0, 0.18), (0, 0, 0.94), st2, bevel=0.05)
    for x in (-0.8, 0, 0.8):
        p.box((0.5, 0.06, 0.4), (x, -0.42, 0.45), st2, bevel=0.02)
    if petals:
        r = random.Random(3)
        for i in range(12):
            p.box((0.13, 0.08, 0.01), (r.uniform(-1.2, 1.2), r.uniform(-0.45, 0.45), 1.035), petals, rot=(0, 0, r.uniform(0, 180)))
    return p


def map8():
    S1, S2, S3 = mat('path_stone_a', '#cbc4ba', .85), mat('path_stone_b', '#b8b0a6', .85), mat('path_stone_c', '#d8d1c6', .85)
    G, WL = mat('grout', '#8a8478', .9), mat('wall_stone', '#a39b8f', .85)
    MO = mat('moss', '#7aa84a', .8)
    P1, P2, P3 = mat('blossom_pink', '#ffa6cf', .7), mat('blossom_light', '#ffc9e3', .7), mat('blossom_deep', '#f27bb4', .7)
    BK = mat('cherry_bark', '#4a2e2a', .9)
    GLOW = mat('lantern_glow', '#ffd27a', .4, emit=6)
    PW, PR, PT, PG = mat('pagoda_wall', '#c8392f', .7), mat('pagoda_roof', '#3b4552', .6), mat('pagoda_trim', '#2a1c18', .7), mat('gold', '#f2c14e', .3, metal=.9)
    TRD, TBK = mat('torii_red', '#e0372b', .6), mat('torii_black', '#1c1c1c', .6)
    GR, GR2 = mat('grass', '#7fb85a', .85), mat('hedge', '#5f9a44', .85)
    CF, CR, CE = mat('coin_gold', '#f7c948', .3, metal=.9), mat('coin_rose_rim', '#e86aa6', .3, metal=.6), mat('coin_blossom', '#ff8cc6', .4, metal=.2)
    parts = [
        stone_path('ch_path_segment', [S1, S2, S3], G, WL, moss=MO, wall_h=0.9, seed=31, petals=[P1, P2, P3]),
        cherry_tree('ch_cherry_tree_a', BK, [P1, P2, P3], seed=1),
        cherry_tree('ch_cherry_tree_b', BK, [P2, P1], seed=2, h=4.5),
        stone_lantern('ch_stone_lantern', S2, G, GLOW),
        pagoda('ch_pagoda', PW, PR, PT, PG, WL),
        torii('ch_torii_gate', TRD, TBK, w=9.5, h=8.0, kind='landmark', nuki=6.2),
        blob_bush('ch_azalea_bush', [GR2, GR], seed=3, size=1.1, flower=P3),
        rock('ch_garden_rock', [S2, WL], size=0.9, seed=4, moss=MO),
        low_wall('ch_obstacle_stone_wall', WL, S1, petals=P1),
        torii('ch_obstacle_torii', TRD, TBK),
        stone_block('ch_obstacle_stone_block', S2, G, moss=MO, size=(2.3, 1.2, 1.0)),
        coin('ch_coin', CF, CR, CE, 'flower', dark=PG),
    ]
    cfg = dict(
        segment='ch_path_segment', seg_range=(-2, 14),
        world=dict(top='#6fb4ff', hor='#ffd9ee', strength=1.1, sun=(2.8, '#fff0f4', (50, 0, 30))),
        ground=dict(hex='#82b85c', z=0.0),
        repeat=[('ch_stone_lantern', 2, [(-4.65, 1.67, 0.3, 0), (4.65, 11.67, 0.3, 0)])],
        lamp_lights=('ch_stone_lantern', (0, 0, 2.6), 40, '#ffc46b'),
        scatter=[dict(names=['ch_cherry_tree_a', 'ch_cherry_tree_b'], n=18, x=(7, 15), y=(-10, 130), s=(0.9, 1.3)),
                 dict(names=['ch_azalea_bush', 'ch_garden_rock'], n=20, x=(5.8, 13), y=(-10, 130), s=(0.8, 1.2))],
        fixed=[('ch_pagoda', (0, 150, 0), 0, 1.6), ('ch_torii_gate', (0, 70, 0.3), 0, 1.0), ('ch_torii_gate', (0, 110, 0.3), 0, 1.0),
               ('ch_cherry_tree_a', (-8, 145, 0), 0, 1.6), ('ch_cherry_tree_a', (9, 140, 0), 60, 1.5)],
        obstacles=[('ch_obstacle_stone_wall', 0, 14), ('ch_obstacle_torii', 1, 22), ('ch_obstacle_stone_block', -1, 30),
                   ('ch_obstacle_torii', 0, 42), ('ch_obstacle_stone_wall', 1, 50)],
        coins=[(0, 3, 7), (-1, 12, 8), (1, 28, 7), (0, 50, 6)],
        coin_arcs=[(0, 14, 7), (1, 50, 7)],
        coin='ch_coin', surface=0.44,
    )
    return parts, cfg


# =========================================================================== MAP 9 - Underwater Tunnel
def glass_tunnel(name, frame, glass, base):
    p = Part(name, 'segment')
    R = 6.4
    for y in (0.2, SEG / 2 + 0.2):
        p.ring(R, R + 0.35, 0.45, (0, y, 0.5), frame, a0=0, a1=180, seg=24)
        for sg in (-1, 1):
            p.box((0.8, 0.8, 0.9), (sg * (R + 0.18), y, 0.45), frame)
    p.ring(R + 0.08, R + 0.14, SEG, (0, SEG / 2, 0.5), glass, a0=0, a1=180, seg=24)
    for sg in (-1, 1):
        p.box((1.2, SEG, 1.0), (sg * (R + 0.2), SEG / 2, 0.0), base)
    for a in (35, 90, 145):
        ang = math.radians(a)
        p.rod(((R + 0.12) * math.cos(ang), 0, 0.5 + (R + 0.12) * math.sin(ang)),
              ((R + 0.12) * math.cos(ang), SEG, 0.5 + (R + 0.12) * math.sin(ang)), 0.07, frame, seg=6)
    return p


def coral_branch(name, mats, seed=0):
    p = Part(name)
    r = random.Random(seed)
    p.ico(0.6, (0, 0, 0.2), mats[0], scale=(1, 1, 0.5), sub=1, jitter=0.2, seed=seed)
    for i in range(7):
        a = math.radians(i * 51 + r.uniform(-15, 15))
        m = r.choice(mats)
        tip = (0.9 * math.cos(a) * r.uniform(0.4, 1), 0.9 * math.sin(a) * r.uniform(0.4, 1), r.uniform(1.2, 2.4))
        p.rod((0, 0, 0.3), tip, 0.13, m, seg=6, r2=0.09)
        p.sphere(0.14, tip, m, seg=8, rings=6)
        mid = (tip[0] * 0.6, tip[1] * 0.6, tip[2] * 0.6)
        t2 = (mid[0] * 1.6 + r.uniform(-0.3, 0.3), mid[1] * 1.6 + r.uniform(-0.3, 0.3), mid[2] + r.uniform(0.4, 0.8))
        p.rod(mid, t2, 0.08, m, seg=6, r2=0.06)
        p.sphere(0.09, t2, m, seg=8, rings=6)
    return p


def coral_fan(name, m, m2, seed=0):
    p = Part(name)
    r = random.Random(seed)
    p.ico(0.5, (0, 0, 0.15), m2, scale=(1, 1, 0.5), sub=1, jitter=0.2, seed=seed)
    p.ico(1.0, (0, 0, 1.4), m, scale=(1.3, 0.12, 1.2), sub=2, jitter=0.12, seed=seed + 1)
    for i in range(4):
        p.ico(0.6, (r.uniform(-1.2, 1.2), r.uniform(-0.6, 0.6), 0.4), m2, sub=2, smooth=True, scale=(1, 1, 0.7))
    return p


def seaweed(name, m, m2, seed=0):
    p = Part(name)
    r = random.Random(seed)
    for k in range(5):
        bx, by = r.uniform(-0.6, 0.6), r.uniform(-0.6, 0.6)
        h = r.uniform(2, 4)
        n = 8
        pts = [(bx + 0.25 * math.sin(i * 0.9 + k), by + 0.2 * math.cos(i * 0.7 + k), h * i / n) for i in range(n + 1)]
        for i in range(n):
            p.rod(pts[i], pts[i + 1], 0.09 * (1 - i / n) + 0.03, m if k % 2 else m2, seg=5)
    return p


def shark(name, body, belly, eye):
    p = Part(name)
    p.sphere(1.0, (0, 0, 0), body, scale=(0.75, 2.6, 0.8), seg=16, rings=10)
    p.sphere(1.0, (0, 0.2, -0.25), belly, scale=(0.6, 2.2, 0.55), seg=16, rings=10)
    p.prism([(-0.6, 0), (0.6, 0), (-0.4, 1.2)], 0.12, (0, 0.1, 0.65), body, rot=(0, 0, 90))
    p.prism([(0, 0), (-1.0, 1.1), (-0.6, 0), (-1.0, -0.8)], 0.12, (0, -2.4, 0), body, rot=(0, 0, 90))
    for sg in (-1, 1):
        p.box((1.3, 0.6, 0.08), (sg * 0.9, 0.5, -0.35), body, rot=(0, sg * 20, sg * 25))
        p.sphere(0.09, (sg * 0.45, 1.9, 0.2), eye, seg=8, rings=6)
    return p


def fish_school(name, mats, seed=0):
    p = Part(name)
    r = random.Random(seed)
    for i in range(10):
        c = (r.uniform(-2, 2), r.uniform(-1.5, 1.5), r.uniform(-1, 1))
        m = mats[i % len(mats)]
        p.sphere(0.25, c, m, scale=(0.5, 1.0, 0.75), seg=10, rings=6)
        p.prism([(0, 0), (-0.22, 0.2), (-0.22, -0.2)], 0.04, (c[0], c[1] - 0.2, c[2]), m, rot=(0, 0, 90))
    return p


def chest(name, wood, gold, dark):
    p = Part(name, 'obstacle_low')
    p.box((2.1, 1.2, 0.8), (0, 0, 0.4), wood, bevel=0.04)
    p.cyl(0.6, 2.1, (0, 0, 0.8), wood, rot=(0, 90, 0), seg=14)
    p.box((2.16, 1.26, 0.06), (0, 0, 0.8), gold)
    for x in (-0.75, 0.75):
        p.box((0.14, 1.24, 0.82), (x, 0, 0.4), gold)
        p.ring(0.58, 0.64, 0.14, (x, 0, 0.8), gold, rot=(0, 0, 90), a0=0, a1=180, seg=10)
    p.box((0.28, 0.08, 0.35), (0, -0.62, 0.75), gold)
    p.box((0.08, 0.1, 0.1), (0, -0.66, 0.7), dark)
    for i in range(5):
        p.cyl(0.12, 0.03, (-0.5 + i * 0.25, 0.4, 1.42), gold, seg=10, rot=(10, 0, 0))
    return p


def map9():
    BED, SL, RA = mat('tunnel_floor', '#1f5a8c', .4), mat('sleeper_blue', '#2c6fa3', .5), mat('rail', '#c6d6e6', .25, metal=.9)
    SD = mat('tunnel_side', '#245f86', .5)
    FR, GLS, BASE = mat('tunnel_frame', '#2b4a66', .3, metal=.7), mat('tunnel_glass', '#a8e6ff', .05, alpha=.18), mat('tunnel_base', '#1c3c58', .5, metal=.4)
    C1, C2, C3, C4 = (mat('coral_orange', '#ff8a3a', .6, emit=.6), mat('coral_pink', '#ff4f9a', .6, emit=.6),
                      mat('coral_purple', '#a35cff', .6, emit=.6), mat('coral_yellow', '#ffd23a', .6, emit=.5))
    SW1, SW2 = mat('seaweed', '#2fbf6a', .7), mat('seaweed_dark', '#1f8f50', .7)
    SB, SBL, EYE = mat('shark_grey', '#5f7d96', .5), mat('shark_belly', '#dfe9f0', .5), mat('eye', '#0a0a0a', .3)
    F1, F2, F3 = mat('fish_yellow', '#ffd23a', .5), mat('fish_orange', '#ff7a2a', .5), mat('fish_blue', '#3ac8ff', .5)
    RK, RK2, SAND = mat('sea_rock', '#355a72', .9), mat('sea_rock_dark', '#27475c', .9), mat('sea_sand', '#c9b88a', .9)
    TB, TS, TRF = mat('train_red', '#b8322a', .45), mat('train_cream', '#f2e2c0', .5), mat('train_roof', '#5a5a60', .5, metal=.4)
    TW, TL, TU = mat('train_window', '#20303f', .1), mat('train_light', '#fff2c0', .3, emit=10), mat('train_under', '#2a2a2e', .7)
    WD, GO, DK = mat('chest_wood', '#7a4a26', .8), mat('gold', '#f7c948', .3, metal=.9), mat('dark', '#111111', .8)
    YL, BKS = mat('hazard_yellow', '#ffd23a', .5), mat('hazard_black', '#1a1a1a', .5)
    CF, CR, CE = mat('coin_pearl', '#f2fbff', .15, metal=.6), mat('coin_aqua_rim', '#3ad8ff', .25, metal=.8, emit=1), mat('coin_shell', '#ffb0c8', .3, metal=.4)
    parts = [
        track_segment('uw_track_segment', BED, SL, RA, SD, side_w=1.8),
        glass_tunnel('uw_glass_tunnel_segment', FR, GLS, BASE),
        coral_branch('uw_coral_branch_a', [C1, C2], seed=1),
        coral_branch('uw_coral_branch_b', [C3, C4], seed=2),
        coral_fan('uw_coral_fan', C2, C3, seed=3),
        seaweed('uw_seaweed', SW1, SW2, seed=4),
        shark('uw_shark', SB, SBL, EYE),
        fish_school('uw_fish_school', [F1, F2, F3]),
        rock('uw_sea_rock', [RK, RK2], size=1.6, seed=5),
        train('uw_train', TB, TS, TRF, TW, TL, TU, stripe2=TS),
        ramp('uw_ramp', TU, YL, BKS),
        chest('uw_obstacle_treasure_chest', WD, GO, DK),
        barrier_high('uw_obstacle_pipe_gate', FR, YL, BKS, light=CR),
        rock('uw_obstacle_coral_rock', [RK, RK2], size=0.9, seed=8, moss=C2, n=2, kind='obstacle_low'),
        coin('uw_coin', CF, CR, CE, 'shell', dark=CR),
    ]
    cfg = dict(
        segment='uw_track_segment', seg_range=(-2, 18),
        repeat=[('uw_glass_tunnel_segment', 1, [(0, 0, 0, 0)])],
        world=dict(top='#063a75', hor='#1aa6dc', strength=1.0, haze=0.018, haze_hex='#2bb8e8', sun=(3.0, '#bfefff', (20, 0, 10))),
        ground=dict(hex='#b7a878', z=-0.4),
        scatter=[dict(names=['uw_coral_branch_a', 'uw_coral_branch_b', 'uw_coral_fan', 'uw_seaweed'], n=36, x=(7.5, 16), y=(-10, 160), s=(0.8, 1.5), z=-0.4),
                 dict(names=['uw_sea_rock'], n=12, x=(9, 22), y=(-10, 160), s=(0.8, 1.6), z=-0.4),
                 dict(names=['uw_fish_school'], n=8, x=(9, 20), y=(0, 120), s=(0.8, 1.3), z=4)],
        fixed=[('uw_shark', (-8, 30, 9), 70, 1.2), ('uw_shark', (6, 48, 11), -110, 1.0), ('uw_shark', (-3, 75, 13), 90, 1.5)],
        obstacles=[('uw_train', 1, 34), ('uw_ramp', 1, 25), ('uw_obstacle_treasure_chest', 0, 15), ('uw_obstacle_pipe_gate', -1, 24),
                   ('uw_obstacle_coral_rock', 0, 44), ('uw_train', -1, 60)],
        coins=[(0, 3, 6), (-1, 10, 7), (0, 26, 8)],
        coin_arcs=[(0, 15, 7), (0, 44, 7)],
        coins_raised=[(1, 29.5, 10, 4.1)],
        lights=[('POINT', (0, 10, 5), 300, '#7fe0ff'), ('POINT', (0, 35, 5), 300, '#7fe0ff')],
        coin='uw_coin', surface=0.56,
    )
    return parts, cfg


# =========================================================================== MAP 10 - Sky Ruins
def portal(name, st, st2, gold, crystal, glow):
    p = Part(name, 'landmark')
    for x in (-5.0, 5.0):
        p.box((2.0, 2.2, 9.0), (x, 0, 4.5), st, bevel=0.12)
        p.box((2.6, 2.8, 0.6), (x, 0, 0.3), st2, bevel=0.08)
        p.box((2.6, 2.8, 0.6), (x, 0, 9.2), st2, bevel=0.08)
        p.box((0.25, 2.25, 7.5), (x - 0.9 * (1 if x > 0 else -1), 0, 4.6), gold)
    p.ring(4.0, 6.0, 2.2, (0, 0, 9.5), st, a0=0, a1=180, seg=20)
    p.ring(3.85, 4.05, 2.3, (0, 0, 9.5), gold, a0=0, a1=180, seg=20)
    p.box((1.4, 2.4, 1.6), (0, 0, 15.3), st2, bevel=0.1)
    p.cyl(0.9, 1.4, (0, -1.0, 13.2), crystal, seg=6, r2=0.0, rot=(0, 0, 0))
    p.cyl(0.9, 1.0, (0, -1.0, 12.0), crystal, seg=6, r2=0.0, rot=(180, 0, 0))
    p.box((8.0, 0.2, 9.5), (0, 0.4, 4.75), glow)
    p.ring(0.001, 4.0, 0.2, (0, 0.4, 9.5), glow, a0=0, a1=180, seg=20)
    return p


def floating_island(name, rock_m, rock2, grass, tree=None, leaf=None, seed=0, R=4.0):
    p = Part(name, 'backdrop')
    r = random.Random(seed)
    p.cyl(0.4, R * 1.6, (0, 0, -R * 0.8), rock_m, seg=9, r2=R, jitter=R * 0.06, seed=seed)
    p.cyl(R * 0.7, R * 0.5, (0.3, 0.2, -R * 0.4), rock2, seg=9, r2=R * 0.95, jitter=R * 0.05, seed=seed + 1)
    p.cyl(R * 1.02, 0.4, (0, 0, 0.15), grass, seg=9, jitter=0.08, seed=seed + 2)
    for i in range(3):
        a = math.radians(r.uniform(0, 360))
        p.cyl(0.05, R * 0.6, (R * 0.6 * math.cos(a), R * 0.6 * math.sin(a), -R * 0.4), rock2, seg=6, r2=R * 0.25, jitter=0.1, seed=seed + 5 + i)
    if tree and leaf:
        for k in range(2):
            tx, ty = r.uniform(-R / 3, R / 3), r.uniform(-R / 3, R / 3)
            p.cyl(0.2, 2.4, (tx, ty, 1.5), tree, seg=6)
            p.ico(1.0, (tx, ty, 3.2), leaf, scale=(1.3, 1.3, 1.1), sub=1, jitter=0.15, seed=seed + 20 + k)
    return p


def pillar(name, st, st2, gold, h=6, broken=False, seed=0):
    p = Part(name)
    p.box((1.5, 1.5, 0.5), (0, 0, 0.25), st2, bevel=0.06)
    hh = h * (0.55 if broken else 1)
    p.cyl(0.55, hh, (0, 0, 0.5 + hh / 2), st, seg=12, jitter=0.03 if broken else 0, seed=seed)
    for z in (0.65, 0.5 + hh - 0.2):
        p.torus(0.57, 0.06, (0, 0, z), gold, seg=16, sides=6)
    if not broken:
        p.box((1.5, 1.5, 0.45), (0, 0, 0.5 + hh + 0.22), st2, bevel=0.06)
    else:
        p.cyl(0.55, 0.3, (0, 0, 0.5 + hh + 0.1), st, seg=12, r2=0.2, jitter=0.12, seed=seed + 1)
    return p


def fallen_column(name, st, st2, gold):
    p = Part(name, 'obstacle_low')
    p.cyl(0.48, 2.5, (0, 0, 0.48), st, rot=(0, 90, 0), seg=12)
    for x in (-0.9, 0.9):
        p.torus(0.5, 0.05, (x, 0, 0.48), gold, rot=(0, 90, 0), seg=16, sides=6)
    p.box((0.9, 0.9, 0.5), (1.2, 0.5, 0.25), st2, rot=(0, 0, 20), bevel=0.06, jitter=0.03)
    return p


def crystal_rock(name, rock_m, crystal):
    p = Part(name, 'obstacle_low')
    p.ico(0.9, (0, 0, 0.35), rock_m, scale=(1.3, 0.8, 0.55), sub=1, jitter=0.15, seed=4)
    for (x, h, tilt) in ((-0.5, 1.2, -15), (0.1, 1.6, 5), (0.6, 1.0, 20)):
        p.cyl(0.22, h, (x, 0, 0.5 + h / 2 - 0.2), crystal, seg=6, r2=0.0, rot=(0, tilt, 0))
    return p


def map10():
    S1, S2, S3 = mat('bridge_stone_a', '#d7cdb8', .8), mat('bridge_stone_b', '#c2b8a2', .8), mat('bridge_stone_c', '#e3dac6', .8)
    G, WL, WL2 = mat('grout', '#9a8f78', .9), mat('wall_stone', '#bfb49c', .8), mat('wall_stone_dark', '#958a74', .85)
    GOLD = mat('gold_trim', '#f2c033', .3, metal=.9)
    CRY, GLOW = mat('crystal', '#5ff0ff', .1, emit=6), mat('portal_glow', '#d8fbff', .3, emit=3, alpha=.55)
    RK, RK2, GR = mat('island_rock', '#7d6f62', .9), mat('island_rock_dark', '#5e5248', .9), mat('island_grass', '#6fbf4a', .8)
    TR, LF = mat('bark', '#6b4a2b', .9), mat('leaf', '#4fa832', .7)
    CL, CL2 = mat('cloud', '#ffffff', .9, emit=.3), mat('cloud_shade', '#e6f0ff', .9, emit=.2)
    CF, CR = mat('coin_gold', '#f7c948', .3, metal=.9), mat('coin_gold_dark', '#c98f22', .35, metal=.9)
    CE = mat('coin_crystal', '#5ff0ff', .1, emit=3)
    parts = [
        stone_path('sky_bridge_segment', [S1, S2, S3], G, WL, trim=GOLD, wall_h=1.0, seed=41, under=WL2, cap=WL2, post_every=2),
        portal('sky_portal_gate', WL, WL2, GOLD, CRY, GLOW),
        floating_island('sky_floating_island_a', RK, RK2, GR, TR, LF, seed=1, R=4.0),
        floating_island('sky_floating_island_b', RK, RK2, GR, seed=2, R=2.5),
        cloud('sky_cloud_a', CL, CL2, seed=1, size=3.5),
        cloud('sky_cloud_b', CL, CL2, seed=2, size=2.2),
        pillar('sky_pillar', S1, WL2, GOLD),
        pillar('sky_pillar_broken', S1, WL2, GOLD, broken=True, seed=3),
        fallen_column('sky_obstacle_fallen_column', S1, WL2, GOLD),
        beam_gate('sky_obstacle_arch', WL, S1, deco=GOLD, round_top=True),
        crystal_rock('sky_obstacle_crystal', RK, CRY),
        coin('sky_coin', CF, CR, CE, 'diamond', dark=CR),
    ]
    cfg = dict(
        segment='sky_bridge_segment', seg_range=(-2, 7),
        world=dict(top='#3f9cff', hor='#eaf7ff', strength=0.85, sun=(2.6, '#fff6e0', (45, 0, 30))),
        repeat=[('sky_pillar', 1, [(-4.65, 2.5, 1.95, 0), (4.65, 7.5, 1.95, 0)])],
        fixed=[('sky_portal_gate', (0, 72, 0), 0, 1.0), ('sky_floating_island_a', (-18, 60, 10), 0, 1.4),
               ('sky_floating_island_a', (22, 90, 18), 40, 2.0), ('sky_floating_island_b', (14, 40, 12), 0, 1.2),
               ('sky_floating_island_b', (-12, 25, 16), 0, 1.0), ('sky_floating_island_b', (-30, 110, 25), 0, 2.2),
               ('sky_floating_island_a', (35, 50, 5), 0, 1.0), ('sky_pillar_broken', (-8, 74, 0), 0, 1.5),
               ('sky_pillar_broken', (8, 74, 0), 0, 1.2)],
        scatter=[dict(names=['sky_cloud_a', 'sky_cloud_b'], n=26, x=(10, 60), y=(-10, 160), s=(1.0, 3.0), z=-12),
                 dict(names=['sky_cloud_a', 'sky_cloud_b'], n=10, x=(15, 60), y=(20, 160), s=(1.0, 2.0), z=8)],
        obstacles=[('sky_obstacle_fallen_column', 0, 14), ('sky_obstacle_arch', 1, 22), ('sky_obstacle_crystal', -1, 30),
                   ('sky_obstacle_arch', 0, 42), ('sky_obstacle_fallen_column', 1, 50)],
        coins=[(0, 2, 7), (-1, 10, 10), (1, 28, 7), (0, 50, 6)],
        coin_arcs=[(0, 14, 7), (1, 50, 7)],
        coin='sky_coin', surface=0.44,
    )
    return parts, cfg


MAPS = [
    (1, 'jungle_temple', 'Jungle Temple', map1),
    (2, 'city_subway', 'City Subway', map2),
    (3, 'desert_temple', 'Desert Temple', map3),
    (4, 'snow_village', 'Snow Village (Night)', map4),
    (5, 'neon_city', 'Neon City (Night)', map5),
    (6, 'jungle_river', 'Jungle River Bridge', map6),
    (7, 'canyon_sunset', 'Canyon Sunset', map7),
    (8, 'cherry_blossom', 'Cherry Blossom Path', map8),
    (9, 'underwater_tunnel', 'Underwater Tunnel', map9),
    (10, 'sky_ruins', 'Sky Ruins', map10),
]
