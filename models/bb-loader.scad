// RAF Otomatik BB Loader — parametrik OpenSCAD modeli
// 6mm airsoft BB şarjör hız yükleyici (hopper + krank / motor besleme)
// Birimler: mm

/* [Gövde] */
body_w = 58;
body_d = 72;
body_h = 110;
wall = 2.4;
fillet = 4;

/* [Hopper] */
hopper_od = 78;
hopper_id = 72;
hopper_h = 55;
hopper_cap_h = 6;
bb_d = 6;

/* [Besleme] */
feed_tube_od = 12;
feed_tube_id = 7.2;
feed_tube_len = 48;
nozzle_len = 22;
adapter_od = 18;
adapter_id = 9;

/* [Krank] */
crank_arm = 28;
crank_knob_r = 6;
shaft_r = 3.5;

/* [Pil bölmesi] */
battery_w = 28;
battery_d = 18;
battery_h = 52;

$fn = 48;

module rounded_box(size, r) {
  hull() {
    for (x = [-1, 1])
      for (y = [-1, 1])
        for (z = [-1, 1])
          translate([
            x * (size[0]/2 - r),
            y * (size[1]/2 - r),
            z * (size[2]/2 - r)
          ])
            sphere(r);
  }
}

module body_shell() {
  difference() {
    rounded_box([body_w, body_d, body_h], fillet);
    // iç boşluk
    translate([0, 0, wall])
      rounded_box([body_w - wall*2, body_d - wall*2, body_h], fillet - 0.5);
    // hopper bağlantı deliği
    translate([0, 0, body_h/2 - 1])
      cylinder(h = wall + 4, r = hopper_id/2 - 1, center = true);
    // alt besleme deliği
    translate([0, body_d/2 - 8, -body_h/2 + 18])
      rotate([90, 0, 0])
        cylinder(h = 30, r = feed_tube_od/2 + 0.3, center = true);
    // krank mili deliği
    translate([body_w/2 - 2, 8, 10])
      rotate([0, 90, 0])
        cylinder(h = 20, r = shaft_r + 0.2, center = true);
    // şeffaf pencere
    translate([0, -body_d/2 + wall/2, 8])
      cube([28, wall + 2, 36], center = true);
  }
}

module hopper() {
  translate([0, 0, body_h/2 + hopper_h/2 - 2]) {
    difference() {
      cylinder(h = hopper_h, r = hopper_od/2, center = true);
      translate([0, 0, -1])
        cylinder(h = hopper_h + 2, r = hopper_id/2, center = true);
      // dişli kenar (kapak tutucu)
      for (a = [0:45:315])
        rotate([0, 0, a])
          translate([hopper_od/2 - 1.5, 0, hopper_h/2 - 4])
            cube([3, 6, 3], center = true);
    }
    // konik huni
    translate([0, 0, -hopper_h/2 + 8])
      difference() {
        cylinder(h = 16, r1 = 10, r2 = hopper_id/2 - 1, center = true);
        cylinder(h = 18, r1 = 5, r2 = hopper_id/2 - 4, center = true);
      }
  }
}

module hopper_cap() {
  translate([0, 0, body_h/2 + hopper_h - 2 + hopper_cap_h/2]) {
    difference() {
      cylinder(h = hopper_cap_h, r = hopper_od/2 + 1.5, center = true);
      translate([0, 0, -1])
        cylinder(h = hopper_cap_h, r = hopper_od/2 - 2, center = true);
    }
    // tutamak
    translate([0, 0, hopper_cap_h/2])
      cylinder(h = 4, r = 10, center = true);
  }
}

module feed_assembly() {
  translate([0, body_d/2 + feed_tube_len/2 - 10, -body_h/2 + 18]) {
    rotate([-90, 0, 0]) {
      difference() {
        union() {
          cylinder(h = feed_tube_len, r = feed_tube_od/2, center = true);
          translate([0, 0, feed_tube_len/2 + nozzle_len/2 - 2])
            cylinder(h = nozzle_len, r1 = feed_tube_od/2, r2 = adapter_od/2 - 2, center = true);
          translate([0, 0, feed_tube_len/2 + nozzle_len - 2])
            cylinder(h = 8, r = adapter_od/2, center = true);
        }
        cylinder(h = feed_tube_len + nozzle_len + 20, r = feed_tube_id/2, center = true);
        translate([0, 0, feed_tube_len/2 + nozzle_len])
          cylinder(h = 12, r = adapter_id/2, center = true);
      }
    }
  }
}

module crank() {
  translate([body_w/2 + 2, 8, 10]) {
    rotate([0, 90, 0]) {
      cylinder(h = 8, r = shaft_r, center = true);
      translate([0, 0, 6])
        cylinder(h = 3, r = 8, center = true);
    }
    // kol
    translate([10, 0, 0]) {
      rotate([0, 0, 25]) {
        hull() {
          sphere(r = 3);
          translate([0, crank_arm, 0]) sphere(r = 3);
        }
        translate([0, crank_arm, 0])
          sphere(r = crank_knob_r);
      }
    }
  }
}

module gear_wheel() {
  translate([0, 8, 10]) {
    rotate([90, 0, 0]) {
      difference() {
        cylinder(h = 6, r = 16, center = true);
        for (a = [0:30:330])
          rotate([0, 0, a])
            translate([16, 0, 0])
              cube([4, 3, 8], center = true);
        cylinder(h = 8, r = shaft_r, center = true);
      }
    }
  }
}

module battery_bay() {
  translate([0, -body_d/2 + battery_d/2 + wall, -body_h/2 + battery_h/2 + 8]) {
    difference() {
      cube([battery_w + 4, battery_d + 2, battery_h + 2], center = true);
      cube([battery_w, battery_d, battery_h], center = true);
      // kablo çıkışı
      translate([0, battery_d/2, battery_h/2 - 6])
        cube([8, 6, 6], center = true);
    }
  }
}

module grip_pad() {
  translate([0, -body_d/2 - 1, -12]) {
    hull() {
      for (z = [-28, 28])
        translate([0, 0, z])
          rotate([90, 0, 0])
            cylinder(h = 4, r = body_w/2 - 4, center = true);
    }
  }
}

module mag_adapter_ring() {
  translate([0, body_d/2 + feed_tube_len + nozzle_len - 8, -body_h/2 + 18]) {
    rotate([-90, 0, 0]) {
      difference() {
        cylinder(h = 14, r = adapter_od/2 + 3, center = true);
        cylinder(h = 16, r = adapter_id/2 + 0.5, center = true);
        // O-ring oluğu
        translate([0, 0, 2])
          rotate_extrude()
            translate([adapter_od/2 + 1, 0, 0])
              circle(r = 1.2);
      }
    }
  }
}

module bb_loader() {
  color("#2C2A28") body_shell();
  color("#3A3A38") hopper();
  color("#C4A35A", 0.55) hopper_cap();
  color("#5A5854") feed_assembly();
  color("#C4A35A") crank();
  color("#8B5A2B") gear_wheel();
  color("#1A1A1A") battery_bay();
  color("#1E2A22") grip_pad();
  color("#A63D1B") mag_adapter_ring();
}

bb_loader();
