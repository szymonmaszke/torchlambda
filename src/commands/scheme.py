import pathlib

from .. import utils


def run(args):
    destination = pathlib.Path(args.destination).absolute()
    with utils.general.message("creating C++ scheme at {}.".format(destination)):
        utils.general.run(
            "cp -r ./templates {}".format(destination),
            operation="copying main.cpp and utils.h",
            silent=args.silent,
        )
