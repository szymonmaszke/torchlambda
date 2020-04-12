import os
import re

import yaml

import utils


def process(settings):
    pattern = re.compile("Duration: (\d+\.?\d*)")
    with open(os.environ["DATA"], "r") as f:
        init, duration, billed = [float(value) for value in pattern.findall(f.read())]
    settings["init"] = init
    settings["duration"] = duration
    settings["billed"] = billed
    with open(os.environ["SETTINGS"], "w") as file:
        yaml.dump(settings, file, default_flow_style=False)


if __name__ == "__main__":
    process(utils.load_settings())
