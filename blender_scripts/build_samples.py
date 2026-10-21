"""Build one long sample level per map using every element of that map.

    blender -b --factory-startup --python build_samples.py -- all      (or: -- 3 5)

Output: <root>/sample_mapN/
    sample_mapN.blend    the level (Scene_Layout) + all source assets (Assets)
    sample_mapN.glb/.fbx the whole level as one file
    level.json           every placement (asset, position, rotation, scale) to rebuild it in an engine
    preview.png          runner's-eye view
    overview.png         aerial view of the level
"""
import bpy, sys, os, math, json, random, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import importlib, lib, build_maps
for mod in (lib, build_maps):
    importlib.reload(mod)
from lib import *
from build_maps import Layout, lane_x, setup_world, add_light, setup_camera, setup_render, gallery_pos, log, ROOT, gltf_export, MAPS, dress, glow_lights

NSEG = 30                 # 30 x 10 m = 300 m of running
LEVEL_LEN = NSEG * SEG


def obstacle_course(L, A, kinds, cfg, r):
    surf = cfg.get('surface', 0.5)
    coin = cfg['coin']
    cz = surf + 0.75
    lows, highs = kinds.get('obstacle_low', []), kinds.get('obstacle_high', [])
    trains, ramps = kinds.get('obstacle_train', []), kinds.get('ramp', [])
    pups = kinds.get('powerup', [])
    counters = {}

    def pick(lst):
        i = counters.get(id(lst), 0)
        counters[id(lst)] = i + 1
        return lst[i % len(lst)]

    def place(name, lane, y):
        dz = -0.1 if A[name]['asset_kind'] in ('obstacle_train', 'ramp') else -0.02
        L.put(name, (lane_x(lane), y, surf + dz))

    def coin_line(lane, y0, n, z=cz):
        for k in range(n):
            L.put(coin, (lane_x(lane), y0 + k * 1.6, z))

    def coin_arc(lane, yc):
        for k in range(7):
            t = k / 6
            L.put(coin, (lane_x(lane), yc - 4.5 + 9 * t, cz + 2.2 * math.sin(math.pi * t)))

    coin_line(0, 4, 8)
    for k, name in enumerate(pups):
        L.put(name, (lane_x((-1, 1)[k % 2]), 10 + k * 4, cz + 0.35))
    y = 26.0
    end = LEVEL_LEN - 22
    while y < end:
        lanes = [-1, 0, 1]
        r.shuffle(lanes)
        pats = ['low', 'low_high', 'double']
        if trains:
            pats += ['train', 'train', 'train_pair']
        pat = r.choice(pats)
        step = r.uniform(15, 20)
        if pat == 'low':
            a = lanes[0]
            place(pick(lows), a, y)
            coin_arc(a, y)
            coin_line(lanes[1], y - 5, 6)
            if pups:
                L.put(pick(pups), (lane_x(lanes[2]), y, cz + 0.35))
        elif pat == 'low_high':
            a, b, free = lanes
            place(pick(lows), a, y)
            place(pick(highs) if highs else pick(lows), b, y)
            coin_arc(a, y)
            coin_line(free, y - 4, 6)
        elif pat == 'double':
            a, b, free = lanes
            place(pick(lows), a, y)
            place(pick(highs) if highs else pick(lows), b, y + 7)
            place(pick(highs) if highs else pick(lows), a, y + 12)
            coin_line(free, y - 2, 9)
            step += 8
        elif pat == 'train':
            a, b, free = lanes
            place(pick(trains), a, y + 6)
            if ramps:
                place(pick(ramps), a, y - 3)
                coin_line(a, y - 5, 3, z=cz + 1.2)
                coin_line(a, y + 1, 8, z=surf + 4.1)
            place(pick(lows), b, y + 4)
            coin_arc(b, y + 4)
            coin_line(free, y, 5)
            step += 10
        elif pat == 'train_pair':
            a, b, free = lanes
            place(pick(trains), a, y + 6)
            place(pick(trains), b, y + 9)
            if ramps:
                place(pick(ramps), b, y)
                coin_line(b, y + 4, 8, z=surf + 4.1)
            coin_line(free, y, 10)
            step += 14
        y += step


def export_level(base):
    """Export the Scene_Layout collection as one GLB + one FBX."""
    vl = bpy.context.view_layer
    vl.update()
    vl.active_layer_collection = vl.layer_collection.children['Scene_Layout']
    gltf_export(base + '.glb', use_active_collection=True)
    try:
        bpy.ops.export_scene.fbx(filepath=base + '.fbx', use_active_collection=True, object_types={'MESH'},
                                 apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y',
                                 mesh_smooth_type='FACE', path_mode='COPY', embed_textures=True)
    except Exception as e:
        log('  fbx failed', e)


def build_sample(idx, key, title, fn, render=True):
    log('=== sample_map%d %s' % (idx, key))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    reset_mats()
    folder = os.path.join(ROOT, 'sample_map%d' % idx)
    os.makedirs(folder, exist_ok=True)
    scene = bpy.context.scene
    lcoll = bpy.data.collections.new('Scene_Layout')
    scene.collection.children.link(lcoll)

    parts, cfg = fn()
    for p in parts:
        p.bm.free()
    # reuse the baked, textured assets from the map's own .blend
    src = os.path.join(ROOT, 'map%d' % idx, key + '.blend')
    with bpy.data.libraries.load(src, link=False) as (data_from, data_to):
        data_to.collections = ['Assets']
    acoll = data_to.collections[0]
    scene.collection.children.link(acoll)
    A, kinds = {}, {}
    for ob in acoll.objects:
        A[ob.name] = ob
        kinds.setdefault(ob['asset_kind'], []).append(ob.name)
    for img in bpy.data.images:
        img.pack()

    r = random.Random(100 + idx)
    L = Layout(A, lcoll)
    s0, s1 = cfg.get('seg_range', (-2, 16))
    ratio = LEVEL_LEN / (s1 * SEG)

    # ground + repeating pieces
    if cfg.get('segment'):
        for i in range(-2, NSEG + 3):
            L.put(cfg['segment'], (0, i * SEG, 0))
    for name, every, offs in cfg.get('repeat', []):
        for i in range(-2, NSEG + 3, every):
            for (x, dy, z, rz) in offs:
                if i * SEG + dy < cfg.get('repeat_min_y', -1e9):
                    continue
                L.put(name, (x, i * SEG + dy, z), rz)
    for row in cfg.get('rows', []):
        for sg in row.get('sides', (-1, 1)):
            y = row['y'][0]
            while y < max(row['y'][1], LEVEL_LEN + 30):
                rz = 0 if (sg < 0 or row.get('fixed_rz')) else 180
                L.put(r.choice(row['names']), (sg * row['x'], y, row.get('z', 0)), rz)
                y += row['step']
    for sc in cfg.get('scatter', []):
        y0, y1 = sc['y']
        y1 = y0 + (y1 - y0) * ratio
        n = int(sc['n'] * ratio * 1.5)
        for k in range(n):
            sg = (-1, 1)[k % 2]
            yy = y0 + (k + r.random()) * (y1 - y0) / n
            zz = r.uniform(*sc['zr']) if 'zr' in sc else sc.get('z', 0)
            L.put(r.choice(sc['names']), (sg * r.uniform(*sc['x']), yy, zz), r.uniform(0, 360),
                  r.uniform(*sc.get('s', (1, 1))))
    for name, loc, rz, s in cfg.get('fixed', []):
        L.put(name, (loc[0], loc[1] * ratio, loc[2]), rz, s)

    dress(L, cfg, r, -6, LEVEL_LEN + 10)
    obstacle_course(L, {k: v for k, v in A.items()}, kinds, cfg, r)

    # make sure every single element appears at least once
    for name, ob in A.items():
        if name in L.placed or ob['asset_kind'] in ('segment', 'coin'):
            continue
        for k in range(3):
            sg = (-1, 1)[k % 2]
            L.put(name, (sg * r.uniform(9, 14), r.uniform(20, LEVEL_LEN - 20), cfg.get('ground', {}).get('z', 0)),
                  r.uniform(0, 360))

    # environment
    g = cfg.get('ground')
    if g:
        gp = Part('ground_plane', 'layout')
        gp.box((900, 1200, 0.2), (0, 250, g['z'] - 0.1), mat(g.get('name', 'ground_plane'), g['hex'], g.get('rough', 0.9)))
        gp.build(lcoll)
    if cfg.get('snowfall'):
        sp = Part('snowfall', 'layout')
        rr = random.Random(1)
        sm = mat('snowflake_fx', '#ffffff', .5, emit=1.5)
        for _ in range(1500):
            sp.ico(0.06, (rr.uniform(-22, 22), rr.uniform(-5, LEVEL_LEN), rr.uniform(0.5, 14)), sm, sub=0)
        sp.build(lcoll)
    base_lights = cfg.get('lights', [])
    for k in range(int(LEVEL_LEN / 70) + 1):
        for (kind, loc, energy, hexc) in base_lights:
            add_light(kind, (loc[0], loc[1] + k * 70, loc[2]), energy, hexc, lcoll, radius=1.0)
    ll = cfg.get('lamp_lights')
    if ll:
        name, off, energy, hexc = ll
        for o in L.placed.get(name, []):
            add_light('POINT', tuple(o.location[i] + off[i] for i in range(3)), energy, hexc, lcoll)
    glow_lights(L, cfg, lcoll, 1e9)
    setup_world(cfg['world'])

    # level description for game engines
    placements = []
    for name, objs in L.placed.items():
        for o in objs:
            placements.append(dict(asset=name, kind=A[name]['asset_kind'], pos=[round(v, 3) for v in o.location],
                                   rot_z_deg=round(math.degrees(o.rotation_euler.z), 2), scale=round(o.scale.x, 3)))
    with open(os.path.join(folder, 'level.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(map=idx, key=key, title=title, length_m=LEVEL_LEN, lane_x=[-LANE, 0, LANE],
                       assets_folder='../map%d/glb' % idx, placements=placements), f, indent=1)

    base = os.path.join(folder, 'sample_map%d' % idx)
    export_level(base)

    # cameras: runner view (scene camera) + aerial overview
    setup_camera(cfg.get('camera'))
    cd = bpy.data.cameras.new('OverviewCam')
    cd.lens = 26
    cd.clip_end = 3000
    oc = bpy.data.objects.new('OverviewCamera', cd)
    oc.location = (-70, -55, 85)
    oc.rotation_euler = (Vector((0, 110, 0)) - oc.location).to_track_quat('-Z', 'Y').to_euler()
    scene.collection.objects.link(oc)
    setup_render(os.path.join(folder, 'preview.png'), cfg['world'])
    bpy.ops.wm.save_as_mainfile(filepath=base + '.blend')
    log('  %d placements, saved' % len(placements))
    if render:
        bpy.ops.render.render(write_still=True)
        runner = scene.camera
        scene.camera = oc
        scene.render.resolution_x, scene.render.resolution_y = 1600, 900
        scene.render.filepath = os.path.join(folder, 'overview.png')
        bpy.ops.render.render(write_still=True)
        scene.camera = runner
        scene.render.resolution_x, scene.render.resolution_y = 720, 1280
        log('  rendered')


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['all']
    render = 'norender' not in argv
    export_only = 'exportonly' in argv
    sel = [a for a in argv if a not in ('norender', 'exportonly') and '=' not in a]
    todo = MAPS if (not sel or sel[0] == 'all') else [m for m in MAPS if str(m[0]) in sel]
    for m in todo:
        try:
            if export_only:
                base = os.path.join(ROOT, 'sample_map%d' % m[0], 'sample_map%d' % m[0])
                bpy.ops.wm.open_mainfile(filepath=base + '.blend')
                export_level(base)
                log('  re-exported sample_map%d' % m[0])
                continue
            build_sample(*m, render=render)
        except Exception:
            log('  FAILED sample_map%d\n%s' % (m[0], traceback.format_exc()))
    log('done')


if __name__ == '__main__':
    main()
