"""Procedural stylized modelling helpers for the Subway-style runner maps.

Every asset is built into a single bmesh (one object, several material slots),
so nothing depends on operator context and the scripts run in `blender -b`.

Look-dev features baked into the geometry (so they survive GLB/FBX export):
  * auto-bevelled edges on boxes / cylinders / prisms  -> chunky, rounded cartoon shapes
  * smooth shading with sharp edges split by angle      -> soft but crisp silhouettes
  * vertex colours ("Col"): per-part tint, noise, ground AO, underside shading
Render-only extras in the .blend: procedural bump on stone / wood materials.
"""
import bpy, bmesh, math, random, os, json, zlib
from mathutils import Vector, Matrix, Euler

LANE = 2.6          # lane spacing (lanes at x = -2.6, 0, +2.6)
SEG = 10.0          # length of one tileable ground segment along +Y
SHARP_ANGLE = math.radians(52)


# --------------------------------------------------------------------------- materials
def srgb(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


_MATS = {}
WOOD_KEYS = ('wood', 'plank', 'bark', 'sleeper', 'timber', 'log', 'post', 'beam', 'crate', 'chest', 'trunk')
STONE_KEYS = ('stone', 'sand', 'rock', 'cliff', 'wall', 'grout', 'brick', 'ballast', 'dirt', 'earth', 'path', 'tile',
              'ground', 'canyon', 'island', 'tunnel', 'snow')


def reset_mats():
    _MATS.clear()


def _sock(node, name, typ=None, out=False):
    for s in (node.outputs if out else node.inputs):
        if s.name == name and (typ is None or s.type == typ):
            return s
    return None


def mat(name, hexc, rough=0.7, metal=0.0, emit=0.0, alpha=1.0, emit_hex=None):
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    try:
        if not m.use_nodes:
            m.use_nodes = True
    except Exception:
        pass
    col = srgb(hexc)
    nt = m.node_tree
    b = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None) if nt else None
    if b:
        b.inputs['Base Color'].default_value = (*col, 1)
        b.inputs['Roughness'].default_value = rough
        b.inputs['Metallic'].default_value = metal
        if emit > 0:
            ec = srgb(emit_hex) if emit_hex else col
            b.inputs['Emission Color'].default_value = (*ec, 1)
            b.inputs['Emission Strength'].default_value = emit
        if alpha < 1:
            b.inputs['Alpha'].default_value = alpha
        try:
            # vertex colour x base colour (the node pattern the glTF exporter understands)
            vc = nt.nodes.new('ShaderNodeVertexColor')
            vc.layer_name = 'Col'
            mix = nt.nodes.new('ShaderNodeMix')
            mix.data_type = 'RGBA'
            mix.blend_type = 'MULTIPLY'
            mix.inputs[0].default_value = 1.0
            a_in = [s for s in mix.inputs if s.name == 'A' and s.type == 'RGBA'][0]
            b_in = [s for s in mix.inputs if s.name == 'B' and s.type == 'RGBA'][0]
            a_in.default_value = (*col, 1)
            nt.links.new(vc.outputs['Color'], b_in)
            res = [s for s in mix.outputs if s.type == 'RGBA'][0]
            nt.links.new(res, b.inputs['Base Color'])
            low = name.lower()
            kind = 'water' if ('water' in low or 'river' in low) else ('wood' if any(k in low for k in WOOD_KEYS) else ('stone' if any(k in low for k in STONE_KEYS) else None))
            if kind and emit == 0:
                tc = nt.nodes.new('ShaderNodeTexCoord')
                bump = nt.nodes.new('ShaderNodeBump')
                bump.inputs['Strength'].default_value = 0.35 if kind == 'stone' else 0.45
                bump.inputs['Distance'].default_value = 0.04
                if kind == 'water':
                    bump.inputs['Strength'].default_value = 0.3
                    tex = nt.nodes.new('ShaderNodeTexWave')
                    tex.inputs['Scale'].default_value = 0.6
                    tex.inputs['Distortion'].default_value = 8
                    nt.links.new(tc.outputs['Object'], tex.inputs['Vector'])
                    nt.links.new(_sock(tex, 'Fac', out=True), bump.inputs['Height'])
                elif kind == 'stone':
                    tex = nt.nodes.new('ShaderNodeTexNoise')
                    tex.inputs['Scale'].default_value = 3.5
                    tex.inputs['Detail'].default_value = 6
                    nt.links.new(tc.outputs['Object'], tex.inputs['Vector'])
                    nt.links.new(_sock(tex, 'Fac', out=True), bump.inputs['Height'])
                else:
                    tex = nt.nodes.new('ShaderNodeTexWave')
                    tex.inputs['Scale'].default_value = 2.5
                    tex.inputs['Distortion'].default_value = 6
                    tex.bands_direction = 'X'
                    nt.links.new(tc.outputs['Object'], tex.inputs['Vector'])
                    nt.links.new(_sock(tex, 'Fac', out=True), bump.inputs['Height'])
                nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
        except Exception as e:
            print('material extras failed', name, e)
    if alpha < 1:
        for attr, val in (('surface_render_method', 'BLENDED'), ('blend_method', 'BLEND')):
            try:
                setattr(m, attr, val)
            except Exception:
                pass
    m.diffuse_color = (*col, alpha)
    m.roughness = rough
    m.metallic = metal
    _MATS[name] = m
    return m


# --------------------------------------------------------------------------- transforms
def M(loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    r = Euler([math.radians(a) for a in rot], 'XYZ').to_matrix().to_4x4()
    s = Matrix.Diagonal(Vector((scale[0], scale[1], scale[2], 1.0)))
    return Matrix.Translation(Vector(loc)) @ r @ s


I4 = Matrix.Identity(4)


def _vnoise(p):
    return 0.5 + 0.5 * math.sin(p.x * 1.7 + math.sin(p.y * 1.3 + p.z * 0.7) * 2.0) * \
        math.cos(p.y * 1.9 - p.z * 1.1 + math.sin(p.x * 0.9) * 1.5)


def _bevel_sharp(t, off, seg=2, angle=1.0):
    edges = [e for e in t.edges if len(e.link_faces) == 2 and e.calc_face_angle(0) > angle]
    if edges and off > 1e-4:
        bmesh.ops.bevel(t, geom=edges, offset=off, segments=seg, profile=0.5, affect='EDGES', clamp_overlap=True)


# --------------------------------------------------------------------------- part builder
class Part:
    def __init__(self, name, kind='prop', ao=True, ao_h=1.4, tint=0.07, seed=None):
        self.name, self.kind = name, kind
        self.bm = bmesh.new()
        self.col = self.bm.loops.layers.float_color.new('Col')
        self.mats = []
        self.ao, self.ao_h, self.tint = ao, ao_h, tint
        self.rng = random.Random(seed if seed is not None else zlib.crc32(name.encode()) & 0xffff)

    def _mi(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def merge(self, t, m, mtx, smooth=True, recalc=True):
        if recalc:
            bmesh.ops.recalc_face_normals(t, faces=t.faces[:])
        mi = self._mi(m)
        vm = {v: self.bm.verts.new(mtx @ v.co) for v in t.verts}
        tint = 1.0 + self.rng.uniform(-self.tint, self.tint)
        cl = self.col
        for f in t.faces:
            try:
                nf = self.bm.faces.new([vm[v] for v in f.verts])
            except ValueError:
                continue
            nf.material_index = mi
            nf.smooth = True
            nf.normal_update()
            nz = nf.normal.z
            for lp in nf.loops:
                p = lp.vert.co
                if self.ao:
                    ao = 0.58 + 0.42 * min(1.0, max(0.0, p.z / self.ao_h))
                    c = tint * ao * (0.9 + 0.16 * _vnoise(p * 2.3))
                    if nz < -0.5:
                        c *= 0.72
                    elif nz > 0.6:
                        c *= 1.05
                else:
                    c = 1.0
                lp[cl] = (c, c, c, 1.0)
        t.free()

    @staticmethod
    def _jit(t, amt, seed):
        if amt <= 0:
            return
        r = random.Random(seed)
        for v in t.verts:
            v.co += Vector((r.uniform(-amt, amt), r.uniform(-amt, amt), r.uniform(-amt, amt)))

    # ---- primitives (rotations in degrees, `pre` = extra parent matrix)
    def box(self, size, loc, m, rot=(0, 0, 0), bevel=None, pre=None, jitter=0, seed=0, seg=None):
        t = bmesh.new()
        bmesh.ops.create_cube(t, size=1.0)
        bmesh.ops.scale(t, vec=Vector(size), verts=t.verts)
        mn = min(size)
        if bevel is None:
            bevel = min(0.12, mn * 0.22) if mn > 0.03 else 0
        if bevel > 0:
            off = min(bevel, mn * 0.45)
            bmesh.ops.bevel(t, geom=t.verts[:] + t.edges[:], offset=off, segments=seg or (3 if off > 0.09 else 2),
                            profile=0.5, affect='EDGES', clamp_overlap=True)
        self._jit(t, jitter, seed)
        self.merge(t, m, (pre or I4) @ M(loc, rot))

    def cyl(self, r, h, loc, m, rot=(0, 0, 0), seg=12, r2=None, smooth=True, pre=None,
            scale=(1, 1, 1), jitter=0, seed=0, bevel=None):
        t = bmesh.new()
        r2v = r if r2 is None else r2
        bmesh.ops.create_cone(t, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r2v, depth=h)
        if bevel is None:
            bevel = min(0.08, min(r, h) * 0.18) if min(r, h) > 0.04 and r2v > 0.02 else 0
        _bevel_sharp(t, bevel, 2)
        self._jit(t, jitter, seed)
        self.merge(t, m, (pre or I4) @ M(loc, rot, scale))

    def sphere(self, r, loc, m, scale=(1, 1, 1), seg=16, rings=10, smooth=True, rot=(0, 0, 0), pre=None):
        t = bmesh.new()
        bmesh.ops.create_uvsphere(t, u_segments=seg, v_segments=rings, radius=r)
        self.merge(t, m, (pre or I4) @ M(loc, rot, scale))

    def ico(self, r, loc, m, scale=(1, 1, 1), sub=2, jitter=0.0, seed=0, smooth=True, rot=(0, 0, 0), pre=None):
        t = bmesh.new()
        bmesh.ops.create_icosphere(t, subdivisions=sub, radius=r)
        self._jit(t, r * jitter, seed)
        self.merge(t, m, (pre or I4) @ M(loc, rot, scale))

    def torus(self, R, r, loc, m, rot=(0, 0, 0), seg=24, sides=8, smooth=True, pre=None, scale=(1, 1, 1)):
        t = bmesh.new()
        rings = []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            ring = []
            for j in range(sides):
                b = 2 * math.pi * j / sides
                rr = R + r * math.cos(b)
                ring.append(t.verts.new((rr * math.cos(a), rr * math.sin(a), r * math.sin(b))))
            rings.append(ring)
        for i in range(seg):
            for j in range(sides):
                t.faces.new([rings[i][j], rings[(i + 1) % seg][j],
                             rings[(i + 1) % seg][(j + 1) % sides], rings[i][(j + 1) % sides]])
        self.merge(t, m, (pre or I4) @ M(loc, rot, scale))

    def prism(self, pts, depth, loc, m, rot=(0, 0, 0), pre=None, scale=(1, 1, 1), bevel=None):
        """2D polygon in the XZ plane, extruded along Y (centred)."""
        t = bmesh.new()
        f = [t.verts.new((x, -depth / 2, z)) for x, z in pts]
        b = [t.verts.new((x, depth / 2, z)) for x, z in pts]
        n = len(pts)
        t.faces.new(f)
        t.faces.new(b[::-1])
        for i in range(n):
            j = (i + 1) % n
            t.faces.new([f[i], f[j], b[j], b[i]])
        bmesh.ops.recalc_face_normals(t, faces=t.faces[:])
        if bevel is None:
            bevel = min(0.06, depth * 0.2) if depth > 0.05 else 0
        try:
            _bevel_sharp(t, bevel, 2)
        except Exception:
            pass
        self.merge(t, m, (pre or I4) @ M(loc, rot, scale))

    def ring(self, r_in, r_out, depth, loc, m, rot=(0, 0, 0), a0=0, a1=180, seg=16, pre=None, smooth=True, bevel=None):
        """Ring sector in the XZ plane (angles from +X towards +Z), extruded along Y."""
        t = bmesh.new()
        full = abs(a1 - a0) >= 360
        n = seg if full else seg + 1
        fo, fi, bo, bi = [], [], [], []
        for i in range(n):
            a = math.radians(a0 + (a1 - a0) * i / seg)
            c, s = math.cos(a), math.sin(a)
            fo.append(t.verts.new((r_out * c, -depth / 2, r_out * s)))
            fi.append(t.verts.new((r_in * c, -depth / 2, r_in * s)))
            bo.append(t.verts.new((r_out * c, depth / 2, r_out * s)))
            bi.append(t.verts.new((r_in * c, depth / 2, r_in * s)))
        for i in range(seg):
            j = (i + 1) % n if full else i + 1
            t.faces.new([fo[i], fo[j], fi[j], fi[i]])
            t.faces.new([bo[i], bi[i], bi[j], bo[j]])
            t.faces.new([fo[i], bo[i], bo[j], fo[j]])
            t.faces.new([fi[i], fi[j], bi[j], bi[i]])
        if not full:
            t.faces.new([fo[0], fi[0], bi[0], bo[0]])
            t.faces.new([fo[-1], bo[-1], bi[-1], fi[-1]])
        bmesh.ops.recalc_face_normals(t, faces=t.faces[:])
        if bevel is None:
            bevel = min(0.08, (r_out - r_in) * 0.2, depth * 0.2)
        if bevel > 0.005:
            try:
                _bevel_sharp(t, bevel, 2)
            except Exception:
                pass
        self.merge(t, m, (pre or I4) @ M(loc, rot))

    def rod(self, a, b, r, m, seg=8, r2=None, smooth=True):
        """Cylinder between two points."""
        a, b = Vector(a), Vector(b)
        d = b - a
        if d.length < 1e-5:
            return
        t = bmesh.new()
        bmesh.ops.create_cone(t, cap_ends=True, cap_tris=False, segments=seg, radius1=r,
                              radius2=r if r2 is None else r2, depth=d.length)
        q = d.normalized().to_track_quat('Z', 'Y')
        self.merge(t, m, Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4())

    def spiky_cone(self, r, h, loc, m, n=10, inner=0.7, droop=0.25, jitter=0.0, seed=0, rot=(0, 0, 0)):
        """Cone with a jagged star-shaped skirt (pine tiers, snow caps)."""
        t = bmesh.new()
        rr = random.Random(seed)
        apex = t.verts.new((0, 0, h))
        ring = []
        for i in range(2 * n):
            a = 2 * math.pi * i / (2 * n) + rr.uniform(-0.05, 0.05)
            rad = r * (rr.uniform(0.92, 1.05) if i % 2 == 0 else inner)
            z = -droop * h * 0.35 if i % 2 == 0 else 0.0
            ring.append(t.verts.new((rad * math.cos(a), rad * math.sin(a), z)))
        mid = [t.verts.new(((ring[i].co.x * 0.5), ring[i].co.y * 0.5, h * 0.5 + ring[i].co.z * 0.4)) for i in range(2 * n)]
        for i in range(2 * n):
            j = (i + 1) % (2 * n)
            t.faces.new([ring[i], ring[j], mid[j], mid[i]])
            t.faces.new([mid[i], mid[j], apex])
        t.faces.new(ring[::-1])
        self._jit(t, jitter * r, seed)
        self.merge(t, m, M(loc, rot))

    def frond(self, base, yaw, length, m, lift=0.45, droop=1.1, width=0.55, n=12, spine=None, seed=0):
        """Palm / fern frond: drooping spine with paired tapered leaflets (double-sided)."""
        r = random.Random(seed)
        yaw = math.radians(yaw)
        dirh = Vector((math.cos(yaw), math.sin(yaw), 0))
        side = Vector((-math.sin(yaw), math.cos(yaw), 0))
        base = Vector(base)
        pts = [base + dirh * length * (i / n) + Vector((0, 0, lift * length * (i / n) - droop * length * (i / n) ** 2))
               for i in range(n + 1)]
        if spine:
            for i in range(n):
                self.rod(pts[i], pts[i + 1], 0.045 * (1 - i / n) + 0.012, spine, seg=5)
        t = bmesh.new()
        step = length / n
        for i in range(1, n + 1):
            tt = i / n
            p0 = pts[i]
            fwd = (pts[min(i + 1, n)] - pts[i - 1]).normalized()
            w = width * (math.sin(math.pi * min(1.0, tt * 1.1)) * 0.85 + 0.15) * (1.05 - 0.45 * tt)
            for sg in (-1, 1):
                sway = r.uniform(-0.05, 0.05)
                tip = p0 + side * sg * w + fwd * w * 0.55 + Vector((0, 0, -w * (0.45 + sway)))
                a = p0 - fwd * step * 0.55
                b = p0 + fwd * step * 0.45
                c = (p0 + tip) * 0.5 + Vector((0, 0, w * 0.08)) + fwd * step * 0.25
                t.faces.new([t.verts.new(a), t.verts.new(c), t.verts.new(tip), t.verts.new(b)])
        self.merge(t, m, I4, recalc=False)

    def leaf_cards(self, center, rad, mats, n=30, seed=0, size=0.45, flat=0.8):
        """Small diamond leaves scattered on an ellipsoid surface -> broken, leafy silhouette."""
        r = random.Random(seed)
        t_by_mat = {}
        c0 = Vector(center)
        for k in range(n):
            d = Vector((r.gauss(0, 1), r.gauss(0, 1), abs(r.gauss(0, 1)) * 0.9 + 0.1)).normalized()
            p = c0 + Vector((d.x * rad, d.y * rad, d.z * rad * flat))
            u = d.cross(Vector((0, 0, 1)))
            if u.length < 0.1:
                u = Vector((1, 0, 0))
            u.normalize()
            v = d.cross(u).normalized()
            ang = r.uniform(0, math.pi)
            u, v = u * math.cos(ang) + v * math.sin(ang), v * math.cos(ang) - u * math.sin(ang)
            s = size * r.uniform(0.7, 1.3)
            m = r.choice(mats)
            t = t_by_mat.setdefault(m, bmesh.new())
            q = [p - u * s, p + v * s * 0.45 + d * s * 0.3, p + u * s * 1.1 + d * s * 0.25, p - v * s * 0.45 + d * s * 0.3]
            t.faces.new([t.verts.new(x) for x in q])
        for m, t in t_by_mat.items():
            self.merge(t, m, I4, recalc=False)

    def canopy(self, center, rad, mats, seed=0, blobs=5, flat=0.75, cards=40, card_size=0.5):
        r = random.Random(seed)
        cx, cy, cz = center
        for i in range(blobs):
            a = math.radians(i * 360 / blobs + r.uniform(-25, 25))
            d = rad * r.uniform(0.3, 0.6) if i else 0
            s = rad * r.uniform(0.5, 0.72)
            c = (cx + d * math.cos(a), cy + d * math.sin(a), cz + r.uniform(-0.25, 0.5) * rad * 0.4)
            self.ico(1.0, c, r.choice(mats), scale=(s, s, s * flat), sub=2, jitter=0.09, seed=seed + i)
            self.leaf_cards(c, s * 1.02, mats, n=cards // blobs, seed=seed + 31 * i, size=card_size, flat=flat)

    def grid(self, sx, sy, nx, ny, loc, m, jitter_z=0.0, seed=0):
        t = bmesh.new()
        bmesh.ops.create_grid(t, x_segments=nx, y_segments=ny, size=0.5)
        bmesh.ops.scale(t, vec=Vector((sx, sy, 1)), verts=t.verts)
        r = random.Random(seed)
        for v in t.verts:
            v.co.z += r.uniform(-jitter_z, jitter_z)
        self.merge(t, m, M(loc), recalc=False)

    def build(self, coll):
        bm = self.bm
        for e in bm.edges:
            if len(e.link_faces) == 2:
                try:
                    e.smooth = e.calc_face_angle(0) < SHARP_ANGLE
                except Exception:
                    pass
        me = bpy.data.meshes.new(self.name)
        bm.to_mesh(me)
        bm.free()
        for m in self.mats:
            me.materials.append(m)
        try:
            ca = me.color_attributes.get('Col')
            if ca:
                me.color_attributes.active_color = ca
                me.color_attributes.render_color_index = list(me.color_attributes).index(ca)
        except Exception:
            pass
        ob = bpy.data.objects.new(self.name, me)
        ob['asset_kind'] = self.kind
        coll.objects.link(ob)
        return ob


# =========================================================================== generic assets
def star_pts(ro, ri, n=5, rot=90):
    pts = []
    for i in range(n * 2):
        a = math.radians(rot + 180 * i / n)
        r = ro if i % 2 == 0 else ri
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def circle_pts(r, n=16, cx=0, cz=0):
    return [(cx + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def rail_line(p, x, L, rail, plate=None, n=13):
    p.box((0.24, L, 0.035), (x, L / 2, 0.44), rail, bevel=0.01)
    p.box((0.05, L, 0.09), (x, L / 2, 0.5), rail, bevel=0.01)
    p.box((0.12, L, 0.055), (x, L / 2, 0.565), rail, bevel=0.02)
    if plate:
        for k in range(n):
            p.box((0.34, 0.2, 0.025), (x, (k + 0.5) * L / n, 0.43), plate, bevel=0.008)


def track_segment(name, bed, sleeper, rail, side, curb=None, side_w=3.0, side_h=0.5, edge=None, pebbles=True):
    p = Part(name, 'segment', ao_h=0.6, seed=11)
    r = random.Random(11)
    L = SEG
    W = 3 * LANE + 0.6
    p.box((W, L, 0.3), (0, L / 2, 0.15), bed, bevel=0.05)
    n = 13
    plate = mat('tie_plate', '#4a4a50', .6, metal=.6)
    for li in (-1, 0, 1):
        x = li * LANE
        p.box((2.0, L, 0.08), (x, L / 2, 0.32), bed, bevel=0.03)
        for k in range(n):
            p.box((1.85, 0.3, 0.13), (x + r.uniform(-0.03, 0.03), (k + 0.5) * L / n, 0.37), sleeper,
                  rot=(0, 0, r.uniform(-1.5, 1.5)), bevel=0.035, jitter=0.008, seed=k + li * 20)
        for s in (-0.55, 0.55):
            rail_line(p, x + s, L, rail, plate, n)
    if pebbles:
        for k in range(160):
            x = r.choice((-1, 0, 1)) * LANE + r.uniform(-1.1, 1.1)
            p.ico(r.uniform(0.04, 0.08), (x, r.uniform(0, L), 0.33), bed, sub=0, jitter=0.25, seed=k)
    for sg in (-1, 1):
        p.box((side_w, L, side_h), (sg * (W / 2 + side_w / 2), L / 2, side_h / 2), side, bevel=0.06)
        if curb:
            p.box((0.38, L, side_h + 0.08), (sg * (W / 2 + 0.17), L / 2, (side_h + 0.08) / 2), curb, bevel=0.07)
        if edge:
            p.box((0.12, L, 0.04), (sg * (W / 2 + 0.45), L / 2, side_h + 0.02), edge, bevel=0.01)
        for k in range(4):
            p.box((side_w * 0.48, 0.04, 0.02), (sg * (W / 2 + side_w / 2), k * L / 4, side_h + 0.005), bed, bevel=0)
    return p


def stone_path(name, stones, grout, wall, moss=None, trim=None, wall_h=1.0, seed=1, petals=None,
               W=8.4, under=None, cap=None, post_every=3, tile=None, gap_moss=None):
    p = Part(name, 'segment', ao_h=0.9, tint=0.1, seed=seed)
    r = random.Random(seed)
    L = SEG
    p.box((W + 1.8, L, 0.6), (0, L / 2, 0.0), grout, bevel=0.05)
    if under:
        p.box((W + 1.4, L, 3.0), (0, L / 2, -1.8), under, bevel=0.15)
        for k in range(4):
            p.box((W + 1.5, 0.12, 0.3), (0, k * L / 4 + 1.2, -0.6 - r.uniform(0, 1.5)), grout)
    y = 0.0
    while y < L - 0.05:
        h = min(r.uniform(*(tile or (0.9, 1.5))), L - y)
        x = -W / 2
        while x < W / 2 - 0.05:
            w = min(r.uniform((tile or (0.9, 1.5))[0], (tile or (0.9, 1.5))[1] * 1.15), W / 2 - x)
            if w > 0.25 and h > 0.25:
                p.box((w - 0.1, h - 0.1, 0.16), (x + w / 2, y + h / 2, 0.37 + r.uniform(-0.02, 0.02)),
                      r.choice(stones), rot=(r.uniform(-0.8, 0.8), r.uniform(-0.8, 0.8), r.uniform(-2, 2)),
                      bevel=0.06, seg=3, jitter=0.018, seed=int(x * 100 + y * 1000))
                if gap_moss and r.random() < 0.35:
                    p.ico(1.0, (x + w * r.choice((0.02, 0.98)), y + h / 2, 0.42), gap_moss, scale=(0.08, h * 0.45, 0.04), sub=1, jitter=0.2, seed=r.randint(0, 999))
                if r.random() < 0.12:
                    p.box((r.uniform(0.25, 0.5), 0.03, 0.02), (x + w / 2, y + h / 2, 0.455), grout,
                          rot=(0, 0, r.uniform(0, 180)), bevel=0)
            x += w
        y += h
    for sg in (-1, 1):
        wx = sg * (W / 2 + 0.45)
        yy = 0.0
        while yy < L - 0.05:
            bl = min(r.uniform(0.9, 1.6), L - yy)
            bh = wall_h + r.uniform(-0.12, 0.12)
            p.box((0.8, bl - 0.07, bh), (wx, yy + bl / 2, 0.3 + bh / 2), r.choice([wall] + stones[:1]), bevel=0.09,
                  seg=3, jitter=0.02, seed=int(yy * 77) + sg)
            if moss and r.random() < 0.45:
                p.ico(1.0, (wx + r.uniform(-0.2, 0.2), yy + bl / 2, 0.3 + bh), moss, scale=(0.4, bl * 0.35, 0.09),
                      sub=2, jitter=0.15, seed=int(yy * 13))
            yy += bl
        for k in range(post_every):
            py = (k + 0.5) * L / post_every
            p.box((1.05, 1.05, wall_h + 0.55), (wx, py, 0.3 + (wall_h + 0.55) / 2), wall, bevel=0.1, seg=3)
            p.box((1.3, 1.3, 0.22), (wx, py, 0.3 + wall_h + 0.66), cap or wall, bevel=0.08, seg=3)
            p.box((1.12, 1.12, 0.12), (wx, py, 0.36), cap or wall, bevel=0.04)
            for face in (-1, 1):
                p.box((0.08, 0.5, 0.5), (wx + face * 0.53, py, 0.3 + wall_h * 0.6), cap or grout, bevel=0.03)
        if trim:
            p.box((0.16, L, 0.1), (sg * (W / 2 + 0.02), L / 2, 0.42), trim, bevel=0.03)
            p.box((0.86, L, 0.06), (wx, L / 2, 0.3 + wall_h - 0.1), trim, bevel=0.02)
        if moss:
            for _ in range(3):
                p.ico(1.0, (sg * (W / 2 - r.uniform(0.2, 0.8)), r.uniform(0.5, L - 0.5), 0.44), moss,
                      scale=(r.uniform(0.2, 0.45), r.uniform(0.3, 0.7), 0.04), sub=2, jitter=0.2, seed=r.randint(0, 999))
    if petals:
        for _ in range(70):
            p.box((0.14, 0.09, 0.012), (r.uniform(-W / 2, W / 2), r.uniform(0, L), 0.458),
                  r.choice(petals), rot=(r.uniform(-8, 8), 0, r.uniform(0, 180)), bevel=0)
    return p


def coin(name, face, rim, emb, emblem='star', dark=None):
    p = Part(name, 'coin', ao=False)
    R, T = 0.42, 0.09
    p.cyl(R, T, (0, 0, 0), face, rot=(90, 0, 0), seg=40, bevel=0.03)
    p.torus(R, 0.06, (0, 0, 0), rim, rot=(90, 0, 0), seg=40, sides=10)
    p.torus(R * 0.78, 0.018, (0, 0, 0), rim, rot=(90, 0, 0), seg=36, sides=6, scale=(1, 1, 2.6))
    for sg in (-1, 1):
        y = sg * (T / 2 + 0.015)
        d = 0.045
        if emblem == 'star':
            p.prism(star_pts(0.24, 0.1), d, (0, y, 0), emb, bevel=0.012)
        elif emblem == 'square':
            for (sx, sz, x, z) in ((0.36, 0.06, 0, 0.15), (0.36, 0.06, 0, -0.15), (0.06, 0.36, 0.15, 0), (0.06, 0.36, -0.15, 0)):
                p.box((sx, d, sz), (x, y, z), emb, bevel=0.012)
            p.box((0.22, d * 0.5, 0.22), (0, y, 0), dark or emb, bevel=0.01)
            for a in range(4):
                p.sphere(0.035, (0.27 * math.cos(math.radians(45 + 90 * a)), y, 0.27 * math.sin(math.radians(45 + 90 * a))), emb, seg=8, rings=5)
        elif emblem == 'snowflake':
            for a in (0, 60, 120):
                p.box((0.5, d, 0.05), (0, y, 0), emb, rot=(0, a, 0), bevel=0.012)
            for a in range(6):
                ang = math.radians(a * 60)
                p.box((0.09, d, 0.09), (0.25 * math.cos(ang), y, 0.25 * math.sin(ang)), emb, rot=(0, 45 - a * 60, 0), bevel=0.012)
        elif emblem == 'bolt':
            p.prism([(0.05, 0.28), (-0.14, -0.02), (-0.01, -0.02), (-0.07, -0.28), (0.15, 0.04), (0.02, 0.04)], d, (0, y, 0), emb, bevel=0.01)
        elif emblem == 'leaf':
            pts = [(0.24 * math.sin(math.pi * i / 10), 0.28 * math.cos(math.pi * i / 10)) for i in range(11)]
            pts += [(-0.16 * math.sin(math.pi * i / 10), 0.28 * math.cos(math.pi * i / 10)) for i in range(9, 0, -1)]
            p.prism(pts, d, (0, y, 0.02), emb, rot=(0, 25, 0), bevel=0.012)
            p.box((0.03, d, 0.14), (-0.09, y, -0.24), emb, rot=(0, 25, 0), bevel=0.008)
        elif emblem == 'sun':
            p.cyl(0.13, d, (0, y, 0), emb, rot=(90, 0, 0), seg=20, bevel=0.012)
            for a in range(8):
                ang = math.radians(a * 45)
                p.prism([(-0.04, 0), (0.04, 0), (0, 0.1)], d, (0.17 * math.cos(ang), y, 0.17 * math.sin(ang)), emb,
                        rot=(0, 90 - a * 45, 0), bevel=0.008)
        elif emblem == 'flower':
            for a in range(5):
                ang = math.radians(90 + a * 72)
                p.cyl(0.1, d, (0.14 * math.cos(ang), y, 0.14 * math.sin(ang)), emb, rot=(90, 0, 0), seg=14, bevel=0.012)
            p.cyl(0.07, d * 1.4, (0, y, 0), dark or rim, rot=(90, 0, 0), seg=12, bevel=0.012)
        elif emblem == 'shell':
            pts = [(0.27 * math.cos(math.radians(a)), -0.12 + 0.3 * math.sin(math.radians(a))) for a in range(0, 181, 15)]
            pts += [(-0.06, -0.2), (0.06, -0.2)]
            p.prism(pts, d, (0, y, 0), emb, bevel=0.012)
            for a in range(20, 170, 30):
                ang = math.radians(a)
                p.box((0.025, d * 1.5, 0.28), (0.12 * math.cos(ang), y, -0.12 + 0.14 * math.sin(ang)), dark or rim,
                      rot=(0, 90 - a, 0), bevel=0.008)
        elif emblem == 'diamond':
            p.prism([(0, 0.28), (0.2, 0.08), (0, -0.28), (-0.2, 0.08)], d, (0, y, 0), emb, bevel=0.012)
            p.prism([(0, 0.08), (0.1, 0.0), (0, -0.16), (-0.1, 0.0)], d * 1.5, (0, y, 0), dark or rim, bevel=0.01)
        elif emblem == 'glyph':
            for (sx, sz, x, z) in ((0.34, 0.06, 0, 0.16), (0.06, 0.34, -0.14, 0), (0.28, 0.06, 0.03, -0.16),
                                   (0.06, 0.18, 0.14, -0.09), (0.16, 0.06, 0.08, 0.0)):
                p.box((sx, d, sz), (x, y, z), emb, bevel=0.012)
    return p


def train(name, body, stripe, roof, window, light, under, L=12.0, W=2.5, H=2.8, door=None, stripe2=None):
    p = Part(name, 'obstacle_train', ao_h=1.2)
    z0 = 0.55
    frame = mat('train_frame_' + name, '#2b2e33', .5, metal=.5)
    chrome = mat('train_chrome', '#cfd6de', .2, metal=1)
    p.box((W - 0.4, L - 0.6, 0.45), (0, 0, 0.5), under, bevel=0.06)
    for yb in (-L / 2 + 2.0, L / 2 - 2.0):
        p.box((W - 0.3, 2.6, 0.35), (0, yb, 0.42), frame, bevel=0.06)
        for y in (yb - 0.6, yb + 0.6):
            for x in (-0.62, 0.62):
                p.cyl(0.36, 0.16, (x, y, 0.38), under, rot=(0, 90, 0), seg=18)
                p.cyl(0.2, 0.2, (x, y, 0.38), chrome, rot=(0, 90, 0), seg=12)
    # body: big rounded shell + a rounded nose
    p.box((W, L - 1.2, H), (0, 0.6, z0 + H / 2), body, bevel=0.32, seg=4)
    p.box((W, 1.8, H - 0.2), (0, -L / 2 + 0.9, z0 + (H - 0.2) / 2), body, bevel=0.55, seg=5)
    p.box((W + 0.04, L - 0.6, 0.32), (0, 0, z0 + 0.75), stripe, bevel=0.06)
    if stripe2:
        p.box((W + 0.05, L - 0.6, 0.1), (0, 0, z0 + 1.18), stripe2, bevel=0.03)
    p.box((W - 0.3, L - 1.0, 0.32), (0, 0.2, z0 + H + 0.06), roof, bevel=0.14, seg=3)
    for yv in (-2.5, 0.5, 3.5):
        p.box((1.0, 1.4, 0.3), (0, yv, z0 + H + 0.3), roof, bevel=0.1, seg=3)
        for k in range(4):
            p.box((0.9, 0.04, 0.05), (0, yv - 0.45 + k * 0.3, z0 + H + 0.46), frame, bevel=0)
    n = 5
    for i in range(n):
        y = -L / 2 + 2.3 + i * (L - 4.2) / (n - 1)
        for sg in (-1, 1):
            p.box((0.07, 1.22, 1.02), (sg * (W / 2 + 0.01), y, z0 + 1.85), frame, bevel=0.1, seg=3)
            p.box((0.09, 1.05, 0.86), (sg * (W / 2 + 0.02), y, z0 + 1.85), window, bevel=0.09, seg=3)
            p.box((0.1, 0.5, 0.06), (sg * (W / 2 + 0.03), y - 0.2, z0 + 2.15), mat('glass_glint', '#ffffff', .1, emit=0.6), bevel=0.02)
    for y in (-L / 4, L / 4):
        for sg in (-1, 1):
            p.box((0.06, 1.35, 2.15), (sg * (W / 2 + 0.008), y + 1.0, z0 + 1.3), door or stripe, bevel=0.08)
            p.box((0.08, 0.04, 1.9), (sg * (W / 2 + 0.03), y + 1.0, z0 + 1.3), frame, bevel=0)
            p.box((0.09, 0.45, 0.6), (sg * (W / 2 + 0.03), y + 1.0 - 0.35, z0 + 1.95), window, bevel=0.05)
            p.box((0.09, 0.45, 0.6), (sg * (W / 2 + 0.03), y + 1.0 + 0.35, z0 + 1.95), window, bevel=0.05)
    yf = -L / 2 - 0.02
    p.box((W - 0.5, 0.14, 1.1), (0, yf + 0.06, z0 + 1.95), window, bevel=0.16, seg=3)
    p.box((W - 0.4, 0.1, 0.06), (0, yf + 0.02, z0 + 2.52), frame, bevel=0)
    p.box((0.06, 0.1, 1.1), (0, yf + 0.02, z0 + 1.95), frame, bevel=0)
    for x in (-0.55, 0.55):
        p.rod((x, yf - 0.02, z0 + 1.5), (x + 0.25, yf - 0.02, z0 + 2.2), 0.02, frame, seg=4)
    p.box((W - 0.2, 0.1, 0.36), (0, yf + 0.03, z0 + 1.2), stripe, bevel=0.06)
    for x in (-0.8, 0.8):
        p.cyl(0.2, 0.08, (x, yf, z0 + 0.62), chrome, rot=(90, 0, 0), seg=18)
        p.cyl(0.15, 0.1, (x, yf - 0.02, z0 + 0.62), light, rot=(90, 0, 0), seg=16)
    p.box((W - 0.1, 0.35, 0.34), (0, yf - 0.08, z0 + 0.16), under, bevel=0.1, seg=3)
    p.box((0.9, 0.12, 0.26), (0, yf + 0.02, z0 + 2.72), light, bevel=0.06)
    for sg in (-1, 1):
        p.rod((sg * (W / 2), yf + 0.4, z0 + 2.0), (sg * (W / 2 + 0.25), yf + 0.3, z0 + 2.0), 0.03, frame, seg=5)
        p.box((0.08, 0.15, 0.3), (sg * (W / 2 + 0.28), yf + 0.3, z0 + 2.0), frame, bevel=0.03)
        p.rod((sg * (W / 2 + 0.03), yf + 1.8, z0 + 0.9), (sg * (W / 2 + 0.03), yf + 1.8, z0 + 2.4), 0.025, chrome, seg=5)
    p.box((0.12, 1.4, 0.08), (0, 0, z0 + H + 0.98), frame, bevel=0)
    p.rod((0, -0.6, z0 + H + 0.25), (0, 0, z0 + H + 0.98), 0.04, frame)
    p.rod((0, 0.6, z0 + H + 0.25), (0, 0, z0 + H + 0.98), 0.04, frame)
    return p


def ramp(name, body, stripe, top):
    p = Part(name, 'ramp')
    Lr, H = 6.0, 3.3
    p.prism([(-Lr / 2, 0), (Lr / 2, 0), (Lr / 2, H)], 2.3, (0, 0, 0), body, rot=(0, 0, 90), bevel=0.06)
    a = math.degrees(math.atan2(H, Lr))
    for i in range(8):
        t = (i + 0.5) / 8
        p.box((2.32, 0.3, 0.05), (0, -Lr / 2 + t * Lr, t * H + 0.03), stripe if i % 2 else top, rot=(a, 0, 0), bevel=0.02)
    for sg in (-1, 1):
        p.rod((sg * 1.18, -Lr / 2, 0.1), (sg * 1.18, Lr / 2, H + 0.1), 0.05, top, seg=6)
    return p


def barrier_low(name, a, b, leg, light=None, kind='obstacle_low'):
    p = Part(name, kind)
    for x in (-1.0, 1.0):
        p.box((0.16, 0.9, 0.12), (x, 0, 0.06), leg)
        p.box((0.12, 0.12, 1.0), (x, 0, 0.5), leg)
        p.rod((x, -0.4, 0.1), (x, 0, 0.7), 0.04, leg, seg=6)
        p.rod((x, 0.4, 0.1), (x, 0, 0.7), 0.04, leg, seg=6)
    n = 6
    for i in range(n):
        p.box((2.3 / n + 0.005, 0.12, 0.42), (-1.15 + (i + 0.5) * 2.3 / n, -0.08, 0.8), a if i % 2 == 0 else b, bevel=0.015)
        p.box((2.3 / n + 0.005, 0.1, 0.22), (-1.15 + (i + 0.5) * 2.3 / n, -0.08, 0.35), b if i % 2 == 0 else a, bevel=0.015)
    if light:
        for x in (-0.9, 0.9):
            p.cyl(0.08, 0.14, (x, -0.08, 1.09), light, seg=14)
    return p


def barrier_high(name, post, a, b, sign=None, light=None):
    p = Part(name, 'obstacle_high')
    for x in (-1.15, 1.15):
        p.box((0.18, 0.18, 2.7), (x, 0, 1.35), post)
        p.box((0.45, 0.55, 0.14), (x, 0, 0.07), post)
    n = 6
    for i in range(n):
        p.box((2.3 / n + 0.005, 0.14, 0.75), (-1.15 + (i + 0.5) * 2.3 / n, -0.1, 2.0), a if i % 2 == 0 else b, bevel=0.02)
    p.box((2.45, 0.16, 0.08), (0, -0.1, 2.4), post, bevel=0.02)
    p.box((2.45, 0.16, 0.08), (0, -0.1, 1.6), post, bevel=0.02)
    if sign:
        p.box((0.9, 0.08, 0.55), (0, -0.2, 2.75), sign, bevel=0.03)
    if light:
        for x in (-1.15, 1.15):
            p.sphere(0.11, (x, 0, 2.8), light)
    return p


def palm(name, trunk, trunk2, leaf, leaf2, h=6.5, seed=0, nuts=None):
    p = Part(name, ao_h=2.0)
    r = random.Random(seed)
    segs = 12
    lean = r.uniform(0.6, 1.4)
    ang = math.radians(r.uniform(0, 360))
    pts = []
    for i in range(segs + 1):
        t = i / segs
        off = lean * t * t
        pts.append(Vector((off * math.cos(ang), off * math.sin(ang), h * t)))
    for i in range(segs):
        t = i / segs
        rr = 0.32 - 0.14 * t
        p.rod(pts[i], pts[i + 1] + (pts[i + 1] - pts[i]) * 0.05, rr, trunk if i % 2 == 0 else trunk2, seg=10, r2=rr * 0.8)
    p.cyl(0.42, 0.5, (0, 0, 0.2), trunk2, seg=10, r2=0.3, jitter=0.03)
    top = pts[-1]
    p.sphere(0.32, top, trunk2, scale=(1, 1, 0.8))
    nl = 11
    for i in range(nl):
        a = i * 360 / nl + r.uniform(-10, 10)
        up = i % 3 == 0
        p.frond(top, a, r.uniform(2.6, 3.4), leaf if i % 2 == 0 else leaf2, lift=0.65 if up else 0.4,
                droop=0.95 if up else 1.15, width=0.62, n=12, spine=trunk2, seed=seed * 10 + i)
    for i in range(3):
        a = math.radians(i * 120 + 30)
        p.sphere(0.17, (top.x + 0.27 * math.cos(a), top.y + 0.27 * math.sin(a), top.z - 0.25), nuts or trunk2, seg=10, rings=7)
    return p


def round_tree(name, trunk, fol, h=5.0, rad=2.3, seed=0, blobs=7, flat=0.75, branches=2):
    p = Part(name, ao_h=2.5)
    r = random.Random(seed)
    pts = [Vector((0, 0, 0))]
    for i in range(1, 6):
        pts.append(Vector((r.uniform(-0.15, 0.15), r.uniform(-0.15, 0.15), h * i / 5)))
    for i in range(5):
        rr = 0.42 - 0.2 * i / 5
        p.rod(pts[i], pts[i + 1] + Vector((0, 0, 0.05)), rr, trunk, seg=10, r2=rr * 0.85)
    for k in range(4):
        a = math.radians(k * 90 + r.uniform(0, 40))
        p.rod((0, 0, 0.5), (1.0 * math.cos(a), 1.0 * math.sin(a), 0.0), 0.2, trunk, seg=8, r2=0.06)
    tips = []
    for k in range(branches + 2):
        a = math.radians(k * 360 / (branches + 2) + r.uniform(-20, 20))
        tip = Vector((rad * 0.55 * math.cos(a), rad * 0.55 * math.sin(a), h * r.uniform(0.85, 1.0)))
        p.rod(pts[3], tip, 0.15, trunk, seg=8, r2=0.07)
        tips.append(tip)
    p.canopy((0, 0, h + rad * 0.15), rad, fol, seed=seed, blobs=blobs, flat=flat, cards=70, card_size=rad * 0.2)
    for i, tip in enumerate(tips):
        s = rad * 0.45
        p.ico(1.0, tip + Vector((0, 0, 0.2)), r.choice(fol), scale=(s, s, s * flat), sub=2, jitter=0.1, seed=seed + 70 + i)
        p.leaf_cards(tip + Vector((0, 0, 0.2)), s, fol, n=10, seed=seed + 90 + i, size=rad * 0.18, flat=flat)
    return p


def pine(name, trunk, fol, snow=None, h=7.0, seed=0, tiers=4):
    p = Part(name, ao_h=2.0)
    p.cyl(0.28, h * 0.35, (0, 0, h * 0.17), trunk, seg=10, r2=0.2)
    z = h * 0.2
    th = (h - z) / tiers * 1.4
    for i in range(tiers):
        t = i / tiers
        rad = (1 - t * 0.72) * h * 0.32
        p.spiky_cone(rad, th, (0, 0, z), fol, n=11, inner=0.72, droop=0.35, jitter=0.03, seed=seed + i, rot=(0, 0, i * 17))
        if snow:
            p.spiky_cone(rad * 0.86, th * 0.78, (0, 0, z + th * 0.24), snow, n=11, inner=0.6, droop=0.3,
                         jitter=0.02, seed=seed + i + 20, rot=(0, 0, i * 17 + 8))
        z += th * 0.6
    if snow:
        p.sphere(0.25, (0, 0, z + th * 0.25), snow)
    return p


def bush(name, fol, seed=0, fronds=9, size=1.0, flower=None):
    p = Part(name, ao_h=0.8)
    r = random.Random(seed)
    for i in range(fronds + 3):
        a = i * 360 / (fronds + 3) + r.uniform(-15, 15)
        p.frond((0, 0, 0.1), a, size * r.uniform(1.1, 1.6), r.choice(fol), lift=r.uniform(0.9, 1.4), droop=1.2,
                width=0.32 * size, n=10, seed=seed * 7 + i)
    p.ico(0.3 * size, (0, 0, 0.15 * size), fol[0], sub=2, jitter=0.15, seed=seed)
    if flower:
        for i in range(5):
            a = math.radians(r.uniform(0, 360))
            p.ico(0.12 * size, (0.5 * size * math.cos(a), 0.5 * size * math.sin(a), 0.55 * size), flower, sub=2)
    return p


def blob_bush(name, fol, seed=0, size=1.0, flower=None):
    p = Part(name, ao_h=1.0)
    r = random.Random(seed)
    for i in range(5):
        a = math.radians(i * 72 + r.uniform(-20, 20))
        s = size * r.uniform(0.5, 0.8)
        c = (size * 0.5 * math.cos(a), size * 0.5 * math.sin(a), s * 0.6)
        p.ico(1.0, c, r.choice(fol), scale=(s, s, s * 0.85), sub=2, jitter=0.1, seed=seed + i)
        p.leaf_cards(c, s, fol, n=12, seed=seed + 40 + i, size=size * 0.22, flat=0.85)
    if flower:
        for i in range(14):
            a = math.radians(r.uniform(0, 360))
            p.ico(0.11, (size * 0.9 * math.cos(a), size * 0.9 * math.sin(a), size * r.uniform(0.5, 1.1)), flower, sub=1)
    return p


def rock(name, mats, size=1.2, seed=0, moss=None, n=3, kind='prop'):
    p = Part(name, kind, ao_h=size)
    r = random.Random(seed)
    for i in range(n):
        s = size * (1.0 if i == 0 else r.uniform(0.4, 0.65))
        a = math.radians(r.uniform(0, 360))
        d = 0 if i == 0 else size * 0.9
        loc = (d * math.cos(a), d * math.sin(a), s * 0.42)
        p.ico(s, loc, r.choice(mats), scale=(1, r.uniform(0.8, 1.2), 0.72), sub=2, jitter=0.12, seed=seed + i)
        if moss and i == 0:
            p.ico(s * 0.82, (loc[0], loc[1], loc[2] + s * 0.42), moss, scale=(1, 1, 0.25), sub=2, jitter=0.12, seed=seed + 9)
    return p


def cliff(name, mats, w=8, d=6, h=12, seed=0, top=None, layer=1.8, shrink=0.25):
    """Organic rock massif: overlapping lumpy boulders in horizontal strata."""
    p = Part(name, 'backdrop', ao_h=h * 0.4, tint=0.1)
    r = random.Random(seed)
    n = max(2, int(h / layer))
    z = 0
    for i in range(n):
        f = 1 - shrink * i / n
        lh = h / n
        m = mats[i % len(mats)]
        p.box((w * f * r.uniform(0.92, 1.05), d * f * r.uniform(0.92, 1.05), lh * 1.04),
              (r.uniform(-0.3, 0.3), r.uniform(-0.3, 0.3), z + lh / 2), m, bevel=min(0.5, lh * 0.3), seg=3,
              jitter=0.14, seed=seed + i)
        for k in range(4):
            s = r.uniform(0.8, 1.6) * lh * 0.6
            ang = r.uniform(0, 2 * math.pi)
            p.ico(1.0, (math.cos(ang) * w * f * 0.48, math.sin(ang) * d * f * 0.48, z + lh * r.uniform(0.3, 0.7)),
                  mats[(i + k) % len(mats)], scale=(s * 1.4, s, s * 0.8), sub=2, jitter=0.15, seed=seed + i * 7 + k)
        z += lh
    if top:
        for i in range(7):
            s = r.uniform(1.2, 2.2)
            c = (r.uniform(-w / 3, w / 3), r.uniform(-d / 3, d / 3), h + s * 0.3)
            p.ico(s, c, r.choice(top), scale=(1, 1, 0.7), sub=2, jitter=0.1, seed=seed + 30 + i)
            p.leaf_cards(c, s, top, n=12, seed=seed + 60 + i, size=0.5, flat=0.7)
        for i in range(6):
            x = r.uniform(-w / 2.2, w / 2.2)
            for j in range(r.randint(4, 9)):
                p.box((0.12, 0.08, 0.5), (x, -d * (1 - shrink) / 2 - 0.3, h - 0.3 - j * 0.45), top[0], bevel=0.02)
    return p


def waterfall(name, rocks, water, foam, h=14, w=4, top=None, seed=4):
    p = Part(name, 'backdrop', ao_h=h * 0.3)
    r = random.Random(seed)
    for sg in (-1, 1):
        p.box((4, 5, h), (sg * (w / 2 + 2), 0.5, h / 2), rocks[0], bevel=0.6, seg=3, jitter=0.18, seed=seed + sg)
        p.box((3, 4, h * 0.7), (sg * (w / 2 + 3.5), -0.5, h * 0.35), rocks[-1], bevel=0.6, seg=3, jitter=0.18, seed=seed + 3 * sg)
        for k in range(5):
            s = r.uniform(0.8, 1.5)
            p.ico(s, (sg * (w / 2 + r.uniform(0.5, 3)), -2.2, r.uniform(0, h)), rocks[k % len(rocks)], scale=(1, 0.7, 1.2),
                  sub=2, jitter=0.15, seed=seed + k * 3 + sg)
    p.box((w + 1, 4, h), (0, 1.8, h / 2), rocks[-1])
    for k in range(5):
        p.box((w / 5 - 0.05, 0.3 + r.uniform(0, 0.15), h), (-w / 2 + (k + 0.5) * w / 5, -0.2 - r.uniform(0, 0.15), h / 2),
              water if k % 2 else foam, bevel=0.12)
    p.cyl(w * 1.1, 0.2, (0, -2.0, 0.1), water, seg=24)
    for i in range(14):
        p.sphere(r.uniform(0.4, 0.9), (r.uniform(-w / 2, w / 2), r.uniform(-1.5, -0.3), 0.3), foam, scale=(1, 1, 0.6), seg=12, rings=7)
    if top:
        for i in range(7):
            s = r.uniform(1.2, 2.0)
            c = (r.uniform(-w, w), r.uniform(0, 3), h + s * 0.3)
            p.ico(s, c, r.choice(top), scale=(1, 1, 0.7), sub=2, jitter=0.1, seed=seed + 40 + i)
            p.leaf_cards(c, s, top, n=12, seed=seed + 70 + i, size=0.5)
    return p


def arched_wall(p, W, H, D, rect_h, rad, wall, frame, dark, depth_dark=None):
    """Wall with an arched opening centred on x=0, front face at y=-D/2."""
    side_w = W / 2 - rad
    for sg in (-1, 1):
        p.box((side_w, D, H), (sg * (rad + side_w / 2), 0, H / 2), wall, bevel=0.15)
    top = rect_h + rad
    if H > top:
        p.box((2 * rad, D, H - top), (0, 0, top + (H - top) / 2), wall, bevel=0.1)
    for sg in (-1, 1):
        pts = [(sg * rad * math.cos(math.radians(90 * i / 8)), rect_h + rad * math.sin(math.radians(90 * i / 8)))
               for i in range(9)]
        p.prism(pts + [(sg * rad, top)], D, (0, 0, 0), wall, bevel=0)
    p.ring(rad - 0.05, rad + 0.55, D + 0.25, (0, 0, rect_h), frame, a0=0, a1=180, seg=18)
    for k in range(9):
        a = math.radians(k * 180 / 8)
        p.box((0.25, D + 0.35, 0.65), ((rad + 0.25) * math.cos(a), 0, rect_h + (rad + 0.25) * math.sin(a)), frame,
              rot=(0, 90 - k * 180 / 8, 0), bevel=0.06)
    for sg in (-1, 1):
        p.box((0.6, D + 0.25, rect_h), (sg * (rad + 0.25), 0, rect_h / 2), frame, bevel=0.08)
    p.box((1.0, D + 0.45, 1.0), (0, 0, top + 0.25), frame, bevel=0.12)
    dd = depth_dark or D * 0.8
    p.box((2 * rad, dd, rect_h), (0, D / 2 - dd / 2 + 0.3, rect_h / 2), dark, bevel=0)
    p.ring(0.0001, rad, dd, (0, D / 2 - dd / 2 + 0.3, rect_h), dark, a0=0, a1=180, seg=18, bevel=0)


def cloud(name, m, m2, seed=0, size=3.0):
    p = Part(name, 'backdrop', ao=False)
    r = random.Random(seed)
    for i in range(11):
        s = size * r.uniform(0.35, 0.75)
        p.sphere(s, (r.uniform(-size * 1.3, size * 1.3), r.uniform(-size * 0.4, size * 0.4), r.uniform(0, size * 0.45) * (1 - abs(i - 5) / 8)),
                 m if i % 3 else m2, scale=(1, 0.9, 0.75), seg=16, rings=10)
    return p


def flame(p, base, size, fire, fire2):
    x, y, z = base
    p.ico(0.5 * size, (x, y, z + 0.25 * size), fire, scale=(1, 1, 0.8), sub=2)
    p.cyl(0.42 * size, 1.1 * size, (x, y, z + 0.75 * size), fire, seg=10, r2=0.0, jitter=0.04 * size, seed=3)
    for k in range(3):
        a = math.radians(k * 120)
        p.cyl(0.18 * size, 0.6 * size, (x + 0.25 * size * math.cos(a), y + 0.25 * size * math.sin(a), z + 0.55 * size), fire,
              seg=8, r2=0.0, rot=(math.cos(a) * 15, math.sin(a) * 15, 0))
    p.cyl(0.25 * size, 0.8 * size, (x, y, z + 0.55 * size), fire2, seg=8, r2=0.0)


def torch(name, stone, bowl, fire, fire2, wood=None, h=1.4):
    p = Part(name)
    p.box((0.5, 0.5, 0.2), (0, 0, 0.1), stone, bevel=0.06)
    p.cyl(0.12, h, (0, 0, h / 2 + 0.2), wood or stone, seg=10)
    p.torus(0.14, 0.04, (0, 0, h * 0.6), bowl, seg=12, sides=6)
    p.cyl(0.18, 0.3, (0, 0, h + 0.3), bowl, seg=14, r2=0.36)
    p.torus(0.36, 0.04, (0, 0, h + 0.45), bowl, seg=16, sides=6)
    flame(p, (0, 0, h + 0.42), 0.5, fire, fire2)
    return p


def brazier(name, stone, bowl, fire, fire2):
    p = Part(name)
    p.box((0.8, 0.8, 0.3), (0, 0, 0.15), stone, bevel=0.07)
    p.cyl(0.25, 0.9, (0, 0, 0.75), stone, seg=10)
    for k in range(3):
        a = math.radians(k * 120)
        p.rod((0.5 * math.cos(a), 0.5 * math.sin(a), 1.25), (0.2 * math.cos(a), 0.2 * math.sin(a), 0.9), 0.04, bowl, seg=6)
    p.cyl(0.3, 0.45, (0, 0, 1.4), bowl, seg=16, r2=0.75)
    p.torus(0.75, 0.07, (0, 0, 1.62), bowl, seg=20, sides=8)
    flame(p, (0, 0, 1.6), 1.1, fire, fire2)
    return p


def fire_lights_offset():
    return (0, 0, 2.2)
