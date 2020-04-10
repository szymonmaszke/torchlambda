import json
import os
import sys

import utils


def load_response():
    try:
        with open(os.environ["RESPONSE"], "r") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print("TEST FAILED DURING RESPONSE LOADING! Error: \n {}".format(e))
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
        field_name = settings["return"][name]["name"]
        return response.get(field_name, None)

    def _validate(name, value, is_array, value_type):
        def _check_type(item):
            if not isinstance(item, value_type):
                print(
                    "TEST_FAILED: {}'s item is not of type {}".format(name, value_type)
                )
                sys.exit(1)

        if is_array:
            if not isinstance(value, list):
                print("TEST FAILED: {} is not a list!".format(name))
                sys.exit(1)
            _check_type(value[0])
        else:
            _check_type(value)

    print("TEST: Getting desired output types to assert...")
    (output_array, output_type), (result_array, result_type) = (
        _get_type("output"),
        _get_type("result"),
    )

    print("TEST: Getting values from response...")
    output_value, result_value = _get_value("output"), _get_value("result")

    print("TEST: Validating response correctness...")
    _validate("output", output_value, output_array, output_type)
    _validate("result", result_value, result_array, result_type)


if __name__ == "__main__":
    response = load_response()
    settings = utils.load_settings()
    validate_response(response, settings)
