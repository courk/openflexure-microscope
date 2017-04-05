// This is a trivial tool to support a 16mm lens as it is inserted
// into the holder.  Part of the OpenFlexure Microscope.

// (c) 2017 Richard Bowman, released under CERN open hardware license.

difference(){
    cylinder(d=12.5, h=6, $fn=32);
    cylinder(d=10.5, h=999, center=true, $fn=32);
}