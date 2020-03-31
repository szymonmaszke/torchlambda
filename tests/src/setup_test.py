import argparse
import json
import sys
import typing

import yaml

import utils


def imput_arguments(data, test) -> None:
    if "inputs" in test:
        data["inputs"] = test["inputs"]
    if "means" in test:
        data["normalize"]["means"] = test["means"]
    if "stddevs" in test:
        data["normalize"]["stddevs"] = test["stddevs"]
    if "operations" in test:
        data["return"]["result"]["operations"] = test["operations"]
    if "arguments" in test:
        data["return"]["result"]["arguments"] = test["arguments"]
    if "type" in test:
        data["return"]["result"]["type"] = test["type"]
    if "item" in test:
        data["return"]["result"]["item"] = test["item"]


def save_settings(data, args):
    with open(args.output, "w") as file:
        yaml.dump(data, file, default_flow_style=False)


if __name__ == "__main__":
    args = utils.parse_args()
    data = utils.load_settings(args)
    test = utils.load_test(args)
    imput_arguments(data, test)
    save_settings(data, args)
