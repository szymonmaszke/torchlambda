from .. import utils


def run(args):
    utils.docker.check()

    with utils.general.message("deployment."):
        image = utils.build.get_image(args)
        utils.build.get_package(args, image)
