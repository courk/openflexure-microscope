/******************************************************************
*                                                                 *
* OpenFlexure Microscope: Illumination arm                        *
*                                                                 *
* This is part of the OpenFlexure microscope, an open-source      *
* microscope and 3-axis translation stage.  It gets really good   *
* precision over a ~10mm range, by using plastic flexure          *
* mechanisms.                                                     *
*                                                                 *
* This file deals with the dovetail clips that are used to hold   *
* the objective and illumination, and provide coarse Z adjustment.*
*                                                                 *
* (c) Richard Bowman, January 2016                                *
* Released under the CERN Open Hardware License                   *
*                                                                 *
******************************************************************/

use <utilities.scad>;
$fn=16;
d=0.05;

module dovetail_clip_cutout(size,dt=1.5,t=2){
    // This will form a female dovetail when subtracted from a block.
    // cut this out of a cube (of size "size", with one edge centred along
    // the X axis extending into +y, +z
    // dt sets the size of the 45-degree clips
    // t sets the thickness of the dovetail arms (2mm is good)
    // I reccommend using ~8-10mm arms for a tight fit.  On all my
    // printers, the ooze of the plastic is enough to keep it tight, so I
    // set the size of the M and F dovetails to be identical.  You might
    // want to make it tighter, either by increasing dt slightly or by
    // decreasing the size slightly (in both cases, of this, the female
    // dovetail).
    // NB that it starts at z=-d and stops at z=size[2]+d to make
    // it easy to subtract from a block.
	hull() reflect([1,0,0]) translate([-size[0]/2+t,0,-d]){
		translate([dt,size[1]-dt,0]) cylinder(r=dt,h=size[2]+2*d,$fn=16);
		translate([0,dt,0]) rotate(-45) cube([dt*2,d,size[2]+2*d]);
	}
}
module dovetail_clip(size=[10,2,10],dt=1.5,t=2,back_t=0){
    // This forms a clip that will grip a dovetail, with the
    // contact between the m/f parts in the y=0 plane.
    // This is the female part, and it is centred in X and 
    // extends into +y, +z.
    // The outer dimensions of the clip are given by size.
    // dt sets the size of the clip's teeth, and t is the
    // thickness of the arms.  By default it has no back, and
    // should be attached to a solid surface.  Specifying back_t>0
    // will add material at the back (by shortening the arms).
	difference(){
		translate([-size[0]/2,0,0]) cube(size);
		dovetail_clip_cutout(size-[0,back_t,0],dt=dt,t=t,h=999);
	}
}

module dovetail_plug(corner_x, r, dt, zx_profile=[[0,0],[10,0],[12,-1]]){
    // Just the "plug" of a male dovetail (i.e. not the flat surface
    // it's attached to, just the bit that fits inside the female).
    // zx_profile is a list of 2-element vectors, each of which defines
    //   a point in Z-X space, i.e. first element is height and second
    //   is the shift in the corner position.  For example,
    //   zx_profile=[[0,0],[10,0],[12,-1]] creates a plug 12mm+d high 
    //   where the top 2mm are sloped at 60 degrees.  NB the use of d.
    union(){
        // sorry for the copy-paste code; I'm fairly sure it's less readable
        // if I arrange things in a way that avoids it...
        // four fat cylinders make the contact point
        for(i=[0:len(zx_profile)-2]){
            hull() for(j=[0:1]){
                z = zx_profile[i+j][0];
                x = zx_profile[i+j][1];
                reflect([1,0,0]) translate([corner_x+x,0,z]) rotate(45) translate([sqrt(3)*r,r,0]) repeat([dt*sqrt(2) - (1+sqrt(3))*r,0,0],2) cylinder(r=r,h=d);
            }
        }
        // another four cylinders join the plug to the y=0 plane
        for(i=[0:len(zx_profile)-2]){
            hull() for(j=[0:1]){
                z = zx_profile[i+j][0];
                x = zx_profile[i+j][1];
                reflect([1,0,0]) translate([corner_x+x,0,z]) rotate(45) repeat([sqrt(3)*r,r,0],2) cylinder(r=d,h=d);
            }
        }
    }
}
module dovetail_m(size=[10,2,10],dt=1.5,t=2,top_taper=1,bottom_taper=0.5,waist=0,waist_dx=0.5){
    // Male dovetail, contact plane is y=0, dovetail is in y>0
    // size is a box that is centred in X, sits on Z=0, and extends
    // in the -y direction from y=0.  This is the mount for the
    // dovetail, which sits in the +y direction.
    // The width of the box should be the same as the width of the
    // female dovetail clip.  The size of the dovetail is set by dt.
    // t sets the thickness of the female dovetail arms; the dovetail
    // is actually size[0]-2*t wide.
    r=0.5; //radius of curvature - something around nozzle width is good.
    w=size[0]-2*t; //width of dovetail
    h=size[2]; //height
    corner=[w/2-dt,0,0]; //location of the pointy bit of the dovetail
    difference(){
		union(){
            //back of the dovetail (the mount) plus the start of the
            //dovetail's neck (as far as y=0)
			sequential_hull(){
                // start with the cube that the dovetail attaches to
				translate([-w/2-t,-size[1],0]) cube([w+2*t,size[1]-r,h]);
                // then add shapes that take in the centres of the cylinders
                // from the next step.  This joins together the nicely-rounded
                // contact points, such that when we subtract out the cylinders
                // at the corners we get a nice smooth shape.
                reflect([1,0,0]) translate(corner+[sqrt(3)*r,-r,0]) cylinder(r=d,h=h);
                reflect([1,0,0]) translate(corner) cylinder(r=d,h=h);
			}
            //contact points (with rounded edges to avoid burrs)
			difference(){
				union(){
					reflect([1,0,0]) hull(){
						translate(corner+[sqrt(3)*r,-r,0]) cylinder(r=r,h=h);	
						translate([w/2+t-r,-r,0]) cylinder(r=r,h=h);	
                    }
					//hull() reflect([1,0,0]) translate(corner) rotate(45) translate([sqrt(3)*r,r,0]) repeat([1,0,0],2) cylinder(r=r,h=h);
                    // the "plug" is tapered for easy insertion, and may
                    // have optional indents in the middle (a "waist").
                    waist_dx = waist>waist_dx*4 ? waist_dx : 0;
                    waist_dz = waist>waist_dx*4 ? waist_dx*2 : d;
                    zx_profile = [[0,-bottom_taper],
                                  [bottom_taper,0],
                                  [h/2-waist/2,0],
                                  [h/2-waist/2+waist_dz,-waist_dx],
                                  [h/2+waist/2-waist_dz,-waist_dx],
                                  [h/2+waist/2,0],
                                  [h-top_taper,0],
                                  [h-d,-top_taper/2]];
                    dovetail_plug(corner[0], r, dt, zx_profile);
                        
				}
			}
		}
        // We round out the internal corner so that we grip with the edges
        // of the tooth and not the point (you get better contact this way).
		reflect([1,0,0]) translate(corner) cylinder(r=r,h=3*h,center=true);
	}
}

test_size = [12,10,24];
test_dt = 2;
color("blue") dovetail_clip(test_size,dt=test_dt);
color("green") translate([0,0,-2]) dovetail_m(test_size, waist=10, dt=test_dt,waist_dx=0.2);
