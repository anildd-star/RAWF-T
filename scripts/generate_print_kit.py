#!/usr/bin/env python3
"""
RAF Silah Organizörü — Elegoo Centauri Carbon 2 (bugün baskı)

Yatak: 256 × 256 × 256 mm | Nozzle: 0.4 mm
Parça + brim ≤ 246 mm (5 mm brim × 2 + pay)
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import numpy as np
import trimesh
from trimesh.creation import box, cylinder
from trimesh.transformations import rotation_matrix, translation_matrix

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "print" / "stl"
PLATES = ROOT / "print" / "plates"
BUILD = 256.0
BRIM = 5.0
SAFE = BUILD - 2 * BRIM - 2.0  # 244 mm — brim ile güvenli
M3 = 1.6
M3_C = 3.2

# Panel gövde (kırlangıç sonrası max SAFE altında kalsın)
PANEL_W = 220.0
PANEL_D = 220.0
PANEL_T = 6.0


def T(x=0.0, y=0.0, z=0.0):
    return translation_matrix([x, y, z])


def Rx(deg, point=None):
    return rotation_matrix(np.radians(deg), [1, 0, 0], point=point)


def Ry(deg, point=None):
    return rotation_matrix(np.radians(deg), [0, 1, 0], point=point)


def Rz(deg, point=None):
    return rotation_matrix(np.radians(deg), [0, 0, 1], point=point)


def clean(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))
    mesh.merge_vertices()
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.update_faces(mesh.unique_faces())
    try:
        mesh.fill_holes()
    except Exception:
        pass
    return mesh


def ground(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    mesh = clean(mesh)
    mesh.apply_translation(-mesh.bounds[0])
    return mesh


def export(mesh: trimesh.Trimesh, name: str, folder: Path = OUT) -> dict:
    mesh = ground(mesh)
    dims = mesh.extents
    assert all(d <= SAFE + 0.2 for d in dims), f"{name} too big for brim: {dims} > {SAFE}"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}.stl"
    mesh.export(path, file_type="stl")
    info = {
        "file": path.name,
        "size_mm": [round(float(x), 2) for x in dims],
        "volume_cm3": round(float(mesh.volume) / 1000.0, 2),
        "with_brim_mm": [round(float(dims[0]) + 2 * BRIM, 1), round(float(dims[1]) + 2 * BRIM, 1)],
        "fits_cc2_with_brim": bool(all(d + 2 * BRIM <= BUILD for d in dims[:2])),
    }
    print(f"  ✓ {name:32s} {info['size_mm']}  brim→{info['with_brim_mm']}  V={info['volume_cm3']}cm³")
    return info


def hole_z(r, h, x, y, z=0.0):
    c = cylinder(radius=r, height=h + 0.4, sections=40)
    c.apply_transform(T(x, y, z + h / 2))
    return c


def hole_y(r, h, x, y, z):
    c = cylinder(radius=r, height=h + 0.4, sections=40)
    c.apply_transform(T(x, y, z) @ Rx(90))
    return c


def make_back_panel() -> trimesh.Trimesh:
    w, d, t = PANEL_W, PANEL_D, PANEL_T
    panel = box(extents=[w, d, t])
    panel.apply_transform(T(w / 2, d / 2, t / 2))

    cut = []
    for x in (16, w - 16):
        for y in (16, d - 16):
            cut.append(hole_z(M3, t, x, y))
            c = cylinder(radius=M3_C, height=1.8, sections=28)
            c.apply_transform(T(x, y, t - 0.7))
            cut.append(c)

    for x in range(40, int(w), 40):
        for y in range(40, int(d), 40):
            cut.append(hole_z(M3, t, x, y))

    male = box(extents=[w - 36, 8, 3.2])
    male.apply_transform(T(w / 2, d + 3.5, t / 2))
    female = box(extents=[w - 34, 8.4, 3.6])
    female.apply_transform(T(w / 2, 3.8, t / 2))
    cut.append(female)

    for y in (55, 165):
        cut.append(hole_z(1.1, t, 8, y))
        cut.append(hole_z(1.1, t, w - 8, y))

    result = panel.difference(cut, engine="manifold")
    return result.union([male], engine="manifold")


def make_panel_pin() -> trimesh.Trimesh:
    pin = cylinder(radius=1.0, height=14, sections=28)
    pin.apply_transform(T(0, 0, 7))
    head = cylinder(radius=2.0, height=1.4, sections=28)
    head.apply_transform(T(0, 0, 0.7))
    return pin.union([head], engine="manifold")


def make_rifle_cradle() -> trimesh.Trimesh:
    body = box(extents=[56, 46, 20])
    body.apply_transform(T(28, 23 + 4, 10))
    flange = box(extents=[66, 8, 20])
    flange.apply_transform(T(33, 4, 10))
    body = body.union([flange], engine="manifold")

    cut = []
    v = box(extents=[30, 50, 30])
    v.apply_transform(Ry(45, point=[28, 30, 20]) @ T(28, 30, 20))
    cut.append(v)
    felt = box(extents=[34, 36, 1.8])
    felt.apply_transform(T(28, 28, 19.3))
    cut.append(felt)
    cut.append(hole_y(M3, 12, 10, 4, 10))
    cut.append(hole_y(M3, 12, 56, 4, 10))
    bump = cylinder(radius=4.0, height=9, sections=28)
    bump.apply_transform(T(28, 32, 5) @ Rx(90))
    cut.append(bump)
    return body.difference(cut, engine="manifold")


def make_stock_rest() -> trimesh.Trimesh:
    body = box(extents=[66, 50, 18])
    body.apply_transform(T(33, 25 + 4, 9))
    flange = box(extents=[76, 8, 18])
    flange.apply_transform(T(38, 4, 9))
    body = body.union([flange], engine="manifold")

    cut = []
    round_cut = cylinder(radius=16, height=48, sections=40)
    round_cut.apply_transform(T(33, 32, 12) @ Rx(90))
    cut.append(round_cut)
    cut.append(hole_y(M3, 12, 10, 4, 9))
    cut.append(hole_y(M3, 12, 66, 4, 9))
    return body.difference(cut, engine="manifold")


def make_magazine_rack() -> trimesh.Trimesh:
    w, d, h, wall = 140.0, 54.0, 50.0, 2.4
    base = box(extents=[w, d, 3.0])
    base.apply_transform(T(w / 2, d / 2, 1.5))
    back = box(extents=[w, wall, h])
    back.apply_transform(T(w / 2, wall / 2, h / 2))
    parts = [base, back]
    slot = w / 4
    for i in range(5):
        div = box(extents=[wall, d, h])
        div.apply_transform(T(i * slot + wall / 2, d / 2, h / 2))
        parts.append(div)
    lip = box(extents=[w, wall, 7])
    lip.apply_transform(T(w / 2, d - wall / 2, 3.5))
    parts.append(lip)
    flange = box(extents=[w, 6, 18])
    flange.apply_transform(T(w / 2, -3, 9))
    parts.append(flange)
    rack = parts[0].union(parts[1:], engine="manifold")
    cut = [hole_y(M3, 14, 18, -3, 9), hole_y(M3, 14, w / 2, -3, 9), hole_y(M3, 14, w - 18, -3, 9)]
    return rack.difference(cut, engine="manifold")


def make_pistol_mount() -> trimesh.Trimesh:
    plate = box(extents=[64, 8, 36])
    plate.apply_transform(T(32, 4, 18))
    cradle = box(extents=[46, 26, 9])
    cradle.apply_transform(T(32, 8 + 13, 31.5))
    hook_arm = cylinder(radius=3.2, height=26, sections=28)
    hook_arm.apply_transform(T(32, 20, 16) @ Rx(90))
    hook_tip = cylinder(radius=4.2, height=9, sections=28)
    hook_tip.apply_transform(T(32, 33, 12))
    body = plate.union([cradle, hook_arm, hook_tip], engine="manifold")
    felt = box(extents=[40, 20, 1.8])
    felt.apply_transform(T(32, 18, 35.3))
    cut = [
        hole_y(M3, 12, 10, 4, 10),
        hole_y(M3, 12, 54, 4, 10),
        hole_y(M3, 12, 10, 4, 26),
        hole_y(M3, 12, 54, 4, 26),
        felt,
    ]
    return body.difference(cut, engine="manifold")


def make_peg_rail() -> trimesh.Trimesh:
    w, d, h = 180.0, 12.0, 16.0
    rail = box(extents=[w, d, h])
    rail.apply_transform(T(w / 2, d / 2, h / 2))
    hooks = []
    for i in range(5):
        x = 18 + i * 36
        arm = cylinder(radius=2.3, height=20, sections=20)
        arm.apply_transform(T(x, d / 2 + 7, h / 2) @ Rx(90))
        tip = cylinder(radius=3.0, height=7, sections=20)
        tip.apply_transform(T(x, d / 2 + 16, h / 2 - 2))
        hooks.extend([arm, tip])
    rail = rail.union(hooks, engine="manifold")
    cut = [
        hole_y(M3, 14, 12, d / 2, h / 2),
        hole_y(M3, 14, w / 2, d / 2, h / 2),
        hole_y(M3, 14, w - 12, d / 2, h / 2),
    ]
    return rail.difference(cut, engine="manifold")


def make_shelf() -> trimesh.Trimesh:
    w, d, t = 220.0, 64.0, 3.6
    shelf = box(extents=[w, d, t])
    shelf.apply_transform(T(w / 2, d / 2, t / 2))
    lip = box(extents=[w, 2.8, 9])
    lip.apply_transform(T(w / 2, d - 1.4, 4.5))
    back = box(extents=[w, 5.5, 20])
    back.apply_transform(T(w / 2, 2.75, 10))
    body = shelf.union([lip, back], engine="manifold")
    cut = []
    for i in range(7):
        cut.append(hole_z(1.5, t + 0.2, 16 + i * 31.3, d / 2))
    for x in (16, w / 2, w - 16):
        cut.append(hole_y(M3, 12, x, 2.75, 12))
    return body.difference(cut, engine="manifold")


def make_wall_bracket() -> trimesh.Trimesh:
    a = box(extents=[28, 36, 3.6])
    a.apply_transform(T(14, 18, 1.8))
    b = box(extents=[28, 3.6, 28])
    b.apply_transform(T(14, 1.8, 14))
    body = a.union([b], engine="manifold")
    cs = cylinder(radius=M3_C, height=1.8, sections=28)
    cs.apply_transform(T(14, 26, 2.9))
    cut = [hole_z(M3, 5, 14, 26), cs, hole_y(M3, 6, 14, 1.8, 16)]
    return body.difference(cut, engine="manifold")


def make_felt_pad() -> trimesh.Trimesh:
    pad = box(extents=[32, 34, 1.6])
    pad.apply_transform(T(16, 17, 0.8))
    return pad


def place(mesh: trimesh.Trimesh, x: float, y: float) -> trimesh.Trimesh:
    m = mesh.copy()
    m = ground(m)
    m.apply_translation([x, y, 0])
    return m


def pack_grid(meshes: list[trimesh.Trimesh], cols: int, gap: float = 4.0, origin=(3.0, 3.0)):
    placed = []
    x0, y0 = origin
    x, y = x0, y0
    col = 0
    row_h = 0.0
    max_x = x0
    max_y = y0
    for m in meshes:
        m = ground(m)
        ext = m.extents
        if col >= cols or x + ext[0] > SAFE:
            x = x0
            y += row_h + gap
            col = 0
            row_h = 0.0
        if x + ext[0] > SAFE or y + ext[1] > SAFE:
            raise RuntimeError(f"Grid overflow placing {ext} at ({x},{y})")
        placed.append(place(m, x, y))
        x += ext[0] + gap
        row_h = max(row_h, ext[1])
        col += 1
        max_x = max(max_x, x)
        max_y = max(max_y, y + row_h)
    return placed, max_x, max_y


def make_plate_A_panel() -> trimesh.Trimesh:
    """Plaka A: 1 panel — 3 kez bas."""
    return make_back_panel()


def make_plate_B_cradles() -> trimesh.Trimesh:
    """Plaka B: 4 cradle + 4 stock — 2×4 grid."""
    cradles = [make_rifle_cradle() for _ in range(4)]
    stocks = [make_stock_rest() for _ in range(4)]
    row1, _, y1 = pack_grid(cradles, cols=2, gap=5, origin=(3, 3))
    row2, _, _ = pack_grid(stocks, cols=2, gap=5, origin=(3, y1 + 5))
    return trimesh.util.concatenate(row1 + row2)


def make_plate_C_accessories() -> trimesh.Trimesh:
    """Plaka C: shelf + mag + pistol×2 + peg + bracket×4 (PETG)."""
    parts = []
    y = 3.0
    shelf = ground(make_shelf())
    parts.append(place(shelf, 3, y))
    y += shelf.extents[1] + 4

    row, _, y2 = pack_grid(
        [make_magazine_rack(), make_pistol_mount(), make_pistol_mount()],
        cols=3,
        gap=4,
        origin=(3, y),
    )
    parts.extend(row)
    y = y2 + 4

    peg = ground(make_peg_rail())
    parts.append(place(peg, 3, y))
    y += peg.extents[1] + 4

    brackets = [make_wall_bracket() for _ in range(4)]
    row, _, _ = pack_grid(brackets, cols=4, gap=4, origin=(3, y))
    parts.extend(row)

    plate = trimesh.util.concatenate(parts)
    plate = ground(plate)
    assert all(d <= SAFE + 0.5 for d in plate.extents[:2]), plate.extents
    return plate


def make_plate_D_small() -> trimesh.Trimesh:
    """Plaka D: pin×8 (PETG) — TPU pad'leri ayrı bas."""
    pins = [make_panel_pin() for _ in range(8)]
    row, _, _ = pack_grid(pins, cols=8, gap=4, origin=(3, 3))
    return trimesh.util.concatenate(row)


def make_plate_E_tpu_pads() -> trimesh.Trimesh:
    """Plaka E: TPU pad ×8 — sadece TPU filament."""
    pads = [make_felt_pad() for _ in range(8)]
    row, _, _ = pack_grid(pads, cols=4, gap=4, origin=(3, 3))
    return trimesh.util.concatenate(row)


def make_plate_DAY1() -> trimesh.Trimesh:
    """Bugün: 2 cradle + 2 stock + 2 bracket + 4 pin (panel ayrı bas)."""
    big = [make_rifle_cradle(), make_rifle_cradle(), make_stock_rest(), make_stock_rest()]
    row1, _, y1 = pack_grid(big, cols=2, gap=5, origin=(3, 3))
    mid = [make_wall_bracket(), make_wall_bracket()] + [make_panel_pin() for _ in range(4)]
    row2, _, _ = pack_grid(mid, cols=6, gap=4, origin=(3, y1 + 5))
    return trimesh.util.concatenate(row1 + row2)


def write_3mf(stls: list[Path], out_path: Path, title: str, metadata: dict) -> None:
    objects = []
    items = []
    for i, stl in enumerate(stls, start=1):
        mesh = trimesh.load(stl)
        if isinstance(mesh, trimesh.Scene):
            mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))
        verts = mesh.vertices
        faces = mesh.faces
        # Büyük plakalarda 3MF şişmesin diye vertex sayısını koru
        v_xml = "\n".join(f'<vertex x="{v[0]:.3f}" y="{v[1]:.3f}" z="{v[2]:.3f}"/>' for v in verts)
        t_xml = "\n".join(f'<triangle v1="{f[0]}" v2="{f[1]}" v3="{f[2]}"/>' for f in faces)
        objects.append(
            f'<object id="{i}" name="{stl.stem}" type="model">'
            f"<mesh><vertices>{v_xml}</vertices><triangles>{t_xml}</triangles></mesh>"
            f"</object>"
        )
        items.append(f'<item objectid="{i}"/>')

    model = f'''<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US"
  xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
  <metadata name="Title">{title}</metadata>
  <metadata name="Application">RAF CC2 Print Kit</metadata>
  <metadata name="Description">{json.dumps(metadata, ensure_ascii=False)}</metadata>
  <resources>{"".join(objects)}</resources>
  <build>{"".join(items)}</build>
</model>'''
    content_types = '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>'''
    rels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Target="/3D/3dmodel.model" Id="rel0"
    Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>'''
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)


def filament_g(volume_cm3: float, density=1.27) -> float:
    return round(volume_cm3 * density, 1)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PLATES.mkdir(parents=True, exist_ok=True)
    print(f"CC2 kit → SAFE {SAFE} mm (yatak {BUILD}, brim {BRIM})\n")

    makers = [
        ("01_back_panel", make_back_panel),
        ("02_panel_pin", make_panel_pin),
        ("03_rifle_cradle", make_rifle_cradle),
        ("04_stock_rest", make_stock_rest),
        ("05_magazine_rack", make_magazine_rack),
        ("06_pistol_mount", make_pistol_mount),
        ("07_peg_rail", make_peg_rail),
        ("08_shelf", make_shelf),
        ("09_wall_bracket", make_wall_bracket),
        ("10_tpu_felt_pad", make_felt_pad),
    ]
    catalog = []
    stl_paths = []
    for name, fn in makers:
        info = export(fn(), name)
        catalog.append(info)
        stl_paths.append(OUT / f"{name}.stl")

    print("\nPlakalar:")
    plates = [
        ("plate_A_panel_x1", make_plate_A_panel, "3 kez bas (PETG)"),
        ("plate_B_cradles_full", make_plate_B_cradles, "1 kez (PETG)"),
        ("plate_C_accessories", make_plate_C_accessories, "1 kez (PETG)"),
        ("plate_D_pins", make_plate_D_small, "1 kez (PETG)"),
        ("plate_E_tpu_pads", make_plate_E_tpu_pads, "1 kez (TPU)"),
        ("plate_DAY1_minimum", make_plate_DAY1, "Bugün minimum set (panel ayrı)"),
    ]
    plate_info = []
    plate_paths = []
    for name, fn, note in plates:
        info = export(fn(), name, PLATES)
        info["note"] = note
        plate_info.append(info)
        plate_paths.append(PLATES / f"{name}.stl")

    bom = {
        "01_back_panel": 3,
        "02_panel_pin": 8,
        "03_rifle_cradle": 4,
        "04_stock_rest": 4,
        "05_magazine_rack": 1,
        "06_pistol_mount": 2,
        "07_peg_rail": 1,
        "08_shelf": 1,
        "09_wall_bracket": 4,
        "10_tpu_felt_pad": 8,
    }
    # Filament tahmini
    by_file = {p["file"]: p for p in catalog}
    petg_cm3 = 0.0
    tpu_cm3 = 0.0
    for part, qty in bom.items():
        v = by_file[f"{part}.stl"]["volume_cm3"] * qty
        if "tpu" in part:
            tpu_cm3 += v
        else:
            petg_cm3 += v

    day1_bom = {
        "01_back_panel": 2,
        "03_rifle_cradle": 2,
        "04_stock_rest": 2,
        "09_wall_bracket": 2,
        "02_panel_pin": 4,
        "10_tpu_felt_pad": 2,
    }
    day1_cm3 = sum(by_file[f"{k}.stl"]["volume_cm3"] * q for k, q in day1_bom.items() if "tpu" not in k)

    meta = {
        "printer": "Elegoo Centauri Carbon 2",
        "build_volume_mm": [256, 256, 256],
        "brim_mm": BRIM,
        "safe_part_mm": SAFE,
        "nozzle_mm": 0.4,
        "parts": catalog,
        "plates": plate_info,
        "bom_qty": bom,
        "day1_bom": day1_bom,
        "filament_estimate": {
            "full_kit_PETG_g": filament_g(petg_cm3),
            "full_kit_TPU_g": filament_g(tpu_cm3, 1.21),
            "day1_PETG_g": filament_g(day1_cm3),
            "note": "Gerçek tüketim infill/wall ile %15–25 artabilir",
        },
        "slicer": "ELEGOO Slicer — Centauri Carbon 2 / 0.20mm Standard",
    }

    print_dir = ROOT / "print"
    (print_dir / "manifest.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    (print_dir / "cc2-settings.json").write_text(
        json.dumps(
            {
                "printer": "Elegoo Centauri Carbon 2",
                "profile": "0.20mm Standard",
                "nozzle_mm": 0.4,
                "petg": {
                    "layer_height_mm": 0.2,
                    "walls": 4,
                    "walls_cradle": 5,
                    "infill": 40,
                    "infill_panel": 25,
                    "pattern": "gyroid",
                    "nozzle_c": 245,
                    "bed_c": 85,
                    "fan": 40,
                    "brim_mm": 5,
                    "max_speed_mms": 180,
                    "supports": False,
                },
                "tpu": {"layer_height_mm": 0.2, "walls": 3, "infill": 15, "speed_mms": 35, "supports": False},
                "start_gcode_note": "ElegooSlicer CC2 profilindeki PRINT_START / PRINT_END makrolarını kullanın",
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    write_3mf(stl_paths, print_dir / "RAF-silah-organizoru-CC2.3mf", "RAF CC2 parts", meta)
    write_3mf(plate_paths, print_dir / "RAF-CC2-PLATES.3mf", "RAF CC2 plates", meta)

    print(f"\n  PETG tam kit ≈ {meta['filament_estimate']['full_kit_PETG_g']} g")
    print(f"  PETG bugün (Day1) ≈ {meta['filament_estimate']['day1_PETG_g']} g")
    print(f"  3MF: print/RAF-silah-organizoru-CC2.3mf + print/RAF-CC2-PLATES.3mf")


if __name__ == "__main__":
    main()
