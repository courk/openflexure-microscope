/*

Tools for assembling the OpenFlexure Microscope v5.16

(c) 2016 Richard Bowman - released under CERN Open Hardware License

*/

use <utilities.scad>;
use <compact_nut_seat.scad>;
include <microscope_parameters.scad>;

ns = nut_slot_size();
shaft_d = nut_size()*1.1;
gap = 9; //size of the gap between gear and screw seat
swing_a = 30; //angle through which the tool swings
sso = ss_outer(25); //outer size of screw seat
handle_w = shaft_d+4; //width of the "handle" part
handle_l = sso[0]/2+gap; //length of handle part


module tool_handle(){
    w = handle_w;
    difference(){
        sequential_hull(){
            rotate([-swing_a,0,0]) translate([-w/2,0,0]) cube([w,sso[0]/2,gap]);
            translate([-w/2,ns[2],0]) cube([w,d,ns[2]]);
            translate([-w/2,sso[0]/2*cos(swing_a)+gap*sin(swing_a),0]) cube([w,d,ns[2]]);
            translate([-ns[0]/2,handle_l,0]) cube([ns[0],d,ns[2]]);
        }
        //ground (or bottom of gear)
        mirror([0,0,1]) cylinder(r=999,h=999,$fn=4);
        //screw seat (in swung-in position)
        rotate([0,180-swing_a,-90]) translate([0,0,-(gap+sso[2]/2)]) screw_seat_shell(25);
        //screw
        rotate([-swing_a,0,0]) cylinder(d=shaft_d,h=999,center=true, $fn=16);
    }
}

module xz_slice(){
    //slice out just the part of something that sits in the XZ plane
    intersection(){
        cube([9999,2*d,9999],center=true);
        children();
    }
}
module nut_and_band_tool(nut_slot=nut_slot){
    //This tool assists with inserting both the nuts and elastic bands.
    //At some point I'll make one for springs, if needed...?
    w = nut_slot[0]-0.5;
    l = actuator_h+36;
    h = nut_slot[2]-0.4;
    n = nut_size;
    nut_y = 0;
    hook_w = 3.5;
    difference(){
        sequential_hull(){
            translate([-w/2, 0,0]) cube([w,d,h]);
            translate([-w/2, 20,0]) cube([w,d,h]);
            union(){
                translate([-hook_w/2-2.5/2, l-12,0]) cube([hook_w+2.5,12,h]);
                translate([-hook_w/2-2.5, l-12,h-1]) cube([hook_w+5,12,1]);
            }
        }
        
        // hold the nut here
        translate([0,nut_y,-d]) rotate(30) cylinder(r=n*1.15, h=999, $fn=6);
        // slot at the other end for band insertion
        hull(){
            translate([0,l,h]) rotate([90,0,0]) cylinder(r=2.5,h=18,center=true);
            translate([0,l,0]) cube([hook_w,18,d],center=true);
        }
        // V shaped end to grip elastic bands
        translate([-99,l,0])hull(){
            translate([0,-1.5,0.75]) cube([999,999,0.5]);
            translate([0,0,0.5]) cube([999,999,h-0.75]);
        }
    }
}
       
module nut_tool(){
    w = ns[0]-0.5; //width of tool tip (needs to fit through the slot that's ns[0] wide
    h = ns[2]-0.4; //height of tool tip (needs to fit through slot)
    l = 5+sso[1]/2+3;
    difference(){
        union(){
            translate([0,-handle_l,0]) tool_handle();
            sequential_hull(){
                xz_slice() translate([0,-handle_l,0]) tool_handle();
                translate([-w/2, 5, 0]) cube([w, d, h]);
                translate([-w/2, l, 0]) cube([w, d, h]);
            }
        }
        
        //nut 
        translate([0,l,-d])rotate(30)cylinder(r=nut_size()*1.15, h=999, $fn=6);
        translate([0,l-nut_size()*1.15+0.6,-d]) cylinder(r=1,h=999,$fn=12);
    }
}

module band_tool(){
    w = ns[0]-0.5; //width of tool tip (needs to fit through the slot that's ns[0] wide
    h = ns[2]-0.4; //height of tool tip (needs to fit through slot)
    l = sso[2]/2+foot_height+5;
    hook_w = 3.5;
    difference(){
        union(){
            translate([0,-handle_l,0]) tool_handle();
            hull(){
                xz_slice() translate([0,-handle_l,0]) tool_handle();
                translate([-hook_w/2-2.5/2, l-12,0]) cube([hook_w+2.5,12,h]);
                translate([-hook_w/2-2.5, l-12,h-1]) cube([hook_w+5,12,1]);
            }
        }
        // slot at the end for band insertion
        hull(){
            translate([0,l,h]) rotate([90,0,0]) cylinder(r=2.5,h=18,center=true);
            translate([0,l,0]) cube([hook_w,18,d],center=true);
        }
        // V shaped end to grip elastic bands
        translate([-99,l,0])hull(){
            translate([0,-1.5,0.75]) cube([999,999,0.5]);
            translate([0,0,0.5]) cube([999,999,h-0.75]);
        }
    }
}


band_tool();
translate([10,0,0]) nut_tool();
