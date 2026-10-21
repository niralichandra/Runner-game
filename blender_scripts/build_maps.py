"""Build all runner maps.

Usage (Blender 4.2+/5.x):
    blender -b --factory-startup --python build_maps.py -- all
    blender -b --factory-startup --python build_maps.py -- 3          (only map3)
    blender -b --factory-startup --python build_maps.py -- 3 norender

Output per map:  <root>/mapN/
    <theme>.blend        assembled preview scene + every asset in the "Assets" collection
    glb/<asset>.glb      one file per element (Unity/Godot/three.js/Unreal)
    fbx/<asset>.fbx
    preview.png          render of the scene
    manifest.json        asset list with kind + size (metres)
"""
import bpy, sys, os, math, json, random, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import importlib, lib, bake
importlib.reload(lib)
importlib.reload(bake)
from lib import *

# map set: "classic" (maps.py -> project root) or "romantic" (maps_romantic.py -> <root>/romantic)
ARGV = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
SET = next((a.split('=', 1)[1] for a in ARGV if a.startswith('set=')), 'classic')
if SET == 'romantic':
    import maps_romantic as _mapsmod
    ROOT = os.path.join(os.path.dirname(HERE), 'romantic')
elif SET == 'options':
    import maps_romantic, maps_options as _mapsmod
    importlib.reload(maps_romantic)
    ROOT = os.path.join(os.path.dirname(HERE), 'romantic', 'options_sample', 'A_detailed_models')
else:
    import maps as _mapsmod
    ROOT = os.path.dirname(HERE)
importlib.reload(_mapsmod)
MAPS = _mapsmod.MAPS
os.makedirs(ROOT, exist_ok=True)
LOG = os.path.join(ROOT, 'build_log.txt')
BAKE = True


def log(*a):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(' '.join(str(x) for x in a) + '\n')


# --------------------------------------------------------------------------- export
def gltf_export(path, **kw):
    """GLB export that keeps the baked vertex colours (option names differ between versions)."""
    for extra in (dict(export_vertex_color='ACTIVE'), dict(export_colors=True), {}):
        try:
            bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', **kw, **extra)
            return
        except TypeError:
            continue


def export_asset(ob, folder):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    glb = os.path.join(folder, 'glb', ob.name + '.glb')
    fbx = os.path.join(folder, 'fbx', ob.name + '.fbx')
    gltf_export(glb, use_selection=True, export_apply=True)
    try:
        bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, apply_scale_options='FBX_SCALE_ALL',
                                 axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE',
                                 path_mode='COPY', embed_textures=True)
    except Exception as e:
        log('  fbx failed', ob.name, e)
    ob.select_set(False)


# --------------------------------------------------------------------------- layout
class Layout:
    def __init__(self, assets, coll):
        self.A, self.coll, self.placed = assets, coll, {}

    def put(self, name, loc, rz=0.0, s=1.0):
        src = self.A[name]
        o = src.copy()
        o.location = loc
        o.rotation_euler = (0, 0, math.radians(rz))
        o.scale = (s, s, s)
        self.coll.objects.link(o)
        self.placed.setdefault(name, []).append(o)
        return o


def lane_x(l):
    return l * LANE


def do_layout(A, cfg, coll):
    r = random.Random(7)
    L = Layout(A, coll)
    s0, s1 = cfg.get('seg_range', (-2, 16))
    if cfg.get('segment'):
        for i in range(s0, s1):
            L.put(cfg['segment'], (0, i * SEG, 0))
    for name, every, offs in cfg.get('repeat', []):
        for i in range(s0, s1, every):
            for (x, dy, z, rz) in offs:
                if i * SEG + dy < cfg.get('repeat_min_y', -1e9):
                    continue
                L.put(name, (x, i * SEG + dy, z), rz)
    for row in cfg.get('rows', []):
        for sg in row.get('sides', (-1, 1)):
            y = row['y'][0]
            while y < row['y'][1]:
                rz = 0 if (sg < 0 or row.get('fixed_rz')) else 180
                L.put(r.choice(row['names']), (sg * row['x'], y, row.get('z', 0)), rz)
                y += row['step']
    for sc in cfg.get('scatter', []):
        n = int(sc['n'] * 1.5)
        y0, y1 = sc['y']
        for k in range(n):
            sg = (-1, 1)[k % 2]
            y = y0 + (k + r.random()) * (y1 - y0) / n
            x = sg * r.uniform(*sc['x'])
            z = r.uniform(*sc['zr']) if 'zr' in sc else sc.get('z', 0)
            L.put(r.choice(sc['names']), (x, y, z), r.uniform(0, 360), r.uniform(*sc.get('s', (1, 1))))
    for name, loc, rz, s in cfg.get('fixed', []):
        L.put(name, loc, rz, s)
    surf = cfg.get('surface', 0.5)
    for name, lane, y in cfg.get('obstacles', []):
        L.put(name, (lane_x(lane), y, surf - 0.02 if 'train' not in name and 'ramp' not in name else surf - 0.1))
    cz = surf + 0.75
    for lane, y0, n in cfg.get('coins', []):
        for k in range(n):
            L.put(cfg['coin'], (lane_x(lane), y0 + k * 1.6, cz))
    for lane, yc, n in cfg.get('coin_arcs', []):
        for k in range(n):
            t = k / (n - 1)
            L.put(cfg['coin'], (lane_x(lane), yc - 4.5 + 9 * t, cz + 2.2 * math.sin(math.pi * t)))
    for lane, y0, n, z in cfg.get('coins_raised', []):
        for k in range(n):
            L.put(cfg['coin'], (lane_x(lane), y0 + k * 1.6, z))
    for name, lane, y in cfg.get('powerups', []):
        L.put(name, (lane_x(lane), y, cz + 0.35))
    return L


def dress(L, cfg, r, y0, y1):
    """Tight edge dressing along the corridor + big framing props near the camera (romantic set)."""
    for e in cfg.get('edge', []):
        for sg in e.get('sides', (-1, 1)):
            y = y0 + r.uniform(0, e['step'][1])
            while y < y1:
                x = sg * r.uniform(*e['x'])
                L.put(r.choice(e['names']), (x, y, e.get('z', 0)), r.uniform(0, 360) if e.get('spin', True) else (0 if sg < 0 else 180),
                      r.uniform(*e.get('s', (1, 1))))
                y += r.uniform(*e['step'])
    for name, x, y, z, rz, s in cfg.get('framing', []):
        L.put(name, (x, y, z), rz, s)


def glow_lights(L, cfg, coll, ymax):
    """Real point lights inside lanterns / torches / lamps so they light the scene around them."""
    for name, off, energy, hexc in cfg.get('glow_lights', []):
        for o in L.placed.get(name, []):
            if o.location.y < ymax:
                s = o.scale.x
                mw = Matrix.LocRotScale(o.location, o.rotation_euler, o.scale)
                add_light('POINT', tuple(mw @ Vector(off)), energy * s * s, hexc, coll, radius=0.25)

# --------------------------------------------------------------------------- environment
def setup_world(w):
    scene = bpy.context.scene
    world = bpy.data.worlds.new('Sky')
    scene.world = world
    try:
        world.use_nodes = True
    except Exception:
        pass
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])
    el = ramp.color_ramp.elements
    el[0].position, el[0].color = 0.0, (*srgb(w['hor']), 1)
    el[1].position, el[1].color = 0.55, (*srgb(w['top']), 1)
    bg.inputs['Strength'].default_value = w.get('strength', 1.0)
    world.mist_settings.start = w.get('haze_start', 12.0)
    world.mist_settings.depth = w.get('haze_depth', 140.0)
    world.mist_settings.falloff = 'QUADRATIC'
    bpy.context.view_layer.use_pass_mist = True

    top = srgb(w['top'])
    if w.get('clouds', (0.2126 * top[0] + 0.7152 * top[1] + 0.0722 * top[2]) > 0.12):
        cm, cm2 = mat('sky_cloud', '#ffffff', .9, emit=.35), mat('sky_cloud_shade', '#e3eefc', .9, emit=.25)
        rr = random.Random(5)
        for k in range(14):
            cp = cloud('sky_cloud_%d' % k, cm, cm2, seed=k, size=rr.uniform(6, 11))
            co = cp.build(scene.collection)
            co.location = (rr.choice((-1, 1)) * rr.uniform(25, 140), rr.uniform(160, 520), rr.uniform(35, 90))
    energy, hexc, rot = w['sun']
    ld = bpy.data.lights.new('Sun', 'SUN')
    ld.energy = energy
    ld.color = srgb(hexc)
    ld.angle = math.radians(3)
    so = bpy.data.objects.new('Sun', ld)
    so.rotation_euler = [math.radians(a) for a in rot]
    scene.collection.objects.link(so)


def add_light(kind, loc, energy, hexc, coll, radius=0.3):
    ld = bpy.data.lights.new('Light', kind)
    ld.energy = energy
    ld.color = srgb(hexc)
    try:
        ld.shadow_soft_size = radius
    except Exception:
        pass
    o = bpy.data.objects.new('Light', ld)
    o.location = loc
    coll.objects.link(o)


def setup_camera(cam=None):
    """cam: optional dict(loc=(x,y,z), target=(x,y,z), lens=mm) - romantic maps use a low, close, framed camera."""
    cam = cam or {}
    scene = bpy.context.scene
    cd = bpy.data.cameras.new('Camera')
    cd.lens = cam.get('lens', 22)
    cd.clip_end = 1500
    co = bpy.data.objects.new('RunnerCamera', cd)
    co.location = cam.get('loc', (0, -9.0, 6.4))
    d = Vector(cam.get('target', (0, 28, 0.0))) - Vector(co.location)
    co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    scene.collection.objects.link(co)
    scene.camera = co


def setup_render(path, world=None):
    scene = bpy.context.scene
    for eng in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'):
        try:
            scene.render.engine = eng
            break
        except TypeError:
            continue
    ee = scene.eevee
    for attr, val in (('taa_render_samples', 48), ('use_raytracing', True), ('use_shadows', True),
                      ('volumetric_end', 260.0), ('volumetric_tile_size', '8'), ('use_gtao', True),
                      ('gtao_distance', 1.5), ('use_bloom', True), ('shadow_ray_count', 2), ('shadow_step_count', 8)):
        try:
            setattr(ee, attr, val)
        except Exception:
            pass
    try:
        ee.ray_tracing_options.resolution_scale = '2'
    except Exception:
        pass
    setup_bloom(scene, world or {})
    scene.render.resolution_x, scene.render.resolution_y = 720, 1280
    scene.render.resolution_percentage = 100
    scene.render.filepath = path
    scene.render.image_settings.file_format = 'PNG'
    try:
        scene.view_settings.view_transform = 'Standard'
        for look in ('Medium High Contrast', 'None'):
            try:
                scene.view_settings.look = look
                break
            except TypeError:
                continue
    except Exception:
        pass


def setup_bloom(scene, w=None):
    """Compositor glow on bright emissive parts (fire, neon, lamps). Handles 4.x and 5.x APIs."""
    try:
        if hasattr(scene, 'compositing_node_group'):
            ng = bpy.data.node_groups.new('Bloom', 'CompositorNodeTree')
            ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
            scene.compositing_node_group = ng
            rl = ng.nodes.new('CompositorNodeRLayers')
            gl = ng.nodes.new('CompositorNodeGlare')
            out = ng.nodes.new('NodeGroupOutput')
        else:
            scene.use_nodes = True
            ng = scene.node_tree
            ng.nodes.clear()
            rl = ng.nodes.new('CompositorNodeRLayers')
            gl = ng.nodes.new('CompositorNodeGlare')
            out = ng.nodes.new('CompositorNodeComposite')
        ts = gl.inputs.get('Type')
        for val in ('Bloom', 'BLOOM', 'Fog Glow', 'FOG_GLOW'):
            try:
                if ts is not None:
                    ts.default_value = val
                else:
                    gl.glare_type = val
                break
            except Exception:
                continue
        for name, val in (('Threshold', 1.0), ('Strength', 0.6), ('Size', 0.5), ('Smoothness', 0.5)):
            s = gl.inputs.get(name)
            if s is not None:
                try:
                    s.default_value = val
                except Exception:
                    pass
        for attr, val in (('threshold', 1.0), ('mix', -0.4), ('size', 7)):
            try:
                setattr(gl, attr, val)
            except Exception:
                pass
        w = w or {}
        img = rl.outputs['Image']
        if w.get('haze', 0) > 0:
            img = _haze(ng, rl, img, w)
        ng.links.new(img, gl.inputs['Image'])
        img = gl.outputs['Image']
        if w.get('grade', 'haze' in w):
            img = _grade(ng, img, w)
        ng.links.new(img, out.inputs[0])
        scene.render.use_compositing = True
    except Exception as e:
        log('  bloom setup failed:', e)


def _cnode(ng, *types):
    for t in types:
        try:
            return ng.nodes.new(t)
        except Exception:
            continue
    raise RuntimeError('no node type among %s' % (types,))


def _mix(ng, fac, a, b, blend='MIX'):
    mx = _cnode(ng, 'ShaderNodeMix', 'CompositorNodeMixRGB')
    try:
        mx.data_type = 'RGBA'
    except Exception:
        pass
    mx.blend_type = blend
    if isinstance(fac, (int, float)):
        mx.inputs[0].default_value = fac
    else:
        ng.links.new(fac, mx.inputs[0])
    ain = [s for s in mx.inputs if s.name in ('A', 'Image') and s.type == 'RGBA'][0]
    bin_ = [s for s in mx.inputs if s.name in ('B', 'Image') and s.type == 'RGBA' and s != ain][0]
    ng.links.new(a, ain)
    if isinstance(b, tuple):
        bin_.default_value = b
    else:
        ng.links.new(b, bin_)
    return [s for s in mx.outputs if s.type == 'RGBA'][0]


def _math(ng, op, a, b):
    m = _cnode(ng, 'ShaderNodeMath', 'CompositorNodeMath')
    m.operation = op
    for sock, v in zip(m.inputs, (a, b)):
        if isinstance(v, (int, float)):
            sock.default_value = v
        else:
            ng.links.new(v, sock)
    return m.outputs[0]


def _haze(ng, rl, img, w):
    """Depth haze from the mist pass; the sky (mist == 1) is left untouched."""
    mist = rl.outputs.get('Mist')
    if mist is None:
        return img
    mask = _math(ng, 'LESS_THAN', mist, 0.995)
    fac = _math(ng, 'MULTIPLY', _math(ng, 'MULTIPLY', mist, w.get('haze', 0.4)), mask)
    return _mix(ng, fac, img, (*srgb(w.get('haze_hex', w['hor'])), 1.0))


def _grade(ng, img, w):
    try:
        hs = ng.nodes.new('CompositorNodeHueSat')
        hs.inputs['Saturation'].default_value = w.get('saturation', 1.18)
        ng.links.new(img, hs.inputs['Image'])
        img = hs.outputs['Image']
        bc = ng.nodes.new('CompositorNodeBrightContrast')
        bc.inputs['Contrast'].default_value = w.get('contrast', 8.0)
        ng.links.new(img, bc.inputs['Image'])
        img = bc.outputs['Image']
        em = ng.nodes.new('CompositorNodeEllipseMask')
        em.inputs['Size'].default_value = (0.92, 0.95)
        try:
            em.inputs['Position'].default_value = (0.5, 0.5)
        except Exception:
            pass
        bl = ng.nodes.new('CompositorNodeBlur')
        bl.inputs['Size'].default_value = (140, 140)
        ng.links.new(em.outputs['Mask'], bl.inputs['Image'])
        img = _mix(ng, w.get('vignette', 0.32), img, bl.outputs['Image'], 'MULTIPLY')
    except Exception as e:
        log('  grade failed:', e)
    return img


def gallery_pos(i):
    return ((i % 6) * 28 - 70, -60 - (i // 6) * 30, 0)


# --------------------------------------------------------------------------- per map
def build_map(idx, key, title, fn, render=True):
    log('=== map%d %s' % (idx, key))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    reset_mats()
    folder = os.path.join(ROOT, 'map%d' % idx)
    for sub in ('glb', 'fbx'):
        os.makedirs(os.path.join(folder, sub), exist_ok=True)
    scene = bpy.context.scene
    acoll = bpy.data.collections.new('Assets')
    lcoll = bpy.data.collections.new('Scene_Layout')
    scene.collection.children.link(acoll)
    scene.collection.children.link(lcoll)

    parts, cfg = fn()
    assets, manifest = {}, []
    for i, p in enumerate(parts):
        ob = p.build(acoll)
        if BAKE:
            try:
                sz = bake.bake_asset(ob, folder)
                log('  baked %s (%dpx)' % (ob.name, sz))
            except Exception:
                log('  bake FAILED %s\n%s' % (ob.name, traceback.format_exc()))
        export_asset(ob, folder)
        dims = [round(v, 2) for v in ob.dimensions]
        manifest.append(dict(name=ob.name, kind=p.kind, size_m=dims,
                             files=dict(glb='glb/%s.glb' % ob.name, fbx='fbx/%s.fbx' % ob.name)))
        ob.location = gallery_pos(i)
        assets[ob.name] = ob
    log('  exported %d assets' % len(parts))

    lay = do_layout(assets, cfg, lcoll)
    dress(lay, cfg, random.Random(9), -6, cfg.get('seg_range', (-2, 16))[1] * SEG)
    g = cfg.get('ground')
    if g:
        gp = Part('ground_plane', 'layout')
        gp.box((900, 900, 0.2), (0, 150, g['z'] - 0.1), mat(g.get('name', 'ground_plane'), g['hex'], g.get('rough', 0.9)))
        gp.build(lcoll)
    if cfg.get('snowfall'):
        sp = Part('snowfall', 'layout')
        rr = random.Random(1)
        sm = mat('snowflake_fx', '#ffffff', .5, emit=1.5)
        for _ in range(500):
            sp.ico(0.06, (rr.uniform(-20, 20), rr.uniform(-5, 80), rr.uniform(0.5, 14)), sm, sub=0)
        sp.build(lcoll)
    for (kind, loc, energy, hexc) in cfg.get('lights', []):
        add_light(kind, loc, energy, hexc, lcoll, radius=1.0)
    ll = cfg.get('lamp_lights')
    if ll:
        name, off, energy, hexc = ll
        for o in lay.placed.get(name, []):
            if o.location.y < 90:
                add_light('POINT', (o.location.x + off[0], o.location.y + off[1], o.location.z + off[2]), energy, hexc, lcoll)

    glow_lights(lay, cfg, lcoll, 130)
    setup_world(cfg['world'])
    setup_camera(cfg.get('camera'))
    setup_render(os.path.join(folder, 'preview.png'), cfg['world'])

    with open(os.path.join(folder, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(map=idx, key=key, title=title, lane_x=[-LANE, 0, LANE], segment_length_m=SEG,
                       forward_axis='+Y (Blender) / -Z (glTF)', coin=cfg['coin'], segment=cfg.get('segment'),
                       assets=manifest), f, indent=2)
    blend = os.path.join(folder, key + '.blend')
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    log('  saved', blend)
    if render:
        bpy.ops.render.render(write_still=True)
        log('  rendered preview')


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['all']
    global BAKE
    render = 'norender' not in argv
    BAKE = 'nobake' not in argv
    sel = [a for a in argv if a not in ('norender', 'nobake') and '=' not in a]
    todo = MAPS if (not sel or sel[0] == 'all') else [m for m in MAPS if str(m[0]) in sel]
    for idx, key, title, fn in todo:
        try:
            build_map(idx, key, title, fn, render)
        except Exception:
            log('  FAILED map%d\n%s' % (idx, traceback.format_exc()))
    log('done')


if __name__ == '__main__':
    main()
