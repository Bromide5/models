# U-maze arena for *Danionella cerebrum* — parametric CAD

A transparent-resin U-shaped arena for social-behaviour / acoustic-communication experiments in
*Danionella cerebrum* (adult). The base geometry follows **Penalva-Tena et al. 2025,
*Current Biology* 35:363–372** ("Method Details", p. e2); this repository holds the parametric
model, the derived print files and the revision notes for the v2 geometry used in the lab.

Everything is generated from one script (`build_umaze.py`) — STEP/STL for the arena, a matching
guillotine-gate baffle, a reference glass plate, plus preview renders. `verify_umaze.py`
re-imports the exported STEP and measures the geometry back (bounding box, solid count, volume,
material/void probes, and a dimensioned plan section) so the drawing is never trusted blindly.

## Geometry (mm)

| Item | Value | Derivation |
|---|---|---|
| Inner cavity (X × Y × Z) | 100 × 100 × 40 | water column 40 deep |
| Outer footprint / height | 110 × 110 × 45 | wall & floor 5 |
| U-branch channel width | 28 (each) | → centre island 44 = 100 − 2×28 |
| Centre island length | 66 | 100 − 34 |
| U-bottom connecting band depth | 34 | fish free space at the U bottom |
| Dividing line (island end) | y = 71 | 110 − 5 − 34 |
| Gate slot (one per arm) | 40.8 × 2.4, floor→top | 1.5 + 28 + 11.3 (see below) |
| Coverslip slit (one per arm) | 35.4 × 1.0, 20 mm from the arm end | keeps the 20 × 28 stimulus chamber |
| Printed gate baffle | 40.4 × 2.0 × 39.95 + tab | print 2 |
| Water volume | ≈ 284 mL | U-channel area 7096 mm² × 40 |

## Why the gate slots are offset (read this before changing dimensions)

A 40 mm-wide glass plate dropped into a 28 mm-wide channel needs its slot to bite **12.8 mm** into
the two side walls. The outer wall is only 5 mm thick — a symmetric 6.4 mm bite would cut straight
through it and the slot would become a **leak path** for the water.

Each slot is therefore offset: it grazes the **outer wall by only 1.5 mm** (leaving 3.5 mm of solid
wall, watertight) and buries the remaining **11.3 mm into the 44 mm-thick island**. The gate ends up
about 4 mm off the channel centreline (cosmetic only — the 28 mm opening is fully sealed).

If you want a centred gate instead, either add a local boss to the outer wall at the slot, or raise
the wall thickness to 8.5 mm (footprint becomes 117 × 117); both are one-parameter changes in
`build_umaze.py` (`biteOut`, `t`).

## Files

| File | Purpose |
|---|---|
| `build_umaze.py` | parametric CadQuery source — **the single source of truth** |
| `verify_umaze.py` | STEP read-back verification + dimensioned plan drawing |
| `Umaze_110x110x45.step` / `.stl` | arena body (CAD / slicer) |
| `Baffle_Door_40.step` / `.stl` | matching gate baffle — **print 2** |
| `Glass_Baffle_40x40x2.step` | reference plate for the 40 mm glass option |
| `Umaze_iLogic.vb` | Inventor iLogic rule — rebuilds arena / gate natively in Inventor |
| `preview_top.png`, `preview_iso.png` | plan / isometric renders |
| `preview_asm.png` | assembly with two gates + glass plate in place |
| `preview_spec.png` | measured plan at z = 25 mm, all dimensions annotated |
| `Umaze_V2改版说明.md` | full revision notes (Chinese) |
| `Umaze_110x110x40.*`, `Coverslip_35x50.*` | v1 model, kept unchanged |

## Regenerate

```bash
uv run --with cadquery python build_umaze.py                 # STEP/STL + previews
uv run --with cadquery --with matplotlib python verify_umaze.py   # read-back check + spec drawing
```

`magick -background white preview_top.svg preview_top.png` converts the SVG renders if needed.

## Printing

* Arena: transparent resin, 0.05 mm layers, opening facing up. After printing, run a needle /
  tweezers through the 40.8 × 2.4 gate slots and the 35.4 × 1.0 coverslip slits — resin residue
  closes them easily.
* Gate baffles: **opaque black resin** is preferable for the gates (blocks visual cues between the
  two arms and avoids reflections); use clear resin if you want the fish to see through them.
* Minimum remaining wall next to a slot is 3.5 mm; no thin unsupported fins.

## Assembly / procedure

1. Arena open side up. The dividing line sits 34 mm from the closed end (island end).
2. Drop the gates (or 40 mm glass plates) vertically into the slots — they stop on the cavity
   floor; the printed gate's tab rests on the rim and locates it.
3. Load the fish into the U-bottom band (100 × 34) with both gates in place → this is the start
   area. Pull both gates at once to open both arms: classic free-choice U-maze trial.
4. The 35 × 50 mm coverslip slits near each arm end (20 mm from the tip) and the 20 × 28 mm
   viewing chambers are kept from the paper design, for holding the stimulus fish.

## Verification (read back from the exported STEP, not script self-report)

* bbox 110.00 × 110.00 × 45.00 mm, single solid, volume 258,676 mm³ (hand calc 258,695 − top fillets)
* 13/13 material/void probes pass (outer wall keeps 3.5 mm beside a slot, slots never pierce it, …)
* 13/13 dimension checks pass (arms 28.00, island 44.00, cavity 100.00, U-bottom 34.00, slot 40.80, coverslip slit 35.40)
* STL: watertight and winding-consistent (trimesh) for both arena and gate

## Attribution

Base arena design and the behavioural paradigm come from Penalva-Tena et al., *Curr. Biol.* 35,
363–372 (2025). This repository only contains our own CAD/scripts; no paper PDFs are redistributed
here. If you reuse the design, please cite the original paper.

## 中文摘要

*Danionella cerebrum* 社会行为实验用透明树脂 U 型迷宫，底板/壁厚 5 mm，内腔 100 × 100 × 40 mm
（外廓 110 × 110 × 45），两条支路各 28 mm，中岛 44 mm，U 形底部连通区 34 mm。分界线（中岛末端，
y = 71）每侧一道 40.8 × 2.4 mm 闸门卡槽，可插 40 mm 宽玻璃片（每侧留 0.4 mm 余裕）或配套打印挡板
（打 2 片）；槽只咬进外壁 1.5 mm（外壁仍留 3.5 mm，水密不穿透），其余 11.3 mm 埋进中岛。支路末端
保留论文原设计的 35 × 50 mm 盖玻片缝与 20 × 28 mm 观察腔。全部尺寸由 `build_umaze.py` 参数化生成，
`verify_umaze.py` 会回读 STEP 复核尺寸。详见 `Umaze_V2改版说明.md`。
