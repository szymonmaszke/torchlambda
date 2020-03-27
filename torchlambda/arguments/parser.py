import argparse

from .subparsers import build, layer, settings, template


def get():
    """Get user provided arguments."""
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        "--silent",
        required=False,
        action="store_true",
        help="Will only output most basic information (e.g. info from build won't be displayed).\n"
        "Default: False",
    )

    subparsers = parser.add_subparsers(help="Available options:", dest="command")
    settings(subparsers)
    template(subparsers)
    build(subparsers)
    layer(subparsers)

    return parser.parse_args()
