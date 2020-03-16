import pathlib
import zipfile

from .. import utils


def run(args):
    destination = pathlib.Path(args.destination).absolute()
    with utils.general.message("packing Torchscript model to {}.".format(destination)):
        with zipfile.ZipFile(
            args.destination,
            "w",
            compression=getattr(zipfile, "ZIP_{}".format(args.compression)),
            compresslevel=utils.model.compression_level(args.compression, args.level),
        ) as file:
            source = pathlib.Path(args.source)
            if not source.is_file:
                print(
                    "torchlambda:: Error: provided path to torchscript model is not a file!"
                )
                exit(1)

            if args.directory is not None:
                pathlib.Path(args.directory)
            file.write(
                source,
                pathlib.Path(args.directory) / args.source
                if args.directory is not None
                else args.source,
            )
