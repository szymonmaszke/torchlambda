import argparse
import base64
import os
import pathlib
import shlex
import struct
import subprocess
import sys

import numpy as np

import utils


def request(test):
    data = np.random.randint(low=0, high=255, size=test["shape"]).flatten().tolist()
    image = struct.pack("<{}B".format(len(data)), *data)
    encoded_image = base64.b64encode(image)

    event = """'{"batch":%d,"channels":%d,"width":%d,"height":%d,"data":"%s"}' %s""" % (
        *test["shape"],
        encoded_image,
        os.environ["OUTPUT"],
    )

    command = (
        "docker run --rm -v {}:/var/task:ro,delegated"
        "-v {}:/opt/model.ptc:ro,delegated"
        "lambci/lambda:provided"
        "torchlambda {}".format(os.environ["TEST_CODE"], os.environ["MODEL"], event)
    )

    subprocess.call(shlex.split(command))


if __name__ == "__main__":
    args = utils.parse_args()
    test = utils.load_test(args)
    request(test)
