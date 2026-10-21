"""Romantic map set: 10 redesigned maps for the birthday runner.

Same conventions as maps.py (lanes x = -2.6/0/+2.6, runner along +Y, 10 m tileable segments),
so the game code, level.json format and collision kinds are unchanged. New asset kind: 'powerup'.
"""
import math, random
from lib import *
from romantic_lib import *
from maps import (temple_gate, city_building, skyscraper, catenary, neon_building, plank_bridge, bank, ruin_gate, mesa,
                  trestle, cactus, mine_cart, cherry_tree, stone_lantern, pagoda, torii, low_wall, glass_tunnel,
                  coral_branch, coral_fan, seaweed, fish_school, chest, floating_island, pillar, fallen_column,
                  crystal_rock, snow_house, snowman, tunnel_gate, banner_pole, stone_block, beam_gate, log, snow_fence)

CAM = dict(loc=(0, -6.0, 4.4), target=(0, 30, 0.7), lens=27)


# shared romantic palette (material names are per map file, so re-creating them per map is fine)
def palette():
    return dict(
        pink=mat('petal_pink', '#ff5c9d', .55), pink2=mat('petal_light', '#ff9cc6', .55), pink3=mat('petal_blush', '#ffd0e4', .55),
        lav=mat('petal_lavender', '#c39bff', .55), peach=mat('petal_peach', '#ffb38a', .55), cream=mat('cream', '#fff3e0', .6),
        center=mat('flower_center', '#ffd23a', .5), gold=mat('gold', '#f5c542', .28, metal=.9),
        gold2=mat('gold_dark', '#c98f22', .35, metal=.9), heart_glow=mat('heart_glow', '#ff4f9a', .3, emit=7),
        warm_glow=mat('lantern_glow', '#ffcf7a', .3, emit=7), glass=mat('lantern_glass', '#fff4f9', .1, alpha=.35),
        metal=mat('iron_dark', '#2e2a33', .45, metal=.6), white=mat('white', '#ffffff', .4),
        leaf=mat('leaf', '#3f9a3a', .7), leaf2=mat('leaf_light', '#66bb44', .7), leaf3=mat('leaf_dark', '#2b7230', .7),
        bark=mat('bark', '#6b4a2b', .9), bark2=mat('bark_dark', '#563a20', .9),
        fire=mat('fire', '#ff7a12', .5, emit=8), fire2=mat('fire_core', '#ffd84a', .5, emit=12),
        wings=[mat('butterfly_pink', '#ff6fb5', .5, emit=0.6), mat('butterfly_lav', '#b98cff', .5, emit=0.6),
               mat('butterfly_peach', '#ffb36b', .5, emit=0.6)],
    )


COIN_KIND = {'en': 'emerald', 'rc': 'bow', 'sd': 'sun', 'sf': 'snowflake', 'rn': 'bolt', 'tf': 'starfish', 'rr': 'amber',
             'cb': 'sakura', 'mu': 'shell', 'hs': 'wing'}


def pickups(prefix, P, coin_gold, coin_rim, coin_emb, extra):
    """Coin + heart (extra life) + the map's own power-up(s)."""
    out = [collectible(COIN_KIND[prefix], prefix + '_coin', P),
           heart_pickup(prefix + '_powerup_heart', mat(prefix + '_heart_pink', '#ff3d8b', .25, emit=0.8), P['heart_glow'], P['gold'])]
    return out + extra


def add_wall_flowers(p, P, seed, W=8.4, z=1.32, n=10, petals=None):
    r = random.Random(seed)
    for k in range(n):
        sg = (-1, 1)[k % 2]
        hibiscus(p, (sg * (W / 2 + 0.45) + r.uniform(-0.2, 0.2), r.uniform(0.3, SEG - 0.3), z + r.uniform(0, 0.1)),
                 r.uniform(0.22, 0.32), r.choice(petals or [P['pink'], P['pink2'], P['pink3']]), P['center'],
                 yaw=r.uniform(0, 360), tilt=r.uniform(10, 40))
        p.ico(0.22, (sg * (W / 2 + 0.45) + r.uniform(-0.3, 0.3), r.uniform(0.3, SEG - 0.3), z - 0.02), P['leaf'], sub=1,
              jitter=0.2, scale=(1.2, 1, 0.5), seed=seed + k)


def tiki_head(name, stone, stone2, moss, P):
    p = Part(name)
    p.box((1.3, 1.1, 2.6), (0, 0, 1.3), stone, bevel=0.2, seg=3, jitter=0.03)
    p.box((1.5, 1.25, 0.35), (0, 0, 2.7), stone2, bevel=0.1)
    for sx in (-0.3, 0.3):
        p.box((0.36, 0.2, 0.28), (sx, -0.56, 1.95), stone2, bevel=0.06)
        p.box((0.16, 0.22, 0.14), (sx, -0.6, 1.95), mat('tiki_eye', '#2a2018', .7), bevel=0.03)
    p.box((0.3, 0.3, 0.6), (0, -0.62, 1.55), stone2, bevel=0.1)
    p.box((0.8, 0.22, 0.22), (0, -0.58, 1.05), stone2, bevel=0.06)
    p.box((1.32, 0.06, 0.08), (0, -0.56, 0.6), moss, bevel=0)
    flowers_on(p, (0, 0, 2.9), 0.55, [P['pink'], P['pink2']], [P['center']], n=5, size=0.3, seed=2)
    return p


# =========================================================================== 1 Enchanted Jungle Temple
def map1():
    P = palette()
    S = [mat('stone_a', '#c4a888', .85), mat('stone_b', '#b09276', .85), mat('stone_c', '#d2b898', .85)]
    G, WL, MO = mat('grout', '#4f5a3a', .9), mat('wall_stone', '#9a8068', .85), mat('moss', '#6aa63a', .8)
    DK = mat('doorway_dark', '#120a0e', 1)
    WA, FO = mat('water', '#9fe6ff', .1, emit=.8), mat('foam', '#ffffff', .4, emit=.6)
    seg = stone_path('en_path_segment', S, G, WL, moss=MO, wall_h=1.0, seed=11, under=WL, tile=(0.45, 0.8), gap_moss=MO)
    add_wall_flowers(seg, P, 5, n=26)
    gate = temple_gate('en_heart_temple_gate', WL, S[1], DK, MO, P['leaf2'])
    heart(gate, (0, -3.35, 8.6), 2.0, 0.3, P['heart_glow'])
    heart_outline(gate, (0, -3.4, 8.6), 2.6, 0.06, P['gold'])
    for k, z in enumerate((0.15, 0.45, 0.75)):
        gate.box((7.6 - k * 0.6, 1.2, 0.3), (0, -3.6 - (2 - k) * 0.6, z), S[k % 3], bevel=0.06)
    flowers_on(gate, (-7, -2.5, 8.6), 2.0, [P['pink'], P['pink2']], [P['center']], n=14, size=0.45, seed=3)
    flowers_on(gate, (7, -2.5, 8.6), 2.0, [P['pink'], P['pink3']], [P['center']], n=14, size=0.45, seed=4)
    tree = round_tree('en_jungle_tree', P['bark'], [P['leaf'], P['leaf2'], P['leaf3']], h=6, rad=2.8, seed=3)
    flowers_on(tree, (0, 0, 6.6), 2.6, [P['pink'], P['pink2']], [P['center']], n=16, size=0.4, seed=5)
    fall = waterfall('en_waterfall', [WL, S[1]], WA, FO, h=16, top=[P['leaf'], P['leaf2'], P['leaf3']])
    flowers_on(fall, (0, 1, 16.5), 4, [P['pink'], P['pink2']], [P['center']], n=16, size=0.5, seed=6)
    bushp = blob_bush('en_flower_bush', [P['leaf'], P['leaf3']], seed=4, size=1.3)
    flowers_on(bushp, (0, 0, 0.9), 1.1, [P['pink'], P['pink2'], P['pink3']], [P['center']], n=12, size=0.35, seed=7)
    arch = deco_arch('en_flower_arch', WL, [P['leaf'], P['leaf3']], [P['pink'], P['pink2'], P['pink3']], [P['center']], glow=P['heart_glow'])
    beam = beam_gate('en_obstacle_vine_beam', WL, S[1], deco=G, moss=MO)
    flowers_on(beam, (0, 0, 3.2), 1.0, [P['pink'], P['pink2']], [P['center']], n=6, size=0.3, seed=8)
    parts = [
        seg, gate, arch,
        heart_lantern('en_heart_lantern', P['metal'], P['heart_glow'], P['glass'], h=2.2, base=WL),
        torch('en_torch', S[1], mat('bronze', '#7a5a3a', .5, metal=.6), P['fire'], P['fire2'], h=0.9),
        palm('en_palm_tree', P['bark'], P['bark2'], P['leaf'], P['leaf2'], h=7, seed=1),
        tree, bush('en_fern', [P['leaf'], P['leaf2'], P['leaf3']], seed=2, size=1.2), bushp, fall,
        cliff('en_cliff', [WL, S[1], S[0]], w=9, d=7, h=14, seed=7, top=[P['leaf'], P['leaf2'], P['leaf3']]),
        tiki_head('en_tiki_statue', WL, S[1], MO, P),
        pillar('en_broken_pillar', S[2], WL, P['gold'], broken=True, seed=3),
        ruin_gate('en_stone_archway', S[0], WL, MO, DK),
        butterfly_cluster('en_butterflies', P['wings'], P['metal'], seed=1),
        spiked_block('en_obstacle_spiked_block', S[1], mat('spike_iron', '#5a5560', .35, metal=.8)),
        beam, log('en_obstacle_fallen_log', P['bark'], mat('log_ring', '#c99a5e', .8), moss=MO),
    ] + pickups('en', P, P['gold'], P['gold2'], mat('en_coin_heart', '#ff4f9a', .3, emit=1.2),
                [magnet('en_powerup_magnet', mat('magnet_red', '#e8314f', .35), mat('magnet_steel', '#d8dde5', .25, metal=.9), P['heart_glow'])])
    cfg = dict(
        camera=CAM,
        segment='en_path_segment', seg_range=(-2, 6),
        world=dict(haze=0.42, top='#6fb8ff', hor='#ffe3f0', strength=1.0, sun=(3.8, '#fff0e0', (50, 0, 35))),
        ground=dict(hex='#4c8a30', z=-0.3),
        repeat=[('en_heart_lantern', 1, [(-4.65, 5.0, 2.05, 0)]), ('en_torch', 1, [(4.65, 5.0, 2.05, 0)]), ('en_flower_arch', 2, [(0, 42, 0, 0)])],
        fixed=[('en_heart_temple_gate', (0, 58, 0), 0, 1.3), ('en_waterfall', (-12, 40, -0.3), 25, 1.0),
               ('en_waterfall', (13, 50, -0.3), -20, 1.1), ('en_cliff', (-16, 62, -0.3), 0, 1.3), ('en_cliff', (17, 64, -0.3), 0, 1.2),
               ('en_tiki_statue', (-6.4, 52, -0.3), 20, 1.6), ('en_tiki_statue', (6.4, 52, -0.3), -20, 1.6),
               ('en_stone_archway', (-8, 28, -0.3), 90, 1.4)],
        scatter=[dict(names=['en_palm_tree', 'en_jungle_tree', 'en_jungle_tree'], n=26, x=(6.6, 12), y=(-10, 56), s=(1.0, 1.4), z=-0.3),
                 dict(names=['en_fern', 'en_flower_bush', 'en_broken_pillar'], n=36, x=(5.8, 10), y=(-10, 56), s=(0.9, 1.4), z=-0.3),
                 dict(names=['en_butterflies'], n=8, x=(5.5, 10), y=(0, 60), s=(0.8, 1.2), zr=(2, 4.5))],
        obstacles=[('en_obstacle_spiked_block', -1, 14), ('en_obstacle_vine_beam', 0, 22), ('en_obstacle_fallen_log', 1, 30),
                   ('en_obstacle_spiked_block', 0, 40), ('en_obstacle_vine_beam', -1, 48)],
        powerups=[('en_powerup_magnet', 1, 20), ('en_powerup_heart', -1, 36)],
        coins=[(0, 3, 6), (1, 10, 6), (-1, 26, 6), (0, 46, 4)], coin_arcs=[(-1, 14, 7), (0, 40, 7)],
        edge=[dict(names=['en_flower_bush', 'en_fern', 'en_flower_bush'], x=(5.5, 6.4), step=(1.6, 2.8), z=-0.3, s=(0.9, 1.3))],
        framing=[('en_jungle_tree', -7.4, 6, -0.3, 0, 1.3), ('en_palm_tree', 7.2, 9, -0.3, 30, 1.2),
                 ('en_flower_bush', -5.9, 3, -0.3, 0, 1.7), ('en_flower_bush', 5.9, 4, -0.3, 40, 1.6)],
        glow_lights=[('en_heart_lantern', (0, 0, 2.55), 80, '#ff6fb0'), ('en_torch', (0, 0, 1.45), 120, '#ff9a3a')],
        coin='en_coin', surface=0.44,
    )
    return parts, cfg


# =========================================================================== 2 Romantic City Subway
def romantic_building(name, w, d, floors, wall, P, seed, awning, sign_txt_m):
    trim, glass, frame = P['cream'], mat('window_glass', '#3a4f78', .15, metal=.3), P['white']
    p = city_building(name, w, d, floors, wall, trim, glass, frame, mat('roof_terracotta', '#c8664a', .8), seed=seed,
                      awning=awning, door=mat('door_wine', '#7a2a3a', .7), balcony=P['metal'])
    nwin = max(2, int(w / 2.2))
    r = random.Random(seed)
    for f in range(1, floors):
        for i in range(nwin):
            yc = -w / 2 + (i + 0.5) * w / nwin
            p.box((0.4, 1.4, 0.3), (d / 2 + 0.25, yc, f * 3.0 + 0.72), mat('planter_box', '#8a4a3a', .7), bevel=0.04)
            for k in range(3):
                p.ico(0.2, (d / 2 + 0.3, yc - 0.45 + k * 0.45, f * 3.0 + 0.95), P['leaf'], sub=1, jitter=0.2, seed=seed + k)
                hibiscus(p, (d / 2 + 0.42, yc - 0.45 + k * 0.45, f * 3.0 + 1.0), 0.17, r.choice([P['pink'], P['pink2'], P['peach']]),
                         P['center'], tilt=70, yaw=-90)
    p.box((0.2, 2.2, 0.9), (d / 2 + 0.15, -w / 2 + 1.6, 3.4), sign_txt_m, bevel=0.06)
    heart(p, (d / 2 + 0.32, -w / 2 + 1.6, 3.38), 0.6, 0.08, P['heart_glow'], rot=(0, 0, 90))
    return p


def map2():
    P = palette()
    BED, SL, RA = mat('ballast', '#8a6a5a', .95), mat('sleeper', '#5a3a24', .9), mat('rail', '#b7bcc6', .3, metal=.9)
    SW, CU = mat('sidewalk_cream', '#f2dcc8', .85), mat('curb_pink', '#ff7eb6', .7)
    walls = [mat('wall_rose', '#ff9cbf', .8), mat('wall_peach', '#ffc29a', .8), mat('wall_lavender', '#c9b0ff', .8),
             mat('wall_cream', '#fff0d6', .8), mat('wall_coral', '#ff8a8a', .8), mat('wall_mint', '#b8ead2', .8)]
    AW1, AW2 = mat('awning_pink', '#ff5c9d', .7), mat('awning_white', '#fafafa', .7)
    TB, TS, TRF = mat('train_pink', '#ff86b8', .4), mat('train_white', '#fff4f8', .45), mat('train_roof', '#e8dce6', .5, metal=.3)
    TW, TL, TU = mat('train_window', '#2a2a44', .1), mat('train_light', '#fff6d0', .3, emit=8), mat('train_under', '#3a3040', .7)
    SIGN = mat('shop_sign', '#fff3f8', .6)
    pink_train = train('rc_pink_train', TB, TS, TRF, TW, TL, TU, door=mat('train_door', '#ff5c9d', .4), stripe2=P['gold'])
    heart(pink_train, (0, -6.12, 1.3), 0.7, 0.1, P['heart_glow'])
    gatep = Part('rc_city_gate', 'landmark')
    for sg in (-1, 1):
        gatep.box((9.0, 3.0, 13.0), (sg * 10.1, 0, 6.5), walls[3], bevel=0.15)
        gatep.box((0.6, 3.3, 6.5), (sg * 5.85, 0, 3.25), P['cream'], bevel=0.08)
        for z in (2.5, 6.0, 9.5):
            gatep.ring(0.0001, 0.7, 0.2, (sg * 10.1, -1.55, z + 1.2), mat('gate_window', '#ffd9a0', .4, emit=3), a0=0, a1=180, seg=10, bevel=0)
            gatep.box((1.4, 0.2, 1.2), (sg * 10.1, -1.55, z + 0.6), mat('gate_window', '#ffd9a0', .4, emit=3), bevel=0)
    gatep.ring(5.6, 6.2, 3.3, (0, 0, 6.5), P['cream'], a0=0, a1=180, seg=24)
    for sg in (-1, 1):
        gatep.prism([(sg * 5.6 * math.cos(math.radians(90 * i / 8)), 6.5 + 5.6 * math.sin(math.radians(90 * i / 8))) for i in range(9)]
                    + [(sg * 5.6, 13.0)], 3.0, (0, 0, 0), walls[3], bevel=0)
    gatep.box((11.2, 3.0, 1.2), (0, 0, 12.7), walls[3], bevel=0.1)
    gatep.box((31, 3.6, 0.6), (0, 0, 13.3), P['cream'], bevel=0.1)
    heart(gatep, (0, -1.8, 14.2), 2.2, 0.3, P['heart_glow'])
    for sg in (-1, 1):
        gatep.cyl(1.6, 4, (sg * 13.5, 0, 15), walls[0], seg=16)
        gatep.cyl(2.0, 3.5, (sg * 13.5, 0, 18.7), mat('roof_teal', '#5ab8b0', .6), seg=16, r2=0.05)
    gate_blank = gatep
    trk = track_segment('rc_track_segment', BED, SL, RA, SW, curb=CU)
    sparkle_field(trk, [mat('sparkle_gold', '#ffd36a', .3, emit=6), mat('sparkle_pink', '#ff8fc8', .3, emit=6)], seed=2)
    parts = [
        trk,
    ] + [romantic_building('rc_building_%s' % c, 8, 6, (4, 5, 4, 6, 5, 4)[i], walls[i], P, i, (AW1, AW2) if i % 2 == 0 else None, SIGN)
         for i, c in enumerate('abcdef')] + [
        victorian_lamp('rc_victorian_lamp', P['metal'], P['warm_glow'], flowers=([P['pink'], P['pink2']], [P['center']])),
        string_lights('rc_heart_garland', P['metal'], [P['heart_glow'], mat('heart_red', '#ff2f5a', .4, emit=4), P['pink2']],
                      P['metal'], span=16.5, h=7.0, hearts=True, n=18),
        string_lights('rc_fairy_lights', P['metal'], [P['warm_glow'], mat('bulb_pink', '#ff8fc0', .3, emit=6)], P['metal'],
                      span=16.5, h=6.2, n=28, poles=False),
        catenary('rc_catenary_frame', P['metal'], mat('wire', '#1a1a1a', .6), mat('insulator', '#ff9cc6', .5)),
        bench('rc_bench', mat('bench_wood', '#a0623a', .7), P['metal']),
        rail_signal('rc_rail_signal', P['metal'], mat('sig_red', '#ff3040', .3, emit=6), mat('sig_green', '#40ff80', .3, emit=2),
                    mat('sig_amber', '#ffb030', .3, emit=2)),
        planter('rc_flower_planter', mat('planter_stone', '#e8d6c6', .8), [P['leaf'], P['leaf3']], [P['pink'], P['pink2'], P['peach']], [P['center']]),
        round_tree('rc_blossom_tree', P['bark'], [P['pink2'], P['pink3'], P['pink']], h=4.5, rad=2.0, seed=5),
        skyscraper('rc_skyscraper', 10, 40, mat('tower_glass', '#c8b8ff', .2, metal=.4), P['cream'], P['metal'], seed=1),
        gate_blank, pink_train,
        ramp('rc_ramp', TU, mat('ramp_pink', '#ff5c9d', .5), P['cream']),
        barrier_low('rc_barrier_low', mat('barrier_pink', '#ff5c9d', .6), P['white'], P['metal'], light=P['heart_glow']),
        barrier_high('rc_barrier_high', P['metal'], mat('barrier_pink2', '#ff5c9d', .6), P['white'], sign=SIGN),
    ] + pickups('rc', P, P['gold'], P['gold2'], mat('rc_coin_heart', '#ff4f9a', .3, emit=1.2),
                [magnet('rc_powerup_magnet', mat('magnet_red', '#e8314f', .35), mat('magnet_steel', '#d8dde5', .25, metal=.9), P['heart_glow'])])
    blds = ['rc_building_%s' % c for c in 'abcdef']
    cfg = dict(
        camera=CAM,
        segment='rc_track_segment', seg_range=(-2, 22), repeat_min_y=8,
        world=dict(haze=0.42, top='#7cc0ff', hor='#ffe0ea', strength=1.0, sun=(4.2, '#fff0e0', (55, 0, -30))),
        ground=dict(hex='#d8c3b0', z=-0.02),
        repeat=[('rc_heart_garland', 2, [(0, 12, 0, 0)]),
                ('rc_fairy_lights', 2, [(0, 17, 0, 0)]), ('rc_victorian_lamp', 2, [(-6.2, 4, 0.5, 0), (6.2, 14, 0.5, 180)]),
                ('rc_flower_planter', 2, [(6.5, 8, 0.5, 90), (-6.5, 18, 0.5, 90)]), ('rc_bench', 4, [(-6.4, 11, 0.5, 90)])],
        rows=[dict(names=blds, x=10.4, y=(-15, 210), step=8.2)],
        fixed=[('rc_city_gate', (0, 62, 0), 0, 1.15), ('rc_pink_train', (-2.6, 9, 0.46), 0, 1.0), ('rc_skyscraper', (-30, 230, 0), 0, 1.0), ('rc_skyscraper', (22, 260, 0), 20, 1.4),
               ('rc_rail_signal', (5.6, 6, 0.5), 0, 1.0), ('rc_rail_signal', (-5.6, 60, 0.5), 0, 1.0)],
        scatter=[dict(names=['rc_blossom_tree'], n=8, x=(6.3, 6.8), y=(20, 150), s=(0.8, 1.0), z=0.5)],
        obstacles=[('rc_pink_train', 1, 34), ('rc_ramp', 1, 25), ('rc_pink_train', 1, 46.5), ('rc_barrier_low', 0, 18),
                   ('rc_barrier_high', -1, 26), ('rc_pink_train', -1, 70), ('rc_barrier_low', 0, 52)],
        powerups=[('rc_powerup_magnet', -1, 14), ('rc_powerup_heart', 0, 40)],
        coins=[(0, 3, 8), (-1, 16, 4), (1, 22, 4), (0, 30, 8)], coin_arcs=[(0, 18, 7), (0, 52, 7)],
        coins_raised=[(1, 29.5, 10, 4.1)],
        edge=[dict(names=['rc_flower_planter', 'rc_flower_planter', 'rc_victorian_lamp', 'rc_blossom_tree'], x=(6.0, 6.8), step=(2.5, 4.5), z=0.5, s=(0.9, 1.1), spin=False)],
        framing=[('rc_victorian_lamp', -6.3, 7, 0.5, 0, 1.25), ('rc_flower_planter', 6.4, 5, 0.5, 90, 1.4), ('rc_blossom_tree', 6.6, 11, 0.5, 0, 1.1)],
        glow_lights=[('rc_victorian_lamp', (0.7, 0, 3.75), 90, '#ffd09a'), ('rc_victorian_lamp', (-0.7, 0, 3.75), 90, '#ffd09a')],
        coin='rc_coin', surface=0.56,
    )
    return parts, cfg


# =========================================================================== 3 Sunset Desert Kingdom
def map3():
    P = palette()
    S = [mat('sand_tile_a', '#efbd8a', .85), mat('sand_tile_b', '#e2a67a', .85), mat('sand_tile_c', '#f6d0a4', .85)]
    G, WL, WL2 = mat('sand_grout', '#b0784a', .9), mat('sandstone', '#d6956a', .85), mat('sandstone_light', '#ecb98c', .85)
    DOME = mat('dome_rose_gold', '#f0a088', .3, metal=.6)
    CL, DK = mat('cloth_red', '#c8304a', .8), mat('doorway_dark', '#2a140e', 1)
    seg = stone_path('sd_path_segment', S, G, WL, wall_h=1.1, seed=21, cap=WL2, tile=(0.45, 0.8))
    for k in range(4):
        sg = (-1, 1)[k % 2]
        seg.prism(star_pts(0.22, 0.09, 8), 0.06, (sg * 5.0, (k // 2) * 5 + 1.67, 1.0), P['gold'], rot=(0, 0, 90))
    dune = Part('sd_rose_dune', 'backdrop')
    dune.ico(1.0, (0, 0, 0), mat('rose_sand', '#f2b0a0', .9), scale=(14, 9, 4), sub=3, jitter=0.03, seed=2)
    dune.ico(1.0, (8, 5, 0), mat('rose_sand_light', '#f8c8b0', .9), scale=(9, 7, 3), sub=3, jitter=0.03, seed=3)
    larch = deco_arch('sd_lantern_arch', WL2, None, None, [P['center']], glow=P['warm_glow'], bulbs=[P['warm_glow'], P['heart_glow']], flowers=False)
    gl = heart_lantern('sd_golden_lantern', P['gold2'], P['warm_glow'], P['glass'], h=2.0, base=WL2)
    parts = [
        seg, desert_palace('sd_palace', WL, WL2, DOME, P['gold'], DK, CL),
        guardian_lion('sd_lion_statue', WL2, WL, P['gold']),
        brazier('sd_brazier', WL2, P['gold2'], P['fire'], P['fire2']),
        banner_pole('sd_banner_pole', mat('banner_wood', '#6b4426', .8), CL, P['gold']),
        palm('sd_palm_tree', P['bark'], P['bark2'], P['leaf'], P['leaf2'], h=7, seed=3),
        gl, dune, larch,
        cliff('sd_cliff', [mat('cliff_rose', '#d88a70', .9), mat('cliff_peach', '#eaa680', .9), mat('cliff_dusk', '#b86e60', .9)], w=10, d=8, h=18, seed=2),
        bush('sd_desert_shrub', [P['leaf2'], P['leaf']], seed=5, size=0.8, flower=P['pink']),
        heart_crate('sd_obstacle_crate', mat('crate_wood', '#a0683a', .8), mat('crate_band', '#5a3820', .8), CL),
        spiked_ball('sd_obstacle_spiked_ball', mat('iron_ball', '#3a3640', .4, metal=.7), mat('spike_iron', '#8a8590', .3, metal=.9), base=WL),
        beam_gate('sd_obstacle_lintel', WL, WL2, deco=CL),
    ] + pickups('sd', P, P['gold'], P['gold2'], mat('sd_coin_heart', '#c8304a', .3, emit=0.6),
                [shield('sd_powerup_shield', mat('shield_blue', '#3a8bff', .3, emit=0.5), P['gold'], P['white'])])
    cfg = dict(
        camera=CAM,
        segment='sd_path_segment', seg_range=(-2, 6),
        world=dict(haze=0.25, saturation=1.0, contrast=2.0, top='#8a6fd8', hor='#ffb38a', strength=1.1, sun=(4.0, '#ffc48a', (70, 0, -30)), clouds=True),
        ground=dict(hex='#eeb48a', z=0.0),
        repeat=[('sd_brazier', 2, [(-4.65, 5.0, 0.98, 0)]), ('sd_golden_lantern', 2, [(4.65, 5.0, 1.0, 0)]),
                ('sd_banner_pole', 2, [(-6.2, 12, 0, 0), (6.2, 17, 0, 180)]), ('sd_lantern_arch', 2, [(0, 42, 0, 0)])],
        fixed=[('sd_palace', (0, 58, 0), 0, 1.25), ('sd_lion_statue', (-6.6, 50, 0), 15, 1.6), ('sd_lion_statue', (6.6, 50, 0), -15, 1.6),
               ('sd_cliff', (-15, 40, 0), 0, 1.2), ('sd_cliff', (16, 55, 0), 40, 1.3), ('sd_rose_dune', (-35, 30, 0), 0, 1.5),
               ('sd_rose_dune', (35, 45, 0), 60, 1.8)],
        scatter=[dict(names=['sd_palm_tree'], n=18, x=(6.8, 11), y=(-10, 52), s=(1.0, 1.3)),
                 dict(names=['sd_desert_shrub'], n=16, x=(6, 16), y=(-10, 66), s=(0.8, 1.4))],
        obstacles=[('sd_obstacle_crate', 0, 14), ('sd_obstacle_lintel', 1, 22), ('sd_obstacle_spiked_ball', -1, 30),
                   ('sd_obstacle_crate', 1, 42), ('sd_obstacle_lintel', 0, 50)],
        powerups=[('sd_powerup_shield', -1, 20), ('sd_powerup_heart', 1, 34)],
        coins=[(0, 2, 7), (-1, 10, 6), (1, 28, 7)], coin_arcs=[(0, 14, 7), (1, 42, 7)],
        edge=[dict(names=['sd_desert_shrub', 'sd_golden_lantern', 'sd_palm_tree', 'sd_desert_shrub'], x=(5.6, 7.0), step=(2.5, 4.5), s=(0.9, 1.2))],
        framing=[('sd_palm_tree', -7.0, 8, 0, 0, 1.3), ('sd_brazier', 5.7, 6, 0, 0, 1.3), ('sd_lion_statue', -6.6, 15, 0, -70, 1.2)],
        glow_lights=[('sd_brazier', (0, 0, 2.2), 160, '#ff9a3a'), ('sd_golden_lantern', (0, 0, 2.35), 70, '#ffc070')],
        coin='sd_coin', surface=0.44,
    )
    return parts, cfg


# =========================================================================== 4 Snowy Fairytale Railway
def map4():
    P = palette()
    BED, SL, RA = mat('ballast_snowy', '#8a84a8', .9), mat('sleeper', '#7a4f32', .85), mat('rail', '#c8cde0', .3, metal=.9)
    SN, SN2 = mat('snow', '#f6f4ff', .55), mat('snow_shadow', '#dcd8f6', .6)
    WIN = mat('window_warm', '#ffc46a', .4, emit=6)
    BULBS = [mat('bulb_pink', '#ff6fb5', .3, emit=8), mat('bulb_gold', '#ffd36a', .3, emit=8)]
    trk4 = track_segment('sf_track_segment', BED, SL, RA, SN, side_h=0.65)
    sparkle_field(trk4, [mat('sparkle_gold', '#ffd36a', .3, emit=7), mat('sparkle_pink', '#ff8fc8', .3, emit=7)], seed=4)
    houses = []
    for i, (c, wall) in enumerate(zip('abc', ('#ffb8c8', '#fff0d8', '#d8c0ff'))):
        h = snow_house('sf_house_' + c, mat('house_wall_' + c, wall, .8), mat('wood_dark', '#5a3424', .85), mat('roof', '#8a3a4a', .8),
                       SN, WIN, mat('door', '#7a2a3a', .8), mat('chimney_brick', '#a05a4a', .9), floors=2 if i != 1 else 3, seed=i)
        H = (2 if i != 1 else 3) * 3.0
        for k in range(14):
            y = -3.5 + k * 0.54
            for sg in (-1, 1):
                h.sphere(0.07, (sg * 3.65, y, H + 0.2), BULBS[(k + i) % 2], seg=8, rings=5)
        houses.append(h)
    TB, TS = mat('train_pink', '#ff9cc6', .4), mat('train_cream', '#fff4e8', .45)
    tr = train('sf_train', TB, TS, mat('train_roof_snow', '#f8f6ff', .5), mat('train_window', '#ffd27a', .2, emit=3),
               mat('train_light', '#fff6d0', .3, emit=10), mat('train_under', '#2a2d33', .7), stripe2=P['gold'])
    heart(tr, (0, -6.12, 1.3), 0.7, 0.1, P['heart_glow'])
    crates = heart_crate('sf_obstacle_snowy_crates', mat('crate_wood', '#8a5a3a', .8), mat('crate_band', '#4a2e1c', .8), P['heart_glow'])
    for (x, z, s) in ((-0.55, 1.0, 1.0), (0.6, 0.9, 0.9), (0.0, 1.75, 0.8)):
        crates.box((s + 0.1, s + 0.1, 0.14), (x, 0, z + 0.02), SN, bevel=0.06)
    tun = tunnel_gate('sf_tunnel_gate', mat('tunnel_stone', '#8a84a0', .85), mat('tunnel_stone_dark', '#6c6680', .85), mat('tunnel_dark', '#07070b', 1), SN)
    for k in range(30):
        a = math.radians(k * 180 / 29)
        tun.sphere(0.12, (5.8 * math.cos(a), -2.3, 3.0 + 5.8 * math.sin(a)), BULBS[k % 2], seg=8, rings=5)
    heart(tun, (0, -2.4, 9.6), 1.4, 0.2, P['heart_glow'])
    parts = [
        trk4,
        *houses,
        deco_tree('sf_christmas_tree', P['bark'], mat('pine', '#1f6a4e', .8), SN, BULBS + [P['gold']], P['gold'], h=6.5, seed=1),
        pine('sf_pine_tree', P['bark'], mat('pine_dark', '#1f5a46', .8), SN, h=8, seed=2),
        victorian_lamp('sf_street_lamp', P['metal'], P['warm_glow']),
        string_lights('sf_string_lights', P['metal'], BULBS, P['metal'], span=17, h=6.8, n=30, poles=True),
        fairy_castle('sf_fairy_castle', mat('castle_wall', '#f6e6ff', .7), mat('castle_roof', '#ff7eb6', .6), WIN, P['gold'], snow=SN),
        tun, rock('sf_snow_pile', [SN, SN2], size=1.2, seed=4),
        tr, ramp('sf_ramp', mat('train_under2', '#2a2d33', .7), mat('ramp_pink', '#ff7eb6', .5), SN),
        snowman('sf_obstacle_snowman', SN, mat('coal', '#111111', .6), mat('carrot', '#ff7a1a', .6), mat('scarf', '#ff4f9a', .8), mat('hat_red', '#c8304a', .7)),
        snow_fence('sf_obstacle_fence', mat('wood_fence', '#6b4426', .85), SN, mat('fence_pink', '#ff6fa8', .7)),
        crates,
    ] + pickups('sf', P, P['gold'], mat('coin_rose_rim', '#ff9cc6', .3, metal=.7), mat('sf_coin_heart', '#ff4f9a', .3, emit=1.2),
                [bubble_pu('sf_powerup_bubble', mat('snow_bubble_glass', '#e6f6ff', .05, alpha=.3), mat('bubble_heart', '#ff4f9a', .3, emit=2))])
    cfg = dict(
        camera=CAM,
        segment='sf_track_segment', seg_range=(-2, 6),
        world=dict(haze=0.3, top='#2a2470', hor='#8a6ac8', strength=0.9, sun=(1.3, '#d8c8ff', (60, 0, 30)), clouds=False),
        ground=dict(hex='#eeeaff', z=0.0),
        rows=[dict(names=['sf_house_a', 'sf_house_b', 'sf_house_c'], x=10.6, y=(-12, 56), step=8.6)],
        repeat=[('sf_street_lamp', 2, [(-6.0, 3, 0.65, 0), (6.0, 13, 0.65, 0)]), ('sf_string_lights', 2, [(0, 8, 0, 0)])],
        lamp_lights=('sf_street_lamp', (0, 0, 4.0), 260, '#ffb8d0'),
        scatter=[dict(names=['sf_pine_tree', 'sf_christmas_tree'], n=16, x=(16, 28), y=(-10, 80), s=(0.9, 1.4)),
                 dict(names=['sf_snow_pile'], n=10, x=(6.5, 9), y=(-10, 75), s=(0.7, 1.2), z=0.4)],
        fixed=[('sf_tunnel_gate', (0, 58, 0), 0, 1.1), ('sf_fairy_castle', (0, 130, 14), 0, 1.45),
               ('sf_christmas_tree', (-8.0, 52, 0.65), 0, 1.4), ('sf_christmas_tree', (8.0, 52, 0.65), 0, 1.4)],
        lights=[('POINT', (0, 40, 8), 800, '#ff9ccf'), ('POINT', (0, 0, 7), 500, '#ffd6a0')],
        obstacles=[('sf_obstacle_fence', 0, 15), ('sf_train', 1, 30), ('sf_obstacle_snowman', -1, 24),
                   ('sf_obstacle_snowy_crates', 0, 40), ('sf_train', -1, 55), ('sf_ramp', -1, 46)],
        powerups=[('sf_powerup_bubble', 1, 18), ('sf_powerup_heart', 0, 30)],
        coins=[(0, 3, 7), (-1, 10, 7), (0, 46, 6)], coin_arcs=[(0, 15, 7)],
        edge=[dict(names=['sf_christmas_tree', 'sf_snow_pile', 'sf_street_lamp', 'sf_snow_pile'], x=(6.0, 7.0), step=(3, 5), z=0.65, s=(0.8, 1.1))],
        framing=[('sf_christmas_tree', -6.6, 9, 0.65, 0, 1.2), ('sf_street_lamp', 6.0, 6, 0.65, 180, 1.1), ('sf_snow_pile', 6.4, 3, 0.65, 0, 1.4)],
        glow_lights=[('sf_christmas_tree', (0, 0, 3.0), 90, '#ff8fc8'), ('sf_house_a', (3.4, 0, 1.7), 60, '#ffb060'),
                     ('sf_house_b', (3.4, 0, 1.7), 60, '#ffb060'), ('sf_house_c', (3.4, 0, 1.7), 60, '#ffb060')],
        snowfall=True, coin='sf_coin', surface=0.56,
    )
    return parts, cfg


# =========================================================================== 5 Romantic Neon City
def map5():
    P = palette()
    BED, SL, RA = mat('wet_ballast', '#2a1a40', .1), mat('sleeper', '#3a2a50', .3), mat('rail_chrome', '#ffd0f0', .1, metal=1)
    SD = mat('wet_sidewalk', '#2e2048', .08)
    NP, NC, NV = mat('neon_pink', '#ff2fd0', .3, emit=14), mat('neon_cyan', '#21e3ff', .3, emit=14), mat('neon_violet', '#a06bff', .3, emit=12)
    WALLS = [mat('wall_night_a', '#2a1d48', .5), mat('wall_night_b', '#1d2244', .5), mat('wall_night_c', '#3a1d48', .5)]
    G1, G2, G3 = mat('win_pink', '#ff6fd8', .3, emit=5), mat('win_cyan', '#46e8ff', .3, emit=5), mat('win_warm', '#ffb35a', .3, emit=4)
    trk5 = track_segment('rn_track_segment', BED, SL, RA, SD, edge=NP)
    sparkle_field(trk5, [NP, NC], seed=5)
    blds = []
    for i, c in enumerate('abc'):
        b = neon_building('rn_building_' + c, 8, 6, 9 + i * 3, WALLS[i], [G1, G2, G3], mat('win_off', '#120c1e', .2),
                          [NP, NC, NV][i], [NC, NP, NP][i], seed=i)
        heart_outline(b, (3.15, 1.5, 8 + i * 2), 2.0, 0.06, [NP, NC, NP][i], rot=(0, 0, 90))
        blds.append(b)
    TB, TS = mat('train_lilac', '#6a4ab8', .25, metal=.4), mat('train_neon_pink', '#ff2fd0', .3, emit=8)
    ft = train('rn_future_train', TB, TS, mat('train_roof', '#3a3060', .4, metal=.5), mat('train_window_glow', '#7af0ff', .2, emit=4),
               mat('train_light', '#ffffff', .3, emit=14), mat('train_under', '#111218', .6), door=NC, stripe2=NC)
    heart(ft, (0, -6.7, 1.3), 0.6, 0.1, NP)
    holo = Part('rn_holo_hearts', 'prop', ao=False)
    rr = random.Random(2)
    for k in range(6):
        heart_outline(holo, (rr.uniform(-1.5, 1.5), rr.uniform(-1, 1), rr.uniform(0, 2.5)), rr.uniform(0.5, 1.1), 0.03,
                      (NP, NC)[k % 2], rot=(0, 0, rr.uniform(-30, 30)))
    parts = [
        trk5,
        *blds,
        skyscraper('rn_skyscraper', 12, 70, mat('tower_glass', '#1a1440', .12, metal=.5), NP, P['metal'], light=NC),
        skyscraper('rn_skyscraper_cyan', 9, 55, mat('tower_glass2', '#141a40', .12, metal=.5), NC, P['metal'], light=NP),
        neon_arch('rn_neon_arch', NP, NC, mat('arch_frame', '#1a1428', .3, metal=.6), NP),
        neon_heart_sign('rn_heart_sign', mat('sign_frame', '#1a1428', .3, metal=.6), NP, NC),
        holo, catenary('rn_catenary_frame', P['metal'], mat('wire', '#0a0a0a', .5), NP, light=NC),
        palm('rn_palm_tree', mat('palm_bark_night', '#2a2030', .8), mat('palm_bark_night2', '#3a2a40', .8),
             mat('palm_leaf_night', '#14404a', .6), mat('palm_leaf_night2', '#1a4a3a', .6), h=7, seed=4),
        ft, ramp('rn_ramp', mat('ramp_dark', '#1a1428', .4), NC, NP),
        laser_gate('rn_obstacle_laser_low', mat('laser_frame', '#1e1a2a', .3, metal=.7), NP),
        laser_gate('rn_obstacle_laser_high', mat('laser_frame2', '#1e1a2a', .3, metal=.7), NC, high=True),
    ] + pickups('rn', P, P['gold'], NP, NC,
                [magnet('rn_powerup_magnet', mat('magnet_neon', '#ff2fd0', .3, emit=1.5), mat('magnet_steel', '#d8dde5', .25, metal=.9), NC)])
    cfg = dict(
        camera=CAM,
        segment='rn_track_segment', seg_range=(-2, 22), repeat_min_y=8,
        world=dict(haze=0.25, saturation=0.95, contrast=0.0, top='#1a0838', hor='#8a2a8a', strength=0.8, sun=(0.6, '#c49cff', (60, 0, 20))),
        ground=dict(hex='#1e1434', z=-0.02, rough=0.1),
        rows=[dict(names=['rn_building_a', 'rn_building_b', 'rn_building_c'], x=10.4, y=(-15, 220), step=8.2)],
        repeat=[('rn_catenary_frame', 2, [(0, 0, 0, 0)]), ('rn_neon_arch', 2, [(0, 15, 0, 0)]),
                ('rn_heart_sign', 3, [(-6.5, 12, 0.5, 90), (6.5, 27, 0.5, -90)])],
        scatter=[dict(names=['rn_palm_tree'], n=8, x=(6.3, 6.8), y=(-5, 150), s=(0.9, 1.1), z=0.5),
                 dict(names=['rn_holo_hearts'], n=10, x=(5, 9), y=(0, 150), s=(0.8, 1.2), zr=(3, 6))],
        fixed=[('rn_skyscraper', (-28, 240, 0), 0, 1.0), ('rn_skyscraper_cyan', (20, 260, 0), 0, 1.3), ('rn_skyscraper', (2, 320, 0), 0, 1.6)],
        lights=[('POINT', (-5, 10, 4), 700, '#ff3fd5'), ('POINT', (5, 25, 4), 700, '#2fe0ff'), ('POINT', (-5, 45, 4), 700, '#2fe0ff'),
                ('POINT', (5, 60, 4), 700, '#ff3fd5'), ('POINT', (0, -4, 6), 400, '#ffd9f0')],
        obstacles=[('rn_future_train', 1, 40), ('rn_future_train', -1, 28), ('rn_obstacle_laser_low', 0, 16),
                   ('rn_obstacle_laser_high', 1, 22), ('rn_ramp', -1, 18.5), ('rn_obstacle_laser_low', 0, 50)],
        powerups=[('rn_powerup_magnet', 0, 30), ('rn_powerup_heart', 1, 12)],
        coins=[(0, 3, 7), (1, 12, 5)], coin_arcs=[(0, 16, 7), (0, 50, 7)], coins_raised=[(-1, 23, 10, 4.1)],
        edge=[dict(names=['rn_heart_sign', 'rn_palm_tree', 'rn_holo_hearts'], x=(6.0, 6.8), step=(4, 7), z=0.5, spin=False)],
        framing=[('rn_heart_sign', -6.2, 8, 0.5, 90, 1.0), ('rn_palm_tree', 6.5, 6, 0.5, 0, 1.1)],
        glow_lights=[('rn_heart_sign', (0, -0.4, 7.0), 250, '#ff4fd8'), ('rn_neon_arch', (0, 0, 7.5), 400, '#ff4fd8')],
        coin='rn_coin', surface=0.56,
    )
    return parts, cfg


# =========================================================================== 6 Tropical Flower Island
def map6():
    P = palette()
    PL = [mat('plank_a', '#b8844e', .85), mat('plank_b', '#a2703e', .85), mat('plank_c', '#c8965e', .85)]
    BM, PO, RP = mat('beam_dark', '#5a3b20', .9), mat('post_wood', '#7a5530', .85), mat('rope', '#d8b87a', .9)
    br = plank_bridge('tf_bridge_segment', PL, BM, PO, RP)
    for sg in (-1, 1):
        for py in (0.3, SEG / 2 + 0.3):
            for k in range(3):
                hibiscus(br, (sg * 4.4 + (k - 1) * 0.18, py - 0.25, 2.1 + (k % 2) * 0.15), 0.28, (P['pink'], P['pink2'], P['peach'])[k],
                         P['center'], tilt=60, yaw=180)
    SAND, GR = mat('island_sand', '#f2dca8', .9), mat('grass', '#5fbf3a', .8)
    isl = bank('tf_island_bank', SAND, GR)
    flowers_on(isl, (-2, 0, 0.6), 3.5, [P['pink'], P['pink2'], P['peach']], [P['center']], n=16, size=0.35, seed=4, flat=0.15)
    hut = tiki_hut('tf_tiki_hut', mat('hut_post', '#6b4426', .85), mat('thatch', '#d8b06a', .9), mat('thatch_dark', '#b88a4a', .9),
                   mat('hut_floor', '#8a5a34', .85), P['heart_glow'], flowers=([P['pink'], P['pink2']], [P['center']]))
    shells = Part('tf_seashells')
    rr = random.Random(5)
    for k in range(7):
        c = (rr.uniform(-1, 1), rr.uniform(-1, 1), 0.05)
        if k % 3 == 0:
            shells.prism(star_pts(0.22, 0.09), 0.06, c, mat('starfish', '#ff8a6a', .6), rot=(90, 0, rr.uniform(0, 90)))
        else:
            shells.sphere(0.13, c, (P['pink3'], P['cream'])[k % 2], scale=(1, 0.8, 0.45))
    farch = deco_arch('tf_flower_arch', PO, [P['leaf'], P['leaf3']], [P['pink'], P['peach'], P['pink2']], [P['center']], glow=P['heart_glow'], span=9.2)
    lam = heart_lantern('tf_heart_lantern', mat('lantern_bamboo', '#b88a4a', .8), P['heart_glow'], P['glass'], h=2.3)
    fall = waterfall('tf_waterfall', [mat('rock', '#8f8d7a', .85), mat('rock_dark', '#74725f', .85)], mat('waterfall', '#a8f0ff', .1, emit=.8),
                     mat('foam', '#ffffff', .4, emit=.6), h=18, w=5, top=[P['leaf'], P['leaf2'], P['leaf3']])
    flowers_on(fall, (0, 1, 18.5), 4, [P['pink'], P['pink2']], [P['center']], n=14, size=0.5, seed=6)
    bushp = blob_bush('tf_hibiscus_bush', [P['leaf'], P['leaf3']], seed=3, size=1.3)
    flowers_on(bushp, (0, 0, 0.9), 1.15, [P['pink'], P['peach'], P['pink2']], [P['center']], n=14, size=0.38, seed=8)
    perch = Part('tf_parrot_perch')
    perch.cyl(0.08, 2.2, (0, 0, 1.1), PO, seg=8)
    perch.cyl(0.05, 1.0, (0, 0, 2.2), PO, rot=(0, 90, 0), seg=8)

    parts = [
        br, isl, hut, farch, palm('tf_palm_tree', P['bark'], P['bark2'], P['leaf'], P['leaf2'], h=7.5, seed=7),
        fall, cliff('tf_cliff', [mat('cliff_rock', '#8f8d7a', .85), mat('cliff_earth', '#7a5a3e', .9)], w=10, d=8, h=16, seed=3, top=[P['leaf'], P['leaf2'], P['leaf3']]),
        bushp, perch, parrot('tf_parrot', mat('parrot_red', '#e8304a', .5), mat('parrot_blue', '#2f7cf6', .5), mat('parrot_yellow', '#ffd23a', .5), mat('beak', '#2a2a2a', .5)), shells, lam, butterfly_cluster('tf_butterflies', P['wings'], P['metal'], seed=3),
        rock('tf_rock', [mat('shore_rock', '#9a9686', .85)], size=1.1, seed=9, moss=GR),
        heart_crate('tf_obstacle_crate', PL[1], BM, P['heart_glow']),
        log('tf_obstacle_log', P['bark'], mat('log_ring', '#c99a5e', .8), moss=GR),
        Part('tf_obstacle_hanging_garland', 'obstacle_high'),
    ] + pickups('tf', P, P['gold'], P['gold2'], mat('tf_coin_heart', '#ff4f9a', .3, emit=1.2),
                [magnet('tf_powerup_magnet', mat('magnet_red', '#e8314f', .35), mat('magnet_steel', '#d8dde5', .25, metal=.9), P['heart_glow'])])
    hg = next(p for p in parts if p.name == 'tf_obstacle_hanging_garland')
    for x in (-1.25, 1.25):
        hg.cyl(0.18, 3.2, (x, 0, 1.6), PO, seg=8)
    hg.cyl(0.38, 2.7, (0, 0, 2.0), P['bark'], rot=(0, 90, 0), seg=12)
    for k in range(9):
        hibiscus(hg, (-1.0 + k * 0.25, -0.38, 1.8 + 0.08 * math.sin(k)), 0.2, (P['pink'], P['peach'], P['pink2'])[k % 3], P['center'], tilt=90)
    cfg = dict(
        camera=CAM,
        segment='tf_bridge_segment', seg_range=(-2, 16),
        world=dict(haze=0.42, top='#4fb4ff', hor='#e6fbff', strength=1.0, sun=(4.0, '#fff4e0', (50, 0, -35))),
        ground=dict(hex='#2fd6d0', z=-1.4, rough=0.05, name='lagoon_water'),
        rows=[dict(names=['tf_island_bank'], x=11.2, y=(-20, 160), step=24, fixed_rz=True)],
        repeat=[('tf_heart_lantern', 2, [(-5.2, 2, 0, 0), (5.2, 12, 0, 0)]), ('tf_flower_arch', 2, [(0, 22, 0.3, 0)])],
        scatter=[dict(names=['tf_palm_tree', 'tf_palm_tree', 'tf_hibiscus_bush'], n=28, x=(7.4, 14), y=(-10, 140), s=(1.0, 1.4), z=0.5),
                 dict(names=['tf_seashells', 'tf_rock', 'tf_hibiscus_bush'], n=24, x=(7.2, 13), y=(-10, 140), s=(0.9, 1.2), z=0.5),
                 dict(names=['tf_butterflies'], n=8, x=(5.5, 12), y=(0, 120), s=(0.8, 1.2), zr=(2, 4.5))],
        fixed=[('tf_waterfall', (12, 60, -1.4), -15, 1.2), ('tf_waterfall', (-16, 80, -1.4), 10, 1.4), ('tf_cliff', (-14, 50, -1.4), 0, 1.4),
               ('tf_cliff', (16, 85, -1.4), 0, 1.6), ('tf_tiki_hut', (-9.6, 20, 0.5), 20, 1.0), ('tf_tiki_hut', (9.6, 40, 0.5), -30, 1.0),
               ('tf_parrot_perch', (-10.5, 25, 0.5), 0, 1.0), ('tf_parrot_perch', (10.5, 48, 0.5), 0, 1.0),
               ('tf_parrot', (-10.5, 25, 2.75), 90, 1.4), ('tf_parrot', (10.5, 48, 2.75), -90, 1.4)],
        obstacles=[('tf_obstacle_log', 0, 14), ('tf_obstacle_crate', 1, 22), ('tf_obstacle_hanging_garland', -1, 30),
                   ('tf_obstacle_log', 1, 40), ('tf_obstacle_crate', -1, 48), ('tf_obstacle_hanging_garland', 0, 58)],
        powerups=[('tf_powerup_magnet', 0, 24), ('tf_powerup_heart', 1, 50)],
        coins=[(0, 2, 7), (-1, 12, 8), (1, 28, 6)], coin_arcs=[(0, 14, 7), (1, 40, 7)],
        framing=[('tf_hibiscus_bush', -7.4, 6, 0.5, 0, 1.6), ('tf_palm_tree', 7.6, 9, 0.5, 0, 1.2)],
        glow_lights=[('tf_heart_lantern', (0, 0, 2.65), 70, '#ff6fb0')],
        coin='tf_coin', surface=0.32,
    )
    return parts, cfg


# =========================================================================== 7 Red Canyon Railway
def map7():
    P = palette()
    BED, SL, RA = mat('red_dirt', '#9a4a2e', .95), mat('sleeper', '#4e3220', .9), mat('rail', '#b9b0b0', .3, metal=.9)
    R = [mat('rock_red', '#b8502e', .9), mat('rock_orange', '#d8703a', .9), mat('rock_dark', '#8a3a24', .9), mat('rock_sand', '#e89a5a', .9)]
    W1, W2 = mat('timber', '#6b4426', .85), mat('timber_dark', '#4a2e18', .85)
    TB, TS = mat('train_red', '#d8364a', .45), mat('train_cream', '#f8e8d0', .5)
    trk7 = track_segment('rr_track_segment', BED, SL, RA, mat('canyon_ground', '#b86038', .95))
    sparkle_field(trk7, [P['warm_glow'], mat('sparkle_gold', '#ffd36a', .3, emit=6)], seed=7)
    tr = train('rr_train', TB, TS, mat('train_roof', '#5a5a60', .5, metal=.4), mat('train_window', '#2a1e2a', .1),
               mat('train_light', '#fff2c0', .3, emit=8), mat('train_under', '#2a2a2e', .7), stripe2=P['gold'])
    heart(tr, (0, -6.12, 1.3), 0.7, 0.1, P['heart_glow'])
    garland = string_lights('rr_lantern_garland', mat('garland_wire', '#2a1a12', .6), [P['warm_glow'], P['heart_glow']], mat('garland_pole', '#4a2e18', .85), span=15.5, h=7.0, n=24)
    cac = cactus('rr_cactus', mat('cactus', '#5a9a44', .7), mat('cactus_dark', '#4a843a', .7), P['pink'])
    for (x, z) in ((-0.9, 2.65), (0.9, 2.85)):
        hibiscus(cac, (x, 0, z), 0.2, P['pink2'], P['center'], tilt=0)
    balloons = [hot_air_balloon('rr_balloon_%s' % c, mats, mat('basket', '#8a5a34', .8), mat('balloon_rope', '#5a4030', .8), seed=i)
                for i, (c, mats) in enumerate((('a', [mat('bal_pink', '#ff7eb6', .5), mat('bal_cream', '#fff0dc', .5)]),
                                                ('b', [mat('bal_lav', '#b89cff', .5), mat('bal_peach', '#ffb38a', .5), mat('bal_gold', '#ffd36a', .5)])))]
    lan = heart_lantern('rr_lantern_post', W2, P['warm_glow'], P['glass'], h=2.4, base=W1)
    parts = [
        trk7,
        mesa('rr_mesa_a', R, w=14, h=28, seed=1), mesa('rr_mesa_b', [R[1], R[3], R[0]], w=9, h=18, seed=2),
        cliff('rr_cliff_wall', R, w=12, d=10, h=22, seed=4, shrink=0.15, layer=2.2),
        canyon_arch('rr_rock_arch', R, seed=3),
        trestle('rr_trestle_bridge', W1, W2, RA),
        *balloons, garland, cac, rock('rr_rock', R[:3], size=1.3, seed=5), lan,
        tr, ramp('rr_ramp', W2, mat('ramp_red', '#d8364a', .5), mat('ramp_cream', '#f8e8d0', .6)),
        mine_cart('rr_obstacle_mine_cart', mat('cart_metal', '#5a5a62', .45, metal=.7), W1, mat('gold_ore', '#ffcf3a', .3, metal=.9), mat('cart_under', '#2a2a2e', .7)),
        heart_crate('rr_obstacle_crate', mat('crate_wood', '#a0683a', .8), W2, mat('crate_heart', '#d8364a', .5)),
        barrier_high('rr_obstacle_wood_high', W2, W1, mat('barrier_red', '#d8364a', .6), sign=TS),
    ] + pickups('rr', P, P['gold'], P['gold2'], mat('rr_coin_heart', '#d8364a', .3, emit=0.8),
                [flame_pu('rr_powerup_flame', P['fire'], P['fire2'], P['gold'])])
    cfg = dict(
        camera=CAM,
        segment='rr_track_segment', seg_range=(-2, 22),
        world=dict(haze=0.22, saturation=0.92, contrast=0.0, top='#5a3a8a', hor='#ff9a5a', strength=1.0, sun=(3.5, '#ffb070', (78, 0, 180)), clouds=True),
        ground=dict(hex='#b8603a', z=-0.02),
        repeat=[('rr_lantern_post', 2, [(-5.6, 4, 0.5, 0), (5.6, 14, 0.5, 0)]), ('rr_lantern_garland', 3, [(0, 12, 0, 0)])],
        scatter=[dict(names=['rr_cactus', 'rr_rock'], n=16, x=(6.5, 14), y=(-10, 150), s=(0.8, 1.3)),
                 dict(names=['rr_balloon_a', 'rr_balloon_b'], n=8, x=(15, 40), y=(30, 220), s=(0.8, 1.4), zr=(12, 30)),
                 dict(names=['rr_mesa_b'], n=6, x=(25, 45), y=(20, 200), s=(0.8, 1.4))],
        rows=[dict(names=['rr_cliff_wall'], x=13.5, y=(-15, 220), step=11)],
        fixed=[('rr_rock_arch', (0, 70, 0), 0, 1.15), ('rr_mesa_a', (-40, 160, 0), 0, 1.4), ('rr_mesa_a', (-20, 260, 0), 30, 2.0),
               ('rr_trestle_bridge', (-16, 60, -12), 90, 1.0)],
        obstacles=[('rr_train', 1, 30), ('rr_ramp', 1, 21), ('rr_obstacle_mine_cart', 0, 15), ('rr_obstacle_wood_high', -1, 25),
                   ('rr_obstacle_crate', 0, 40), ('rr_train', -1, 55)],
        powerups=[('rr_powerup_flame', -1, 12), ('rr_powerup_heart', 0, 26)],
        coins=[(0, 3, 6), (-1, 14, 5)], coin_arcs=[(0, 15, 7), (0, 40, 7)], coins_raised=[(1, 25.5, 10, 4.1)],
        edge=[dict(names=['rr_cactus', 'rr_rock', 'rr_lantern_post'], x=(5.8, 7.0), step=(3, 5), z=0.5, s=(0.9, 1.2))],
        framing=[('rr_lantern_post', -5.8, 7, 0.5, 0, 1.2), ('rr_cactus', 6.4, 9, 0.5, 0, 1.3)],
        glow_lights=[('rr_lantern_post', (0, 0, 2.75), 90, '#ffb060')],
        coin='rr_coin', surface=0.56,
    )
    return parts, cfg


# =========================================================================== 8 Cherry Blossom Kingdom
def map8():
    P = palette()
    S = [mat('path_stone_a', '#e8d2d2', .85), mat('path_stone_b', '#d6c0c4', .85), mat('path_stone_c', '#f2e2e0', .85)]
    G, WL = mat('grout', '#a08a8a', .9), mat('wall_stone', '#b8a8a8', .85)
    PK = [mat('blossom_pink', '#ffa6cf', .7), mat('blossom_light', '#ffc9e3', .7), mat('blossom_deep', '#f27bb4', .7)]
    TRD, TBK = mat('torii_red', '#e8372b', .6), mat('torii_black', '#1c1c1c', .6)
    GLOW = mat('lantern_glow', '#ffd27a', .4, emit=6)
    pal = pagoda('cb_palace', mat('pagoda_wall', '#fff0f4', .7), mat('pagoda_roof', '#ff7eb6', .6), mat('pagoda_trim', '#5a2a3a', .7), P['gold'], WL)
    paper = Part('cb_paper_lantern')
    paper.cyl(0.06, 2.6, (0, 0, 1.3), TBK, seg=8)
    paper.rod((0, 0, 2.55), (0.6, 0, 2.55), 0.04, TBK, seg=6)
    paper.sphere(0.32, (0.6, 0, 2.05), mat('paper_red', '#ff4a4a', .6, emit=2.5), scale=(1, 1, 1.25))
    for z in (2.42, 1.68):
        paper.cyl(0.18, 0.06, (0.6, 0, z), TBK, seg=10)
    blossom_wall = low_wall('cb_obstacle_flower_wall', WL, S[0], petals=PK[0])
    flowers_on(blossom_wall, (0, 0, 1.05), 0.9, PK, [P['center']], n=10, size=0.28, seed=4, flat=0.3)
    parts = [
        stone_path('cb_path_segment', S, G, WL, moss=mat('moss', '#8ab85a', .8), wall_h=0.9, seed=31, petals=PK, tile=(0.45, 0.8)),
        deco_arch('cb_blossom_arch', mat('arch_wood', '#5a2a2a', .8), PK, None, [P['center']], glow=GLOW, flowers=False),
        cherry_tree('cb_cherry_tree_a', mat('cherry_bark', '#4a2e2a', .9), PK, seed=1),
        cherry_tree('cb_cherry_tree_b', mat('cherry_bark', '#4a2e2a', .9), [PK[1], PK[0]], seed=2, h=4.5),
        stone_lantern('cb_stone_lantern', S[1], G, GLOW), paper, pal,
        torii('cb_torii_gate', TRD, TBK, w=9.5, h=8.0, kind='landmark', nuki=6.2),
        koi_pond('cb_koi_pond', mat('pond_water', '#5ac8d8', .05), S[1], WL, mat('koi_orange', '#ff7a2a', .5), mat('koi_white', '#fff4ec', .5),
                 mat('lily_pad', '#4f9a3a', .6), PK[0]),
        blob_bush('cb_azalea_bush', [mat('hedge', '#5f9a44', .85), mat('hedge2', '#7ab85a', .85)], seed=3, size=1.1, flower=PK[2]),
        rock('cb_garden_rock', [S[1], WL], size=0.9, seed=4, moss=mat('moss2', '#8ab85a', .8)),
        blossom_wall, torii('cb_obstacle_torii', TRD, TBK),
        stone_block('cb_obstacle_lantern_block', S[1], G, size=(2.3, 1.2, 1.0)),
    ] + pickups('cb', P, P['gold'], mat('coin_rose_rim', '#ff8cc6', .3, metal=.6), mat('cb_coin_heart', '#ff4f9a', .3, emit=1.2),
                [wings_pu('cb_powerup_wings', P['white'], P['gold'], mat('wing_heart', '#ff4f9a', .3, emit=1.5))])
    cfg = dict(
        camera=CAM,
        segment='cb_path_segment', seg_range=(-2, 10),
        world=dict(haze=0.42, top='#9ac8ff', hor='#ffd6ec', strength=0.95, sun=(3.0, '#fff0f4', (50, 0, 30))),
        ground=dict(hex='#8ac06a', z=0.0),
        repeat=[('cb_stone_lantern', 2, [(-4.65, 1.67, 0.3, 0), (4.65, 11.67, 0.3, 0)]), ('cb_paper_lantern', 2, [(-5.6, 7, 0, 0), (5.6, 17, 0, 180)]), ('cb_blossom_arch', 3, [(0, 33, 0, 0)])],
        lamp_lights=('cb_stone_lantern', (0, 0, 2.6), 40, '#ffc46b'),
        scatter=[dict(names=['cb_cherry_tree_a', 'cb_cherry_tree_b'], n=32, x=(6.6, 12), y=(-10, 100), s=(1.0, 1.4)),
                 dict(names=['cb_azalea_bush', 'cb_garden_rock'], n=18, x=(5.8, 13), y=(-10, 130), s=(0.8, 1.2))],
        fixed=[('cb_palace', (0, 95, 0), 0, 2.2), ('cb_torii_gate', (0, 40, 0.3), 0, 1.0), ('cb_torii_gate', (0, 70, 0.3), 0, 1.0),
               ('cb_koi_pond', (-9.6, 20, 0.02), 0, 1.0), ('cb_koi_pond', (9.6, 45, 0.02), 40, 1.1)],
        obstacles=[('cb_obstacle_flower_wall', 0, 14), ('cb_obstacle_torii', 1, 22), ('cb_obstacle_lantern_block', -1, 30),
                   ('cb_obstacle_torii', 0, 42), ('cb_obstacle_flower_wall', 1, 50)],
        powerups=[('cb_powerup_wings', -1, 20), ('cb_powerup_heart', 1, 36)],
        coins=[(0, 3, 7), (-1, 10, 6), (1, 28, 7)], coin_arcs=[(0, 14, 7), (1, 50, 7)],
        edge=[dict(names=['cb_azalea_bush', 'cb_paper_lantern', 'cb_garden_rock', 'cb_azalea_bush'], x=(5.5, 6.6), step=(2, 3.5), s=(0.9, 1.3))],
        framing=[('cb_cherry_tree_a', -7.2, 7, 0, 0, 1.4), ('cb_cherry_tree_a', 7.4, 10, 0, 90, 1.3), ('cb_paper_lantern', 5.7, 4, 0, 180, 1.2)],
        glow_lights=[('cb_stone_lantern', (0, 0, 2.2), 50, '#ffc070'), ('cb_paper_lantern', (0.6, 0, 2.0), 60, '#ff6a5a')],
        coin='cb_coin', surface=0.44,
    )
    return parts, cfg


# =========================================================================== 9 Magical Underwater Railway
def map9():
    P = palette()
    BED, SL, RA = mat('tunnel_floor', '#24589a', .4), mat('sleeper_blue', '#2c6fa8', .5), mat('rail', '#d8e6f6', .25, metal=.9)
    FR = mat('tunnel_frame', '#3a5a8a', .3, metal=.7)
    trk9 = track_segment('mu_track_segment', BED, SL, RA, mat('tunnel_side', '#2a6090', .5), side_w=1.8)
    sparkle_field(trk9, [mat('sparkle_pink', '#ff8fd8', .3, emit=6), mat('sparkle_cyan', '#7ff0ff', .3, emit=6)], seed=9)
    tun = glass_tunnel('mu_glass_tunnel_segment', FR, mat('tunnel_glass', '#c8f0ff', .05, alpha=.16), mat('tunnel_base', '#1c3c68', .5, metal=.4))
    for y in (0.2, SEG / 2 + 0.2):
        for k in range(13):
            a = math.radians(8 + k * 164 / 12)
            tun.sphere(0.09, (6.15 * math.cos(a), y - 0.25, 0.5 + 6.15 * math.sin(a)), (P['heart_glow'], mat('bulb_cyan', '#5ae8ff', .3, emit=6))[k % 2], seg=8, rings=5)
    C = [mat('coral_pink', '#ff5fa2', .6, emit=.8), mat('coral_purple', '#b05cff', .6, emit=.8), mat('coral_peach', '#ff9a6a', .6, emit=.6),
         mat('coral_yellow', '#ffd23a', .6, emit=.5)]
    TB, TS = mat('train_red', '#d8364a', .45), mat('train_cream', '#f8e8d0', .5)
    tr = train('mu_train', TB, TS, mat('train_roof', '#5a5a70', .5, metal=.4), mat('train_window', '#2a6a9a', .1, emit=1),
               mat('train_light', '#fff2c0', .3, emit=10), mat('train_under', '#2a2a2e', .7), stripe2=P['gold'])
    heart(tr, (0, -6.12, 1.3), 0.7, 0.1, P['heart_glow'])
    GLASS = mat('bubble_glass', '#dff6ff', .05, alpha=.3)
    parts = [
        trk9, tun,
        jellyfish('mu_jellyfish_pink', mat('jelly_pink', '#ff8fd0', .2, emit=2.5, alpha=.6), mat('jelly_pink_core', '#ff5fb8', .3, emit=4),
                  mat('jelly_tentacle', '#ffb8e8', .3, emit=2), seed=1),
        jellyfish('mu_jellyfish_blue', mat('jelly_blue', '#8fe8ff', .2, emit=2.5, alpha=.6), mat('jelly_blue_core', '#5ad8ff', .3, emit=4),
                  mat('jelly_tentacle_b', '#c8f4ff', .3, emit=2), seed=2, size=0.8),
        coral_branch('mu_coral_branch_a', [C[0], C[2]], seed=1), coral_branch('mu_coral_branch_b', [C[1], C[3]], seed=2),
        coral_fan('mu_coral_fan', C[0], C[1], seed=3), seaweed('mu_seaweed', mat('seaweed', '#2fbf8a', .7), mat('seaweed_dark', '#1f8f70', .7), seed=4),
        fish_school('mu_fish_school', [mat('fish_pink', '#ff7eb6', .5), mat('fish_yellow', '#ffd23a', .5), mat('fish_cyan', '#3ad8ff', .5)]),
        bubbles('mu_bubbles', GLASS), rock('mu_sea_rock', [mat('sea_rock', '#3a5a82', .9), mat('sea_rock_dark', '#2a4766', .9)], size=1.6, seed=5),
        tr, ramp('mu_ramp', mat('ramp_dark', '#1c2c48', .6), mat('ramp_pink', '#ff5fa2', .5), mat('ramp_cyan', '#5ae8ff', .5)),
        heart_crate('mu_obstacle_crate', mat('crate_wood_wet', '#7a5a42', .7), mat('crate_band', '#3a2a20', .7), P['heart_glow']),
        sea_mine('mu_obstacle_sea_mine', mat('mine_metal', '#3a4a5a', .35, metal=.8), mat('mine_spike', '#8a9aaa', .3, metal=.9),
                 mat('mine_base', '#2a3a4a', .6), mat('mine_glow', '#ff3a6a', .3, emit=6)),
        chest('mu_obstacle_treasure_chest', mat('chest_wood', '#7a4a26', .8), P['gold'], mat('dark', '#111111', .8)),
        barrier_high('mu_obstacle_pipe_gate', FR, mat('pipe_pink', '#ff5fa2', .5), mat('pipe_white', '#f4f8ff', .5), light=P['heart_glow']),
    ] + pickups('mu', P, P['gold'], mat('coin_aqua_rim', '#5ae8ff', .25, metal=.8, emit=1), mat('mu_coin_heart', '#ff5fa2', .3, emit=1.2),
                [bubble_pu('mu_powerup_bubble', GLASS, mat('bubble_heart', '#ff4f9a', .3, emit=2))])
    cfg = dict(
        camera=CAM,
        segment='mu_track_segment', seg_range=(-2, 18),
        repeat=[('mu_glass_tunnel_segment', 1, [(0, 0, 0, 0)])],
        world=dict(haze=0.6, haze_hex='#2bb8e8', haze_start=6, haze_depth=80, top='#0a3a8a', hor='#3ab8f0', strength=1.0, sun=(3.0, '#c8f0ff', (20, 0, 10))),
        ground=dict(hex='#d8c49a', z=-0.4),
        scatter=[dict(names=['mu_coral_branch_a', 'mu_coral_branch_b', 'mu_coral_fan', 'mu_seaweed'], n=56, x=(7.0, 12), y=(-10, 160), s=(0.8, 1.5), z=-0.4),
                 dict(names=['mu_sea_rock'], n=10, x=(9, 22), y=(-10, 160), s=(0.8, 1.6), z=-0.4),
                 dict(names=['mu_jellyfish_pink', 'mu_jellyfish_blue'], n=26, x=(7.2, 12), y=(0, 120), s=(0.9, 1.6), zr=(3, 8)),
                 dict(names=['mu_fish_school', 'mu_bubbles'], n=12, x=(8, 20), y=(0, 120), s=(0.8, 1.3), zr=(2, 8))],
        lights=[('POINT', (0, 10, 5), 350, '#ff8fd0'), ('POINT', (0, 35, 5), 350, '#7fe0ff')],
        obstacles=[('mu_train', 1, 34), ('mu_ramp', 1, 25), ('mu_obstacle_treasure_chest', 0, 15), ('mu_obstacle_pipe_gate', -1, 24),
                   ('mu_obstacle_sea_mine', 0, 44), ('mu_obstacle_crate', -1, 52), ('mu_train', -1, 64)],
        powerups=[('mu_powerup_bubble', 0, 30), ('mu_powerup_heart', 1, 48)],
        coins=[(0, 3, 6), (-1, 16, 4)], coin_arcs=[(0, 15, 7), (0, 44, 7)], coins_raised=[(1, 29.5, 10, 4.1)],
        glow_lights=[('mu_jellyfish_pink', (0, 0, 0), 120, '#ff6fd0'), ('mu_jellyfish_blue', (0, 0, 0), 120, '#6fe0ff')],
        coin='mu_coin', surface=0.56,
    )
    return parts, cfg


# =========================================================================== 10 Heavenly Sky Temple
def map10():
    P = palette()
    S = [mat('marble_a', '#eee2dc', .35), mat('marble_b', '#e0d0cc', .35), mat('marble_c', '#f6ece6', .35)]
    G, WL, WL2 = mat('marble_grout', '#c8b4ac', .5), mat('marble_wall', '#ece0da', .4), mat('marble_dark', '#d4c2ba', .45)
    seg = stone_path('hs_bridge_segment', S, G, WL, trim=P['gold'], wall_h=1.0, seed=41, under=WL2, cap=WL2, post_every=2, tile=(0.5, 0.85))
    for k in range(2):
        for sg in (-1, 1):
            y = (k + 0.5) * SEG / 2
            seg.cyl(0.35, 0.35, (sg * 4.85, y, 2.2), P['gold2'], seg=12, r2=0.42)
            flowers_on(seg, (sg * 4.85, y, 2.45), 0.35, [P['pink'], P['pink2'], P['lav']], [P['center']], n=6, size=0.22, seed=k * 3 + sg)
    isl_a = floating_island('hs_floating_island_a', mat('island_rock', '#c8b8b0', .9), mat('island_rock_dark', '#a8968e', .9), mat('island_grass', '#8ad86a', .8), seed=1, R=4.0)
    isl_a.canopy((0.5, 0.5, 3.2), 1.8, [P['pink2'], P['pink3'], P['pink']], seed=5, blobs=3, cards=30, card_size=0.35)
    isl_a.cyl(0.18, 2.4, (0.5, 0.5, 1.4), P['bark'], seg=8)
    flowers_on(isl_a, (-1.5, -1, 0.45), 1.5, [P['pink'], P['lav']], [P['center']], n=8, size=0.3, seed=7, flat=0.2)
    isl_b = floating_island('hs_floating_island_b', mat('island_rock', '#c8b8b0', .9), mat('island_rock_dark', '#a8968e', .9), mat('island_grass', '#8ad86a', .8), seed=2, R=2.5)
    flowers_on(isl_b, (0, 0, 0.45), 1.5, [P['pink'], P['pink2']], [P['center']], n=8, size=0.3, seed=9, flat=0.2)
    harch = deco_arch('hs_flower_arch', P['gold'], [P['pink3'], P['white']], [P['pink'], P['pink2'], P['lav']], [P['center']], glow=P['heart_glow'], span=9.4)
    garden = blob_bush('hs_flower_garden', [P['leaf2'], P['leaf']], seed=6, size=1.2)
    flowers_on(garden, (0, 0, 0.9), 1.1, [P['pink'], P['pink2'], P['lav'], P['pink3']], [P['center']], n=16, size=0.32, seed=10)
    CL, CL2 = mat('cloud', '#ffffff', .9, emit=.3), mat('cloud_pink', '#ffe6f2', .9, emit=.3)
    parts = [
        seg, heaven_gate('hs_heaven_gate', WL, S[2], P['gold'], mat('crystal', '#ff9cd8', .1, emit=5), mat('portal_glow', '#fff0fa', .3, emit=3, alpha=.6), P['heart_glow']),
        angel_statue('hs_angel_statue', S[2], P['gold']),
        pillar('hs_marble_pillar', S[0], WL2, P['gold']), pillar('hs_marble_pillar_broken', S[0], WL2, P['gold'], broken=True, seed=3),
        isl_a, isl_b, garden, harch, cloud('hs_cloud_a', CL, CL2, seed=1, size=3.5), cloud('hs_cloud_b', CL2, CL, seed=2, size=2.2),
        butterfly_cluster('hs_butterflies', P['wings'], P['gold'], seed=5),
        fallen_column('hs_obstacle_fallen_column', S[0], WL2, P['gold']),
        beam_gate('hs_obstacle_arch', WL, S[2], deco=P['gold'], round_top=True),
        crystal_rock('hs_obstacle_crystal', mat('crystal_base', '#e8dce8', .6), mat('crystal_pink', '#ff9cd8', .1, emit=4)),
    ] + pickups('hs', P, P['gold'], P['gold2'], mat('hs_coin_heart', '#ff7eb6', .3, emit=1.2),
                [shield('hs_powerup_shield', mat('shield_sky', '#5aa8ff', .3, emit=0.6), P['gold'], P['white'])])
    cfg = dict(
        camera=CAM,
        segment='hs_bridge_segment', seg_range=(-2, 6),
        world=dict(haze=0.35, haze_hex='#ffe6f4', top='#7ab4ff', hor='#ffe6f4', strength=0.7, sun=(2.2, '#fff0e0', (50, 0, 30))),
        repeat=[('hs_marble_pillar', 2, [(-6.0, 2.5, 0, 0), (6.0, 12.5, 0, 0)]), ('hs_flower_arch', 2, [(0, 42, 0, 0)])],
        fixed=[('hs_heaven_gate', (0, 56, 0), 0, 1.25), ('hs_angel_statue', (-6.8, 48, 0), 20, 1.4), ('hs_angel_statue', (6.8, 48, 0), -20, 1.4),
               ('hs_floating_island_a', (-11, 38, 7), 0, 1.4), ('hs_floating_island_a', (14, 60, 12), 40, 2.0),
               ('hs_floating_island_b', (10, 24, 8), 0, 1.2), ('hs_floating_island_b', (-9, 14, 10), 0, 1.0),
               ('hs_floating_island_a', (18, 30, 3), 0, 1.0), ('hs_marble_pillar_broken', (-8, 58, 0), 0, 1.5)],
        scatter=[dict(names=['hs_cloud_a', 'hs_cloud_b'], n=40, x=(7, 40), y=(-10, 120), s=(1.0, 3.0), z=-8),
                 dict(names=['hs_cloud_a', 'hs_cloud_b'], n=10, x=(15, 60), y=(20, 160), s=(1.0, 2.0), z=8),
                 dict(names=['hs_butterflies'], n=6, x=(5.5, 9), y=(0, 60), s=(0.8, 1.2), zr=(2, 4))],
        obstacles=[('hs_obstacle_fallen_column', 0, 14), ('hs_obstacle_arch', 1, 22), ('hs_obstacle_crystal', -1, 30),
                   ('hs_obstacle_arch', 0, 42), ('hs_obstacle_fallen_column', 1, 50)],
        powerups=[('hs_powerup_shield', -1, 20), ('hs_powerup_heart', 0, 34)],
        coins=[(0, 2, 7), (-1, 10, 6), (1, 28, 7)], coin_arcs=[(0, 14, 7), (1, 50, 7)],
        coin='hs_coin', surface=0.44,
    )
    return parts, cfg


MAPS = [
    (1, 'enchanted_jungle_temple', 'Enchanted Jungle Temple', map1),
    (2, 'romantic_city_subway', 'Romantic City Subway', map2),
    (3, 'sunset_desert_kingdom', 'Sunset Desert Kingdom', map3),
    (4, 'snowy_fairytale_railway', 'Snowy Fairytale Railway', map4),
    (5, 'romantic_neon_city', 'Romantic Neon City', map5),
    (6, 'tropical_flower_island', 'Tropical Flower Island', map6),
    (7, 'red_canyon_railway', 'Red Canyon Railway', map7),
    (8, 'cherry_blossom_kingdom', 'Cherry Blossom Kingdom', map8),
    (9, 'magical_underwater_railway', 'Magical Underwater Railway', map9),
    (10, 'heavenly_sky_temple', 'Heavenly Sky Temple', map10),
]
