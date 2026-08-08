// RAF Silah Organizörü — parametrik OpenSCAD modeli
// Duvara monte: 4 tüfek yuvası, şarjör rafı, tabanca askı plakaları
// Birimler: mm

/* [Genel] */
board_w = 600;
board_h = 900;
board_t = 18;
edge = 12;

/* [Tüfek yuvaları] */
cradle_count = 4;
cradle_span = 360;
upper_y = 700;
lower_y = 220;
cradle_w = 55;
cradle_d = 45;
cradle_h = 18;

/* [Şarjör rafı] */
mag_slots = 4;
mag_w = 140;
mag_d = 55;
mag_h = 50;

module backboard() {
  difference() {
    cube([board_w, board_t, board_h], center = true);
    // Montaj delikleri
    for (x = [-board_w/2 + 40, board_w/2 - 40])
      for (z = [-board_h/2 + 40, board_h/2 - 40])
        translate([x, 0, z])
          rotate([90, 0, 0])
            cylinder(h = board_t + 2, r = 3, center = true, $fn = 24);
  }
}

module cradle(x, z) {
  translate([x, board_t/2 + cradle_d/2, z]) {
    difference() {
      cube([cradle_w, cradle_d, cradle_h], center = true);
      // V-kanal
      translate([0, 8, cradle_h/2])
        rotate([0, 45, 0])
          cube([28, cradle_d, 28], center = true);
    }
  }
}

module magazine_rack() {
  x0 = -board_w/4;
  z0 = -board_h/2 + 80;
  translate([x0, board_t/2, z0]) {
    cube([mag_w, mag_d, 4], center = false);
    translate([0, 0, 0])
      cube([mag_w, 4, mag_h], center = false);
    slot = mag_w / mag_slots;
    for (i = [0:mag_slots])
      translate([i * slot, 0, 0])
        cube([2, mag_d, mag_h], center = false);
  }
}

module pistol_plate(x, z) {
  translate([x, board_t/2, z]) {
    cube([70, 30, 12], center = true);
    translate([0, 20, -8])
      rotate([90, 0, 0])
        cylinder(h = 25, r = 4, $fn = 24);
  }
}

module peg_strip() {
  translate([board_w/6, board_t/2, -board_h/2 + 120]) {
    cube([200, 10, 16], center = false);
    for (i = [0:4])
      translate([20 + i * 40, 10, 8])
        rotate([90, 0, 0])
          cylinder(h = 20, r = 3, $fn = 16);
  }
}

module shelf() {
  translate([-board_w/2 + 20, board_t/2, board_h/2 - 40])
    cube([board_w - 40, 70, 12], center = false);
}

module organizer() {
  color("#8B5A2B") backboard();
  color("#5C3A1A") {
    for (i = [0:cradle_count - 1]) {
      x = -cradle_span/2 + i * (cradle_span / (cradle_count - 1));
      cradle(x, upper_y - board_h/2);
      cradle(x, lower_y - board_h/2);
    }
    magazine_rack();
    shelf();
  }
  color("#3A3A38") {
    pistol_plate(board_w/3, 200);
    pistol_plate(board_w/3, 50);
    peg_strip();
  }
}

organizer();
