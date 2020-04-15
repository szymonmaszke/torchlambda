from .. import implementation


def run(args):
    """Entrypoint for `torchlambda build` subcommand"""
    implementation.docker.check()

    with implementation.general.message("deployment."):
        image = implementation.build.get_image(args)
        if not args.no_run:
            implementation.build.get_package(args, image)
