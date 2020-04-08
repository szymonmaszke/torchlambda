import base64
import contextlib
import json
import os
import pathlib
import shlex
import struct
import subprocess
import sys
import time

import numpy as np

import utils


@contextlib.contextmanager
def clean(container: str) -> None:
    try:
        yield
    finally:
        # It will be auto-deleted after stopping due to --rm
        subprocess.check_output(
            shlex.split("docker container stop {}".format(container))
        ).decode()


def create_server() -> None:
    print("Test: Creating Lambda container...")
    source_code = pathlib.Path(os.environ["TEST_CODE"]).absolute()
    model = pathlib.Path(os.environ["MODEL"]).absolute()
    command = (
        "docker run --rm -d "
        "-e DOCKER_LAMBDA_STAY_OPEN=1 "
        "-p 9001:9001 "
        "-v {}:/var/task:ro,delegated "
        "-v {}:/opt/model.ptc:ro,delegated "
        "lambci/lambda:provided "
        "torchlambda".format(source_code, model)
    )

    container_id = subprocess.check_output(shlex.split(command)).decode()
    print("Container ID: {}".format(container_id))
    return container_id


def make_request(test):
    type_mapping = {
        "byte": np.uint8,
        "char": np.int8,
        "short": np.int16,
        "int": np.int32,
        "long": np.int64,
        "float": np.float32,
        "double": np.float64,
    }

    data = np.random.randint(low=0, high=255, size=test["request_shape"]).flatten()
    if test["input_type"].lower() == "base64":
        data = base64.b64encode(
            struct.pack("<{}B".format(len(data)), *(data.tolist()))
        ).decode()
    else:
        data = data.astype(type_mapping[test["input_type"]]).tolist()

    batch, channels, width, height = test["request_shape"]
    request = {
        "batch": batch,
        "channels": channels,
        "width": width,
        "height": height,
        "data": data,
    }

    event_file = os.environ["EVENT_FILE"]
    with open(event_file, "w") as file:
        json.dump(request, file)

    command = (
        "aws lambda invoke "
        "--endpoint http://localhost:9001 "
        "--no-sign-request "
        "--function-name torchlambda "
        "--payload file://{} {}".format(event_file, os.environ["OUTPUT_FILE"])
    )

    try:
        subprocess.call(shlex.split(command))
    except subprocess.CalledProcessError as e:
        print("TEST FAILED DURING MAKING REQUEST! Error: \n {}".format(e))
        sys.exit(1)

    try:
        with open(os.environ["OUTPUT_FILE"], "r") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print("TEST FAILED DURING OUTPUT_FILE LOADING! Error: \n {}".format(e))
        sys.exit(1)


def validate_response(output, test):
    def _validate_test_case():
        required_types = test["required_types"]
        required = test["required"]
        assert isinstance(required, list), "TEST FAILED: required has to be list!"
        assert isinstance(
            required_types, list
        ), "TEST FAILED: required_types has to be list!"
        assert isinstance(
            required[0], str
        ), "TEST FAILED: required values has to be string!"
        assert isinstance(
            required_types[0], str
        ), "TEST FAILED: required_types values has to be string!"
        assert len(required) == len(
            required_types
        ), "TEST FAILED: required and required_types has to be the same length!"
        return required, required_types

    def _validate_type(name, value, required_type_name):
        mapping = {
            "int": int,
            "float": float,
            "list_int": (list, int),
            "list_float": (list, float),
        }
        required_type = mapping[required_type_name]
        if isinstance(required_type, tuple):
            container_type, item_type = required_type
            assert isinstance(
                value, container_type
            ), "TEST FAILED: {} is not a container type!".format(name)
            assert isinstance(
                value[0], item_type
            ), "TEST_FAILED: {}'s item is not of type {}".format(
                name, required_type_name
            )
        else:
            assert isinstance(
                value, required_type
            ), "TEST_FAILED: {} is not of type {}".format(name, required_type_name)

    required, required_types = _validate_test_case()

    for required_key, required_type_name in zip(required, required_types):
        if required_key not in output:
            print(
                "TEST FAILED! Required key {} not found in response!".format(
                    required_key
                )
            )
        _validate_type(required_key, output[required_key], required_type_name)


if __name__ == "__main__":
    args = utils.parse_args()
    test = utils.load_test(args)
    container = create_server()
    with clean(container):
        output = make_request(test)
        validate_response(output, test)
