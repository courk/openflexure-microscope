import json
import os
import operator
import pathlib


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
                        "Expecting 'set' at key '{}', got {}".format(k, type(merged[k]))
                    )

                merged[k] = merged[k].union(v)

            else:
                if k not in merged:
                    merged[k] = set()

                merged[k].add(v)

    return merged


class JsonGenerator:
    def __init__(self, build_dir, option_docs, stl_presets, required_stls):
        self._all_select_stl_params = set()
        self._stl_options = []
        self._build_dir = build_dir
        self._option_docs = option_docs
        self._stl_presets = stl_presets
        self._required_stls = required_stls

    def register(
        self,
        output,
        input,
        parameters,
        file_local_parameters,
        select_stl_if,
    ):
        """
        Register the stl and its parameters for JSON output.

        Arguments:
            self {JsonGenerator}
            output {str} -- file path of the output stl file
            input {str} -- file path of the input scad file
            parameters {dict} -- values of globally used parameters
            file_local_parameters {dict} -- values of parameters only used for this specific scad file
            openscad_only_parameters {dict} -- values of parameters only used by openscad, ignored for stl selection
            select_stl_if {dict}|{list} -- values of parameters not used by openscad but relevant to selecting this stl when making a specific variant.
                                           Using a list means or-ing the combinations listed.
        """

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

            self._all_select_stl_params = self._all_select_stl_params.union(
                select.keys()
            )
            stl_option_params = {**parameters, **select, **flp_prefixed}
            self._stl_options.append(
                {"stl": output, "input": input, "parameters": stl_option_params}
            )

    def write(self):
        # condense all used parameters down to sets of possible values
        available_options = {}
        for v in self._stl_options:
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
            # if it's a select_stl_if param then it can have just a single value
            elif name in self._all_select_stl_params:
                if (False in options) or (True in options):
                    changeable_options[name] = "bool"
                else:
                    changeable_options[name] = options

        # make sure we have some docs for these options
        option_docs_dict = dict([(v["key"], v) for v in self._option_docs])
        for k in changeable_options:
            if k not in option_docs_dict:
                raise Exception(
                    f"No documentation found for '{k}' option, please add it to 'option_docs'"
                )
            docs = option_docs_dict[k]
            if "description" not in docs:
                raise Exception(
                    f"No description found for '{k}' option, please add it to 'option_docs'"
                )
            if "default" not in docs:
                raise Exception(
                    f"No default value found for '{k}' option, please add it to 'option_docs'"
                )
            if "options" in docs:
                # make a list of all documented options
                opts = [o["key"] for o in docs["options"]]

                # make sure it's the same as the set of used options
                if set(opts) != changeable_options[k]:
                    raise Exception(f"Invalid sub-options in option_docs in '{k}'")

                # replace the set with the list so we take on the ordering from option_docs
                changeable_options[k] = opts

        self._stl_options.sort(key=operator.itemgetter("stl"))

        def encode_set(s):
            """ encode 'set' as sorted 'list' when converting to JSON """
            if type(s) is set:
                return sorted(list(s))
            else:
                raise TypeError("Expecting 'set' got {}".format(type(s)))

        # equivalent to mkdir -p, tries to make the folder but doesn't error if it's already there
        pathlib.Path(self._build_dir).mkdir(parents=True, exist_ok=True)

        p = os.path.join(self._build_dir, "stl_options.json")
        with open(p, "w") as f:
            json.dump(
                {
                    "stls": self._stl_options,
                    "options": changeable_options,
                    "docs": self._option_docs,
                    "required": self._required_stls,
                    "presets": self._stl_presets,
                },
                f,
                indent=2,
                default=encode_set,
            )
        print(f"generated {p}")
