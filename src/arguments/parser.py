import argparse

from .subparsers import deploy, scheme


def get():
    """Get user provided arguments."""
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    subparsers = parser.add_subparsers(help="Available options:", dest="command")
    deploy(subparsers)
    scheme(subparsers)

    return parser.parse_args()
