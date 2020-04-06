import pathlib

from .. import implementation


def run(args):
    """Entrypoint for `torchlambda settings` command"""
    destination = pathlib.Path(args.destination).absolute()
    with implementation.general.message(
        "creating YAML settings at {}.".format(destination)
    ):
        implementation.general.run(
            "cp -r ./templates/yaml/settings.yaml {}".format(destination),
            operation="copying YAML source code",
            silent=args.silent,
        )
