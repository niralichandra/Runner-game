"""Render a preview image of every element of every map.

    blender -b --factory-startup --python render_elements.py -- all set=romantic

Output: <root>/mapN/elements/<asset>.png  (transparent background, 512x512)
"""
import bpy, sys, os, math, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_maps
from build_maps import ROOT, MAPS, log
from mathutils import Vector

VIEW = {
    'coin': Vector((0.0, -1.0, 0.12)), 'powerup': Vector((0.0, -1.0, 0.12)),
    'segment': Vector((-0.55, -1.0, 1.15)), 'landmark': Vector((-0.35, -1.0, 0.35)), 'backdrop': Vector((-0.6, -1.0, 0.45)),
}
DEFAULT_VIEW = Vector((-0.8, -1.5, 0.75))


def thumb_lights(scene):
    for name, energy, rot in (('ThumbKey', 3.2, (50, 0, -35)), ('ThumbFill', 1.3, (65, 0, 140)), ('ThumbRim', 1.8, (20, 0, 180))):
        ld = bpy.data.lights.new(name, 'SUN')
        ld.energy = energy
        o = bpy.data.objects.new(name, ld)
        o.rotation_euler = [math.radians(a) for a in rot]
        scene.collection.objects.link(o)


def render_map(idx, key):
    folder = os.path.join(ROOT, 'map%d' % idx)
    bpy.ops.wm.open_mainfile(filepath=os.path.join(folder, key + '.blend'))
    scene = bpy.context.scene
    out = os.path.join(folder, 'elements')
    os.makedirs(out, exist_ok=True)
    assets = bpy.data.collections['Assets']
    asset_objs = list(assets.objects)
    for o in scene.objects:
        if o.type in ('MESH', 'LIGHT'):
            o.hide_render = True
    thumb_lights(scene)
    try:
        scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
    except Exception:
        pass
    scene.render.film_transparent = True
    scene.render.resolution_x = scene.render.resolution_y = 512
    try:
        scene.eevee.taa_render_samples = 24
    except Exception:
        pass
    cd = bpy.data.cameras.new('ThumbCam')
    cd.lens = 50
    cd.clip_end = 2000
    cam = bpy.data.objects.new('ThumbCam', cd)
    scene.collection.objects.link(cam)
    scene.camera = cam
    fov = cd.angle
    for ob in asset_objs:
        try:
            old = ob.location.copy()
            ob.location = (0, 0, 0)
            ob.hide_render = False
            bpy.context.view_layer.update()
            pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
            c = sum(pts, Vector()) / 8
            rad = max((p - c).length for p in pts)
            views = [('', VIEW.get(ob.get('asset_kind', ''), DEFAULT_VIEW))]
            if ob.get('asset_kind') == 'coin':
                views = [('', Vector((-0.75, -1.0, 0.3))), ('_front', Vector((0, -1, 0))), ('_side', Vector((1, 0, 0))),
                         ('_3d', Vector((-0.75, -1.0, 0.3)))]
            for suffix, d in views:
                d = d.normalized()
                dist = rad / math.sin(fov / 2) * 0.92
                cam.location = c + d * dist
                cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
                cd.clip_start = max(0.01, dist * 0.02)
                scene.render.filepath = os.path.join(out, ob.name + suffix + '.png')
                bpy.ops.render.render(write_still=True)
            ob.hide_render = True
            ob.location = old
        except Exception:
            log('  thumb FAILED %s\n%s' % (ob.name, traceback.format_exc()))
    log('  map%d: %d element previews' % (idx, len(asset_objs)))


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['all']
    sel = [a for a in argv if '=' not in a]
    todo = MAPS if (not sel or sel[0] == 'all') else [m for m in MAPS if str(m[0]) in sel]
    for idx, key, title, fn in todo:
        try:
            render_map(idx, key)
        except Exception:
            log('  FAILED elements map%d\n%s' % (idx, traceback.format_exc()))
    log('elements done')


if __name__ == '__main__':
    main()
