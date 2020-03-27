import pathlib
import typing


def validate(args) -> None:
    source = pathlib.Path(args.source)
    if not source.is_file:
        print("torchlambda:: Error: provided path to torchscript model is not a file!")
        exit(1)


def path(args) -> pathlib.Path:
    if args.directory is not None:
        return pathlib.Path(args.directory) / args.source
    return pathlib.Path(args.source)


def compression_level(compression, level):
    def _wrong_parameters(minimum, maximum):
        print(
            "--level should be in range [{}, {}] for compression type {}".format(
                minimum, maximum, level
            )
        )
        exit(1)

    if compression == "DEFLATED":
        if not 0 <= level <= 9:
            _wrong_parameters(0, 9)
        return level
    if compression == "BZIP2":
        if not 1 <= level <= 9:
            _wrong_parameters(1, 9)
        return level

    return level
