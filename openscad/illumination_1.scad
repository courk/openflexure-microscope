use <utilities.scad>;

$fn=32;
h=28;
neck_h=10;
outer_r=5; //radius of tube
inner_r=5.5; //inner radius of bottom of tube
lens_outer_r=3.04+0.15; //outer radius of lens 
lens_aperture_r=2.2; //clear aperture of lens
lens_t=3.0; //thickness of lens

n_cones=floor((h-lens_t)/2); //how many ridges to make
cone_h=(h-lens_t)/n_cones; //height of each ridge
cone_dr=cone_h/2; //change in radius over each cone


objective_clip_w = 10;
objective_clip_y = 6;

d=0.05;


module clip_tooth(h){
	intersection(){
		cube([999,999,h]);
		rotate(-45) cube([1,1,1]*999*2);
	}
}

module objective_body(){
	assign(r=0.5,corner=[objective_clip_w/2-1.5,objective_clip_y,0]) difference(){
		union(){
			cylinder(r=8,h=h-neck_h); //body
			difference(){
				union(){
					reflect([1,0,0]) translate(corner+[sqrt(3)*r,-r,0]) hull() repeat([1,0,0],2) cylinder(r=r,h=h-neck_h);	
					hull() reflect([1,0,0]) translate(corner) rotate(45) translate([sqrt(3)*r,r,0]) repeat([1,0,0],2) cylinder(r=r,h=h-neck_h);
				}
			}
		}
		reflect([1,0,0]) translate(corner) cylinder(r=r,h=2*h,center=true);
		reflect([1,0,0]) translate(corner+[0,0,-1]) clip_tooth(999);
	}
}

module objective(){
	difference(){
		objective_body();
	
		translate([0, 0, h-lens_t]) cylinder(r=lens_outer_r, h=999); //lens
	
		//clearance for beam, with light-trapping edges
		for(i = [0 : n_cones - 1]) assign(p = i/(n_cones - 1))
			translate([0, 0, i * cone_h - d]) 
				cylinder(r1=(1-p)*inner_r + p*(lens_aperture_r + cone_dr),
							r2=(1-p)*(inner_r - cone_dr) + p*lens_aperture_r,
							h=cone_h+2*d);
	}
}

//intersection(){
//	objective();
//	translate([0,0,h-neck_h+2]) cylinder(r=999,h=999);
//}
objective();