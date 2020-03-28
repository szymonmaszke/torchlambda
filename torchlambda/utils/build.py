import pathlib
import shutil
import sys
import uuid

from . import docker, general


def get_image(args) -> str:
    """
    Get torchlambda deployment image.

    If image specified by --image exists locally it's name will be returned.
    Else if image should be build from source it is built and it's name is returned
    as specified by --image.
    Otherwise pre-built torchlambda:latest image will be used.

    Parameters
    ----------
    args : dict-like
        User provided arguments parsed by argparse.ArgumentParser instance.

    Returns
    -------
    str:
        Name of obtained image
    """

    def _custom_build(args):
        """True if any of the flags specified as non-default."""
        flags = (
            "pytorch",
            "aws",
            "operations",
            "aws_components",
            "docker_build",
            "pytorch_version",
        )
        # If any is not None or empty list
        return any(map(lambda flag: getattr(args, flag), flags))

    image_exists: bool = docker.image_exists(args.image)
    if image_exists:
        print(
            "torchlambda:: Image {} was found locally and will be used.".format(
                args.image
            )
        )
        return args.image
    print("torchlambda:: Image {} was not found locally.".format(args.image))
    if _custom_build(args):
        general.copy_operations(args)
        return docker.build(args)

    print("torchlambda:: Default szymonmaszke/torchlambda:latest image will be used.")
    return "szymonmaszke/torchlambda:latest"


def get_package(args, image):
    """Generate deployment package by running provided image.

    Deployment package will be .zip file containing compiled source code
    and statically linked AWS and Libtorch (with optional user-specified flags).

    Parameters
    ----------
    args : dict-like
        User provided arguments parsed by argparse.ArgumentParser instance.
    image : str
        Name of image used to create container.
    """
    container: str = docker.run(args, image)
    with docker.rm(container):
        destination = pathlib.Path(args.destination).absolute()
        if not destination.is_file():
            docker.cp(
                args, container, "/usr/local/build/torchlambda.zip", destination,
            )
        else:
            print(
                "torchlambda:: Error: path {} exists. Please run the script again with the same --image argument.".format(
                    destination
                )
            )
