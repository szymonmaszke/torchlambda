import argparse


def deploy(subparsers) -> None:
    """Perform deployment of PyTorch C++ code to AWS Lambda."""
    parser = subparsers.add_parser(
        "deploy",
        help="Obtain lambda ready .zip package from C++ deployment source code.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "source", help="Path to inference source code.",
    )

    parser.add_argument(
        "destination",
        help="Path where deployment .zip files will be stored.\nShould be a filename ending with .zip extension",
    )

    parser.add_argument(
        "--compilation_flags",
        required=False,
        help="""Compilation flags used for inference source code.\n"""
        """Should be provided as string, e.g. "-Wall -Werror -O3".\n"""
        "By default none are passed to CMake targets.\nCommand line defaults pass none additional flags as well.",
    )

    parser.add_argument(
        "--operations",
        required=False,
        help="Path containing exported model operations in yaml format.",
    )

    parser.add_argument(
        "--build_flags",
        required=False,
        help="PyTorch build flags customizing dependency build.\n"
        "Default build parameters used for build_mobile script:\n"
        "-DBUILD_PYTHON=OFF\n"
        "-DUSE_MPI=OFF\n"
        "-DUSE_NUMPY=OFF\n"
        "-DUSE_ROCM=OFF\n"
        "-DUSE_NCCL=OFF\n"
        "-DUSE_NUMA=OFF\n"
        "-DUSE_MKLDNN=OFF\n"
        "-DUSE_GLOO=OFF\n"
        "-DUSE_OPENMP=OFF\n"
        """User can override those default by providing string, e.g. "-DUSE_NCCL=ON -DUSE_MKLDNN=ON".\n"""
        "By default additional command line options: None",
    )

    parser.add_argument(
        "--docker_image",
        required=False,
        default="altorch:custom",
        help="Name of image if custom build used (either --operations or --build provided or both).\n"
        "If provided name image exists it will be used for `docker run` command.\n"
        "Default: altorch:custom",
    )

    parser.add_argument(
        "--docker_flags",
        required=False,
        help="Flags passed to docker command during build and/or run.\n"
        """Flags should be passed as string, e.g. "--debug --log-level debug".\nDefault: None""",
    )

    parser.add_argument(
        "--docker_build_flags",
        required=False,
        help="Flags passed to docker build command (custom image building).\n"
        """Flags should be passed as string, e.g. "--compress --no-cache".\n"""
        "`-t` flag SHOULD NOT BE USED, specify --docker_image instead\nDefault: None",
    )

    parser.add_argument(
        "--docker_run_flags",
        required=False,
        help="Flags passed to docker run command (deployment building).\n"
        """Flags should be passed as string, e.g. "--name deployment --mount source=myvol2,target=/home/app".\nDefault: None""",
    )


def scheme(subparsers) -> None:
    """Create scheme C++ source for model inference."""
    parser = subparsers.add_parser(
        "scheme",
        help="Create C++ deployment code scheme with AWS Lambda C++ runtime and PyTorch",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--base64",
        required=False,
        action="store_true",
        help="Create C++ code scheme utilizing base64 encoded input.",
    )
