import os
import pathlib
import re
import sys

import numpy as np
import yaml

import utils


def load(result):
    with open(result, "r") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as error:
            print("Test error:: Error during {} loading.".format(result))
            print(error)
            sys.exit(1)


def gather():
    # init, duration, billed 3
    # grad [True, False] 2
    # type [] 8
    # size [[256, 256], [256, 512], [512, 256], [512, 512], [64, 64], [128, 64], [64, 128], [128, 128]] 3
    # normalize [True, False]
    # return [output, result, output+result]
    mapping = {
        "grad": {True: 0, False: 1},
        "type": {
            "base64": 0,
            "byte": 1,
            "char": 2,
            "short": 3,
            "int": 4,
            "long": 5,
            "float": 6,
            "double": 7,
        },
        "payload": {
            (256, 256): 0,
            (256, 512): 1,
            (512, 256): 2,
            (512, 512): 3,
            (64, 64): 4,
            (128, 64): 5,
            (64, 128): 6,
            (128, 128): 7,
        },
        "model_name": {
            "shufflenet_v2_x1_0": 0,
            "resnet18": 1,
            "mobilenet_v2": 2,
            "mnasnet1_0": 3,
            "mnasnet1_3": 4,
        }
        # normalize: None, Smth
        # return: output, result, output+result,
        # duration, init, billed
    }

    def index(key: str, result, input_field: bool = False):
        def _return():
            output_exists = "output" in result["return"]
            result_exists = "result" in result["return"]
            if output_exists and result_exists:
                return 0
            if output_exists:
                return 1
            return 2

        def _normalize():
            return 0 if result["normalize"] is None else 1

        if key == "return":
            return _return()
        if key == "normalize":
            return _normalize()

        if input_field:
            return mapping[key][result["input"][key]]
        if key == "payload":
            _, _, width, height = result["payload"]
            return mapping[key][(width, height)]
        return mapping[key][result[key]]

    # + normalize, return, duration
    data = np.zeros([len(value) for value in mapping.values()] + [2, 3, 3])
    occurrences = np.zeros_like(data).astype(int)
    for file in pathlib.Path(os.environ["DATA"]).iterdir():
        result = load(file)
        grad, types, payload, model_name, normalize, output = [
            index("grad", result),
            index("type", result, True),
            index("payload", result),
            index("model_name", result),
            index("normalize", result),
            index("return", result),
        ]
        data[grad, types, payload, model_name, normalize, output, ...] = [
            result["init"],
            result["duration"],
            result["billed"],
        ]
        occurrences[grad, types, payload, model_name, normalize, output, ...] += 1

    np.savez(os.environ["OUTPUT"], data=data, occurrences=occurrences)


if __name__ == "__main__":
    gather()
