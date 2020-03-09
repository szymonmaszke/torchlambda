import importlib

from . import arguments


def main():
    args = arguments.parser.get()
    module = importlib.import_module("commands." + args.command)
    module.run(args)


if __name__ == "__main__":
    main()
