#!/usr/bin/env python3
from ninja import Writer, ninja as run_build
import json
import os
import sys
import pathlib
import operator

build_dir = "builds"

build_file = open("build.ninja", "w")
ninja = Writer(build_file, width=120)

generate_stl_options = (
    len(sys.argv) > 1 and sys.argv[1] == "--generate-stl-options-json"
)

if generate_stl_options:
    stl_presets = [
        {
            "key": "high_resolution_raspberry_pi",
            "title": "High Resolution with Raspberry Pi",
            "description": "A microscope using the Raspberry Pi camera and  high resolution optics, as used for medical work.",
            "parameters": {
                "optics": "rms_f50d13",
                "camera": "picamera_2",
                "reflection_illumination": False,
                "motorised": True,
                "base": "bucket",
                "pi_in_base": True,
            },
        },
        {
            "key": "basic_raspberry_pi",
            "title": "Basic with Raspberry Pi",
            "description": "A basic microscope using the Raspberry Pi camera and simple optics. Best suited for low resolution microscopy and educational workshops.",
            "parameters": {
                "optics": "pilens",
                "use_pilens_optics_module": False,
                "camera": "picamera_2",
                "motorised": False,
                "base": "bucket",
                "pi_in_base": True,
            },
        },
        {
            "key": "low_cost_webcam",
            "title": "Low Cost with Webcam",
            "description": "The cheapest possible option using a computer webcam.",
            "parameters": {
                "optics": "c270_lens",
                "camera": "logitech_c270",
                "motorised": False,
                "base": "feet",
            },
        },
    ]

    option_docs = [
        {
            "key": "enable_smart_brim",
            "default": True,
            "description": "Add a smart brim to the main body that helps with bed adhesion but doesn't gunk up the spaces needed for the flexure hinges.",
        },
        {
            "key": "optics",
            "default": "rms_f50d13",
            "description": "The type of lens you'd like to use on your microscope.",
            "options": [
                {
                    "key": "rms_f50d13",
                    "title": "RMS F50D13",
                    "description": "An RMS-threaded microscope objective with 160mm tube length, and a 12.7mm diameter, 50mm focal length achromatic doublet lens.",
                },
                {
                    "key": "rms_infinity_f50d13",
                    "title": "RMS Infinity F50D13",
                    "description": "An RMS-threaded, infinity-corrected microscope objective with a 12.7mm diameter, 50mm focal length achromatic doublet lens.",
                },
                {
                    "key": "pilens",
                    "title": "Pi Lens",
                    "description": "The lens included with the Raspberry Pi camera module, v1 or v2 (either will fit)",
                },
                {
                    "key": "c270_lens",
                    "title": "C270 Lens",
                    "description": "The lens included with the Logitech C270 webcam",
                },
                {
                    "key": "m12_lens",
                    "title": "M12 Lens",
                    "description": "A typical M12 CCTV lens",
                },
                {
                    "key": "rms_f40d16",
                    "title": "RMS F40D16",
                    "description": "An RMS-threaded microscope objective with 160mm tube length, and a 16mm diameter, 40mm focal length lens (no longer recommended due to poor quality at the edges of the image)",
                },
            ],
        },
        {
            "key": "use_pilens_optics_module",
            "default": False,
            "description": "Use the optics module with the Raspberry Pi lens rather than the lens spacer. Using the lens spacer is recommended for most uses.",
        },
        {
            "key": "reflection_illumination",
            "default": False,
            "description": "Enable the microscope modifications required for reflection illumination and fluorescence microscopy.",
        },
        {
            "key": "camera",
            "default": "picamera_2",
            "description": "The type of camera to use with your microscope.",
            "options": [
                {
                    "key": "picamera_2",
                    "title": "Pi Camera",
                    "description": "The Raspberry Pi camera module, version 1 or 2",
                },
                {
                    "key": "logitech_c270",
                    "title": "Logitech C270",
                    "description": "The Logitech C270 webcam",
                },
                {
                    "key": "m12",
                    "title": "M12 Camera",
                    "description": "A M12 CCTV camera",
                },
                {"key": "6led", "title": "6 LED", "description": "USB 6 LED Webcam"},
            ],
        },
        {
            "key": "motorised",
            "default": True,
            "description": "Use unipolar stepper motors and a motor controller PCB to move the stage. The alternative is to use hand-actuated thumbwheels.",
        },
        {
            "key": "use_motor_gears_for_hand_actuation",
            "default": False,
            "description": "Use the normal motor gears instead of the thumbwheels with the hand-actuated version of the microscope.",
        },
        {
            "key": "riser",
            "default": "sample",
            "description": "Type of riser to use on top of the stage. The slide riser is custom made for microscope slides. The sample riser is more versatile and can also hold slides using the set of included sample clips.",
        },
        {
            "key": "base",
            "default": "bucket",
            "description": "Whether to use a bucket base style microscope stand. The alternative is to let it rest on its feet without housing any electronics inside it.",
        },
        {
            "key": "pi_in_base",
            "default": True,
            "description": "Whether you'd like to house a Raspberry Pi in the bucket base.",
        },
        {
            "key": "include_actuator_drilling_jig",
            "description": "This part is very much optional, and is only useful for cleaning up slightly dodgy prints, if the 3mm hole in the actuator has printed too small.",
            "default": False,
        },
    ]

    # additonal constraints on what is required to build a working microscope
    # that are not already expressed through openscad parameters, these are
    # used to disable option combinations that result in essential parts
    # missing
    required_stls = [
        # you need an optics module or a lens spacer
        r"^(optics_|lens_spacer).*\.stl",
        # you need a main microscope body
        r"^main_body_.*\.stl",
        # you need some feet
        r"^feet.*\.stl",
    ]

    # we collect all the select_stl_if parameters and other parameters globally
    all_select_stl_params = set()
    stl_options = []

    # ninja looks at the arguments and would get confused if we didn't remove
    # the `--generate-stl-options-json`
    sys.argv.pop()


ninja.rule(
    "openscad", command="openscad $parameters $in -o $out -d $out.d", depfile="$out.d"
)


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


def openscad(
    output,
    input,
    parameters=None,
    file_local_parameters=None,
    openscad_only_parameters=None,
    select_stl_if=None,
):
    """
    Invokes ninja task generation using the 'openscad' rule. If
    --generate-stl-options-json is enabled it registers the stl and its
    parameters at this point.

    Arguments:
        output {str} -- file path of the output stl file
        input {str} -- file path of the input scad file
        parameters {dict} -- values of globally used parameters
        file_local_parameters {dict} -- values of parameters only used for this specific scad file
        openscad_only_parameters {dict} -- values of parameters only used by openscad, ignored for stl selection
        select_stl_if {dict}|{list} -- values of parameters not used by openscad but relevant to selecting this stl when making a specific variant.
                                       Using a list means or-ing the combinations listed.
    """

    if parameters is None:
        parameters = {}
    if file_local_parameters is None:
        file_local_parameters = {}
    if openscad_only_parameters is None:
        openscad_only_parameters = {}
    if select_stl_if is None:
        select_stl_if = {}

    if generate_stl_options:
        if not isinstance(select_stl_if, list):
            ssif = [select_stl_if]
        else:
            ssif = select_stl_if

        for select in ssif:
            # prefix any file-local parameters with the input file name so they
            # don't overwrite any global parameters
            prefix = os.path.splitext(input)[0] + ":"
            flp_prefixed = {}
            for k, v in file_local_parameters.items():
                flp_prefixed[prefix + k] = v

            global all_select_stl_params
            all_select_stl_params = all_select_stl_params.union(select.keys())
            stl_option_params = {**parameters, **select, **flp_prefixed}
            stl_options.append(
                {"stl": output, "input": input, "parameters": stl_option_params}
            )

    ninja.build(
        os.path.join(build_dir, output),
        rule="openscad",
        inputs=os.path.join("openscad/", input),
        variables={
            "parameters": parameters_to_string(
                {**parameters, **file_local_parameters, **openscad_only_parameters}
            )
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

                output = "main_body_{stage_size}{sample_z}{motors}{beamsplitter}{brim}.stl".format(
                    stage_size=stage_size,
                    sample_z=sample_z,
                    motors="-M" if motors else "",
                    beamsplitter="-BS" if beamsplitter else "",
                    brim="_brim" if brim else "",
                )

                parameters = {
                    **stage_parameters(stage_size, sample_z),
                    "motor_lugs": motors,
                    "enable_smart_brim": brim,
                }
                openscad_only = {"beamsplitter": beamsplitter}
                select_stl_if = {"reflection_illumination": beamsplitter}

                openscad(
                    output,
                    "main_body.scad",
                    parameters,
                    openscad_only_parameters=openscad_only,
                    select_stl_if=select_stl_if,
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
            output = "optics_{camera}_{lens}{beamsplitter}.stl".format(
                camera=camera,
                lens=lens,
                beamsplitter="_beamsplitter" if beamsplitter else "",
            )

            parameters = {"sample_z": sample_z, "optics": lens, "camera": camera}
            openscad_only = {"beamsplitter": beamsplitter}
            select_stl_if = {"reflection_illumination": beamsplitter}

            if lens == "pilens":
                select_stl_if["use_pilens_optics_module"] = True

            if lens not in rms_lenses:
                select_stl_if["riser"] = "no riser"

            openscad(
                output,
                "optics.scad",
                parameters,
                openscad_only_parameters=openscad_only,
                select_stl_if=select_stl_if,
            )


####################
### MICROSCOPE STAND

# Stand with pi
for stand_height in [30]:
    for beamsplitter in [True, False]:
        output = "microscope_stand_{stand_height}{beamsplitter}.stl".format(
            stand_height=stand_height, beamsplitter="-BS" if beamsplitter else ""
        )

        openscad_only = {"beamsplitter": beamsplitter}

        openscad(
            output,
            "microscope_stand.scad",
            openscad_only_parameters=openscad_only,
            file_local_parameters={"h": stand_height},
            select_stl_if={
                "pi_in_base": True,
                "base": "bucket",
                "reflection_illumination": beamsplitter,
            },
        )

# Stand without pi
openscad(
    "microscope_stand_no_pi.stl",
    input="microscope_stand_no_pi.scad",
    parameters={},
    select_stl_if={"pi_in_base": False, "base": "bucket"},
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

    openscad_only_parameters = {"foot_height": foot_height}

    if foot_height == 26:
        select_stl_if = {
            "base": "feet",
            "optics": {"rms_f50d13", "rms_infinity_f50d13", "rms_f40d16"},
        }
    elif foot_height == 15:
        select_stl_if = [
            {
                "base": "bucket",
                "optics": {
                    "c270_lens",
                    "m12_lens",
                    "pilens",
                    "rms_f40d16",
                    "rms_f50d13",
                    "rms_infinity_f50d13",
                },
            },
            {"base": "feet", "optics": {"c270_lens", "m12_lens", "pilens"}},
        ]
    openscad(
        "feet{version}.stl".format(version=version_name),
        "feet.scad",
        openscad_only_parameters=openscad_only_parameters,
        select_stl_if=select_stl_if,
    )
    openscad(
        f"back_foot{version_name}.stl",
        "back_foot.scad",
        openscad_only_parameters=openscad_only_parameters,
        select_stl_if=select_stl_if,
    )


###################
### CAMERA PLATFORM

for stage_size in stage_size_options:
    for sample_z in sample_z_options:
        for version in ["picamera_2", "6led"]:
            output = "camera_platform_{version}_{stage_size}{sample_z}.stl".format(
                version=version, stage_size=stage_size, sample_z=sample_z
            )

            parameters = {
                **stage_parameters(stage_size, sample_z),
                "optics": "pilens",
                "camera": version,
            }

            openscad(output, "camera_platform.scad", parameters)


###############
### LENS SPACER

for stage_size in stage_size_options:
    for sample_z in sample_z_options:
        output = "lens_spacer_picamera_2_pilens_{stage_size}{sample_z}.stl".format(
            stage_size=stage_size, sample_z=sample_z
        )

        parameters = {**stage_parameters(stage_size, sample_z), "optics": "pilens"}

        openscad(
            output,
            "lens_spacer.scad",
            parameters,
            select_stl_if={
                "camera": "picamera_2",
                "reflection_illumination": False,
                "use_pilens_optics_module": False,
            },
        )


##################
### PICAMERA TOOLS

picamera_2_tools = ["cover", "gripper", "lens_gripper"]
for tool in picamera_2_tools:
    output = f"picamera_2_{tool}.stl"
    input = f"cameras/picamera_2_{tool}.scad"

    parameters = {"camera": "picamera_2"}

    openscad(output, input, parameters)


#################
### SAMPLE RISERS

for riser_type in ["sample", "slide"]:
    output = f"{riser_type}_riser_LS10.stl"
    input = f"{riser_type}_riser.scad"

    parameters = {"big_stage": True}

    openscad(
        output,
        input,
        parameters,
        file_local_parameters={"h": 10},
        select_stl_if={"riser": riser_type},
    )


###############
### SMALL PARTS

parts = ["actuator_assembly_tools", "condenser", "illumination_dovetail", "lens_tool"]

for part in parts:
    output = f"{part}.stl"
    input = f"{part}.scad"
    openscad(output, input)

openscad(
    "actuator_drilling_jig.stl",
    "actuator_drilling_jig.scad",
    select_stl_if={"include_actuator_drilling_jig": True},
)

openscad("fl_cube.stl", "fl_cube.scad", select_stl_if={"reflection_illumination": True})

openscad(
    "motor_driver_case.stl",
    "motor_driver_case.scad",
    select_stl_if={"motorised": True, "base": "feet"},
)

openscad("small_gears.stl", "small_gears.scad", select_stl_if={"motorised": True})

openscad(
    "thumbwheels.stl",
    "thumbwheels.scad",
    select_stl_if={"motorised": False, "use_motor_gears_for_hand_actuation": False},
)

openscad(
    "gears.stl",
    "gears.scad",
    select_stl_if=[
        {"motorised": True},
        {"motorised": False, "use_motor_gears_for_hand_actuation": True},
    ],
)

openscad("sample_clips.stl", "sample_clips.scad", select_stl_if={"riser": "sample"})

openscad(
    "reflection_illuminator.stl",
    "reflection_illuminator.scad",
    select_stl_if={"reflection_illumination": True},
)

###############
### RUN BUILD

build_file.close()

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
    for v in stl_options:
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
        # if it's a select_stl_if param then it can have a single value
        elif name in all_select_stl_params:
            if (False in options) or (True in options):
                changeable_options[name] = "bool"
            else:
                changeable_options[name] = options

    # make sure we have some docs for these options
    option_docs_dict = dict([(v["key"], v) for v in option_docs])
    for k in changeable_options:
        if k not in option_docs_dict:
            raise Exception(
                f"No documentation found for '{k}' option, please add it to 'option_docs' in '{__file__}'"
            )
        docs = option_docs_dict[k]
        if "description" not in docs:
            raise Exception(
                f"No description found for '{k}' option, please add it to 'option_docs' in '{__file__}'"
            )
        if "default" not in docs:
            raise Exception(
                f"No default value found for '{k}' option, please add it to 'option_docs' in '{__file__}'"
            )
        if "options" in docs:
            opts = [o["key"] for o in docs["options"]]
            if set(opts) != changeable_options[k]:
                raise Exception(f"Invalid sub-options in option_docs in '{k}'")

            # replace the set with a list so we get the ordering from option_docs
            changeable_options[k] = opts

    stl_options.sort(key=operator.itemgetter("stl"))

    def encode_set(s):
        """ encode 'set' as sorted 'list' when converting to JSON """
        if type(s) is set:
            return sorted(list(s))
        else:
            raise TypeError("Expecting 'set' got {}".format(type(s)))

    # eqivilent to mkdir -p
    pathlib.Path(build_dir).mkdir(parents=True, exist_ok=True)

    p = os.path.join(build_dir, "stl_options.json")
    with open(p, "w") as f:
        json.dump(
            {
                "stls": stl_options,
                "options": changeable_options,
                "docs": option_docs,
                "required": required_stls,
                "presets": stl_presets,
            },
            f,
            indent=2,
            default=encode_set,
        )
    print(f"generated {p}")


run_build()
