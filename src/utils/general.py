import contextlib
import pathlib
import shlex
import shutil
import subprocess
import sys


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
    print("ALTorch:: Started {}".format(operation), file=sys.stderr)
    yield
    print("ALTorch:: Finished {}".format(operation), file=sys.stderr)


def run(command: str, operation: str, exit_on_failure: bool = True) -> int:
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
    with _message(operation):
        return_value = subprocess.call(
            shlex.split(command), cwd=pathlib.Path(__file__).absolute().parent
        )
        if return_value != 0 and exit_on_failure:
            print(
                "ALTorch:: Error: Failed during {}".format(operation), file=sys.stderr,
            )
            exit(1)

        return return_value


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
        shutil.copyfile(
            pathlib.Path(args.operations).absolute(),
            pathlib.Path(__file__).parent.absolute() / "model.yaml",
        )
