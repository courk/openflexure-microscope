import os
import requests
from argparse import ArgumentParser, Namespace
from zenodo import Zenodo
import yaml

# you have to explicitely set ZENODO_USE_SANDBOX=false to not use the
# sandbox, any other value or unset variable means this script will use
# the sandbox zenodo site
if "ZENODO_USE_SANDBOX" in os.environ:
    USE_SANDBOX = not os.environ["ZENODO_USE_SANDBOX"] == "false"
else:
    USE_SANDBOX = True


if USE_SANDBOX:
    API_KEY = os.environ["ZENODO_API_KEY_SANDBOX"]
else:
    API_KEY = os.environ["ZENODO_API_KEY_REAL"]


def parse_arguments() -> Namespace:
    p = ArgumentParser(description="Upload data to Zenodo")
    p.add_argument("paths", help="Directories and files to upload to Zenodo", nargs="*")
    return p.parse_args()


def script_directory(path):
    """resolves path to directory of the current script"""
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def get_meta():
    with open(script_directory("metadata.yaml")) as f:
        metadata = f.read()

    return yaml.safe_load(metadata)


def main():
    args = parse_arguments()

    metadata = get_meta()

    zenodo = Zenodo(API_KEY, USE_SANDBOX)
    deposit = zenodo.create_new_deposit()

    zenodo.set_metadata(deposit["id"], metadata)

    for path in args.paths:
        zenodo.upload_file(deposit["id"], path)

    with open("zenodo.url", "w") as f:
        f.write(deposit["links"]["latest_draft_html"])


if __name__ == "__main__":
    main()
