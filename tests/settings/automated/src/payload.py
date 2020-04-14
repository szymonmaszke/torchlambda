import base64
import json
import os
import pathlib
import random
import struct
import typing

import numpy as np
import yaml

import utils


def create_payload(data, batch, channels, width, height) -> pathlib.Path:
    request = {
        "batch": batch,
        "channels": channels,
        "width": width,
        "height": height,
        "data": data,
    }

    payload_file = pathlib.Path(os.environ["OUTPUT"]).absolute()
    with open(payload_file, "w") as file:
        json.dump(request, file)
    return payload_file


def create_data(
    settings,
    type_mapping: typing.Dict = {
        "byte": np.uint8,
        "char": np.int8,
        "short": np.int16,
        "int": np.int32,
        "long": np.int64,
        "float": np.float32,
        "double": np.float64,
    },
):
    def _get_shape(settings):
        return [1, 3] + random.choice(
            [[128, 128], [256, 256], [512, 512], [1024, 1024]]
        )

    batch, channels, width, height = _get_shape(settings)
    settings["payload"] = [batch, channels, width, height]
    print(
        "Test:: Request shape: [{}, {}, {}, {}]".format(batch, channels, width, height)
    )
    data = np.random.randint(
        low=0, high=255, size=(batch, channels, width, height)
    ).flatten()
    if settings["input"]["type"] == "base64":
        data = base64.b64encode(
            struct.pack("<{}B".format(len(data)), *(data.tolist()))
        ).decode()
    else:
        data = data.astype(type_mapping[settings["input"]["type"]]).tolist()
    with open(os.environ["SETTINGS"], "w") as file:
        yaml.dump(settings, file, default_flow_style=False)
    return data, (batch, channels, width, height)


if __name__ == "__main__":
    print("Test:: Creating payload")
    settings = utils.load_settings()
    data, (batch, channels, width, height) = create_data(settings)
    create_payload(data, batch, channels, width, height)
