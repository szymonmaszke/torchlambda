import pathlib
import zipfile

from .. import implementation


def run(args):
    """Entrypoint for `torchlambda layer` subcommand"""
    destination = pathlib.Path(args.destination).absolute()
    with implementation.general.message(
        "packing Torchscript model to {}.".format(destination)
    ):
        with zipfile.ZipFile(
            destination,
            "w",
            compression=getattr(zipfile, "ZIP_{}".format(args.compression)),
            compresslevel=implementation.layer.compression_level(
                args.compression, args.compression_level
            ),
        ) as file:
            implementation.layer.validate(args)
            file.write(
                pathlib.Path(args.source),
                implementation.layer.path(args)
                if args.directory is not None
                else args.source,
            )
