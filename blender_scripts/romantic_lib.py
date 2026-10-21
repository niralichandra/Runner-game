"""Romantic / dreamy asset kit for the second map set (hearts, flowers, lanterns, power-ups, ...).

Built on lib.Part, so everything gets rounded bevels, baked vertex colour and texture baking.
Orientation conventions are the same as lib.py: runner moves along +Y, pickups face -Y.
"""
import math, random
from mathutils import Vector, Matrix
from lib import *


# --------------------------------------------------------------------------- shapes
def heart_pts(s=1.0, n=36):
    """Heart outline in the XZ plane, about s wide, centred."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        z = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x * s / 32, (z + 2.5) * s / 32))
    return pts


def heart(p, loc, size, depth, m, rot=(0, 0, 0), puffy=True, pre=None):
    p.prism(heart_pts(size), depth, loc, m, rot=rot, pre=pre, bevel=depth * (0.42 if puffy else 0.15))


def heart_outline(p, loc, size, r, m, rot=(0, 0, 0), n=36):
    pts = heart_pts(size, n)
    mtx = M(loc, rot)
    for i in range(n):
        a = mtx @ Vector((pts[i][0], 0, pts[i][1]))
        b = mtx @ Vector((pts[(i + 1) % n][0], 0, pts[(i + 1) % n][1]))
        p.rod(a, b, r, m, seg=6)


def hibiscus(p, loc, size, petal, center, yaw=0.0, tilt=25.0, seed=0):
    """Five round petals + stamen, facing up/outwards."""
    pre = M(loc, (tilt, 0, yaw))
    for k in range(5):
        a = math.radians(k * 72)
        p.sphere(size * 0.5, (math.cos(a) * size * 0.45, math.sin(a) * size * 0.45, 0), petal,
                 scale=(1.0, 0.8, 0.22), rot=(0, 0, k * 72), seg=12, rings=6, pre=pre)
    p.sphere(size * 0.2, (0, 0, size * 0.06), center, seg=10, rings=6, pre=pre)
    p.cyl(size * 0.04, size * 0.6, (0, 0, size * 0.3), center, seg=6, pre=pre)
    p.sphere(size * 0.08, (0, 0, size * 0.62), center, seg=8, rings=5, pre=pre)


def flowers_on(p, center, rad, petals, centers, n=8, size=0.35, seed=0, flat=0.8):
    r = random.Random(seed)
    for k in range(n):
        d = Vector((r.gauss(0, 1), r.gauss(0, 1), abs(r.gauss(0, 1)) + 0.3)).normalized()
        loc = Vector(center) + Vector((d.x * rad, d.y * rad, d.z * rad * flat))
        hibiscus(p, loc, size * r.uniform(0.8, 1.2), r.choice(petals), r.choice(centers),
                 yaw=math.degrees(math.atan2(d.y, d.x)) - 90, tilt=r.uniform(10, 60), seed=seed + k)


def gore_balloon(p, r, loc, mats, gores=12, rings=14):
    """Hot-air-balloon envelope (teardrop) with coloured vertical gores."""
    cx, cy, cz = loc
    verts = []
    for j in range(rings + 1):
        phi = math.pi * j / rings
        z = -math.cos(phi)
        rad = math.sin(phi) * (0.55 + 0.45 * (1 - (1 - phi / math.pi) ** 1.6))
        verts.append((rad, z))
    for g in range(gores):
        a0, a1 = 2 * math.pi * g / gores, 2 * math.pi * (g + 1) / gores
        t = bmesh.new()
        for j in range(rings):
            (r0, z0), (r1, z1) = verts[j], verts[j + 1]
            q = [t.verts.new((cx + r * r0 * math.cos(a0), cy + r * r0 * math.sin(a0), cz + r * 1.15 * z0)),
                 t.verts.new((cx + r * r0 * math.cos(a1), cy + r * r0 * math.sin(a1), cz + r * 1.15 * z0)),
                 t.verts.new((cx + r * r1 * math.cos(a1), cy + r * r1 * math.sin(a1), cz + r * 1.15 * z1)),
                 t.verts.new((cx + r * r1 * math.cos(a0), cy + r * r1 * math.sin(a0), cz + r * 1.15 * z1))]
            try:
                t.faces.new(q)
            except ValueError:
                pass
        bmesh.ops.remove_doubles(t, verts=t.verts[:], dist=1e-5)
        p.merge(t, mats[g % len(mats)], I4)


# --------------------------------------------------------------------------- pickups
def heart_coin(name, gold, rim, emb, glow=None):
    p = Part(name, 'coin', ao=False)
    R, T = 0.42, 0.1
    p.cyl(R, T, (0, 0, 0), gold, rot=(90, 0, 0), seg=40, bevel=0.03)
    p.torus(R, 0.06, (0, 0, 0), rim, rot=(90, 0, 0), seg=40, sides=10)
    if glow:
        p.torus(R + 0.1, 0.018, (0, 0, 0), glow, rot=(90, 0, 0), seg=40, sides=6)
    for sg in (-1, 1):
        heart(p, (0, sg * (T / 2 + 0.02), -0.02), 0.5, 0.05, emb)
    return p


def heart_pickup(name, pink, glow, gold):
    p = Part(name, 'powerup', ao=False)
    heart(p, (0, 0, -0.05), 0.85, 0.32, pink)
    heart(p, (-0.12, -0.17, 0.12), 0.22, 0.03, mat('heart_shine', '#ffffff', .2, emit=1.5), rot=(0, -20, 0))
    p.torus(0.62, 0.025, (0, 0, 0), glow, rot=(90, 0, 0), seg=40, sides=6)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        p.prism(star_pts(0.09, 0.035, 4), 0.02, (0.72 * math.cos(a), 0, 0.72 * math.sin(a)), gold)
    return p


def magnet(name, red, silver, glow=None):
    p = Part(name, 'powerup', ao=False)
    p.ring(0.2, 0.42, 0.28, (0, 0, 0.05), red, a0=180, a1=360, seg=20)
    for sg in (-1, 1):
        p.box((0.22, 0.28, 0.3), (sg * 0.31, 0, 0.2), red, bevel=0.04)
        p.box((0.23, 0.29, 0.18), (sg * 0.31, 0, 0.43), silver, bevel=0.04)
    if glow:
        p.torus(0.62, 0.025, (0, 0, 0.05), glow, rot=(90, 0, 0), seg=40, sides=6)
    return p


def shield(name, blue, gold, star_m):
    p = Part(name, 'powerup', ao=False)
    pts = [(0, -0.48)] + [(0.4 * math.sin(math.radians(a)), 0.1 - 0.58 * math.cos(math.radians(a)) * 0.5) for a in range(20, 90, 10)]
    pts += [(0.4, 0.3), (0.2, 0.38), (0, 0.42), (-0.2, 0.38), (-0.4, 0.3)]
    pts += [(-0.4 * math.sin(math.radians(a)), 0.1 - 0.58 * math.cos(math.radians(a)) * 0.5) for a in range(80, 10, -10)]
    p.prism(pts, 0.14, (0, 0, 0), gold, bevel=0.03)
    p.prism([(x * 0.82, z * 0.82) for x, z in pts], 0.18, (0, 0, 0.01), blue, bevel=0.04)
    p.prism(star_pts(0.17, 0.07), 0.22, (0, 0, 0.02), star_m, bevel=0.02)
    return p


def snowflake_pu(name, ice, glow):
    p = Part(name, 'powerup', ao=False)
    for a in (0, 60, 120):
        p.box((0.9, 0.1, 0.09), (0, 0, 0), ice, rot=(0, a, 0), bevel=0.03)
        for sg in (-1, 1):
            for d in (0.22, 0.34):
                ang = math.radians(a)
                c = (sg * d * math.cos(ang), 0, sg * d * math.sin(ang))
                p.box((0.16, 0.08, 0.05), c, ice, rot=(0, a + 45, 0), bevel=0.02)
                p.box((0.16, 0.08, 0.05), c, ice, rot=(0, a - 45, 0), bevel=0.02)
    p.sphere(0.12, (0, 0, 0), glow)
    p.torus(0.6, 0.02, (0, 0, 0), glow, rot=(90, 0, 0), seg=40, sides=6)
    return p


def bolt_pu(name, yellow, glow):
    p = Part(name, 'powerup', ao=False)
    p.prism([(0.08, 0.5), (-0.26, -0.04), (-0.02, -0.04), (-0.12, -0.5), (0.28, 0.08), (0.04, 0.08)], 0.16, (0, 0, 0), yellow, bevel=0.04)
    p.torus(0.6, 0.03, (0, 0, 0), glow, rot=(90, 0, 0), seg=40, sides=6)
    return p


def flame_pu(name, fire, fire2, gold):
    p = Part(name, 'powerup', ao=False)
    p.sphere(0.22, (0, 0, -0.25), gold, scale=(1, 1, 0.6))
    flame(p, (0, 0, -0.2), 0.75, fire, fire2)
    p.torus(0.6, 0.025, (0, 0, 0), fire, rot=(90, 0, 0), seg=40, sides=6)
    return p


def wing(p, base, side, m, m2=None, scale=1.0, pre=None):
    """Feathered angel wing spreading towards +X*side."""
    for k in range(7):
        t = k / 6
        ln = scale * (0.55 + 0.6 * math.sin(math.pi * (0.25 + 0.6 * t)))
        a = math.radians(70 - t * 85)
        dx, dz = math.cos(a) * side, math.sin(a)
        c = (base[0] + dx * ln * 0.55, base[1], base[2] + dz * ln * 0.55 - t * 0.05 * scale)
        p.sphere(1.0, c, m if k % 2 == 0 or not m2 else m2, scale=(ln * 0.55, 0.05 * scale, 0.13 * scale),
                 rot=(0, -math.degrees(a) * side, 0), seg=12, rings=6, pre=pre)
    p.sphere(scale * 0.22, (base[0] + 0.15 * side * scale, base[1], base[2] + 0.18 * scale), m, scale=(1.3, 0.35, 1), pre=pre)


def wings_pu(name, white, gold, pink):
    p = Part(name, 'powerup', ao=False)
    for sg in (-1, 1):
        wing(p, (sg * 0.12, 0, 0), sg, white, gold, scale=0.55)
    heart(p, (0, -0.05, -0.08), 0.32, 0.16, pink)
    return p


def shell_pu(name, pink, pearl, glow):
    p = Part(name, 'powerup', ao=False)
    for k in range(9):
        a = 15 + k * 18.75
        ang = math.radians(a)
        p.sphere(1.0, (0.22 * math.cos(ang), 0, -0.15 + 0.22 * math.sin(ang)), pink, scale=(0.08, 0.06, 0.3),
                 rot=(0, 90 - a, 0), seg=10, rings=6)
    p.box((0.22, 0.08, 0.1), (0, 0, -0.2), pink, bevel=0.03)
    p.sphere(0.11, (0, -0.1, -0.05), pearl)
    p.torus(0.55, 0.02, (0, 0, 0), glow, rot=(90, 0, 0), seg=40, sides=6)
    return p


def bubble_pu(name, glass, pink):
    p = Part(name, 'powerup', ao=False)
    p.sphere(0.48, (0, 0, 0), glass, seg=24, rings=14)
    heart(p, (0, 0, -0.05), 0.42, 0.14, pink)
    p.sphere(0.08, (-0.2, -0.38, 0.22), mat('bubble_shine', '#ffffff', .1, emit=2.0), scale=(1, 0.4, 1.3))
    return p


# --------------------------------------------------------------------------- decorations
def heart_lantern(name, metal, glow_m, glass, h=2.4, base=None, hang=False):
    p = Part(name)
    if not hang:
        p.box((0.5, 0.5, 0.18), (0, 0, 0.09), base or metal, bevel=0.05)
        p.cyl(0.07, h, (0, 0, h / 2), metal, seg=10)
        p.torus(0.1, 0.03, (0, 0, h * 0.35), metal, seg=12, sides=6)
    z = h + 0.35
    p.box((0.62, 0.62, 0.06), (0, 0, z - 0.32), metal, bevel=0.02)
    p.box((0.56, 0.56, 0.56), (0, 0, z), glass, bevel=0.05)
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box((0.05, 0.05, 0.62), (sx * 0.29, sy * 0.29, z), metal, bevel=0.01)
    heart(p, (0, -0.06, z - 0.1), 0.42, 0.14, glow_m)
    heart(p, (0, 0.06, z - 0.1), 0.42, 0.14, glow_m)
    p.cyl(0.44, 0.3, (0, 0, z + 0.43), metal, seg=4, r2=0.06, rot=(0, 0, 45))
    p.torus(0.08, 0.025, (0, 0, z + 0.66), metal, rot=(90, 0, 0), seg=12, sides=5)
    return p


def victorian_lamp(name, metal, glow_m, h=4.2, arms=2, flowers=None):
    p = Part(name)
    p.cyl(0.28, 0.5, (0, 0, 0.25), metal, seg=12, r2=0.16)
    p.cyl(0.08, h, (0, 0, h / 2), metal, seg=10)
    for z in (0.7, h * 0.55):
        p.torus(0.1, 0.03, (0, 0, z), metal, seg=12, sides=6)
    p.sphere(0.12, (0, 0, h + 0.05), metal)
    for k in range(arms):
        sg = 1 if k == 0 else -1
        p.torus(0.35, 0.035, (sg * 0.35, 0, h - 0.2), metal, rot=(90, 0, 0), seg=16, sides=6)
        lx = sg * 0.7
        p.cyl(0.18, 0.08, (lx, 0, h - 0.3), metal, seg=10)
        p.cyl(0.14, 0.42, (lx, 0, h - 0.55), glow_m, seg=10, r2=0.2)
        p.cyl(0.24, 0.16, (lx, 0, h - 0.24), metal, seg=8, r2=0.05)
    if flowers:
        petals, centers = flowers
        for k in range(6):
            a = math.radians(k * 60)
            hibiscus(p, (0.2 * math.cos(a), 0.2 * math.sin(a), 1.25), 0.22, petals[k % len(petals)], centers[0],
                     yaw=k * 60, tilt=40)
    return p


def string_lights(name, wire, bulbs, pole, span=16.5, h=7.0, hearts=False, n=22, poles=True):
    p = Part(name)
    if poles:
        for sg in (-1, 1):
            p.cyl(0.08, h, (sg * span / 2, 0, h / 2), pole, seg=8)
            p.sphere(0.12, (sg * span / 2, 0, h + 0.05), pole)
    pts = [(-span / 2 + span * i / n, 0, h - 0.2 - 1.4 * math.sin(math.pi * i / n)) for i in range(n + 1)]
    for i in range(n):
        p.rod(pts[i], pts[i + 1], 0.018, wire, seg=4)
    for i in range(1, n):
        x, y, z = pts[i]
        m = bulbs[i % len(bulbs)]
        if hearts:
            p.rod((x, 0, z), (x, 0, z - 0.25), 0.01, wire, seg=4)
            heart(p, (x, 0, z - 0.5), 0.34, 0.06, m)
        else:
            p.sphere(0.09, (x, 0, z - 0.1), m, seg=10, rings=6)
    return p


def butterfly_cluster(name, wings, body, n=5, seed=0):
    p = Part(name, ao=False)
    r = random.Random(seed)
    for k in range(n):
        c = Vector((r.uniform(-1.5, 1.5), r.uniform(-1.5, 1.5), r.uniform(-0.6, 0.8)))
        yaw = r.uniform(0, 360)
        pre = Matrix.Translation(c) @ M(rot=(0, 0, yaw))
        m = wings[k % len(wings)]
        p.cyl(0.025, 0.22, (0, 0, 0), body, rot=(90, 0, 0), seg=6, pre=pre)
        for sg in (-1, 1):
            op = r.uniform(25, 60)
            p.sphere(1.0, (sg * 0.12, 0.04, 0.02), m, scale=(0.13, 0.1, 0.012), rot=(0, sg * op, 20 * sg), seg=12, rings=6, pre=pre)
            p.sphere(1.0, (sg * 0.09, -0.08, 0.0), m, scale=(0.09, 0.07, 0.01), rot=(0, sg * op, -15 * sg), seg=10, rings=5, pre=pre)
    return p


def parrot(name, red, blue, yellow, beak_m, perch=None):
    p = Part(name)
    if perch:
        p.cyl(0.05, 1.2, (0, 0, 0), perch, rot=(0, 90, 0), seg=8)
    p.sphere(0.2, (0, 0, 0.35), red, scale=(1, 1, 1.5))
    p.sphere(0.16, (0, -0.05, 0.68), red)
    p.cyl(0.06, 0.16, (0, -0.2, 0.66), beak_m, rot=(80, 0, 0), seg=8, r2=0.01)
    for sg in (-1, 1):
        p.sphere(0.035, (sg * 0.1, -0.12, 0.72), mat('eye_white', '#ffffff', .3))
        p.sphere(1.0, (sg * 0.18, 0.05, 0.38), blue, scale=(0.07, 0.17, 0.3), rot=(10, 0, sg * 10))
        p.sphere(1.0, (sg * 0.19, 0.06, 0.25), yellow, scale=(0.06, 0.12, 0.15))
    p.box((0.16, 0.05, 0.55), (0, 0.18, 0.05), blue, rot=(-25, 0, 0), bevel=0.02)
    p.box((0.12, 0.04, 0.4), (0, 0.22, -0.05), red, rot=(-28, 0, 0), bevel=0.015)
    return p


def jellyfish(name, bell, inner, tent, seed=0, size=1.0):
    p = Part(name, ao=False)
    r = random.Random(seed)
    p.sphere(size, (0, 0, 0), bell, scale=(1, 1, 0.75), seg=20, rings=12)
    p.sphere(size * 0.6, (0, 0, -0.05 * size), inner, scale=(1, 1, 0.6))
    for k in range(10):
        a = math.radians(k * 36)
        bx, by = 0.75 * size * math.cos(a), 0.75 * size * math.sin(a)
        pts = [(bx + 0.12 * size * math.sin(i * 0.9 + k), by + 0.12 * size * math.cos(i * 0.8 + k), -0.1 * size - i * 0.35 * size) for i in range(8)]
        for i in range(7):
            p.rod(pts[i], pts[i + 1], 0.035 * size * (1 - i / 8) + 0.01, tent, seg=5)
    for k in range(4):
        a = math.radians(k * 90 + 45)
        p.rod((0.2 * size * math.cos(a), 0.2 * size * math.sin(a), -0.2 * size),
              (0.35 * size * math.cos(a), 0.35 * size * math.sin(a), -1.5 * size), 0.07 * size, inner, seg=6, r2=0.02)
    return p


def bubbles(name, glass, n=14, seed=0):
    p = Part(name, ao=False)
    r = random.Random(seed)
    for k in range(n):
        p.sphere(r.uniform(0.06, 0.25), (r.uniform(-0.5, 0.5), r.uniform(-0.5, 0.5), k * 0.35 + r.uniform(0, 0.2)), glass, seg=12, rings=8)
    return p


def hot_air_balloon(name, mats, basket, rope, seed=0):
    p = Part(name, 'backdrop', ao=False)
    gore_balloon(p, 3.0, (0, 0, 7.0), mats, gores=12)
    p.cyl(0.9, 0.4, (0, 0, 3.5), mats[0], seg=12, r2=1.3)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        p.rod((0.95 * math.cos(a), 0.95 * math.sin(a), 3.3), (0.55 * math.cos(a), 0.55 * math.sin(a), 1.2), 0.03, rope, seg=4)
    p.box((1.2, 1.2, 1.0), (0, 0, 0.6), basket, bevel=0.1)
    p.torus(0.62, 0.06, (0, 0, 1.1), rope, seg=16, sides=6, scale=(1, 1, 1))
    return p


def guardian_lion(name, stone, stone2, gold=None):
    p = Part(name)
    p.box((1.6, 2.6, 0.8), (0, 0, 0.4), stone2, bevel=0.08)
    p.box((1.3, 2.1, 1.0), (0, 0.25, 1.3), stone, bevel=0.35, seg=3)
    p.box((1.25, 0.9, 1.5), (0, -0.55, 1.55), stone, bevel=0.35, seg=3)
    for sx in (-0.35, 0.35):
        p.box((0.32, 0.9, 0.35), (sx, -1.0, 0.98), stone, bevel=0.14)
    p.ico(0.75, (0, -0.85, 2.55), stone2, sub=2, jitter=0.12, scale=(1.1, 0.8, 1.05))
    p.sphere(0.5, (0, -1.15, 2.5), stone, scale=(1, 0.9, 1.0))
    p.sphere(0.2, (0, -1.6, 2.35), stone, scale=(1.2, 1, 0.8))
    for sx in (-0.2, 0.2):
        p.sphere(0.07, (sx, -1.55, 2.62), mat('lion_eye', '#3a2414', .5))
    p.cyl(0.12, 1.4, (0, 1.3, 1.5), stone, rot=(-60, 0, 0), seg=8, r2=0.05)
    if gold:
        p.torus(0.62, 0.06, (0, -0.8, 2.05), gold, rot=(15, 0, 0), seg=18, sides=6)
    return p


def angel_statue(name, marble, gold, h=3.2):
    p = Part(name)
    p.cyl(0.8, 0.5, (0, 0, 0.25), marble, seg=8)
    p.torus(0.8, 0.06, (0, 0, 0.5), gold, seg=24, sides=6)
    p.cyl(0.65, h * 0.55, (0, 0, 0.5 + h * 0.275), marble, seg=16, r2=0.28)
    p.sphere(0.32, (0, 0, 0.5 + h * 0.6), marble, scale=(1, 0.85, 1.1))
    p.sphere(0.24, (0, -0.02, 0.5 + h * 0.75), marble)
    p.torus(0.22, 0.03, (0, 0, 0.5 + h * 0.75 + 0.36), gold, seg=20, sides=6)
    for sg in (-1, 1):
        p.rod((sg * 0.3, -0.05, 0.5 + h * 0.6), (sg * 0.1, -0.35, 0.5 + h * 0.5), 0.08, marble, seg=8)
    pre = M(rot=(0, 0, 0))
    for sg in (-1, 1):
        wing(p, (sg * 0.25, 0.25, 0.5 + h * 0.62), sg, marble, None, scale=1.6, pre=pre)
    heart(p, (0, -0.4, 0.5 + h * 0.48), 0.3, 0.1, gold)
    return p


def spiked_block(name, stone, metal, size=(2.2, 1.2, 1.0)):
    p = Part(name, 'obstacle_low')
    w, d, h = size
    p.box(size, (0, 0, h / 2), stone, bevel=0.12, jitter=0.02)
    p.box((w * 0.9, 0.06, h * 0.25), (0, -d / 2 - 0.02, h * 0.55), metal, bevel=0.02)
    for i in range(5):
        x = -w / 2 + 0.25 + i * (w - 0.5) / 4
        p.cyl(0.13, 0.42, (x, 0, h + 0.2), metal, seg=8, r2=0.0)
        p.cyl(0.11, 0.3, (x, -d / 2 - 0.12, h * 0.55), metal, rot=(90, 0, 0), seg=8, r2=0.0)
    return p


def spiked_ball(name, metal, spike, base=None, kind='obstacle_low'):
    p = Part(name, kind)
    if base:
        p.box((2.3, 1.0, 0.25), (0, 0, 0.12), base, bevel=0.06)
    r = 0.5
    c = (0, 0, 0.25 + r)
    p.sphere(r, c, metal, seg=18, rings=12)
    for k in range(14):
        th = math.acos(1 - 2 * (k + 0.5) / 14)
        ph = math.pi * (1 + 5 ** 0.5) * k
        d = Vector((math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)))
        p.rod(Vector(c) + d * r * 0.9, Vector(c) + d * (r + 0.3), 0.08, spike, seg=8, r2=0.0)
    for sx in (-0.85, 0.85):
        p.sphere(0.32, (sx, 0, 0.55), metal, seg=14, rings=10)
        for k in range(6):
            a = math.radians(k * 60)
            p.rod((sx + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.55), (sx + 0.48 * math.cos(a), 0.48 * math.sin(a), 0.55), 0.06, spike, seg=6, r2=0.0)
    return p


def laser_gate(name, frame, laser, high=False):
    p = Part(name, 'obstacle_high' if high else 'obstacle_low')
    H = 2.8 if high else 1.25
    for x in (-1.2, 1.2):
        p.box((0.22, 0.3, H), (x, 0, H / 2), frame, bevel=0.06)
        p.sphere(0.14, (x, 0, H + 0.06), laser)
    if high:
        for z in (1.65, 2.05, 2.45):
            p.rod((-1.1, 0, z), (1.1, 0, z), 0.045, laser, seg=8)
        heart(p, (0, -0.1, 2.75), 0.5, 0.08, laser)
    else:
        p.rod((-1.1, 0, 0.15), (1.1, 0, 1.15), 0.05, laser, seg=8)
        p.rod((-1.1, 0, 1.15), (1.1, 0, 0.15), 0.05, laser, seg=8)
        p.rod((-1.1, 0, 0.65), (1.1, 0, 0.65), 0.035, laser, seg=8)
        p.box((2.6, 0.4, 0.12), (0, 0, 0.06), frame, bevel=0.03)
    return p


def heart_crate(name, wood, wood2, heart_m, stack=1):
    p = Part(name, 'obstacle_low')
    for (x, z, s, rz) in ((-0.55, 0.5, 1.0, 4), (0.6, 0.45, 0.9, -6), (0.0, 1.35, 0.8, 12))[:max(2, stack + 1)]:
        pre = M((x, 0, z), (0, 0, rz))
        p.box((s, s, s), (0, 0, 0), wood, bevel=0.05, pre=pre)
        p.box((s + 0.02, s * 0.14, s + 0.02), (0, 0, 0), wood2, pre=pre, bevel=0.02)
        for e in (-1, 1):
            p.box((s * 0.12, s + 0.03, s + 0.03), (e * (s / 2 - 0.07), 0, 0), wood2, pre=pre, bevel=0.02)
        heart(p, (0, -s / 2 - 0.03, 0), s * 0.45, 0.04, heart_m, pre=pre)
    return p


def bench(name, wood, metal):
    p = Part(name)
    for x in (-0.8, 0.8):
        p.box((0.08, 0.5, 0.45), (x, 0, 0.22), metal, bevel=0.02)
        p.box((0.08, 0.08, 0.6), (x, 0.24, 0.7), metal, bevel=0.02)
    for k in range(3):
        p.box((1.9, 0.14, 0.05), (0, -0.18 + k * 0.17, 0.47), wood, bevel=0.02)
    for k in range(2):
        p.box((1.9, 0.05, 0.13), (0, 0.27, 0.68 + k * 0.2), wood, bevel=0.02)
    return p


def rail_signal(name, metal, red, green, amber):
    p = Part(name)
    p.box((0.4, 0.4, 0.2), (0, 0, 0.1), metal, bevel=0.04)
    p.cyl(0.07, 4.0, (0, 0, 2.1), metal, seg=10)
    p.box((0.45, 0.25, 1.3), (0, 0, 4.2), metal, bevel=0.08)
    for z, m in ((4.6, red), (4.2, amber), (3.8, green)):
        p.cyl(0.13, 0.08, (0, -0.14, z), m, rot=(90, 0, 0), seg=14)
        p.box((0.32, 0.25, 0.04), (0, -0.2, z + 0.15), metal, rot=(-25, 0, 0), bevel=0.01)
    return p


def planter(name, box_m, leaf, petals, centers, w=1.4):
    p = Part(name)
    p.box((w, 0.45, 0.4), (0, 0, 0.2), box_m, bevel=0.05)
    for k in range(4):
        x = -w / 2 + (k + 0.5) * w / 4
        p.ico(0.3, (x, 0, 0.5), leaf[k % len(leaf)], sub=2, jitter=0.15, scale=(1, 0.8, 0.8))
        hibiscus(p, (x, -0.1, 0.72), 0.2, petals[k % len(petals)], centers[0], tilt=50, yaw=k * 40)
    return p


def deco_tree(name, trunk, fol, snow, bulbs, star_m, h=6.0, seed=0):
    p = pine(name, trunk, fol, snow, h=h, seed=seed, tiers=4)
    r = random.Random(seed)
    for k in range(40):
        t = k / 40
        z = h * (0.28 + 0.62 * t)
        rad = (1 - (z / h - 0.2) / 0.85) * h * 0.3 + 0.1
        a = t * math.pi * 7 + seed
        p.sphere(0.08 if k % 3 else 0.14, (rad * math.cos(a), rad * math.sin(a), z), bulbs[k % len(bulbs)], seg=10, rings=6)
    p.prism(star_pts(0.45, 0.18), 0.12, (0, 0, h + 0.5), star_m, bevel=0.03)
    p.prism(star_pts(0.45, 0.18), 0.12, (0, 0, h + 0.5), star_m, rot=(0, 0, 90), bevel=0.03)
    return p


def koi_pond(name, water, stone, stones2, koi1, koi2, pad, flower):
    p = Part(name)
    r = random.Random(3)
    p.cyl(3.0, 0.1, (0, 0, 0.05), water, seg=32)
    for k in range(22):
        a = 2 * math.pi * k / 22
        p.ico(0.45, (3.1 * math.cos(a) * 1.0, 3.1 * math.sin(a), 0.15), r.choice([stone, stones2]), sub=1, jitter=0.15,
              scale=(1.2, 1, 0.6), seed=k)
    for k in range(5):
        a = r.uniform(0, 6.28)
        c = (r.uniform(-1.8, 1.8), r.uniform(-1.8, 1.8), 0.13)
        pre = Matrix.Translation(Vector(c)) @ M(rot=(0, 0, math.degrees(a)))
        m = koi1 if k % 2 else koi2
        p.sphere(1.0, (0, 0, 0), m, scale=(0.13, 0.35, 0.07), pre=pre)
        p.prism([(0, 0), (-0.12, 0.15), (0.12, 0.15)], 0.02, (0, 0.32, 0), m, rot=(90, 0, 0), pre=pre)
    for k in range(6):
        c = (r.uniform(-2.2, 2.2), r.uniform(-2.2, 2.2), 0.11)
        p.cyl(0.32, 0.02, c, pad, seg=14)
        if k % 2 == 0:
            hibiscus(p, (c[0], c[1], 0.15), 0.18, flower, flower, tilt=0)
    return p


def tiki_hut(name, post, thatch, thatch2, floor, glow, flowers=None):
    p = Part(name, 'backdrop')
    p.box((4.2, 4.2, 0.3), (0, 0, 1.2), floor, bevel=0.05)
    for sx in (-1.8, 1.8):
        for sy in (-1.8, 1.8):
            p.cyl(0.15, 4.4, (sx, sy, 2.2), post, seg=8)
    p.cyl(3.5, 2.0, (0, 0, 4.6), thatch, seg=10, r2=0.2, jitter=0.06)
    p.cyl(3.6, 0.35, (0, 0, 3.6), thatch2, seg=10, r2=3.3, jitter=0.08)
    for k in range(20):
        a = 2 * math.pi * k / 20
        p.box((0.25, 0.04, 0.6), (3.5 * math.cos(a), 3.5 * math.sin(a), 3.3), thatch2, rot=(0, 0, math.degrees(a) + 90), bevel=0)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        p.box((1.6, 0.1, 0.1), (1.0 * math.cos(a), 1.0 * math.sin(a), 1.95), post, rot=(0, 0, math.degrees(a)))
    heart(p, (0, -1.9, 3.1), 0.45, 0.12, glow)
    if flowers:
        petals, centers = flowers
        for k, (sx, sy) in enumerate(((-1.8, -1.8), (1.8, -1.8), (-1.8, 1.8), (1.8, 1.8))):
            hibiscus(p, (sx, sy - 0.2, 3.0), 0.3, petals[k % len(petals)], centers[0], tilt=70, yaw=180)
    return p


def desert_palace(name, st, st2, dome, gold, dark, cloth):
    p = Part(name, 'landmark')
    W, D, H = 26.0, 7.0, 10.0
    arched_wall(p, W, H, D, 4.8, 3.9, st, st2, dark)
    p.box((W + 1, D + 1, 0.7), (0, 0, H + 0.35), st2, bevel=0.1)
    for i in range(13):
        p.box((0.9, D + 0.6, 0.9), (-W / 2 + 1 + i * 2.0, 0, H + 1.15), st, bevel=0.15)
    p.box((10, D - 1, 5), (0, 0.5, H + 2.5), st, bevel=0.2)
    p.sphere(4.2, (0, 0.5, H + 5), dome, scale=(1, 1, 1.15), seg=24, rings=14)
    p.cyl(0.25, 2.5, (0, 0.5, H + 10.5), gold, seg=10, r2=0.05)
    p.sphere(0.4, (0, 0.5, H + 9.6), gold)
    for k in range(5):
        x = -3.6 + k * 1.8
        p.ring(0.0001, 0.6, 0.3, (x, -D / 2 + 0.3, H + 1.5), dark, a0=0, a1=180, seg=12)
        p.box((1.2, 0.3, 1.5), (x, -D / 2 + 0.3, H + 0.75), dark, bevel=0)
    for sg in (-1, 1):
        x = sg * (W / 2 + 2)
        p.box((4.2, D + 1.5, H + 8), (x, 0, (H + 8) / 2), st, bevel=0.2)
        for z in (H - 1, H + 3.5):
            p.ring(0.0001, 0.6, 0.3, (x, -D / 2 - 0.6, z), dark, a0=0, a1=180, seg=12)
            p.box((1.2, 0.3, 1.6), (x, -D / 2 - 0.6, z - 0.8), dark, bevel=0)
        p.sphere(2.2, (x, 0, H + 8.4), dome, scale=(1, 1, 1.3), seg=20, rings=12)
        p.cyl(0.15, 1.6, (x, 0, H + 11.6), gold, seg=8, r2=0.03)
        p.box((1.5, 0.12, 4.5), (x, -D / 2 - 0.82, H + 0.5), cloth, bevel=0.02)
        p.prism([(-0.75, 0), (0.75, 0), (0, -0.6)], 0.12, (x, -D / 2 - 0.82, H - 1.75), cloth)
        p.prism(star_pts(0.4, 0.17, 8), 0.14, (x, -D / 2 - 0.9, H + 1.2), gold)
    for k in range(8):
        a = math.radians(k * 22.5)
        p.cyl(0.08, 0.1, (5.0 * math.cos(a), -D / 2 + 0.05, 4.8 + 4.5 * math.sin(a)), gold, rot=(90, 0, 0), seg=8)
    return p


def fairy_castle(name, wall, roof, glow, gold, snow=None):
    p = Part(name, 'backdrop')
    p.box((22, 10, 9), (0, 0, 4.5), wall, bevel=0.3)
    for k in range(11):
        p.box((1.2, 10.4, 1.2), (-10 + k * 2, 0, 9.4), wall, bevel=0.15)
    towers = [(-11, 0, 3.0, 18), (11, 0, 3.0, 18), (-5, -1, 2.4, 22), (5, -1, 2.4, 22), (0, 1, 3.4, 28)]
    for (x, y, r, h) in towers:
        p.cyl(r, h, (x, y, h / 2), wall, seg=16)
        p.torus(r, 0.25, (x, y, h - 0.3), gold, seg=24, sides=6)
        p.cyl(r * 1.25, r * 2.6, (x, y, h + r * 1.3), roof, seg=16, r2=0.05)
        if snow:
            p.cyl(r * 1.27, r * 0.6, (x, y, h + 0.3), snow, seg=16, r2=r * 1.0)
        p.cyl(0.08, 1.5, (x, y, h + r * 2.6 + 0.6), gold, seg=6)
        p.prism([(0, 0), (0.7, -0.2), (0, -0.45)], 0.04, (x + 0.05, y, h + r * 2.6 + 1.2), mat('castle_flag', '#ff5fa2', .6))
        for z in range(4, int(h) - 2, 4):
            for a in (-60, -90, -120):
                ang = math.radians(a)
                p.ring(0.0001, 0.35, 0.2, (x + r * math.cos(ang) * 0.98, y + r * math.sin(ang) * 0.98, z + 0.6), glow,
                       rot=(0, 0, a + 90), a0=0, a1=180, seg=8)
                p.box((0.7, 0.2, 1.0), (x + r * math.cos(ang) * 0.98, y + r * math.sin(ang) * 0.98, z + 0.1), glow,
                      rot=(0, 0, a + 90), bevel=0)
    p.ring(0.0001, 2.5, 0.3, (0, -5.1, 3.5), glow, a0=0, a1=180, seg=16)
    p.box((5, 0.3, 3.5), (0, -5.1, 1.75), glow, bevel=0)
    for k in range(10):
        p.box((0.7, 0.2, 1.1), (-9 + k * 2, -5.1, 6.5), glow, bevel=0)
    return p


def neon_arch(name, m1, m2, frame, sign):
    p = Part(name)
    R = 7.5
    p.ring(R, R + 0.25, 0.25, (0, 0, 0.5), m1, a0=0, a1=180, seg=36)
    p.ring(R + 0.6, R + 0.8, 0.25, (0, 0, 0.5), m2, a0=0, a1=180, seg=36)
    p.ring(R + 0.25, R + 0.6, 0.6, (0, 0, 0.5), frame, a0=0, a1=180, seg=36)
    for sg in (-1, 1):
        p.box((0.9, 0.9, 0.6), (sg * (R + 0.4), 0, 0.3), frame, bevel=0.08)
    heart_outline(p, (0, -0.3, R + 1.0), 2.4, 0.08, sign)
    heart(p, (0, -0.2, R + 1.0), 1.4, 0.12, sign)
    return p


def neon_heart_sign(name, frame, m1, m2, h=6):
    p = Part(name)
    p.box((0.25, 0.25, h), (0, 0, h / 2), frame, bevel=0.04)
    p.box((2.6, 0.3, 2.6), (0, 0, h + 1.2), frame, bevel=0.1)
    heart_outline(p, (0, -0.2, h + 0.85), 2.2, 0.07, m1)
    heart_outline(p, (0, -0.22, h + 0.98), 1.4, 0.06, m2)
    return p


def heaven_gate(name, marble, marble2, gold, crystal, glow, pink):
    p = Part(name, 'landmark')
    for x in (-5.4, 5.4):
        p.box((2.4, 2.6, 10.0), (x, 0, 5.0), marble, bevel=0.15)
        for z in (0.35, 10.2):
            p.box((3.0, 3.2, 0.7), (x, 0, z), marble2, bevel=0.1)
        for k in range(5):
            p.cyl(0.22, 8.6, (x - 0.9 + k * 0.45, -1.3, 5.2), marble2, seg=10)
        p.box((2.5, 0.1, 0.35), (x, -1.35, 9.4), gold, bevel=0.02)
        p.box((2.5, 0.1, 0.35), (x, -1.35, 1.0), gold, bevel=0.02)
    p.ring(4.2, 6.6, 2.6, (0, 0, 10.5), marble, a0=0, a1=180, seg=28)
    p.ring(4.0, 4.25, 2.7, (0, 0, 10.5), gold, a0=0, a1=180, seg=28)
    p.ring(6.6, 6.85, 2.7, (0, 0, 10.5), gold, a0=0, a1=180, seg=28)
    p.sphere(3.0, (0, 0.5, 16.3), marble, scale=(1, 1, 0.9), seg=20, rings=10)
    p.torus(3.0, 0.15, (0, 0.5, 16.3), gold, seg=32, sides=6)
    p.cyl(0.2, 2.5, (0, 0.5, 19.8), gold, seg=8, r2=0.03)
    p.cyl(1.1, 1.6, (0, -1.4, 14.6), crystal, seg=6, r2=0.0)
    p.cyl(1.1, 1.1, (0, -1.4, 13.3), crystal, seg=6, r2=0.0, rot=(180, 0, 0))
    p.box((8.6, 0.25, 10.4), (0, 0.6, 5.2), glow, bevel=0)
    p.ring(0.001, 4.25, 0.25, (0, 0.6, 10.5), glow, a0=0, a1=180, seg=24, bevel=0)
    heart(p, (0, 0.3, 7.5), 2.6, 0.2, pink)
    for sg in (-1, 1):
        wing(p, (sg * 6.6, 0.4, 13.5), sg, marble2, gold, scale=5.0)
    return p


def canyon_arch(name, mats, seed=0):
    p = Part(name, 'backdrop', ao_h=6)
    r = random.Random(seed)
    for sg in (-1, 1):
        p.cyl(3.2, 16, (sg * 9, 0, 8), mats[0], seg=8, r2=2.4, jitter=0.25, seed=seed + sg)
        for k in range(5):
            p.ico(2.0, (sg * 9 + r.uniform(-2, 2), r.uniform(-2, 2), r.uniform(1, 15)), mats[k % len(mats)],
                  scale=(1.3, 1, 0.7), sub=2, jitter=0.15, seed=seed + k)
    p.ring(8.0, 11.5, 5.0, (0, 0, 13.5), mats[1], a0=0, a1=180, seg=20)
    for k in range(8):
        a = math.radians(k * 180 / 7)
        p.ico(1.8, (10 * math.cos(a), r.uniform(-2, 2), 13.5 + 10 * math.sin(a)), mats[k % len(mats)], sub=2, jitter=0.15,
              scale=(1.4, 1.2, 0.8), seed=seed + 20 + k)
    return p


def sea_mine(name, metal, spike, chain, glow):
    p = spiked_ball(name, metal, spike, base=None)
    p.box((2.3, 1.0, 0.2), (0, 0, 0.1), chain, bevel=0.05)
    p.sphere(0.12, (0, -0.5, 0.8), glow)
    return p


def flower_arch(name, frame, leaf, petals, centers):
    p = Part(name)
    for sg in (-1, 1):
        p.box((0.25, 0.25, 4.0), (sg * 2.0, 0, 2.0), frame, bevel=0.04)
    p.ring(1.88, 2.12, 0.25, (0, 0, 4.0), frame, a0=0, a1=180, seg=20)
    r = random.Random(4)
    for k in range(26):
        a = math.radians(k * 180 / 25)
        c = (2.0 * math.cos(a), 0, 4.0 + 2.0 * math.sin(a))
        p.ico(0.32, c, leaf[k % len(leaf)], sub=1, jitter=0.15, seed=k)
        hibiscus(p, (c[0], -0.25, c[2]), 0.2, petals[k % len(petals)], centers[0], tilt=90, yaw=r.uniform(-20, 20))
    for sg in (-1, 1):
        for z in (0.6, 1.6, 2.6, 3.4):
            p.ico(0.3, (sg * 2.0, 0, z), leaf[0], sub=1, jitter=0.15)
            hibiscus(p, (sg * 2.0, -0.25, z + 0.1), 0.2, petals[int(z) % len(petals)], centers[0], tilt=90)
    return p


# --------------------------------------------------------------------------- themed collectibles (replace the round coin)
def outline(p, pts, loc, r, m, rot=(0, 0, 0)):
    mtx = M(loc, rot)
    n = len(pts)
    for i in range(n):
        a = mtx @ Vector((pts[i][0], 0, pts[i][1]))
        b = mtx @ Vector((pts[(i + 1) % n][0], 0, pts[(i + 1) % n][1]))
        p.rod(a, b, r, m, seg=6)
        p.sphere(r, a, m, seg=8, rings=5)


def gem(p, pts, depth, loc, m, table=0.55, rot=(0, 0, 0)):
    """Faceted cut gem: outline girdle at y=0, smaller flat tables front/back."""
    t = bmesh.new()
    girdle = [t.verts.new((x, 0, z)) for x, z in pts]
    front = [t.verts.new((x * table, -depth / 2, z * table)) for x, z in pts]
    back = [t.verts.new((x * table, depth / 2, z * table)) for x, z in pts]
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        t.faces.new([girdle[i], girdle[j], front[j], front[i]])
        t.faces.new([girdle[j], girdle[i], back[i], back[j]])
    t.faces.new(front[::-1])
    t.faces.new(back)
    p.merge(t, m, M(loc, rot))


def ellipse_pts(w, h, n=24, cz=0.0):
    return [(w * math.sin(2 * math.pi * i / n), cz + h * math.cos(2 * math.pi * i / n)) for i in range(n)]


def collectible(kind, name, P):
    """kind: emerald | bow | sun | snowflake | bolt | starfish | amber | sakura | shell | wing"""
    p = Part(name, 'coin', ao=False)
    gold, gold2 = P['gold'], P['gold2']
    pearl = mat('coin_pearl', '#fff6f0', .15, metal=.35, emit=0.4)
    if kind == 'emerald':
        g = mat('emerald', '#14b85e', .05, metal=.35, emit=0.35)
        pts = [(0, 0.5), (0.14, 0.26), (0.28, 0), (0.14, -0.26), (0, -0.5), (-0.14, -0.26), (-0.28, 0), (-0.14, 0.26)]
        gem(p, pts, 0.34, (0, 0, 0), g, table=0.4)
        outline(p, pts, (0, 0, 0), 0.035, gold)
        p.sphere(0.07, (0, -0.02, 0.56), gold, seg=10, rings=6)
        for sg in (-1, 1):
            p.sphere(1.0, (sg * 0.16, -0.02, 0.52), P['leaf2'], scale=(0.13, 0.03, 0.06), rot=(0, sg * -30, 0))
            p.sphere(1.0, (sg * 0.12, -0.02, -0.5), P['leaf2'], scale=(0.11, 0.03, 0.05), rot=(0, sg * 30, 0))
    elif kind == 'bow':
        pk, pk2 = mat('bow_pink', '#ff5ea8', .35, emit=0.2), mat('bow_inner', '#d0306e', .4)
        wing = [(0.06, 0.06), (0.25, 0.3), (0.44, 0.3), (0.5, 0.12), (0.48, -0.1), (0.4, -0.26), (0.22, -0.26), (0.06, -0.06)]
        for sg in (-1, 1):
            w = [(sg * x, z) for x, z in wing]
            p.prism(w, 0.2, (0, 0, 0.05), pk, bevel=0.08)
            p.prism([(sg * (0.15 + (x - 0.06) * 0.55), z * 0.55) for x, z in wing], 0.24, (0, 0, 0.05), pk2, bevel=0.03)
            outline(p, w, (0, -0.1, 0.05), 0.02, gold)
            p.prism([(sg * 0.05, 0), (sg * 0.2, -0.05), (sg * 0.32, -0.5), (sg * 0.2, -0.42), (sg * 0.12, -0.5)], 0.12, (0, 0.02, -0.02), pk, bevel=0.03)
        p.sphere(0.13, (0, 0, 0.05), pk, scale=(1, 0.9, 1.1))
        p.sphere(0.08, (0, -0.12, 0.06), pearl, seg=12, rings=8)
    elif kind == 'sun':
        p.cyl(0.3, 0.14, (0, 0, 0), gold, rot=(90, 0, 0), seg=32, bevel=0.04)
        p.torus(0.31, 0.035, (0, 0, 0), gold2, rot=(90, 0, 0), seg=32, sides=8)
        for k in range(12):
            a = math.radians(k * 30)
            ln = 0.2 if k % 2 == 0 else 0.13
            p.prism([(-0.07, 0), (0.07, 0), (0, ln)], 0.1, (0.3 * math.cos(a), 0, 0.3 * math.sin(a)), gold, rot=(0, 90 - k * 30, 0), bevel=0.02)
        sp = [(0.22 * (i / 40) * math.cos(i * 0.47), 0.22 * (i / 40) * math.sin(i * 0.47)) for i in range(41)]
        for sg in (-1, 1):
            for i in range(40):
                p.rod((sp[i][0], sg * 0.075, sp[i][1]), (sp[i + 1][0], sg * 0.075, sp[i + 1][1]), 0.022, gold2, seg=5)
    elif kind == 'snowflake':
        ice, glow = mat('coin_ice', '#5ab8ff', .1, metal=.35, emit=0.45), mat('coin_ice_glow', '#e8f8ff', .2, emit=3)
        p.cyl(0.13, 0.14, (0, 0, 0), ice, rot=(90, 0, 0), seg=6, bevel=0.03)
        for k in range(6):
            a = k * 60
            pre = M(rot=(0, -a, 0))
            p.box((0.48, 0.1, 0.08), (0.26, 0, 0), ice, bevel=0.03, pre=pre)
            for d, ln in ((0.22, 0.14), (0.34, 0.1)):
                p.box((ln, 0.08, 0.05), (d + ln * 0.3, 0, ln * 0.35), ice, rot=(0, -45, 0), bevel=0.02, pre=pre)
                p.box((ln, 0.08, 0.05), (d + ln * 0.3, 0, -ln * 0.35), ice, rot=(0, 45, 0), bevel=0.02, pre=pre)
            p.sphere(0.04, (0.5, 0, 0), glow, pre=pre)
        p.sphere(0.06, (0, -0.07, 0), glow)
    elif kind == 'bolt':
        pk, cy = mat('coin_neon_pink', '#e81fb8', .2, emit=1.1), mat('coin_neon_violet', '#9a4bff', .2, emit=3)
        pts = [(0.1, 0.5), (-0.26, -0.04), (-0.02, -0.04), (-0.14, -0.5), (0.28, 0.08), (0.04, 0.08)]
        p.prism(pts, 0.16, (0, 0, 0), pk, bevel=0.05)
        outline(p, [(x * 1.18, z * 1.12) for x, z in pts], (0, 0, 0), 0.03, cy)
    elif kind == 'starfish':
        orng, dot = mat('starfish_orange', '#ff7a14', .35, emit=0.12), mat('starfish_dot', '#fff0c8', .3)
        p.prism(star_pts(0.5, 0.22), 0.2, (0, 0, 0), orng, bevel=0.09)
        for k in range(5):
            a = math.radians(90 + k * 72)
            for d in (0.18, 0.3, 0.4):
                for sg in (-1, 1):
                    p.sphere(0.028, (d * math.cos(a), sg * 0.1, d * math.sin(a)), dot, seg=8, rings=5)
        for sg in (-1, 1):
            p.sphere(0.09, (0, sg * 0.1, 0), pearl, seg=12, rings=8)
    elif kind == 'amber':
        am = mat('amber', '#d8650f', .05, metal=.35, emit=0.45)
        pts = [(0.0, 0.52), (0.2, 0.32), (0.27, -0.05), (0.15, -0.42), (-0.05, -0.5), (-0.24, -0.25), (-0.25, 0.2)]
        gem(p, pts, 0.36, (0, 0, 0), am, table=0.42)
        outline(p, pts, (0, 0, 0), 0.025, gold2)
    elif kind == 'sakura':
        pk, pk2 = mat('sakura_pink', '#ff86b8', .35, emit=0.25), mat('sakura_core', '#ff3f8a', .35, emit=0.5)
        petal = [(0.16 * math.sin(2 * math.pi * i / 20), 0.21 - 0.21 * math.cos(2 * math.pi * i / 20)) for i in range(20)]
        petal[10] = (0, 0.33)
        for k in range(5):
            r = 90 - k * 72
            p.prism(petal, 0.12, (0, 0, 0), pk, rot=(0, r - 90, 0), bevel=0.05)
            outline(p, petal, (0, -0.06, 0), 0.015, gold, rot=(0, r - 90, 0))
            a = math.radians(r)
            p.sphere(0.03, (0.14 * math.cos(a), -0.08, 0.14 * math.sin(a)), gold, seg=8, rings=5)
        p.cyl(0.09, 0.16, (0, 0, 0), pk2, rot=(90, 0, 0), seg=16, bevel=0.03)
        p.sphere(0.07, (0, -0.1, 0), pearl, seg=12, rings=8)
    elif kind == 'shell':
        bl, bl2 = mat('shell_blue', '#1f78f0', .2, metal=.35, emit=0.3), mat('shell_ridge', '#7ad0ff', .2, emit=1.0)
        pts = [(-0.09, -0.4), (0.09, -0.4), (0.2, -0.33), (0.13, -0.25)]
        for i in range(17):
            a = math.radians(-10 + i * 200 / 16)
            r = 0.44 if i % 2 == 0 else 0.4
            pts.append((r * math.cos(a), -0.05 + r * math.sin(a)))
        pts += [(-0.13, -0.25), (-0.2, -0.33)]
        p.prism(pts, 0.16, (0, 0, 0), bl, bevel=0.06)
        outline(p, pts, (0, 0, 0), 0.025, gold)
        for i in range(7):
            a = math.radians(20 + i * 23.3)
            for sg in (-1, 1):
                p.rod((0, sg * 0.09, -0.22), (0.38 * math.cos(a), sg * 0.09, -0.05 + 0.38 * math.sin(a)), 0.02, bl2, seg=5)
        for sg in (-1, 1):
            p.sphere(0.09, (0, sg * 0.1, -0.24), pearl, seg=12, rings=8)
    elif kind == 'wing':
        wt, wt2 = mat('wing_white', '#fff6f0', .3, emit=0.15), mat('wing_inner', '#f4e6ee', .3)
        blue = mat('wing_gem', '#2a6bff', .05, metal=.35, emit=1.2)
        pts = [(-0.12, -0.38), (-0.2, -0.2), (-0.22, 0.02), (-0.16, 0.22), (-0.02, 0.4), (0.15, 0.5), (0.32, 0.53),
               (0.22, 0.38), (0.28, 0.32), (0.16, 0.2), (0.22, 0.13), (0.1, 0.02), (0.15, -0.06), (0.04, -0.16),
               (0.08, -0.25), (-0.02, -0.32)]
        p.prism(pts, 0.16, (0, 0, 0), wt, bevel=0.05)
        outline(p, pts, (0, 0, 0), 0.022, gold)
        inner = [(-0.1 + (x + 0.1) * 0.68, -0.3 + (z + 0.3) * 0.68) for x, z in pts]
        p.prism(inner, 0.2, (0, 0, 0), wt2, bevel=0.04)
        for sg in (-1, 1):
            for tx, tz in ((0.22, 0.38), (0.16, 0.2), (0.1, 0.02), (0.04, -0.16)):
                p.rod((-0.1, sg * 0.105, -0.28), (tx * 0.92, sg * 0.105, tz * 0.92), 0.012, gold, seg=5)
        p.sphere(0.085, (-0.12, -0.1, -0.33), blue, seg=16, rings=10)
        p.torus(0.095, 0.022, (-0.12, -0.08, -0.33), gold, rot=(90, 0, 0), seg=18, sides=6)
    return p


def deco_arch(name, frame, leaves, petals, centers, glow=None, bulbs=None, span=11.2, base_z=3.0, flowers=True, lanterns=True):
    """Decorative arch spanning the whole corridor (lanes keep >= 6.8 m clearance)."""
    p = Part(name)
    R = span / 2
    for sg in (-1, 1):
        p.box((0.35, 0.35, base_z), (sg * R, 0, base_z / 2), frame, bevel=0.06)
        p.box((0.6, 0.6, 0.25), (sg * R, 0, 0.12), frame, bevel=0.05)
    p.ring(R - 0.15, R + 0.15, 0.3, (0, 0, base_z), frame, a0=0, a1=180, seg=28)
    r = random.Random(len(name))
    n = 34
    for k in range(n):
        a = math.radians(k * 180 / (n - 1))
        c = (R * math.cos(a), r.uniform(-0.15, 0.15), base_z + R * math.sin(a))
        if leaves:
            p.ico(0.42, c, leaves[k % len(leaves)], sub=1, jitter=0.18, seed=k, scale=(1, 0.8, 0.9))
        if flowers and petals:
            hibiscus(p, (c[0], -0.32, c[2]), 0.24, petals[k % len(petals)], centers[0], tilt=90, yaw=r.uniform(-25, 25))
        if bulbs and k % 2 == 0:
            p.sphere(0.1, (c[0], -0.45, c[2] - 0.15), bulbs[(k // 2) % len(bulbs)], seg=8, rings=5)
    for sg in (-1, 1):
        for z in (0.6, 1.4, 2.2):
            if leaves:
                p.ico(0.36, (sg * R, 0, z), leaves[0], sub=1, jitter=0.18, seed=int(z * 10))
            if flowers and petals:
                hibiscus(p, (sg * R, -0.32, z + 0.1), 0.22, petals[int(z * 3) % len(petals)], centers[0], tilt=90)
    if lanterns and glow:
        for x in (-3.9, 0.0, 3.9):
            top = base_z + math.sqrt(max(0.0, R * R - x * x))
            p.rod((x, 0, top), (x, 0, top - 0.9), 0.015, frame, seg=4)
            heart(p, (x, 0, top - 1.25), 0.45, 0.12, glow)
    return p


def sparkle_field(p, mats, n=26, seed=0, z=0.44, span=(-4.0, 4.0)):
    """Little glowing sparkles in the track gaps (reference look for rails)."""
    r = random.Random(seed)
    for k in range(n):
        x = r.choice((-1, 0, 1)) * LANE + r.uniform(-0.95, 0.95)
        p.prism(star_pts(0.07, 0.025, 4), 0.02, (x, r.uniform(0.2, SEG - 0.2), z), r.choice(mats), rot=(90, 0, r.uniform(0, 90)))
