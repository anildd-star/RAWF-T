# RAF — Silah Organizörü & Otomatik BB Loader

Duvara monte silah organizörü ve 6mm airsoft BB şarjör hız yükleyicisinin etkileşimli Three.js modelleri + parametrik OpenSCAD dosyaları.

## Ürünler

### Silah Organizörü (`index.html`)

- Meşe arka panel + çelik ray çerçevesi
- 4 tüfek / uzun namlu yuvası (keçe kaplı)
- 2 tabanca askısı
- Şarjör rafı (4 bölmeli)
- Üst aksesuar rafı ve askı şeridi

### Otomatik BB Loader (`bb-loader.html`)

- Hopper rezervuar (6mm BB)
- Krank / dişli besleme animasyonu
- Besleme tüpü + adaptör nozulu
- Pil bölmesi ve ergonomik tutamak
- “Otomatik Yükle” ile BB akış demosu
- Parametrik baskı modeli: `models/bb-loader.scad`

## Çalıştırma

Yerel bir HTTP sunucusu gerekir (ES modules):

```bash
npx --yes serve .
```

Ardından tarayıcıda:

- Organizör → `/`
- BB Loader → `/bb-loader.html`

## OpenSCAD

```bash
openscad models/bb-loader.scad
openscad models/silah-organizoru.scad
```

Hopper çapı, tüp boyu ve adaptör ölçüleri dosya başındaki parametrelerden ayarlanır.
