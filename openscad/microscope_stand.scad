// A "bucket" base for the microscope to raise it up and houseto make a nice bridge above sd card cutout
// the electronics.

use <utilities.scad>;
include <microscope_parameters.scad>;
use <compact_nut_seat.scad>;
use <main_body_transforms.scad>;
use <main_body.scad>;
use <feet.scad>;

bottom_thickness = 1.0;
inset_depth = 3.0;
allow_space = 1.5;
wall_thickness = 2.35;
raspi_support = 4.0;

raspi_board = [85, 58, 19]; //this is wrong, should be 85, 56, 19

box_h = bottom_thickness + raspi_support + raspi_board[2] + 5;

module foot_footprint(tilt=0){
    // the footprint of one foot/actuator column
    projection(cut=true) translate([0,0,-1]) screw_seat_shell(tilt=tilt);
}

module pi_frame(){
    // coordinate system relative to the corner of the pi.
    translate([0,15]) rotate(-45) translate([-raspi_board[0]/2, -raspi_board[1]/2]) children();
}

module pi_footprint(){
    // basic space for the Pi (in 2D)
    pi_frame() translate([-1,-1]) square([raspi_board[0]+2,raspi_board[1]+2]);
}

module pi_connectors(){
    pi_frame(){
        // USB/network ports
        translate([raspi_board[0]/2,-1,1]) cube(raspi_board + [2,2,-1]);

        // micro-USB power and HDMI
        translate([24-(40/2), -100, -2]) cube([46,100,14]);

        // micro-SD card cutout
        translate([-25,raspi_board[1]/2-16,-10]) cube([30,30,16]);
    }
}

module pi_hole_frame(){
    // This transform repeats objects at each hole in the pi PCB
    pi_frame() translate([3.5,3.5]) repeat([58,0,0],2) repeat([0,49,0], 2) children();
}

module pi_support_frame(){
    // position supports for each of the pi's mounting screws
    pi_frame() translate([3.5,3.5,bottom_thickness-d]) repeat([58,0,0],2) repeat([0,49,0], 2) children();
}

module pi_supports(){
    // pillars into which the pi can be screwed (holes are hollowed out later)
    difference(){
        pi_support_frame() cylinder(h=raspi_support+d, d=7);
    }
}

module hull_from(){
    // take the convex hull betwen one object and all subsequent objects
    for(i=[1:$children-1]) hull(){
        children(0);
        children(i);
    }
}

module microscope_bottom(enlarge_legs=1.5, illumination_clip_void=true, lugs=true, feet=true, legs=true){
    // a 2D representation of the bottom of the microscope
    hull(){
        projection(cut=true) translate([0,0,-d]) wall_inside_xy_stage();
        if(illumination_clip_void){
            translate([0, illumination_clip_y-14]) square([12, d], center=true);
        }
    }
    hull() reflect([1,0,0]) projection(cut=true) translate([0,0,-d]){
        wall_outside_xy_actuators();
        wall_between_actuators();
    }
    if(feet){
        each_actuator() translate([0, actuating_nut_r]) foot_footprint();
        translate([0, z_nut_y]) foot_footprint(tilt=z_actuator_tilt);
    }
    
    if(lugs) projection(cut=true) translate([0,0,-d]) mounting_hole_lugs();
    
    if(legs) offset(enlarge_legs) microscope_legs();
}

module microscope_legs(){
    difference(){
        each_leg() union(){
            projection(cut=true) translate([0,0,-d]) leg();
            projection(cut=true) translate([0,-5,-d]) leg();
        }
        translate([-999,0]) square(999*2);
    }
}

module feet_in_place(grow_r=1, grow_h=2){
    difference() {
        union(){   
            each_actuator() translate([0,actuating_nut_r,0]) minkowski(){
                hull() outer_foot(lie_flat=false);
                cylinder(r=grow_r, h=grow_h, center=true);
            }
            translate([0,z_nut_y,0]) minkowski(){
                hull() middle_foot(lie_flat=false);
                cylinder(r=grow_r, h=grow_h, center=true);
            }
            translate([-9.3,60,0.1]) rotate([0,9,0]) rotate([-20,0,0]) cube([17.5,10,8]);
        } 
        translate([-20,52,-15]) rotate([-25,0,0]) translate([0,-30,0]) cube([40,30,30]);
    }
}

module footprint(){
    hull(){
        translate([-2, illumination_clip_y-14]) square(4);
        each_actuator() translate([0, actuating_nut_r]) foot_footprint();
        translate([0, z_nut_y]) foot_footprint(tilt=z_actuator_tilt);
        offset(wall_thickness) pi_footprint();
    }
}

module bucket_base_stackable(local_h=box_h){
    // The stackable "bucket" before holes and supports
    difference(){
        union(){
            sequential_hull(){
                translate([0,0,0]) linear_extrude(d) offset(0) footprint();
                translate([0,0,local_h-6]) linear_extrude(d) offset(0) footprint();
                translate([0,0,local_h-d]) linear_extrude(inset_depth) offset(wall_thickness) footprint();
            }
            
        }
        
        // hollow out the inside
        sequential_hull(){
            translate([0,0,bottom_thickness]) linear_extrude(d) offset(-wall_thickness) footprint();
            translate([0,0,local_h-10]) linear_extrude(d) offset(-wall_thickness) footprint();
            translate([0,0,local_h-d]) linear_extrude(d) difference(){
                offset(-3.0) footprint();
                translate([-99, illumination_clip_y-14+10-999]) square(999);
                each_actuator() translate([-99, actuating_nut_r-5]) square(999);
            }
            translate([0,0,local_h]) linear_extrude(999) offset(0) footprint();
        }
    }
}

module top_casing_block(local_h=box_h, os=0, legs=true, lugs=true){
    // The "bucket" baseplate before holes and supports (i.e. a solid object)
    bottom = os<0?bottom_thickness:0;
    top_h = os<0?d:inset_depth;
    union(){
        translate([0,0,bottom]) linear_extrude(local_h+d-bottom) offset(os) footprint();
        hull_from(){
            translate([0,0,local_h]) linear_extrude(2*d) offset(os) footprint(); //top of the box
            
            for(a=[0,180]) translate([0,0,local_h+foot_height]) linear_extrude(top_h) difference(){
                offset(os*2+wall_thickness) microscope_bottom(lugs=lugs, feet=false, legs=legs);
                rotate(a) translate([-999,0]) square(999*2);
            }
            //if(legs) translate([0,0,local_h+foot_height-t]) linear_extrude(t+top_h) offset(os+1.5+t) microscope_legs();
        }
        if (os<0) translate([0,0,local_h+foot_height]) linear_extrude(2*inset_depth) offset(0) microscope_bottom(lugs=true);  
    }
}

module bucket_base_with_microscope_top(local_h=box_h){
    // A bucket base for the microscope, without cut-outs
    difference() {
        union() {
            difference(){
                top_casing_block(local_h=local_h, os=0, legs=true);
        
                difference(){
            // we hollow out the casing, but not underneath the legs or lugs.
                    top_casing_block(local_h=local_h, os=-wall_thickness, legs=false, lugs=false);
                    for(p=base_mounting_holes) hull(){
                // double-subtract under the mounting holes to make attachment points
                        translate(p+[0,0,local_h+foot_height-4]) cylinder(r=4,h=4);
                        translate(p*1.2 + [0,0,local_h+foot_height-4-norm(p)*0.3]) cylinder(r=4,h=4+norm(p)*0.3);
                    }
                }
  
            }
            
//The following is a monstrous but necessary kludge.
//A good bridge will need a straight run, but both ends
//are along a curve that shifts with different wall thicknesses.
//I manually located the block once for my chosen wall
//and interpolate for others.
//It is at least close - but not entirely correct.
            pi_frame() {
                translate([-17.06+(wall_thickness-2.35)/sin(90-15.35),raspi_board[1]/2-16,5.8+bottom_thickness+raspi_support]) rotate([0,0,-15.35-0.8*(2.35-wall_thickness)]) translate([-3,0,0]) linear_extrude(height=19.0) {
                    polygon(points=[[3,0], [3.2, 0], [3.2, 35], [3, 35], [-1, 15]]);
                }
            }
        }   
     
        // cut-outs so the feet and legs can protrude downwards
        translate([0,0,local_h+foot_height]) feet_in_place(grow_r=allow_space, grow_h=allow_space);
        intersection(){
            translate([0,0,local_h+foot_height+allow_space]) feet_in_place(grow_r=1.5*allow_space, grow_h=4*allow_space);
            translate([0,0,local_h+foot_height]) cylinder(r=999,h=999,$fn=4);
        }
        translate([0,0,local_h+foot_height-allow_space]) linear_extrude(999) offset(1.5) microscope_legs();
        for(p=base_mounting_holes) if(p[0]>0) reflect([1,0,0]){ 
            translate(p+[0,0,local_h+foot_height]) cylinder(r=3/2*1.7,h=20,$fn=3, center=true); //TODO: better self-tapping holes
            // NB the reflect ensures that the triangular holes work for both y>0 lugs.
            // otherwise the x<0 one snaps when you screw into it.
            // TODO: nut traps underneath these holes
        }
    }
}

module mounting_holes(){
    // holes to mount the buckets together (stacking) or to a breadboard

    // breadboard mounting
    for(p=[[0,0,0], [25,25,0], [-25,25,0], [0,50,0], [0,-25,0]]) translate(p) cylinder(d=6.6,h=999,center=true);
        
    // holes at 3 corners to allow mounting to something underneath/stacking
    // NB the bottom hole is larger to allow for screwing through it, the top 
    // is approximately "self tapping" (a triangular hole, to allow for some 
    // space for swarf).
    mirror([1,0,0]) leg_frame(45)
    translate([0, actuating_nut_r, 0]){
        cylinder(d=4.4, h=20, center=true);
        rotate(90) trylinder_selftap(3, h=999, center=true);
    }
    // this hole is moved out of the way of the sd-card cutout
    leg_frame(45)
    translate([-10, actuating_nut_r-1, 0]){
        cylinder(d=4.4, h=20, center=true);
        rotate(90) trylinder_selftap(3, h=999, center=true);
    }
    translate([0, illumination_clip_y-14+7, 0]){
        cylinder(d=4.4, h=20, center=true);
        rotate(30) trylinder_selftap(3, h=999, center=true);
    }
}

module microscope_stand(){
    // A stand for the microscope, with integrated Raspberry Pi
    difference(){
        union(){
            bucket_base_with_microscope_top();
    
            // supports for the pi circuit board
            pi_supports();
        }
        
// shave some of the extra material off to make a nice bridge above sd card cutout
//This is another ugly kludge, but needed for good bridge.
//Same issue as the other side of the wall - you do not
//know precisely the endpoints.  I fixed it the same way.
//I made it work for my wall size, then interpolated.
//It should be acceptably close for most sane wall sizes.
        pi_frame() {
            translate([-19.24,raspi_board[1]/2-15.96,10+bottom_thickness]) rotate([0,0,-15-0.9*(2.35-wall_thickness)]) rotate([0,-7,0]) translate([-11.5,0,0]) cube([11.5, 31.2, 27]);
        }
        
        // space for pi connectors
        translate([0,0,bottom_thickness + raspi_support]) pi_connectors();
        
        // holes for the pi go all the way through
        pi_support_frame() trylinder_selftap(2.5, h=60, center=true);
        
        mounting_holes();
        
        // if we are building for reflection illumination, cut out the front to allow access
        if(beamsplitter) translate([0,0,local_h+foot_height]) rotate([90,0,0]) cylinder(d=30,h=999);
        
    }
}

module sangaboard_connectors(){
    pi_frame(){
        // USB/network ports
        translate([raspi_board[0]/2,-1,1]) cube(raspi_board + [2,2,-1]);
        // micro-USB power
        //translate([10.6-10/2, -99, -2]) cube([10,100,8]);
        // HDMI
        translate([10, -99, -2]) cube([35,100,18]);
        // micro-SD card
        //translate([0,raspi_board[1]/2+6,0]) cube([80,12,8], center=true);
        //translate([-4,raspi_board[1]/2,0]) cube([16,12,20], center=true);
       // translate([32-25/2,20,-5/2])cube([100,26,21]); // you need to uncomment this and comment the other above to use for low cost microscope.
    }
}

module sangaboard_support_frame(){
    // position supports for each of the sangaboard's mounting screws
    pi_frame() translate([3.5,3.5,bottom_thickness-d]) repeat([57,0,0],2) repeat([0,47,0], 2) children();
}

module sangaboard_supports(){
    // pillars into which the pi can be screwed
    difference(){
        sangaboard_support_frame() cylinder(h=raspi_support+d, d=7);
        // holes for the sangaboard go all the way through
        sangaboard_support_frame() trylinder_selftap(3, h=999, center=true); //these screws are M2.5, not M3
    }
}

module motor_driver_case(){
    // A stackable "bucket" that holds the motor board under the microscope stand
    difference(){
        union(){
            bucket_base_stackable();
    
            // supports for the circuit board
            sangaboard_supports();
        }
        // space for sangaboard connectors
        translate([0,0,bottom_thickness+raspi_support]) sangaboard_connectors();
    
        // motor cables
        translate([0,z_nut_y,box_h]) cube([20,50,15],center=true);
        
        
        mounting_holes();
    }
}


//top_shell();
//feet_in_place();
//footprint();

//motor_driver_case();
microscope_stand();


