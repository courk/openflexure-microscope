import os
import requests
from argparse import ArgumentParser, Namespace
from zenodo import Zenodo
import yaml


def parse_arguments() -> Namespace:
    p = ArgumentParser(description="Upload data to Zenodo")
    p.add_argument("paths", help="Directories and files to upload to Zenodo", nargs="*")
    p.add_argument(
        "--use-sandbox",
        help="Use sandbox.zenodo.org instead of the real site.",
        action="store_true",
    )
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

    zenodo = Zenodo(args.use_sandbox)
    deposit = zenodo.create_new_deposit()

    zenodo.set_metadata(deposit["id"], metadata)

    for path in args.paths:
        zenodo.upload_file(deposit["id"], path)

    with open("zenodo.url", "w") as f:
        f.write(deposit["links"]["latest_draft_html"])


if __name__ == "__main__":
    main()
