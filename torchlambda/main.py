import importlib

from . import arguments, subcommands
from ._version import __version__


def main() -> None:
    """Entrypoint run after torchlambda command.

    Responsibilities for functionalities are fully transferred to specific
    subcommand.

    See subcommands module for details.

    """

    args = arguments.parser.get()
    module = importlib.import_module(
        ".subcommands." + args.subcommand, package=__package__
    )
    module.run(args)


if __name__ == "__main__":
    main()
