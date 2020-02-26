import pathlib
import shutil
import sys
import uuid

from . import docker, utils


def get_image(args) -> str:
    """
    Get ALTorch deployment image.

    If image specified by --docker_image exists locally it's name will be returned.
    Else if image should be build from source it is built and it's name is returned
    as specified by --docker_image.
    Otherwise pre-built ALTorch:latest image will be used.

    Parameters
    ----------
    args : dict-like
        User provided arguments parsed by argparse.ArgumentParser instance.

    Returns
    -------
    str:
        Name of obtained image
    """
    image_exists: bool = docker.image_exists(args.docker_image)
    if image_exists:
        image: str = args.docker_image
    elif args.build is not None or args.operations is not None:
        utils.copy_operations(args)
        image: str = docker.build(args)
    else:
        image: str = "szymonmaszke/altorch:latest"

    return image


def get_package(args, image):
    """
    Generate deployment package by running provided image.

    Deployment package will be .zip file containing compiled source code
    and statically linked possibly minimalistic PyTorch.

    Parameters
    ----------
    args : dict-like
        User provided arguments parsed by argparse.ArgumentParser instance.
    image : str
        Name of image used to create container.
    """
    container: str = docker.run(args, image)
    docker.copy(
        container,
        "/home/app/build/altorch.zip",
        pathlib.Path(args.destination).absolute(),
    )
