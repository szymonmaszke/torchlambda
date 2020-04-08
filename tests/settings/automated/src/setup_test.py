import os
import sys
import typing

import yaml

import utils


def load_settings() -> typing.Dict:
    with open(os.environ["SETTINGS"], "r") as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as error:
            print("Test error:: Error during user settings loading.")
            print(error)
            sys.exit(1)


def save(settings):
    with open(os.environ["OUTPUT"], "w") as file:
        yaml.dump(settings, file, default_flow_style=False)


def imput_arguments(settings, test) -> None:
    def _conditional_change(dictionary, target, value):
        dictionary[target] = test.get(value, dictionary[target])

    def _conditional_remove(dictionary, key):
        if key in test:
            if not test[key]:
                dictionary.pop(key)

    _conditional_change(settings["input"], "shape", "shape")
    _conditional_change(settings["input"], "type", "input_type")
    _conditional_change(settings["normalize"], "means", "means")
    _conditional_change(settings["normalize"], "stddevs", "stddevs")
    _conditional_change(settings["return"]["result"], "operations", "operations")
    _conditional_change(settings["return"]["result"], "arguments", "arguments")
    _conditional_change(settings["return"]["result"], "type", "return_type")
    _conditional_change(settings["return"]["result"], "item", "item")

    # Remove if no output or result should be returned
    _conditional_remove(settings, "normalize")
    _conditional_remove(settings["return"], "output")
    _conditional_remove(settings["return"], "result")


if __name__ == "__main__":
    args = utils.parse_args()
    test = utils.load_test(args)
    settings = load_settings()
    imput_arguments(settings, test)
    save(settings)
