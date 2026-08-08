#!/usr/bin/env python3
"""
RAF Silah Organizörü — Elegoo Centauri Carbon 2 baskı kiti üreticisi

Yazıcı: Elegoo Centauri Carbon 2
Hacim: 256 × 256 × 256 mm
Nozzle: 0.4 mm (varsayılan)

Tüm parçalar 250 mm sınırının altında; brim/etek için pay bırakılmıştır.
Birimler: mm
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import numpy as np
import trimesh
from trimesh.creation import box, cylinder
from trimesh.transformations import rotation_matrix, translation_matrix

OUT = Path(__file__).resolve().parent.parent / "print" / "stl"
BUILD = 256.0
SAFE = 250.0  # brim/skirt payı
M3 = 1.6  # M3 vida için delik yarıçapı (gevşek geçme)
M3_C = 3.2  # havşa / vida başı yarıçapı


def T(x=0.0, y=0.0, z=0.0):
    return translation_matrix([x, y, z])


def Rx(deg, point=None):
    return rotation_matrix(np.radians(deg), [1, 0, 0], point=point)


def Ry(deg, point=None):
    return rotation_matrix(np.radians(deg), [0, 1, 0], point=point)


def Rz(deg, point=None):
    return rotation_matrix(np.radians(deg), [0, 0, 1], point=point)


def ensure_watertight(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
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


def export(mesh: trimesh.Trimesh, name: str) -> dict:
    mesh = ensure_watertight(mesh)
    # Zemin: en büyük düz yüzeyi XY'ye yatır (Z min = 0)
    mesh.apply_translation(-mesh.bounds[0])
    dims = mesh.extents
    assert all(d <= SAFE + 0.05 for d in dims), f"{name} too big: {dims}"
    path = OUT / f"{name}.stl"
    mesh.export(path, file_type="stl")
    info = {
        "file": path.name,
        "size_mm": [round(float(x), 2) for x in dims],
        "volume_cm3": round(float(mesh.volume) / 1000.0, 2),
        "fits_cc2": bool(all(d <= BUILD for d in dims)),
    }
    print(f"  ✓ {name:28s} {info['size_mm']}  V={info['volume_cm3']} cm³")
    return info


def hole_z(r, h, x, y, z=0.0):
    """Z ekseni boyunca silindirik delik (boolean fark için)."""
    c = cylinder(radius=r, height=h + 0.4, sections=48)
    c.apply_transform(T(x, y, z + h / 2))
    return c


def hole_y(r, h, x, y, z):
    c = cylinder(radius=r, height=h + 0.4, sections=48)
    # Önce Z→Y döndür, sonra konuma taşı
    c.apply_transform(T(x, y, z) @ Rx(90))
    return c


# ─── Parçalar ───────────────────────────────────────────────────────────────


def make_back_panel() -> trimesh.Trimesh:
    """240×240×8 mm modüler arka panel — 3 adet bas → ~720 mm yükseklik."""
    w, d, t = 240.0, 240.0, 8.0
    panel = box(extents=[w, d, t])
    panel.apply_transform(T(w / 2, d / 2, t / 2))

    cut = []
    # Köşe duvar montaj delikleri
    for x in (20, w - 20):
        for y in (20, d - 20):
            cut.append(hole_z(M3, t, x, y))
            # Havşa
            c = cylinder(radius=M3_C, height=2.2, sections=32)
            c.apply_transform(T(x, y, t - 0.9))
            cut.append(c)

    # Aksesuar ızgarası (M3) — 40 mm aralık
    for x in range(40, int(w), 40):
        for y in range(40, int(d), 40):
            if (x in (20, w - 20) and y in (20, d - 20)):
                continue
            cut.append(hole_z(M3, t, x, y))

    # Üst kenar erkek kırlangıç (dovetail)
    male = box(extents=[w - 40, 10, 4])
    male.apply_transform(T(w / 2, d + 4, t / 2))
    # Alt kenar dişi kanal
    female = box(extents=[w - 38, 10.4, 4.4])
    female.apply_transform(T(w / 2, 4.8, t / 2))
    cut.append(female)

    # Yan hizalama pimleri (2 mm)
    for y in (60, 180):
        cut.append(hole_z(1.1, t, 8, y))
        cut.append(hole_z(1.1, t, w - 8, y))

    result = panel.difference(cut, engine="manifold")
    result = result.union([male], engine="manifold")
    return result


def make_panel_pin() -> trimesh.Trimesh:
    """Panel hizalama pimi — 2 mm mil, 16 mm uzunluk. 8 adet bas."""
    pin = cylinder(radius=1.0, height=16, sections=32)
    pin.apply_transform(T(0, 0, 8))
    head = cylinder(radius=2.0, height=1.5, sections=32)
    head.apply_transform(T(0, 0, 0.75))
    return pin.union([head], engine="manifold")


def make_rifle_cradle() -> trimesh.Trimesh:
    """
    Tüfek yuvası (üst/alt ortak).
    V-kanal + keçe boşluğu + panel montaj flanşı.
    Baskı yönü: flanş zeminde (mukavemet için katmanlar flanşa paralel değil — 
    flanşı XY'de, V kanalı yukarı).
    """
    # Gövde
    body = box(extents=[60, 50, 22])
    body.apply_transform(T(30, 25, 11))

    # Montaj flanşı (panel'e vida)
    flange = box(extents=[70, 8, 22])
    flange.apply_transform(T(35, 4, 11))
    body = body.union([flange], engine="manifold")

    cut = []
    # V-kanal
    v = box(extents=[32, 52, 32])
    v.apply_transform(Ry(45, point=[30, 25, 22]) @ T(30, 25, 22))
    cut.append(v)
    # Keçe yuvası (1.5 mm çukur)
    felt = box(extents=[36, 40, 2])
    felt.apply_transform(T(30, 28, 21.2))
    cut.append(felt)
    # Panel vida delikleri
    cut.append(hole_y(M3, 12, 12, 4, 11))
    cut.append(hole_y(M3, 12, 58, 4, 11))
    # Kauçuk tampon yuvası (alt)
    bump = cylinder(radius=4.2, height=10, sections=32)
    bump.apply_transform(T(30, 35, 6) @ Rx(90))
    cut.append(bump)

    return body.difference(cut, engine="manifold")


def make_stock_rest() -> trimesh.Trimesh:
    """Dipçik / alt dayanak — daha geniş, yumuşak kanal."""
    body = box(extents=[70, 55, 20])
    body.apply_transform(T(35, 27.5, 10))
    flange = box(extents=[80, 8, 20])
    flange.apply_transform(T(40, 4, 10))
    body = body.union([flange], engine="manifold")

    cut = []
    # U-kanal
    u = box(extents=[36, 50, 14])
    u.apply_transform(T(35, 32, 13))
    cut.append(u)
    # İç radyüs benzeri (silindir)
    round_cut = cylinder(radius=18, height=50, sections=48)
    round_cut.apply_transform(T(35, 32, 13) @ Rx(90))
    cut.append(round_cut)

    cut.append(hole_y(M3, 12, 12, 4, 10))
    cut.append(hole_y(M3, 12, 68, 4, 10))
    return body.difference(cut, engine="manifold")


def make_magazine_rack() -> trimesh.Trimesh:
    """4 bölmeli şarjör rafı — tek parça, supportsiz."""
    w, d, h = 150.0, 58.0, 55.0
    wall = 2.4
    base = box(extents=[w, d, 3.2])
    base.apply_transform(T(w / 2, d / 2, 1.6))
    back = box(extents=[w, wall, h])
    back.apply_transform(T(w / 2, wall / 2, h / 2))

    parts = [base, back]
    # Bölmeler
    slot_w = (w - wall) / 4
    for i in range(5):
        x = wall / 2 + i * slot_w
        div = box(extents=[wall, d, h])
        div.apply_transform(T(x, d / 2, h / 2))
        parts.append(div)

    # Ön dudak (şarjörlerin düşmesini engeller)
    lip = box(extents=[w, wall, 8])
    lip.apply_transform(T(w / 2, d - wall / 2, 4))
    parts.append(lip)

    rack = parts[0].union(parts[1:], engine="manifold")

    # Panel montaj flanşı
    flange = box(extents=[w, 6, 20])
    flange.apply_transform(T(w / 2, -3, 10))
    rack = rack.union([flange], engine="manifold")

    cut = [
        hole_y(M3, 14, 20, -3, 10),
        hole_y(M3, 14, w / 2, -3, 10),
        hole_y(M3, 14, w - 20, -3, 10),
    ]
    return rack.difference(cut, engine="manifold")


def make_pistol_mount() -> trimesh.Trimesh:
    """Tabanca askısı — plaka + kanca."""
    plate = box(extents=[70, 8, 40])
    plate.apply_transform(T(35, 4, 20))

    # Yatak
    cradle = box(extents=[50, 28, 10])
    cradle.apply_transform(T(35, 8 + 14, 35))

    # Kanca gövdesi
    hook_arm = cylinder(radius=3.5, height=28, sections=32)
    hook_arm.apply_transform(T(35, 22, 18) @ Rx(90))
    hook_tip = cylinder(radius=4.5, height=10, sections=32)
    hook_tip.apply_transform(T(35, 36, 14))

    body = plate.union([cradle, hook_arm, hook_tip], engine="manifold")

    felt = box(extents=[42, 22, 2])
    felt.apply_transform(T(35, 20, 39.2))
    cut = [
        hole_y(M3, 12, 12, 4, 12),
        hole_y(M3, 12, 58, 4, 12),
        hole_y(M3, 12, 12, 4, 28),
        hole_y(M3, 12, 58, 4, 28),
        felt,
    ]
    return body.difference(cut, engine="manifold")


def make_peg_rail() -> trimesh.Trimesh:
    """Askı şeridi — 5 kanca, panel'e vidalanır."""
    w, d, h = 200.0, 14.0, 18.0
    rail = box(extents=[w, d, h])
    rail.apply_transform(T(w / 2, d / 2, h / 2))

    hooks = []
    for i in range(5):
        x = 20 + i * 40
        arm = cylinder(radius=2.5, height=22, sections=24)
        arm.apply_transform(T(x, d / 2 + 8, h / 2) @ Rx(90))
        tip = cylinder(radius=3.2, height=8, sections=24)
        tip.apply_transform(T(x, d / 2 + 18, h / 2 - 2))
        hooks.extend([arm, tip])

    rail = rail.union(hooks, engine="manifold")
    cut = [hole_y(M3, 16, 15, d / 2, h / 2), hole_y(M3, 16, w - 15, d / 2, h / 2),
           hole_y(M3, 16, w / 2, d / 2, h / 2)]
    return rail.difference(cut, engine="manifold")


def make_shelf() -> trimesh.Trimesh:
    """Üst aksesuar rafı — 240×70×4 + ön kenar + montaj."""
    w, d, t = 240.0, 70.0, 4.0
    shelf = box(extents=[w, d, t])
    shelf.apply_transform(T(w / 2, d / 2, t / 2))
    lip = box(extents=[w, 3, 10])
    lip.apply_transform(T(w / 2, d - 1.5, 5))
    back = box(extents=[w, 6, 24])
    back.apply_transform(T(w / 2, 3, 12))
    body = shelf.union([lip, back], engine="manifold")

    # Pirinç kanca delikleri (üst yüzey)
    cut = []
    for i in range(7):
        x = 20 + i * 33.3
        cut.append(hole_z(1.6, t + 0.2, x, d / 2))
    # Montaj
    for x in (20, w / 2, w - 20):
        cut.append(hole_y(M3, 14, x, 3, 14))
    return body.difference(cut, engine="manifold")


def make_wall_bracket() -> trimesh.Trimesh:
    """Duvar askı braketi — panel arkasına. 4 adet."""
    # L profil
    a = box(extents=[30, 40, 4])
    a.apply_transform(T(15, 20, 2))
    b = box(extents=[30, 4, 30])
    b.apply_transform(T(15, 2, 15))
    body = a.union([b], engine="manifold")
    cut = [
        hole_z(M3, 5, 15, 28),
        hole_z(M3_C, 2, 15, 28),
        hole_y(M3, 6, 15, 2, 18),
    ]
    # countersink on wall hole
    cs = cylinder(radius=M3_C, height=2, sections=32)
    cs.apply_transform(T(15, 28, 3.2))
    cut.append(cs)
    return body.difference(cut, engine="manifold")


def make_felt_pad() -> trimesh.Trimesh:
    """Opsiyonel TPU keçe/pad — cradle içine. Esnek filament."""
    pad = box(extents=[34, 38, 1.6])
    pad.apply_transform(T(17, 19, 0.8))
    return pad


def make_build_plate_layout() -> trimesh.Trimesh:
    """
    Tek plakaya sığan örnek düzen (referans görsel / demo plate).
    Gerçek baskıda parçaları ayrı ayrı slice etmek önerilir.
    """
    # Sadece boyut doğrulama için boş — atlanabilir
    plate = box(extents=[250, 250, 0.2])
    plate.apply_transform(T(125, 125, 0.1))
    return plate


def write_3mf(stls: list[Path], out_path: Path, metadata: dict) -> None:
    """Basit 3MF: her STL'yi mesh olarak paketle (Elegoo Slicer / Orca uyumlu)."""
    # Minimal 3MF structure
    model_xml_parts = []
    objects = []
    for i, stl in enumerate(stls, start=1):
        mesh = trimesh.load(stl)
        verts = mesh.vertices
        faces = mesh.faces
        v_xml = "\n".join(f'<vertex x="{v[0]:.4f}" y="{v[1]:.4f}" z="{v[2]:.4f}"/>' for v in verts)
        t_xml = "\n".join(
            f'<triangle v1="{f[0]}" v2="{f[1]}" v3="{f[2]}"/>' for f in faces
        )
        objects.append(
            f'<object id="{i}" name="{stl.stem}" type="model">'
            f"<mesh><vertices>{v_xml}</vertices><triangles>{t_xml}</triangles></mesh>"
            f"</object>"
        )
        model_xml_parts.append(f'<item objectid="{i}"/>')

    model = f'''<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US"
  xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
  <metadata name="Title">RAF Silah Organizoru — Centauri Carbon 2</metadata>
  <metadata name="Designer">RAF</metadata>
  <metadata name="Description">{json.dumps(metadata, ensure_ascii=False)}</metadata>
  <resources>
    {"".join(objects)}
  </resources>
  <build>
    {"".join(model_xml_parts)}
  </build>
</model>
'''
    content_types = '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>
'''
    rels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Target="/3D/3dmodel.model"
    Id="rel0"
    Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
'''
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"Centauri Carbon 2 baskı kiti → {OUT}")
    print(f"Güvenli sınır: {SAFE} mm (yatak {BUILD} mm)\n")

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
        mesh = fn()
        info = export(mesh, name)
        catalog.append(info)
        stl_paths.append(OUT / f"{name}.stl")

    meta = {
        "printer": "Elegoo Centauri Carbon 2",
        "build_volume_mm": [256, 256, 256],
        "nozzle_mm": 0.4,
        "parts": catalog,
        "bom_qty": {
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
        },
    }

    print_dir = OUT.parent
    with open(print_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    # 3MF: tüm parçalar tek arşiv (slicer'da ayrı object olarak gelir)
    write_3mf(stl_paths, print_dir / "RAF-silah-organizoru-CC2.3mf", meta)
    print(f"\n  ✓ 3MF → print/RAF-silah-organizoru-CC2.3mf")
    print(f"  ✓ manifest → print/manifest.json")


if __name__ == "__main__":
    main()
