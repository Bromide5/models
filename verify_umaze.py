# -*- coding: utf-8 -*-
# Verification + annotated plan drawing for Umaze_110x110x45.step
# Run:  uv run --with cadquery --with matplotlib python verify_umaze.py
#   * re-imports the exported STEP and measures it back (independent of build_umaze.py)
#   * material/void probes at critical points
#   * writes preview_spec.png: measured plan with the real target dimensions annotated

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import cadquery as cq
from cadquery import importers

STEP = "Umaze_110x110x45.step"
Z_CUT = 25.0            # section height for the plan view (inside the water column)

part = importers.importStep(STEP)
solid = part.val()
bb = solid.BoundingBox()
print(f"STEP {STEP}: bbox {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} | solids {len(solid.Solids())} "
      f"| vol {solid.Volume():.0f} mm^3")

# ---------------------------------------------------------------- probes
def inside(pt, r=0.25):
    b = cq.Solid.makeBox(2 * r, 2 * r, 2 * r, cq.Vector(pt[0] - r, pt[1] - r, pt[2] - r))
    return solid.intersect(b).Volume() > (2 * r) ** 3 * 0.9

PROBES = [
    # (x, y, z, expected_material, what it proves)
    (1.75, 71.0, 25, True,  "outer wall keeps 3.5 mm beside the door slot"),
    (4.0, 71.0, 25, False, "door slot bites 1.5 mm into the outer wall"),
    (38.0, 71.0, 25, False, "door slot bites deep into the island (groove)"),
    (38.0, 69.0, 25, True,  "island material just outside the door-slot groove"),
    (38.0, 73.0, 25, False, "band (void) starts right after the dividing line"),
    (50.0, 65.0, 25, True,  "island extends past y=65 -> U bottom band shrunk to 34"),
    (50.0, 90.0, 25, False, "U-bottom band is open water"),
    (32.0, 50.0, 25, False, "left arm channel void (28 mm wide)"),
    (34.0, 50.0, 25, True,  "island material starts at x=33"),
    (4.0, 25.0, 25, False, "coverslip slit void inside the outer wall"),
    (4.0, 21.0, 25, True,  "wall material away from the coverslip slit"),
    (50.0, 55.0, 2.5, True, "5 mm floor under the island"),
    (50.0, 55.0, 47.0, False, "air above the maze rim"),
]
bad = 0
for x, y, z, exp_mat, why in PROBES:
    got = inside((x, y, z))
    ok = "OK " if got == exp_mat else "FAIL"
    if got != exp_mat:
        bad += 1
    print(f"  [{ok}] ({x:5.1f},{y:5.1f},{z:4.1f}) material={str(got):5s} - {why}")

# ---------------------------------------------------------------- section
sec = part.section(Z_CUT)
polys = []
for f in sec.vals():
    for w in f.Wires():
        segs = []
        for e in w.Edges():
            p0, p1 = e.positionAt(0), e.positionAt(1)
            segs.append(((p0.x, p0.y), (p1.x, p1.y)))
        # chain the segments into one closed loop
        loop = [segs[0][0], segs[0][1]]
        segs.pop(0)
        while segs:
            end = loop[-1]
            for k, (a, b) in enumerate(segs):
                if abs(a[0] - end[0]) < 1e-6 and abs(a[1] - end[1]) < 1e-6:
                    loop.append(b); segs.pop(k); break
                if abs(b[0] - end[0]) < 1e-6 and abs(b[1] - end[1]) < 1e-6:
                    loop.append(a); segs.pop(k); break
            else:
                break
        polys.append(np.array(loop))

polys.sort(key=lambda p: -abs(np.max(p[:, 0]) - np.min(p[:, 0])))
outer, holes = polys[0], polys[1:]          # material boundary / channel void(s)
print(f"\nsection z={Z_CUT}: {len(holes)} void loop(s)")

def cross_h(poly, y):
    xs = []
    n = len(poly)
    for i in range(n):
        (xa, ya), (xb, yb) = poly[i], poly[(i + 1) % n]
        if (ya > y) != (yb > y):
            xs.append(xa + (y - ya) / (yb - ya) * (xb - xa))
    return sorted(xs)

def cross_v(poly, x):
    ys = []
    n = len(poly)
    for i in range(n):
        (xa, ya), (xb, yb) = poly[i], poly[(i + 1) % n]
        if (xa > x) != (xb > x):
            ys.append(ya + (x - xa) / (xb - xa) * (yb - ya))
    return sorted(ys)

def voids_h(y):
    out = []
    for p in holes:
        xs = cross_h(p, y)
        out += [(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)]
    return sorted(out)

def voids_v(x):
    out = []
    for p in holes:
        ys = cross_v(p, x)
        out += [(ys[i], ys[i + 1]) for i in range(0, len(ys) - 1, 2)]
    return sorted(out)

def rep(label, measured, target, tol=0.06):
    ok = "OK " if abs(measured - target) <= tol else "DIFF"
    print(f"  [{ok}] {label:38s} measured {measured:7.2f}  target {target:6.2f}")
    return abs(measured - target) <= tol

print("\nmeasured geometry (from the STEP section):")
checks = []
arm_l = voids_h(50.0)
checks.append(rep("left arm channel width", arm_l[0][1] - arm_l[0][0], 28.0))
checks.append(rep("right arm channel width", arm_l[1][1] - arm_l[1][0], 28.0))
checks.append(rep("centre island width", arm_l[1][0] - arm_l[0][1], 44.0))
checks.append(rep("inner width (wall face to wall face)", arm_l[1][1] - arm_l[0][0], 100.0))
band = voids_v(50.0)[-1]
checks.append(rep("U-bottom band depth", band[1] - band[0], 34.0))
checks.append(rep("island inner length", band[0] - 5.0, 66.0))
sd = voids_h(70.5)[0]
checks.append(rep("door slot length (left arm)", sd[1] - sd[0], 40.8))
checks.append(rep("outer-wall bite into the slot", 5.0 - sd[0], 1.5))
checks.append(rep("wall material left beside the slot", sd[0], 3.5))
cs = voids_h(25.0)[0]
checks.append(rep("coverslip slit length", cs[1] - cs[0], 35.4))
checks.append(rep("outer footprint X", bb.xlen, 110.0))
checks.append(rep("outer footprint Y", bb.ylen, 110.0))
checks.append(rep("total height", bb.zlen, 45.0))
print(f"  probes failed: {bad} | dim checks failed: {checks.count(False)}")

# ---------------------------------------------------------------- drawing
fig, ax = plt.subplots(figsize=(9.6, 9.2), dpi=170)
for p in holes:
    ax.fill(p[:, 0], p[:, 1], color="#cfe4f5", zorder=2, lw=0)
    ax.plot(np.append(p[:, 0], p[0, 0]), np.append(p[:, 1], p[0, 1]), color="#1a3f66", lw=1.6, zorder=3)
o = np.vstack([outer, outer[:1]])
ax.plot(o[:, 0], o[:, 1], color="#222222", lw=2.0, zorder=4)
ax.axhline(71.0, color="#c1121f", lw=1.0, ls="--", zorder=5)

def dim_h(y, xa, xb, text, dy=0, color="#b8860b"):
    ax.annotate("", (xa, y), (xb, y), arrowprops=dict(arrowstyle="<->", color=color, lw=1.5))
    ax.text((xa + xb) / 2, y + dy, text, ha="center", va="bottom", color=color,
            fontsize=12, fontweight="bold")

def dim_v(x, ya, yb, text, dx=0, color="#1b7f4b"):
    ax.annotate("", (x, ya), (x, yb), arrowprops=dict(arrowstyle="<->", color=color, lw=1.5))
    ax.text(x + dx, (ya + yb) / 2, text, ha="right", va="center", color=color,
            fontsize=12, fontweight="bold", rotation=90)

dim_h(112, 0, 110, "outer 110")
dim_h(106.5, 5, 105, "inner 100")
dim_h(50, 5, 33, "28", dy=1.5)
dim_h(50, 33, 77, "island 44", dy=1.5)
dim_h(50, 77, 105, "28", dy=1.5)
dim_v(-7, 0, 110, "outer 110", dx=-1.5)
dim_v(-2.5, 5, 105, "inner 100", dx=-1.0)
dim_v(112.5, 5, 71, "island 66", dx=1.2)
dim_v(112.5, 71, 105, "U bottom 34", dx=1.2)
dim_h(71, 3.5, 44.3, "door slot 40.8", dy=2.0, color="#c1121f")
dim_h(25, 3.5, 38.9, "coverslip slit 35.4", dy=1.5, color="#5a189a")
dim_v(60, 5, 25, "chamber 20", dx=1.2, color="#5a189a")
NOTES = (
    "water depth 40 (inner Z) | total height 45 | wall & floor 5 mm\n"
    "door slot 40.8 long x 2.4 wide, on the dividing line y = 71 (one per arm) = outer-wall bite 1.5 + channel 28 + island 11.3\n"
    "        -> a 40 mm-wide glass plate drops in with 0.4 mm clearance per side; the 5 mm outer wall keeps 3.5 mm (never pierced)\n"
    "coverslip slit 35.4 x 1.0, 20 mm from the arm end (chamber 20 x 28) - kept from the paper design\n"
    "dashed red line = U-bottom connecting band (34 deep) / upper part dividing line"
)
ax.text(0, -8, NOTES, fontsize=10, color="#333333", va="top", linespacing=1.45)
ax.set_title("Umaze_110x110x45  —  measured plan at z=25 mm (dimensions in mm)", fontsize=12)
ax.set_aspect("equal")
ax.set_xlim(-18, 132)
ax.set_ylim(-40, 122)
ax.axis("off")
fig.tight_layout()
fig.savefig("preview_spec.png", facecolor="white")
print("\nwrote preview_spec.png")
