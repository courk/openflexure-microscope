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
    output = "build/main_body_LS" + size + motors + brim + ".stl"
    parameters = ["-D big_stage=true"]

    if brim == "":
        parameters.append("-D enable_smart_brim=false")
    else:
        parameters.append("-D enable_smart_brim=true")

    parameters.append("-D sample_z=" + size)

    if motors == "":
        parameters.append("-D motor_lugs=false")
    else:
        parameters.append("-D motor_lugs=true")

    ninja.build(
        output,
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
    output = f"build/optics_{camera}_{lens}_LS65.stl"
    parameters = ["-D big_stage=true", "-D sample_z=65"]
    parameters.append(f"-D 'optics=\"{lens}\"'")
    parameters.append(f"-D 'camera=\"{camera}\"'")
    ninja.build(
        output,
        rule="openscad",
        inputs="openscad/optics.scad",
        variables={"parameters": " ".join(parameters)},
    )


stand_versions = ["LS65-30", "LS65-160"]

sample_riser_versions = ["LS10"]
slide_riser_versions = ["LS10"]

build_file.close()
run_build()
