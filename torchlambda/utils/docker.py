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

    def _cmake_environment_variables(name: str, values: typing.List[str]) -> str:
        return (
            '--build-arg {}="{}" '.format(
                name, " ".join(["-D{}".format(value) for value in values]),
            )
            if values
            else " "
        )

    def _create_aws_components(components):
        return ["BUILD_ONLY='{}'".format(";".join(components))] if components else []

    def _pytorch_version(version: str):
        return (
            '--build-arg PYTORCH_VERSION="{}" '.format(version)
            if version is not None
            else " "
        )

    command = "docker {} build {} -t {} ".format(
        *general.parse_none(args.docker, args.docker_build, args.image)
    )
    command += _cmake_environment_variables("PYTORCH", args.pytorch)
    command += _pytorch_version(args.pytorch_version)
    command += _cmake_environment_variables(
        "AWS", _create_aws_components(args.aws_components) + args.aws
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

    def _add_components(args):
        return (
            '"' + ";".join(args.aws_components) + '"'
            if args.aws_components
            else '"core"'
        )

    def _compilation(args):
        return '"' + args.compilation + '"' if args.compilation else ""

    container_name = "torchlambda-" + str(uuid.uuid4())
    source_directory = pathlib.Path(args.source).absolute()
    if source_directory.is_dir():
        command = "docker {} run {} -v {}:/usr/local/user_code --name {} {} {} ".format(
            *general.parse_none(
                args.docker,
                args.docker_run,
                source_directory,
                container_name,
                image,
                _add_components(args),
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
    """
    Copy source to destination from named container.

    Will verbosely copy file from container, yet no output of `docker` command
    will be displayed.

    Will crash the program if anything goes wrong.

    Parameters
    ----------
    args : dict-like
        User provided arguments parsed by argparse.ArgumentParser instance.
    args : dict-like
        User provided arguments
    name : str
        Name of container
    source : str
        Path to source to be copied
    destination : str
        Destination where source will be copied

    """
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
def rm(name: str) -> None:
    """
    Remove container specified by name

    Container to be removed after deployment was copied from it to localhost.

    Parameters
    ----------
    name : str
        Name of the container to be removed

    """
    try:
        yield
    finally:
        general.run(
            "docker rm {}".format(name),
            operation="removing created docker container named {}.".format(name),
            silent=True,
        )
