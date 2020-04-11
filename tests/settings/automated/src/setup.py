import os
import random
import typing

import yaml

import torchlambda


class OptionGenerator:
    def __init__(self, options: int):
        self.options = options

    def __call__(self):
        return random.choice(self.options)


def generate(possibilities: typing.Dict) -> typing.Dict:
    return {
        key: value() if isinstance(value, OptionGenerator) else generate(value)
        for key, value in possibilities.items()
    }


def post_process(settings: typing.Dict) -> typing.Dict:
    def _remove_nones(dictionary):
        return {
            key: value if not isinstance(value, dict) else _remove_nones(value)
            for key, value in dictionary.items()
            if value is not None
        }

    def _possibly_nullify(dictionary):
        def _randomly_nullify_field(field, key):
            choice = random.choice([True, False])
            if choice:
                field[key] = None
            return choice

        # cast cannot be nullified as model hangs on other input than float
        _randomly_nullify_field(dictionary["input"], "divide")
        _randomly_nullify_field(dictionary, "normalize")
        no_output = _randomly_nullify_field(dictionary["return"], "output")
        if not no_output:
            _randomly_nullify_field(dictionary["return"], "result")

    _possibly_nullify(settings)
    return _remove_nones(settings)


def create_settings() -> None:
    validator = torchlambda.implementation.utils.template.validator.get()
    possibilities = {
        "grad": OptionGenerator([False]),
        "validate_json": OptionGenerator([True, False]),
        "input": {
            "validate": OptionGenerator([True, False]),
            "type": OptionGenerator(
                ["base64", "byte", "char", "short", "int", "long", "float", "double"]
            ),
            "shape": OptionGenerator(
                [
                    [1, 3, 64, 64],
                    ["batch", "channels", "width", "height"],
                    [1, 3, "width", "height"],
                ]
            ),
            "validate_shape": OptionGenerator([True, False]),
            # cast cannot be different as model hangs on different input than float
            "cast": OptionGenerator(["float"]),
            "divide": OptionGenerator([255]),
        },
        "normalize": {
            "means": OptionGenerator([[0.485, 0.456, 0.406], [0.485], [0.444, 0.444]]),
            "stddevs": OptionGenerator([[0.44], [0.229, 0.224, 0.225]]),
        },
        "return": {
            "output": {
                "type": OptionGenerator(["double"]),
                "item": OptionGenerator([False]),
            },
            "result": {
                "type": OptionGenerator(["int", "long"]),
                "item": OptionGenerator([True, False]),
                "operations": OptionGenerator(["argmax", ["sigmoid", "argmax"]]),
                "arguments": OptionGenerator([None, [[], 1]]),
            },
        },
    }

    settings = generate(possibilities)
    settings = post_process(settings)
    if not validator.validate(settings):
        create_settings()
    else:
        with open(os.environ["OUTPUT"], "w") as file:
            yaml.dump(settings, file, default_flow_style=False)


if __name__ == "__main__":
    create_settings()
