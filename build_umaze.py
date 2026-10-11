# -*- coding: utf-8 -*-
# U-shaped arena (U-maze) for Danionella cerebrum social-behaviour work.
# Base design: Penalva-Tena et al. 2025, Curr. Biol. 35:363-372 (Method Details, p. e2).
#
# V2 (2026-10-12) per user request:
#   1) inner cavity  -> 100 x 100 x 40 mm  (X x Y x inner depth)  => outer 110 x 110 x 45
#   2) both U-branch channel widths -> 28 mm   (centre island becomes 44 mm)
#   3) NEW: guillotine-door slots on the line that separates the U bottom (connecting
#      band) from the upper part (arms beside the island); each slot takes a 40 mm-wide
#      glass plate with clearance (slot length 40.8 mm)
#   4) NEW: matching printed baffle part delivered by the same script
#   5) U-bottom connecting band depth 40 -> 34 mm (fish free space at the U bottom reduced)
#   6) the paper's coverslip slits kept, adapted to the 28 mm channels (slot 35.4 mm)
#
# Every slot grazes the OUTER wall by only 1.5 mm, so the 5 mm outer wall is never
# pierced (the wall keeps 3.5 mm); all deeper engagement goes into the 44 mm island.
# That is what keeps the arena watertight with a 40 mm plate in a 28 mm channel.
#
# Run:  uv run --with cadquery python build_umaze.py

import cadquery as cq
from cadquery import importers

# ============================================================ parameters (mm)
# --- arena envelope -------------------------------------------------------
inner_x = 100.0      # inner cavity X (between the two outer walls)
inner_y = 100.0      # inner cavity Y (arm-length direction)
water_d = 40.0       # inner depth Z = water column
t_wall = 5.0         # wall thickness
t_floor = 5.0        # floor thickness
f_top = 0.3          # fillet radius on exposed top edges

# --- U-channel layout -----------------------------------------------------
arm_w = 28.0                        # width of each U-branch channel (was 35)
island_w = inner_x - 2 * arm_w      # centre island width = 44
band_d = 34.0                       # depth of the U-bottom connecting band (was 40)

# --- coverslip slit at each arm end (kept from the paper design) ----------
chamber_d = 20.0     # stimulus viewing-chamber depth (paper)
cs_w = 35.0          # 35 mm coverslip width (paper)
cs_clear = 0.4       # slot is this much longer than the plate
cs_slit_w = 1.0      # slit width in Y (paper: 1 mm)

# --- NEW branch-partition door (guillotine) -------------------------------
door_plate_w = 40.0                   # user's glass plate width
door_clear = 0.8                      # total clearance along the slot length (0.4 mm/side)
door_slot_l = door_plate_w + door_clear   # 40.8 -> takes a 40 mm-wide plate
door_slot_w = 2.4                     # slot width in Y (plate-thickness direction)
wall_bite = 1.5                       # every slot grazes the OUTER wall by this much

# --- printed baffle (new part) -------------------------------------------
bf_clear = 0.4       # baffle length clearance vs the slot
bf_t = 2.0           # baffle plate thickness (fits the 2.4 mm slot)
bf_gap = 0.05        # baffle height clearance under the maze rim
tab_l, tab_t, tab_h = 14.0, 8.0, 12.0    # handle tab (wider than the slot -> acts as a stop)
tab_hole_d = 4.0                         # finger / thread hole through the tab

# ============================================================ derived geometry
L = inner_x + 2 * t_wall        # 110
W = inner_y + 2 * t_wall        # 110
H = t_floor + water_d           # 45

x0 = t_wall                     # 5     inner left wall face
x1 = x0 + arm_w                 # 33    left arm | island
x2 = x1 + island_w              # 77    island | right arm
x3 = L - t_wall                 # 105   inner right wall face
y0 = t_wall                     # 5     arm end (stimulus chamber end)
y1 = W - t_wall                 # 105   closed end of the U
y_div = y1 - band_d             # 71    island end = U-bottom / upper-part dividing line

door_slot_x_left = x0 - wall_bite                    # 3.5
door_slot_x_right = x3 + wall_bite - door_slot_l     # 65.7
cs_slot_len = cs_w + cs_clear                        # 35.4
cs_slot_x_left = x0 - wall_bite                      # 3.5
cs_slot_x_right = x3 + wall_bite - cs_slot_len       # 71.1

# ============================================================ 1) the arena
part = cq.Workplane("XY").box(L, W, H, centered=(False, False, False))

# U-shaped channel: two arms + the connecting band at the closed end
channel = (
    cq.Workplane("XY")
    .workplane(offset=t_floor)
    .polyline([
        (x0, y0), (x1, y0), (x1, y_div), (x2, y_div), (x2, y0),
        (x3, y0), (x3, y1), (x0, y1),
    ])
    .close()
    .extrude(water_d)
)
part = part.cut(channel)


def cut_box(part, lx, ly, lz, x, y, z):
    """Cut an axis-aligned box (corner anchored at x, y, z) out of `part`."""
    s = cq.Solid.makeBox(lx, ly, lz, cq.Vector(x, y, z))
    return part.cut(cq.Workplane(obj=s))


# ---- NEW: branch-partition door slots, on the dividing line, one per arm
for sx in (door_slot_x_left, door_slot_x_right):
    part = cut_box(part, door_slot_l, door_slot_w, water_d,
                   sx, y_div - door_slot_w / 2, t_floor)

# ---- coverslip slits at the arm ends (paper feature, kept)
for sx in (cs_slot_x_left, cs_slot_x_right):
    part = cut_box(part, cs_slot_len, cs_slit_w, water_d,
                   sx, y0 + chamber_d - cs_slit_w / 2, t_floor)

# ---- soften the exposed top edges only (never the slot mouths: thin slivers)
try:
    top_edges = part.edges().filter(lambda e: abs(e.Center().z - H) < 1e-3)
    part = top_edges.fillet(f_top)
except Exception as ex:
    print("top fillet skipped:", ex)

cq.exporters.export(part, "Umaze_110x110x45.step")
cq.exporters.export(part, "Umaze_110x110x45.stl")

# ============================================================ 2) printed baffle
bf_l = door_slot_l - bf_clear          # 40.4
bf_h = water_d - bf_gap                # 39.95 (rests on the interior floor, stops at the rim)
baffle = cq.Workplane("XY").box(bf_l, bf_t, bf_h, centered=(False, False, False))

tab_solid = cq.Solid.makeBox(tab_l, tab_t, tab_h,
                             cq.Vector(bf_l / 2 - tab_l / 2, bf_t / 2 - tab_t / 2, bf_h))
baffle = baffle.union(cq.Workplane(obj=tab_solid))
try:
    baffle = baffle.edges("|Z").fillet(1.0)
except Exception as ex:
    print("baffle tab fillet skipped:", ex)

tab_cx = bf_l / 2
tab_cz = bf_h + tab_h / 2
tab_cy = bf_t / 2
hole = cq.Solid.makeCylinder(tab_hole_d / 2, tab_t + 4.0,
                             cq.Vector(tab_cx, tab_cy - tab_t / 2 - 2.0, tab_cz),
                             cq.Vector(0, 1, 0))
baffle = baffle.cut(cq.Workplane(obj=hole))
try:
    baffle = baffle.faces("<Z").edges().chamfer(0.5)   # eases insertion
except Exception as ex:
    print("baffle chamfer skipped:", ex)

cq.exporters.export(baffle, "Baffle_Door_40.step")
cq.exporters.export(baffle, "Baffle_Door_40.stl")

# ============================================================ 3) reference glass plate
glass = cq.Workplane("XY").box(door_plate_w, 2.0, water_d - 0.4, centered=(False, False, False))
cq.exporters.export(glass, "Glass_Baffle_40x40x2.step")

# ============================================================ 4) verification
s = importers.importStep("Umaze_110x110x45.step").val()
bb = s.BoundingBox()
# U-channel area: two arms + connecting band, minus the band/arm overlap
ch_area = 2 * arm_w * inner_y + inner_x * band_d - 2 * arm_w * band_d
island_bite = door_slot_l - arm_w - wall_bite
door_cut = 2 * (wall_bite * door_slot_w + island_bite * (door_slot_w / 2)) * water_d
cs_cut = 2 * (wall_bite * cs_slit_w + (cs_slot_len - arm_w - wall_bite) * cs_slit_w) * water_d
exp = L * W * H - ch_area * water_d - door_cut - cs_cut
print("=" * 78)
print(f"ARENA   bbox {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} mm | solids {len(s.Solids())} "
      f"| vol {s.Volume():.0f} mm^3   (hand calc {exp:.0f}, fillets explain the small gap)")
b2 = importers.importStep("Baffle_Door_40.step").val()
bb2 = b2.BoundingBox()
print(f"BAFFLE  bbox {bb2.xlen:.2f} x {bb2.ylen:.2f} x {bb2.zlen:.2f} mm | solids {len(b2.Solids())} "
      f"| vol {b2.Volume():.0f} mm^3")
print(f"inner {inner_x}x{inner_y}x{water_d} | outer {L}x{W}x{H} | arm {arm_w} | island {island_w} | band {band_d}")
print(f"door slot {door_slot_l} x {door_slot_w} @ y={y_div} (wall bite {wall_bite}, island bite {island_bite:.1f})")
print(f"coverslip slit {cs_slot_len} x {cs_slit_w} @ y={y0 + chamber_d} | chamber {chamber_d} deep")
print(f"U-channel area {ch_area:.0f} mm^2 (= {ch_area / 100:.1f} cm^2) | water volume {ch_area * water_d / 1000:.1f} mL")
print("=" * 78)

# ---- SVG previews (convert with: magick -background white x.svg x.png)
cq.exporters.export(part, "preview_top.svg", opt={"projectionDir": (0, 0, 1), "width": 560, "height": 560})
cq.exporters.export(part, "preview_iso.svg", opt={"projectionDir": (1, -1, 0.7), "width": 700, "height": 560})

assy = cq.Assembly()
assy.add(part, name="arena", color=cq.Color(0.55, 0.75, 0.95, 0.5))
d1 = cq.Workplane(obj=baffle.val()).translate((door_slot_x_left + bf_clear / 2, y_div - bf_t / 2, t_floor))
d2 = cq.Workplane(obj=baffle.val()).translate((door_slot_x_right + bf_clear / 2, y_div - bf_t / 2, t_floor))
g1 = cq.Workplane(obj=glass.val()).translate((door_slot_x_right + 0.4, y_div - 1.0, t_floor + 0.2))
assy.add(d1, name="door_left", color=cq.Color(0.9, 0.25, 0.15, 0.95))
assy.add(d2, name="door_right", color=cq.Color(0.9, 0.25, 0.15, 0.95))
assy.add(g1, name="glass_right", color=cq.Color(0.15, 0.8, 0.4, 0.6))
try:
    cq.exporters.export(assy.toCompound(), "preview_asm.svg",
                        opt={"projectionDir": (1, -1, 0.7), "width": 700, "height": 560})
    print("assembly preview written")
except Exception as ex:
    print("assembly preview skipped:", ex)
print("done.")
