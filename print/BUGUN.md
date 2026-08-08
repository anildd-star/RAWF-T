# BUGÜN BASKI — Centauri Carbon 2

Tüm parçalar **256×256** yatağa **5 mm brim** ile sığar. G-code’u **ELEGOO Slicer** ile üret (CC2 profili).

## Şimdi yap (5 dk)

1. USB’ye kopyala:
   - `print/plates/plate_A_panel_x1.stl`
   - `print/plates/plate_DAY1_minimum.stl`
   - veya hepsi: `print/RAF-CC2-PLATES.3mf`
2. **ELEGOO Slicer** → Printer: **Centauri Carbon 2** → **0.20mm Standard**
3. Filament: **PETG** (yoksa PLA ile de basarsın ama yük taşımaz — sadece deneme)
4. Ayarlar (PETG):

| Ayar | Değer |
|------|-------|
| Layer | 0.20 |
| Walls | 4 (yuvalarda 5) |
| Infill | %40 gyroid / panel %25 |
| Nozzle | 245 °C |
| Bed | 85 °C |
| Brim | **5 mm** |
| Supports | **Off** |
| Max speed | **180 mm/s** |

5. Slice → Export → yazıcıya gönder / USB kök dizinine at.

## Bugün sırası (2 silah asacak minimum)

| Sıra | Dosya | Adet baskı | Ne çıkar |
|------|-------|------------|----------|
| 1 | `plate_A_panel_x1.stl` | **2 kez** | 2 arka panel (~440 mm yükseklik) |
| 2 | `plate_DAY1_minimum.stl` | **1 kez** | 2 yuva + 2 dayanak + 2 braket + 4 pin |

Tahmini PETG: **~0.9–1.1 kg** (infill’e göre). Tek makaraysa önce 1 panel + DAY1 bas, ikinci paneli sonra.

## Tam kit (sonraki oturumlar)

| Plaka | Dosya | Not |
|-------|-------|-----|
| A | `plate_A_panel_x1.stl` | Toplam **3** panel |
| B | `plate_B_cradles_full.stl` | 4+4 yuva |
| C | `plate_C_accessories.stl` | raf, şarjör, tabanca, askı, braket |
| D | `plate_D_pins.stl` | pinler |
| E | `plate_E_tpu_pads.stl` | **TPU** ile bas |

Tekil STL: `print/stl/`  
Ayar JSON: `print/cc2-settings.json`

## Montaj (bugün bitince)

1. 2 paneli kırlangıç + pin ile birleştir  
2. 2 braket ile duvara sabitle (sağlam dübel)  
3. Üste 2 cradle, alta 2 stock_rest (aynı hiza)  
4. Silahı asmadan önce yuva içine keçe/TPU veya elektrik bandı koy  

## Dikkat

- Brim açık kalsın; panel büyük yüzey, warp riski var.  
- Glue stick / temiz PEI kullan.  
- Orca’dan G-code atma; **ElegooSlicer CC2** profili kullan (`PRINT_START` / `PRINT_END`).  
- 500 mm/s kullanma — fonksiyonel parça.
