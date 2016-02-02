use <utilities.scad>;

//this is for mini culture plates, 39mm outer diameter and 12.4mm high
sample=[0,19/2,12.4-1.5-9]; //position of clamping point relative to bolt

$fn=32;


//rotate([0,90,0]) 
module sample_clip(sample,t=2.5,w=6,roc=-1,slope=30){
    roc = roc>0 ? roc : sample[2]/2 + sample[1]*sin(slope) - t/2; //radius of curvature
    a = sqrt(pow(sample[1], 2) + pow(sample[2] - roc - t/2, 2));
      //a is the distance from the contact-point cylinder to the 
      //centre of the curved part
    angle = acos( (roc + t/2) / a ) + atan((sample[2] - roc - t/2)/sample[1]); //angle through which we must rotate the join between
    //curved part and straight part
    echo("angle set to:",angle);
    /*angle = 75; //angle of straight part to the vertical
    roc =*/ 
    difference(){
        union(){
            //anchor to stage
            hull() repeat([sample[0],0,0],2) cylinder(r=w/2,h=t);
            
            translate([0,0,roc+t]) rotate([0,90,0]) difference(){
                cylinder(r=roc+t,h=6,center=true);
                cylinder(r=roc,h=999,center=true);
                translate([0,0,-99]) rotate(0) cube([999,999,999]);
                translate([0,0,-99]) rotate(angle) cube([999,999,999]);
            }
            sequential_hull(){
                translate([0,0,roc+t]) rotate([0,90,0]) rotate(angle) translate([0,roc+t/2,0]) cylinder(r=t/2,h=6,center=true);
                translate([0,sample[1],sample[2]+t/2]) rotate([0,90,0]) cylinder(r=t/2,h=6,center=true);
                translate([0,sample[1]+t,sample[2]+t]) rotate([0,90,0]) cylinder(r=t/2,h=6,center=true);
            }
            
        }
        cylinder(r=3/2*1.2,h=999,center=true,$fn=16);
    }
}

sample_clip([0,19/2+3,12.4-1.5],slope=7.5);
/*
translate([10,0,0]) sample_clip([0,20,0]);
translate([20,0,0]) sample_clip([0,20,10]);
translate([30,0,0]) sample_clip([0,10,3]);
translate([40,0,0]) sample_clip([0,10,15]);
*/