import contextlib
import pathlib
import shlex
import shutil
import subprocess
import sys
import typing


def parse_none(*args):
    """Return tuple of arguments excluding the ones being None."""
    return tuple(arg if arg is not None else "" for arg in args)


@contextlib.contextmanager
def message(operation: str):
    """
    Verbose logging of operation to be performed.

    Used only by `utils.run_command`

    Parameters
    ----------
    operation : str
        String describing operation to be run.

    """
    print("torchlambda:: Started {}".format(operation), file=sys.stderr)
    yield
    print("torchlambda:: Finished {}".format(operation), file=sys.stderr)


def run(
    command: str,
    operation: str,
    silent: bool,
    exit_on_failure: bool = True,
    no_stdout: bool = False,
    no_stderr: bool = False,
) -> int:
    """
    Run specific cli command, parse and return it's results.

    Parameters
    ----------
    command : str
        CLI Linux command to be run.
    operation : str
        Name of operation for verbose logging of output.
    exit_on_failure : bool, optional
        Whether program should exit with error if the command didn't return 0.
        Default: `True`

    Returns
    -------
    int
        Value returned by command

    """

    def _set_streams() -> typing.Dict:
        kwargs = {}
        if no_stdout or silent:
            kwargs["stdout"] = subprocess.DEVNULL
        if no_stderr or silent:
            kwargs["stderr"] = subprocess.DEVNULL
        return kwargs

    with message(operation):
        return_value = subprocess.call(
            shlex.split(command),
            cwd=pathlib.Path(__file__).absolute().parent.parent,
            **_set_streams()
        )
        if return_value != 0 and exit_on_failure:
            print(
                "torchlambda:: Error: Failed during {}".format(operation),
                file=sys.stderr,
            )
            exit(1)

        return return_value


@message("copying provided model operations.")
def copy_operations(args) -> None:
    """
    Copy custom operations.yaml of PyTorch model if provided by user.

    Providing custom operations.yaml will trigger docker image build from scratch.

    Parameters
    ----------
    args : dict-like
        User provided arguments parsed by argparse.ArgumentParser instance.

    """
    if args.operations is not None:
        operations_path = pathlib.Path(args.operations).absolute()
        if operations_path.is_file():
            print("torchlambda:: Copying custom model operations...")
            shutil.copyfile(
                pathlib.Path(args.operations).absolute(),
                pathlib.Path(__file__).absolute().parent.parent / "model.yaml",
            )
        else:
            print("torchlambda:: Error, provided operations are not a file!")
            exit(1)
