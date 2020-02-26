from . import docker, utils


def run(args):
    docker.check()

    with utils.general.message("deployment."):
        image = utils.deploy.get_image(args)
        utils.deploy.get_package(image, args)
