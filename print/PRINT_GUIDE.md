# Elegoo Centauri Carbon 2 — Baskı Kılavuzu

RAF Silah Organizörü, **256 × 256 × 256 mm** yatak için modüler parçalara bölünmüştür. Tüm STL’ler güvenli sınır olan **≤250 mm** içindedir (brim / etek payı).

## Dosyalar

| Dosya | Açıklama |
|-------|----------|
| `print/RAF-silah-organizoru-CC2.3mf` | Tüm parçalar (Elegoo Slicer / Orca / Bambu Studio) |
| `print/stl/*.stl` | Tek tek STL’ler |
| `print/manifest.json` | Boyutlar, hacimler, adet listesi |
| `scripts/generate_print_kit.py` | Yeniden üretmek için script |

## Malzeme önerisi

| Parça | Filament | Neden |
|-------|----------|--------|
| Panel, yuva, raf, braket | **PETG** veya **PETG-CF** | Darbe / yük dayanımı |
| Askı şeridi, tabanca askısı | PETG | Fonksiyonel |
| Keçe pad (`10_tpu_felt_pad`) | **TPU 95A** | Silah yüzeyini korur |

PLA yalnızca prototip için uygundur; uzun namlu yükü için önerilmez. Centauri Carbon 2 hardened nozzle ile CF filament basabilir.

## Adet listesi (BOM)

| Parça | Adet | Not |
|-------|------|-----|
| `01_back_panel` | **3** | Üst üste kırlangıç ile ~720 mm yükseklik |
| `02_panel_pin` | **8** | Panel hizalama |
| `03_rifle_cradle` | **4** | Üst namlu yuvası |
| `04_stock_rest` | **4** | Alt dipçik dayanağı |
| `05_magazine_rack` | **1** | 4 şarjör bölmesi |
| `06_pistol_mount` | **2** | |
| `07_peg_rail` | **1** | 5 kanca |
| `08_shelf` | **1** | Üst aksesuar rafı |
| `09_wall_bracket` | **4** | Duvar montajı |
| `10_tpu_felt_pad` | **8** | Yuva içi (opsiyonel) |

### Donanım

- **M3×12** vida ≈ 36 adet (aksesuar → panel)
- **M3×16** vida ≈ 8 adet (braket → duvar / panel)
- Duvar dübeli (tuğla/beton) veya ahşap vidası
- İsteğe bağlı: M3 brass heat-set insert (panel deliklerine)

## Elegoo Slicer ayarları (0.4 mm nozzle)

Profile: **Centauri Carbon 2** / **0.20 mm Standard**

### Yapısal parçalar (PETG)

| Ayar | Değer |
|------|-------|
| Layer height | 0.20 mm |
| First layer | 0.28 mm |
| Wall loops | **4** (yuva/dayanak için **5**) |
| Top / bottom shells | 5 / 5 |
| Infill | **40%** gyroid (panel **25%**) |
| Nozzle | 240–250 °C (filamente göre) |
| Bed | 80–90 °C |
| Fan | %30–50 |
| Outer wall speed | 80–120 mm/s |
| Max speed | ≤200 mm/s (kalite için 500’e çıkmayın) |
| Brim | Panel ve rafta **8 mm brim** |
| Supports | **Kapalı** (aşağıdaki yönelimlerle) |

### TPU pad

| Ayar | Değer |
|------|-------|
| Layer | 0.20 mm |
| Walls | 3 |
| Infill | 15% |
| Speed | 30–40 mm/s |
| Retraction | düşük / filamente göre |
| Supports | Yok |

## Baskı yönelimi (supportsiz)

1. **back_panel** — düz yüzeyi yatağa; kırlangıç kenarı serbest
2. **rifle_cradle / stock_rest** — montaj flanşı yatağa (Y delikleri yatay)
3. **magazine_rack** — taban yatağa
4. **pistol_mount** — arka plaka yatağa
5. **peg_rail** — arka yüz yatağa (kancalar yukarı)
6. **shelf** — raf yüzeyi yatağa
7. **wall_bracket** — L’nin bir kanadı yatağa
8. **panel_pin / tpu pad** — düz

> Kancalı parçalarda küçük köprüler olabilir; PETG’de genelde destek gerekmez. Kopma olursa tree support açın.

## Plaka planı (örnek)

Tek seferde sığabilecekler (yaklaşık):

- Plaka A: 1× panel  
- Plaka B: 4× cradle + 4× stock_rest  
- Plaka C: mag_rack + 2× pistol + peg_rail + shelf + 4× bracket + pinler  

3 paneli ayrı basmak en güvenlisidir (büyük yüzey, warp riski).

## Montaj sırası

1. 3 paneli kırlangıç + hizalama pimi ile birleştir → dikey sütun (~720 mm).
2. 4× `wall_bracket` ile duvara sabitle (sağlam dübel).
3. Üst sıraya 4× `rifle_cradle`, alta 4× `stock_rest` (aynı X hizası, ızgara delikleri).
4. Sol alt: `magazine_rack`.
5. Sağ: 2× `pistol_mount`.
6. Alt orta/sağ: `peg_rail`.
7. En üst: `shelf`.
8. TPU pad’leri yuva kanallarına yapıştır (kontakt / CA).

## Güvenlik

- Organizör **boş ağırlık** ve silah ağırlığını taşır; duvar ankrajını abartılı yapın.
- Namlu / dipçik temas yüzeylerinde mutlaka yumuşak pad kullanın.
- Yerel silah saklama mevzuatına uyun.

## Yeniden üretme

```bash
pip install trimesh manifold3d numpy
python3 scripts/generate_print_kit.py
```
