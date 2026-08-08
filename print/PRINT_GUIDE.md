# Elegoo Centauri Carbon 2 — Baskı Kılavuzu

> **Bugün basıyorsan:** önce [`BUGUN.md`](BUGUN.md) oku.

Yatak **256 × 256 × 256 mm**. Parçalar brim (5 mm) ile **≤244 mm** olacak şekilde boyutlandırıldı.

## Dosyalar

| Dosya | Kullanım |
|-------|----------|
| [`BUGUN.md`](BUGUN.md) | Bugünkü adım adım sıra |
| [`plates/`](plates/) | Hazır dizilmiş plakalar (önerilen) |
| [`RAF-CC2-PLATES.3mf`](RAF-CC2-PLATES.3mf) | Tüm plakalar tek 3MF |
| [`stl/`](stl/) | Tek parçalar |
| [`RAF-silah-organizoru-CC2.3mf`](RAF-silah-organizoru-CC2.3mf) | Tek parçalar 3MF |
| [`cc2-settings.json`](cc2-settings.json) | Slicer parametreleri |
| [`manifest.json`](manifest.json) | Boyut / filament tahmini |

## Slicer

**ELEGOO Slicer** → makine: **Centauri Carbon 2** → **0.20mm Standard**  
G-code’u Orca’dan üretme; CC2 `PRINT_START` / `PRINT_END` makroları Elegoo profilinde.

## Malzeme

| Parça | Filament |
|-------|----------|
| Panel, yuva, raf, braket, pin | **PETG** veya PETG-CF |
| `plate_E_tpu_pads` | **TPU 95A** |

## Adet (tam kit)

| Parça | Adet |
|-------|------|
| back_panel | 3 (~660 mm yükseklik) |
| rifle_cradle | 4 |
| stock_rest | 4 |
| magazine_rack | 1 |
| pistol_mount | 2 |
| peg_rail | 1 |
| shelf | 1 |
| wall_bracket | 4 |
| panel_pin | 8 |
| tpu_felt_pad | 8 |

Donanım: M3×12 ≈ 36, M3×16 ≈ 8, duvar dübeli.

## PETG ayar (0.4 mm)

Layer 0.20 · Walls 4 (yuva 5) · Infill %40 gyroid (panel %25) · 245 / 85 °C · Fan %40 · Brim 5 mm · Supports off · Max 180 mm/s

## Plaka planı

1. `plate_A_panel_x1` ×3  
2. `plate_B_cradles_full` ×1  
3. `plate_C_accessories` ×1  
4. `plate_D_pins` ×1  
5. `plate_E_tpu_pads` ×1 (TPU)

## Yeniden üret

```bash
pip install trimesh manifold3d numpy
python3 scripts/generate_print_kit.py
```
