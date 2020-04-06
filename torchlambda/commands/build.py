from .. import utils


def run(args):
    """Entrypoint for `torchlambda build` command"""
    utils.docker.check()

    with utils.general.message("deployment."):
        image = utils.build.get_image(args)
        if not args.no_run:
            utils.build.get_package(args, image)
