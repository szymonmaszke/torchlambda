import pathlib
import shutil
import sys
import uuid

from . import general


def check() -> None:
    """Check whether docker is available for usage by ALTorch."""
    if shutil.which("docker") is None:
        print(
            "Docker is required but was not found on $PATH.\n"
            "Please install docker and make it available for ALTorch (see https://docs.docker.com/install/).",
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
            exit_on_failure=False,
        )
    )


def build(args) -> str:
    """
    Build docker image from scratch.

    User can provide various flags to docker and build commands except `-t` which
    is specified by `docker_image` argument and parsed separately.

    Parameters
    ----------
    args : dict-like
        User provided arguments parsed by argparse.ArgumentParser instance.

    Returns
    -------
    str:
        Name of created image
    """
    general.run(
        "docker {} build -t {} {} .".format(
            args.docker_flags, args.docker_image, args.docker_build_flags
        ),
        operation="custom PyTorch build.",
    )

    return args.docker_image


def run(args, image: str) -> str:
    """
    Run docker image and mount .cpp deployment file.

    [TODO:description]

    Parameters
    ----------
    args : dict-like
        User provided arguments parsed by argparse.ArgumentParser instance.
    image : str
        Name of image from which container is run

    Returns
    -------
    str:
        Name of created container. Consist of altorch prefix and random string
    """
    container_name = "altorch-" + str(uuid.uuid4())
    general.run(
        "docker {} run -v {}:/home/app/main.cpp {} --name {} {}".format(
            args.docker_flags,
            pathlib.Path(args.source).absolute(),
            args.docker_run_flags,
            container_name,
            image,
        ),
        operation="building inference AWS Lambda package.",
    )
    return container_name


def cp(name: str, source: str, destination: str) -> None:
    general.run(
        "docker cp {}:{} {}".format(
            name, pathlib.Path(source).absolute(), pathlib.Path(destination).absolute()
        ),
        operation="Copying deployment .zip to {}.".format(destination),
    )
