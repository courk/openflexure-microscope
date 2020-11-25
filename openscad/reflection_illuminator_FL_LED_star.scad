use <./utilities.scad>;
use <./optics.scad>;
include <./microscope_parameters.scad>;
use <./dovetail.scad>;

base_r = 20/2; // must be >= lens_r+1
LEDstar_r = 19/2;
extra_space = 2.5;
slip_plate_thickness=2;
slip_plate_edge_slot  =3;
excitation_thickness = 3.5;
top_filter_cube =LEDstar_r-fl_cube_w/2+extra_space;
beam_z = top_filter_cube+fl_cube_w/2;
roc = 0.6;
w = illuminator_width(); //nominal width of the mount (is the width between the outsides of the dovetail clip points)
dovetail_pinch = fl_cube_w - 4*roc - 1 - 3; //width between the pinch-points of the dovetail
h = fl_cube_w + top_filter_cube; //should probably be fl_cube_w
filter = [10,14,1.5];
beamsplit = [0, 0, w/2]; //NB different to fl_cube because we're printing with z=z here.

front_t = 2;
back_y = fl_cube_w/2 + roc + 1.5; //flat of dovetail (we actually start 1.5mm behind this)
led_y = back_y+3; //don't worry about precise imaging (is this OK?)
front_y = led_y + front_t;
module fl_cube_mount(beam_d=5){
    // This part clips on to the filter cube, to allow a light source (generally LED) to be coupled in using the beamsplitter.
    $fn=8;
    echo(top_filter_cube+slip_plate_thickness);
    difference(){
        union(){
            translate([0, back_y,0]) mirror([0,1,0]) dovetail_m([fl_cube_w-1, 1, h], t=2*roc);
            hull(){
                translate([-w/2,back_y,0]) cube([w,d,h]);
                reflect([1,0,0]) translate([w/2-roc, back_y + excitation_thickness + 2,0]) cylinder(r=roc, h=h, $fn=16);
            }
                //hull(){
                //    l=3.5;
                //    translate([-w/2+2.5,back_y-1.5+d,top_filter_cube-beam_d/2-3-l]) cube([w-5,d,beam_d+4+2*l]);
                //    translate([-w/2+2.5,back_y-1.5+d-l,top_filter_cube-beam_d/2-3]) cube([w-5,d,beam_d+4]);
                //}
                
        }
            
            // add a hole for the LED
        translate([0,0,beam_z]){
        cylinder_with_45deg_top(h=999, r=beam_d/2, $fn=16, extra_height=0, center=true); //LED
        }
    }
}

module lens_holder(led_d=3.5){
    // A simple one-lens condenser, re-imaging the LED onto the sample.
    led_h = 2;              //distance from bottom to the top of the LED
    aperture_h = 2;
    aperture_to_lens = 6.5; //distance from aperture stop to lens
    aperture_stop_r = 0.6;
    
    lens_z = led_h + aperture_to_lens + aperture_h;
    pedestal_h = 3;
    lens_r = 13/2;
    lens_t = 1;
    led_r = led_d/2;

    difference(){
        union(){
            //lens gripper to hold the plastic asphere
            translate([0,0,lens_z-pedestal_h]){
                // gripper
                trylinder_gripper(inner_r=lens_r, grip_h=pedestal_h + lens_t/3,h=pedestal_h+lens_t+1.5, base_r=base_r, flare=0.5);
                // pedestal to raise the tube lens up within the gripper
                cylinder(r=lens_r-0.5,h=pedestal_h);
            }
            cylinder(r=base_r, h=lens_z-pedestal_h+d);
            //mounts for screws for LED star
            translate([0,-LEDstar_r,0]){
                cylinder(r=3,h =lens_z-pedestal_h+d);
            }

        }
        }
}
        //beam
        hull(){ // todo: make this a light trap?
            translate([0,0,led_h+aperture_h-d]) cylinder(r=d,h=d);
            translate([0,0,led_h+aperture_h+1]) cylinder(r=4,h=d);
            //translate([0,0,lens_z]) cube([3,4,d], center=true);
            translate([0,0,lens_z]) cylinder(r=lens_r-2,h=d);
        }
        
        //LED
        deformable_hole_trylinder(led_r-0.1,led_r+0.6,h=2*led_h+d, center=true);
        translate([0,0,led_h]) cylinder(r1=led_r+0.6, r2=aperture_stop_r,h=aperture_h-0.5+d);
        translate([0,0,led_h+aperture_h]) cylinder(r=aperture_stop_r,h=2,center=true);
        cylinder(r=led_r+0.5, h=1.5, center=true);
        
        //screws for LED star

        translate([LEDstar_r,0,0]){
            rotate([0,0,30])trylinder_selftap(nominal_d = 3, h = lens_z-pedestal_h - 1);
        }

        //screws for slip plate
        translate([0,LEDstar_r+extra_space+0.1,(lens_z-pedestal_h)/2])
        rotate([90,0,0])
        reflect(){
            translate([w/2-slip_plate_edge_slot,0,0])rotate([0,0,-30])trylinder_selftap(nominal_d = 2.5, h = 6);
        }

        //nut trap for slip plate screws
        reflect([1,0,0]){
            hull(){
                translate([w/2-4,LEDstar_r+extra_space-3,(lens_z-pedestal_h)/2])rotate([90,0,0])rotate([0,0,0])cylinder(d = 5.8, h = 2.4, $fn=6);
                translate([w/2+4,LEDstar_r+extra_space-3,(lens_z-pedestal_h)/2])rotate([90,0,0])rotate([0,0,0])cylinder(d = 5.8, h = 2.4, $fn=6);
            }
        }
    }
    
}

module field_stop(aperture=[3,4], illuminator_d=2*base_r, h=5){
    // a cylindrical plug with a rectangular aperture in it
    difference(){
        cylinder(d=illuminator_d, h=h);
        
        hull(){
            linear_extrude(0.5, center=true) square(aperture, center=true);
            translate([0,0,h]) cylinder(d=illuminator_d - 5, h=1);
        }
    }
}

// Function we can import to get width of illuminator holder
function illuminator_width() = 17;

module slip_plate(w){
    translate([0,8,-(base_r-fl_cube_w/2)-2]){
        difference(){
            union(){
                translate([-w/2+0.5,0.5,0]){
                    minkowski() {
                        cube([w-1,40-1,1]);
                        translate([0,0,0])cylinder(r=0.5,h=1);
                    }
                }
                reflect([90,0,0]){
                translate([(fl_cube_w/2+3),0,0]){
                    hull(){
                        translate([0,0,(base_r-fl_cube_w/2)+2]){
                            rotate([-90,0,0]){
                                    cylinder(r=2, h= 2);
                            }
                        }   
                        translate([0,0,2]){
                            rotate([-90,0,0]){
                                    cylinder(r=2, h= 2);
                            }
                        } 
                        translate([-4,0,0.5]){
                            rotate([-90,0,0]){
                                    cylinder(r=0.5, h= 2);
                            }
                        }    
                    }
                }
                }
            }
            reflect([90,0,0]){
                hull(){
                    translate([w/2-2,10,0])cylinder(r=1.3,h = 5);
                    translate([w/2-2,37,0])cylinder(r=1.3,h = 5);
                }
                translate([(fl_cube_w/2+3),0,(base_r-fl_cube_w/2)+2]){
                    rotate([-90,60,0]){
                        trylinder_selftap(nominal_d = 2.5,h= 6);
                    }
                }   

            }
        }
    }
}

// Geometry of illuminator holder
module illuminator_holder(){
    illuminator_d = 2*base_r; // Illuminator diameter
    h = fl_cube_width() - 1; // Illuminator holder height
    w = illuminator_width(); // Illuminator holder width
    
    intersection(){
    difference(){
            fl_cube_mount();
        //translate([0,13,0]) rotate([-90,0,0]) cylinder(h=999,r=999,$fn=5);
        
    //grooves to fit screw segments of illuminator
    for (i = [0:1]){
                        translate([0,16,h/2])rotate([0,180*i,0]) translate([0,0,LEDstar_r]) rotate([-90,0,0])
                cylinder(r=3,h =40);   
        }
        //bodge to remove top parts when base_r = 19/2
        //translate([-7.5,15,h-2])cube([15,40,3]);
        // grip the illuminator
        translate([0,16, h/2]) rotate([-90,0,0]) cylinder(h=999,d=illuminator_d);
        //translate([-w/2+2,15,-1]) cube([w-4, 4+d,999]); // cut out flexible bits
        //translate([-w/2+5,19,-1]) cube([w-5*2, 999,999]); // cut out flexible bits
        // cable tie grooves to squeeze it
        repeat([0,12,0],4) translate([0,22,h/2]) rotate([-90,0,0]) difference(){
            cylinder(d=999,h=4.5,$fn=5);
          cylinder(d=illuminator_d + 2*3, h=999, center=true);
        }
        // beam
        translate([0,0,h/2]) rotate([-90,0,0]) cylinder(d=7, h=999, center=true);
    }
    translate([0,0,h/2]) rotate([-90,0,0]) cylinder(d=base_r*2+2, h=999, center=true);
}
}

<<<<<<< HEAD
<<<<<<< HEAD
//translate([30,30,0]) rotate(90) illuminator_holder();
=======
translate([30,30,0]) rotate(90) illuminator_holder();
>>>>>>> 025f179... Add slip plate
=======
translate([30,30,(base_r-fl_cube_w/2)+2]) rotate(90) illuminator_holder();
>>>>>>> ead0158... Add screw holes for attachment to optics unit
//translate([-30,0,0]) field_stop();
lens_holder();


//difference(){
//    lens_holder();
//    //rotate([90,0,0]) //mirror([0,0,1]) 
//    translate([0,0,10]) cylinder(r=99,h=999,$fn=5);
//}
//for(i=[0:3]) translate([i*15,-20, 0]) difference(){
//    cylinder(h=0.5 * pow(2,i), d=12); 
//    cylinder(h=999,d=6,center=true);
//}