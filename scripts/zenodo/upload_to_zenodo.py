import pynodo
import os
from argparse import ArgumentParser, Namespace


def parse_arguments() -> Namespace:
    p = ArgumentParser(description="Upload data to Zenodo")
    p.add_argument("path", help="Directory or file to upload to Zenodo")
    p.add_argument(
        "--use-sandbox",
        help="Use sandbox.zenodo.org instead of the real site.",
        action="store_true",
    )
    return p.parse_args()


def main():
    args = parse_arguments()

    zenodo = pynodo.Depositions(
        access_token=os.environ["ZENODO_API_KEY"], sandbox=args.use_sandbox
    )

    new_depo = zenodo.create()

    ret_depo = zenodo.retrieve(deposition=new_depo.id)

    zen_files = pynodo.DepositionFiles(
        deposition=new_depo.id,
        access_token=os.environ["ZENODO_API_KEY"],
        sandbox=True,
    )

    zen_files.upload(args.path, os.path.basename(args.path))

    print(new_depo, ret_depo, zen_files)


if __name__ == "__main__":
    main()
