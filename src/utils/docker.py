import contextlib
import pathlib
import shutil
import sys
import typing
import uuid

from . import general


def check() -> None:
    """Check whether docker is available for usage by torchlambda."""
    if shutil.which("docker") is None:
        print(
            "Docker is required but was not found on $PATH.\n"
            "Please install docker and make it available for torchlambda (see https://docs.docker.com/install/).",
            file=sys.stderr,
        )
        exit(1)


def image_exists(name: str) -> bool:
    """
    Return true if specified image exist locally on host.

    Parameters
    ----------
    name : str
        Name of image to be searched for

    Returns
    -------
    bool
        Whether image exists on localhost

    """
    return not bool(
        general.run(
            "docker inspect --type=image {}".format(name),
            operation="image existence check.",
            silent=True,
            exit_on_failure=False,
        )
    )


def build(args) -> str:
    """
    Build docker image from scratch.

    User can provide various flags to docker and build commands except `-t` which
    is specified by `image` argument and parsed separately.

    Parameters
    ----------
    args : dict-like
        User provided arguments parsed by argparse.ArgumentParser instance.

    Returns
    -------
    str:
        Name of created image
    """

    def _add_build_arg(name: str, values: typing.List[str]) -> str:
        if values is not None:
            return '--build-arg {}="{}" '.format(
                name,
                " ".join(
                    ["-D{}".format(value) for value in values if value is not None]
                ),
            )
        return " "

    def _add_components_to_build(components):
        if components is not None:
            return "BUILD_ONLY='{}'".format(";".join(components))
        return None

    command = "docker {} build {} -t {} ".format(
        *general.parse_none(args.docker, args.build, args.image)
    )
    command += _add_build_arg("PYTORCH", args.pytorch)
    command += _add_build_arg(
        "AWS",
        [_add_components_to_build(args.components)] + args.aws
        if args.aws is not None
        else [],
    )
    command += "."
    general.run(command, operation="custom PyTorch build.", silent=args.silent)

    return args.image


def run(args, image: str) -> str:
    """
    Run docker image and mount user-provided folder with C++ files.

    Parameters
    ----------
    args : dict-like
        User provided arguments parsed by argparse.ArgumentParser instance.
    image : str
        Name of image from which container is run

    Returns
    -------
    str:
        Name of created container. Consist of torchlambda prefix and random string
    """

    def _add_components(components):
        return (
            '"' + ";".join(args.components) + '"'
            if components is not None
            else '"core"'
        )

    def _compilation(args):
        return "" if args.compilation is None else '"' + args.compilation + '"'

    container_name = "torchlambda-" + str(uuid.uuid4())
    source_directory = pathlib.Path(args.source).absolute()
    if source_directory.is_dir():
        command = "docker {} run {} -v {}:/usr/local/user_code --name {} {} {} ".format(
            *general.parse_none(
                args.docker,
                args.run,
                source_directory,
                container_name,
                image,
                _add_components(args.components),
            )
        )

        command += _compilation(args)

        general.run(
            command,
            operation="building inference AWS Lambda package.",
            silent=args.silent,
        )
        return container_name

    print("torchlambda:: Provided source files are not directory, exiting.")
    exit(1)


def cp(args, name: str, source: str, destination: str) -> None:
    general.run(
        "docker container cp {}:{} {}".format(
            name, source, pathlib.Path(destination).absolute()
        ),
        operation="copying {} from docker container {} to {}.".format(
            source, name, destination
        ),
        silent=args.silent,
    )


@contextlib.contextmanager
def rm(args, name: str) -> None:
    try:
        yield
    finally:
        general.run(
            "docker rm {}".format(name),
            operation="removing created docker container named {}.".format(name),
            silent=True,
        )
