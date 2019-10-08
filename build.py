#!/usr/bin/env python3
from ninja import Writer, ninja as run_build

build_file = open("build.ninja", "w")
ninja = Writer(build_file, width=120)

ninja.rule(
    "openscad", command="openscad $parameters $in -o $out -d $out.d", depfile="$out.d"
)

for brim in ["", "_brim"]:
    size = "65"
    motors = "-M"
    outputs = "builds/main_body_LS" + size + motors + brim + ".stl"
    parameters = ["-D big_stage=true", "-D sample_z=65", "-D motor_lugs=true"]

    if brim == "":
        parameters.append("-D enable_smart_brim=false")
    else:
        parameters.append("-D enable_smart_brim=true")

    ninja.build(
        outputs,
        rule="openscad",
        inputs="openscad/main_body.scad",
        variables={"parameters": " ".join(parameters)},
    )


cameras = ["picamera_2", "logitech_c270", "m12"]
rms_lenses = ["rms_f40d16", "rms_f50d13", "rms_infinity_f50d13"]
optics_versions = [
    ("picamera_2", "pilens"),
    ("logitech_c270", "c270_lens"),
    ("m12", "m12_lens"),
] + [(camera, lens) for camera in cameras for lens in rms_lenses]

for (camera, lens) in optics_versions:
    outputs = f"builds/optics_{camera}_{lens}_LS65.stl"
    parameters = ["-D big_stage=true", "-D sample_z=65", "-D enable_smart_brim=false"]
    parameters.append(f"-D 'optics=\"{lens}\"'")
    parameters.append(f"-D 'camera=\"{camera}\"'")
    ninja.build(
        outputs,
        rule="openscad",
        inputs="openscad/optics.scad",
        variables={"parameters": " ".join(parameters)},
    )


camera_platform_versions = ["picamera_2", "6led"]
for version in camera_platform_versions:
    outputs = f"builds/camera_platform_{version}_LS65.stl"
    parameters = ["-D big_stage=true", "-D sample_z=65", "-D enable_smart_brim=false"]
    parameters.append("-D 'optics=\"pilens\"'")
    parameters.append(f"-D 'camera=\"{version}\"'")
    ninja.build(
        outputs,
        rule="openscad",
        inputs="openscad/camera_platform.scad",
        variables={"parameters": " ".join(parameters)},
    )

feet_versions = ["", "_tall"]
for version in feet_versions:
    outputs = f"builds/feet{version}.stl"
    if version == "_tall":
        parameters.append("-D foot_height=26")
    ninja.build(
        outputs,
        rule="openscad",
        inputs="openscad/camera_platform.scad",
        variables={"parameters": " ".join(parameters)},
    )

parameters = ["-D big_stage=true", "-D sample_z=65", "-D enable_smart_brim=false"]
parameters.append("-D 'optics=\"pilens\"'")
ninja.build(
    outputs="builds/lens_spacer_picamera_2_pilens_LS65.stl",
    rule="openscad",
    inputs="openscad/lens_spacer.scad",
    variables={"parameters": " ".join(parameters)},
)

picamera_2_tools = ["cover", "gripper", "lens_gripper"]
for tool in picamera_2_tools:
    outputs = f"builds/picamera_2_{tool}.stl"
    inputs = f"openscad/cameras/picamera_2_{tool}.scad"
    parameters = ["-D 'camera=\"picamera_2\"'"]
    ninja.build(
        outputs,
        rule="openscad",
        inputs=inputs,
        variables={"parameters": " ".join(parameters)},
    )

stand_versions = ["", "_no_pi"]
for version in stand_versions:
    output = f"builds/microscope_stand{version}.stl"
    inputs = f"openscad/microscope_stand{version}.scad"
    parameters = ["-D big_stage=true", "-D sample_z=65", "-D enable_smart_brim=false"]
    ninja.build(
        output,
        rule="openscad",
        inputs=inputs,
        variables={"parameters": " ".join(parameters)},
    )


riser_types = ["sample", "slide"]
for t in riser_types:
    outputs = f"builds/{t}_riser_LS10.stl"
    inputs = f"openscad/{t}_riser.scad"
    parameters = ["-D big_stage=true", "-D h=10"]
    ninja.build(
        outputs,
        rule="openscad",
        inputs=inputs,
        variables={"parameters": " ".join(parameters)},
    )

parts = [
    "actuator_assembly_tools",
    "actuator_drilling_jig",
    "back_foot",
    "condenser",
    "gears",
    "illumination_dovetail",
    "lens_tool",
    "motor_driver_case",
    "sample_clips",
    "small_gears",
    "thumbwheels",
]

for part in parts:
    outputs = f"builds/{part}.stl"
    inputs = f"openscad/{part}.scad"
    ninja.build(
        outputs,
        rule="openscad",
        inputs=inputs,
    )


build_file.close()
run_build()
