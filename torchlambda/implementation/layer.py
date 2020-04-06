import pathlib
import typing


def validate(args) -> None:
    """
    Validate torchscript model is a file. Exit with 1 otherwise

    Parameters
    ----------
    args : dict-like
        User provided arguments parsed by argparse.ArgumentParser instance.

    """
    source = pathlib.Path(args.source)
    if not source.is_file:
        print("torchlambda:: Error: provided path to torchscript model is not a file!")
        exit(1)


def path(args) -> pathlib.Path:
    """
    Return path where model will be placed upon `.zip` unpacking.

    Parameters
    ----------
    args : dict-like
        User provided arguments parsed by argparse.ArgumentParser instance.

    Returns
    -------
    pathlib.Path

    """
    if args.directory is not None:
        return pathlib.Path(args.directory) / args.source
    return pathlib.Path(args.source)


def compression_level(compression, level):
    """
    Validate compression and compression's level user arguments.

    This function return appropriate compression level for any `zipfile.Zipfile`
    supported values.

    Check: https://docs.python.org/3/library/zipfile.html#zipfile-objects
    to see possible values for each type.

    Parameters
    ----------
    args : dict-like
        User provided arguments parsed by argparse.ArgumentParser instance.

    Returns
    -------
    pathlib.Path

    """

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
