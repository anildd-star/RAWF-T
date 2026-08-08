# RAF — Silah Organizörü

Duvara monte silah organizörü: etkileşimli Three.js önizleme + **Elegoo Centauri Carbon 2** baskı kiti.

## 3D baskı (Centauri Carbon 2)

Yazıcı hacmi **256³ mm**. Kit modülerdir; tüm parçalar **≤250 mm**.

1. Kılavuz: [`print/PRINT_GUIDE.md`](print/PRINT_GUIDE.md)
2. Slice dosyası: [`print/RAF-silah-organizoru-CC2.3mf`](print/RAF-silah-organizoru-CC2.3mf)
3. Ayar özeti: [`print/cc2-settings.json`](print/cc2-settings.json)
4. STL’ler: [`print/stl/`](print/stl/)

Önerilen filament: **PETG / PETG-CF** (yapısal), **TPU** (koruyucu pad).

```bash
python3 scripts/generate_print_kit.py
```

## Web önizleme

```bash
npx --yes serve .
```

## OpenSCAD

[`models/silah-organizoru.scad`](models/silah-organizoru.scad) — `PART` ile parça seçip export alın.
