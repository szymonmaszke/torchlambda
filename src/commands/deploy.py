from .. import utils


def run(args):
    utils.docker.check()

    with utils.general.message("deployment."):
        image = utils.deploy.get_image(args)
        utils.deploy.get_package(args, image)
