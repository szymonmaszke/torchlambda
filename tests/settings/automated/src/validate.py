import json
import os
import sys

import torchlambda
import utils


def load_response():
    try:
        with open(os.environ["RESPONSE"], "r") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print("Test:: Failed during error response loading! Error: \n {}".format(e))
        sys.exit(1)


def validate_response(response, settings):
    def _get_type(name: str):
        mapping = {
            "int": int,
            "long": int,
            "float": float,
            "double": float,
        }
        if settings["return"][name] is not None:
            return (
                settings["return"][name]["item"],
                mapping[settings["return"][name]["type"]],
            )
        return (None, None)

    def _get_value(name: str):
        if settings["return"][name] is None:
            return None
        return response[name]

    def _validate(name, value, is_item, value_type):
        def _check_type(item):
            if not isinstance(item, value_type):
                print("Test:: {}'s item is not of type {}".format(name, value_type))
                sys.exit(1)

        if not any(value is None for value in (value, is_item, value_type)):
            print("Test:: Validating {} correctness...".format(name))
            if is_item:
                _check_type(value)
            else:
                if not isinstance(value, list):
                    print("Test:: {} is not a list!".format(name))
                    sys.exit(1)
                _check_type(value[0])

    print("Test:: Getting desired output types to assert...")
    (output_is_item, output_type), (result_is_item, result_type) = (
        _get_type("output"),
        _get_type("result"),
    )

    output_value, result_value = _get_value("output"), _get_value("result")

    print("Test:: Validating response correctness...")
    _validate("output", output_value, output_is_item, output_type)
    _validate("result", result_value, result_is_item, result_type)


if __name__ == "__main__":
    response = load_response()
    settings = utils.load_settings()
    validate_response(response, settings)
