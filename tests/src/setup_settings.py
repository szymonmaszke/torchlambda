import argparse
import json
import sys
import typing

import yaml


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("file", help="Settings file to modify")
    parser.add_argument("test", help="Specific JSON test settings used")
    parser.add_argument("output", help="Specific JSON test settings used")

    return parser.parse_args()


def load_settings(args) -> typing.Dict:
    with open(args.file, "r") as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as error:
            print("Test error:: Error during user settings loading.")
            print(error)
            sys.exit(1)


def load_test(args) -> typing.Dict:
    with open(args.test, "r") as file:
        try:
            return json.load(file)
        except Exception as error:
            print("Test error:: JSON file loaded uncorrectly.")
            print(error)
            sys.exit(1)


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
    args = parse_args()
    data = load_settings(args)
    test = load_test(args)
    imput_arguments(data, test)
    save_settings(data, args)
