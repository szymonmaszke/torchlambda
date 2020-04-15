import pathlib

from .. import implementation


def run(args):
    """Entrypoint for `torchlambda settings` subcommand"""
    destination = pathlib.Path(args.destination).absolute()
    with implementation.general.message(
        "creating YAML settings at {}.".format(destination)
    ):
        implementation.general.run(
            "cp -r ./templates/settings/torchlambda.yaml {}".format(destination),
            operation="copying YAML source code",
            silent=args.silent,
        )
