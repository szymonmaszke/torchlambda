import importlib

from . import arguments, commands
from ._version import __version__


def main():
    args = arguments.parser.get()
    module = importlib.import_module(".commands." + args.command, package=__package__)
    module.run(args)


if __name__ == "__main__":
    main()
