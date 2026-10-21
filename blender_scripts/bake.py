"""Texture baking: turns each procedural asset into a game-ready textured asset.

Per asset:  UV unwrap -> "hand-painted" shading network (mottling, wood grain, cavity AO,
worn/bright edges, bump + rounded-edge normals) -> Cycles bake of an albedo map and a
tangent-space normal map -> materials rewired to plain image textures (exports cleanly
to GLB/FBX; looks the same in any engine).
"""
import bpy, os, math
from lib import WOOD_KEYS, STONE_KEYS

_GPU_DONE = [False]


def _enable_gpu(scene):
    if _GPU_DONE[0]:
        return
    _GPU_DONE[0] = True
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        for dev in ('OPTIX', 'CUDA', 'HIP', 'ONEAPI', 'METAL'):
            try:
                prefs.compute_device_type = dev
                prefs.get_devices()
                gpus = [d for d in prefs.devices if d.type != 'CPU']
                if gpus:
                    for d in prefs.devices:
                        d.use = True
                    scene.cycles.device = 'GPU'
                    print('bake: using', dev)
                    return
            except Exception:
                continue
    except Exception as e:
        print('bake: gpu setup failed', e)


def setup_bake(scene):
    scene.render.engine = 'CYCLES'
    _enable_gpu(scene)
    if _GPU_DONE[0] and getattr(scene.cycles, 'device', 'CPU') != 'GPU':
        try:
            scene.cycles.device = 'GPU'
        except Exception:
            pass
    scene.cycles.samples = 12
    try:
        scene.cycles.use_denoising = False
    except Exception:
        pass
    scene.render.bake.margin = 6
    scene.render.bake.use_clear = True


def unwrap(ob):
    vl = bpy.context.view_layer
    for o in vl.objects:
        o.select_set(False)
    ob.select_set(True)
    vl.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.004)
    bpy.ops.object.mode_set(mode='OBJECT')


def tex_size(ob):
    d = max(ob.dimensions)
    kind = ob.get('asset_kind', 'prop')
    if kind in ('segment', 'landmark') or d > 12:
        return 1024
    if d < 1.5:
        return 256
    return 512


def _kind(name):
    low = name.lower()
    if 'water' in low or 'river' in low:
        return 'water'
    if any(k in low for k in WOOD_KEYS):
        return 'wood'
    if any(k in low for k in STONE_KEYS):
        return 'stone'
    return 'other'


def _rgba_in(node, name):
    return [s for s in node.inputs if s.name == name and s.type == 'RGBA'][0]


def _rgba_out(node):
    return [s for s in node.outputs if s.type == 'RGBA'][0]


def _mul(nt, col_out, fac_out=None, value=None, blend='MULTIPLY', fac=1.0):
    mx = nt.nodes.new('ShaderNodeMix')
    mx.data_type = 'RGBA'
    mx.blend_type = blend
    mx.inputs[0].default_value = fac
    nt.links.new(col_out, _rgba_in(mx, 'A'))
    if fac_out is not None:
        nt.links.new(fac_out, _rgba_in(mx, 'B'))
    else:
        _rgba_in(mx, 'B').default_value = value
    return mx


def _range(nt, src, lo, hi, from_lo=0.0, from_hi=1.0):
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = from_lo
    mr.inputs['From Max'].default_value = from_hi
    mr.inputs['To Min'].default_value = lo
    mr.inputs['To Max'].default_value = hi
    nt.links.new(src, mr.inputs['Value'])
    return mr.outputs['Result']


def paint(m, emissive):
    """Append the painted-look network in front of Base Color, and bevel-normals into the bump."""
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    base_in = b.inputs['Base Color']
    if base_in.is_linked:
        col = base_in.links[0].from_socket
    else:
        rgb = nt.nodes.new('ShaderNodeRGB')
        rgb.outputs[0].default_value = base_in.default_value
        col = rgb.outputs[0]
    kind = _kind(m.name)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    if not emissive:
        nz = nt.nodes.new('ShaderNodeTexNoise')
        nz.inputs['Scale'].default_value = 2.2 if kind != 'other' else 1.2
        nz.inputs['Detail'].default_value = 5
        nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
        amp = {'stone': (0.8, 1.12), 'wood': (0.85, 1.08), 'water': (0.9, 1.1), 'other': (0.93, 1.05)}[kind]
        col = _rgba_out(_mul(nt, col, _range(nt, nz.outputs['Fac'], *amp, 0.3, 0.7)))
        if kind == 'wood':
            wv = nt.nodes.new('ShaderNodeTexWave')
            wv.inputs['Scale'].default_value = 2.5
            wv.inputs['Distortion'].default_value = 7
            wv.inputs['Detail'].default_value = 3
            nt.links.new(tc.outputs['Object'], wv.inputs['Vector'])
            col = _rgba_out(_mul(nt, col, _range(nt, wv.outputs['Fac'], 0.78, 1.04)))
        if kind == 'stone':
            vo = nt.nodes.new('ShaderNodeTexVoronoi')
            vo.inputs['Scale'].default_value = 5.0
            try:
                vo.feature = 'DISTANCE_TO_EDGE'
            except Exception:
                pass
            nt.links.new(tc.outputs['Object'], vo.inputs['Vector'])
            col = _rgba_out(_mul(nt, col, _range(nt, vo.outputs['Distance'], 0.82, 1.0, 0.0, 0.06)))
        ao = nt.nodes.new('ShaderNodeAmbientOcclusion')
        ao.inputs['Distance'].default_value = 0.6
        ao.only_local = True
        ao.samples = 12
        col = _rgba_out(_mul(nt, col, _range(nt, ao.outputs['AO'], 0.5, 1.0)))
        bev = nt.nodes.new('ShaderNodeBevel')
        bev.inputs['Radius'].default_value = 0.035
        bev.samples = 8
        geo = nt.nodes.new('ShaderNodeNewGeometry')
        dot = nt.nodes.new('ShaderNodeVectorMath')
        dot.operation = 'DOT_PRODUCT'
        nt.links.new(bev.outputs['Normal'], dot.inputs[0])
        nt.links.new(geo.outputs['Normal'], dot.inputs[1])
        edge = _range(nt, dot.outputs['Value'], 0.55, 0.0, 0.85, 1.0)
        scr = nt.nodes.new('ShaderNodeMix')
        scr.data_type = 'RGBA'
        scr.blend_type = 'SCREEN'
        nt.links.new(edge, scr.inputs[0])
        nt.links.new(col, _rgba_in(scr, 'A'))
        _rgba_in(scr, 'B').default_value = (0.32, 0.3, 0.27, 1)
        col = _rgba_out(scr)
        # rounded-edge shading goes into the normal bake
        bump = next((n for n in nt.nodes if n.type == 'BUMP'), None)
        if bump:
            nt.links.new(bev.outputs['Normal'], bump.inputs['Normal'])
        else:
            nt.links.new(bev.outputs['Normal'], b.inputs['Normal'])
    nt.links.new(col, base_in)


def _rewire(m, alb, nrm):
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    for n in list(nt.nodes):
        if n not in (b, out):
            nt.nodes.remove(n)
    ti = nt.nodes.new('ShaderNodeTexImage')
    ti.image = alb
    nt.links.new(ti.outputs['Color'], b.inputs['Base Color'])
    tn = nt.nodes.new('ShaderNodeTexImage')
    tn.image = nrm
    nm = nt.nodes.new('ShaderNodeNormalMap')
    nt.links.new(tn.outputs['Color'], nm.inputs['Color'])
    nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    ti.location, tn.location, nm.location = (-500, 300), (-500, -100), (-220, -100)


def bake_asset(ob, folder):
    scene = bpy.context.scene
    setup_bake(scene)
    unwrap(ob)
    size = tex_size(ob)
    tex_dir = os.path.join(folder, 'textures')
    os.makedirs(tex_dir, exist_ok=True)
    mats, saved = [], []
    for i, m0 in enumerate(ob.data.materials):
        m = m0.copy()
        m.name = '%s__%s' % (ob.name, m0.name)
        ob.data.materials[i] = m
        b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        emissive = b.inputs['Emission Strength'].default_value > 0
        saved.append((b.inputs['Metallic'].default_value, b.inputs['Alpha'].default_value))
        b.inputs['Metallic'].default_value = 0.0      # diffuse-colour bake of metals would be black
        b.inputs['Alpha'].default_value = 1.0
        paint(m, emissive)
        mats.append(m)
    alb = bpy.data.images.new(ob.name + '_albedo', size, size)
    nrm = bpy.data.images.new(ob.name + '_normal', size, size)
    nrm.colorspace_settings.name = 'Non-Color'
    nodes = []
    for m in mats:
        tn = m.node_tree.nodes.new('ShaderNodeTexImage')
        tn.image = alb
        m.node_tree.nodes.active = tn
        nodes.append(tn)
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, margin=6, use_clear=True)
    for tn in nodes:
        tn.image = nrm
    bpy.ops.object.bake(type='NORMAL', normal_space='TANGENT', margin=6, use_clear=True)
    for img, suffix in ((alb, 'albedo'), (nrm, 'normal')):
        path = os.path.join(tex_dir, '%s_%s.png' % (ob.name, suffix))
        img.filepath_raw = path
        img.file_format = 'PNG'
        img.save()
        img.filepath = path
    for m, (metal, alpha) in zip(mats, saved):
        _rewire(m, alb, nrm)
        b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        b.inputs['Metallic'].default_value = metal
        b.inputs['Alpha'].default_value = alpha
    ca = ob.data.color_attributes.get('Col')
    if ca:
        ob.data.color_attributes.remove(ca)
    return size
