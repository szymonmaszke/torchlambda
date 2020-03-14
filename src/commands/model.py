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

            file.write(source, "{}/{}".format(args.directory, source.name))
