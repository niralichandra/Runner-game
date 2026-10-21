"""Option A demo: map 1 (Enchanted Jungle Temple) rebuilt with much more detailed models.

Run:  blender -b --factory-startup --python build_maps.py -- all set=options nobake
Output: <root>/romantic/options_sample/map1/
"""
import math, random
from mathutils import Vector
from lib import *
from romantic_lib import *
from maps import temple_gate
from maps_romantic import map1 as rom_map1, palette, tiki_head, add_wall_flowers


def vine(p, top, length, stem, leaves, seed=0, sway=0.25, leaf=0.16):
    """Hanging vine: wavy stem with alternating leaf cards."""
    r = random.Random(seed)
    n = max(3, int(length / 0.35))
    pts = [Vector(top) + Vector((sway * math.sin(i * 0.9 + seed) * (i / n), 0.05 * math.cos(i * 1.3), -length * i / n)) for i in range(n + 1)]
    for i in range(n):
        p.rod(pts[i], pts[i + 1], 0.025, stem, seg=4)
    for i in range(1, n + 1):
        p.leaf_cards(pts[i], 0.08, leaves, n=2, seed=seed * 31 + i, size=leaf * r.uniform(0.8, 1.2), flat=1.0)


def ornate_temple(name, P, st, st2, st3, dark, moss, gold):
    p = temple_gate(name, st, st2, dark, moss, P['leaf2'])
    r = random.Random(7)
    D = 6.0
    fy = -D / 2
    # grand stairs up to the doorway
    for k in range(6):
        h = 0.22 * (k + 1)
        p.box((10.5 - k * 0.45, 0.75, h), (0, fy - 0.4 - (5 - k) * 0.72, h / 2), (st2, st3)[k % 2], bevel=0.05, jitter=0.01, seed=k)
    for sg in (-1, 1):
        p.box((1.1, 4.6, 1.6), (sg * 5.6, fy - 2.4, 0.8), st, bevel=0.1)
        flame(p, (sg * 5.6, fy - 1.0, 1.75), 0.7, P['fire'], P['fire2'])
        p.cyl(0.45, 0.35, (sg * 5.6, fy - 1.0, 1.75), gold, seg=14, r2=0.6)
    # carved columns flanking the door and at the corners
    for x in (-4.6, 4.6, -9.2, 9.2):
        p.cyl(0.55, 8.2, (x, fy - 0.45, 4.1), st3, seg=14)
        for z in (0.4, 2.2, 4.1, 6.0, 7.9):
            p.torus(0.58, 0.08, (x, fy - 0.45, z), st2, seg=18, sides=6)
        p.box((1.5, 1.5, 0.45), (x, fy - 0.45, 8.45), st2, bevel=0.08)
        p.box((1.3, 1.3, 0.35), (x, fy - 0.45, 0.17), st2, bevel=0.06)
    # carved frieze bands
    for z in (7.7, 9.6):
        for k in range(36):
            x = -9.6 + k * 0.55
            p.box((0.42, 0.18, 0.42), (x, fy - 0.12, z), (st3, st2)[k % 2], bevel=0.04)
            if k % 3 == 0:
                p.box((0.2, 0.22, 0.2), (x, fy - 0.16, z), dark, bevel=0.02)
    # heart sunburst above the door
    heart(p, (0, fy - 0.35, 8.6), 2.0, 0.3, P['heart_glow'])
    heart_outline(p, (0, fy - 0.42, 8.6), 2.6, 0.07, gold)
    for k in range(12):
        a = math.radians(k * 30)
        p.prism([(-0.12, 0), (0.12, 0), (0, 0.7)], 0.08, (1.9 * math.cos(a), fy - 0.4, 8.6 + 1.9 * math.sin(a)), gold, rot=(0, 90 - k * 30, 0))
    p.box((7.0, 0.08, 0.6), (0, fy + 0.6, 0.3), mat('door_glow', '#ff6fb0', .4, emit=2.5), bevel=0)
    # small guardian heads on the roof tiers
    for (x, z) in ((-8.6, 9.0), (8.6, 9.0), (-6.2, 12.1), (6.2, 12.1), (-3.6, 14.8), (3.6, 14.8)):
        p.box((0.8, 0.7, 1.0), (x, fy + 0.9, z + 0.5), st3, bevel=0.15)
        for sx in (-0.17, 0.17):
            p.box((0.16, 0.1, 0.12), (x + sx, fy + 0.53, z + 0.65), dark, bevel=0.02)
        p.box((0.9, 0.75, 0.15), (x, fy + 0.9, z + 1.05), st2, bevel=0.04)
    # vines, moss and flowers everywhere
    for k in range(34):
        x = r.uniform(-10, 10)
        top = r.choice((8.5, 9.0, 12.0, 14.6))
        if abs(x) < 3.6 and top < 9:
            continue
        vine(p, (x, fy - 0.25, top), r.uniform(1.5, 5.5), P['leaf3'], [P['leaf'], P['leaf2'], P['leaf3']], seed=k)
    for (x, z) in ((-7, 8.7), (7, 8.7), (-5, 11.9), (5, 11.9), (-9.5, 0.5), (9.5, 0.5), (-2.5, 14.6), (2.5, 14.6)):
        flowers_on(p, (x, fy - 0.3, z), 1.3, [P['pink'], P['pink2'], P['pink3']], [P['center']], n=14, size=0.38, seed=int(x * 7 + z))
        p.ico(1.0, (x, fy - 0.2, z), moss, scale=(1.4, 0.6, 0.35), sub=2, jitter=0.15, seed=int(z * 3))
    return p


def detailed_tiki(name, P, st, st2, moss):
    p = tiki_head(name, st, st2, moss, P)
    for k in range(9):
        a = math.radians(-60 + k * 15)
        c = (0.95 * math.sin(a), 0.1, 2.95 + 0.9 * math.cos(a))
        p.prism([(-0.13, 0), (0.13, 0), (0, 0.95)], 0.06, c, (P['pink'], mat('feather_teal', '#2fbfa8', .5), P['gold'])[k % 3], rot=(0, -math.degrees(a), 0))
    for z in (0.35, 0.7):
        for k in range(6):
            p.box((0.16, 0.1, 0.16), (-0.5 + k * 0.2, -0.58, z), st2, bevel=0.03)
    for k in range(5):
        p.box((0.1, 0.1, 0.14), (-0.24 + k * 0.12, -0.7, 1.0), P['cream'], bevel=0.02)
    for sg in (-1, 1):
        p.torus(0.14, 0.04, (sg * 0.72, 0, 1.9), P['gold'], rot=(0, 90, 0), seg=12, sides=5)
    return p


def detailed_segment(name, P, S, G, WL, MO):
    p = stone_path(name, S, G, WL, moss=MO, wall_h=1.0, seed=11, under=WL, tile=(0.45, 0.8), gap_moss=MO)
    add_wall_flowers(p, P, 5, n=34)
    r = random.Random(3)
    for sg in (-1, 1):
        for k in range(5):
            y = r.uniform(0.4, SEG - 0.4)
            vine(p, (sg * 4.27, y, 1.3), r.uniform(0.6, 1.1), P['leaf3'], [P['leaf'], P['leaf2']], seed=k * 5 + sg, sway=0.04, leaf=0.12)
        for k in range(3):
            y = r.uniform(0.5, SEG - 0.5)
            for j in range(5):
                p.frond((sg * 4.65, y, 1.32), j * 72 + r.uniform(-15, 15), 0.7, r.choice([P['leaf'], P['leaf2']]), lift=1.0, droop=1.3, width=0.16, n=6, seed=k * 9 + j)
        for k in range(4):
            y = (k + 0.5) * SEG / 4
            p.box((0.05, 0.6, 0.45), (sg * 4.03, y, 0.8), G, bevel=0.02)
            p.box((0.06, 0.3, 0.22), (sg * 4.0, y, 0.8), WL, bevel=0.02)
    return p


def cascade(name, P, rocks, water, foam, mist):
    """Tall stepped waterfall cliff that sits right beside the path."""
    p = Part(name, 'backdrop', ao_h=5)
    r = random.Random(11)
    for k, (z, h, w) in enumerate(((0, 5, 7), (5, 5, 6.2), (10, 6, 5.4))):
        p.box((w, 4.5, h), (-0.4 * k, 1.2, z + h / 2), rocks[k % 2], bevel=0.5, seg=3, jitter=0.2, seed=k)
        for j in range(5):
            s = r.uniform(0.7, 1.4)
            p.ico(s, (r.uniform(-w / 2, w / 2), -1.2, z + r.uniform(0, h)), rocks[(j + k) % 2], scale=(1.2, 0.7, 1), sub=2, jitter=0.15, seed=k * 9 + j)
        p.box((1.8, 0.3, h), (0.6 - 0.4 * k, -1.1, z + h / 2), water, bevel=0.1)
        p.box((0.8, 0.32, h), (0.4 - 0.4 * k, -1.15, z + h / 2), foam, bevel=0.1)
        for j in range(6):
            p.sphere(r.uniform(0.25, 0.55), (0.6 - 0.4 * k + r.uniform(-1, 1), -1.4, z + 0.2), foam, scale=(1, 1, 0.6), seg=10, rings=6)
        flowers_on(p, (-w / 2 + 0.6, -1.4, z + h - 0.2), 0.9, [P['pink'], P['pink2']], [P['center']], n=8, size=0.35, seed=k * 3)
        p.ico(1.0, (w / 2 - 0.6, -1.0, z + h), P['leaf'], scale=(1.2, 1, 0.5), sub=2, jitter=0.12, seed=k)
        p.leaf_cards((w / 2 - 0.6, -1.0, z + h), 1.0, [P['leaf'], P['leaf2'], P['leaf3']], n=16, seed=k * 7, size=0.3)
        for j in range(4):
            vine(p, (r.uniform(-w / 2, w / 2), -1.6, z + h), r.uniform(1, 3), P['leaf3'], [P['leaf'], P['leaf2']], seed=k * 11 + j)
    p.cyl(3.0, 0.2, (0.4, -2.6, 0.1), water, seg=24)
    for j in range(10):
        p.sphere(r.uniform(0.6, 1.2), (r.uniform(-1.2, 2), r.uniform(-3, -1.5), r.uniform(0.3, 2.5)), mist, seg=12, rings=8)
    return p


def vine_tree(name, P):
    """Huge jungle tree whose canopy and vine curtain lean over the path edge (towards +X)."""
    p = round_tree(name, P['bark'], [P['leaf'], P['leaf2'], P['leaf3']], h=9.5, rad=4.0, seed=21, blobs=8)
    p.rod((0, 0, 6), (3.2, 0, 8.8), 0.35, P['bark'], seg=10, r2=0.18)
    p.canopy((3.4, 0, 9.4), 2.6, [P['leaf'], P['leaf2'], P['leaf3']], seed=33, blobs=4, cards=50, card_size=0.6)
    flowers_on(p, (2.0, 0, 9.4), 3.0, [P['pink'], P['pink2']], [P['center']], n=22, size=0.42, seed=8)
    r = random.Random(4)
    for k in range(26):
        x = r.uniform(0.5, 4.0)
        vine(p, (x, r.uniform(-2.2, 2.2), 8.4 - x * 0.2), r.uniform(2.5, 4.8), P['leaf3'], [P['leaf'], P['leaf2'], P['leaf3']], seed=k + 50)
    return p


def flower_carpet(name, P, seed=0):
    p = Part(name, ao_h=0.6)
    r = random.Random(seed)
    for k in range(10):
        c = (r.uniform(-1.0, 1.0), r.uniform(-0.6, 0.6), 0.15)
        p.ico(0.3, c, r.choice([P['leaf'], P['leaf3']]), scale=(1.3, 1, 0.6), sub=1, jitter=0.2, seed=k)
    for k in range(26):
        hibiscus(p, (r.uniform(-1.1, 1.1), r.uniform(-0.7, 0.7), 0.32 + r.uniform(0, 0.15)), r.uniform(0.2, 0.3),
                 r.choice([P['pink'], P['pink2'], P['pink3'], P['peach']]), P['center'], yaw=r.uniform(0, 360), tilt=r.uniform(0, 35))
    for j in range(6):
        p.frond((r.uniform(-0.8, 0.8), r.uniform(-0.4, 0.4), 0.1), r.uniform(0, 360), 0.9, r.choice([P['leaf'], P['leaf2']]), lift=0.9, droop=1.1, width=0.2, n=8, seed=j)
    return p


def map1_detailed():
    parts, cfg = rom_map1()
    P = palette()
    S = [mat('stone_a', '#c4a888', .85), mat('stone_b', '#b09276', .85), mat('stone_c', '#d2b898', .85)]
    G, WL, MO = mat('grout', '#4f5a3a', .9), mat('wall_stone', '#9a8068', .85), mat('moss', '#6aa63a', .8)
    DK = mat('doorway_dark', '#120a0e', 1)
    WA, FO = mat('water', '#9fe6ff', .1, emit=.8), mat('foam', '#ffffff', .4, emit=.6)
    MIST = mat('waterfall_mist', '#ffffff', .5, emit=.4, alpha=.35)
    replace = {'en_heart_temple_gate', 'en_tiki_statue', 'en_path_segment'}
    for p in parts:
        if p.name in replace:
            p.bm.free()
    parts = [p for p in parts if p.name not in replace]
    parts += [
        detailed_segment('en_path_segment', P, S, G, WL, MO),
        ornate_temple('en_heart_temple_gate', P, WL, S[1], S[2], DK, MO, P['gold']),
        detailed_tiki('en_tiki_statue', P, WL, S[1], MO),
        cascade('en_side_waterfall', P, [WL, S[1]], WA, FO, MIST),
        vine_tree('en_vine_tree', P),
        flower_carpet('en_flower_carpet', P, seed=1),
    ]
    cfg['fixed'] += [('en_side_waterfall', (-8.6, 30, -0.3), 90, 1.0), ('en_side_waterfall', (9.0, 44, -0.3), -90, 0.9),
                     ('en_vine_tree', (-9.5, 12, -0.3), 0, 1.0), ('en_vine_tree', (9.5, 22, -0.3), 180, 1.0)]
    cfg['edge'] = [dict(names=['en_flower_carpet', 'en_flower_bush', 'en_fern', 'en_flower_carpet'], x=(5.5, 6.4), step=(1.2, 2.2), z=-0.3, s=(0.9, 1.3))]
    cfg['framing'] = [('en_vine_tree', -8.2, 4, -0.3, 0, 1.0), ('en_flower_carpet', -5.8, 3, -0.3, 0, 1.6), ('en_flower_carpet', 5.8, 4, -0.3, 40, 1.6),
                      ('en_tiki_statue', 6.4, 12, -0.3, -30, 1.4)]
    cfg['glow_lights'] = cfg.get('glow_lights', []) + [('en_heart_temple_gate', (0, -3.6, 8.6), 300, '#ff6fb0'),
                                                       ('en_heart_temple_gate', (5.6, -4.0, 2.4), 200, '#ff9a3a'),
                                                       ('en_heart_temple_gate', (-5.6, -4.0, 2.4), 200, '#ff9a3a')]
    return parts, cfg


MAPS = [(1, 'enchanted_jungle_temple_detailed', 'Enchanted Jungle Temple (detailed models)', map1_detailed)]
