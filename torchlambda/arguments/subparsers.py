import argparse


def settings(subparsers) -> None:
    """Create YAML settings to use with `torchlambda template --yaml`."""

    description = "Create YAML settings to use with `torchlambda template --yaml`\n"
    "This is the easiest way to deploy model, just modify default settings provided by this comand.\n"
    "Not all provided fields are required, please see: https://github.com/szymonmaszke/torchlambda/wiki/Commands for more information."

    parser = subparsers.add_parser(
        "settings",
        description=description,
        help=description,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--destination",
        required=False,
        default="./torchlambda.yaml",
        help="""Path to file where YAML settings will be stored. Default: "./torchlambda.yaml" """,
    )


def template(subparsers) -> None:
    """Create C++ source code template used for model inference."""

    description = (
        "Create C++ deployment code scheme with AWS Lambda C++ SDK and PyTorch.\n"
        "In general users are advised to stick to YAML settings (--yaml) flag.\n"
        "Not all YAML fields are required, please see: https://github.com/szymonmaszke/torchlambda/wiki/Commands for more information.\n"
        "If --yaml unspecified, generate C++ code which one can use as a starting point for custom use cases."
    )

    parser = subparsers.add_parser(
        "template",
        description=description,
        help=description,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--yaml",
        required=False,
        default=None,
        help="Path to YAML settings file from which code will be generated.\n"
        "See torchlambda settings and comments in generated YAML for more info.",
    )

    parser.add_argument(
        "--destination",
        required=False,
        default="./torchlambda",
        help="""Path to folder where C++ deployment files will be created. Default: "./torchlambda" """,
    )


def build(subparsers) -> None:
    """Perform deployment of PyTorch C++ code to AWS Lambda."""
    description = "Obtain AWS Lambda ready .zip package from C++ deployment source code and Torchscript compiled model.\n"
    "See following resources for more information:\n"
    "- Torchscript documentation: https://pytorch.org/docs/stable/jit.html\n"
    "- AWS Lambda Getting Started: https://aws.amazon.com/lambda/getting-started/\n"
    "- AWS SDK for C++: https://aws.amazon.com/sdk-for-cpp/"
    parser = subparsers.add_parser(
        "build",
        formatter_class=argparse.RawTextHelpFormatter,
        description=description,
        help=description,
    )

    parser.add_argument(
        "source",
        help="Directory containing source files (possibly multiple) with C++ deployment code.\n"
        "cmake will build all files in this folder matching *.cpp, *.c, *.h or *.hpp extensions.\n"
        "If you are unsure how to create one, please use torchlambda scheme command.",
    )

    parser.add_argument(
        "--destination",
        default="./torchlambda.zip",
        required=False,
        help="Path where created AWS Lambda deployment .zip package will be stored.\n"
        "Should be a filename ending with .zip extension",
    )

    parser.add_argument(
        "--compilation",
        required=False,
        help="""Compilation flags used for inference source code.\n"""
        """Should be provided as string, e.g. "-Wall -Werror -O3".\n"""
        "By default no flags are passed to CMake targets.\n"
        'If you want to pass a single flag you should add space after string, e.g. "-Wall "\n'
        "Command line defaults pass none additional flags as well.\n"
        "User might want to specify -Os for smaller size or -O2 for possibly increased performance.\n"
        "IMPORTANT: Due to linker flags smaller binary size may not be possible at the moment.",
    )

    parser.add_argument(
        "--operations",
        required=False,
        help="Path containing exported model operations in .yaml format.\n"
        "See: https://pytorch.org/mobile/ios/#custom-build for more information.\n"
        "If specified, custom image will be build from scratch.\n"
        "Default: None (no operations)",
    )

    parser.add_argument(
        "--pytorch",
        nargs="+",
        required=False,
        default=[],
        help="PyTorch's libtorch build flags.\n"
        "See PyTorch's CMakeLists.txt for all available flags: https://github.com/pytorch/pytorch/blob/master/CMakeLists.txt\n"
        "If specified, custom image will be build from scratch.\n"
        "Default build parameters used:\n"
        "-DBUILD_PYTHON=OFF\n"
        "-DUSE_MPI=OFF\n"
        "-DUSE_NUMPY=OFF\n"
        "-DUSE_ROCM=OFF\n"
        "-DUSE_NCCL=OFF\n"
        "-DUSE_NUMA=OFF\n"
        "-DUSE_MKLDNN=OFF\n"
        "-DUSE_GLOO=OFF\n"
        "-DUSE_OPENMP=OFF\n"
        "User can override defaults by providing multiple arguments WITHOUT -D, e.g. \n"
        "--pytorch USE_NUMPY=ON USE_OPENMP=ON\n"
        "Default additional command line options: None",
    )

    parser.add_argument(
        "--pytorch-version",
        required=False,
        default=None,
        help="Commit or tag to which PyTorch will be set during build.\n"
        "See available releases at: https://github.com/pytorch/pytorch/releases (but any commit can be used)\n"
        'Special value "None" allowed which leaves PyTorch at current head on master.\n'
        "If specified, custom image will be build from scratch.\n"
        "Default: latest ",
    )

    parser.add_argument(
        "--aws",
        nargs="+",
        required=False,
        default=[],
        help="AWS C++ SDK build flags customizing dependency build.\n"
        "See: https://docs.aws.amazon.com/sdk-for-cpp/v1/developer-guide/cmake-params.html#cmake-build-only for more information.\n"
        "If specified, custom image will be built from scratch.\n"
        "Default build parameters used:\n"
        "-DBUILD_SHARED_LIBS=OFF (cannot be overriden)\n"
        "-DENABLE_UNITY_BUILD=ON (usually shouldn't be overriden)\n"
        "-DCUSTOM_MEMORY_MANAGEMENT=OFF\n"
        "-DCPP_STANDARD=17\n"
        "User can override defaults by providing multiple arguments WITHOUT -D, e.g. \n"
        "--aws CPP_STANDARD=11 CUSTOM_MEMORY_MANAGEMENT=ON\n"
        "`-DBUILD_ONLY` flag SHOULD NOT BE USED HERE, specify --aws-components instead\n"
        "Default additional command line options: None",
    )

    parser.add_argument(
        "--aws-components",
        nargs="+",
        default=[],
        required=False,
        help="Components of AWS C++ SDK to build.\n"
        "If specified, custom image will be built from scratch.\n"
        "Acts as `-DBUILD_ONLY` during build, please see https://docs.aws.amazon.com/sdk-for-cpp/v1/developer-guide/cmake-params.html#cmake-build-only.\n"
        "Pass components as space separated arguments, e.g.\n"
        "--aws-components s3 dynamodb\n"
        "By default only core will be build."
        "Default additional command line options: None",
    )

    parser.add_argument(
        "--image",
        required=False,
        default="torchlambda:custom",
        help="Name of Docker image to use for code building.\n"
        "If provided name image exists on localhost it will be used for `docker run` command.\n"
        "Otherwise AND IF custom build specified (either of --operations, --pytorch, --aws, --components or --build) image will be build from scratch.\n"
        "Otherwise prebuilt image szymonmaszke/torchlambda:latest will be downloaded and used.\n"
        "Default: torchlambda:custom",
    )

    parser.add_argument(
        "--docker",
        required=False,
        help='Flags passed to "docker" command during build and run.\n'
        'If you want to pass a single flag you should add space after string, e.g. "--debug "\n'
        """Flags should be passed as space separated string, e.g. "--debug --log-level debug".\nDefault: None""",
    )

    parser.add_argument(
        "--docker-build",
        required=False,
        help="Flags passed to docker build command (custom image building).\n"
        """Flags should be passed as space separated string, e.g. "--compress --no-cache".\n"""
        'If you want to pass a single flag you should add space after string, e.g. "--compress "\n'
        "`-t` flag SHOULD NOT BE USED, specify --image instead.\n"
        "Default: None",
    )

    parser.add_argument(
        "--docker-run",
        required=False,
        help="Flags passed to docker run command (code deployment building).\n"
        "Flags should be passed as space separated string, e.g.\n"
        """--name deployment --mount source=myvol2,target=/home/app".\n"""
        'If you want to pass a single flag you should add space after string, e.g. "--name my_name"\n'
        "Default: None",
    )

    parser.add_argument(
        "--no-run",
        required=False,
        action="store_true",
        help="Do not run compilation of source code part.\n"
        "Can be used to only create Docker building image to be run later."
        "Default: False",
    )


def layer(subparsers) -> None:
    """Pack model as .zip file ready to deploy on AWS Lambda as layer."""
    description = "Pack model as .zip file ready to deploy on AWS Lambda as layer."
    parser = subparsers.add_parser(
        "layer",
        description=description,
        help=description,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "source",
        help="Path pointing to TorchScript compiled model.\n"
        "For more information check introduction to TorchScript:\n"
        "https://pytorch.org/tutorials/beginner/Intro_to_TorchScript_tutorial.html.",
    )

    parser.add_argument(
        "--destination",
        required=False,
        default="./model.zip",
        help="Path where AWS Lambda layer containing model will be stored.\n"
        """Default: "./model.zip" """,
    )

    parser.add_argument(
        "--directory",
        required=False,
        default=None,
        help="Directory where model will be stored. Usually you don't want to change that.\n"
        "Model will be unpacked to /opt/your/specified/directory and needs to be set analogously in C++/YAML settings.\n"
        "Default: None (model will be placed in /opt)",
    )

    parser.add_argument(
        "--compression",
        required=False,
        default="STORED",
        choices=["STORED", "DEFLATED", "BZIP2", "LZMA"],
        type=str.upper,
        help="""Compression method used for model compression.\n"""
        "See: https://docs.python.org/3/library/zipfile.html#zipfile.ZIP_STORED for more information.\n"
        "IMPORTANT: It's best to use default (uncompressed archive stored in.zip).\n"
        "Model .ptc file will barely be compressed by any algorithm, while it may increase decompression speed on AWS Lambda.\n"
        "If you wish to compress your model please use quantization (https://pytorch.org/docs/stable/quantization.html) or related techniques instead.\n"
        """Default: "STORED" """,
    )

    parser.add_argument(
        "--compression-level",
        required=False,
        default=None,
        choices=list(range(10)),
        type=int,
        help="""Level of compression used.\n"""
        "See: https://docs.python.org/3/library/zipfile.html#zipfile-objects for more information.\n"
        """Default: None (default for specified --compression) """,
    )
