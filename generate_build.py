from ninja import Writer

f = open("build.ninja", "w")
ninja = Writer(f, width=120)

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
    parameters = "-D 'big_stage=true'"

    if brim == "":
        parameters += " -D 'enable_smart_brim=false'"
    else:
        parameters += " -D 'enable_smart_brim=true'"

    parameters += " -D 'sample_z={}'".format(size)

    if motors == "":
        parameters += " -D 'motor_lugs=false'"
    else:
        parameters += " -D 'motor_lugs=true'"

    output = "build/main_body_LS" + size + motors + brim + ".stl"

    ninja.build(
        output,
        rule="openscad",
        inputs="openscad/main_body.scad",
        variables={"parameters": parameters},
    )
