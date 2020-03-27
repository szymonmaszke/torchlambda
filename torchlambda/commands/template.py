import pathlib

from .. import utils


def run(args):
    with utils.general.message("creating C++ scheme at {}.".format(args.destination)):
        if args.yaml is None:
            utils.general.run(
                "cp -r ./templates/cpp {}".format(
                    pathlib.Path(args.destination).absolute()
                ),
                operation="copying CPP sources",
                silent=args.silent,
            )
        else:
            utils.template.create_template(args)
