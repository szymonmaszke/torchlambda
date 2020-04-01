import base64
import json
import os
import pathlib
import shlex
import struct
import subprocess
import sys

import numpy as np

import utils


def create_request(test):
    data = np.random.randint(low=0, high=255, size=test["shape"]).flatten().tolist()
    image = struct.pack("<{}B".format(len(data)), *data)
    encoded_image = base64.b64encode(image)

    event = """'{"batch":%d,"channels":%d,"width":%d,"height":%d,"data":"%s"}'""" % (
        *test["shape"],
        encoded_image,
    )

    source_code = pathlib.Path(os.environ["TEST_CODE"]).absolute()
    model = pathlib.Path(os.environ["MODEL"]).absolute()
    command = (
        "docker run --rm -v {}:/var/task:ro,delegated "
        "-v {}:/opt/model.ptc:ro,delegated "
        "lambci/lambda:provided "
        "torchlambda {} {}".format(source_code, model, event, os.environ["OUTPUT"])
    )
    return command


def make_request(command):
    try:
        return json.loads(subprocess.check_output(shlex.split(command)).decode())
    except subprocess.CalledProcessError as e:
        output = e.output.decode()
        print("TEST FAILED DURING MAKING REQUEST! OUTPUT: \n {}".format(output))
        exit(1)


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
    command = create_request(test)
    output = make_request(command)
    validate_response(output, test)
