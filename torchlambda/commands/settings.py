import pathlib

from .. import utils


def run(args):
    destination = pathlib.Path(args.destination).absolute()
    with utils.general.message("creating YAML settings at {}.".format(destination)):
        utils.general.run(
            "cp -r ./templates/yaml/settings.yaml {}".format(destination),
            operation="copying YAML source code",
            silent=args.silent,
        )
