// RAF Silah Organizörü — Centauri Carbon 2 (256³) uyumlu OpenSCAD
// Parçaları tek tek basmak için PART değişkenini değiştirin.
// Birimler: mm | Güvenli sınır: 250 mm

/* [Parça seçimi] */
// 0=panel 1=pin 2=cradle 3=stock 4=mag 5=pistol 6=peg 7=shelf 8=bracket 9=pad
PART = 0;

$fn = 48;
M3 = 3.2;

module m3_hole(h) cylinder(h = h, d = M3, center = true);

module back_panel() {
  w = 240; d = 240; t = 8;
  difference() {
    union() {
      cube([w, d, t]);
      // erkek kırlangıç
      translate([20, d, 2]) cube([w - 40, 9, 4]);
    }
    // dişi kanal
    translate([19, -0.2, 1.8]) cube([w - 38, 10.4, 4.4]);
    // montaj + ızgara
    for (x = [20:40:w-1])
      for (y = [20:40:d-1])
        translate([x, y, t/2]) m3_hole(t + 2);
    // hizalama
    for (y = [60, 180]) {
      translate([8, y, t/2]) cylinder(h = t + 2, d = 2.2, center = true);
      translate([w - 8, y, t/2]) cylinder(h = t + 2, d = 2.2, center = true);
    }
  }
}

module panel_pin() {
  cylinder(h = 16, d = 2);
  cylinder(h = 1.5, d = 4);
}

module rifle_cradle() {
  difference() {
    union() {
      translate([0, 4, 0]) cube([60, 46, 22]);
      cube([70, 8, 22]);
    }
    translate([30, 30, 22]) rotate([0, 45, 0]) cube([32, 55, 32], center = true);
    translate([12, 0, 11]) rotate([90, 0, 0]) m3_hole(20);
    translate([58, 0, 11]) rotate([90, 0, 0]) m3_hole(20);
  }
}

module stock_rest() {
  difference() {
    union() {
      translate([0, 4, 0]) cube([70, 51, 20]);
      cube([80, 8, 20]);
    }
    translate([35, 35, 14]) rotate([90, 0, 0]) cylinder(h = 50, r = 18, center = true);
    translate([12, 0, 10]) rotate([90, 0, 0]) m3_hole(20);
    translate([68, 0, 10]) rotate([90, 0, 0]) m3_hole(20);
  }
}

module magazine_rack() {
  w = 150; d = 58; h = 55; wall = 2.4;
  difference() {
    union() {
      cube([w, d, 3.2]);
      cube([w, wall, h]);
      for (i = [0:4]) translate([i * (w / 4), 0, 0]) cube([wall, d, h]);
      translate([0, d - wall, 0]) cube([w, wall, 8]);
      translate([0, -6, 0]) cube([w, 6, 20]);
    }
    for (x = [20, w/2, w - 20])
      translate([x, -3, 10]) rotate([90, 0, 0]) m3_hole(20);
  }
}

module pistol_mount() {
  difference() {
    union() {
      cube([70, 8, 40]);
      translate([10, 8, 30]) cube([50, 28, 10]);
      translate([35, 22, 18]) rotate([90, 0, 0]) cylinder(h = 28, r = 3.5, center = true);
      translate([35, 36, 10]) cylinder(h = 10, r = 4.5);
    }
    for (x = [12, 58]) for (z = [12, 28])
      translate([x, 0, z]) rotate([90, 0, 0]) m3_hole(20);
  }
}

module peg_rail() {
  w = 200; d = 14; h = 18;
  difference() {
    union() {
      cube([w, d, h]);
      for (i = [0:4]) {
        x = 20 + i * 40;
        translate([x, d + 8, h/2]) rotate([90, 0, 0]) cylinder(h = 22, r = 2.5, center = true);
        translate([x, d + 18, h/2 - 4]) cylinder(h = 8, r = 3.2);
      }
    }
    for (x = [15, w/2, w - 15])
      translate([x, d/2, h/2]) rotate([90, 0, 0]) m3_hole(30);
  }
}

module shelf() {
  w = 240; d = 70;
  difference() {
    union() {
      cube([w, d, 4]);
      translate([0, d - 3, 0]) cube([w, 3, 10]);
      translate([0, 0, 0]) cube([w, 6, 24]);
    }
    for (i = [0:6]) translate([20 + i * 33.3, d/2, 0]) cylinder(h = 5, d = 3.2);
    for (x = [20, w/2, w - 20])
      translate([x, 3, 14]) rotate([90, 0, 0]) m3_hole(20);
  }
}

module wall_bracket() {
  difference() {
    union() {
      cube([30, 40, 4]);
      cube([30, 4, 30]);
    }
    translate([15, 28, 0]) cylinder(h = 5, d = M3);
    translate([15, 2, 18]) rotate([90, 0, 0]) m3_hole(10);
  }
}

module felt_pad() cube([34, 38, 1.6]);

parts = [
  back_panel, panel_pin, rifle_cradle, stock_rest, magazine_rack,
  pistol_mount, peg_rail, shelf, wall_bracket, felt_pad
];

parts[PART]();
