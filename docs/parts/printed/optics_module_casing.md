# Optics module casing
This is a printed tube, into which the objective lens, (optionally) tube lens, and camera are all fitted.  There are various different versions depending on what optics options you have picked.  As of v5.20 there are two basic designs of the optics module - the one-piece design (used primarily for the high resolution versions of the microscope) and the two-part design (better for low-resolution microscopes).  This page describes the one-piece module.

## Printing instructions
There are several versions of the optics module, depending on your camera (Raspberry Pi Camera v2, Logitech C270, or USB camera with M12 lens) and on whether you will use the lens from the camera (pilens, M12, ownlens) or an RMS objective and 40mm tube lens.  Make sure you pick the right STL file for your camera module!  There is an optional cover that fits over the Raspberry Pi camera module, and holds it firmly onto the optics module.

The optics module needs to print with some fine detail, so the dovetail meshes nicely with the stage.  A good way to ensure this is to print it at the same time as other parts - either print more than one optics module at a time, or print it at the same time as the microscope body.  This slows down the time for each layer, and means the plastic can cool more completely before the layer on top is deposited, resulting in a higher-quality part.  The optics module is best printed in black to cut down on stray light inside the tube - though it will still work in other colours.

## STL Files
The STL file for this part will be named ``optics_<camera>_<lens>_<body>.stl``.  The three options can take various values:
* ``<camera>`` can be:
  - ``picamera_2`` for the Raspberry Pi camera module (v1 should fit the same parts, but it's deprecated).
  - ``logitech_c270`` for a Logitech C270 webcam (NB you'll need to remove its casing).
  - ``m12`` for a USB webcam with an M12 lens, such as the typical boards sourced from China for $3
* ``<lens>`` can be:
  - ``rms_f50d13`` to use a finite-conjugates RMS [microscope objective](../optics/objective.md), together with a [tube lens](../optics/tube_lens.md) with 50mm focal length and outer diameter of 12.7mm (half an inch).  This is the recommended option.
  - ``rms_infinity_f50d13`` is the same as the above, but for infinite-conjugates objectives.  It is, currently, untested.
  - ``rms_f40d16`` is for finite-conjugates RMS objectives, but with a (cheaper) 16mm diameter, 40mm focal length lens.  It produces less good images than the 50mm focal length version (largely because the 40mm lenses we sourced were singlets rather than doublets).
  - ``pilens``, ``c270_lens``, or ``M12_lens`` for the lens supplied with the respective camera module.  This option will produce high-magnification, but low-resolution, images.  It is not recommended: use the two-part low resolution optics module instead.
* ``<body>`` is now always ``LS65``.  Bear in mind, when using the RMS objectives, that there are two common heights - 35mm parfocal and 45mm parfocal.  45mm is more common on Plan-corrected objectives, which generally give better images.  In order to use a 45mm objective, you should pick the ``LS65`` module, but raise the sample up 10mm using the [sample riser](./sample_riser.md)




