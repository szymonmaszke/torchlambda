import argparse

from .subparsers import build, layer, settings, template


def get():
    """Get user provided arguments."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="Lightweight tool to deploy PyTorch models on AWS Lambda.\n"
        "For more information see documentation: https://github.com/szymonmaszke/torchlambda/wiki",
    )

    parser.add_argument(
        "--silent",
        required=False,
        action="store_true",
        help="Will only output torchlambda information (e.g. building PyTorch output won't be displayed).\n"
        "Default: False",
    )

    subparsers = parser.add_subparsers(help="Subcommands:", dest="subcommand")
    settings(subparsers)
    template(subparsers)
    build(subparsers)
    layer(subparsers)

    return parser.parse_args()
