#!/usr/bin/env python3
from ninja import Writer, ninja as run_build
import json
import os
import sys


build_file = open("build.ninja", "w")
ninja = Writer(build_file, width=120)

generate_stl_options = (
    len(sys.argv) > 1 and sys.argv[1] == "--generate-stl-options-json"
)

if generate_stl_options:
    # ninja looks at the arguments and would get confused if we didn't remove it
    sys.argv.pop()

ninja.rule(
    "openscad", command="openscad $parameters $in -o $out -d $out.d", depfile="$out.d"
)

build_dir = "builds"


def parameters_to_string(parameters):
    """
    Build an OpenScad parameter arguments string from a variable name and value

    Arguments:
        parameters {dict} -- Dictionary of parameters
    """
    strings = []
    for name in parameters:
        value = parameters[name]
        # Convert bools to lowercase
        if type(value) == bool:
            value = str(value).lower()
        # Wrap strings in quotes
        elif type(value) == str:
            value = f'"{value}"'

        strings.append("-D '{}={}'".format(name, value))

    return " ".join(strings)


if generate_stl_options:
    stl_options = {}


def openscad(
    output,
    input,
    parameters=None,
    file_local_parameters=None,
    stl_selection_parameters=None,
):
    """
    Invokes ninja task generation using the 'openscad' rule. if
    --generate-stl-options-json is enabled we register the stl and it's
    parameters at this point.

    Arguments:
        output {str} -- file path of the output stl file
        input {str} -- file path of the input scad file
        parameters {dict} -- values of globally used parameters
        file_local_parameters {dict} -- values of parameters only used for this specific scad file
        stl_selection_parameters {dict} -- values of parameters not used by openscad but relevant to selecting this stl when making a specific variant
    """

    if parameters is None:
        parameters = {}
    if file_local_parameters is None:
        file_local_parameters = {}
    if stl_selection_parameters is None:
        stl_selection_parameters = {}

    if generate_stl_options:
        input_file = os.path.relpath(input, "openscad/")
        output_file = os.path.relpath(output, build_dir)

        # prefix any file-local parameters with the input file name so they
        # don't look like global parameters
        prefix = os.path.splitext(input_file)[0] + ":"
        flp_prefixed = {}
        for k, v in file_local_parameters.items():
            flp_prefixed[prefix + k] = v

        stl_options[output_file] = {
            "input": input_file,
            "parameters": {**parameters, **stl_selection_parameters, **flp_prefixed},
        }

    ninja.build(
        output,
        rule="openscad",
        inputs=input,
        variables={
            "parameters": parameters_to_string({**parameters, **file_local_parameters})
        },
    )


def stage_parameters(stage_size, sample_z):
    """
    Return common stage parameters for a given size and sample z

    Arguments:
        stage_size {str} -- Stage size, e.g. "LS"
        sample_z {int} -- Sample z position, default 65
    """
    return {"big_stage": stage_size == "LS", "sample_z": sample_z}


################################
### GENERAL, WIDELY USED OPTIONS

# All available microscope sizes
stage_size_options = ["LS"]
sample_z_options = [65]
# All permutations of microscope size
microscope_size_options = [
    f"{stage_size}{sample_z}"
    for stage_size in stage_size_options
    for sample_z in sample_z_options
]


###################
### MICROSCOPE BODY

for stage_size in stage_size_options:
    for sample_z in sample_z_options:
        for beamsplitter in [True, False]:
            for brim in [True, False]:
                motors = True  # Right now we never need to remove motor lugs

                output = "{build_dir}/main_body_{stage_size}{sample_z}{motors}{beamsplitter}{brim}.stl".format(
                    build_dir=build_dir,
                    stage_size=stage_size,
                    sample_z=sample_z,
                    motors="-M" if motors else "",
                    beamsplitter="-BS" if beamsplitter else "",
                    brim="_brim" if brim else "",
                )

                parameters = {
                    **stage_parameters(stage_size, sample_z),
                    "motor_lugs": motors,
                    "beamsplitter": beamsplitter,
                    "enable_smart_brim": brim,
                }

                openscad(
                    output, "openscad/main_body.scad", parameters
                )


#################
### OPTICS MODULE

cameras = ["picamera_2", "logitech_c270", "m12"]

rms_lenses = [
    "rms_f40d16",
    "rms_f50d13",
    "rms_infinity_f50d13",
]  # NB: Only RMS lenses are compatible with the beamsplitter

optics_versions = [
    ("picamera_2", "pilens"),
    ("logitech_c270", "c270_lens"),
    ("m12", "m12_lens"),
] + [(camera, lens) for camera in cameras for lens in rms_lenses]

for sample_z in sample_z_options:
    for (camera, lens) in optics_versions:
        beamsplitter_options = [True, False] if lens in rms_lenses else [False]

        for beamsplitter in beamsplitter_options:
            output = "{build_dir}/optics_{camera}_{lens}{beamsplitter}.stl".format(
                build_dir=build_dir,
                camera=camera,
                lens=lens,
                beamsplitter="_beamsplitter" if beamsplitter else "",
            )

            parameters = {
                "sample_z": sample_z,
                "optics": lens,
                "camera": camera,
                "beamsplitter": beamsplitter,
            }

            openscad(output, "openscad/optics.scad", parameters)


####################
### MICROSCOPE STAND

# Stand with pi
for stand_height in [30]:
    for beamsplitter in [True, False]:
        output = "{build_dir}/microscope_stand_{stand_height}{beamsplitter}.stl".format(
            build_dir=build_dir,
            stand_height=stand_height,
            beamsplitter="-BS" if beamsplitter else "",
        )

        parameters = {"beamsplitter": beamsplitter}

        openscad(
            output,
            "openscad/microscope_stand.scad",
            parameters,
            file_local_parameters={"h": stand_height},
            stl_selection_parameters={"raspberry_pi": True},
        )

# Stand without pi
openscad(
    "builds/microscope_stand_no_pi.stl",
    input="openscad/microscope_stand_no_pi.scad",
    parameters={},
    stl_selection_parameters={"raspberry_pi": False},
)


########
### FEET

for foot_height in [15, 26]:

    # Figure out some nice names for foot heights
    if foot_height == 26:
        version_name = "_tall"
    elif foot_height == 15:
        version_name = ""
    else:
        version_name = f"_{foot_height}"

    output = "{build_dir}/feet{version}.stl".format(
        build_dir=build_dir, version=version_name
    )

    parameters = {"foot_height": foot_height}

    openscad(output, "openscad/feet.scad", parameters)


###################
### CAMERA PLATFORM

for stage_size in stage_size_options:
    for sample_z in sample_z_options:
        for version in ["picamera_2", "6led"]:
            output = "{build_dir}/camera_platform_{version}_{stage_size}{sample_z}.stl".format(
                build_dir=build_dir,
                version=version,
                stage_size=stage_size,
                sample_z=sample_z,
            )

            parameters = {
                **stage_parameters(stage_size, sample_z),
                "optics": "pilens",
                "camera": version,
            }

            openscad(
                output, "openscad/camera_platform.scad", parameters
            )


###############
### LENS SPACER

for stage_size in stage_size_options:
    for sample_z in sample_z_options:
        output = "{build_dir}/lens_spacer_picamera_2_pilens_{stage_size}{sample_z}.stl".format(
            build_dir=build_dir, stage_size=stage_size, sample_z=sample_z
        )

        parameters = {**stage_parameters(stage_size, sample_z), "optics": "pilens"}

        openscad(output, "openscad/lens_spacer.scad", parameters)


##################
### PICAMERA TOOLS

picamera_2_tools = ["cover", "gripper", "lens_gripper"]
for tool in picamera_2_tools:
    output = f"builds/picamera_2_{tool}.stl"
    input = f"openscad/cameras/picamera_2_{tool}.scad"

    parameters = {"camera": "picamera_2"}

    openscad(output, input, parameters)


#################
### SAMPLE RISERS

for riser_type in ["sample", "slide"]:
    output = f"builds/{riser_type}_riser_LS10.stl"
    input = f"openscad/{riser_type}_riser.scad"

    parameters = {"big_stage": True}

    openscad(
        output, input, parameters, file_local_parameters={"h": 10}
    )


###############
### SMALL PARTS

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
    "fl_cube",
    "reflection_illuminator",
]

for part in parts:
    output = f"builds/{part}.stl"
    input = f"openscad/{part}.scad"
    openscad(output, input)


###############
### RUN BUILD

build_file.close()
run_build()

if generate_stl_options:

    def merge_dicts(d1, d2):
        """
        Recursively merge two dictionaries condensing all non-dict values into
        sets. The result is a dict containing sets of all the values used.

        >>> merge_dicts({'a': 1}, {'a': 2})
        {'a': {1, 2}}
        >>> merge_dicts({'a': 1}, {'b': 2})
        {'a': {1}, 'b': {2}}
        >>> merge_dicts({'a': {'b': 2}}, {'a': {'b': 1}})
        {'a': {'b': {1, 2}}}

        We assume that the dicts are compatible in structure: one dict
        shouldn't have a value where the other has a dict or a TypeError will
        be raised.

        >>> merge_dicts({'a': 1}, {'a': {'b': 1}})
        TypeError: Expecting 'dict' at key 'a', got <class 'set'>


        Any sets that are values in the original dicts are merged in.

        >>> merge_dicts({'a': {1}, {'a': {2}})
        {'a': {1, 2}}
        >>> merge_dicts({'a': 1, {'a': {2}})
        {'a': {1, 2}}

        Arguments:
            d1 {dict}
            d2 {dict}

        """
        merged = {}
        for d in [d1, d2]:
            for k, v in d.items():
                if type(v) is dict:
                    if k not in merged:
                        merged[k] = {}
                    if type(merged[k]) is not dict:
                        raise TypeError(
                            "Expecting 'dict' at key '{}', got {}".format(
                                k, type(merged[k])
                            )
                        )

                    merged[k] = merge_dicts(merged[k], v)

                elif type(v) is set:
                    if k not in merged:
                        merged[k] = set()
                    if type(merged[k]) is not set:
                        raise TypeError(
                            "Expecting 'set' at key '{}', got {}".format(
                                k, type(merged[k])
                            )
                        )

                    merged[k] = merged[k].union(v)

                else:
                    if k not in merged:
                        merged[k] = set()

                    merged[k].add(v)

        return merged

    # condense all used parameters down to sets of possible values
    available_options = {}
    for stl_file, v in stl_options.items():
        available_options = merge_dicts(available_options, v["parameters"])

    # filter out parameters that are never changed and rename {True, False}
    # values to "bool"
    changeable_options = {}
    for name, options in available_options.items():
        if len(options) > 1:
            if options == {False, True}:
                changeable_options[name] = "bool"
            else:
                changeable_options[name] = options

    def encode_set(s):
        """ encode 'set' as 'list' when converting to JSON """
        if type(s) is set:
            return list(s)
        else:
            raise TypeError("Expecting 'set' got {}".format(type(s)))

    with open("builds/stl_options.json", "w") as f:
        json.dump(
            {"stls": stl_options, "options": changeable_options},
            f,
            indent=2,
            default=encode_set,
        )
    print("generated builds/stl_options.json")
