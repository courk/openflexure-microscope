#!/usr/bin/env python3
from ninja import Writer, ninja as run_build

build_file = open("build.ninja", "w")
ninja = Writer(build_file, width=120)

ninja.rule(
    "openscad", command="openscad $parameters $in -o $out -d $out.d", depfile="$out.d"
)


body_versions = [
    (size, motors, brim)
    for size in ["65"]
    for motors in ["-M", ""]
    for brim in ["", "_brim"]
]


for size, motors, brim in body_versions:
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

    output = "build/main_body_LS" + size + motors + brim + ".stl"

    ninja.build(
        output,
        rule="openscad",
        inputs="openscad/main_body.scad",
        variables={"parameters": " ".join(parameters)},
    )


build_file.close()
run_build()
