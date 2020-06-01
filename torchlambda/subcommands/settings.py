import pathlib

from .. import implementation


def run(args):
    """Entrypoint for `torchlambda settings` subcommand"""
    destination = pathlib.Path(args.destination).absolute()
    with implementation.general.message(
        "creating YAML settings at {}.".format(destination)
    ):
        template_path = (
            pathlib.Path(__file__).resolve().parent.parent
            / "templates/settings/torchlambda.yaml"
        )
        implementation.general.run(
            "cp -r {} {}".format(template_path, destination),
            operation="copying YAML source code",
            silent=args.silent,
        )
