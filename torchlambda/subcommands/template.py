import pathlib

from .. import implementation


def run(args):
    """Entrypoint for `torchlambda template` subcommand"""
    with implementation.general.message(
        "creating C++ scheme at {}.".format(args.destination)
    ):
        if args.yaml is None:
            implementation.general.run(
                "cp -r ./templates/custom {}".format(
                    pathlib.Path(args.destination).absolute()
                ),
                operation="copying CPP sources",
                silent=args.silent,
            )
        else:
            implementation.template.create_template(args)
